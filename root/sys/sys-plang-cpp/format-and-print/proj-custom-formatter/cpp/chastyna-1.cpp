#include <format>
#include <array>
#include <string_view>
#include <iostream>
#include <algorithm>
#include <chrono>

class Matrix3x3 {
public:
    std::array<double, 9> data{};

    constexpr Matrix3x3() noexcept : data{1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0} {}
    constexpr Matrix3x3(std::initializer_list<double> list) noexcept {
        std::copy(list.begin(), list.end(), data.begin());
    }

    constexpr double at(std::size_t r, std::size_t c) const noexcept {
        return data[r * 3 + c];
    }
};

template <>
struct std::formatter<Matrix3x3> {
    bool single_line = false;
    int precision = 2;

    // 1. Компіляційний розбір специфікаторів у constexpr контексті
    constexpr auto parse(std::format_parse_context& ctx) {
        auto it = ctx.begin();
        auto end = ctx.end();

        if (it != end && *it == '1') {
            single_line = true;
            ++it;
        }

        if (it != end && *it == '.') {
            ++it;
            if (it != end && *it >= '0' && *it <= '9') {
                precision = *it - '0';
                ++it;
            }
        }

        if (it != end && *it != '}') {
            throw std::format_error("Invalid format specifier for Matrix3x3");
        }
        return it;
    }

    // 2. Генерація заформатованого виводу у вихідний ітератор
    template <typename FormatContext>
    auto format(const Matrix3x3& m, FormatContext& ctx) const {
        if (single_line) {
            return std::format_to(ctx.out(), 
                "[[{:.{}f}, {:.{}f}, {:.{}f}], [{:.{}f}, {:.{}f}, {:.{}f}], [{:.{}f}, {:.{}f}, {:.{}f}]]",
                m.at(0,0), precision, m.at(0,1), precision, m.at(0,2), precision,
                m.at(1,0), precision, m.at(1,1), precision, m.at(1,2), precision,
                m.at(2,0), precision, m.at(2,1), precision, m.at(2,2), precision);
        }

        return std::format_to(ctx.out(),
            "| {:>{}.{}f} {:>{}.{}f} {:>{}.{}f} |\n"
            "| {:>{}.{}f} {:>{}.{}f} {:>{}.{}f} |\n"
            "| {:>{}.{}f} {:>{}.{}f} {:>{}.{}f} |",
            m.at(0,0), precision + 5, precision, m.at(0,1), precision + 5, precision, m.at(0,2), precision + 5, precision,
            m.at(1,0), precision + 5, precision, m.at(1,1), precision + 5, precision, m.at(1,2), precision + 5, precision,
            m.at(2,0), precision + 5, precision, m.at(2,1), precision + 5, precision, m.at(2,2), precision + 5, precision);
    }
};
