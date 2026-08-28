import math

# amp[0] — основна (1-ша гармоніка), amp[1:] — 2-га, 3-тя, ...
def thd_from_harmonics(amp):
    fund = amp[0]                          # основна гармоніка, U₁
    if fund <= 0.0:
        return 0.0                         # немає сигналу — THD не визначений

    # сума квадратів вищих гармонік: U₂² + U₃² + ...
    sum_sq = sum(a * a for a in amp[1:])   # від 2-ї (індекс 1) і вище

    return math.sqrt(sum_sq) / fund        # √(ΣUₙ²) / U₁  — частка


def demo():
    # основна 1.000 В; гармоніки 2..7 (типовий спадний «хвіст»)
    amp = [1.000, 0.0120, 0.0050, 0.0020,
           0.0011, 0.0006, 0.0003]

    thd     = thd_from_harmonics(amp)      # √(1.2e-4+2.5e-5+...) /1.0
    thd_pct = thd * 100.0                  # у відсотках
    thd_db  = 20.0 * math.log10(thd)       # у децибелах

    # thd     ≈ 0.0132  (корінь із суми ≈ 0.0132 В при основній 1.000 В)
    # thd_pct ≈ 1.32 %
    # thd_db  ≈ −37.6 dB
    return thd, thd_pct, thd_db
