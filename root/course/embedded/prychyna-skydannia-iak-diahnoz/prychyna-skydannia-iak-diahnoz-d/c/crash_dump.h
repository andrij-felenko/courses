// crash_dump.h — структури та інтерфейс діагностики крахів
#ifndef CRASH_DUMP_H
#define CRASH_DUMP_H

#include <stdint.h>
#include <stdbool.h>

#define CRASH_DUMP_MAGIC    0x43525348U  // ASCII 'CRSH'
#define CRASH_STACK_WORDS   16U

// Класифікована причина скидання MCU
typedef enum {
    RESET_CAUSE_UNKNOWN     = 0,
    RESET_CAUSE_COLD_BOOT   = 1,  // Power-on reset (POR/PDR)
    RESET_CAUSE_BROWNOUT    = 2,  // Просадка напруги живлення (BOR)
    RESET_CAUSE_WATCHDOG    = 3,  // Таймаут сторожового таймера (IWDG/WWDG)
    RESET_CAUSE_SOFTWARE    = 4,  // Програмний ресет / Assert (SFTRST)
    RESET_CAUSE_PIN_RESET   = 5,  // Зовнішня кнопка / сигнал NRST
    RESET_CAUSE_HARDFAULT   = 6   // Апаратний виняток HardFault
} reset_cause_t;

// Структура збереженого контексту аварії
typedef struct __attribute__((packed)) {
    uint32_t magic;                 // CRASH_DUMP_MAGIC
    uint32_t rcc_csr;               // Сирий стан регістру RCC_CSR
    uint32_t reset_cause;           // Розкодована причина reset_cause_t
    uint32_t uptime_ms;             // Час роботи до збою (SysTick)
    
    // Регістри ядра, збережені апаратурою на стек
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;                    // Адреса повернення (хто викликав)
    uint32_t pc;                    // Адреса інструкції, де стався крах
    uint32_t xpsr;
    
    // Регістри діагностики SCB
    uint32_t cfsr;                  // UFSR + BFSR + MMFSR
    uint32_t hfsr;                  // HardFault Status
    uint32_t bfar;                  // Bus Fault Address
    uint32_t mmfar;                 // MemManage Fault Address
    uint32_t exc_return;            // Значення LR при вході у Fault Handler
    
    // Знімок верхівки стека
    uint32_t stack_dump[CRASH_STACK_WORDS];
    
    // Інформація про Assert (якщо збій програмний)
    char assert_file[32];
    uint32_t assert_line;
    
    uint32_t crc32;                 // Контрольна сума структури
} crash_dump_t;

void crash_dump_early_init(void);
bool crash_dump_has_valid_record(void);
const crash_dump_t* crash_dump_get(void);
void crash_dump_clear(void);
void crash_dump_software_assert(const char* file, uint32_t line);

#endif // CRASH_DUMP_H
