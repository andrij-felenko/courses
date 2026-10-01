// Опис конфігурації та функції ініціалізації мовою C
typedef struct {
    void *i2c_handle;          // Вказівник на апаратний контролер I2C
    uint8_t aht20_addr;        // Адреса AHT20 (зазвичай 0x38)
    uint8_t bmp280_addr;       // Адреса BMP280 (0x76 або 0x77)
    uint8_t bmp280_osrs_t;     // Передискретизація температури BMP280
    uint8_t bmp280_osrs_p;     // Передискретизація тиску BMP280
} aht20_bmp280_config_t;

typedef struct {
    uint16_t dig_T1; int16_t dig_T2, dig_T3;
    uint16_t dig_P1; int16_t dig_P2, dig_P3, dig_P4, dig_P5, dig_P6, dig_P7, dig_P8, dig_P9;
} bmp280_calib_t;

typedef struct {
    aht20_bmp280_config_t cfg;
    bmp280_calib_t bmp_calib;
    bool is_initialized;
} combo_sensor_t;

int combo_sensor_init(combo_sensor_t *dev, const aht20_bmp280_config_t *cfg);
