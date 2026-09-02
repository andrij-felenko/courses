#ifndef FAULT_REPORT_H
#define FAULT_REPORT_H

/*
 * Посмертний розбір помилок ядра.
 *
 * Довідник описує ескалацію словами: поки стоїть маска, настроюваний обробник
 * (MemManage, BusFault, UsageFault) виконатися не може, і апаратура підмінює
 * його HardFault-ом із пріоритетом -1. Цей модуль перетворює ту підміну на
 * запис, який переживає скидання, і відповідає на єдине питання, заради якого
 * його й писали:
 *
 *     помилка сталася ВСЕРЕДИНІ критичної секції чи поза нею?
 *
 * Ознакою підміни служить біт HFSR.FORCED, ознакою секції — маски, зчитані
 * при вході в обробник (вхід у виключення їх не міняє, тому в обробнику ще
 * видно той самий стан, у якому програма була в момент помилки).
 *
 * Випадок FAULTMASK сюди не потрапляє взагалі: помилка під FAULTMASK — це
 * Lockup State, ядро припиняє вибірку інструкцій, і жоден обробник не
 * запускається. Слід у такому разі лишає хіба сторожовий таймер.
 */

#include "stm32f4xx.h"

#include <stdbool.h>
#include <stdint.h>

/* Яке саме виключення привело нас у пролог asm/fault_entry.S. */
typedef enum {
    FAULT_KIND_HARD      = 0,
    FAULT_KIND_MEMMANAGE = 1,
    FAULT_KIND_BUS       = 2,
    FAULT_KIND_USAGE     = 3
} fault_kind_t;

/*
 * Кадр, який апаратура складає на стек перед входом у обробник. Порядок
 * полів заданий архітектурою, міняти його не можна. Регістри r4..r11 сюди
 * не входять — їх зберігає викликана функція, а не апаратура.
 */
typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;     /* адреса повернення того, хто викликав винуватця */
    uint32_t pc;     /* інструкція, на якій усе сталося                */
    uint32_t xpsr;   /* біт 9 = 1: апаратура вставила 4 байти вирівнювання */
} fault_frame_t;

typedef struct {
    fault_kind_t kind;
    uint32_t exc_return;   /* біт 2: кадр на PSP; біт 3: перервано Thread Mode */

    uint32_t hfsr;         /* FORCED, VECTTBL, DEBUGEVT */
    uint32_t cfsr;         /* MMFSR[7:0] | BFSR[15:8] | UFSR[31:16] */
    uint32_t mmfar;        /* дійсна лише при mmfar_valid */
    uint32_t bfar;         /* дійсна лише при bfar_valid  */
    bool mmfar_valid;
    bool bfar_valid;
    bool escalated;        /* HFSR.FORCED: сюди нас відправила підміна */

    /* Маски в момент помилки. */
    uint32_t primask;
    uint32_t basepri;
    uint32_t faultmask;

    fault_frame_t frame;
} fault_record_t;

/*
 * Точка входу з асемблерного прологу. Тіло не повертається: воно гасить
 * силовий каскад, складає запис і просить апаратне скидання.
 */
void fault_entry_to_c(const fault_frame_t *frame, uint32_t exc_return, uint32_t kind);

/*
 * Вмикає настроювані обробники помилок і пастку ділення на нуль.
 * Без цього BusFault та UsageFault як окремі виключення не існують: усе
 * приходить HardFault-ом одразу, і відрізнити ескалацію від звичайної
 * фатальної помилки стає нічим.
 */
void fault_report_enable_configurable_faults(void);

/* Запис попереднього запуску або NULL, якщо його немає. */
const fault_record_t *fault_report_last(void);

/* Позначає запис прочитаним: наступне завантаження почнеться з чистого аркуша. */
void fault_report_clear(void);

/* Чи стояла в момент помилки хоч якась маска — тобто чи була відкрита секція. */
bool fault_report_masked_at_fault(const fault_record_t *rec);

/*
 * Адреса, на якій стався збій, якщо апаратура її зафіксувала. Повертає false
 * для неточної помилки шини: там запис завис у буфері, BFAR не заповнюється,
 * а PC у кадрі показує вже наступні інструкції.
 */
bool fault_report_data_address(const fault_record_t *rec, uint32_t *out_address);

/* Причина людською мовою: перший встановлений біт CFSR у порядку розбору. */
const char *fault_report_cause(const fault_record_t *rec);

#endif /* FAULT_REPORT_H */
