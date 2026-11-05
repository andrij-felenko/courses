#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>

// Апаратні константи для прикладу (наприклад, STM32-подібне середовище або абстракція)
namespace hw {
    // Умовні адреси та піни
    constexpr uint32_t PIN_OE_N = 1 << 2;  // Output Enable (Active Low для 74AHCT245)
    constexpr uint32_t PIN_DIR  = 1 << 3;  // Direction (HIGH = A to B)
}

/**
 * @brief RAII-охоронець для шини 74AHCT245.
 * Керує станом напрямку та виходів буфера для запобігання нестабільним станам напруги.
 */
class AhctBusGuard {
public:
    enum class Direction {
        Input,
        Output
    };

    explicit AhctBusGuard(Direction dir) {
        // Увімкнення апаратного живлення / рівня шини
        enableBus();
        setDirection(dir);
    }

    ~AhctBusGuard() {
        // Безпечне вимкнення виходів (Output Enable -> HIGH / Z-стан) перед знищенням
        disableBus();
    }

    // Заборона копіювання для уникнення подвійного керування апаратним ресурсом
    AhctBusGuard(const AhctBusGuard&) = delete;
    AhctBusGuard& operator=(const AhctBusGuard&) = delete;

    // Дозволено переміщення
    AhctBusGuard(AhctBusGuard&&) noexcept = default;
    AhctBusGuard& operator=(AhctBusGuard&&) noexcept = default;

private:
    void enableBus() {
        // Низький рівень на OE (Output Enable) активує буфер 74AHCT
        // Наприклад: GPIO_Port->ODR &= ~hw::PIN_OE_N;
    }

    void disableBus() {
        // Високий рівень на OE переводить виходи у високоімпедансний стан (Z)
        // Наприклад: GPIO_Port->ODR |= hw::PIN_OE_N;
    }

    void setDirection(Direction dir) {
        if (dir == Direction::Output) {
            // Встановлення напрямку від мікроконтролера (3.3V) до периферії (5V 74AHCT)
            // GPIO_Port->ODR |= hw::PIN_DIR;
        } else {
            // Напрямок від периферії до контролера
            // GPIO_Port->ODR &= ~hw::PIN_DIR;
        }
    }
};

/**
 * @brief Колірна структура пікселя RGB / GRB.
 */
struct Pixel {
    uint8_t g;
    uint8_t r;
    uint8_t b;
};

/**
 * @brief Драйвер світлодіодів WS2812B через SPI з використанням буфера та 74AHCT рівня.
 * Транслює байти кольору у SPI біти (швидкий протокол передачі для 800kHz).
 */
class Ws2812SpiDriver {
public:
    explicit Ws2812SpiDriver(std::span<uint8_8_t> spiBuffer) : spiTxBuffer_(spiBuffer) {} // Виправлення під синтаксис span
    
    // Альтернативний конструктор для правильного типу
    explicit Ws2812SpiDriver(std::span<uint8_t> spiBuffer) : spiTxBuffer_(spiBuffer) {}

    /**
     * @brief Кодує масив піксерів у SPI-буфер для подальшої відправки через DMA/SPI.
     * Кожен біт '0' кодується як певна комбінація бітів SPI (наприклад, 0b1100 для 8MHz SPI),
     * а '1' як 0b1110. Тут використовується спрощене транслірування байтів.
     */
    size_t encodePixels(std::span<const Pixel> pixels) {
        size_t byteIndex = 0;
        
        for (const auto& px : pixels) {
            // WS2812B очікує порядок GRB
            uint8_t bytes[3] = {px.g, px.r, px.b};
            
            for (uint8_t b : bytes) {
                for (int i = 7; i >= 0; --i) {
                    bool bit = (b >> i) & 1;
                    if (byteIndex < spiTxBuffer_.size()) {
                        // Імітація кодування біта у SPI патерн (наприклад, високий імпульс)
                        spiTxBuffer_[byteIndex++] = bit ? 0xFC : 0xC0;
                    } else {
                        // Помилка переповнення буфера
                        return byteIndex;
                    }
                }
            }
        }
        return byteIndex;
    }

private:
    std::span<uint8_t> spiTxBuffer_;
};
