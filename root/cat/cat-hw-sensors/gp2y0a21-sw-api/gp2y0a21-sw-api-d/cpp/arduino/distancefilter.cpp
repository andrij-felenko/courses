#include <Arduino.h>

class DistanceFilter {
private:
    static const uint8_t WINDOW_SIZE = 5;
    uint16_t _buffer[WINDOW_SIZE];
    uint8_t _index;
    bool _filled;
    float _ema_state;
    float _alpha;

public:
    DistanceFilter(float alpha = 0.2f) 
        : _index(0), _filled(false), _ema_state(0.0f), _alpha(alpha) {}

    uint16_t update(uint16_t raw_adc) {
        _buffer[_index] = raw_adc;
        _index = (_index + 1) % WINDOW_SIZE;
        if (_index == 0) _filled = true;

        uint16_t median_val = raw_adc;
        if (_filled) {
            uint16_t temp[WINDOW_SIZE];
            memcpy(temp, _buffer, sizeof(temp));
            // Сортування масиву для знаходження медіани
            for (uint8_t i = 0; i < WINDOW_SIZE - 1; i++) {
                for (uint8_t j = i + 1; j < WINDOW_SIZE; j++) {
                    if (temp[i] > temp[j]) {
                        uint16_t t = temp[i];
                        temp[i] = temp[j];
                        temp[j] = t;
                    }
                }
            }
            median_val = temp[WINDOW_SIZE / 2];
        }

        if (_ema_state == 0.0f) {
            _ema_state = static_cast<float>(median_val);
        } else {
            _ema_state = _alpha * median_val + (1.0f - _alpha) * _ema_state;
        }

        return static_cast<uint16_t>(_ema_state);
    }
};
