#pragma once

#include <cstdint>
#include <string>
#include <vector>
#include <algorithm>
#include <cmath>

/**
 * @brief Клас інкапсуляції роботи з тензометричним мостом і перетворювачем АЦП.
 */
class LoadCell {
public:
    explicit LoadCell(std::string name, double counts_per_newton = 420.0)
        : name_(std::move(name)), counts_per_newton_(counts_per_newton) {}

    /**
     * @brief Проводить процедуру тарування (визначення нульового зміщення датчика).
     * @param sample_count Кількість вибірок для усереднення.
     */
    void tare(std::size_t sample_count = 10) {
        if (sample_count == 0) return;
        int64_t sum = 0;
        for (std::size_t i = 0; i < sample_count; ++i) {
            sum += readRawAdc();
        }
        tare_offset_ = static_cast<int32_t>(sum / static_cast<int64_t>(sample_count));
    }

    /**
     * @brief Зчитує поточне зусилля в Ньютонах з урахуванням тари та коефіцієнта калібрування.
     */
    [[nodiscard]] double readForceNewtons() {
        int32_t raw = readRawAdc();
        int32_t net = raw - tare_offset_;
        double force = static_cast<double>(net) / counts_per_newton_;
        return (force > 0.0) ? force : 0.0;
    }

    /**
     * @brief Калібрує коефіцієнт чутливості за еталонною вагою або силою.
     */
    void calibrate(double reference_force_n, int32_t raw_counts_with_load) {
        if (reference_force_n > 0.0) {
            counts_per_newton_ = static_cast<double>(raw_counts_with_load - tare_offset_) / reference_force_n;
        }
    }

    [[nodiscard]] const std::string& getName() const noexcept { return name_; }
    [[nodiscard]] int32_t getTareOffset() const noexcept { return tare_offset_; }
    [[nodiscard]] double getCountsPerNewton() const noexcept { return counts_per_newton_; }

    /**
     * @brief Зчитує код АЦП (у демонстраційному середовищі моделює відгук датчика).
     */
    int32_t readRawAdc() {
        sim_step_++;
        double sim_n = 0.0;
        if (sim_step_ < 10) {
            sim_n = 0.0;
        } else if (sim_step_ < 65) {
            // Пружна та пластична деформація полімерної бобишки під час витягування втулки
            double progress = (sim_step_ - 10) / 55.0;
            sim_n = 640.0 * (1.0 - std::exp(-2.5 * progress)) / (1.0 - std::exp(-2.5));
        } else if (sim_step_ < 80) {
            // Зрив різьбової посадки
            double drop = (sim_step_ - 65) * 35.0;
            sim_n = std::max(90.0, 640.0 - drop);
        } else {
            // Залишкове тертя вирваної втулки
            sim_n = 90.0;
        }
        int32_t counts = tare_offset_ + static_cast<int32_t>(sim_n * counts_per_newton_);
        counts += ((sim_step_ % 5) - 2) * 12; // шум тензомосту
        return counts;
    }

private:
    std::string name_;
    double counts_per_newton_{420.0};
    int32_t tare_offset_{145000};
    int sim_step_{0};
};
