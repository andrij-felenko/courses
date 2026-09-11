// Драйвер привода MG90S на базі 16-бітного апаратного таймера Timer1 (ATmega328P)
#include <Arduino.h>

class MG90SServo {
public:
    MG90SServo() 
        : pin_(9), min_us_(540), max_us_(2400), current_us_(1500), attached_(false) {}

    // Ініціалізація виводу та встановлення безпечних меж імпульсів
    bool attach(uint8_t pin, uint16_t min_us = 540, uint16_t max_us = 2400) {
        // Апаратний Fast PWM на Timer1 підтримує виводи 9 (OC1A / PB1) та 10 (OC1B / PB2)
        if (pin != 9 && pin != 10) {
            return false;
        }

        pin_ = pin;
        min_us_ = min_us;
        max_us_ = max_us;

        pinMode(pin_, OUTPUT);
        digitalWrite(pin_, LOW);

        // Налаштування Timer1: режим Fast PWM 14 (TOP = ICR1), переддільник 8
        // При тактовій частоті 16 МГц один такт таймера дорівнює 0.5 мкс
        TCCR1A = _BV(WGM11);
        TCCR1B = _BV(WGM13) | _BV(WGM12) | _BV(CS11);

        // Встановлення періоду 20 мс (50 Гц): 20 000 мкс / 0.5 мкс = 40 000 тактів
        ICR1 = 40000 - 1;

        // Підключення виходу таймера до відповідного виводу
        if (pin_ == 9) {
            TCCR1A |= _BV(COM1A1);
        } else {
            TCCR1A |= _BV(COM1B1);
        }

        attached_ = true;
        // Встановлення вала у безпечне центральне положення (90 градусів)
        write_microseconds((min_us_ + max_us_) / 2);
        return true;
    }

    // Встановлення тривалості імпульсу в мікросекундах із захисним обмеженням
    void write_microseconds(uint16_t us) {
        if (!attached_) {
            return;
        }

        // Захист від виходу за калібровані межі та механічного клину
        if (us < min_us_) {
            us = min_us_;
        } else if (us > max_us_) {
            us = max_us_;
        }

        current_us_ = us;

        // Перерахунок мікросекунд у такти таймера (1 мкс = 2 такти при дільнику 8)
        uint16_t ticks = us * 2;

        if (pin_ == 9) {
            OCR1A = ticks;
        } else {
            OCR1B = ticks;
        }
    }

    // Встановлення кута від 0 до 180 градусів через лінійну інтерполяцію
    void write_angle(float angle) {
        if (angle < 0.0f) {
            angle = 0.0f;
        } else if (angle > 180.0f) {
            angle = 180.0f;
        }

        // Лінійне переведення кута у мікросекунди без плаваючої коми
        uint32_t span = max_us_ - min_us_;
        uint16_t us = min_us_ + static_cast<uint16_t>((static_cast<uint32_t>(angle * 10.0f) * span) / 1800U);

        write_microseconds(us);
    }

    // Зняття керуючого сигналу для вимкнення H-моста та усунення нагріву двигуна
    void detach() {
        if (!attached_) {
            return;
        }

        // Відключення генерації ШІМ на виводі мікроконтролера
        if (pin_ == 9) {
            TCCR1A &= ~_BV(COM1A1);
        } else {
            TCCR1A &= ~_BV(COM1B1);
        }

        digitalWrite(pin_, LOW);
        attached_ = false;
    }

    uint16_t read_microseconds() const {
        return current_us_;
    }

    bool is_attached() const {
        return attached_;
    }

private:
    uint8_t pin_;
    uint16_t min_us_;
    uint16_t max_us_;
    uint16_t current_us_;
    bool attached_;
};
