#include <string_view>
#include <charconv>
#include <system_error>
#include <optional>
#include <cstdint>

// Предметна модель вісімкових прав Unix
struct UnixPermissions {
    uint16_t special : 3;
    uint16_t user    : 3;
    uint16_t group   : 3;
    uint16_t other   : 3;

    // Збираємо 12-бітну маску для системних викликів (наприклад, chmod)
    [[nodiscard]] uint16_t to_mask() const noexcept {
        return (special << 9) | (user << 6) | (group << 3) | other;
    }
};

// Парсер, що не генерує винятків і не виділяє пам'яті
std::optional<UnixPermissions> parse_chmod_octal(std::string_view input) noexcept {
    // 1. Відкидаємо можливий програмістський префікс "0o" або класичний "0"
    if (input.starts_with("0o") || input.starts_with("0O")) {
        input.remove_prefix(2);
    } else if (input.starts_with('0') && input.length() > 1) {
        input.remove_prefix(1);
    }

    // 2. Права не можуть містити більше ніж 4 вісімкові цифри (максимум 7777)
    if (input.empty() || input.length() > 4) {
        return std::nullopt;
    }

    uint16_t raw_val = 0;
    
    // 3. Безпечний парсинг з основою 8 без аллокацій
    auto [ptr, ec] = std::from_chars(input.data(), input.data() + input.size(), raw_val, 8);

    // 4. Перевірка на успіх і відсутність зайвого «сміття» в кінці рядка
    if (ec != std::errc() || ptr != input.data() + input.size()) {
        return std::nullopt;
    }

    // 5. Розпакування зсувами для ініціалізації бітових полів
    return UnixPermissions{
        static_cast<uint16_t>((raw_val >> 9) & 7),
        static_cast<uint16_t>((raw_val >> 6) & 7),
        static_cast<uint16_t>((raw_val >> 3) & 7),
        static_cast<uint16_t>(raw_val & 7)
    };
}
