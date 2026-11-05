#pragma once

#include <vector>
#include <utility>
#include <stdexcept>

class IEC60751 {
public:
    explicit IEC60751(double r0 = 100.0);

    double temperature_to_resistance(double t) const;
    double resistance_to_temperature(double r) const;

private:
    double r0_;
    static constexpr double A = 3.9083e-3;
    static constexpr double B = -5.7750e-7;
    static constexpr double C = -4.1830e-12;
};

class LookupTable {
public:
    LookupTable(const IEC60751& sensor, double t_min, double t_max, double step);

    double lookup_temperature(double r) const;

private:
    std::vector<std::pair<double, double>> table_;
};
