#include <cstdint>
#include <string_view>
#include <vector>

// Логічний контейнер зі статичної моделі — те, що на статиці одна «коробка».
struct Container {
    std::string_view name;   // "api" або "db" — назва з логічної моделі
};

// Вузол розгортання — місце, де крутяться копії (сервер / VM / контейнер).
struct Deployment {
    std::string_view node;      // напр. "eu-node-1"
    const Container  *of;       // ЯКИЙ логічний контейнер тут живе
    std::uint8_t      replicas; // СКІЛЬКИ копій — ось чого немає на статиці
};

// Скільки всього копій цього контейнера піднято в цьому середовищі.
std::uint16_t total_replicas(const std::vector<Deployment>& deps, std::string_view name) {
    std::uint16_t sum = 0;
    for (const auto& d : deps)
        if (d.of->name == name)   // той самий логічний контейнер...
            sum += d.replicas;    // ...сумуємо копії по всіх вузлах
    return sum;
}
