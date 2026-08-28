// Бекенд ChibiOS: те саме «обличчя», але тіла говорять із залізом STM32.
class UARTDriver_ChibiOS : public AP_HAL::UARTDriver {
    SerialDriver *sd;                 // дескриптор периферії UART плати
public:
    UARTDriver_ChibiOS(SerialDriver *s) : sd(s) {}

    void begin(uint32_t baud) override {
        sdStart(sd, baud);            // налаштувати швидкість на залізі
    }
    size_t write(uint8_t b) override {
        return sdPut(sd, b);          // байт → апаратний регістр передавання
    }
    int16_t read() override {
        return sdGetTimeout(sd, 0);   // байт з апаратного буфера прийому
    }
    uint32_t available() override {
        return sdBytesPending(sd);
    }
};
