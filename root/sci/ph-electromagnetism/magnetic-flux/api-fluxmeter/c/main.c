#include <stdint.h>
#include <stdbool.h>

#define FLUX_REG_CTRL       0x00
#define FLUX_REG_CONFIG     0x01
#define FLUX_REG_STATUS     0x02
#define FLUX_REG_DATA_0     0x03

#define FLUX_CTRL_ENABLE    (1 << 0)
#define FLUX_CTRL_AUTOZERO  (1 << 1)
#define FLUX_CTRL_START     (1 << 2)

typedef struct {
    uint8_t i2c_address;
    int (*i2c_read)(uint8_t dev_addr, uint8_t reg_addr, uint8_t* data, uint16_t len);
    int (*i2c_write)(uint8_t dev_addr, uint8_t reg_addr, const uint8_t* data, uint16_t len);
    double lsb_to_weber; /* Масштабний коефіцієнт Вб/LSB */
} FluxmeterDevice;

int fluxmeter_init(FluxmeterDevice* dev) {
    if (!dev || !dev->i2c_read || !dev->i2c_write) {
        return -1;
    }
    
    /* Увімкнення пристрою та встановлення частоти 1 кГц */
    uint8_t ctrl_val = FLUX_CTRL_ENABLE;
    if (dev->i2c_write(dev->i2c_address, FLUX_REG_CTRL, &ctrl_val, 1) != 0) {
        return -2;
    }
    
    uint8_t config_val = 0x04; /* 1000 SPS */
    if (dev->i2c_write(dev->i2c_address, FLUX_REG_CONFIG, &config_val, 1) != 0) {
        return -3;
    }
    
    return 0;
}

int fluxmeter_calibrate_zero(FluxmeterDevice* dev) {
    uint8_t ctrl_val = FLUX_CTRL_ENABLE | FLUX_CTRL_AUTOZERO;
    if (dev->i2c_write(dev->i2c_address, FLUX_REG_CTRL, &ctrl_val, 1) != 0) {
        return -1;
    }
    
    /* Очікування завершення калібрування */
    uint8_t status = 0;
    do {
        if (dev->i2c_read(dev->i2c_address, FLUX_REG_STATUS, &status, 1) != 0) {
            return -2;
        }
    } while ((status & (1 << 2)) == 0); /* Перевірка біта CAL_DONE */
    
    return 0;
}

int fluxmeter_read_flux(FluxmeterDevice* dev, double* out_webers) {
    if (!dev || !out_webers) {
        return -1;
    }
    
    uint8_t buffer[3];
    if (dev->i2c_read(dev->i2c_address, FLUX_REG_DATA_0, buffer, 3) != 0) {
        return -2;
    }
    
    /* Збирання 24-бітного числа зі знаком (2's complement) */
    int32_t raw_adc = (int32_t)((uint32_t)buffer[0] | 
                               ((uint32_t)buffer[1] << 8) | 
                               ((uint32_t)buffer[2] << 16));
    
    /* Доповнення знакового біта для 32-бітного integer */
    if (raw_adc & 0x00800000) {
        raw_adc |= 0xFF000000;
    }
    
    *out_webers = (double)raw_adc * dev->lsb_to_weber;
    return 0;
}
