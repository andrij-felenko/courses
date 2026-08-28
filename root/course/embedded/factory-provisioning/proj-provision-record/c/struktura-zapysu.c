#include <stdint.h>
#include <string.h>

// Магічне число: ASCII "PROV" (Provisioning) як 32-бітне значення.
// 'P'=0x50, 'R'=0x52, 'O'=0x4F, 'V'=0x56. Читаємо порядком байтів чипа
// (ESP32 — little-endian), тому в пам'яті лягає 0x50 0x52 0x4F 0x56.
#define PROV_MAGIC    0x564F5250u   // 'V''O''R''P' у little-endian == "PROV" у пам'яті
#define PROV_VERSION  1u            // версія розкладки цієї структури

#define PROV_CAL_COEFFS  6          // скільки калібрувальних коефіцієнтів (приклад)

// Запис провізіонування — рівно те, що лежить у розділі даних.
// packed: без прихованих байтів вирівнювання, щоб байти співпали з хостом.
typedef struct __attribute__((packed)) {
    uint32_t magic;                 // PROV_MAGIC — мітка «це наш дійсний запис»
    uint16_t version;               // PROV_VERSION — за якою схемою складено
    uint8_t  serial[8];             // серійний номер (наш формат, напр. BCD або ASCII)
    uint8_t  mac[6];                // MAC-адреса, зашита на заводі
    float    cal[PROV_CAL_COEFFS];  // калібрувальні поправки саме цього давача
    uint32_t crc32;                 // CRC-32 усіх попередніх байтів (ОСТАННЄ поле!)
} prov_record_t;
