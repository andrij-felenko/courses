/* Завантажувач: єдиний код, який вирішує, звідки стартувати.
 * Лежить за адресою вектора скидання й закритий від запису бітами Option Bytes. */
#ifndef BOOT_H
#define BOOT_H

#include <stdbool.h>
#include <stdint.h>

#include "flash.h"

typedef enum {
    BOOT_RUN,           /* стартуємо з вибраного банку          */
    BOOT_ROLLED_BACK,   /* лічильник збоїв вичерпано — повернулись на старий банк */
    BOOT_NO_IMAGE       /* жоден банк не цілий: лишаємось у завантажувачі */
} boot_kind_t;

typedef struct {
    boot_kind_t kind;
    boot_bank_t bank;
    uint32_t    entry;       /* база банку = початок його таблиці векторів */
    uint8_t     failures;    /* лічильник аварійних стартів після інкременту */
} boot_decision_t;

boot_decision_t boot_select(void);

/* Передача керування: VTOR на таблицю векторів банку, MSP з неї ж, стрибок на
 * Reset_Handler. Повернення звідси немає. */
void boot_jump(uint32_t bank_base);

#endif /* BOOT_H */
