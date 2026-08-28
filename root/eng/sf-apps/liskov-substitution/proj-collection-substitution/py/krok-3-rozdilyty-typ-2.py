# fill просить MutableList — тобто «уміє add».
def fill(lst: MutableList, n: int) -> None:
    for i in range(n):
        lst.add(i)

fill(ArrayList(), 3)                       # ок

frozen = ImmutableList([10, 20])
fill(frozen, 3)
#    ^^^^^^ mypy: Argument 1 to "fill" has incompatible type
#           "ImmutableList"; expected "MutableList"
