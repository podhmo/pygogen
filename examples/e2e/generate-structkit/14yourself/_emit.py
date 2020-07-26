import typing as t
import contextlib
from egoist.internal.prestringutil import Module
from egoist.generators.structkit import runtime


@contextlib.contextmanager
def emit(
    env: runtime.Env, classes: t.List[t.Type[t.Any]], dry_run: bool
) -> t.Iterator[Module]:
    if dry_run:
        yield env.m
        return

    from egoist.go.types import get_gopackage
    from egoist.go.walker import get_walker
    from egoist.generators.structkit import _emit

    m = env.m
    w = get_walker(classes, m=m, metadata_handler=runtime._default_metadata_handler)

    yield m
    m.import_("")
    m.stmt(f"// this file is generated by *me*")
    m.sep()

    for item in w.walk():
        gopackage = get_gopackage(item.type_)
        if gopackage is not None:
            continue

        # emit only struct
        _emit.emit_struct(w, item)
        m.sep()
    return m
