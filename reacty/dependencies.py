from dataclasses import dataclass, field
import logging

from .refs import AttrRef, CallRef, Ref

logger=logging.getLogger(__name__)

def _traverse(ref, rdeps, lst, st):  # breath first sorting
    if ref in rdeps:
        for dep in rdeps[ref]:
            if dep not in st:
                lst.append(dep)
                st.add(dep)
            _traverse(dep.target, rdeps, lst, st)
    return lst


def traverse(ref, rdeps):
    return _traverse(ref, rdeps, [], set())


class FuncWrapper:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return CallRef(self.func, args, tuple(kwargs.items()))


@dataclass(frozen=True, unsafe_hash=True)
class Dependency:
    target: object
    dependencies: tuple
    callback: object
    args: tuple = field(default_factory=tuple)
    kwargs: tuple = field(default_factory=tuple)

    def __repr__(self):
        return f"Dependency({self.target},{self.dependencies})"

    def run(self):
        logger.info(f"Run {self}")
        res = self.callback(*self.args, **dict(self.kwargs))
        if self.target is not None:
            self.target._set(res)


class DepManager:
    def __init__(self):
        self.deps = set()
        self.rdeps = {}

    def apply_set(self, ref):
        logger.info(f"Apply_set {ref}")
        for dep in traverse(ref, self.rdeps):
            dep.run()

    def register(self, dep):
        logger.info(f"Register {dep}")
        self.deps.add(dep)
        for ref in dep.dependencies:
            self.rdeps.setdefault(ref, set()).add(dep)

    def unregister(self, dep):
        logger.info(f"Register {dep}")
        self.deps.remove(dep)
        for ref in dep.dependencies:
            self.rdeps[ref].remove(dep)
            if len(self.rdeps[ref]) == 0:
                del self.rdeps[ref]

    def class_(self, cls):
        cls_setattr=cls.__setattr__
        def _silent_setattr(self, name, value):
            cls_setattr(self, name, value)

        def __getattr__(self, name):
            if name.endswith("_"):
                orig = name[:-1]
                if hasattr(self, orig):
                    return AttrRef(self, orig, self._notify)
            raise AttributeError

        def __setattr__(self, name, value):
            ref = AttrRef(self, name, self._notify)
            if isinstance(value, Ref):
                self._dep_remove(name)
                dependencies = value._get_dependencies()
                dep = Dependency(ref, tuple(dependencies), value._get_value)
                self._dep_add(name, dep)
                value = value._get_value()
            self._silent_setattr(name, value)
            self._notify.apply_set(ref)

        def _dep_add(self, name, dep):
            if not hasattr(self, "_deps"):
                self._deps = {}
            self._deps[name] = dep
            self._notify.register(dep)

        def _dep_remove(self, name):
            if hasattr(self, "_deps") and name in self._deps:
                self._notify.unregister(self._deps[name])
                del self._deps[name]


        for ff in (_silent_setattr, __setattr__, _dep_add, _dep_remove, __getattr__):
            setattr(cls, ff.__name__, ff)

        setattr(cls, "_notify", self)
        return cls

    def fun_(self, fun):
        return FuncWrapper(fun)

reactive=DepManager()
