import math

# дБ → рази
def db2lin(db): return 10.0 ** (db / 10.0)
# рази → дБ
def lin2db(x):  return 10.0 * math.log10(x)

F1 = db2lin(1.0)     # NF LNA: 1 дБ  → F₁ ≈ 1.259
G1 = db2lin(20.0)    # підсилення LNA: 20 дБ → G₁ = 100
F2 = db2lin(10.0)    # NF змішувача: 10 дБ → F₂ = 10

# формула Фрііса для двох каскадів
F  = F1 + (F2 - 1.0) / G1   # 1.259 + 9/100 = 1.349
NF = lin2db(F)              # 10·log₁₀(1.349) ≈ 1.30 дБ
