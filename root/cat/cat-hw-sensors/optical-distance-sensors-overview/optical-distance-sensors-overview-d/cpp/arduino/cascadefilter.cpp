#include <Arduino.h>

template <size_t N>
class CascadeFilter {
private:
    uint16_t _buffer[N];
    size_t _index = 0;
    size_t _count = 0;
    float _alpha;
    float _ema_state = 0.0f;
    bool _initialized = false;

public:
    CascadeFilter(float alpha = 0.2f) : _alpha(alpha) {}

    float update(uint16_t raw_value) {
        _buffer[_index] = raw_value;
        _index = (_index + 1) % N;
        if (_count < N) {
            _count++;
        }

        uint16_t temp[N];
        for (size_t i = 0; i < _count; i++) {
            temp[i] = _buffer[i];
        }

        for (size_t i = 1; i < _count; i++) {
            uint16_t key = temp[i];
            int j = (int)i - 1;
            while (j >= 0 && temp[j] > key) {
                temp[j + 1] = temp[j];
                j--;
            }
            temp[j + 1] = key;
        }

        uint16_t median = temp[_count / 2];

        if (!_initialized) {
            _ema_state = static_cast<float>(median);
            _initialized = true;
        } else {
            _ema_state = _alpha * static_cast<float>(median) + (1.0f - _alpha) * _ema_state;
        }

        return _ema_state;
    }
};
