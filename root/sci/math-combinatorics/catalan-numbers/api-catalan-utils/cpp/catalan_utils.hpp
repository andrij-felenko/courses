// catalan_utils.hpp — C++20 заголовок з RAII та типобезпечною обробкою помилок
#ifndef CATALAN_UTILS_HPP
#define CATALAN_UTILS_HPP

#include <cstdint>
#include <vector>
#include <string_view>
#include <optional>
#include <system_error>
#include <stdexcept>

namespace catalan {

enum class ErrorCode {
    Overflow = 1,
    InvalidParameter,
    AllocationFailure,
    InvalidDyckSequence
};

class CatalanErrorCategory : public std::error_category {
public:
    [[nodiscard]] const char* name() const noexcept override { 
        return "catalan"; 
    }
    
    [[nodiscard]] std::string message(int ev) const override {
        switch (static_cast<ErrorCode>(ev)) {
            case ErrorCode::Overflow: 
                return "Catalan number exceeds 64-bit unsigned integer limit (n > 35)";
            case ErrorCode::InvalidParameter: 
                return "Invalid input parameter passed to catalan function";
            case ErrorCode::AllocationFailure: 
                return "Dynamic memory allocation failed during sequence generation";
            case ErrorCode::InvalidDyckSequence: 
                return "Provided string violates Dyck path balance invariant";
            default: 
                return "Unknown catalan system error";
        }
    }
};

inline const CatalanErrorCategory& error_category() noexcept {
    static CatalanErrorCategory instance;
    return instance;
}

inline std::error_code make_error_code(ErrorCode e) noexcept {
    return {static_cast<int>(e), error_category()};
}

class CatalanCalculator {
public:
    // Обчислення точного значення за O(n) з поверненням std::optional
    [[nodiscard]] static std::optional<std::uint64_t> compute(std::uint32_t n) noexcept {
        if (n > 35) {
            return std::nullopt;
        }
        std::uint64_t res = 1;
        for (std::uint64_t i = 1; i <= n; ++i) {
            res = res * (4 * i - 2) / (i + 1);
        }
        return res;
    }

    // Генерація таблиці динамічного програмування в контейнер std::vector
    [[nodiscard]] static std::vector<std::uint64_t> generate_sequence(std::uint32_t n) {
        if (n > 35) {
            throw std::overflow_error("Catalan index n exceeds 64-bit uint limit");
        }
        std::vector<std::uint64_t> c(n + 1, 0);
        c[0] = 1;
        for (std::size_t i = 1; i <= n; ++i) {
            for (std::size_t j = 0; j < i; ++j) {
                c[i] += c[j] * c[i - 1 - j];
            }
        }
        return c;
    }

    // Валідація дужкової послідовності Дюка без виділення пам'яті
    [[nodiscard]] static bool validate_dyck_path(std::string_view seq) noexcept {
        int balance = 0;
        for (char ch : seq) {
            if (ch == '(') {
                balance++;
            } else if (ch == ')') {
                balance--;
                if (balance < 0) return false;
            }
        }
        return balance == 0;
    }
};

} // namespace catalan

#endif // CATALAN_UTILS_HPP
