#include "LvcBuffer.hpp"
#include <iostream>
#include <utility>

LvcBuffer::LvcBuffer(int oe_pin)
    : oe_pin_(oe_pin), enabled_(false) {
    // Ініціалізація апаратного піна: налаштування на вихід, встановлення HIGH (Hi-Z за замовчуванням)
    write_pin(true);
    std::cout << "[LvcBuffer] Пін /OE #" << oe_pin_ << " ініціалізовано у стані Hi-Z (ВИМКНЕНО).\n";
}

LvcBuffer::~LvcBuffer() {
    // RAII: гарантоване вимкнення при знищенні об'єкта або виході з області видимості
    disable();
    std::cout << "[LvcBuffer] Деструктор: пін /OE #" << oe_pin_ << " переведено у безпечний стан Hi-Z.\n";
}

LvcBuffer::LvcBuffer(LvcBuffer&& other) noexcept
    : oe_pin_(other.oe_pin_), enabled_(other.enabled_) {
    other.oe_pin_ = -1;
    other.enabled_ = false;
}

LvcBuffer& LvcBuffer::operator=(LvcBuffer&& other) noexcept {
    if (this != &other) {
        disable(); // вимикаємо поточний
        oe_pin_ = other.oe_pin_;
        enabled_ = other.enabled_;
        other.oe_pin_ = -1;
        other.enabled_ = false;
    }
    return *this;
}

void LvcBuffer::enable() {
    if (!enabled_) {
        write_pin(false); // Активний рівень LOW для /OE у 74LVC1G125
        enabled_ = true;
        std::cout << "[LvcBuffer] Пін /OE #" << oe_pin_ << " УВІМКНЕНО (виходи активні).\n";
    }
}

void LvcBuffer::disable() {
    if (enabled_) {
        write_pin(true); // Неактивний рівень HIGH (Hi-Z)
        enabled_ = false;
        std::cout << "[LvcBuffer] Пін /OE #" << oe_pin_ << " ВИМКНЕНО (стан Hi-Z).\n";
    }
}

bool LvcBuffer::is_enabled() const noexcept {
    return enabled_;
}

void LvcBuffer::switch_to(LvcBuffer& to_enable, std::chrono::microseconds delay) {
    std::cout << "[LvcBuffer] Початок перемикання шини (break-before-make)...\n";
    // 1. Спочатку вимикаємо поточний буфер (Break)
    this->disable();
    
    // 2. Витримуємо захисну паузу для запобігання колізіям на шині (Dead time / guard interval)
    std::this_thread::sleep_for(delay);
    
    // 3. Увімкнення нового буфера (Make)
    to_enable.enable();
    std::cout << "[LvcBuffer] Перемикання завершено успішно.\n";
}

void LvcBuffer::write_pin(bool high) {
    // Симуляція взаємодії з апаратним рівнем GPIO /OE
    // У реальному мікроконтролері чи платформі тут викликається відповідний HAL (наприклад, digitalWrite)
    // Високий рівень (true) -> Hi-Z, Низький рівень (false) -> передача даних
    (void)high;
}
