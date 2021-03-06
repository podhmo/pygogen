from __future__ import annotations
from egoist.go import di
from egoist.internal.prestringutil import Module


class X:
    pass


class Y:
    pass


class Z:
    pass


class providers:
    @staticmethod
    def NewX(filename: str) -> X:
        pass

    @staticmethod
    def NewY(filename: str) -> Y:
        pass

    @staticmethod
    def NewZ(x: X, y: Y) -> Z:
        pass


m = Module()

m.stmt("// both of NewX() and NewY() depend on an argument with the same name")
m.sep()

with m.func("run2"):
    config = m.let("config", '"config.json"')
    m.sep()

    b = di.Builder()

    b.add_provider(providers.NewX)
    b.add_provider(providers.NewY)
    b.add_provider(providers.NewZ)

    injector = b.build(variables={"filename": config})
    z = injector.inject(m)

    m.return_(z.Run())
print(m)
