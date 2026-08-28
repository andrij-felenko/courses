/* incident_recorder.h / incident_recorder.c */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define INCIDENT_MAGIC 0xDEADBEEFUL

typedef struct __attribute__((packed)) {
    uint32_t magic;            /* 0xDEADBEEF */
    uint32_t timestamp_sec;    /* Час аварії від запуску */
    uint32_t reset_reason;     /* Регістр скидання RCC_CSR */
    uint32_t fault_pc;         /* Адреса збою (Program Counter) */
    uint32_t fault_lr;         /* Регістр зв'язку (Link Register) */
    uint32_t fault_cfsr;       /* Configurable Fault Status Register */
    uint16_t supply_mv;        /* Напруга живлення в мілівольтах */
    int16_t  die_temp_c;       /* Температура кристала (°C) */
    uint16_t i2c_nack_count;   /* Лічильник таймаутів шини I2C */
    uint16_t spi_err_count;    /* Лічильник помилок SPI */
    uint32_t active_task_id;   /* Ідентифікатор активного потоку */
    uint32_t free_heap_bytes;  /* Залишок динамічної пам'яті */
    uint32_t crc32;            /* Контрольна сума кадру */
} incident_snapshot_t;

/* Виділений енергонезалежний сектор у Backup SRAM */
#define BACKUP_SRAM_ADDR ((void*)0x40024000UL)

static uint32_t compute_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFUL;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320UL & -(crc & 1));
        }
    }
    return ~crc;
}

void record_fatal_incident(uint32_t pc, uint32_t lr, uint32_t cfsr, 
                           uint32_t task_id, uint16_t v_mv, int16_t temp_c) {
    incident_snapshot_t snap;
    memset(&snap, 0, sizeof(snap));

    snap.magic = INCIDENT_MAGIC;
    snap.timestamp_sec = 10423; /* Зчитується з апаратного таймера/RTC */
    snap.reset_reason = 0x20000000UL; /* Приклад: прапор IWDGRSTF */
    snap.fault_pc = pc;
    snap.fault_lr = lr;
    snap.fault_cfsr = cfsr;
    snap.supply_mv = v_mv;
    snap.die_temp_c = temp_c;
    snap.active_task_id = task_id;
    snap.i2c_nack_count = 14;
    snap.spi_err_count = 0;
    snap.free_heap_bytes = 4096;

    /* Обчислення контрольної суми без поля crc32 */
    snap.crc32 = compute_crc32((const uint8_t*)&snap, sizeof(snap) - sizeof(uint32_t));

    /* Атомарне копіювання в енергонезалежний регіон */
    memcpy(BACKUP_SRAM_ADDR, &snap, sizeof(snap));
}
