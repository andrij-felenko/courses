#include <cstdint>
#include <span>

class ChecksumVerifier {
public:
    [[nodiscard]] static uint32_t adler32(std::span<const uint8_t> data) noexcept {
        uint32_t a = 1, b = 0;
        constexpr uint32_t kModAdler = 65521;

        for (uint8_t byte : data) {
            a = (a + byte) % kModAdler;
            b = (b + a) % kModAdler;
        }
        return (b << 16) | a;
    }
};
