// RAII-обгортка керування когерентністю D-Cache (C++)
#include <cstdint>
#include <cstddef>
#include <span>

template <typename T>
struct DmaCacheManager {
    static void invalidate(std::span<T> memory_block) noexcept {
        auto addr = reinterpret_cast<uint32_t*>(const_cast<std::remove_cv_t<T>*>(memory_block.data()));
        SCB_InvalidateDCache_by_Addr(addr, memory_block.size_bytes());
    }

    static void clean(std::span<const T> memory_block) noexcept {
        auto addr = reinterpret_cast<uint32_t*>(const_cast<T*>(memory_block.data()));
        SCB_CleanDCache_by_Addr(addr, memory_block.size_bytes());
    }
};
