#include <string_view>
#include <cstdint>

// 1. constexpr змінна: гарантована константа часу збірки, незмінна в рантаймі
constexpr int MAX_PACKET_SIZE = 1500;

// 2. constexpr функція: подвійний режим роботи (compile-time або runtime)
constexpr int compute_buffer(int multiplier) noexcept {
    return MAX_PACKET_SIZE * multiplier;
}

// 3. consteval функція: жорсткий бар'єр, який ніколи не транслюється в рантайм
consteval uint32_t fnv1a_hash(std::string_view str) noexcept {
    uint32_t hash = 2166136261u;
    for (char c : str) {
        hash = (hash ^ static_cast<uint8_t>(c)) * 16777619u;
    }
    return hash;
}

// 4. constinit змінна: ініціалізується компілятором, але може змінюватися в рантаймі
constinit int g_transaction_counter = compute_buffer(2); // Початкове значення 3000

void process_event(int dynamic_multiplier) {
    // Коректно: constexpr функція працює в рантаймі з динамічними даними
    int runtime_buf = compute_buffer(dynamic_multiplier);

    // Коректно: consteval функція викликається зі статичним рядковим літералом
    constexpr uint32_t packet_id = fnv1a_hash("SENSOR_TELEMETRY_V1");

    // Помилка компіляції: consteval не можна викликати з динамічним рядком!
    // std::string dyn_str = "DYNAMIC_KEY";
    // uint32_t bad_id = fnv1a_hash(dyn_str);

    // Коректно: constinit змінну вільно модифікуємо під час виконання
    g_transaction_counter += 1;
}
