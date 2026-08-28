#include <meta>
#include <string_view>
#include <iostream>

struct NetworkEndpoint {
    std::string_view hostname;
    uint16_t port;
    bool use_tls;
};

void inspect_endpoint() {
    // 1. Отримуємо метадескриптор структури NetworkEndpoint під час компіляції
    constexpr std::meta::info meta_type = ^^NetworkEndpoint;

    // 2. Отримуємо ім'я типу як рядковий літерал часу компіляції
    constexpr std::string_view name = std::meta::name_of(meta_type);
    std::cout << "Назва типу: " << name << std::endl; // Виведе: NetworkEndpoint

    // 3. Досліджуємо кількість та імена полів структури
    constexpr auto fields = std::meta::nonstatic_data_members_of(meta_type);
    std::cout << "Кількість нестатичних полів: " << fields.size() << std::endl; // Виведе: 3
}
