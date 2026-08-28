INPUTS = [(0, 0), (0, 1), (1, 0), (1, 1)]

def nand(a, b):
    return 1 - (a & b)                 # ¬(a ∧ b) — єдина цегла

# З одного лише NAND:
def not_(a):     return nand(a, a)               # ¬a
def and_(a, b):  return not_(nand(a, b))         # a ∧ b = ¬(a | b)
def or_(a, b):   return nand(not_(a), not_(b))   # a ∨ b = ¬a | ¬b

# Звіряємо з еталонними таблицями істинності на всіх входах:
assert [not_(a)    for a, _ in INPUTS] == [1, 1, 0, 0]
assert [and_(a, b) for a, b in INPUTS] == [0, 0, 0, 1]
assert [or_(a, b)  for a, b in INPUTS] == [0, 1, 1, 1]
print("усе зібрано з NAND і збігається")
