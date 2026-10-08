#pragma once

#include "dma_spi_hardware.hpp"
#include <cstdint>
#include <cstddef>
#include <array>
#include <algorithm>

namespace embedded {

/**
 * @brief Структура для представлення 24-бітного RGB кольору.
 */
struct Color {
    uint8_t r{0};
    uint8_t g{0};
    uint8_t b{0};

    constexpr Color() = default;
    constexpr Color(uint8_t red, uint8_t green, uint8_t blue)
        : r(red), g(green), b(blue) {}

    /**
     * @brief Створення кольору з HSV колірного простору.
     * @param h Відтінок (Hue: 0..255)
     * @param s Насиченість (Saturation: 0..255)
     * @param v Яскравість (Value: 0..255)
     */
    static Color fromHsv(uint8_t h, uint8_t s, uint8_t v);

    /**
     * @brief Лінійна інтерполяція (змішування) двох кольорів.
     * @param c1 Початковий колір.
     * @param c2 Кінцевий колір.
     * @param factor Коефіцієнт змішування (0..255).
     */
    static Color blend(Color c1, Color c2, uint8_t factor);

    /**
     * @brief Масштабування яскравості кольору.
     * @param scale Коефіцієнт яскравості (0..255).
     */
    constexpr Color dim(uint8_t scale) const {
        return Color(
            static_cast<uint8_t>((static_cast<uint16_t>(r) * scale) / 255),
            static_cast<uint8_t>((static_cast<uint16_t>(g) * scale) / 255),
            static_cast<uint8_t>((static_cast<uint16_t>(b) * scale) / 255)
        );
    }

    /**
     * @brief Конвертація кольору у формат байтів GRB (апаратний порядок передачі WS2812B).
     */
    constexpr std::array<uint8_t, 3> toGrbArray() const {
        return {g, r, b};
    }

    constexpr bool operator==(const Color& other) const {
        return r == other.r && g == other.g && b == other.b;
    }

    constexpr bool operator!=(const Color& other) const {
        return !(*this == other);
    }
};

/**
 * @brief Шаблонізований клас фреймбуфера для статичного розрахунку SPI-імпульсів WS2812B.
 * @tparam LedsCount Кількість світлодіодів у стрічці.
 */
template <std::size_t LedsCount>
class FrameBuffer {
public:
    static_assert(LedsCount > 0, "LedsCount must be greater than zero");

    // Для 1 байта каналу WS2812B формуються 3 байти SPI (24 біти SPI для 8 біт даних)
    static constexpr std::size_t BytesPerLed = 9; // 3 канали (GRB) * 3 SPI байти = 9 байтів
    static constexpr std::size_t ResetBytesCount = 24; // > 50 мкс пауза RESET (24 байти зі значенням 0x00)
    static constexpr std::size_t BufferSize = LedsCount * BytesPerLed + ResetBytesCount;

    FrameBuffer() {
        pixels_.fill(Color{0, 0, 0});
        spi_buffer_.fill(0x00);
        updateSpiBuffer();
    }

    /**
     * @brief Встановлення кольору конкретного пікселя.
     */
    void setPixel(std::size_t index, Color color) {
        if (index < LedsCount) {
            pixels_[index] = color;
        }
    }

    /**
     * @brief Отримання поточного кольору пікселя.
     */
    Color getPixel(std::size_t index) const {
        if (index < LedsCount) {
            return pixels_[index];
        }
        return Color{0, 0, 0};
    }

    /**
     * @brief Заповнення всієї стрічки одним кольором.
     */
    void fill(Color color) {
        pixels_.fill(color);
    }

    /**
     * @brief Очищення фреймбуфера (всі пікселі вимкнено).
     */
    void clear() {
        fill(Color{0, 0, 0});
    }

    /**
     * @brief Перетворення кольорів пікселів у кодові SPI-послідовності (T0H / T1H імпульси).
     */
    void updateSpiBuffer() {
        std::size_t buf_idx = 0;
        for (std::size_t i = 0; i < LedsCount; ++i) {
            auto grb = pixels_[i].toGrbArray();
            for (uint8_t color_byte : grb) {
                encodeByteToSpi(color_byte, &spi_buffer_[buf_idx]);
                buf_idx += 3;
            }
        }
        // Гарантуємо, що область RESET заповнена нулями
        std::fill(spi_buffer_.begin() + buf_idx, spi_buffer_.end(), static_cast<uint8_t>(0x00));
    }

    /**
     * @brief Отримання вказівника на сирий буфер для DMA передачі.
     */
    const uint8_t* getRawData() const {
        return spi_buffer_.data();
    }

    /**
     * @brief Отримання розміру сирого SPI-буфера в байтах.
     */
    constexpr std::size_t getRawSize() const {
        return BufferSize;
    }

    /**
     * @brief Кодування одного 8-бітного колірного байта у 3 байти SPI (24 біти імпульсів).
     * біт '0' WS2812B -> SPI 3 біти: 100 (0b100)
     * біт '1' WS2812B -> SPI 3 біти: 110 (0b110)
     */
    static void encodeByteToSpi(uint8_t byte, uint8_t* out_spi) {
        uint32_t pattern = 0;
        for (int i = 7; i >= 0; --i) {
            bool bit = (byte >> i) & 0x01;
            uint32_t spi_bits = bit ? 0b110 : 0b100;
            pattern = (pattern << 3) | spi_bits;
        }
        out_spi[0] = static_cast<uint8_t>((pattern >> 16) & 0xFF);
        out_spi[1] = static_cast<uint8_t>((pattern >> 8) & 0xFF);
        out_spi[2] = static_cast<uint8_t>(pattern & 0xFF);
    }

private:
    std::array<Color, LedsCount> pixels_{};
    std::array<uint8_t, BufferSize> spi_buffer_{};
};

/**
 * @brief Головний шаблонізований драйвер світлодіодної стрічки WS2812B.
 * @tparam LedsCount Кількість світлодіодів.
 */
template <std::size_t LedsCount>
class Ws2812bDriver {
public:
    explicit Ws2812bDriver(DmaSpiHardware& hardware)
        : hardware_(hardware) {}

    /**
     * @brief Ініціалізація апаратних ресурсів та фреймбуфера.
     */
    bool init() {
        if (!hardware_.init()) {
            return false;
        }
        frame_buffer_.clear();
        frame_buffer_.updateSpiBuffer();
        return true;
    }

    /**
     * @brief Встановлення кольору пікселя з урахуванням глобальної яскравості.
     */
    void setPixel(std::size_t index, Color color) {
        Color scaled_color = color.dim(global_brightness_);
        frame_buffer_.setPixel(index, scaled_color);
    }

    /**
     * @brief Отримання поточного кольору пікселя.
     */
    Color getPixel(std::size_t index) const {
        return frame_buffer_.getPixel(index);
    }

    /**
     * @brief Встановлення одного кольору для всіх пікселів.
     */
    void setAll(Color color) {
        Color scaled_color = color.dim(global_brightness_);
        frame_buffer_.fill(scaled_color);
    }

    /**
     * @brief Вимкнення всіх світлодіодів.
     */
    void clear() {
        frame_buffer_.clear();
    }

    /**
     * @brief Встановлення глобального рівня яскравості (0..255).
     */
    void setBrightness(uint8_t brightness) {
        global_brightness_ = brightness;
    }

    /**
     * @brief Отримання поточного рівня яскравості.
     */
    uint8_t getBrightness() const {
        return global_brightness_;
    }

    /**
     * @brief Асинхронний вивід кадру на світлодіодну стрічку через DMA.
     * @return true у разі успішного запуску фонового виводу, false якщо DMA зайнятий.
     */
    bool renderAsync() {
        if (hardware_.isBusy()) {
            return false;
        }
        frame_buffer_.updateSpiBuffer();
        return hardware_.startTransmitDma(frame_buffer_.getRawData(), frame_buffer_.getRawSize());
    }

    /**
     * @brief Перевірка готовності драйвера до виводу нового кадру.
     */
    bool isReady() const {
        return !hardware_.isBusy();
    }

    /**
     * @brief Ефект «Веселка» (Rainbow effect).
     * @param offset Зсув фази кольорової гами.
     */
    void applyRainbow(uint8_t offset) {
        for (std::size_t i = 0; i < LedsCount; ++i) {
            uint8_t hue = static_cast<uint8_t>((i * 255 / LedsCount) + offset);
            setPixel(i, Color::fromHsv(hue, 255, 255));
        }
    }

    /**
     * @brief Ефект «Пульсація» (Breathing effect).
     * @param base_color Базовий колір.
     * @param phase Фаза пульсації (0..255).
     */
    void applyBreathing(Color base_color, uint8_t phase) {
        uint8_t brightness = (phase < 128) ? static_cast<uint8_t>(phase * 2) : static_cast<uint8_t>((255 - phase) * 2);
        Color dimmed = base_color.dim(brightness);
        setAll(dimmed);
    }

    /**
     * @brief Ефект «Біжучий вогонь» (Running Light).
     * @param color Колір голови вогню.
     * @param position Позиція голови вогню.
     * @param tail_length Довжина хвоста згасання.
     */
    void applyRunningLight(Color color, std::size_t position, std::size_t tail_length) {
        clear();
        for (std::size_t i = 0; i < LedsCount; ++i) {
            if (i <= position && (position - i) < tail_length) {
                std::size_t dist = position - i;
                uint8_t scale = static_cast<uint8_t>(255 - (dist * 255 / tail_length));
                setPixel(i, color.dim(scale));
            }
        }
    }

private:
    DmaSpiHardware& hardware_;
    FrameBuffer<LedsCount> frame_buffer_{};
    uint8_t global_brightness_{255};
};

} // namespace embedded
