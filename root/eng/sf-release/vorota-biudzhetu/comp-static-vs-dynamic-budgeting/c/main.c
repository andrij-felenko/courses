#include <stdint.h>
#include <stddef.h>

#define STACK_WATERMARK_PATTERN 0xA5A5A5A5U

void stack_paint(uint32_t *stack_start, size_t word_count) {
    for (size_t i = 0; i < word_count; ++i) {
        stack_start[i] = STACK_WATERMARK_PATTERN;
    }
}

size_t stack_measure_used_bytes(const uint32_t *stack_start, size_t word_count) {
    size_t unused_words = 0;
    while (unused_words < word_count && stack_start[unused_words] == STACK_WATERMARK_PATTERN) {
        unused_words++;
    }
    return (word_count - unused_words) * sizeof(uint32_t);
}
