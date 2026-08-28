// Дім для знання про конкретний давач — правиться при зміні давача
class Tmp117 {
public:
    static float celsius(uint16_t raw) { return raw * 0.0078125f; }  // 7.8125 м°C/LSB
    static bool  plausible(float c)    { return c > -40.0f && c < 125.0f; }
};

// Дім для знання про шину — правиться при зміні протоколу
class I2cFrame {
public:
    static uint8_t crc8(const uint8_t* d, size_t n);  // поліном 0x07, як у SMBus
};

// Дім для логу — правиться при зміні формату/носія
class ReadingLog {
public:
    void append(float celsius);
};
