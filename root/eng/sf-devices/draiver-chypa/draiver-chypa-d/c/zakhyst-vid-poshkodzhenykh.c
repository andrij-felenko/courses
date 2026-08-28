bmp280_status_t bmp280_validate_calibration(const bmp280_calib_data_t *calib) {
    if (calib == NULL) {
        return BMP280_ERR_NULL_PTR;
    }
    /* Коефіцієнти dig_T1 та dig_P1 є дільниками у формулах і не можуть бути 0 або 0xFFFF */
    if ((calib->dig_T1 == 0x0000U) || (calib->dig_T1 == 0xFFFFU)) {
        return BMP280_ERR_CRC_MISMATCH;
    }
    if ((calib->dig_P1 == 0x0000U) || (calib->dig_P1 == 0xFFFFU)) {
        return BMP280_ERR_CRC_MISMATCH;
    }
    return BMP280_OK;
}
