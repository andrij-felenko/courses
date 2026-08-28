// Детальний приклад спеціалізації для власного типу Point3D із повноцінною обробкою
#include <format>
#include <string_view>
#include <cstdint>

struct Point3D {
    double x, y, z;
};

template <>
struct std::formatter<Point3D> {
    enum class Mode { Default, Compact, Hex };
    Mode mode = Mode::Default;
    int precision = 2;

    // 1. Розбір специфікації у constexpr контексті
    constexpr auto parse(std::format_parse_context& ctx) {
        auto it = ctx.begin();
        auto end = ctx.end();

        if (it != end && *it != '}') {
            if (*it == 'c') { mode = Mode::Compact; ++it; }
            else if (*it == 'x') { mode = Mode::Hex; ++it; }
        }

        if (it != end && *it == '.') {
            ++it;
            if (it != end && *it >= '0' && *it <= '9') {
                precision = *it - '0';
                ++it;
            }
        }

        if (it != end && *it != '}') {
            throw std::format_error("Invalid format specifier for Point3D");
        }
        return it;
    }

    // 2. Генерація текстового виводу у вихідний ітератор
    template <typename FormatContext>
    auto format(const Point3D& pt, FormatContext& ctx) const {
        if (mode == Mode::Hex) {
            return std::format_to(ctx.out(), "({:a}, {:a}, {:a})", pt.x, pt.y, pt.z);
        } else if (mode == Mode::Compact) {
            return std::format_to(ctx.out(), "{:.{}f},{:.{}f},{:.{}f}", 
                                  pt.x, precision, pt.y, precision, pt.z, precision);
        }
        return std::format_to(ctx.out(), "Point3D(x={:.{}f}, y={:.{}f}, z={:.{}f})", 
                              pt.x, precision, pt.y, precision, pt.z, precision);
    }
};
