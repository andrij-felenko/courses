#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

typedef int32_t (*jit_func_t)(int32_t);

// Перевірка цільової архітектури під час збірки
#if defined(__x86_64__) || defined(_M_X64)
#define ARCH_X86_64 1
#elif defined(__aarch64__) || defined(_M_ARM64)
#define ARCH_AARCH64 1
#else
#error "Непідтримувана процесорна архітектура для прямої генерації коду"
#endif

// Структура дескриптора виділеного блоку пам'яті JIT
typedef struct {
    uint8_t *buffer;
    size_t size;
    size_t code_len;
} jit_block_t;

// Виділення анонімної сторінки пам'яті
int jit_alloc(jit_block_t *block, size_t min_size) {
    long page_size = sysconf(_SC_PAGESIZE);
    if (page_size <= 0) page_size = 4096;

    // Округлення розміру до найближчого розміру цілої сторінки
    size_t alloc_size = (min_size + page_size - 1) & ~(page_size - 1);

    // Пам'ять спочатку виділяється як доступна на читання та запис (RW)
    void *ptr = mmap(NULL, alloc_size, PROT_READ | PROT_WRITE,
                     MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
    if (ptr == MAP_FAILED) {
        perror("mmap failed");
        return -1;
    }

    block->buffer = (uint8_t *)ptr;
    block->size = alloc_size;
    block->code_len = 0;
    return 0;
}

// Звільнення сторінки пам'яті
void jit_free(jit_block_t *block) {
    if (block->buffer && block->size > 0) {
        munmap(block->buffer, block->size);
        block->buffer = NULL;
        block->size = 0;
        block->code_len = 0;
    }
}

// Емісія машинного коду лінійної функції: f(x) = x * multiplier + addend
int jit_emit_linear(jit_block_t *block, int32_t multiplier, int32_t addend) {
#if defined(ARCH_X86_64)
    uint8_t code[] = {
        // IMUL EDI, EDI, imm32 (6 байтів)
        0x69, 0xFF,
        (uint8_t)(multiplier & 0xFF),
        (uint8_t)((multiplier >> 8) & 0xFF),
        (uint8_t)((multiplier >> 16) & 0xFF),
        (uint8_t)((multiplier >> 24) & 0xFF),

        // ADD EDI, imm32 (6 байтів)
        0x81, 0xC7,
        (uint8_t)(addend & 0xFF),
        (uint8_t)((addend >> 8) & 0xFF),
        (uint8_t)((addend >> 16) & 0xFF),
        (uint8_t)((addend >> 24) & 0xFF),

        // MOV EAX, EDI (2 байти)
        0x89, 0xF8,

        // RET (1 байт)
        0xC3
    };
    size_t len = sizeof(code);
#elif defined(ARCH_AARCH64)
    uint32_t imm_mul = (uint32_t)multiplier & 0xFFFF;
    uint32_t imm_add = (uint32_t)addend & 0xFFFF;

    uint32_t code[] = {
        // MOVZ W1, #multiplier
        0x52800000 | (imm_mul << 5) | 1,
        // MUL W0, W0, W1
        0x1B017C00,
        // MOVZ W1, #addend
        0x52800000 | (imm_add << 5) | 1,
        // ADD W0, W0, W1
        0x0B010000,
        // RET
        0xD65F03C0
    };
    size_t len = sizeof(code);
#endif

    if (len > block->size) return -1;
    memcpy(block->buffer, code, len);
    block->code_len = len;
    return 0;
}

// Захист пам'яті W^X та апаратна синхронізація кешів
int jit_finalize(jit_block_t *block) {
    // 1. Зміна прав сторінки на RX (Read + Execute)
    if (mprotect(block->buffer, block->size, PROT_READ | PROT_EXEC) != 0) {
        perror("mprotect RX failed");
        return -1;
    }

    // 2. Інвалідація кешів: D-Cache clean + I-Cache invalidate + ISB
    __builtin___clear_cache((char *)block->buffer,
                            (char *)block->buffer + block->code_len);
    return 0;
}

// Гаряча модифікація константи множника у згенерованому коді
int jit_patch_multiplier(jit_block_t *block, int32_t new_multiplier) {
    // 1. Відкриваємо права на запис RW
    if (mprotect(block->buffer, block->size, PROT_READ | PROT_WRITE) != 0) {
        perror("mprotect RW failed");
        return -1;
    }

    // 2. Модифікуємо байти константи
#if defined(ARCH_X86_64)
    // Зсув константи multiplier в інструкції IMUL дорівнює 2 байтам
    uint8_t *patch_ptr = block->buffer + 2;
    patch_ptr[0] = (uint8_t)(new_multiplier & 0xFF);
    patch_ptr[1] = (uint8_t)((new_multiplier >> 8) & 0xFF);
    patch_ptr[2] = (uint8_t)((new_multiplier >> 16) & 0xFF);
    patch_ptr[3] = (uint8_t)((new_multiplier >> 24) & 0xFF);
#elif defined(ARCH_AARCH64)
    // Інструкція MOVZ W1, #multiplier знаходиться за зсувом 0
    uint32_t *patch_ptr = (uint32_t *)block->buffer;
    uint32_t imm = (uint32_t)new_multiplier & 0xFFFF;
    patch_ptr[0] = 0x52800000 | (imm << 5) | 1;
#endif

    // 3. Закриваємо запис, повертаємо права RX та синхронізуємо кеші
    return jit_finalize(block);
}

int main(void) {
    jit_block_t jit;
    if (jit_alloc(&jit, 4096) != 0) {
        return EXIT_FAILURE;
    }

    printf("1. Генерація функції: f(x) = x * 10 + 7\n");
    if (jit_emit_linear(&jit, 10, 7) != 0 || jit_finalize(&jit) != 0) {
        jit_free(&jit);
        return EXIT_FAILURE;
    }

    jit_func_t func = (jit_func_t)jit.buffer;
    int32_t input = 5;
    int32_t res1 = func(input);
    printf("   Результат f(%d) = %d (очікувано: 57)\n", input, res1);

    printf("2. Гаряче латання коду на льоту: f(x) = x * 100 + 7\n");
    if (jit_patch_multiplier(&jit, 100) != 0) {
        jit_free(&jit);
        return EXIT_FAILURE;
    }

    int32_t res2 = func(input);
    printf("   Результат f(%d) після патчу = %d (очікувано: 507)\n", input, res2);

    jit_free(&jit);
    printf("3. Пам'ять успішно звільнено.\n");
    return EXIT_SUCCESS;
}
