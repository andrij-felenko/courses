// C++ реалізація неблокувального драйвера HC-SR505 для Arduino
#include <Arduino.h>

class HCSR505Driver {
public:
    enum State {
        STATE_QUARANTINE,
        STATE_IDLE,
        STATE_MOTION_ACTIVE,
        STATE_LOCKOUT
    };

    typedef void (*EventCallback)();

    HCSR505Driver(uint8_t pin) : _pin(pin), _state(STATE_QUARANTINE), 
                                 _stateStartTime(0), _edgeFlag(false), 
                                 _currentLevel(false), _onStart(nullptr), _onEnd(nullptr) {}

    void begin(EventCallback onStart = nullptr, EventCallback onEnd = nullptr) {
        _onStart = onStart;
        _onEnd = onEnd;
        pinMode(_pin, INPUT_PULLDOWN);
        _stateStartTime = millis();
        _state = STATE_QUARANTINE;
    }

    void handleInterrupt() {
        _currentLevel = digitalRead(_pin);
        _edgeFlag = true;
    }

    void tick() {
        uint32_t now = millis();

        switch (_state) {
            case STATE_QUARANTINE:
                // Витримка 15-секундного періоду стабілізації
                if (now - _stateStartTime >= 15000) {
                    if (digitalRead(_pin) == LOW) {
                        _state = STATE_IDLE;
                        _edgeFlag = false;
                    }
                }
                break;

            case STATE_IDLE:
                if (_edgeFlag) {
                    _edgeFlag = false;
                    if (_currentLevel == HIGH) {
                        _state = STATE_MOTION_ACTIVE;
                        _stateStartTime = now;
                        if (_onStart) _onStart();
                    }
                }
                break;

            case STATE_MOTION_ACTIVE:
                if (_edgeFlag) {
                    _edgeFlag = false;
                    if (_currentLevel == LOW) {
                        _state = STATE_LOCKOUT;
                        _stateStartTime = now;
                        if (_onEnd) _onEnd();
                    }
                }
                break;

            case STATE_LOCKOUT:
                // Пауза відновлення піроелемента (2.5 с)
                if (now - _stateStartTime >= 2500) {
                    _state = STATE_IDLE;
                    _edgeFlag = false;
                }
                break;
        }
    }

    State getState() const { return _state; }

private:
    uint8_t _pin;
    State _state;
    uint32_t _stateStartTime;
    volatile bool _edgeFlag;
    volatile bool _currentLevel;
    EventCallback _onStart;
    EventCallback _onEnd;
};
