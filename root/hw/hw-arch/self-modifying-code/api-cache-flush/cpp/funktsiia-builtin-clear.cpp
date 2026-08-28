#include <span>
#include <cstdint>

// Ідіоматична C++ обгортка над вбудованою функцією компілятора
inline void clear_instruction_cache(std::span<const uint8_t> code_range) noexcept {
    __builtin___clear_cache(
        reinterpret_cast<char*>(const_cast<uint8_t*>(code_range.data())),
        reinterpret_cast<char*>(const_cast<uint8_t*>(code_range.data() + code_range.size()))
    );
}
