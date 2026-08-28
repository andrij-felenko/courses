#include <cstdint>
#include <cstddef>
#include <span>
#include <algorithm>

class StackMonitor {
public:
    static constexpr uint32_t Watermark = 0xA5A5A5A5U;

    static void paint(std::span<uint32_t> stack_arena) noexcept {
        std::fill(stack_arena.begin(), stack_arena.end(), Watermark);
    }

    [[nodiscard]] static size_t measure_used_bytes(std::span<const uint32_t> stack_arena) noexcept {
        const auto it = std::find_if(stack_arena.begin(), stack_arena.end(),
                                     [](uint32_t val) noexcept { return val != Watermark; });
        const auto unused_words = static_cast<size_t>(std::distance(stack_arena.begin(), it));
        return (stack_arena.size() - unused_words) * sizeof(uint32_t);
    }
};
