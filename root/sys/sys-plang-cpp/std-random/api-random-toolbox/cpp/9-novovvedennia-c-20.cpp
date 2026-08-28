#include <random>
#include <array>

constexpr auto generate_compile_time_table() {
    std::array<uint32_t, 10> table{};
    std::minstd_rand rng(42);
    for (auto& val : table) {
        val = rng();
    }
    return table;
}

// Таблиця обчислюється під час компіляції і розміщується у секції констант .rodata
constexpr auto random_table = generate_compile_time_table();
