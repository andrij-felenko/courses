#ifndef BOOT_STATE_H
#define BOOT_STATE_H

#include <stdint.h>

#include "boot_status.h"

/* Два банки прошивки: A — той, що працює, B — той, що приїхав оновленням. */
typedef enum {
    BOOT_SLOT_A = 0,
    BOOT_SLOT_B = 1
} boot_slot_t;

#define BOOT_STATE_MAGIC   0x41545342U  /* "BSTA" */
#define STATUS_CONFIRMED   0x434F4E46U  /* "CONF" — образ підтверджено застосунком */
#define STATUS_TESTING     0x54455354U  /* "TEST" — образ у пробному запуску */

/* Скільки пробних запусків дозволено, поки застосунок не підтвердив себе. */
#define BOOT_MAX_TRIES     3U

/*
 * Запис стану завантаження. Лежить в окремій сторінці Flash, накритий CRC-32:
 * зникнення живлення посеред запису мусить читатися як «запис зіпсовано»,
 * а не як довільне сміття у полях.
 */
typedef struct {
    uint32_t magic;                /* 0x00 */
    uint32_t crc;                  /* 0x04: CRC-32 байтів 0x08..0x20 */
    uint32_t active_slot;          /* 0x08: який банк запускати */
    uint32_t previous_slot;        /* 0x0C: куди відкочуватись, якщо пробний провалився */
    uint32_t status;               /* 0x10: STATUS_CONFIRMED або STATUS_TESTING */
    uint32_t try_count;            /* 0x14: скільки пробних запусків уже було */
    uint32_t pending_revoke_mask;  /* 0x18: слоти ключів, які спалити після підтвердження */
    uint32_t pending_counter;      /* 0x1C: до якого значення підняти лічильник */
} boot_state_t;

/* Читає запис; при пошкодженні або чистій сторінці віддає стан «банк A, підтверджено». */
void boot_state_load(boot_state_t *state);

/* Перераховує CRC і переписує сторінку стану. */
boot_status_t boot_state_store(boot_state_t *state);

/*
 * ПЕРША ФАЗА двофазного комміту. Викликає застосунок, коли новий образ уже
 * записано в інший банк: ми лише позначаємо його як пробний. Жодна перемичка
 * тут не палиться — саме тому цей крок оборотний.
 */
boot_status_t boot_stage_update(boot_slot_t new_slot);

/*
 * ДРУГА ФАЗА двофазного комміту. Викликає САМ ЗАСТОСУНОК після самодіагностики
 * і першого успішного зв'язку з сервером. Тільки тут — і ніде раніше — палимо
 * біти відкликання старих ключів і піднімаємо лічильник анти-відкату.
 */
boot_status_t boot_confirm_update(void);

#endif /* BOOT_STATE_H */
