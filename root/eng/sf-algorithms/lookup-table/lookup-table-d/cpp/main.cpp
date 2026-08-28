#include <cstdint>
#include <array>

class HexValidator {
public:
    static consteval auto generate_table() {
        std::array<bool, 256> table{};
        for (char c = '0'; c <= '9'; ++c) table[static_cast<uint8_t>(c)] = true;
        for (char c = 'a'; c <= 'f'; ++c) table[static_cast<uint8_t>(c)] = true;
        for (char c = 'A'; c <= 'F'; ++c) table[static_cast<uint8_t>(c)] = true;
        return table;
    }

    static inline constexpr auto Table = generate_table();

    [[nodiscard]] static constexpr bool is_hex(uint8_t c) noexcept {
        return Table[c];
    }
};
