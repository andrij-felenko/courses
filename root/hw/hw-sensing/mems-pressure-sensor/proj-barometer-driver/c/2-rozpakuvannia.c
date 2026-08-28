BaroStatus baro_parse_calibration(MemsBarometer *dev, const uint8_t *raw_nvm) {
    if (!dev || !raw_nvm) return BARO_ERR_COMM;

    // Збирання сирих 16-бітних та 8-бітних слів із буфера NVM
    uint16_t raw_t1 = (uint16_t)(raw_nvm[0] | (raw_nvm[1] << 8));
    uint16_t raw_t2 = (uint16_t)(raw_nvm[2] | (raw_nvm[3] << 8));
    int8_t   raw_t3 = (int8_t)raw_nvm[4];

    int16_t  raw_p1 = (int16_t)(raw_nvm[5] | (raw_nvm[6] << 8));
    int16_t  raw_p2 = (int16_t)(raw_nvm[7] | (raw_nvm[8] << 8));
    int8_t   raw_p3 = (int8_t)raw_nvm[9];
    int8_t   raw_p4 = (int8_t)raw_nvm[10];
    uint16_t raw_p5 = (uint16_t)(raw_nvm[11] | (raw_nvm[12] << 8));
    uint16_t raw_p6 = (uint16_t)(raw_nvm[13] | (raw_nvm[14] << 8));
    int8_t   raw_p7 = (int8_t)raw_nvm[15];
    int8_t   raw_p8 = (int8_t)raw_nvm[16];
    int16_t  raw_p9 = (int16_t)(raw_nvm[17] | (raw_nvm[18] << 8));
    int8_t   raw_p10 = (int8_t)raw_nvm[19];
    int8_t   raw_p11 = (int8_t)raw_nvm[20];

    // Масштабування за специфікацією виробника
    dev->calib.t1 = (double)raw_t1 * 256.0;                    // множник 2^-8
    dev->calib.t2 = (double)raw_t2 / 1073741824.0;             // дільник 2^30
    dev->calib.t3 = (double)raw_t3 / 281474976710656.0;        // дільник 2^48

    dev->calib.p1 = ((double)raw_p1 - 16384.0) / 1048576.0;    // зміщення 2^14, дільник 2^20
    dev->calib.p2 = ((double)raw_p2 - 16384.0) / 536870912.0;  // зміщення 2^14, дільник 2^29
    dev->calib.p3 = (double)raw_p3 / 4294967296.0;             // дільник 2^32
    dev->calib.p4 = (double)raw_p4 / 137438953472.0;           // дільник 2^37
    dev->calib.p5 = (double)raw_p5 * 8.0;                      // множник 2^-3
    dev->calib.p6 = (double)raw_p6 / 64.0;                     // дільник 2^6
    dev->calib.p7 = (double)raw_p7 / 256.0;                    // дільник 2^8
    dev->calib.p8 = (double)raw_p8 / 32768.0;                  // дільник 2^15
    dev->calib.p9 = (double)raw_p9 / 281474976710656.0;        // дільник 2^48
    dev->calib.p10 = (double)raw_p10 / 281474976710656.0;      // дільник 2^48
    dev->calib.p11 = (double)raw_p11 / 36893488147419103232.0; // дільник 2^65

    return BARO_OK;
}
