#ifndef LIBSCHWARZIAN_HPP
#define LIBSCHWARZIAN_HPP

#include <functional>
#include <vector>
#include <expected>
#include <optional>
#include <limits>

namespace schwarzian {

enum class Error {
    CriticalPoint,
    InvalidStep,
    NullCallback
};

struct Point {
    double x;
    double df1;
    double df2;
    double df3;
    double schwarzian;
};

struct Config {
    double h{1e-4};
    double epsCritical{1e-9};
};

class Evaluator {
public:
    explicit Evaluator(Config config = Config{}) : config_(config) {}

    // Обчислення за точними похідними
    [[nodiscard]] std::expected<Point, Error> evalExact(double x, double df1, double df2, double df3) const {
        if (std::abs(df1) < config_.epsCritical) {
            return std::unexpected(Error::CriticalPoint);
        }
        const double ratio = df2 / df1;
        const double sf = (df3 / df1) - 1.5 * ratio * ratio;
        return Point{x, df1, df2, df3, sf};
    }

    // Чисельне оцінювання для довільного лямбда-виразу
    [[nodiscard]] std::expected<Point, Error> evalNumeric(const std::function<double(double)>& func, double x) const {
        if (config_.h <= 0.0) {
            return std::unexpected(Error::InvalidStep);
        }
        const double h = config_.h;
        const double f_p2 = func(x + 2.0 * h);
        const double f_p1 = func(x + h);
        const double f_m1 = func(x - h);
        const double f_m2 = func(x - 2.0 * h);

        const double df1 = (f_m2 - 8.0 * f_m1 + 8.0 * f_p1 - f_p2) / (12.0 * h);
        if (std::abs(df1) < config_.epsCritical) {
            return std::unexpected(Error::CriticalPoint);
        }

        const double df2 = (-f_m2 + 16.0 * f_m1 - 30.0 * func(x) + 16.0 * f_p1 - f_p2) / (12.0 * h * h);
        const double df3 = (-f_p2 + 2.0 * f_p1 - 2.0 * f_m1 + f_m2) / (2.0 * h * h * h);

        return evalExact(x, df1, df2, df3);
    }

    // Перевірка умови від'ємного Шварціана S(f) < 0 на сітці
    [[nodiscard]] bool checkSingerCondition(const std::function<double(double)>& func,
                                            double xMin, double xMax,
                                            std::size_t numSamples) const {
        const double step = (xMax - xMin) / static_cast<double>(numSamples);
        for (std::size_t i = 0; i <= numSamples; ++i) {
            const double x = xMin + static_cast<double>(i) * step;
            auto res = evalNumeric(func, x);
            if (res.has_value()) {
                if (res->schwarzian >= 0.0) {
                    return false;
                }
            }
        }
        return true;
    }

private:
    Config config_;
};

} // namespace schwarzian

#endif // LIBSCHWARZIAN_HPP
