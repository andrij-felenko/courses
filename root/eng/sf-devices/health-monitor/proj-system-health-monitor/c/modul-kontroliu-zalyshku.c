#define STACK_CANARY_WORD       0xA5A5A5A5U
#define STACK_SAFE_LIMIT_BYTES  256U
#define STACK_DANGER_LIMIT_BYTES 64U

uint16_t health_check_task_stack(const uint32_t *stack_bottom, size_t total_words) {
    if (!stack_bottom || total_words < 16) {
        return 0;
    }

    // 1. Швидка перевірка канарки на самому дні стека
    if (stack_bottom[0] != STACK_CANARY_WORD || stack_bottom[1] != STACK_CANARY_WORD) {
        return 0; // Стек повністю зруйновано
    }

    // 2. Підрахунок недоторканих слів від дна стека вгору
    size_t unused_words = 0;
    while (unused_words < total_words && stack_bottom[unused_words] == STACK_CANARY_WORD) {
        unused_words++;
    }

    size_t free_bytes = unused_words * sizeof(uint32_t);

    if (free_bytes >= STACK_SAFE_LIMIT_BYTES) {
        return 1000;
    }
    if (free_bytes <= STACK_DANGER_LIMIT_BYTES) {
        return (uint16_t)((free_bytes * 400) / STACK_DANGER_LIMIT_BYTES);
    }

    // Лінійна інтерполяція між 400 та 1000
    uint32_t range = STACK_SAFE_LIMIT_BYTES - STACK_DANGER_LIMIT_BYTES;
    uint32_t delta = free_bytes - STACK_DANGER_LIMIT_BYTES;
    return (uint16_t)(400 + (delta * 600) / range);
}
