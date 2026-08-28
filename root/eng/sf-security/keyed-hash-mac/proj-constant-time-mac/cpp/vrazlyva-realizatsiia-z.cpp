#include <cstddef>
#include <cstdint>
#include <span>

/* НЕБЕЗПЕЧНО: Ранній вихід дозволяє побайтовий підбір тегу */
[[nodiscard]] bool vulnerable_verify_mac(std::span<const uint8_t> expected,
                                         std::span<const uint8_t> received) noexcept {
    if (expected.size() != received.size()) {
        return false;
    }
    for (size_t i = 0; i < expected.size(); ++i) {
        if (expected[i] != received[i]) {
            return false; /* Час повернення корелює з кількістю вгаданих байтів */
        }
    }
    return true;
}
