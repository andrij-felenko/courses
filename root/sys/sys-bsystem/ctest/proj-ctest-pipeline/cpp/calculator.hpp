// src/calculator.hpp
#pragma once
#include <string>
#include <expected>

namespace engine {

enum class MathError {
    DivisionByZero,
    Overflow
};

class Calculator {
public:
    [[nodiscard]] std::expected<double, MathError> divide(double a, double b) const noexcept;
    [[nodiscard]] bool write_record(const std::string& filepath, int key, double value) const;
};

} // namespace engine
