// app/telemetry.cpp — арифметика вікна телеметрії.
// Файл не знає ні про шину, ні про давач: на вхід приходять числа, на
// вихід іде запис, і саме тому його перевіряють таблицею значень.
#include "app/telemetry.hpp"

#include <algorithm>
#include <cmath>

namespace app {

void TelemetryWindow::add(const Measurement& m)
{
    if (samples_ == 0) {
        temp_min_ = m.temperature_c;
        temp_max_ = m.temperature_c;
    } else if (m.temperature_c < temp_min_) {
        temp_min_ = m.temperature_c;
    } else if (m.temperature_c > temp_max_) {
        temp_max_ = m.temperature_c;
    }

    temp_sum_     += m.temperature_c;
    humidity_sum_ += m.humidity_rh;
    pressure_sum_ += m.pressure_hpa;

    // Середньоквадратичне значення вібрації рахуємо накопиченням суми
    // квадратів: зберігати самі зразки нема куди, а корінь потрібен один
    // раз на вікно.
    vibration_sq_sum_ += m.vibration_g * m.vibration_g;
    vibration_peak_ = std::max(vibration_peak_, m.vibration_g);

    ++samples_;
}

void TelemetryWindow::restart(hal::Millis now) noexcept
{
    start_            = now;
    samples_          = 0;
    faults_           = 0;
    temp_sum_         = 0.0F;
    temp_min_         = 0.0F;
    temp_max_         = 0.0F;
    humidity_sum_     = 0.0F;
    pressure_sum_     = 0.0F;
    vibration_sq_sum_ = 0.0F;
    vibration_peak_   = 0.0F;
}

std::optional<TelemetryRecord> TelemetryWindow::close(hal::Millis now)
{
    if (samples_ == 0) {
        // Вікно без жодного виміру: запису немає, але вікно зсуваємо,
        // інакше наступне закриття підбере чужий інтервал часу. Невдачі
        // переносимо далі — вони й є новина цього вікна.
        const auto carried = faults_;
        restart(now);
        faults_ = carried;
        return std::nullopt;
    }

    const auto n = static_cast<float>(samples_);

    const TelemetryRecord record{
        .window_start      = start_,
        .window_end        = now,
        .sample_count      = samples_,
        .temp_avg_c        = temp_sum_ / n,
        .temp_min_c        = temp_min_,
        .temp_max_c        = temp_max_,
        .humidity_avg_rh   = humidity_sum_ / n,
        .pressure_avg_hpa  = pressure_sum_ / n,
        .vibration_rms_g   = std::sqrt(vibration_sq_sum_ / n),
        .vibration_peak_g  = vibration_peak_,
        .fault_count       = faults_,
    };

    restart(now);
    return record;
}

} // namespace app
