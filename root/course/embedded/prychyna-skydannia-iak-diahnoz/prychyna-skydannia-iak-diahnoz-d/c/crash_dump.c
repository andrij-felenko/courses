// crash_dump.c — реалізація перехоплення та збереження краху
#include "crash_dump.h"
#include <string.h>

// Макроси базових регістрів ARM Cortex-M та STM32 RCC
#define SCB_CFSR    (*(volatile uint32_t*)0xE000ED28U)
#define SCB_HFSR    (*(volatile uint32_t*)0xE000ED2CU)
#define SCB_MMFAR   (*(volatile uint32_t*)0xE000ED34U)
#define SCB_BFAR    (*(volatile uint32_t*)0xE000ED38U)
#define SCB_AIRCR   (*(volatile uint32_t*)0xE000ED0CU)

#define RCC_CSR     (*(volatile uint32_t*)0x40023874U) // Приклад адреси для STM32F4
#define RCC_CSR_RMVF_BIT    (1U << 24)
#define RCC_CSR_BOR_BIT     (1U << 25)
#define RCC_CSR_PIN_BIT     (1U << 26)
#define RCC_CSR_POR_BIT     (1U << 27)
#define RCC_CSR_SFT_BIT     (1U << 28)
#define RCC_CSR_IWDG_BIT    (1U << 29)
#define RCC_CSR_WWDG_BIT    (1U << 30)

// Розміщення в секції Retention RAM (.noinit)
__attribute__((section(".noinit"))) static crash_dump_t g_crash_dump;
static uint32_t g_saved_rcc_csr = 0;
static reset_cause_t g_detected_cause = RESET_CAUSE_UNKNOWN;

// Простий швидкий CRC32 (IEEE 802.3)
static uint32_t calc_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1U)));
        }
    }
    return ~crc;
}

// Рання ініціалізація та фіксація прапорців RCC_CSR
void crash_dump_early_init(void) {
    g_saved_rcc_csr = RCC_CSR;
    
    // Негайне очищення накопичувальних прапорців
    RCC_CSR |= RCC_CSR_RMVF_BIT;
    
    // Перевірка наявності валідного дампу HardFault у .noinit
    if (crash_dump_has_valid_record()) {
        g_detected_cause = (reset_cause_t)g_crash_dump.reset_cause;
        return;
    }
    
    // Розкодування апаратних прапорців контролера скидання
    if (g_saved_rcc_csr & RCC_CSR_BOR_BIT) {
        g_detected_cause = RESET_CAUSE_BROWNOUT;
    } else if (g_saved_rcc_csr & RCC_CSR_POR_BIT) {
        g_detected_cause = RESET_CAUSE_COLD_BOOT;
    } else if ((g_saved_rcc_csr & RCC_CSR_IWDG_BIT) || (g_saved_rcc_csr & RCC_CSR_WWDG_BIT)) {
        g_detected_cause = RESET_CAUSE_WATCHDOG;
    } else if (g_saved_rcc_csr & RCC_CSR_SFT_BIT) {
        g_detected_cause = RESET_CAUSE_SOFTWARE;
    } else if (g_saved_rcc_csr & RCC_CSR_PIN_BIT) {
        g_detected_cause = RESET_CAUSE_PIN_RESET;
    } else {
        g_detected_cause = RESET_CAUSE_UNKNOWN;
    }
}

bool crash_dump_has_valid_record(void) {
    if (g_crash_dump.magic != CRASH_DUMP_MAGIC) {
        return false;
    }
    size_t payload_len = sizeof(crash_dump_t) - sizeof(uint32_t); // Без поля crc32
    uint32_t expected_crc = calc_crc32((const uint8_t*)&g_crash_dump, payload_len);
    return (g_crash_dump.crc32 == expected_crc);
}

const crash_dump_t* crash_dump_get(void) {
    return &g_crash_dump;
}

void crash_dump_clear(void) {
    g_crash_dump.magic = 0;
    g_crash_dump.crc32 = 0;
}

// C-обробник аварії, що викликається з асемблерного трампліна
void prv_c_hardfault_handler(const uint32_t *stack_frame, uint32_t exc_return) {
    // 1. Заборона всіх переривань
    __asm volatile("cpsid i" : : : "memory");
    
    // 2. Заповнення структури дампу
    g_crash_dump.magic = CRASH_DUMP_MAGIC;
    g_crash_dump.rcc_csr = g_saved_rcc_csr;
    g_crash_dump.reset_cause = RESET_CAUSE_HARDFAULT;
    g_crash_dump.uptime_ms = 0; // Якщо доступний таймер SysTick
    
    g_crash_dump.r0   = stack_frame[0];
    g_crash_dump.r1   = stack_frame[1];
    g_crash_dump.r2   = stack_frame[2];
    g_crash_dump.r3   = stack_frame[3];
    g_crash_dump.r12  = stack_frame[4];
    g_crash_dump.lr   = stack_frame[5];
    g_crash_dump.pc   = stack_frame[6];
    g_crash_dump.xpsr = stack_frame[7];
    
    g_crash_dump.cfsr  = SCB_CFSR;
    g_crash_dump.hfsr  = SCB_HFSR;
    g_crash_dump.bfar  = SCB_BFAR;
    g_crash_dump.mmfar = SCB_MMFAR;
    g_crash_dump.exc_return = exc_return;
    
    // Копіювання слів стека аварії
    for (uint32_t i = 0; i < CRASH_STACK_WORDS; ++i) {
        g_crash_dump.stack_dump[i] = stack_frame[i];
    }
    
    g_crash_dump.assert_file[0] = '\0';
    g_crash_dump.assert_line = 0;
    
    // Розрахунок CRC32
    size_t payload_len = sizeof(crash_dump_t) - sizeof(uint32_t);
    g_crash_dump.crc32 = calc_crc32((const uint8_t*)&g_crash_dump, payload_len);
    
    // 3. Бар'єр пам'яті та системний перезапуск
    __asm volatile("dsb" : : : "memory");
    SCB_AIRCR = 0x05FA0000U | (1U << 2); // SYSRESETREQ
    for (;;) { }
}

// Голий асемблерний трамплін для перехоплення HardFault
__attribute__((naked)) void HardFault_Handler(void) {
    __asm volatile(
        "tst   lr, #4               \n" // Перевірка біта 2 EXC_RETURN (SPSEL)
        "ite   eq                   \n"
        "mrseq r0, msp              \n" // Якщо 0 -> стек MSP у R0
        "mrsne r0, psp              \n" // Якщо 1 -> стек PSP у R0
        "mov   r1, lr               \n" // EXC_RETURN у R1
        "b     prv_c_hardfault_handler \n"
    );
}

// Програмний Assert
void crash_dump_software_assert(const char* file, uint32_t line) {
    __asm volatile("cpsid i" : : : "memory");
    
    g_crash_dump.magic = CRASH_DUMP_MAGIC;
    g_crash_dump.rcc_csr = g_saved_rcc_csr;
    g_crash_dump.reset_cause = RESET_CAUSE_SOFTWARE;
    g_crash_dump.uptime_ms = 0;
    
    g_crash_dump.cfsr = 0;
    g_crash_dump.hfsr = 0;
    g_crash_dump.bfar = 0;
    g_crash_dump.mmfar = 0;
    
    strncpy(g_crash_dump.assert_file, file, sizeof(g_crash_dump.assert_file) - 1);
    g_crash_dump.assert_file[sizeof(g_crash_dump.assert_file) - 1] = '\0';
    g_crash_dump.assert_line = line;
    
    size_t payload_len = sizeof(crash_dump_t) - sizeof(uint32_t);
    g_crash_dump.crc32 = calc_crc32((const uint8_t*)&g_crash_dump, payload_len);
    
    __asm volatile("dsb" : : : "memory");
    SCB_AIRCR = 0x05FA0000U | (1U << 2);
    for (;;) { }
}
