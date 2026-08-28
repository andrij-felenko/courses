#include <experimental/meta>
#include <iostream>
#include <string_view>

struct UserAccount {
    int id;
    std::string name;
    double balance;
};

// Універсальний друк полів будь-якої структури на етапі компіляції
template <typename T>
void print_struct_fields(const T& obj) {
    // 1. Отримуємо дескриптор метаданих типу
    constexpr std::meta::info type_meta = ^^T;

    // 2. У constexpr-контексті отримуємо вектор дескрипторів усіх нестатичних полів
    constexpr auto fields = std::meta::nonstatic_data_members_of(type_meta);

    // 3. Розгортаємо цикл по полях через шаблонну згортку
    [:expand(fields):] >> [&]<auto field_meta>() {
        // Отримуємо назву поля як рядок під час збірки
        constexpr std::string_view field_name = std::meta::name_of(field_meta);
        
        // Звертаємося до поля об'єкта obj через сплайсинг дескриптора поля
        std::cout << field_name << " = " << obj.[:field_meta:] << '\n';
    };
}
