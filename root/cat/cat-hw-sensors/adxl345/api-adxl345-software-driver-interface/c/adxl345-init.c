#define ADXL345_REG_DEVID 0x00
#define ADXL345_DEVICE_ID 0xE5

typedef enum {
    ADXL345_OK = 0,
    ADXL345_ERR_BUS = -1,
    ADXL345_ERR_DEV_NOT_FOUND = -2
} adxl345_err_t;

typedef struct {
    adxl345_hal_t hal;
    uint8_t       dev_id;
} adxl345_dev_t;

adxl345_err_t adxl345_init(adxl345_dev_t *dev, adxl345_hal_t hal) {
    if (!dev || !hal.read || !hal.write) return ADXL345_ERR_BUS;
    dev->hal = hal;
    uint8_t id = 0;
    if (dev->hal.read(dev->hal.handle, ADXL345_REG_DEVID, &id, 1) != 0) {
        return ADXL345_ERR_BUS;
    }
    if (id != ADXL345_DEVICE_ID) {
        return ADXL345_ERR_DEV_NOT_FOUND;
    }
    dev->dev_id = id;
    return ADXL345_OK;
}
