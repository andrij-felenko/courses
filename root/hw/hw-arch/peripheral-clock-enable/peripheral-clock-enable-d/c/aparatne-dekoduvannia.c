#include <stdint.h>
#include <stdbool.h>

// Структура збереженого апаратного стекового кадру Cortex-M
typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t xpsr;
} exception_stack_frame_t;

// Діагностичний обробник шинних помилок
void bus_fault_analyzer_c(const exception_stack_frame_t *frame) {
    volatile uint32_t cfsr = *(volatile uint32_t*)0xE000ED28; // SCB->CFSR
    volatile uint8_t  bfsr = (uint8_t)((cfsr >> 8) & 0xFF);   // Байт BFSR
    volatile uint32_t bfar = *(volatile uint32_t*)0xE000ED38; // SCB->BFAR

    // Перевірка прапорця валідності адреси BFARVALID (біт 7 у BFSR)
    bool has_valid_address = (bfsr & (1U << 7)) != 0;
    uint32_t fault_address = has_valid_address ? bfar : 0x00000000;

    // Перевірка точного збою PRECISERR (біт 1 у BFSR)
    bool is_precise = (bfsr & (1U << 1)) != 0;

    // Якщо адреса потрапляє в діапазон периферії (0x40000000 - 0x5FFFFFFF)
    if (has_valid_address && (fault_address >= 0x40000000 && fault_address < 0x60000000)) {
        // Збій викликано доступом до знеструмленого за тактом модуля!
        // fault_address містить точну адресу регістра, PC містить адресу інструкції
        (void)is_precise;
    }

    // Зависання для аналізу в налагоджувачі
    while (1) {
        __asm volatile("BKPT #0");
    }
}
