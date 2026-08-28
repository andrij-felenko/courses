#include <cstdint>
#include <array>
#include <numeric>
#include <span>
#include <iostream>
#include <optional>

namespace telemetry {

constexpr size_t HistoryDepth = 4;

class TelemetryFilter {
public:
    TelemetryFilter() = default; // Члени ініціалізуються значеннями за замовчуванням

    // Метод з навмисно закладеним багом виходу за межі для демонстрації ASan
    void add_sample_buggy(int32_t sample) {
        // Прямий доступ за сирим індексом без перевірки розміру
        history_buffer_[count_] = sample;
        ++count_;
    }

    // Безпечний ідіоматичний метод C++
    bool add_sample_safe(int32_t sample) noexcept {
        if (count_ >= HistoryDepth) {
            return false;
        }
        history_buffer_[count_++] = sample;
        return true;
    }

    [[nodiscard]] std::optional<int32_t> get_average() const noexcept {
        if (!is_calibrated_ || count_ == 0) {
            return std::nullopt;
        }
        const size_t limit = std::min(count_, HistoryDepth);
        const int64_t sum = std::accumulate(history_buffer_.begin(),
                                            history_buffer_.begin() + limit,
                                            int64_t{0});
        return static_cast<int32_t>(sum / limit);
    }

    void set_calibrated(bool state) noexcept { is_calibrated_ = state; }

private:
    std::array<int32_t, HistoryDepth> history_buffer_{};
    size_t count_{0};
    bool is_calibrated_{false};
};

[[nodiscard]] int32_t calculate_pressure_buggy(int32_t raw_adc, int32_t calib_p1, int32_t calib_p2) noexcept {
    // Навмисне знакове переповнення (демонстрація UBSan)
    const int32_t intermediate = raw_adc * calib_p1;
    return (intermediate / 100) + calib_p2;
}

[[nodiscard]] constexpr int32_t calculate_pressure_safe(int32_t raw_adc, int32_t calib_p1, int32_t calib_p2) noexcept {
    // Безпечне обчислення через 64-бітний проміжний тип
    const auto intermediate = static_cast<int64_t>(raw_adc) * calib_p1;
    return static_cast<int32_t>((intermediate / 100) + calib_p2);
}

} // namespace telemetry

int main() {
    std::cout << "=== Запуск демонстраційного C++20 драйвера ===\n";

    // Тест 1: Знакове переповнення
    const int32_t p = telemetry::calculate_pressure_buggy(60000, 50000, 101325);
    std::cout << "Обчислений тиск: " << p << " Па\n";

    // Тест 2: Вихід за межі масиву
    telemetry::TelemetryFilter filter;
    filter.set_calibrated(true);

    for (int i = 0; i < 6; ++i) {
        filter.add_sample_buggy(1000 + i * 10);
    }

    if (const auto avg = filter.get_average()) {
        std::cout << "Середній тиск: " << *avg << "\n";
    }

    return 0;
}
