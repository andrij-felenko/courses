#pragma once

// Фільтр на базі експоненційного ковзного середнього (EMA)
// для згладжування імпульсних перешкод та шумів давачів.
class SensorFilter {
public:
    // alpha - коефіцієнт згладжування (0 < alpha <= 1). 
    // Чим менше значення, тим сильніше згладжування (але більша інерційність).
    explicit SensorFilter(float alpha = 0.2f) 
        : alpha_(alpha), is_initialized_(false), current_value_(0.0f) {}

    float update(float new_value) {
        if (!is_initialized_) {
            current_value_ = new_value;
            is_initialized_ = true;
        } else {
            current_value_ = alpha_ * new_value + (1.0f - alpha_) * current_value_;
        }
        return current_value_;
    }

    void reset() {
        is_initialized_ = false;
    }

private:
    float alpha_;
    bool is_initialized_;
    float current_value_;
};
