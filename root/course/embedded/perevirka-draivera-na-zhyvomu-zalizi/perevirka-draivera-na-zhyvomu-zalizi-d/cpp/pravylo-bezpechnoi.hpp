// Коректне переведення інтерфейсу в енергозберігаючий стан на C++ з RAII-вартою
class LowPowerPinGuard {
public:
    LowPowerPinGuard() noexcept {
        isolatePins();
    }
    ~LowPowerPinGuard() noexcept {
        restorePins();
    }
    LowPowerPinGuard(const LowPowerPinGuard&) = delete;
    LowPowerPinGuard& operator=(const LowPowerPinGuard&) = delete;

private:
    void isolatePins() noexcept {
        // Переведення ліній SCK, MISO, MOSI, CS у режим Analog High-Z
        setPinModeAnalog(Pin::SCK | Pin::MISO | Pin::MOSI | Pin::CS);
    }
    void restorePins() noexcept {
        // Відновлення апаратних функцій SPI
        setPinModeAlternate(Pin::SCK | Pin::MISO | Pin::MOSI | Pin::CS);
    }
};
