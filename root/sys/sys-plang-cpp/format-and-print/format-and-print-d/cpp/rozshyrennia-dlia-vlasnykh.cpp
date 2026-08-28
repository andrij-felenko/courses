#include <format>
#include <string_view>

// Власний тип даних
struct Vector2D {
    double x;
    double y;
};

// Спеціалізація std::formatter у просторі імен std
template <>
struct std::formatter<Vector2D> {
    bool is_hex = false;

    // 1. Метод parse аналізує специфікатор формату в constexpr-контексті
    constexpr auto parse(std::format_parse_context& ctx) {
        auto it = ctx.begin();
        auto end = ctx.end();

        if (it != end && *it == 'x') {
            is_hex = true;
            ++it;
        }

        if (it != end && *it != '}') {
            throw std::format_error("Invalid format specifier for Vector2D");
        }
        return it;
    }

    // 2. Метод format виконує безпосередній запис заформатованих даних у буфер
    template <typename FormatContext>
    auto format(const Vector2D& vec, FormatContext& ctx) const {
        if (is_hex) {
            return std::format_to(ctx.out(), "({:a}, {:a})", vec.x, vec.y);
        }
        return std::format_to(ctx.out(), "({:.2f}, {:.2f})", vec.x, vec.y);
    }
};
