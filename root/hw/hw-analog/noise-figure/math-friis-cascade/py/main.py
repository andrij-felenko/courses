import math

# дБ → рази (за потужністю)
def db2lin(db):
    return 10.0 ** (db / 10.0)

# рази → дБ
def lin2db(x):
    return 10.0 * math.log10(x)

# Повний коефіцієнт шуму ланцюга за формулою Фрііса.
# nf_db[i], gain_db[i] — коефіцієнт шуму й підсилення i-ї ланки В ДЕЦИБЕЛАХ.
# Повертає повний NF тракту в дБ.
def cascade_nf_db(nf_db, gain_db):
    if not nf_db:
        return 0.0

    F_total    = db2lin(nf_db[0])    # перша ланка входить ЦІЛОЮ, без поділу
    gain_accum = db2lin(gain_db[0])  # добуток підсилень УСІХ ланок перед наступною

    for i in range(1, len(nf_db)):
        Fi = db2lin(nf_db[i])
        # надлишок (Fᵢ − 1), поділений на добуток підсилень усіх попередніх
        F_total    += (Fi - 1.0) / gain_accum
        gain_accum *= db2lin(gain_db[i])   # долучаємо підсилення цієї ланки до добутку
    return lin2db(F_total)
