#include <meta>
#include <string>
#include <string_view>
#include <format>
#include <vector>
#include <type_traits>
#include <concepts>
#include <iostream>

// Концепт для виявлення арифметичних типів та рядкових представлень
template <typename T>
concept JsonPrimitive = std::is_arithmetic_v<T> || 
                        std::is_same_v<T, std::string> || 
                        std::is_same_v<T, std::string_view>;

// Базова серілізація скалярних значень
template <JsonPrimitive T>
std::string serialize_value(const T& val) {
    if constexpr (std::is_same_v<T, std::string> || std::is_same_v<T, std::string_view>) {
        return std::format("\"{}\"", val);
    } else if constexpr (std::is_same_v<T, bool>) {
        return val ? "true" : "false";
    } else {
        return std::format("{}", val);
    }
}

// Попередня декларація головного шаблону для забезпечення рекурсії
template <typename T>
std::string to_json(const T& obj);

// Концепт для ітерованих стандартних контейнерів
template <typename T>
concept IterableContainer = requires(const T& c) {
    { c.begin() } -> std::input_iterator;
    { c.end() } -> std::input_iterator;
} && !std::is_same_v<T, std::string> && !std::is_same_v<T, std::string_view>;

// Серілізація масивів та векторів у формат JSON-списку
template <IterableContainer T>
std::string serialize_value(const T& container) {
    std::string result = "[";
    bool first = true;
    for (const auto& item : container) {
        if (!first) result += ", ";
        result += to_json(item);
        first = false;
    }
    result += "]";
    return result;
}

// Головна рефлексивна функція для довільних користувацьких класів і структур
template <typename T>
std::string to_json(const T& obj) {
    if constexpr (JsonPrimitive<T> || IterableContainer<T>) {
        return serialize_value(obj);
    } else if constexpr (std::is_class_v<T>) {
        std::string json = "{";
        bool first = true;

        // 1. Отримуємо метадескриптор цільового типу під час компіляції
        constexpr auto type_meta = ^^T;

        // 2. Отримуємо вектор дескрипторів нестатичних полів класу
        constexpr auto members = std::meta::nonstatic_data_members_of(type_meta);

        // 3. Розгортаємо поля через компіляторну ітерацію сплайсингу
        [: expand(members) :] >> [&]<auto member_meta>() {
            // Отримуємо назву поля безпосередньо з абстрактного синтаксичного дерева
            constexpr std::string_view field_name = std::meta::name_of(member_meta);

            // Отримуємо прямий доступ до поля об'єкта через сплайсер
            const auto& field_value = obj.[: member_meta :];

            if (!first) {
                json += ", ";
            }

            // Формуємо пару "ім'я": значення з рекурсивною серілізацією
            json += std::format("\"{}\": {}", field_name, to_json(field_value));
            first = false;
        };

        json += "}";
        return json;
    } else {
        static_assert(sizeof(T) == 0, "Тип не підтримується для автоматичної серілізації в JSON!");
    }
}
