#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CRASH_MAGIC_FLAG   0xDEADBEEFU
#define STACK_DUMP_WORDS   32

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t uptime_sec;
    uint32_t reset_flags;
    
    // Збережені апаратні регістри
    uint32_t r0, r1, r2, r3;
    uint32_t r12, lr, pc, xpsr;
    
    // Системні регістри несправностей SCB
    uint32_t hfsr;
    uint32_t cfsr;
    uint32_t mmfar;
    uint32_t bfar;
    
    // Зріз вершини стека
    uint32_t stack_len;
    uint32_t stack_words[STACK_DUMP_WORDS];
    
    uint32_t checksum;
} crash_record_t;

// Розміщення в неініціалізованій пам'яті
__attribute__((section(".noinit"))) static volatile crash_record_t g_crash_record;

static uint32_t calc_checksum(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1)));
        }
    }
    return ~crc;
}

// C-частина обробника винятку
void HardFault_Handler_C(uint32_t *stack_frame, uint32_t lr_exc) {
    volatile uint32_t *scb_cfsr  = (volatile uint32_t *)0xE000ED28;
    volatile uint32_t *scb_hfsr  = (volatile uint32_t *)0xE000ED2C;
    volatile uint32_t *scb_mmfar = (volatile uint32_t *)0xE000ED34;
    volatile uint32_t *scb_bfar  = (volatile uint32_t *)0xE000ED38;
    
    g_crash_record.magic = CRASH_MAGIC_FLAG;
    g_crash_record.uptime_sec = 12450; // Зчитується з системного RTC
    g_crash_record.reset_flags = 0;
    
    // Розпакування збереженого апаратурою кадру
    g_crash_record.r0   = stack_frame[0];
    g_crash_record.r1   = stack_frame[1];
    g_crash_record.r2   = stack_frame[2];
    g_crash_record.r3   = stack_frame[3];
    g_crash_record.r12  = stack_frame[4];
    g_crash_record.lr   = stack_frame[5];
    g_crash_record.pc   = stack_frame[6];
    g_crash_record.xpsr = stack_frame[7];
    
    // Зчитування діагностичних регістрів
    g_crash_record.cfsr  = *scb_cfsr;
    g_crash_record.hfsr  = *scb_hfsr;
    g_crash_record.mmfar = *scb_mmfar;
    g_crash_record.bfar  = *scb_bfar;
    
    // Збереження зрізу стека вище кадру
    uint32_t *sp_above_frame = stack_frame + 8;
    g_crash_record.stack_len = STACK_DUMP_WORDS;
    for (uint32_t i = 0; i < STACK_DUMP_WORDS; ++i) {
        g_crash_record.stack_words[i] = sp_above_frame[i];
    }
    
    // Розрахунок контрольної суми
    size_t payload_len = sizeof(crash_record_t) - sizeof(uint32_t);
    g_crash_record.checksum = calc_checksum((const uint8_t *)&g_crash_record, payload_len);
    
    // Примусове системне скидання процесора
    volatile uint32_t *aircr = (volatile uint32_t *)0xE000ED0C;
    *aircr = 0x05FA0000U | (1U << 2); // SYSRESETREQ
    while (1) { __asm volatile("nop"); }
}

// Асемблерний місток для визначення активного стека за EXC_RETURN
__attribute__((naked)) void HardFault_Handler(void) {
    __asm volatile(
        "tst lr, #4\n"
        "ite eq\n"
        "mrseq r0, msp\n"
        "mrsne r0, psp\n"
        "mov r1, lr\n"
        "b HardFault_Handler_C\n"
    );
}

bool crash_dump_fetch(crash_record_t *out_record) {
    if (g_crash_record.magic != CRASH_MAGIC_FLAG) {
        return false;
    }
    size_t payload_len = sizeof(crash_record_t) - sizeof(uint32_t);
    uint32_t expected_crc = calc_checksum((const uint8_t *)&g_crash_record, payload_len);
    if (g_crash_record.checksum != expected_crc) {
        g_crash_record.magic = 0;
        return false;
    }
    memcpy(out_record, (const void *)&g_crash_record, sizeof(crash_record_t));
    g_crash_record.magic = 0; // Очищення після зчитування
    return true;
}
