/* flight_recorder.c - C99 логіка роботи з енергонезалежним буфером */
#include "flight_recorder.h"
#include <string.h>

/* Імітація виділеної енергонезалежної пам'яті FRAM або збереженого SRAM-домену */
static crash_dump_t g_nvm_crash_dump __attribute__((section(".noinit")));
static uint32_t g_pvd_counter = 0;
static uint32_t g_bus_errors = 0;

/* Таблиця або прямий розрахунок IEEE 802.3 CRC32 */
uint32_t flight_recorder_calc_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        crc ^= (uint32_t)data[i];
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 1U) {
                crc = (crc >> 1U) ^ 0xEDB88320U;
            } else {
                crc = (crc >> 1U);
            }
        }
    }
    return ~crc;
}

void flight_recorder_init(uint32_t raw_rcc_csr, uint32_t total_boots) {
    uint8_t flags = RESET_CAUSE_UNKNOWN;

    /* Декодування апаратних бітів скидання (приклад для Cortex-M/STM32) */
    if (raw_rcc_csr & (1U << 31)) flags |= RESET_CAUSE_LOW_POWER;
    if (raw_rcc_csr & (1U << 29)) flags |= RESET_CAUSE_IWDG;
    if (raw_rcc_csr & (1U << 28)) flags |= RESET_CAUSE_WWDG;
    if (raw_rcc_csr & (1U << 27)) flags |= RESET_CAUSE_SOFT;
    if (raw_rcc_csr & (1U << 26)) flags |= RESET_CAUSE_PIN;
    if (raw_rcc_csr & (1U << 25)) flags |= RESET_CAUSE_BOR;
    if (raw_rcc_csr & (1U << 24)) flags |= RESET_CAUSE_POR_PDR;

    /* Оновлення лічильників поточного сеансу */
    g_nvm_crash_dump.boot_count = total_boots;
    g_nvm_crash_dump.last_reset_flags = flags;
}

void flight_recorder_log_pvd_event(uint16_t current_mv, int16_t current_temp) {
    g_pvd_counter++;
    g_nvm_crash_dump.supply_mv = current_mv;
    g_nvm_crash_dump.die_temp_c_x10 = current_temp;
    g_nvm_crash_dump.brownout_count = g_pvd_counter;
}

void flight_recorder_record_hardfault(uint32_t cfsr, uint32_t hfsr, uint32_t bfar,
                                     uint32_t lr, uint32_t pc, uint16_t vdd_mv, int16_t temp) {
    g_nvm_crash_dump.magic = CRASH_DUMP_MAGIC;
    g_nvm_crash_dump.version = CRASH_DUMP_VERSION;
    g_nvm_crash_dump.cfsr = cfsr;
    g_nvm_crash_dump.hfsr = hfsr;
    g_nvm_crash_dump.bfar = bfar;
    g_nvm_crash_dump.lr = lr;
    g_nvm_crash_dump.pc = pc;
    g_nvm_crash_dump.supply_mv = vdd_mv;
    g_nvm_crash_dump.die_temp_c_x10 = temp;
    g_nvm_crash_dump.brownout_count = g_pvd_counter;
    g_nvm_crash_dump.bus_error_count = g_bus_errors;

    /* Розрахунок CRC по всіх полях крім самого crc32 */
    const size_t payload_len = offsetof(crash_dump_t, crc32);
    g_nvm_crash_dump.crc32 = flight_recorder_calc_crc32((const uint8_t *)&g_nvm_crash_dump, payload_len);
}

bool flight_recorder_read_dump(crash_dump_t *out_dump) {
    if (!out_dump) return false;

    if (g_nvm_crash_dump.magic != CRASH_DUMP_MAGIC) return false;
    if (g_nvm_crash_dump.version != CRASH_DUMP_VERSION) return false;

    const size_t payload_len = offsetof(crash_dump_t, crc32);
    uint32_t expected_crc = flight_recorder_calc_crc32((const uint8_t *)&g_nvm_crash_dump, payload_len);

    if (g_nvm_crash_dump.crc32 != expected_crc) return false;

    memcpy(out_dump, &g_nvm_crash_dump, sizeof(crash_dump_t));
    return true;
}

void flight_recorder_clear(void) {
    memset(&g_nvm_crash_dump, 0, sizeof(crash_dump_t));
}
