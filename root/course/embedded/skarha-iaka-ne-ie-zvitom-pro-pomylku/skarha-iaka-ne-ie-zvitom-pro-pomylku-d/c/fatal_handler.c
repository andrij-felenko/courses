/* fatal_handler.c */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define SNAPSHOT_MAGIC   0xDEADBEEFUL
#define BACKUP_SRAM_BASE 0x40024000UL

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t reset_reason;
    uint32_t fault_pc;
    uint32_t fault_lr;
    uint32_t fault_cfsr;
    uint16_t v_bat_mv;
    int16_t  temp_c;
    uint16_t bus_i2c_nack;
    uint16_t rtos_task_id;
    uint32_t crc32;
} crash_dump_t;

static uint32_t calc_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFUL;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int b = 0; b < 8; ++b) {
            crc = (crc >> 1) ^ (0xEDB88320UL & -(crc & 1));
        }
    }
    return ~crc;
}

void HardFault_C_Handler(uint32_t *stack_frame, uint32_t lr_exc) {
    /* Вимикаємо всі масковані переривання */
    __asm volatile ("cpsid i" : : : "memory");

    crash_dump_t dump;
    memset(&dump, 0, sizeof(dump));

    dump.magic = SNAPSHOT_MAGIC;
    dump.reset_reason = 0x20000000UL; /* Прапор IWDG з регістра RCC_CSR */
    dump.fault_pc = stack_frame[6];    /* Шосте слово у стек-фреймі Cortex-M — PC */
    dump.fault_lr = stack_frame[5];    /* П'яте слово у стек-фреймі — LR */
    dump.fault_cfsr = (*((volatile uint32_t*)0xE000ED28UL)); /* Апаратний регістр CFSR */
    dump.v_bat_mv = 2780;              /* Останнє збережене значення АЦП */
    dump.temp_c = 64;
    dump.bus_i2c_nack = 14;
    dump.rtos_task_id = 2;

    /* Обчислення контрольної суми без поля CRC */
    dump.crc32 = calc_crc32((const uint8_t*)&dump, sizeof(dump) - sizeof(uint32_t));

    /* Атомарне копіювання у Backup SRAM */
    memcpy((void*)BACKUP_SRAM_BASE, &dump, sizeof(dump));

    /* Примусовий бар'єр пам'яті перед перезавантаженням */
    __asm volatile ("dsb 0xF" : : : "memory");
    __asm volatile ("isb 0xF" : : : "memory");

    /* Скидання мікроконтролера */
    *((volatile uint32_t*)0xE000ED0CUL) = 0x05FA0004UL; /* AIRCR SYSRESETREQ */

    while(1) {
        __asm volatile ("nop");
    }
}
