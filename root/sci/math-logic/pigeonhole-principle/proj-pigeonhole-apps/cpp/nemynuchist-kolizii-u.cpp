#include <iostream>
#include <string_view>
#include <cstdint>

uint16_t simple_16bit_hash(std::string_view str) {
    uint16_t hash = 0x5555;
    for (char ch : str) {
        hash ^= static_cast<uint16_t>(ch);
        hash = static_cast<uint16_t>((hash << 5) | (hash >> 11));
    }
    return hash;
}

int main() {
    constexpr uint32_t cell_count = 1 << 16;
    std::cout << "=== 16-бітний простір криптографічних комірок ===\n";
    std::cout << "Доступно комірок: " << cell_count << "\n";
    std::cout << "Межа Діріхле для 100% гарантії колізії: " << cell_count + 1 << " входів\n";

    std::string_view msg1 = "Message-A";
    std::string_view msg2 = "Message-B";
    std::cout << "Hash('" << msg1 << "') = 0x" << std::hex << simple_16bit_hash(msg1) << "\n";
    std::cout << "Hash('" << msg2 << "') = 0x" << std::hex << simple_16bit_hash(msg2) << "\n";
    return 0;
}
