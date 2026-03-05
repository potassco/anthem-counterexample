"""
Module for checking dependencies in a logic program.
"""

from clingo.ast import AST, ASTType, Sign, Transformer
from networkx import DiGraph, MultiDiGraph, simple_cycles, strongly_connected_components

from . import Predicate
from .logging import get_logger
from .transformation import atom_to_predicate

log = get_logger(__name__)


def has_enough_visible_atoms(program: list[AST], public_predicates: set[Predicate]) -> bool:
    """
    Check if a program has enough visible atoms by checking a modified predicate dependency graph for negative cycles.
    """
    graph_builder = SignedDependencyGraphBuilder(public_predicates)
    for n in program:
        graph_builder(n)

    graph = graph_builder.graph

    log.debug("Nodes: %s", graph.nodes)
    log.debug("Edges: %s", graph.edges(data=True))

    for scc in strongly_connected_components(graph):
        subgraph = graph.subgraph(scc)
        for _, _, data in subgraph.edges(data=True):
            if data.get("weight", 0) < 0:
                log.debug("SCC with negative loop: %s", scc)
                return False

    return True


def has_recursive_aggregates(program: list[AST]) -> bool:
    """
    Check if a program contains recursive aggregates.
    """
    graph_builder = AggregateDependencyGraphBuilder()
    for n in program:
        graph_builder(n)

    graph = graph_builder.graph
    cycles = list(simple_cycles(graph))

    log.debug("Nodes: %s", graph.nodes)
    log.debug("Edges: %s", graph.edges)
    if cycles:
        log.debug("Cycles: %s", cycles)
    else:
        log.debug("No cycles found")

    return bool(cycles)


class SignedDependencyGraphBuilder(Transformer):
    """
    Transformer to build a predicate dependency graph.
    """

    def __init__(self, public_predicates: set[Predicate]):
        super().__init__()
        self.graph = MultiDiGraph()
        self.current_head: Predicate | None = None
        self._public_predicates = public_predicates

    def _is_private(self, pred: Predicate):
        return pred not in self._public_predicates

    def visit_Rule(self, node: AST) -> AST:  # pylint: disable=invalid-name
        """
        Process each rule: add head predicate as node and process body.
        """
        self.current_head = None

        if node.head.ast_type == ASTType.Literal:
            if node.head.atom.ast_type == ASTType.SymbolicAtom:
                pred = atom_to_predicate(node.head.atom)
                self.graph.add_node(pred)
                self.current_head = pred
                self.visit_sequence(node.body)

        elif node.head.ast_type == ASTType.Aggregate:
            if len(node.head.elements) > 1:
                raise ValueError(f"Choice rule should not have more than 1 element: {node}")

            atom = node.head.elements[0].atom
            pred = atom_to_predicate(atom)
            self.graph.add_node(pred)
            self.current_head = pred
            self.visit_sequence(node.body)

        return node

    def visit_Literal(self, node: AST) -> AST:  # pylint: disable=invalid-name
        """
        Process body literals: add a edge for body predicats.
        """
        if self.current_head is None:
            return node

        atom = node.atom

        if atom.ast_type != ASTType.SymbolicAtom:
            return node

        body_pred = atom_to_predicate(atom)
        self.graph.add_node(body_pred)

        # add all positive dependencies with weight 0
        if node.sign == Sign.NoSign:
            weight = 0
        # add negative dependencies of private predicates with weight -1
        elif self._is_private(body_pred):
            weight = -1
        # ignore negative dependencies of public predicates
        else:
            return node

        self.graph.add_edge(self.current_head, body_pred, weight=weight)

        return node


class AggregateDependencyGraphBuilder(Transformer):
    """
    Build an aggregate dependency graph.
    """

    def __init__(self):
        super().__init__()
        self.graph = DiGraph()
        self.current_head: Predicate | None = None

    def visit_Rule(self, node: AST) -> AST:  # pylint: disable=invalid-name
        """
        Process each rule: add head predicate as node and process body.
        """
        self.current_head = None

        if node.head.ast_type == ASTType.Literal:
            if node.head.atom.ast_type == ASTType.SymbolicAtom:
                pred = atom_to_predicate(node.head.atom)
                self.graph.add_node(pred)
                self.current_head = pred
                self.visit_sequence(node.body)
        elif node.head.ast_type == ASTType.Aggregate:
            if len(node.head.elements) > 1:
                raise ValueError(f"Choice rule should not have more than 1 element: {node}")

            atom = node.head.elements[0].atom
            pred = atom_to_predicate(atom)
            self.graph.add_node(pred)
            self.current_head = pred
            self.visit_sequence(node.body)

        return node

    def visit_Literal(self, node: AST) -> AST:  # pylint: disable=invalid-name
        """
        Process body literals: add a edge for each predicate in an aggregate.
        """
        if node.atom.ast_type == ASTType.BodyAggregate:
            aggregate = node.atom
            for elem in aggregate.elements:
                for lit in elem.condition:
                    if lit.atom.ast_type == ASTType.SymbolicAtom:
                        pred = atom_to_predicate(lit.atom)
                        self.graph.add_edge(self.current_head, pred)
        elif node.atom.ast_type == ASTType.Aggregate:
            aggregate = node.atom
            for elem in aggregate.elements:
                lit = elem.literal
                if lit.atom.ast_type == ASTType.SymbolicAtom:
                    pred = atom_to_predicate(lit.atom)
                    self.graph.add_edge(self.current_head, pred)
                for lit in elem.condition:
                    if lit.atom.ast_type == ASTType.SymbolicAtom:
                        pred = atom_to_predicate(lit.atom)
                        self.graph.add_edge(self.current_head, pred)

        return node
