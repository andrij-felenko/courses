// Еталонний C++ драйвер підсилювача XPT8871 для платформи Arduino
#include <Arduino.h>

class Xpt8871 {
public:
    enum State {
        STATE_SHUTDOWN = 0,
        STATE_POWERING_UP,
        STATE_ACTIVE
    };

    Xpt8871(uint8_t pin_shdn, uint16_t wakeup_delay_ms = 120)
        : _pin(pin_shdn), _twu(wakeup_delay_ms), _state(STATE_SHUTDOWN), _start_time(0) {}

    void begin() {
        // Запобігаємо глитчу: спершу LOW, потім конфігурація виходу
        digitalWrite(_pin, LOW);
        pinMode(_pin, OUTPUT);
        _state = STATE_SHUTDOWN;
    }

    void enable() {
        if (_state == STATE_SHUTDOWN) {
            digitalWrite(_pin, HIGH);
            _start_time = millis();
            _state = STATE_POWERING_UP;
        }
    }

    void disable() {
        digitalWrite(_pin, LOW);
        _state = STATE_SHUTDOWN;
    }

    bool isReady() {
        if (_state == STATE_POWERING_UP) {
            if (millis() - _start_time >= _twu) {
                _state = STATE_ACTIVE;
            }
        }
        return (_state == STATE_ACTIVE);
    }

    bool playStart() {
        // Дозволяємо старт звуку лише після виходу на режим
        return isReady();
    }

    void playStop() {
        // Вимикання підсилювача після зупинки потоку ЦАП
        disable();
    }

    State getState() const {
        return _state;
    }

private:
    uint8_t  _pin;
    uint16_t _twu;
    State    _state;
    uint32_t _start_time;
};
