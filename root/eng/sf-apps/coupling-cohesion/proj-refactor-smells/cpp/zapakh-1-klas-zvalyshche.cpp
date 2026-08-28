// SensorUtils: звалище. Що спільного? Слово "sensor" у назві файлу — і все.
class SensorUtils {
public:
    static float   celsiusFromRaw(uint16_t raw);      // математика перетворення
    static uint8_t crc8(const uint8_t* d, size_t n);  // контрольна сума I²C
    static void    logReading(float t);               // запис у кільцевий буфер
    static bool    isPlausible(float t);              // перевірка діапазону
    static uint32_t millisSinceBoot();                // обгортка над таймером
    static void    blinkError(uint8_t code);          // блимання світлодіодом
    // …ще п'ять таких самих різнорідних
};
