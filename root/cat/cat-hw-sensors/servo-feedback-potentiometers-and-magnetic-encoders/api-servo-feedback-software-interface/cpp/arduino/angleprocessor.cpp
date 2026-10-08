#include <Arduino.h>
#include <math.h>

class AngleProcessor {
private:
    float _filteredRaw;
    float _alpha;
    uint16_t _maxRes;
    bool _initialized;

public:
    AngleProcessor(float alpha, uint16_t maxRes)
        : _filteredRaw(0.0f), _alpha(alpha), _maxRes(maxRes), _initialized(false) {}

    float process(uint16_t rawAngle) {
        if (!_initialized) {
            _filteredRaw = static_cast<float>(rawAngle);
            _initialized = true;
        } else {
            float delta = static_cast<float>(rawAngle) - _filteredRaw;
            float halfRes = _maxRes / 2.0f;

            if (delta > halfRes) {
                delta -= _maxRes;
            } else if (delta < -halfRes) {
                delta += _maxRes;
            }

            _filteredRaw += _alpha * delta;

            if (_filteredRaw >= _maxRes) {
                _filteredRaw -= _maxRes;
            } else if (_filteredRaw < 0.0f) {
                _filteredRaw += _maxRes;
            }
        }
        return (_filteredRaw * 2.0f * M_PI) / static_cast<float>(_maxRes);
    }
};
