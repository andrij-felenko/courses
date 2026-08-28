#include <stdint.h>

#define CRASH_MAGIC_WORD  0xDEADBEEFU

typedef struct __attribute__((packed)) {
    uint32_t magic;           // CRASH_MAGIC_WORD
    uint32_t boot_counter;    // Лічильник запусків
    uint32_t timestamp;       // Час роботи пристрою до збою
    uint32_t reset_reason;    // Прапорці регістру RCC_CSR
    uint32_t r0, r1, r2, r3;
    uint32_t r12, lr, pc, xpsr;
    uint32_t hfsr, cfsr, mmfar, bfar;
    uint32_t stack_len;
    uint32_t stack_data[32];  // 128 байтів зрізу стека
    uint32_t crc32;           // Контрольна сума всього блоку
} crash_dump_t;

__attribute__((section(".noinit"))) static crash_dump_t g_crash_record;
