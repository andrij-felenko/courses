#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define POOL_SIZE       1024
#define SHADOW_SIZE     (POOL_SIZE >> 3) // 128 байтів тіні (1 байт на 8 байтів пулу)
#define REDZONE_SIZE    16

#define SHADOW_VALID    0x00
#define SHADOW_REDZONE  0xFA
#define SHADOW_FREED    0xFD

static uint8_t g_memory_pool[POOL_SIZE];
static uint8_t g_shadow_memory[SHADOW_SIZE];
static size_t g_pool_offset = 0;

// Пряма трансляція адреси: обчислення індексу в тіньовому масиві
static inline size_t addr_to_shadow(const void *addr) {
    uintptr_t offset = (uintptr_t)addr - (uintptr_t)g_memory_pool;
    return (size_t)(offset >> 3);
}

// Отруєння діапазону пам'яті певним маркером
void poison_range(const void *addr, size_t size, uint8_t tag) {
    size_t start_shadow = addr_to_shadow(addr);
    size_t shadow_bytes = (size + 7) >> 3;
    for (size_t i = 0; i < shadow_bytes && (start_shadow + i) < SHADOW_SIZE; ++i) {
        g_shadow_memory[start_shadow + i] = tag;
    }
}

// Зняття отруєння для валідних корисних даних
void unpoison_range(const void *addr, size_t size) {
    size_t start_shadow = addr_to_shadow(addr);
    size_t full_chunks = size >> 3;
    size_t remainder = size & 7;

    for (size_t i = 0; i < full_chunks; ++i) {
        g_shadow_memory[start_shadow + i] = SHADOW_VALID;
    }
    if (remainder > 0) {
        g_shadow_memory[start_shadow + full_chunks] = (uint8_t)remainder;
    }
}

// Перевірка 1 байта пам'яті перед виконанням load/store
bool check_access(const void *addr) {
    if (addr < (void *)g_memory_pool || addr >= (void *)(g_memory_pool + POOL_SIZE)) {
        printf("[ASAN-EMU] CRASH: Поза межами адресної пам'яті! Адреса: %p\n", addr);
        return false;
    }

    size_t s_idx = addr_to_shadow(addr);
    uint8_t shadow_val = g_shadow_memory[s_idx];
    size_t byte_in_chunk = ((uintptr_t)addr - (uintptr_t)g_memory_pool) & 7;

    if (shadow_val == SHADOW_VALID) {
        return true; // Усі 8 байтів валідні
    }
    if (shadow_val == SHADOW_REDZONE) {
        printf("[ASAN-EMU] CRASH: Спроба запису в REDZONE (Buffer Overflow)! Адреса: %p\n", addr);
        return false;
    }
    if (shadow_val == SHADOW_FREED) {
        printf("[ASAN-EMU] CRASH: Спроба доступу до звільненої пам'яті (Use-After-Free)! Адреса: %p\n", addr);
        return false;
    }
    if (shadow_val >= 1 && shadow_val <= 7) {
        if (byte_in_chunk < shadow_val) {
            return true;
        }
        printf("[ASAN-EMU] CRASH: Частковий вихід за межі (Tail Overflow)! Адреса: %p\n", addr);
        return false;
    }
    return false;
}

// Безпечний розподілювач пам'яті з червоними зонами
void *sanitized_malloc(size_t payload_size) {
    size_t total_size = REDZONE_SIZE + payload_size + REDZONE_SIZE;
    if (g_pool_offset + total_size > POOL_SIZE) {
        return NULL;
    }

    uint8_t *base = g_memory_pool + g_pool_offset;
    uint8_t *left_rz = base;
    uint8_t *payload = base + REDZONE_SIZE;
    uint8_t *right_rz = payload + payload_size;

    // Отруюємо ліву та праву червоні зони
    poison_range(left_rz, REDZONE_SIZE, SHADOW_REDZONE);
    unpoison_range(payload, payload_size);
    poison_range(right_rz, REDZONE_SIZE, SHADOW_REDZONE);

    g_pool_offset += total_size;
    return payload;
}

// Звільнення пам'яті та відправка в карантин
void sanitized_free(void *ptr, size_t payload_size) {
    if (!ptr) return;
    uint8_t *left_rz = (uint8_t *)ptr - REDZONE_SIZE;
    size_t total_size = REDZONE_SIZE + payload_size + REDZONE_SIZE;
    // Весь блок (разом із зонами) отруюється як FREED
    poison_range(left_rz, total_size, SHADOW_FREED);
}

int main(void) {
    memset(g_shadow_memory, SHADOW_REDZONE, sizeof(g_shadow_memory));
    printf("=== Демонстрація переповнення буфера (Heap Buffer Overflow) ===\n");
    
    char *buf = (char *)sanitized_malloc(10); // Виділяємо 10 байтів
    
    // Запис у межах виділеного блоку
    for (int i = 0; i < 10; ++i) {
        if (check_access(&buf[i])) {
            buf[i] = 'A' + (char)i;
        }
    }
    printf("Успішно записано 10 байтів.\n");

    // Спроба виходу за межі (Buffer Overflow на 11-му байті)
    printf("Спроба запису в buf[10] (індекс 10 поза межами 0..9):\n");
    if (check_access(&buf[10])) {
        buf[10] = 'X';
    }

    printf("\n=== Демонстрація Use-After-Free ===\n");
    sanitized_free(buf, 10);
    printf("Пам'ять звільнено (free).\n");

    printf("Спроба читання з buf[0] після free:\n");
    if (check_access(&buf[0])) {
        char val = buf[0];
        (void)val;
    }

    return 0;
}
