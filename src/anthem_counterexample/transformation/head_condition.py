"""
Module to remove conditional literals in rule heads.
"""

from clingo.ast import AST, ASTType, Rule, Transformer

from ..utils.logging import get_logger
from ..utils.transformation import LOC

log = get_logger(__name__)


class RemoveHeadCondition(Transformer):
    """
    Remove conditional literals in rule heads

    h : c :- body. is turned into
    h :- body, c.
    """

    def visit_Rule(self, node: AST) -> AST:  # pylint: disable=invalid-name
        """
        Transform rules whose head is a conditional literal.
        """
        head = node.head

        # conditionals are elements of a disjunction
        if head.ast_type != ASTType.Disjunction:
            return node

        # empty head
        if len(head.elements) == 0:
            return node

        # ensure that the head only has one (disjunctive) element
        if len(head.elements) > 1:
            log.warning("Unexpected disjunctive rule %s", node)

        conditional = head.elements[0]

        # add the condition to the body
        new_body = node.body
        for cond in conditional.condition:
            new_body.append(cond)

        new_rule = Rule(
            location=LOC,
            # new head is just the literal of the conditional
            head=conditional.literal,
            body=new_body,
        )

        return new_rule
