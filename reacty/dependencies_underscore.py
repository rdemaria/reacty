from dataclasses import dataclass, field

from .refs import AttrRef, CallRef, Ref

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
        return f"Dependency({self.target},{self.dependencies},...)"

    def run(self):
        res = self.callback(*self.args, **dict(self.kwargs))
        if self.target is not None:
            self.target._set(res)



class DepManager:
    def __init__(self):
        self.deps = set()
        self.rdeps = {}

    def apply_set(self, ref):
        # print("Setting", ref, ref in self.rdeps)
        for dep in traverse(ref, self.rdeps):
            dep.run()

    def register(self, dep):
        # print("Register", dep)
        self.deps.add(dep)
        for ref in dep.dependencies:
            self.rdeps.setdefault(ref, set()).add(dep)

    def unregister(self, dep):
        # print("Unregister", dep)
        self.deps.remove(dep)
        for ref in dep.dependencies:
            self.rdeps[ref].remove(dep)
            if len(self.rdeps[ref]) == 0:
                del self.rdeps[ref]

    def class_(self, cls):
        def _silent_setattr(self, name, value):
            object.__setattr__(self, name, value)

        def __getattr__(self, name):
            if name.endswith("_"):
                orig = name[:-1]
                if hasattr(self, orig):
                    return AttrRef(self, orig)
            else:
                raise AttributeError

        def __setattr__(self, name, value):
            if name.endswith("_"):
                orig = name[:-1]
                if hasattr(self, orig):
                   self._dep_remove(orig)
                   ref = AttrRef(self, orig)
                   if isinstance(value, Ref):
                       dependencies = value._get_dependencies()
                       dep = Dependency(ref, tuple(dependencies), value._get_value)
                       self._dep_add(orig, dep)
                       value = value._get_value()
                   self._silent_setattr(orig, value)
                   self._notify.apply_set(ref)
            else:
                self._silent_setattr(name, value)

        def _dep_add(self, name, dep):
            # print("Add dep", dep)
            if not hasattr(self, "_deps"):
                self._deps = {}
            self._deps[name] = dep
            self._notify.register(dep)
            # print(self._notify.deps)
            # print(self._notify.rdeps)

        def _dep_remove(self, name):
            if hasattr(self, "_deps") and name in self._deps:
                # print("Remove dep", name)
                self._notify.unregister(self._deps[name])
                del self._deps[name]


        for ff in (_silent_setattr, __setattr__, _dep_add, _dep_remove, __getattr__):
            setattr(cls, ff.__name__, ff)

        setattr(cls, "_notify", self)
        return cls

    def fun_(self, fun):
        return FuncWrapper(fun)

reactive=DepManager()
