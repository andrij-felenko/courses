#include <meta>
#include <iostream>
#include <string_view>
#include <format>

// Універсальний інспектор полів будь-якої структури
template <typename T>
void print_struct_fields(const T& obj) {
    constexpr auto type_meta = ^^T;
    constexpr auto fields = std::meta::nonstatic_data_members_of(type_meta);

    std::cout << "Структура " << std::meta::name_of(type_meta) << " містить:\n";

    // Компілятор розгортає лямбду для кожного поля структури під час трансляції
    [: expand(fields) :] >> [&]<auto field_meta>() {
        constexpr std::string_view field_name = std::meta::name_of(field_meta);
        const auto& field_value = obj.[: field_meta :];

        std::cout << std::format("  Поле: {:12} | Значення: {}\n", field_name, field_value);
    };
}
