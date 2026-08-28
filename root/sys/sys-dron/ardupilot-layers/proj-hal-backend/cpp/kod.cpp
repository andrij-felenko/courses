// AP_HAL: чистий інтерфейс — що ВМІЄ будь-який послідовний порт.
// Жодної реалізації; самі суто віртуальні методи (= 0).
namespace AP_HAL {
class UARTDriver {
public:
    virtual void     begin(uint32_t baud) = 0;   // відкрити порт на швидкості
    virtual size_t   write(uint8_t b)      = 0;   // надіслати один байт
    virtual int16_t  read()                = 0;   // прийняти байт (−1 якщо порожньо)
    virtual uint32_t available()           = 0;   // скільки байтів чекає
    virtual ~UARTDriver() {}                       // віртуальний деструктор — обов'язково
};
}
