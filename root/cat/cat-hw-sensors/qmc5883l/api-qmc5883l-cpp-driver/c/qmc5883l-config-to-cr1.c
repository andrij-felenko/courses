#include <stdint.h>

typedef enum {
    QMC5883L_ODR_10HZ  = 0x00,
    QMC5883L_ODR_50HZ  = 0x04,
    QMC5883L_ODR_100HZ = 0x08,
    QMC5883L_ODR_200HZ = 0x0C
} qmc5883l_odr_t;

typedef enum {
    QMC5883L_RANGE_2G = 0x00,
    QMC5883L_RANGE_8G = 0x10
} qmc5883l_range_t;

typedef enum {
    QMC5883L_OSR_512 = 0x00,
    QMC5883L_OSR_256 = 0x40,
    QMC5883L_OSR_128 = 0x80,
    QMC5883L_OSR_64  = 0xC0
} qmc5883l_osr_t;

typedef enum {
    QMC5883L_MODE_STANDBY    = 0x00,
    QMC5883L_MODE_CONTINUOUS = 0x01
} qmc5883l_mode_t;

typedef struct {
    qmc5883l_odr_t   odr;
    qmc5883l_range_t range;
    qmc5883l_osr_t   osr;
    qmc5883l_mode_t  mode;
} qmc5883l_config_t;

static inline uint8_t qmc5883l_config_to_cr1(const qmc5883l_config_t* config) {
    return (uint8_t)(config->odr | config->range | config->osr | config->mode);
}
