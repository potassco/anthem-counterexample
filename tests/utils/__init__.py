"""Shared utilities for utils unit tests."""

from clingo.ast import AST, Function, Location, Pool, Position, SymbolicAtom, Variable

LOC = Location(Position("<string>", 1, 1), Position("<string>", 1, 1))


def make_function_atom(name: str) -> AST:
    """Construct a SymbolicAtom with a zero-arity Function symbol."""
    return SymbolicAtom(symbol=Function(LOC, name, [], False))


def make_pool_atom(names: list[str]) -> AST:
    """Construct a SymbolicAtom with a Pool of zero-arity Functions."""
    functions: list[AST] = [Function(LOC, name, [], False) for name in names]
    return SymbolicAtom(symbol=Pool(LOC, functions))


def make_variable_pool_atom() -> AST:
    """Construct a SymbolicAtom with a Pool containing a Variable."""
    return SymbolicAtom(symbol=Pool(LOC, [Variable(LOC, "X")]))


def make_unexpected_symbol_atom() -> AST:
    """Construct a SymbolicAtom with a Variable symbol (neither Function nor Pool)."""
    return SymbolicAtom(symbol=Variable(LOC, "X"))
