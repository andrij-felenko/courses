// C++ драйвер для платформ Arduino / AVR / ESP
#include <Arduino.h>

class LaserLineDriver {
public:
    // controlPin: вивід МК, з'єднаний із затвором N-MOSFET
    // maxContinuousOnMs: ліміт безперервного світіння до спрацьовування захисту
    LaserLineDriver(uint8_t controlPin, uint32_t maxContinuousOnMs = 50)
        : _pin(controlPin),
          _maxOnMs(maxContinuousOnMs),
          _isActive(false),
          _safetyTripped(false),
          _turnOnTime(0),
          _lastHeartbeat(0),
          _dutyPercent(100) {}

    void begin() {
        pinMode(_pin, OUTPUT);
        digitalWrite(_pin, LOW);
        _isActive = false;
        _safetyTripped = false;
        _lastHeartbeat = millis();
    }

    // Налаштування яскравості через ШІМ (0–100%)
    void setBrightness(uint8_t dutyPercent) {
        if (dutyPercent > 100) {
            dutyPercent = 100;
        }
        _dutyPercent = dutyPercent;

        if (_isActive && !_safetyTripped) {
            analogWrite(_pin, map(_dutyPercent, 0, 100, 0, 255));
        }
    }

    // Формування мікросекундного стробу, синхронізованого з камерою
    void triggerStrobe(uint32_t durationUs) {
        if (_safetyTripped) {
            return;
        }

        // Активація випромінювання на точний інтервал експозиції
        digitalWrite(_pin, HIGH);
        _isActive = true;
        _turnOnTime = millis();
        _lastHeartbeat = _turnOnTime;

        // Точна мікросекундна пауза
        delayMicroseconds(durationUs);

        digitalWrite(_pin, LOW);
        _isActive = false;
    }

    // Скидання сторожового таймера з основного циклу
    void feedWatchdog() {
        _lastHeartbeat = millis();
    }

    // Періодична перевірка умов безпеки (викликається в loop)
    void service() {
        uint32_t now = millis();

        // Захист від перевищення максимальної тривалості безперервного світіння
        if (_isActive && (now - _turnOnTime > _maxOnMs)) {
            emergencyShutdown();
        }

        // Захист від зависання головного циклу обробки (тайм-аут 100 мс)
        if (now - _lastHeartbeat > 100) {
            emergencyShutdown();
        }
    }

    bool isFault() const {
        return _safetyTripped;
    }

    void resetFault() {
        digitalWrite(_pin, LOW);
        _isActive = false;
        _safetyTripped = false;
        _lastHeartbeat = millis();
    }

private:
    void emergencyShutdown() {
        digitalWrite(_pin, LOW);
        _isActive = false;
        _safetyTripped = true;
    }

    const uint8_t _pin;
    const uint32_t _maxOnMs;
    bool _isActive;
    bool _safetyTripped;
    uint32_t _turnOnTime;
    uint32_t _lastHeartbeat;
    uint8_t _dutyPercent;
};
