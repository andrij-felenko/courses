# Калібрувальна поправка офсету (виміряна на нульовому вході — еталоні).
ADC_OFFSET  = const(8)    # систематичний зсув, віднімаємо ОДИН раз
ADC_SAMPLES = const(16)   # усереднення: гасить випадковий шум у √16 = 4 рази

def read_adc_corrected():
    acc = 0
    for _ in range(ADC_SAMPLES):
        acc += adc.read_u16()         # 16 сирих вибірок поспіль
    avg = acc // ADC_SAMPLES          # середнє → розкид ±3 стиснувся до ≈ ±0.75

    # систематичний зсув НЕ гаситься усередненням — віднімаємо окремо:
    return avg - ADC_OFFSET if avg > ADC_OFFSET else 0
