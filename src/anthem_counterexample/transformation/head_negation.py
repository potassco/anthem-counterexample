"""
Module to remove negation in rule heads.
"""

from clingo.ast import AST, ASTType, Disjunction, Literal, Rule, Sign, Transformer

from ..utils.logging import get_logger
from ..utils.transformation import LOC

log = get_logger(__name__)


def _remove_negation(sign: Sign) -> Sign:
    """
    Remove one negation from sign.
    """
    match sign:
        case Sign.NoSign:
            log.warning("Unexpected no sign")
            return sign
        case Sign.Negation:
            return Sign.NoSign
        case Sign.DoubleNegation:
            return Sign.Negation


class RemoveHeadNegation(Transformer):
    """
    Remove any negated head literals

    not l :- body. is turned into
    :- body, l.

    not not l :- body. is turned into
    :- body, not l.
    """

    def visit_Rule(self, node: AST) -> AST:  # pylint: disable=invalid-name
        """
        Transform rules with negative heads.
        """
        head = node.head

        # skip all rules whose head is not a literal
        if head.ast_type != ASTType.Literal:
            # TODO: what about negations in choices?
            return node

        # only rules whose head literal is negated are transformed
        if head.sign in [Sign.Negation, Sign.DoubleNegation]:
            # empty head for the constraint
            empty_head = Disjunction(
                location=LOC,
                elements=[],
            )

            # remove a negation
            new_sign = _remove_negation(head.sign)

            # new body is obtained by adding the head atom with its new sign
            new_body = node.body
            new_body.append(
                Literal(
                    location=LOC,
                    sign=new_sign,
                    atom=head.atom,
                )
            )

            new_rule = Rule(
                location=LOC,
                head=empty_head,
                body=new_body,
            )

            return new_rule

        return node
