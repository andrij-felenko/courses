#include <array>
#include <cstdint>
#include <string_view>
#include <span>

namespace crc32 {

// Стандартний поліном IEEE 802.3 для зворотного представлення бітів
inline constexpr uint32_t POLYNOMIAL = 0xEDB88320u;

// Розрахунок одного 32-бітного елемента таблиці для заданого значення байта
constexpr uint32_t make_table_entry(uint8_t byte_value) noexcept {
    uint32_t crc = byte_value;
    for (int bit = 0; bit < 8; ++bit) {
        if (crc & 1u) {
            crc = (crc >> 1) ^ POLYNOMIAL;
        } else {
            crc >>= 1;
        }
    }
    return crc;
}

// Генерація повної таблиці на 256 записів
constexpr std::array<uint32_t, 256> generate_table() noexcept {
    std::array<uint32_t, 256> table{};
    for (size_t i = 0; i < 256; ++i) {
        table[i] = make_table_entry(static_cast<uint8_t>(i));
    }
    return table;
}

// Глобальна стала таблиця: створюється компілятором у секції .rodata
inline constexpr auto TABLE = generate_table();

// Потокове обчислення CRC-32 для довільного буфера пам'яті
constexpr uint32_t calculate(std::string_view data) noexcept {
    uint32_t crc = 0xFFFFFFFFu;
    for (char c : data) {
        const uint8_t byte = static_cast<uint8_t>(c);
        const uint8_t index = static_cast<uint8_t>(crc ^ byte);
        crc = (crc >> 8) ^ TABLE[index];
    }
    return crc ^ 0xFFFFFFFFu;
}

// Негайна функція (consteval): гарантує виконання ВИКЛЮЧНО компілятором
consteval uint32_t calculate_compile_time(std::string_view data) noexcept {
    return calculate(data);
}

} // namespace crc32

// ── Верифікація під час компіляції (Compile-Time Unit Testing) ────────────────

// 1. Перевірка на канонічному тестовому векторі "123456789"
// Результат зобов'язаний точно дорівнювати 0xCBF43926 за стандартом POSIX/IEEE
static_assert(crc32::calculate("123456789") == 0xCBF43926u,
              "Помилка розрахунку CRC-32 на стандартному тестовому векторі!");

// 2. Перевірка контрольної суми порожнього рядка
static_assert(crc32::calculate("") == 0x00000000u,
              "CRC-32 порожнього рядка мусить дорівнювати нулю!");

// 3. Перевірка окремих ключових комірок згенерованої таблиці
static_assert(crc32::TABLE[0] == 0x00000000u);
static_assert(crc32::TABLE[1] == 0x77073096u);
static_assert(crc32::TABLE[255] == 0x2D02EF8Du);
