#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FLIGHT_LOG_CAPACITY 64
#define NOINIT_MAGIC 0xDEADBEEF

typedef enum {
    EVT_SYSTEM_BOOT        = 0x01,
    EVT_BROWNOUT_DETECTED  = 0x02,
    EVT_BUS_SETUP_VIOLATION= 0x03,
    EVT_BUS_CRC_ERROR      = 0x04,
    EVT_FRAMING_ERROR      = 0x05,
    EVT_STRESS_BURST_START = 0x06
} event_type_t;

typedef struct {
    uint32_t timestamp_us;
    uint8_t  event_type;
    uint8_t  bus_status;
    uint16_t aux_data;
} __attribute__((packed)) log_entry_t;

typedef struct {
    uint32_t magic;
    uint32_t boot_counter;
    uint32_t write_idx;
    uint32_t total_errors;
    log_entry_t entries[FLIGHT_LOG_CAPACITY];
} noinit_flight_recorder_t;

/* Розміщення у спеціальній секції RAM, яка не затирається під час RESET */
__attribute__((section(".noinit"))) 
static noinit_flight_recorder_t g_recorder;

/* Псевдо-таймер для міток часу (наприклад, DWT->CYCCNT або SysTick) */
static inline uint32_t get_system_micros(void) {
    extern volatile uint32_t g_system_tick_us;
    return g_system_tick_us;
}

/* Швидкий неінвазивний запис події (виконується за ~10-15 тактів) */
void flight_recorder_log(event_type_t evt, uint8_t status, uint16_t aux) {
    uint32_t idx = g_recorder.write_idx % FLIGHT_LOG_CAPACITY;
    
    g_recorder.entries[idx].timestamp_us = get_system_micros();
    g_recorder.entries[idx].event_type   = (uint8_t)evt;
    g_recorder.entries[idx].bus_status   = status;
    g_recorder.entries[idx].aux_data     = aux;
    
    g_recorder.write_idx++;
    if (evt == EVT_BUS_CRC_ERROR || evt == EVT_FRAMING_ERROR || evt == EVT_BUS_SETUP_VIOLATION) {
        g_recorder.total_errors++;
    }
}

void flight_recorder_init(uint32_t reset_flags) {
    if (g_recorder.magic != NOINIT_MAGIC) {
        /* Холодний старт (Power-On) — ініціалізація з нуля */
        g_recorder.magic = NOINIT_MAGIC;
        g_recorder.boot_counter = 1;
        g_recorder.write_idx = 0;
        g_recorder.total_errors = 0;
        memset(g_recorder.entries, 0, sizeof(g_recorder.entries));
    } else {
        /* Гарячий рестарт після збою або Brownout */
        g_recorder.boot_counter++;
    }

    flight_recorder_log(EVT_SYSTEM_BOOT, (uint8_t)reset_flags, (uint16_t)g_recorder.boot_counter);
}

/* Модуль штучного провокування граничних таймінгів (Stress Stimulator) */
typedef struct {
    uint32_t jitter_seed;
    bool     inject_delays;
    bool     force_power_burst;
} stress_config_t;

static stress_config_t g_stress = { .jitter_seed = 0x12345678, .inject_delays = true, .force_power_burst = false };

/* Псевдовипадковий генератор (Xorshift32) для наносекундного джиттеру */
static inline uint32_t fast_rand(void) {
    g_stress.jitter_seed ^= g_stress.jitter_seed << 13;
    g_stress.jitter_seed ^= g_stress.jitter_seed >> 17;
    g_stress.jitter_seed ^= g_stress.jitter_seed << 5;
    return g_stress.jitter_seed;
}

/* Виконання транзакції шини з активною варіацією часових інтервалів */
bool marginal_bus_transfer(uint8_t *tx_buf, uint8_t *rx_buf, uint16_t len) {
    if (g_stress.inject_delays) {
        /* Вносимо джиттер затримки між лініями CS і CLK (від 0 до 31 циклу NOP) */
        uint32_t delay_cycles = fast_rand() & 0x1F;
        for (volatile uint32_t i = 0; i < delay_cycles; i++) {
            __asm__ __volatile__("nop");
        }
    }

    /* Імітація апаратного опитування з перевіркою апаратних помилок шини */
    extern bool hardware_spi_transfer_raw(uint8_t *tx, uint8_t *rx, uint16_t l);
    extern uint8_t hardware_spi_get_status_flags(void);
    
    bool ok = hardware_spi_transfer_raw(tx_buf, rx_buf, len);
    uint8_t status = hardware_spi_get_status_flags();

    if (!ok || (status & 0x08)) { /* 0x08 — прапорець порушення таймінгу/CRC */
        flight_recorder_log(EVT_BUS_SETUP_VIOLATION, status, len);
        return false;
    }

    return true;
}
