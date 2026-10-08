// Каскадна фільтрація рівня та розрахунок об'єму (C++ / Arduino)
#include <Arduino.h>

template <size_t WindowSize = 5>
class LevelFilter {
private:
    float _buffer[WindowSize];
    size_t _index = 0;
    size_t _count = 0;
    float _emaState = 0.0f;
    float _alpha = 0.1f;
    bool _initialized = false;

public:
    LevelFilter(float alpha = 0.1f) : _alpha(alpha) {}

    float process(float rawH) {
        // 1. Збереження виміру у кільцевий буфер
        _buffer[_index] = rawH;
        _index = (_index + 1) % WindowSize;
        if (_count < WindowSize) _count++;

        float temp[WindowSize];
        for (size_t i = 0; i < _count; i++) {
            temp[i] = _buffer[i];
        }

        // 2. Бульбашкове сортування малого вікна
        for (size_t i = 0; i < _count - 1; i++) {
            for (size_t j = 0; j < _count - i - 1; j++) {
                if (temp[j] > temp[j + 1]) {
                    float t = temp[j];
                    temp[j] = temp[j + 1];
                    temp[j + 1] = t;
                }
            }
        }
        float medianH = temp[_count / 2];

        // 3. Експоненціальне згладжування хвильових завад
        if (!_initialized) {
            _emaState = medianH;
            _initialized = true;
        } else {
            _emaState = _alpha * medianH + (1.0f - _alpha) * _emaState;
        }
        return _emaState;
    }
};
