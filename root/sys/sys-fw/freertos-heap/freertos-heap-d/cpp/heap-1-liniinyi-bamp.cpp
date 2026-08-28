#include <array>
#include <cstddef>
#include <cstdint>

template <std::size_t HeapSizeBytes>
class BumpAllocatorState {
public:
    static inline std::array<std::uint8_t, HeapSizeBytes> heap_storage{};
    static inline std::size_t next_free_byte{0};
};
