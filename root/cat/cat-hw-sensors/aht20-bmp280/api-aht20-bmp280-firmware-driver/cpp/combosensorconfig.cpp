// Клас опису драйвера та конфігурації мовою C++
struct ComboSensorConfig {
    void *i2c_handle;
    uint8_t aht20_addr = 0x38;
    uint8_t bmp280_addr = 0x76;
    uint8_t osrs_temp = 1;      // Передискретизація T (x1)
    uint8_t osrs_press = 1;     // Передискретизація P (x1)
};

class ComboSensor {
public:
    explicit ComboSensor(const ComboSensorConfig &config);
    bool begin();
private:
    ComboSensorConfig cfg_;
    struct CalibData {
        uint16_t dig_T1; int16_t dig_T2, dig_T3;
        uint16_t dig_P1; int16_t dig_P2, dig_P3, dig_P4, dig_P5, dig_P6, dig_P7, dig_P8, dig_P9;
    } calib_;
    bool initialized_ = false;
};
