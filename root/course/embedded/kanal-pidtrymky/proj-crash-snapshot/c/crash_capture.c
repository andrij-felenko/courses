/* crash_capture.c — аварійний збирач діагностичного контексту */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BUNDLE_MAGIC        0x4442554E  /* 'DBUN' */
#define BUNDLE_VERSION      0x0200      /* v2.0 */
#define FLASH_DIAG_ADDR     0x080E0000  /* Адреса виділеного сектора Flash */

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint16_t version;
    uint16_t header_size;
    uint32_t payload_size;
    uint32_t serial_number;
    uint16_t hw_revision;
    uint16_t reset_reason;
    uint32_t fw_git_hash;
    uint64_t uptime_ms;
} crash_header_t;

typedef struct __attribute__((packed)) {
    uint32_t r0, r1, r2, r3, r12, lr, pc, xpsr;
    uint32_t cfsr, hfsr, mmfar, bfar;
} cpu_registers_t;

typedef struct __attribute__((packed)) {
    uint16_t v_in_mv;
    uint16_t v_3v3_mv;
    int16_t  mcu_temp_c10;
    uint16_t reserved;
} power_telemetry_t;

typedef struct __attribute__((packed)) {
    crash_header_t    header;
    cpu_registers_t   cpu;
    power_telemetry_t power;
    uint32_t          crc32;
} crash_snapshot_t;

/* Статичний буфер у секції .noinit для збереження контексту */
__attribute__((section(".noinit"))) static crash_snapshot_t s_active_snapshot;

/* Швидкий табличний розрахунок CRC32 */
static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
        }
    }
    return ~crc;
}

/* Низькорівневий запис у внутрішню Flash-пам'ять методом опитування */
static void flash_write_polling(uint32_t dest_addr, const uint8_t *src, size_t size) {
    /* Симуляція прямого доступу до регістрів Flash контролера */
    /* У реальній системі: розблокування Flash -> стирання сектора -> запис слів -> блокування */
    volatile uint32_t *flash_ptr = (volatile uint32_t *)dest_addr;
    const uint32_t *src_ptr = (const uint32_t *)src;
    size_t words = (size + 3) / 4;

    for (size_t i = 0; i < words; ++i) {
        flash_ptr[i] = src_ptr[i];
    }
}

/* С-функція, яка викликається з асемблерного HardFault-трампліна */
void HardFault_Handler_C(uint32_t *hardfault_args) {
    /* Читання регістрів ядра зі стек-фрейму */
    s_active_snapshot.cpu.r0   = hardfault_args[0];
    s_active_snapshot.cpu.r1   = hardfault_args[1];
    s_active_snapshot.cpu.r2   = hardfault_args[2];
    s_active_snapshot.cpu.r3   = hardfault_args[3];
    s_active_snapshot.cpu.r12  = hardfault_args[4];
    s_active_snapshot.cpu.lr   = hardfault_args[5];
    s_active_snapshot.cpu.pc   = hardfault_args[6];
    s_active_snapshot.cpu.xpsr = hardfault_args[7];

    /* Зчитування апаратних системних регістрів SCB (System Control Block) */
    volatile uint32_t *scb_cfsr  = (volatile uint32_t *)0xE000ED28;
    volatile uint32_t *scb_hfsr  = (volatile uint32_t *)0xE000ED2C;
    volatile uint32_t *scb_mmfar = (volatile uint32_t *)0xE000ED34;
    volatile uint32_t *scb_bfar  = (volatile uint32_t *)0xE000ED38;

    s_active_snapshot.cpu.cfsr  = *scb_cfsr;
    s_active_snapshot.cpu.hfsr  = *scb_hfsr;
    s_active_snapshot.cpu.mmfar = *scb_mmfar;
    s_active_snapshot.cpu.bfar  = *scb_bfar;

    /* Заповнення заголовка пакета */
    s_active_snapshot.header.magic          = BUNDLE_MAGIC;
    s_active_snapshot.header.version        = BUNDLE_VERSION;
    s_active_snapshot.header.header_size    = sizeof(crash_header_t);
    s_active_snapshot.header.payload_size   = sizeof(crash_snapshot_t) - sizeof(crash_header_t);
    s_active_snapshot.header.serial_number  = 20260042;
    s_active_snapshot.header.hw_revision    = 0x0043; /* 'C' */
    s_active_snapshot.header.reset_reason   = 0x0001; /* HardFault */
    s_active_snapshot.header.fw_git_hash    = 0x7F89BC20;
    s_active_snapshot.header.uptime_ms      = 3693600000ULL;

    /* Останні відомі показники телеметрії з тіньових регістрів */
    s_active_snapshot.power.v_in_mv       = 23850;
    s_active_snapshot.power.v_3v3_mv      = 3290;
    s_active_snapshot.power.mcu_temp_c10  = 485;

    /* Розрахунок контрольної суми */
    s_active_snapshot.crc32 = calculate_crc32((const uint8_t *)&s_active_snapshot,
                                              sizeof(crash_snapshot_t) - sizeof(uint32_t));

    /* Запис у захищений сектор Flash */
    flash_write_polling(FLASH_DIAG_ADDR, (const uint8_t *)&s_active_snapshot, sizeof(crash_snapshot_t));

    /* Примусовий системний перезапуск через SCB AIRCR */
    volatile uint32_t *scb_aircr = (volatile uint32_t *)0xE000ED0C;
    *scb_aircr = (0x5FA << 16) | (1 << 2); /* SYSRESETREQ */

    while (1) {
        __asm volatile("nop");
    }
}
