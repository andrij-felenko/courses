bmp280_status_t bmp280_compensate(bmp280_handle_t *dev, const uint8_t *raw_6b, bmp280_sample_t *out_sample) {
    if ((dev == NULL) || (raw_6b == NULL) || (out_sample == NULL)) {
        return BMP280_ERR_NULL_PTR;
    }

    /* 1. Розпаковка 20-бітних кодів АЦП */
    int32_t adc_P = (int32_t)((((uint32_t)raw_6b[0]) << 12) |
                             (((uint32_t)raw_6b[1]) << 4)  |
                             (((uint32_t)raw_6b[2]) >> 4));

    int32_t adc_T = (int32_t)((((uint32_t)raw_6b[3]) << 12) |
                             (((uint32_t)raw_6b[4]) << 4)  |
                             (((uint32_t)raw_6b[5]) >> 4));

    /* 2. Температурна компенсація (32 біти) */
    int32_t var1_T = ((((adc_T >> 3) - ((int32_t)dev->calib.dig_T1 << 1))) * ((int32_t)dev->calib.dig_T2)) >> 11;
    int32_t var2_T = (((((adc_T >> 4) - ((int32_t)dev->calib.dig_T1)) *
                       ((adc_T >> 4) - ((int32_t)dev->calib.dig_T1))) >> 12) *
                      ((int32_t)dev->calib.dig_T3)) >> 14;

    dev->t_fine = var1_T + var2_T;
    out_sample->temperature_centidegrees = (dev->t_fine * 5 + 128) >> 8;

    /* 3. Компенсація тиску на 64-бітних цілих (захист від переповнення) */
    int64_t var1_P = ((int64_t)dev->t_fine) - 128000;
    int64_t var2_P = var1_P * var1_P * (int64_t)dev->calib.dig_P6;
    var2_P = var2_P + ((var1_P * (int64_t)dev->calib.dig_P5) << 17);
    var2_P = var2_P + (((int64_t)dev->calib.dig_P4) << 35);
    var1_P = ((var1_P * var1_P * (int64_t)dev->calib.dig_P3) >> 8) +
             ((var1_P * (int64_t)dev->calib.dig_P2) << 12);
    var1_P = (((((int64_t)1) << 47) + var1_P)) * ((int64_t)dev->calib.dig_P1) >> 33;

    if (var1_P == 0) {
        out_sample->pressure_pascals = 0;
        out_sample->valid = false;
        return BMP280_ERR_OVERFLOW;
    }

    int64_t p = 1048576 - adc_P;
    p = (((p << 31) - var2_P) * 3125) / var1_P;
    var1_P = (((int64_t)dev->calib.dig_P9) * (p >> 13) * (p >> 13)) >> 25;
    var2_P = (((int64_t)dev->calib.dig_P8) * p) >> 19;

    p = ((p + var1_P + var2_P) >> 8) + (((int64_t)dev->calib.dig_P7) << 4);

    out_sample->pressure_q24_8 = (uint32_t)p;
    out_sample->pressure_pascals = (uint32_t)(p >> 8);
    out_sample->valid = true;

    return BMP280_OK;
}
