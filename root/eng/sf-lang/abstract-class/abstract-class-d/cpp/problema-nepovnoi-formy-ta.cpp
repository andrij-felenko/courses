#include <cstddef>
#include <iostream>
#include <vector>

class AudioFilter {
public:
    explicit AudioFilter(int sample_rate) : m_sample_rate(sample_rate) {}
    virtual ~AudioFilter() = default;

    // Фіктивні реалізації за замовчуванням
    virtual void process(float* buffer, std::size_t frames) {
        // Порожнє тіло: не робить нічого
    }

    virtual double get_latency_ms() const {
        return 0.0; // Фіктивне значення
    }

protected:
    int m_sample_rate;
};
