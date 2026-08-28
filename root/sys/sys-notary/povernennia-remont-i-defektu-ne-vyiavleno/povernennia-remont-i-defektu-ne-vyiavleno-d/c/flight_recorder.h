/* flight_recorder.h - C99 реалізація реєстратора зліпків стану та NFF-діагностики */
#ifndef FLIGHT_RECORDER_H
#define FLIGHT_RECORDER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define CRASH_DUMP_MAGIC      0x444E4646U /* Магічне число "NFFD" */
#define CRASH_DUMP_VERSION    1U
#define FLIGHT_LOG_MAX_EVENTS 16U

/* Прапорці причин апаратного перезапуску */
typedef enum {
    RESET_CAUSE_UNKNOWN      = 0x00,
    RESET_CAUSE_POR_PDR      = 0x01, /* Вмикання / вимикання живлення */
    RESET_CAUSE_BOR          = 0x02, /* Просідання живлення (Brown-out) */
    RESET_CAUSE_PIN          = 0x04, /* Зовнішній сигнал скидання (NRST) */
    RESET_CAUSE_IWDG         = 0x08, /* Незалежний сторожовий таймер */
    RESET_CAUSE_WWDG         = 0x10, /* Віконний сторожовий таймер */
    RESET_CAUSE_SOFT         = 0x20, /* Програмне скидання ядра (NVIC_SystemReset) */
    RESET_CAUSE_LOW_POWER    = 0x40  /* Скидання при виході з глибокого сну */
} reset_cause_flags_t;

/* Структура зліпка аварійного стану (Crash Dump) */
typedef struct {
    uint32_t magic;               /* Магічне число валідації */
    uint32_t version;             /* Версія формату структури */
    uint64_t uptime_ms;           /* Час безперервної роботи від старту, мс */
    uint32_t boot_count;          /* Загальна кількість запусків пристрою */
    uint8_t  last_reset_flags;    /* Апаратні прапорці причини скидання */
    uint8_t  reserved[3];         /* Вирівнювання структури до 32-біт */
    
    /* Зріз апаратних регістрів винятків ARM Cortex-M */
    uint32_t cfsr;                /* Configurable Fault Status Register */
    uint32_t hfsr;                /* HardFault Status Register */
    uint32_t bfar;                /* BusFault Address Register */
    uint32_t lr;                  /* Link Register (повернення з винятку) */
    uint32_t pc;                  /* Program Counter (точка краху) */

    /* Телеметрія фізичного середовища на момент збою */
    uint16_t supply_mv;           /* Напруга живлення Vdd, мілівольти */
    int16_t  die_temp_c_x10;      /* Температура кристала (°C * 10) */
    uint32_t brownout_count;      /* Кількість зафіксованих подій PVD */
    uint32_t bus_error_count;     /* Лічильник інтермітуючих збоїв шин */

    uint32_t crc32;               /* Контрольна сума цілісності запису */
} __attribute__((packed)) crash_dump_t;

/* Публічний інтерфейс реєстратора */
void flight_recorder_init(uint32_t raw_rcc_csr, uint32_t total_boots);
void flight_recorder_log_pvd_event(uint16_t current_mv, int16_t current_temp);
void flight_recorder_record_hardfault(uint32_t cfsr, uint32_t hfsr, uint32_t bfar,
                                     uint32_t lr, uint32_t pc, uint16_t vdd_mv, int16_temp);
bool flight_recorder_read_dump(crash_dump_t *out_dump);
void flight_recorder_clear(void);
uint32_t flight_recorder_calc_crc32(const uint8_t *data, size_t length);

#endif /* FLIGHT_RECORDER_H */
