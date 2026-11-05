#include <Arduino.h>

/**
 * @brief Клас безконтактного тахометра на основі відбивального сенсора TCRT5000.
 */
class TcrtTachometer {
public:
    static constexpr uint8_t FILTER_SIZE = 8;
    static constexpr uint32_t DEBOUNCE_MICROS = 500;

    TcrtTachometer(uint8_t pin, uint8_t slots_per_rev = 4)
        : _pin(pin), _slots(slots_per_rev), _last_pulse_us(0), _filter_idx(0), _total_pulses(0) {
        for (uint8_t i = 0; i < FILTER_SIZE; i++) {
            _periods_us[i] = 0;
        }
    }

    void begin() {
        pinMode(_pin, INPUT_PULLUP);
        instance = this;
        attachInterrupt(digitalPinToInterrupt(_pin), isrHandler, FALLING);
    }

    float getRPM() {
        uint32_t now = micros();
        noInterrupts();
        uint32_t last_time = _last_pulse_us;
        uint32_t periods_copy[FILTER_SIZE];
        for (uint8_t i = 0; i < FILTER_SIZE; i++) {
            periods_copy[i] = _periods_us[i];
        }
        interrupts();

        /* Перевірка зупинки вала (таймаут 0.5 с) */
        if (now - last_time > 500000UL) {
            return 0.0f;
        }

        uint64_t sum_us = 0;
        for (uint8_t i = 0; i < FILTER_SIZE; i++) {
            sum_us += periods_copy[i];
        }

        float avg_period_us = (float)sum_us / FILTER_SIZE;
        if (avg_period_us <= 0.0f) return 0.0f;

        /* Розрахунок обертів за хвилину */
        return (60.0f * 1000000.0f) / (_slots * avg_period_us);
    }

    uint32_t getTotalRevolutions() const {
        return _total_pulses / _slots;
    }

private:
    uint8_t _pin;
    uint8_t _slots;
    volatile uint32_t _last_pulse_us;
    volatile uint32_t _periods_us[FILTER_SIZE];
    volatile uint8_t _filter_idx;
    volatile uint32_t _total_pulses;

    static TcrtTachometer* instance;

    static void IRAM_ATTR isrHandler() {
        if (!instance) return;
        uint32_t now = micros();
        uint32_t dt = now - instance->_last_pulse_us;

        if (dt > DEBOUNCE_MICROS) {
            instance->_last_pulse_us = now;
            instance->_periods_us[instance->_filter_idx] = dt;
            instance->_filter_idx = (instance->_filter_idx + 1) % FILTER_SIZE;
            instance->_total_pulses++;
        }
    }
};

TcrtTachometer* TcrtTachometer::instance = nullptr;
