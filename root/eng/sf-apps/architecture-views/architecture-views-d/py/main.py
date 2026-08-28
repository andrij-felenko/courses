from enum import Enum


class Kind(Enum):                                 # рід зв'язку = вимір в'ю
    DEPENDS = 1
    CALLS = 2
    DEPLOYED = 3


# Одна модель — усі факти про систему разом, без поділу на діаграми.
MODEL = [
    ("orders", "prices",  Kind.DEPENDS),   # orders статично залежить від prices
    ("orders", "prices",  Kind.CALLS),     # і в часі його викликає
    ("orders", "node-eu", Kind.DEPLOYED),  # а розгорнутий orders на вузлі EU
    ("prices", "node-us", Kind.DEPLOYED),  # prices — на іншому вузлі, US!
    ("prices", "cache",   Kind.DEPENDS),
]


# «Намалювати в'ю» = профільтрувати одну модель за родом зв'язку.
def render_view(name, kind):
    print(f"В'ю: {name}")
    for src, dst, k in MODEL:
        if k == kind:
            print(f"  {src:<8} -> {dst:<8}")


render_view("логічний (залежності)", Kind.DEPENDS)
render_view("процесний (виклики)",   Kind.CALLS)
render_view("розгортання (вузли)",   Kind.DEPLOYED)
