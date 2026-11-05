// Реалізація обгортки C++ для 64-бітного накопичувального лічильника енкодера
#include <Arduino.h>

class Encoder64BitDriver {
private:
    TIM_TypeDef* _timer;
    int64_t _accumulated_position;
    uint16_t _last_cnt;
    uint32_t _cpr;

public:
    Encoder64BitDriver(TIM_TypeDef* timer, uint32_t cpr) 
        : _timer(timer), _accumulated_position(0), _last_cnt(0), _cpr(cpr) {}

    void begin() {
        _last_cnt = static_cast<uint16_t>(_timer->CNT);
        _accumulated_position = 0;
    }

    // Періодичне оновлення стану позиції та швидкості
    void update() {
        uint16_t current_cnt = static_cast<uint16_t>(_timer->CNT);
        
        // Магія 2's complement: приведення різниці безпосередньо до int16_t
        // коректно обробляє як overflow (65535 -> 0), так і underflow (0 -> 65535)!
        int16_t delta = static_cast<int16_t>(current_cnt - _last_cnt);
        
        _accumulated_position += delta;
        _last_cnt = current_cnt;
    }

    int64_t getAbsolutePosition() const {
        return _accumulated_position;
    }

    double getTurns() const {
        return static_cast<double>(_accumulated_position) / static_cast<double>(_cpr);
    }

    void resetPosition(int64_t new_position = 0) {
        _timer->CNT = 0;
        _last_cnt = 0;
        _accumulated_position = new_position;
    }
};
