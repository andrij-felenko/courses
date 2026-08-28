#ifndef AUDIT_LOGGER_API_H
#define AUDIT_LOGGER_API_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define AUDIT_RECORD_SIZE       128U
#define AUDIT_HASH_SIZE         32U   /* SHA-256 */
#define AUDIT_MAGIC_SYNC        0x41554454U /* 'AUDT' у Little-Endian */
#define AUDIT_SECTOR_MAGIC      0x53454354U /* 'SECT' у Little-Endian */
#define AUDIT_MAX_PAYLOAD_SIZE  32U

/* Статуси повернення функцій логера */
typedef enum {
    AUDIT_OK                    =  0,
    AUDIT_ERR_INVALID_PARAM     = -1,
    AUDIT_ERR_FLASH_IO          = -2,
    AUDIT_ERR_CHAIN_CORRUPTED   = -3,
    AUDIT_ERR_BUFFER_FULL       = -4,
    AUDIT_ERR_NOT_INITIALIZED   = -5,
    AUDIT_ERR_UNALIGNED_ADDR    = -6,
    AUDIT_ERR_POWER_LOSS_DETECT = -7
} audit_status_t;

/* Статус виконання зафіксованої команди */
typedef enum {
    AUDIT_EXEC_PENDING          = 0x00, /* Команду прийнято, очікує перевірки */
    AUDIT_EXEC_ACCEPTED         = 0x01, /* Пройшла перевірку прав та інтерлоків */
    AUDIT_EXEC_REJECTED_AUTH    = 0x02, /* Відхилено: недійсний ключ/підпис */
    AUDIT_EXEC_REJECTED_SAFETY  = 0x03, /* Відхилено: блокування безпеки (Interlock) */
    AUDIT_EXEC_SUCCESS          = 0x04, /* Успішно виконано автопілотом */
    AUDIT_EXEC_FAILED           = 0x05, /* Помилка під час виконання приводу */
    AUDIT_EXEC_TIMEOUT          = 0x06  /* Час очікування підтвердження вичерпано */
} audit_exec_status_t;

/* Прапорці атрибутів запису */
typedef enum {
    AUDIT_FLAG_NONE             = 0x00,
    AUDIT_FLAG_EMERGENCY        = 0x01, /* Аварійна дія (Emergency Disarm/RTL) */
    AUDIT_FLAG_SIGNATURE_VALID  = 0x02, /* Наземний підпис Ed25519 перевірено */
    AUDIT_FLAG_RESERVED_BIT2    = 0x04,
    AUDIT_FLAG_SYNC_RTC         = 0x08  /* Час UTC синхронізовано з GNSS PPS */
} audit_flags_t;
