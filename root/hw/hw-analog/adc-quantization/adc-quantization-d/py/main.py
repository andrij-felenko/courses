import math

# Граничний SNR ідеального N-розрядного АЦП (повношкальна синусоїда), дБ.
def ideal_adc_snr_db(bits: int) -> float:
    return 6.02 * bits + 1.76

# Скільки розрядів треба, щоб дотягти до заданого SNR (округлення вгору).
def bits_for_snr(target_db: float) -> int:
    n = (target_db - 1.76) / 6.02   # обернена формула
    return math.ceil(n)             # дробовий розряд не буває — вгору

def main() -> None:
    need = 80.0
    n = bits_for_snr(need)                    # (80 - 1.76)/6.02 = 13.0 -> 13
    print(f"Для {need:.0f} дБ треба {n} розрядів; "
          f"вони дають {ideal_adc_snr_db(n):.1f} дБ")    # 13 біт -> 80.0 дБ
    print(f"14 розрядів дали б {ideal_adc_snr_db(14):.1f} дБ "
          f"(запас на залізо)")                          # 86.0 дБ

if __name__ == "__main__":
    main()
