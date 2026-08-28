# Повертає температуру в °C, роздільність 0.01 °C.
# Значення "5123" означає 51.23 °C.
# t_fine несе точну температуру; тут повертаємо кортеж (T, t_fine).
def bmp280_compensate_T_int32(adc_T, dig_T1, dig_T2, dig_T3):
    var1 = (((adc_T >> 3) - (dig_T1 << 1)) * dig_T2) >> 11
    var2 = (((((adc_T >> 4) - dig_T1) *
              ((adc_T >> 4) - dig_T1)) >> 12) * dig_T3) >> 14
    t_fine = var1 + var2
    T = (t_fine * 5 + 128) >> 8
    return T, t_fine
