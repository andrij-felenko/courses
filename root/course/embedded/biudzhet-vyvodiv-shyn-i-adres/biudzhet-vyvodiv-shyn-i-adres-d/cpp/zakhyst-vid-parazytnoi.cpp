#include <cstdint>

class SpiCsDecoder {
public:
    struct GpioConfig {
        uint8_t pinA0;
        uint8_t pinA1;
        uint8_t pinA2;
        uint8_t pinEn;
    };

    explicit SpiCsDecoder(const GpioConfig& cfg) : cfg_(cfg) {
        deselect();
    }

    void select(uint8_t deviceId) const {
        if (deviceId > 7) return;

        /* Блокуємо дешифратор перед зміною адресних бітів */
        setPin(cfg_.pinEn, true);

        setPin(cfg_.pinA0, (deviceId & 0x01) != 0);
        setPin(cfg_.pinA1, (deviceId & 0x02) != 0);
        setPin(cfg_.pinA2, (deviceId & 0x04) != 0);

        /* Активуємо вибрану лінію CS (падає в 0) */
        setPin(cfg_.pinEn, false);
    }

    void deselect() const {
        setPin(cfg_.pinEn, true);
    }

private:
    GpioConfig cfg_;

    static void setPin(uint8_t pin, bool high) {
        /* Низькорівневий запис у регістр GPIO мікроконтролера */
        extern void platform_gpio_write(uint8_t pin, bool level);
        platform_gpio_write(pin, high);
    }
};

/* RAII-обгортка для автоматичного вибору й деселекту SPI пристрою */
class ScopedSpiSelect {
public:
    ScopedSpiSelect(const SpiCsDecoder& decoder, uint8_t deviceId)
        : decoder_(decoder) {
        decoder_.select(deviceId);
    }

    ~ScopedSpiSelect() {
        decoder_.deselect();
    }

    ScopedSpiSelect(const ScopedSpiSelect&) = delete;
    ScopedSpiSelect& operator=(const ScopedSpiSelect&) = delete;

private:
    const SpiCsDecoder& decoder_;
};
