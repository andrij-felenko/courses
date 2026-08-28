#include <stdint.h>
#include <stdbool.h>

#define BOOT_METADATA_MAGIC 0x544F4F42UL /* ASCII "BOOT" */

typedef enum {
    OTA_SLOT_STATE_EMPTY          = 0xFF, /* Слот стертий або не містить валідного образу */
    OTA_SLOT_STATE_UNVALIDATED    = 0x01, /* Новий образ записано, очікує пробного запуску */
    OTA_SLOT_STATE_VALID          = 0x02, /* Прошивку підтверджено застосунком як робочу */
    OTA_SLOT_STATE_MARKED_BAD     = 0x03  /* Прошивка зазнала краху під час випробування */
} ota_slot_state_t;

typedef struct {
    uint32_t magic;               /* Магічний маркер валідності структури (0x544F4F42) */
    uint32_t sequence_number;     /* Монотонний лічильник транзакцій */
    uint8_t  active_slot;         /* Ідентифікатор активного слота: 0 = Slot_A, 1 = Slot_B */
    uint8_t  slot_state;          /* Поточний стан активного слота (ota_slot_state_t) */
    uint8_t  boot_attempts_left;  /* Залишок дозволених спроб запуску */
    uint8_t  max_boot_attempts;   /* Початковий ліміт спроб (типово 3) */
    uint32_t image_version;       /* Числовий монотонний номер версії образу */
    uint32_t image_crc;           /* Контрольна сума всього тіла прошивки */
    uint32_t header_crc;          /* Контрольна сума CRC32 структури метаданих */
} __attribute__((packed)) boot_metadata_t;
