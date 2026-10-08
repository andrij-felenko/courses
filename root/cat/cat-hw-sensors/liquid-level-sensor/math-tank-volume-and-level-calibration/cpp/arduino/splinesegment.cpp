// Обчислення об'єму за кубічним сплайном (C++ / Arduino)
#include <Arduino.h>

struct SplineSegment {
    float h; // Початковий рівень інтервалу (см)
    float a; // Коефіцієнт a_i (л)
    float b; // Коефіцієнт b_i (л/см)
    float c; // Коефіцієнт c_i (л/см²)
    float d; // Коефіцієнт d_i (л/см³)
};

class SplineCalibrator {
private:
    const SplineSegment* _segments;
    size_t _count;

public:
    SplineCalibrator(const SplineSegment* segments, size_t count)
        : _segments(segments), _count(count) {}

    float evaluate(float h) const {
        if (_count == 0 || _segments == nullptr) return 0.0f;
        if (h <= _segments[0].h) return _segments[0].a;
        if (h >= _segments[_count - 1].h) return _segments[_count - 1].a;

        size_t low = 0;
        size_t high = _count - 1;
        size_t idx = 0;

        while (low <= high) {
            size_t mid = low + (high - low) / 2;
            if (_segments[mid].h <= h) {
                idx = mid;
                low = mid + 1;
            } else {
                if (mid == 0) break;
                high = mid - 1;
            }
        }

        float dx = h - _segments[idx].h;
        return _segments[idx].a + dx * (_segments[idx].b + dx * (_segments[idx].c + dx * _segments[idx].d));
    }
};
