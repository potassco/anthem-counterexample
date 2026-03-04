"""
Module for checking dependencies in a logic program.
"""

from clingo.ast import AST, ASTType, Transformer
from networkx import DiGraph, simple_cycles

from . import Predicate
from .logging import get_logger
from .transformation import atom_to_predicate

log = get_logger(__name__)


def is_private_stratified(program: list[AST]) -> bool:
    # TODO: implement private stratification check
    return True


def has_recursive_aggregates(program: list[AST]) -> bool:
    graph_builder = AggregateDependencyGraphBuilder()
    for n in program:
        graph_builder(n)

    graph = graph_builder.graph

    cycles = simple_cycles(graph)
    return bool(cycles)


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

    def visit_Literal(self, node: AST) -> AST:  # pylint disable=invalid-name
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
