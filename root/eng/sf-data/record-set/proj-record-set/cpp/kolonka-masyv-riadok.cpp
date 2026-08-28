#include <cstdint>
#include <functional>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <unordered_map>
#include <variant>
#include <vector>

enum class Type : uint8_t { Int64, Text };

struct Column {
    std::string              name;
    Type                     type;
    bool                     generated = false;  // ключ, який видає база
    bool                     key_ref   = false;  // ключ або посилання на ключ
    std::vector<int64_t>     i64;                // живий, якщо type == Int64
    std::vector<std::string> txt;                // живий, якщо type == Text
    std::vector<uint64_t>    valid;              // біт j: 1 — значення є, 0 — NULL
};
// колонка id у нашій таблиці несе ОБИДВА прапорці: її видає база (generated)
// і її значення проходить через книгу ключів (key_ref)

inline bool bit(const std::vector<uint64_t>& mask, size_t j) {
    return (mask[j >> 6] >> (j & 63)) & 1ull;
}

inline void set_bit(std::vector<uint64_t>& mask, size_t j, bool on) {
    uint64_t&      word = mask[j >> 6];
    const uint64_t b    = 1ull << (j & 63);
    word = on ? (word | b) : (word & ~b);
}
