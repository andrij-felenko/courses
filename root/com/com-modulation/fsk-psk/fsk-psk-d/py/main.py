from math import log2

# Біт на символ для сузір'я з M станами: log2(M).
def bits_per_symbol(M):
    return round(log2(M))          # M=4 → 2, M=256 → 8

# Бітова швидкість (біт/с) із символьної (бод) і кількості станів сузір'я.
def bit_rate_bps(baud, M):
    return baud * bits_per_symbol(M)

# 1 Мбод:  BPSK → 1e6,  QPSK → 2e6,  16-QAM → 4e6 біт/с
r_bpsk = bit_rate_bps(1_000_000, 2)    # 1 000 000
r_qpsk = bit_rate_bps(1_000_000, 4)    # 2 000 000
r_qam  = bit_rate_bps(1_000_000, 16)   # 4 000 000
