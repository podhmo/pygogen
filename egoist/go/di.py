from __future__ import annotations
import typing as t
import typing_extensions as tx
from collections import defaultdict
from prestring.go.codeobject import Module, Symbol
from egoist.internal.graph import primitive, Graph, Builder as _Builder
from egoist.internal.graph import topological_sorted
from egoist.internal._fnspec import fnspec, Fnspec
from .types import get_gopackage, GoPointer, priority


class Metadata(tx.TypedDict, total=False):
    return_type: t.Type[t.Any]
    component_type: t.Type[t.Any]
    fnspec: Fnspec
    levels: t.Dict[str, int]  # name -> level


class Variable(Symbol):
    __slots__ = ("name", "as_", "level")

    def __init__(self, name: str, as_: t.Optional[str] = None, level=0):
        super().__init__(name, as_=as_)
        self.level = level


def _unwrap_pointer_type(
    typ: t.Type[t.Any], *, level: int = 0
) -> t.Tuple[t.Type[t.Any], int]:
    # todo: support slice, map
    # value = 0, pointer = 1, pointer of pointer = 2, ...
    if not hasattr(typ, "__origin__"):
        return typ, level

    if typ.__origin__ == GoPointer:
        return _unwrap_pointer_type(t.get_args(typ)[0], level=level + 1)
    return typ, level


def parse(fn: t.Callable[..., t.Any]) -> t.Tuple[str, t.List[str], Metadata]:
    spec = fnspec(fn)

    depends: t.List[str] = []
    levels: t.Dict[str, int] = {}
    for name, typ, _ in spec.arguments:  # parameters?
        if typ.__module__ == "builtins":
            depends.append(primitive(name, metadata={"component_type": typ}))
            continue
        typ, level = _unwrap_pointer_type(typ)
        depends.append(typ.__name__)
        levels[name] = level

    return_type = spec.return_type
    return_level = 0
    if not hasattr(return_type, "__origin__"):
        component_type = return_type
    elif return_type.__origin__ == tuple:
        component_type, *_ = t.get_args(return_type)
    elif return_type.__origin__ == GoPointer:
        component_type, return_level = _unwrap_pointer_type(return_type)
    else:
        import inspect

        raise RuntimeError(f"unexpected return-type. {inspect.signature(spec.body)}")
    levels["return"] = return_level

    metadata: Metadata = {
        "return_type": return_type,
        "component_type": component_type,
        "fnspec": spec,
        "levels": levels,
    }
    return {
        "name": component_type.__name__,
        "depends": depends,
        "metadata": metadata,
    }


# TODO: rename
def primitives(g: Graph, local_mapping: t.Dict[str, Symbol]) -> t.Dict[int, Symbol]:
    try:
        return {
            node.uid: local_mapping[node.name] for node in g.nodes if node.is_primitive
        }
    except KeyError as e:
        raise RuntimeError(f"arguments {e} is not found in {local_mapping.keys()}")


def inject(
    m: Module,
    g: Graph,
    *,
    variables: t.Dict[int, Symbol],
    levels: t.Optional[t.Dict[int, int]] = None,
    strict: bool = True,
) -> Symbol:
    # TODO: name
    i = 0
    if levels is None:
        levels = defaultdict(int)
    for node in topological_sorted(g):
        if node.is_primitive:
            if strict:
                assert node.uid in variables
            else:
                variables[node.uid] = m.symbol(node.name)
            continue

        metadata = t.cast(Metadata, node.metadata)
        return_type = metadata.get("return_type", "")

        # handling provider callable
        return_types = list(t.get_args(return_type) or [return_type])
        var_names = [
            f"v{i}",
            *[getattr(typ, "name", typ.__name__) for typ in return_types[1:]],
        ]

        spec: Fnspec = metadata.get("fnspec")
        provider_callable: t.Optional[Symbol] = None
        if spec is not None:
            provider = spec.name
            pkg = get_gopackage(metadata["fnspec"].body)
            if pkg is not None:
                pkg_prefix = m.import_(pkg)
                provider = f"{pkg_prefix}.{provider}"
            provider_callable = m.symbol(provider)
        if provider_callable is None:
            provider_callable = m.symbol(spec.name if spec else node.name)

        # handling arguments (pointer)
        if spec is None:
            args = [variables[dep.uid] for dep in node.depends]  # todo: remove
        else:
            args: t.List[Symbol] = []
            assert len(node.depends) == len(spec.arguments), (
                len(node.depends),
                len(spec.arguments),
            )
            for dep, (name, typ, _) in zip(node.depends, spec.arguments):  # parameters?
                sym = variables[dep.uid]

                current_level = levels[dep.uid]
                need_level = metadata["levels"].get(name, 0)  # more strict?
                level_diff = need_level - current_level

                if level_diff == 0:
                    pass
                elif level_diff > 0:
                    sym = Symbol(f"&" * level_diff + str(sym))
                else:
                    sym = Symbol(f"*" * -level_diff + str(sym))
                args.append(sym)
            levels[node.uid] = metadata["levels"]["return"]

        variables[node.uid], *extra_vars = m.letN(var_names, provider_callable(*args))

        # handling error and teardown:
        if extra_vars:
            for sym, typ in sorted(
                zip(extra_vars, return_types[1:]),
                key=lambda pair: getattr(pair[1], "priority", priority.NORMAL),
                reverse=True,
            ):
                if hasattr(typ, "emit"):
                    typ.emit(m, sym)

        i += 1
    return variables[node.uid]


class Builder:
    def __init__(self):
        self.b: _Builder = _Builder()

    def add_provider(self, provider: t.Callable[..., t.Any]):
        self.b.add_node(**parse(provider))

    def build(self, *, variables: t.Optional[str, Symbol] = None) -> Injector:
        g = self.b.build()
        uid_variable_mapping = primitives(g, variables)
        return Injector(g, variables=uid_variable_mapping)


class Injector:
    def __init__(self, g: Graph, *, variables: t.Dict[int, Symbol]) -> None:
        self.g = g
        self.variables: t.Dict[int, Symbol] = variables
        self.variable_levels: t.Dict[int, int] = defaultdict(int)

    def inject(self, m: Module) -> Symbol:
        return inject(m, self.g, variables=self.variables, levels=self.variable_levels)