// C99 цілочисельна компенсація вологості
uint32_t bme280_compensate_H_int32(int32_t adc_H, int32_t t_fine, const bme280_calib_t* calib) {
    int32_t v_x1_u32r = (t_fine - ((int32_t)76800));
    v_x1_u32r = (((((adc_H << 14) - (((int32_t)calib->dig_H4) << 20) - (((int32_t)calib->dig_H5) * v_x1_u32r)) + 16384) >> 15) *
                 (((((((v_x1_u32r * ((int32_t)calib->dig_H6)) >> 10) * (((v_x1_u32r * ((int32_t)calib->dig_H3)) >> 11) + 32768)) >> 10) + 2097152) *
                  ((int32_t)calib->dig_H2) + 8192) >> 14));
    v_x1_u32r = (v_x1_u32r - (((((v_x1_u32r >> 15) * (v_x1_u32r >> 15)) >> 7) * ((int32_t)calib->dig_H1)) >> 4));
    v_x1_u32r = (v_x1_u32r < 0 ? 0 : v_x1_u32r);
    v_x1_u32r = (v_x1_u32r > 419430400 ? 419430400 : v_x1_u32r);
    return (uint32_t)(v_x1_u32r >> 12);
}
