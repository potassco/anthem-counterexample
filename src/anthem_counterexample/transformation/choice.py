"""
Module to transform choice rules into normal form.
"""

from clingo.ast import AST, Transformer, ASTType, Aggregate, Rule

from ..utils.transformation import LOC, aggregate_constraint, choice_rule_for_elements
from ..utils.logging import get_logger

log = get_logger(__name__)


class ChoiceGuardNormalizer(Transformer):
    """
    Normalize choice heads by removing guards.

    E.g. lower <= { l : L } <= upper :- body. is turned into:
    1. { l : L } :- body. and
    2. :- body, not lower <= { l : L } <= upper.
    """

    def visit_Rule(self, node: AST) -> AST | list[AST]:  # pylint: disable=invalid-name
        """
        Transform choice rules.
        """
        head = node.head

        # skip any rules whose head is not an aggregate
        if head.ast_type != ASTType.Aggregate:
            return node

        # skip choice rules without guards
        if head.left_guard is None and head.right_guard is None:
            return node

        # new choice rule without guards
        choice_rule = choice_rule_for_elements(head.elements, node.body)

        # body aggregate corresponding to the original choice head
        body_aggregate = Aggregate(
            location=LOC,
            left_guard=head.left_guard,
            elements=head.elements,
            right_guard=head.right_guard,
        )

        # constraint to enforce the guards of the original choice
        constraint = aggregate_constraint(body_aggregate, node.body)

        return [choice_rule, constraint]


class ChoiceElementNormalizer(Transformer):
    """
    Normalize choice heads.

    E.g. { l1 : L1 ; l2 : L2 } :- body. is turned into:
    { l1 } :- body, L1. and
    { l2 } :- body, L2.
    """

    def visit_Rule(self, node: AST) -> AST | list[AST]:  # pylint: disable=invalid-name
        """
        Transform choice rules.
        """
        head = node.head

        # skip any rules whose head is not a choice
        if head.ast_type != ASTType.Aggregate:
            return node

        new_rules = []

        # construct a new rule for each element of the choice
        for elem in head.elements:
            # the new choice head
            choice = Aggregate(
                location=LOC,
                left_guard=None,
                elements=[elem.literal],
                right_guard=None,
            )

            # new body is the old body and any elements of the conditional
            new_body = []
            for lit in node.body:
                new_body.append(lit)
            for cond in elem.condition:
                new_body.append(cond)

            new_rules.append(
                Rule(
                    location=LOC,
                    head=choice,
                    body=new_body,
                )
            )

        return new_rules
