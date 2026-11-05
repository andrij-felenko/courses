#include "Ws2812bBuffer.hpp"
#include <thread>
#include <chrono>
#include <iostream>

/**
 * @file Ws2812bBuffer.cpp
 * @brief Реалізація методів класу Ws2812bBuffer для керування 74AHCT125 та генерації NRZ-сигналів WS2812B.
 */

namespace hardware {

Ws2812bBuffer::Ws2812bBuffer(int oe_pin, int data_pin)
    : oe_pin_(oe_pin), data_pin_(data_pin), is_enabled_(false) {
    // Імітація ініціалізації апаратних пінів GPIO мікроконтролера:
    // 1. Пін /OE переводиться у високий рівень (HIGH) для безпечного високоімпедансного стану (Hi-Z)
    // 2. Пін даних переводиться у вихідний режим зі стабільним низьким рівнем (LOW)
    std::cout << "[GPIO Init] Конфігурація піна /OE (" << oe_pin_ 
              << ") як OUTPUT. Початковий стан: HIGH (буфер вимкнено, Hi-Z).\n";
    std::cout << "[GPIO Init] Конфігурація піна DATA (" << data_pin_ 
              << ") як OUTPUT. Початковий стан: LOW.\n";
    
    // Апаратно встановлюємо /OE = HIGH (вимкнено)
    disable();
}

Ws2812bBuffer::~Ws2812bBuffer() {
    // RAII гарантує безпечне вимкнення буфера (переведення у Hi-Z) при знищенні об'єкта
    disable();
    std::cout << "[RAII Destructor] Буфер 74AHCT125 (пін /OE: " << oe_pin_ 
              << ") безпечно переведено у стан Hi-Z, ресурси звільнено.\n";
}

Ws2812bBuffer::Ws2812bBuffer(Ws2812bBuffer&& other) noexcept
    : oe_pin_(other.oe_pin_),
      data_pin_(other.data_pin_),
      is_enabled_(other.is_enabled_),
      timings_(other.timings_) {
    other.oe_pin_ = -1;
    other.data_pin_ = -1;
    other.is_enabled_ = false;
}

Ws2812bBuffer& Ws2812bBuffer::operator=(Ws2812bBuffer&& other) noexcept {
    if (this != &other) {
        disable();
        oe_pin_ = other.oe_pin_;
        data_pin_ = other.data_pin_;
        is_enabled_ = other.is_enabled_;
        timings_ = other.timings_;

        other.oe_pin_ = -1;
        other.data_pin_ = -1;
        other.is_enabled_ = false;
    }
    return *this;
}

void Ws2812bBuffer::enable() {
    if (!is_enabled_) {
        is_enabled_ = true;
        // Активний рівень для /OE у 74AHCT125 — LOW (0 В). 
        // Це відкриває буфер і забезпечує трансляцію 3.3В логіки в чисті 5В рівні.
        std::cout << "[74AHCT125] Пін /OE (" << oe_pin_ << ") встановлено в LOW. Буфер увімкнено (трансляція 5В активна).\n";
    }
}

void Ws2812bBuffer::disable() {
    if (is_enabled_ || oe_pin_ != -1) {
        is_enabled_ = false;
        // Неактивний рівень /OE — HIGH (3.3В підтяжка). 
        // Виходи буфера переходять у високоімпедансний стан (Hi-Z), захищаючи лінію від наведень.
        std::cout << "[74AHCT125] Пін /OE (" << oe_pin_ << ") встановлено в HIGH. Буфер вимкнено (стан Hi-Z).\n";
    }
}

bool Ws2812bBuffer::isEnabled() const noexcept {
    return is_enabled_;
}

void Ws2812bBuffer::setTimings(const Ws2812Timings& timings) noexcept {
    timings_ = timings;
}

void Ws2812bBuffer::writeBit(bool bit) {
    // У реальному вбудованому коді тут використовується швидкісний GPIO-регістр, 
    // DMA+SPI або RMT (Remote Control) периферія для наносекундної точності.
    // Для демонстрації архітектури демонструємо логіку бітових інтервалів.
    if (bit) {
        // Передача логічної '1': високий рівень T1H, потім низький T1L
    } else {
        // Передача логічного '0': високий рівень T0H, потім низький T0L
    }
}

void Ws2812bBuffer::sendPixels(std::span<const Color> pixels) {
    if (!is_enabled_) {
        std::cerr << "[Попередження] Спроба передачі даних при вимкненому буфері! Буфер автоматично активується.\n";
        enable();
    }

    std::cout << "[WS2812B] Початок передачі кадру з " << pixels.size() << " пікселів у форматі GRB.\n";

    for (const auto& pixel : pixels) {
        // Послідовне пакування каналів у порядку GRB (Green, Red, Blue), починаючи з старшого біта (MSB)
        uint32_t grb_packet = (static_cast<uint32_t>(pixel.g) << 16) |
                              (static_cast<uint32_t>(pixel.r) << 8)  |
                              static_cast<uint32_t>(pixel.b);

        // Передача 24 біт (по 8 біт на кожен канал G, R, B)
        for (int i = 23; i >= 0; --i) {
            bool bit = (grb_packet >> i) & 1;
            writeBit(bit);
        }
    }

    // Завершення кадру імпульсом скидання
    sendReset();
}

void Ws2812bBuffer::sendReset() {
    // Утримання лінії у низькому стані довше за час мікросхемного скидання (зазвичай > 280-300 мкс)
    std::this_thread::sleep_for(std::chrono::microseconds(timings_.reset_us));
    std::cout << "[WS2812B] Імпульс Reset завершено. Кадр защолкнуто в стрічці.\n";
}

} // namespace hardware
