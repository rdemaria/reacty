from dataclasses import dataclass

@dataclass(frozen=True,unsafe_hash=True)
class Dep:
    target: str
    deps: tuple


def mk_rdeps(deps):
    rdeps={}
    for dep in deps:
        for d in dep.deps:
            rdeps.setdefault(d,[]).append(dep)
    return rdeps

def traverse(ref,rdeps,lst,st):
    if ref in rdeps:
        for dep in rdeps[ref]:
            if dep not in st:
                lst.append(dep)
                st.add(dep)
            traverse(dep.target,rdeps,lst,st)
    return lst

deps=[
        Dep('c',('a','b')),
        Dep('d',('a','c')),
        Dep('e',('b','c')),
        Dep('f',('d','b')),
        Dep('g',('f','a')),
]

rdeps=mk_rdeps(deps)

traverse('a',rdeps,[],set())


