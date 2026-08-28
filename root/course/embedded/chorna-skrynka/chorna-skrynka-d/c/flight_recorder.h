/* flight_recorder.h - Модуль бортового реєстратора подій (C) */
#ifndef FLIGHT_RECORDER_H
#define FLIGHT_RECORDER_H

#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BLACKBOX_MAGIC_HEADER   0x424F5831  /* 'BOX1' */
#define BLACKBOX_BUFFER_CAPACITY 256        /* Кількість 16-байтних подій у RAM (4 КБ) */

typedef enum {
    SUBSYS_CORE   = 0x00,
    SUBSYS_POWER  = 0x01,
    SUBSYS_NAV    = 0x02,
    SUBSYS_MOTORS = 0x03,
    SUBSYS_COM    = 0x04
} SubsystemID_t;

typedef enum {
    EVT_NONE         = 0x00,
    EVT_STATE_CHANGE = 0x01,
    EVT_BUS_ERROR    = 0x02,
    EVT_WARN_THRESH  = 0x03,
    EVT_CRASH_PANIC  = 0xFF
} EventID_t;

typedef struct __attribute__((packed, aligned(4))) {
    uint32_t timestamp_ms;
    uint8_t  subsystem_id;
    uint8_t  event_id;
    uint16_t fsm_state;
    uint8_t  payload[6];
    uint16_t crc16;
} FlightEvent_t;

typedef struct __attribute__((packed, aligned(4))) {
    uint32_t magic;
    uint32_t boot_count;
    uint32_t crash_count;
    volatile uint32_t head_index;
    volatile uint32_t is_frozen;
    FlightEvent_t events[BLACKBOX_BUFFER_CAPACITY];
    uint16_t header_crc;
} BlackBoxRamStorage_t;

/* Публічний інтерфейс реєстратора */
void flight_recorder_init(void);
void flight_recorder_log(SubsystemID_t subsys, EventID_t evt, uint16_t fsm, const void* payload, uint8_t len);
void flight_recorder_panic(uint8_t reason_code, uint32_t fault_addr, uint32_t pc);
bool flight_recorder_has_valid_dump(void);
const BlackBoxRamStorage_t* flight_recorder_get_storage(void);

#endif /* FLIGHT_RECORDER_H */
