from dataclasses import dataclass

# один ORB-дескриптор: 256 бітів як одне ціле python-число
# (набір — просто список таких цілих, довжина = кількість)

@dataclass
class OrbMatch:
    query: int          # індекс у наборі A
    train: int = -1     # індекс у наборі B (-1 = немає пари)
    dist: int = 257     # відстань Гаммінга до пари (0..256)
