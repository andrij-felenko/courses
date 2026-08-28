/* Згенерована запакована структура C */
MAVPACKED(
typedef struct __mavlink_payload_spectral_status_t {
    uint32_t time_boot_ms;        /*< [ms] Час роботи */
    float integration_time_ms;   /*< [ms] Час інтегрування */
    float sensor_temperature;    /*< [degC] Температура */
    uint16_t spectral_irradiance;/*< [mW/m^2] Освітленість */
    uint8_t filter_mode;         /*< Активний фільтр */
    uint8_t status_flags;        /*< Прапорці */
    uint32_t calibration_crc;    /*< [ext] Контрольна сума калібрування */
    uint8_t gain_level;          /*< [ext] Підсилення */
}) mavlink_payload_spectral_status_t;
