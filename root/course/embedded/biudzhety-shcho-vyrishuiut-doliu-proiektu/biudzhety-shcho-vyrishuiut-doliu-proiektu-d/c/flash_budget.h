#ifndef FLASH_BUDGET_H
#define FLASH_BUDGET_H

/*
 * Бюджет Flash-пам'яті під безвідмовне оновлення по повітрю.
 *
 * Повний обсяг ділиться на завантажувач, енергонезалежне сховище і два
 * однакові слоти образу. Слот, куди не влазить поточний образ, робить OTA
 * неможливим: запис поверх активного слота перетворює пристрій на цеглину при
 * першому ж зникненні живлення.
 */

#include "budget_types.h"

typedef struct {
    uint32_t total_bytes;      /* повний обсяг Flash мікроконтролера */
    uint32_t sector_bytes;     /* гранула стирання: слоти вирівнюються по ній */
    uint32_t bootloader_bytes; /* незмінний сектор перевірки підпису */
    uint32_t nvs_bytes;        /* сховище ключів, сертифікатів, калібрувань */
    uint32_t image_bytes;      /* розмір скомпільованого образу */
} flash_layout_t;

typedef struct {
    uint32_t slot_bytes;       /* розмір кожного зі слотів A і B */
    uint32_t slot_free_bytes;  /* запас у слоті під майбутні версії */
    uint32_t image_share_pm;   /* частка образу від повного Flash, проміле */
    uint32_t unusable_bytes;   /* залишок, що не влазить у пару слотів */
    bool     dual_bank_ready;  /* чи можливе оновлення без ризику */
} flash_report_t;

budget_flags_t flash_budget_audit(const flash_layout_t *layout,
                                  flash_report_t *report);

#endif /* FLASH_BUDGET_H */
