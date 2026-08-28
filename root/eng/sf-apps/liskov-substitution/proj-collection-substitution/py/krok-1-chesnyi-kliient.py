# Клієнт написаний під ArrayList і вірить його контракту:
# «дали список — у нього можна додавати».
def fill(lst: "ArrayList", n: int) -> None:
    for i in range(n):
        lst.add(i)                  # контракт ArrayList це дозволяє

normal = ArrayList()
fill(normal, 3)                     # ок: [0, 1, 2]
print(normal.size())                # 3

frozen = ImmutableList([10, 20])
fill(frozen, 3)                     # ← ВИБУХ: TypeError на першому ж add
