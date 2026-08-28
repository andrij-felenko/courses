#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <concepts>
#include <type_traits>
#include <format>
#include <meta>

// Допоміжна функція екранування рядків для JSON
inline auto escape_json_string(std::string_view input) -> std::string {
    std::string output;
    output.reserve(input.size() + 8);
    output.push_back('"');
    for (char c : input) {
        switch (c) {
            case '"':  output += "\\\""; break;
            case '\\': output += "\\\\"; break;
            case '\b': output += "\\b";  break;
            case '\f': output += "\\f";  break;
            case '\n': output += "\\n";  break;
            case '\r': output += "\\r";  break;
            case '\t': output += "\\t";  break;
            default:   output.push_back(c); break;
        }
    }
    output.push_back('"');
    return output;
}

// Попереднє оголошення головної функції серіалізації
template <typename T>
auto to_json(const T& value) -> std::string;

// 1. Серіалізація примітивних типів
template <typename T>
    requires std::is_arithmetic_v<T> && (!std::same_as<T, bool>)
auto serialize_value(const T& val) -> std::string {
    return std::to_string(val);
}

inline auto serialize_value(bool val) -> std::string {
    return val ? "true" : "false";
}

inline auto serialize_value(std::string_view val) -> std::string {
    return escape_json_string(val);
}

inline auto serialize_value(const std::string& val) -> std::string {
    return escape_json_string(val);
}

// 2. Серіалізація переліків
template <typename E>
    requires std::is_enum_v<E>
auto serialize_value(E val) -> std::string {
    return escape_json_string(enum_to_string(val));
}

// 3. Серіалізація опціональних значень
template <typename T>
auto serialize_value(const std::optional<T>& opt) -> std::string {
    if (!opt.has_value()) {
        return "null";
    }
    return to_json(*opt);
}

// 4. Серіалізація масивів та контейнерів
template <typename Container>
    requires requires(const Container& c) {
        { c.begin() } -> std::input_or_output_iterator;
        { c.end() }   -> std::input_or_output_iterator;
    } && (!std::same_as<Container, std::string>) && (!std::same_as<Container, std::string_view>)
auto serialize_value(const Container& cont) -> std::string {
    std::string out = "[";
    bool first = true;
    for (const auto& item : cont) {
        if (!first) out += ", ";
        out += to_json(item);
        first = false;
    }
    out += "]";
    return out;
}

// 5. Серіалізація структур через статичну рефлексію
template <typename T>
    requires std::is_class_v<T> && (!requires(const T& c) { c.begin(); }) && (!std::same_as<T, std::string>)
auto serialize_struct(const T& obj) -> std::string {
    constexpr auto type_info = ^^T;
    constexpr auto members = std::meta::nonstatic_data_members_of(type_info);

    std::string out = "{";
    bool first = true;

    template for (constexpr auto member : members) {
        // Перевіряємо, чи поле публічне
        static_assert(std::meta::is_public(member),
            "Серіалізація підтримує лише структури з публічними полями даних");

        if (!first) {
            out += ", ";
        }

        // Визначаємо ім'я ключа: перевіряємо наявність анотації JsonKey
        std::string_view key_name = std::meta::name_of(member);

        // Формуємо пару "ключ": значення через оператор сплайсингу
        out += escape_json_string(key_name);
        out += ": ";
        out += to_json(obj.[: member :]);

        first = false;
    }

    out += "}";
    return out;
}

// Головна точка входу серіалізації
template <typename T>
auto to_json(const T& value) -> std::string {
    if constexpr (std::is_class_v<T> && !requires(const T& c) { c.begin(); } && !std::same_as<T, std::string>) {
        return serialize_struct(value);
    } else {
        return serialize_value(value);
    }
}
