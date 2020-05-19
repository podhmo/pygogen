from __future__ import annotations
import typing as t
import typing_extensions as tx
import pathlib
from egoist.app import App
from egoist import runtime

NAME = __name__


class Dependency(tx.TypedDict):
    name: str
    depends: t.Set[t.Union[str, pathlib.Path]]
    task: str


class Tracker:
    def __init__(self) -> None:
        self.deps_map: t.Dict[str, Dependency] = {}

    def track(
        self,
        name_or_path: t.Union[str, pathlib.Path],
        *,
        task: str = "",
        depends_on: t.Optional[t.Collection[t.Union[str, pathlib.Path]]]
    ) -> None:
        name = str(name_or_path)
        dependency = self.deps_map.get(name)
        if dependency is None:
            dependency = self.deps_map[name] = {
                "name": name,
                "depends": set(),
                "task": task,
            }
        if depends_on:
            dependency["depends"].update(depends_on)

    def get_dependencies(
        self, *, root: t.Union[str, pathlib.Path], relative: bool = False
    ) -> t.Dict[str, t.Dict[str, t.Union[str, t.List[str]]]]:
        root_path = pathlib.Path(root).absolute()
        if not relative:
            return {
                str((root_path / name)): {
                    "task": dep.get("task", ""),
                    "depends": [str(x) for x in dep["depends"]],
                }
                for name, dep in self.deps_map.items()
            }

        cwd_path = pathlib.Path().absolute()
        return {
            str((root_path / name).relative_to(cwd_path)): {
                "task": dep.get("task", ""),
                "depends": [
                    str(pathlib.Path(x).relative_to(cwd_path)) for x in dep["depends"]
                ],
            }
            for name, dep in self.deps_map.items()
        }


def get_tracker() -> Tracker:
    return t.cast(Tracker, runtime.get_component(NAME))


def includeme(app: App) -> None:
    app.register_factory(NAME, Tracker)
    app.register_dryurn_factory(NAME, Tracker)
