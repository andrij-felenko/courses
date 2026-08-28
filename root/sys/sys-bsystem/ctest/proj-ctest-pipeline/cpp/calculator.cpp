// src/calculator.cpp
#include "calculator.hpp"
#include <fstream>

namespace engine {

std::expected<double, MathError> Calculator::divide(double a, double b) const noexcept {
    if (b == 0.0) {
        return std::unexpected(MathError::DivisionByZero);
    }
    return a / b;
}

bool Calculator::write_record(const std::string& filepath, int key, double value) const {
    std::ofstream out(filepath, std::ios::app);
    if (!out) return false;
    out << key << ":" << value << "\n";
    return true;
}

} // namespace engine
