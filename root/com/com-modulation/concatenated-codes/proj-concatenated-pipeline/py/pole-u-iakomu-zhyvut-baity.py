PRIM = 0x11D                      # x⁸+x⁴+x³+x²+1 — незвідний многочлен поля
EXP = [0] * 512                   # EXP[i] = αⁱ (подвоєно, щоб не брати модуль)
LOG = [0] * 256                   # LOG[αⁱ] = i

x = 1
for i in range(255):
    EXP[i] = x
    LOG[x] = i
    x <<= 1                       # множення на α — це зсув…
    if x & 0x100:
        x ^= PRIM                 # …і згортка назад у поле, коли виліз 9-й біт
for i in range(255, 512):
    EXP[i] = EXP[i - 255]

def mul(a, b):
    return 0 if a == 0 or b == 0 else EXP[LOG[a] + LOG[b]]

def div(a, b):
    return 0 if a == 0 else EXP[(LOG[a] + 255 - LOG[b]) % 255]

def pw(a, n):
    return EXP[(LOG[a] * (n % 255)) % 255]

def inv(a):
    return EXP[255 - LOG[a]]
