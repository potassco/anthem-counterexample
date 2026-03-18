# EVA examples

This folder contains three examples to show different situations regarding the
enough visible atoms (EVA) condition. All examples are programs that are
externally equivalent and use the same user guide `eva.ug`. As all examples are
propositional we only have to consider counterexamples of domain size 0, to do
so we add the option `-m 0`.

## EVA holds

The first two examples are cases where the EVA condition holds. For these
examples it is not necessary to use the guess and check approach.

### Example 1

The examples consists of programs `1-left.lp` and `1-right.lp` Here the EVA
condition can be verified using the syntactic criterion.

### Example 2

The example consists of programs `2-left.lp` and `2-right.lp` Here the EVA
condition can not be verified using the syntactic criterion. As a result the
guess and check approach is automatically used. To disable the use of the guess
and check approach we can add the option `--no-guess-and-check`. Neither method
produces a counterexample.

## EVA does not hold

In example 3, consisting of programs `3-left.lp` and `3-right.lp`, the EVA
condition does not hold. If we disable the use of the guess and check approach
(by using `--no-guess-and-check`) an incorrect counterexample is produced.
