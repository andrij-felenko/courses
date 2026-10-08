#include <cstdint>

class LvdtDemodulator {
public:
    explicit LvdtDemodulator(float alpha)
        : alpha_(alpha), filtered_output_(0.0f) {}

    // Обробка відліків збудження та вторинного сигналу LVDT
    float process(float exc_sample, float sec_sample) {
        const float ref_sign = (exc_sample >= 0.0f) ? 1.0f : -1.0f;
        const float rectified = sec_sample * ref_sign;
        
        // Цифрова низькочастотна фільтрація (IIR ФНЧ)
        filtered_output_ += alpha_ * (rectified - filtered_output_);
        return filtered_output_;
    }

    void reset() {
        filtered_output_ = 0.0f;
    }

private:
    float alpha_;
    float filtered_output_;
};
