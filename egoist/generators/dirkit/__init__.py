from __future__ import annotations
import typing as t

import logging
import pathlib
from egoist import types
from egoist.components.fs import open_fs
from egoist.langhelpers import get_path_from_function_name

logger = logging.getLogger(__name__)

if t.TYPE_CHECKING:
    from egoist.app import App


def includeme(app: App) -> None:
    app.include("egoist.components.fs")


def walk(fns: t.Dict[str, types.Command], *, root: t.Union[str, pathlib.Path]) -> None:
    with open_fs(root=root) as fs:
        for name, fn in fns.items():
            logger.debug("walk %s", name)
            fpath = get_path_from_function_name(getattr(fn, "_rename", None) or name)
            with fs.open_dir_with_tracking(fpath, target=fn) as env:
                kwargs = {
                    name: str(env.fnspec.here.parent / default)
                    for name, default in (
                        env.fnspec.argspec.kwonlydefaults or {}
                    ).items()
                }
                fn(**kwargs)
