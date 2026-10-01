#define ADXL345_REG_DATAX0 0x32
#define ADXL345_SCALE_FULL_RES 0.0039f

typedef struct {
    float x;
    float y;
    float z;
} adxl345_data_t;

adxl345_err_t adxl345_read_accel(adxl345_dev_t *dev, adxl345_data_t *data) {
    uint8_t buf[6];
    if (dev->hal.read(dev->hal.handle, ADXL345_REG_DATAX0, buf, 6) != 0) {
        return ADXL345_ERR_BUS;
    }
    int16_t raw_x = (int16_t)((buf[1] << 8) | buf[0]);
    int16_t raw_y = (int16_t)((buf[3] << 8) | buf[2]);
    int16_t raw_z = (int16_t)((buf[5] << 8) | buf[4]);

    data->x = raw_x * ADXL345_SCALE_FULL_RES;
    data->y = raw_y * ADXL345_SCALE_FULL_RES;
    data->z = raw_z * ADXL345_SCALE_FULL_RES;
    return ADXL345_OK;
}
