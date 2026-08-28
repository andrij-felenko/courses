import math

f0       = 100e6    # такт, Гц
harmonic = 5        # проблемна гармоніка
spread   = 0.005    # 0.5 %  розмаз униз
rbw      = 120e3    # вікно приймача CISPR, Гц

f_harm  = harmonic * f0            # 500 МГц — де стоїть спиця
df      = spread * f_harm          # абсолютний обшир розмазу на цій гармоніці
gain_dB = 10.0 * math.log10(df / rbw)  # наближене падіння піку

print(f"гармоніка : {f_harm / 1e6:.0f} МГц")
print(f"розмаз Δf  : {df / 1e6:.2f} МГц ({spread * 100:.1f} % від гармоніки)")
print(f"вікно RBW  : {rbw / 1e3:.0f} кГц")
print(f"падіння піку ~ {gain_dB:.1f} дБ")

margin_before = -6.0               # було: на 6 дБ ВИЩЕ межі
margin_after  = margin_before + gain_dB
verdict = "(проходить)" if margin_after > 0 else "(усе ще завалено)"
print(f"запас до межі: {margin_before:.1f} дБ → {margin_after:.1f} дБ  {verdict}")
