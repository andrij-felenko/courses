# Шумове число каскаду (формула Фрііса), вхід і вихід — у dB
import math

def db2lin(db): return 10 ** (db / 10)
def lin2db(x):  return 10 * math.log10(x)

def cascade_nf(nf1_db, g1_db, nf2_db):
    F1 = db2lin(nf1_db)
    G1 = db2lin(g1_db)
    F2 = db2lin(nf2_db)
    Ftot = F1 + (F2 - 1) / G1   # внесок 2-го ділиться на G1
    return lin2db(Ftot)

# cascade_nf(2.0, 20.0, 8.0) ≈ 2.14 dB
