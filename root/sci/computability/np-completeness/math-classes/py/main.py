from itertools import product

def solve_np(x, verify, p):
    """Універсальний розв'язувач будь-якої NP-задачі: перебрати всіх свідків.
       verify(x, w) — поліномний перевіряч; p — межа на довжину свідка."""
    m = p(len(x))                          # свідок не довший за p(|x|)
    for bits in product((0, 1), repeat=m): # усі 2^m рядків-свідків
        if verify(x, bits):                # знайшовся придатний свідок
            return True                    #   → відповідь «так»
    return False                           # жоден не підійшов → «ні»

# Задача про суму підмножини як NP-мова: свідок — маска вибраних чисел.
def subset_sum_verify(inst, mask):
    nums, target = inst
    return sum(v for v, b in zip(nums, mask) if b) == target

solve_np(([3, 34, 4, 12, 5, 2], 9), subset_sum_verify, p=lambda n: n)  # True
