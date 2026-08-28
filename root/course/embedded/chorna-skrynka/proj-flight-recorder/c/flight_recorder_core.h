/* flight_recorder_core.h - Двійковий інтерфейс реєстратора (C) */
#ifndef FLIGHT_RECORDER_CORE_H
#define FLIGHT_RECORDER_CORE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define BLACKBOX_MAGIC_HEADER   0x424F5831U /* 'BOX1' */
#define BLACKBOX_BUFFER_SIZE    256U        /* 256 подій * 16 байтів = 4096 байтів */
#define BLACKBOX_BUFFER_MASK    (BLACKBOX_BUFFER_SIZE - 1U)

typedef enum {
    SUBSYS_CORE     = 0x00,
    SUBSYS_POWER    = 0x01,
    SUBSYS_NAV      = 0x02,
    SUBSYS_ACTUATOR = 0x03,
    SUBSYS_COMM     = 0x04
} BlackBoxSubsystem_t;

typedef enum {
    EVT_NONE           = 0x00,
    EVT_BOOT_OK        = 0x01,
    EVT_FSM_TRANSITION = 0x02,
    EVT_BUS_NACK       = 0x03,
    EVT_BUS_TIMEOUT    = 0x04,
    EVT_VOLTAGE_WARN   = 0x05,
    EVT_TEMP_CRITICAL  = 0x06,
    EVT_HARDFAULT      = 0xFE,
    EVT_PANIC_ABORT    = 0xFF
} BlackBoxEventCode_t;

/* 16-байтний двійковий кадр події */
typedef struct __attribute__((packed, aligned(4))) {
    uint32_t timestamp_ms;
    uint8_t  subsystem;
    uint8_t  event_code;
    uint16_t fsm_state;
    uint8_t  payload[6];
    uint16_t crc16;
} BlackBoxFrame_t;

/* Заголовок та пам'ять тому реєстратора */
typedef struct __attribute__((packed, aligned(4))) {
    uint32_t magic;
    uint32_t boot_counter;
    uint32_t crash_counter;
    volatile uint32_t head_index;
    volatile uint32_t is_frozen;
    BlackBoxFrame_t frames[BLACKBOX_BUFFER_SIZE];
    uint16_t header_crc;
} BlackBoxStorage_t;

/* Функції керування та логування */
void blackbox_init(void);
void blackbox_record(BlackBoxSubsystem_t subsys, BlackBoxEventCode_t code, uint16_t fsm, const void* data, uint8_t len);
void blackbox_emergency_panic(uint8_t reason, uint32_t pc, uint32_t fault_addr);
bool blackbox_is_crash_dump_present(void);
const BlackBoxStorage_t* blackbox_get_storage_ptr(void);

#ifdef __cplusplus
}
#endif

#endif /* FLIGHT_RECORDER_CORE_H */
