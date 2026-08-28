#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define WARRANTY_MAGIC 0x52524157U /* "WARR" у little-endian */
#define WARRANTY_SCHEMA_V2 0x0002U
#define MAX_VIOLATION_RECORDS 16U

/* Бітові маски порушень умов експлуатації */
#define VIOLATION_NONE            0x00000000U
#define VIOLATION_LIQUID_INGRESS  (1U << 0) /* Спрацював LCI або вологомір */
#define VIOLATION_OVERVOLTAGE_EOS (1U << 1) /* Перенапруга > Absolute Max */
#define VIOLATION_OVERHEAT        (1U << 2) /* Температура T > T_j_max */
#define VIOLATION_MECHANICAL_SHOCK (1U << 3)/* Ударне навантаження > 50g */
#define VIOLATION_TAMPER_OPEN     (1U << 4) /* Розкриття корпусу (mesh/switch) */
#define VIOLATION_FW_UNAUTHORIZED (1U << 5) /* Непідписана прошивка */
#define VIOLATION_REV_POLARITY    (1U << 6) /* Зворотна полярність живлення */

/* Статуси гарантійного висновку RMA */
typedef enum {
    RMA_STATUS_APPROVED_WARRANTY = 0,
    RMA_STATUS_REJECTED_EXPIRED,
    RMA_STATUS_REJECTED_LIQUID,
    RMA_STATUS_REJECTED_ELECTRICAL_ABUSE,
    RMA_STATUS_REJECTED_THERMAL_ABUSE,
    RMA_STATUS_REJECTED_TAMPER_MODIFIED,
    RMA_STATUS_REJECTED_INTEGRITY_CORRUPT
} rma_verdict_t;

#pragma pack(push, 1)

/* Структура одиничного запису про подію порушення */
typedef struct {
    uint32_t timestamp_poh;    /* Мотогодина виникнення аварії */
    uint16_t event_type;       /* Тип сенсорної події */
    int16_t  peak_temperature; /* Температура в десятих долях °C */
    uint32_t peak_voltage_mv;  /* Напруга в мілівольтах */
    uint16_t peak_shock_deci_g;/* Прискорення в десятих долях g */
    uint8_t  sensor_flags;     /* Прапорці конкретного датчика */
    uint8_t  reserved;
    uint32_t record_crc32;     /* Контрольна сума запису */
} violation_record_t;

/* Заголовок захищеного журналу EEPROM */
typedef struct {
    uint32_t magic;
    uint16_t schema_version;
    uint16_t header_len;
    uint8_t  device_uuid[16];
    uint32_t power_on_hours;       /* Загальний напрацьований час */
    uint32_t boot_count;           /* Кількість увімкнень приладу */
    uint32_t thermal_cycles;       /* Лічильник термічних циклів */
    uint32_t violation_flags;      /* Кумулятивна маска порушень */
    int16_t  max_recorded_temp;    /* Абсолютний пік температури (°C * 10) */
    uint32_t max_recorded_voltage; /* Абсолютний пік напруги (мВ) */
    uint16_t max_recorded_shock;   /* Абсолютний пік удару (g * 10) */
    uint16_t record_count;         /* Кількість записів у буфері */
    uint32_t header_crc32;         /* Контрольна сума заголовка */
} warranty_log_header_t;

/* Повний образ сховища журналу */
typedef struct {
    warranty_log_header_t header;
    violation_record_t records[MAX_VIOLATION_RECORDS];
} warranty_storage_t;

#pragma pack(pop)

/* Обчислення стандартизованого CRC32 (IEEE 802.3) */
static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        crc ^= (uint32_t)data[i];
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 1U) {
                crc = (crc >> 1) ^ 0xEDB88320U;
            } else {
                crc = (crc >> 1);
            }
        }
    }
    return crc ^ 0xFFFFFFFFU;
}

/* Перевірка цілісності та діагностика гарантійного стану */
rma_verdict_t evaluate_warranty_status(
    const warranty_storage_t *storage,
    uint32_t max_allowed_poh,
    int16_t limit_temp_deci_c,
    uint32_t limit_voltage_mv
) {
    if (storage == NULL) {
        return RMA_STATUS_REJECTED_INTEGRITY_CORRUPT;
    }

    /* 1. Перевірка магічного числа та версії схеми */
    if (storage->header.magic != WARRANTY_MAGIC ||
        storage->header.schema_version != WARRANTY_SCHEMA_V2) {
        return RMA_STATUS_REJECTED_INTEGRITY_CORRUPT;
    }

    /* 2. Перевірка цілісності заголовка */
    const size_t crc_calc_len = sizeof(warranty_log_header_t) - sizeof(uint32_t);
    const uint32_t expected_crc = calculate_crc32((const uint8_t *)&storage->header, crc_calc_len);
    if (storage->header.header_crc32 != expected_crc) {
        return RMA_STATUS_REJECTED_INTEGRITY_CORRUPT;
    }

    /* 3. Перевірка ліміту напрацювання (мотогодин) */
    if (storage->header.power_on_hours > max_allowed_poh) {
        return RMA_STATUS_REJECTED_EXPIRED;
    }

    /* 4. Аналіз бітових прапорців порушень */
    const uint32_t flags = storage->header.violation_flags;

    if (flags & VIOLATION_LIQUID_INGRESS) {
        return RMA_STATUS_REJECTED_LIQUID;
    }

    if ((flags & VIOLATION_TAMPER_OPEN) || (flags & VIOLATION_FW_UNAUTHORIZED)) {
        return RMA_STATUS_REJECTED_TAMPER_MODIFIED;
    }

    if ((flags & VIOLATION_OVERVOLTAGE_EOS) || (flags & VIOLATION_REV_POLARITY) ||
        (storage->header.max_recorded_voltage > limit_voltage_mv)) {
        return RMA_STATUS_REJECTED_ELECTRICAL_ABUSE;
    }

    if ((flags & VIOLATION_OVERHEAT) ||
        (storage->header.max_recorded_temp > limit_temp_deci_c)) {
        return RMA_STATUS_REJECTED_THERMAL_ABUSE;
    }

    /* Якщо всі перевірки пройдено — претензія підлягає гарантійному обслуговуванню */
    return RMA_STATUS_APPROVED_WARRANTY;
}
