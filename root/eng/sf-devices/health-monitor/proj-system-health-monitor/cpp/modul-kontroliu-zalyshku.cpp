namespace Health {

inline constexpr uint32_t StackCanaryWord = 0xA5A5A5A5U;
inline constexpr size_t StackSafeLimitBytes = 256U;
inline constexpr size_t StackDangerLimitBytes = 64U;

[[nodiscard]] uint16_t check_task_stack(std::span<const uint32_t> stack_memory) noexcept {
    if (stack_memory.size() < 16) {
        return 0;
    }

    // 1. Швидка перевірка цілісності канарок на дні стека
    if (stack_memory[0] != StackCanaryWord || stack_memory[1] != StackCanaryWord) {
        return 0; // Стек пошкоджено
    }

    // 2. Сканування глибини водяного знака
    size_t unused_words = 0;
    for (const auto word : stack_memory) {
        if (word != StackCanaryWord) {
            break;
        }
        ++unused_words;
    }

    const size_t free_bytes = unused_words * sizeof(uint32_t);

    if (free_bytes >= StackSafeLimitBytes) {
        return 1000;
    }
    if (free_bytes <= StackDangerLimitBytes) {
        return static_cast<uint16_t>((free_bytes * 400) / StackDangerLimitBytes);
    }

    const size_t range = StackSafeLimitBytes - StackDangerLimitBytes;
    const size_t delta = free_bytes - StackDangerLimitBytes;
    return static_cast<uint16_t>(400 + (delta * 600) / range);
}

} // namespace Health
