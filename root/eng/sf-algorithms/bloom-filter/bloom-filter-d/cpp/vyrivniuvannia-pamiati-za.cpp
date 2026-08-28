#include <cstdint>
#include <new>
#include <cstddef>

namespace sys {

// Вирівняний виділювач пам'яті C++17
uint8_t* allocate_aligned_bitset(std::size_t bytes) {
    std::size_t aligned_bytes = (bytes + 63) & ~static_cast<std::size_t>(63);
    return static_cast<uint8_t*>(::operator new[](aligned_bytes, std::align_val_t{64}));
}

} // namespace sys
