// --- TouchButton: драйвер миттєвого режиму TTP223 ---------------------------
class TouchButton {
public:
    // pin — куди заведено SIG; activeLevel — HIGH (акт. у 1) або LOW (акт. у 0)
    TouchButton(uint8_t pin, uint8_t activeLevel = HIGH)
        : _pin(pin), _active(activeLevel) {}

    void begin() {
        pinMode(_pin, INPUT);                 // двотактний вихід → без підтяжки
        _stable = _raw = readActive();        // старт із поточного стану
        _lastEdge = millis();
    }

    // Викликати щоразу в loop(); повертає true рівно в момент активації (фронт).
    bool update() {
        bool a = readActive();
        uint32_t now = millis();

        if (a != _raw) {          // сирий рівень змінився — почали відлік стійкості
            _raw = a;
            _lastEdge = now;
        }
        // рівень протримався GUARD мс → визнаємо його справжнім
        if (a == _raw && (now - _lastEdge) >= GUARD && _stable != a) {
            _stable = a;
            if (_stable) {                    // перехід у "активно" = момент дотику
                _pressedAt = now;
                _justPressed = true;
                return true;
            } else {                          // перехід у "спокій" = відпускання
                _justReleased = true;
            }
        }
        return false;
    }

    bool pressed()  { bool r = _justPressed;  _justPressed  = false; return r; }
    bool released() { bool r = _justReleased; _justReleased = false; return r; }
    bool held()     { return _stable; }                 // тримають зараз?
    uint32_t heldMs() { return _stable ? millis() - _pressedAt : 0; }

private:
    bool readActive() { return digitalRead(_pin) == _active; }

    static const uint32_t GUARD = 5;   // мс стійкості проти імпульсів-привидів
    uint8_t  _pin, _active;
    bool     _raw = false, _stable = false;
    bool     _justPressed = false, _justReleased = false;
    uint32_t _lastEdge = 0, _pressedAt = 0;
};
