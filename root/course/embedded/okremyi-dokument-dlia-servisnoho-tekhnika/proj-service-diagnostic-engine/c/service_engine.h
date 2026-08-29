/* service_engine.h — публічний інтерфейс сервісного діагностичного рушія. */
#ifndef SERVICE_ENGINE_H
#define SERVICE_ENGINE_H

#include <stdbool.h>
#include <stdint.h>

#define CLI_BUFFER_SIZE 128 /* довжина рядка команди разом із термінатором */
#define SRV_CAL_SLOTS   4   /* калібрувальні зсуви каналів ADC 0..3, мВ */

typedef enum {
    SRV_STATE_LOCKED = 0,
    SRV_STATE_CHALLENGE_ISSUED,
    SRV_STATE_UNLOCKED,
    SRV_STATE_ACTUATION_ACTIVE,
    SRV_STATE_EMERGENCY
} srv_state_t;

/* Коди, які технік бачить у рядку «-ERR: 0xXXXX ...» */
typedef enum {
    SRV_ERR_LOCKED         = 0x4000,
    SRV_ERR_ACCESS_DENIED  = 0x4001,
    SRV_ERR_BAD_CHANNEL    = 0x4002,
    SRV_ERR_BAD_TIMEOUT    = 0x4003,
    SRV_ERR_AUTH_FAILED    = 0x4004,
    SRV_ERR_BAD_ARGUMENTS  = 0x4005,
    SRV_ERR_UNKNOWN_CMD    = 0x4006,
    SRV_ERR_ACT_ACTIVE     = 0x4007,
    SRV_ERR_LINE_TOO_LONG  = 0x4008,
    SRV_ERR_HW_FAULT       = 0x4009,
    SRV_ERR_EEPROM_WRITE   = 0x400A,
    SRV_ERR_BUS_BUSY       = 0x400B,
    SRV_ERR_INPUT_OVERRUN  = 0x400C
} srv_err_t;

/* Викликати ПІСЛЯ ініціалізації BSP: гасить реле й читає калібрування. */
void srv_init(void);

/* Контекст ISR приймача UART: лише накопичує байт у буфері. */
void srv_feed_byte(char c);

/* Контекст суперциклу або сервісної задачі: розбір рядка й усі таймери. */
void srv_poll_step(void);

/* Безумовне знеструмлення силових виходів. */
void srv_emergency_all_off(void);

/* Контекст ISR апаратного захисту: аварійна зупинка з фіксацією причини. */
void srv_fault_trip(uint32_t flags);

srv_state_t srv_get_state(void);
int32_t     srv_get_cal(uint8_t slot);

#endif /* SERVICE_ENGINE_H */
