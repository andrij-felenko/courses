#pragma once

#include <chrono>
#include <cstdint>
#include <filesystem>
#include <span>
#include <vector>

namespace pid {

using Micros = std::chrono::duration<double, std::micro>;
using Millis = std::chrono::duration<double, std::milli>;

/// Один відлік бортового логу: час, завдання, гіроскоп, D-терм, напруга.
struct Sample {
    std::chrono::microseconds t{};
    double setpoint{};   ///< завдання кутової швидкості, deg/s
    double gyro{};       ///< виміряна кутова швидкість, deg/s
    double dTerm{};      ///< вихід диференційної гілки, одиниці мікшера
    double vbat{};       ///< напруга батареї під навантаженням, В
};

/// Лог у пам'яті. Створюється лише через loadCsv — недочитаного логу не існує.
class FlightLog {
public:
    /// Читає CSV t_us,setpoint,gyro,d_term,vbat.
    /// Кидає std::runtime_error із номером рядка на будь-якій біді.
    static FlightLog loadCsv(const std::filesystem::path& path);

    [[nodiscard]] std::span<const Sample> samples() const noexcept { return samples_; }
    [[nodiscard]] std::size_t size() const noexcept { return samples_.size(); }

    /// Середній період дискретизації.
    [[nodiscard]] Micros meanPeriod() const;

private:
    explicit FlightLog(std::vector<Sample> samples) noexcept : samples_(std::move(samples)) {}

    std::vector<Sample> samples_;
};

/// Інтервал між двома відліками в секундах — потрібен усім, хто рахує похідні.
[[nodiscard]] inline double secondsBetween(const Sample& a, const Sample& b) noexcept {
    return std::chrono::duration<double>(b.t - a.t).count();
}

} // namespace pid
