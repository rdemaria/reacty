from reacty import reactive

import logging
logging.basicConfig(level=logging.INFO)

@reactive.class_
class C:
    pass

c1=C()
c1.lst=[1,2,3]

c1.lst_[2]=c1.lst_[2]*2

