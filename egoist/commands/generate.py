from __future__ import annotations
import typing as t
from functools import partial
from miniconfig.exceptions import ConfigurationError
from egoist.app import App, get_root_path
from egoist.types import AnyFunction

if t.TYPE_CHECKING:
    from argparse import ArgumentParser


def generate(
    app: App,
    *,
    tasks: t.Optional[t.List[str]] = None,
    rootdir: t.Optional[str] = None,
    dry_run: bool = False
) -> None:
    root_path = get_root_path(app.settings, root=rootdir)
    app.commit(dry_run=dry_run)
    app.context.queue.clear()  # xxx: clear

    action_list: t.List[t.Callable[..., t.Any]] = []
    included_after_commit_list: t.List[t.Union[str, t.Callable[..., t.Any]]] = []

    for kit, fns in app.registry.generators.items():
        walk_or_module = app.maybe_dotted(kit)
        if callable(walk_or_module):
            walk = walk_or_module
        elif hasattr(walk_or_module, "walk"):
            walk = walk_or_module.walk  # type: ignore
        else:
            # TODO: genetle error message
            raise ConfigurationError("{kit!r} is not callable")

        if not tasks:
            sources = {fn.__name__: fn for fn in fns}
        else:
            sources = {fn.__name__: fn for fn in fns if fn.__name__ in tasks}
        action_list.append(partial(walk, sources, root=root_path))

        # for app.include_when()
        delayed_include_mapping = app.delayed_include_mapping
        for fn in sources.values():
            if fn in delayed_include_mapping:
                for _app, path in delayed_include_mapping[fn]:
                    _app.include(path)
                    included_after_commit_list.append(path)
        app.delayed_include_mapping.clear()  # xxx: clear

    if len(included_after_commit_list) > 0:
        app.shallow_commit()

    for action in action_list:
        action()


def setup(app: App, sub_parser: ArgumentParser, fn: AnyFunction) -> None:
    sub_parser.add_argument("--rootdir", required=False, help="-")
    sub_parser.add_argument("tasks", nargs="*", choices=app.registry._task_list)
    sub_parser.set_defaults(subcommand=partial(fn, app))


def includeme(app: App) -> None:
    app.include("egoist.directives.add_subcommand")
    app.add_subcommand(setup, fn=generate)
