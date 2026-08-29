/* Карта Flash, запис образу в неактивний банк і незалежний від RAM стан кампанії.
 *
 * Карта повторює розкладку статті: 1 МБ на кристалі Cortex-M, два симетричні
 * банки по 432 КБ і два службові сектори. */
#ifndef FLASH_H
#define FLASH_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define BOOTLOADER_BASE 0x08000000u   /*  64 КБ  захищений завантажувач        */
#define BOOTLOADER_SIZE 0x00010000u

#define NVRAM_BASE      0x08010000u   /*  16 КБ  стан кампанії та ключі OTA    */
#define NVRAM_SIZE      0x00004000u

#define BANK_A_BASE     0x08014000u   /* 432 КБ  основний розділ виконання     */
#define BANK_B_BASE     0x08080000u   /* 432 КБ  резервний розділ оновлення    */
#define BANK_SIZE       0x0006C000u

#define NVS_BASE        0x080EC000u   /*  80 КБ  налаштування застосунку       */
#define NVS_SIZE        0x00014000u

typedef enum {
    BOOT_BANK_A = 0,
    BOOT_BANK_B = 1
} boot_bank_t;

#define MAX_ALLOWED_CRASHES 3u

/* Стан кампанії. Живе в RTC Backup Domain (переживає скидання ядра) і
 * дублюється журналом у секторі NVRAM (переживає зникнення живлення).
 * У RAM його не тримають: лічильник збоїв, який щоразу починається з нуля,
 * дає нескінченну петлю перезавантажень. */
typedef struct {
    boot_bank_t active_bank;
    bool        trial_pending;   /* прошивка ще не підтвердила стабільність */
    uint8_t     boot_failures;   /* аварійні старти нової версії            */
    uint8_t     seq;             /* версія запису; старша перемагає         */
    uint32_t    campaign_id;
    uint32_t    bank_len[2];     /* довжина образу в кожному банку          */
    uint32_t    bank_crc[2];     /* CRC-32 цього образу                     */
} ota_state_t;

/* Читання стану: backup-регістри → журнал NVRAM → типовий стан (Bank A). */
void ota_state_load(ota_state_t *out);

/* Запис стану в обидва сховища. Хибне значення означає, що журнал у Flash не
 * оновився: стан у backup-регістрах усе одно записаний. */
bool ota_state_store(ota_state_t *st);

uint32_t flash_bank_base(boot_bank_t bank);
boot_bank_t flash_other_bank(boot_bank_t bank);

/* Стирання цілого банку перед завантаженням образу. */
bool flash_bank_erase(boot_bank_t bank);

/* Запис блоку OTA. Виконується з RAM: у багатьох сімействах запис у Flash
 * блокує вибірку інструкцій з усієї Flash, і переривання, що виконується
 * звідти, вішає ядро на шині. */
bool flash_bank_write(boot_bank_t bank, uint32_t offset, const uint8_t *data, size_t len);

uint32_t flash_bank_crc(boot_bank_t bank, uint32_t len);

uint32_t crc32_update(uint32_t crc, const uint8_t *data, size_t len);

#endif /* FLASH_H */
