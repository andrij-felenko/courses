#include <iostream>
#include <array>
#include <span>
#include <cstdint>

namespace ble::crypto {
    using Key128 = std::array<uint8_t, 16>;
    using Hash24 = std::array<uint8_t, 3>;
    Hash24 ah(const Key128& irk, std::span<const uint8_t, 3> prand) noexcept;
}

bool run_selftest() noexcept {
    constexpr ble::crypto::Key128 irk = {
        0x9B, 0x7B, 0x63, 0x41, 0x1A, 0x29, 0x55, 0xB1,
        0x8F, 0x8F, 0x86, 0x16, 0xB7, 0xB8, 0x0B, 0x7A
    };
    constexpr std::array<uint8_t, 3> prand = {0x70, 0x81, 0x94};

    const auto hash = ble::crypto::ah(irk, prand);
    if (hash[0] == 0x05 && hash[1] == 0x13 && hash[2] == 0x46) {
        std::cout << "[OK] ah() test vector verified.\n";
        return true;
    }

    std::cerr << "[FAIL] ah() test vector mismatch!\n";
    return false;
}
