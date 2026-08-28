# Повертає: +1 якщо a>b,  0 якщо a==b,  -1 якщо a<b.
# Свідомо скановано побітово від старшого біта — так само, як каскад у залізі.
def cmp16_bitwise(a: int, b: int) -> int:
    for i in range(15, -1, -1):          # біт 15 = старший
        mask = 1 << i
        abit = a & mask
        bbit = b & mask
        if abit != bbit:                 # перша відмінність
            return +1 if abit > bbit else -1   # чий біт «1» — той більший
    return 0                             # жодної відмінності — рівні
