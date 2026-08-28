#include <linux/filter.h>
#include <cstdint>

namespace sys {

// Представлення BPF інструкції для C++20
struct BpfInstruction {
    uint16_t code;
    uint8_t  jt;
    uint8_t  jf;
    uint32_t k;

    constexpr explicit operator ::sock_filter() const noexcept {
        return ::sock_filter{ code, jt, jf, k };
    }
};

} // namespace sys
