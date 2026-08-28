#include <string_view>
#include <optional>
#include <vector>
#include <stdexcept>
#include <meta>

// Конвертація значення enum у строкове представлення
template <typename E>
    requires std::is_enum_v<E>
constexpr auto enum_to_string(E value) -> std::string_view {
    constexpr auto enum_info = ^^E;
    constexpr auto enumerators = std::meta::enumerators_of(enum_info);

    // Розгортання статичного switch під час компіляції
    template for (constexpr auto e : enumerators) {
        if (value == [: e :]) {
            return std::meta::name_of(e);
        }
    }

    return "Unknown";
}

// Конвертація рядка в значення enum
template <typename E>
    requires std::is_enum_v<E>
constexpr auto string_to_enum(std::string_view str) -> std::optional<E> {
    constexpr auto enum_info = ^^E;
    constexpr auto enumerators = std::meta::enumerators_of(enum_info);

    template for (constexpr auto e : enumerators) {
        if (str == std::meta::name_of(e)) {
            return [: e :];
        }
    }

    return std::nullopt;
}
