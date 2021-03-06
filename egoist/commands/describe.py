from __future__ import annotations
import typing as t
from functools import partial
from egoist.app import App
from egoist.types import AnyFunction

if t.TYPE_CHECKING:
    from argparse import ArgumentParser


def describe(app: App) -> None:
    import json
    import inspect
    from egoist.langhelpers import get_fullname_of_type, get_fullname_of_callable

    app.commit(dry_run=False)

    definitions: t.Dict[str, t.Dict[str, t.Union[str, t.List[str]]]] = {}
    delayed_include_mapping = app.delayed_include_mapping
    for kit, fns in app.registry.generators.items():
        for fn in fns:
            name = get_fullname_of_callable(fn)
            summary = (inspect.getdoc(fn) or "").strip().split("\n", 1)[0]

            definitions[name] = {"doc": summary, "generator": kit}

            if fn in delayed_include_mapping:
                definitions[name]["include_when"] = [
                    get_fullname_of_callable(dep)
                    if callable(dep)
                    else (_app.module.__name__ + dep if dep.startswith(".") else dep)
                    for _app, dep in delayed_include_mapping[fn]
                ]

    factories = {
        name: [get_fullname_of_type(x) for x in xs]  # type: ignore
        for name, xs in app.registry.factories.items()
    }

    empty_context = app.context_factory()
    current_directives = set(
        name for name, attr in app.context.__dict__.items() if callable(attr)
    )
    append_directives = current_directives.difference(empty_context.__dict__.keys())
    append_directives = append_directives.difference(["run"])

    d = {
        "definitions": definitions,
        "components": factories,
        "directives": {
            name: get_fullname_of_type(getattr(app.context, name))
            for name in append_directives
        },
    }
    print(json.dumps(d, indent=2, ensure_ascii=False))


def setup(app: App, sub_parser: ArgumentParser, fn: AnyFunction) -> None:
    sub_parser.set_defaults(subcommand=partial(fn, app))


def includeme(app: App) -> None:
    app.include("egoist.directives.add_subcommand")
    app.add_subcommand(setup, fn=describe)
