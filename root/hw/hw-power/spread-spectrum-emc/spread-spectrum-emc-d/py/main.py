import math

fsw    = 440e3    # частота перемикання, Гц
harm   = 3        # проблемна гармоніка
spread = 0.06     # ±6 % розмаху
rbw    = 9e3      # вікно приймача CISPR 25 (низька смуга), Гц

f_harm = harm * fsw               # 1.32 МГц — де стоїть спиця
df     = 2.0 * spread * f_harm    # повна ширина розмазу (±6 % → 12 %)
gain   = 10.0 * math.log10(df / rbw)  # наближене падіння піку

print(f"гармоніка : {f_harm / 1e6:.2f} МГц")
print(f"розмаз Δf  : {df / 1e3:.0f} кГц ({2 * spread * 100:.0f} % від гармоніки)")
print(f"вікно RBW  : {rbw / 1e3:.0f} кГц")
print(f"падіння піку ~ {gain:.1f} дБ")

before = -8.0                     # було: на 8 дБ ВИЩЕ стелі
after  = before + gain
print(f"запас до стелі: {before:.1f} -> {after:.1f} дБ  "
      f"{'(проходить)' if after > 0 else '(усе ще завалено)'}")
