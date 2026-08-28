def bmp280_compensate_P_double(adc_P, t_fine, dig_P):
    var1 = (t_fine / 2.0) - 64000.0
    var2 = var1 * var1 * dig_P[6] / 32768.0
    var2 = var2 + var1 * dig_P[5] * 2.0
    var2 = (var2 / 4.0) + (dig_P[4] * 65536.0)
    var1 = (dig_P[3] * var1 * var1 / 524288.0 +
            dig_P[2] * var1) / 524288.0
    var1 = (1.0 + var1 / 32768.0) * dig_P[1]
    if var1 == 0.0:
        return 0
    p = 1048576.0 - adc_P
    p = (p - (var2 / 4096.0)) * 6250.0 / var1
    var1 = dig_P[9] * p * p / 2147483648.0
    var2 = p * dig_P[8] / 32768.0
    p = p + (var1 + var2 + dig_P[7]) / 16.0
    return p    # тиск одразу в Pa, дробом
