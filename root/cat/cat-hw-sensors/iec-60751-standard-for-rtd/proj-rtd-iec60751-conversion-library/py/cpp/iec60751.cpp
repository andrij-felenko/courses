#include "iec60751.hpp"
#include <cmath>
#include <algorithm>

IEC60751::IEC60751(double r0) : r0_(r0) {}

double IEC60751::temperature_to_resistance(double t) const {
    if (t >= 0.0) {
        return r0_ * (1.0 + A * t + B * t * t);
    } else {
        return r0_ * (1.0 + A * t + B * t * t + C * (t - 100.0) * t * t * t);
    }
}

double IEC60751::resistance_to_temperature(double r) const {
    if (r >= r0_) {
        return (-A + std::sqrt(A * A - 4.0 * B * (1.0 - r / r0_))) / (2.0 * B);
    } else {
        double t_guess = (r / r0_ - 1.0) / A;
        for (int i = 0; i < 5; ++i) {
            double f = r0_ * (1.0 + A * t_guess + B * t_guess * t_guess + C * (t_guess - 100.0) * t_guess * t_guess * t_guess) - r;
            double df = r0_ * (A + 2.0 * B * t_guess + 4.0 * C * t_guess * t_guess * t_guess - 300.0 * C * t_guess * t_guess);
            t_guess -= f / df;
        }
        return t_guess;
    }
}

LookupTable::LookupTable(const IEC60751& sensor, double t_min, double t_max, double step) {
    if (step <= 0.0 || t_min >= t_max) {
        throw std::invalid_argument("Некоректні параметри таблиці");
    }
    
    size_t size = static_cast<size_t>((t_max - t_min) / step) + 1;
    table_.reserve(size);
    
    for (size_t i = 0; i < size; ++i) {
        double t = t_min + i * step;
        double r = sensor.temperature_to_resistance(t);
        table_.emplace_back(r, t);
    }
}

double LookupTable::lookup_temperature(double r) const {
    if (table_.empty()) return 0.0;
    
    if (r <= table_.front().first) return table_.front().second;
    if (r >= table_.back().first) return table_.back().second;

    auto it = std::lower_bound(table_.begin(), table_.end(), r,
        [](const std::pair<double, double>& element, double value) {
            return element.first < value;
        });

    auto prev = std::prev(it);
    
    double r0 = prev->first;
    double t0 = prev->second;
    double r1 = it->first;
    double t1 = it->second;

    return t0 + (r - r0) * (t1 - t0) / (r1 - r0);
}
