#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define CANARY_HEAD 0xDEADBEEFCAFE0001ULL
#define CANARY_TAIL 0xDEADBEEFCAFE0002ULL

typedef struct {
    uint64_t head_canary;
    char raw_data[64];
    uint64_t tail_canary;
} GuardedBuffer;

void guarded_buffer_init(GuardedBuffer *gb) {
    if (!gb) return;
    gb->head_canary = CANARY_HEAD;
    gb->tail_canary = CANARY_TAIL;
    memset(gb->raw_data, 0, sizeof(gb->raw_data));
}

bool guarded_buffer_verify(const GuardedBuffer *gb) {
    if (!gb) return false;
    return (gb->head_canary == CANARY_HEAD) && (gb->tail_canary == CANARY_TAIL);
}

void guarded_buffer_write(GuardedBuffer *gb, const char *src, size_t len) {
    if (len > sizeof(gb->raw_data)) {
        printf("[!] Спроба переповнення: запис %zu байтів у буфер на %zu байтів\n",
               len, sizeof(gb->raw_data));
    }
    // Навмисна емуляція некоректного копіювання для демонстрації виявлення
    memcpy(gb->raw_data, src, len);
}

int main(void) {
    GuardedBuffer buffer;
    guarded_buffer_init(&buffer);

    // Спроба записати 80 байтів (переповнення на 16 байтів у tail_canary)
    char payload[80];
    memset(payload, 'A', sizeof(payload));

    guarded_buffer_write(&buffer, payload, sizeof(payload));

    if (!guarded_buffer_verify(&buffer)) {
        printf("[АЛАРМ] Пошкодження пам'яті виявлено! Tail Canary спотворено: 0x%llX\n",
               (unsigned long long)buffer.tail_canary);
    } else {
        printf("[OK] Цілісність буфера збережено.\n");
    }
    return 0;
}
