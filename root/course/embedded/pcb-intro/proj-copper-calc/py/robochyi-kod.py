import math

# Сталі підгінки кривих IPC-2221 (переріз — у кв. мілах, I — A, dT — °C).
IPC_B = 0.44
IPC_C = 0.725
IPC_K_EXTERNAL = 0.048   # мідь на зовнішньому шарі (обдувається)
IPC_K_INTERNAL = 0.024   # мідь на внутрішньому шарі (похована)

MM_PER_MIL = 0.0254      # 1 мил = 0.0254 мм
MIL_PER_OZ = 1.378       # товщина 1 oz міді у мілах

# Пряма формула IPC-2221: струм (А), який дасть переріз area_mils2 при перегріві dT.
def ipc2221_current(area_mils2, delta_t_c, k):
    return k * delta_t_c ** IPC_B * area_mils2 ** IPC_C
