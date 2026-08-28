#include <Arduino.h>

// Ключ на біполярному транзисторі. Полярність задається при створенні,
// далі on()/off() означають саме «увімкнути/вимкнути навантаження»,
// незалежно від того, NPN це низом чи PNP верхом.
class Switch {
public:
    enum Polarity { ACTIVE_HIGH, ACTIVE_LOW };  // NPN низом vs PNP верхом

    Switch(uint8_t pin, Polarity pol = ACTIVE_HIGH)
        : pin_(pin), active_low_(pol == ACTIVE_LOW) {}

    void begin() {
        pinMode(pin_, OUTPUT);
        off();                 // ГАРАНТОВАНИЙ старт: навантаження вимкнене
    }

    void on()  { digitalWrite(pin_, active_low_ ? LOW  : HIGH); }
    void off() { digitalWrite(pin_, active_low_ ? HIGH : LOW ); }
    void set(bool state) { state ? on() : off(); }
    void toggle() { on_ = !on_; set(on_); }
    bool is_on() const { return on_; }

private:
    uint8_t pin_;
    bool active_low_;
    bool on_ = false;
};
