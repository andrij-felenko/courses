#ifndef BUS_DIAGNOSTICS_H
#define BUS_DIAGNOSTICS_H

#include <stdint.h>
#include <stdbool.h>

#define DIAGNOSTIC_LOG_CAPACITY 32

typedef enum {
    EVENT_NONE = 0,
    EVENT_TIMEOUT_TXE,
    EVENT_TIMEOUT_RXNE,
    EVENT_BUS_LOCKUP_9PULSES,
    EVENT_TIER1_SOFT_RESET,
    EVENT_TIER2_PIN_RESET,
    EVENT_TIER3_POWER_CYCLE,
    EVENT_CALIBRATION_CRC_ERROR,
    EVENT_RECOVERY_SUCCESS
} bus_event_type_t;

typedef struct {
    uint32_t timestamp_cycles;
    bus_event_type_t event_type;
    uint8_t peripheral_id;
    int8_t status_code;
    uint8_t aux_data;
} bus_log_entry_t;

typedef struct {
    bus_log_entry_t entries[DIAGNOSTIC_LOG_CAPACITY];
    uint16_t head;
    uint16_t count;
    uint32_t total_events_recorded;
} bus_diagnostics_log_t;

void diagnostics_log_init(bus_diagnostics_log_t *log) {
    log->head = 0;
    log->count = 0;
    log->total_events_recorded = 0;
}

void diagnostics_log_record(bus_diagnostics_log_t *log, bus_event_type_t event, uint8_t periph_id, int8_t status, uint8_t aux) {
    bus_log_entry_t *entry = &log->entries[log->head];
    entry->timestamp_cycles = DWT->CYCCNT;
    entry->event_type = event;
    entry->peripheral_id = periph_id;
    entry->status_code = status;
    entry->aux_data = aux;

    log->head = (log->head + 1) % DIAGNOSTIC_LOG_CAPACITY;
    if (log->count < DIAGNOSTIC_LOG_CAPACITY) {
        log->count++;
    }
    log->total_events_recorded++;
}

#endif // BUS_DIAGNOSTICS_H
