#ifndef BUDGET_TYPES_H
#define BUDGET_TYPES_H

/*
 * Спільний словник підсистеми аудиту бюджетів.
 *
 * Кожен інженерний бюджет має власний біт у масці порушень: підсистема ніколи
 * не повертає «перше знайдене порушення», бо на реальній платі просідання шини
 * живлення й переповнення стеку трапляються одночасно і мають різні наслідки.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef uint32_t budget_flags_t;

enum {
    BUDGET_OK                 = 0u,

    /* Бюджет пам'яті */
    BUDGET_STACK_LOW          = 1u << 0,  /* запас стеку впав нижче резерву */
    BUDGET_STACK_OVERFLOW     = 1u << 1,  /* сторожове слово стеку затерте */
    BUDGET_HEAP_LOW           = 1u << 2,  /* сумарний вільний обсяг кучі малий */
    BUDGET_HEAP_FRAGMENTED    = 1u << 3,  /* вільного багато, суцільного блоку немає */
    BUDGET_FLASH_NO_OTA       = 1u << 4,  /* образ не влазить у пасивний слот */
    BUDGET_FLASH_TIGHT        = 1u << 5,  /* образ перетнув 45 % повного Flash */

    /* Струмовий та енергетичний бюджети */
    BUDGET_VDD_SAG            = 1u << 6,  /* напруга нижча за поріг тривоги */
    BUDGET_VDD_BROWNOUT       = 1u << 7,  /* напруга дійшла до порогу BOR */
    BUDGET_ENERGY_OVER        = 1u << 8,  /* середній струм з'їдає батарею завчасно */

    /* Тепловий бюджет */
    BUDGET_THERMAL_WARN       = 1u << 9,  /* кристал увійшов у зону запасу */
    BUDGET_THERMAL_TRIP       = 1u << 10, /* перевищено T_j_max */

    /* Часовий бюджет критичних секцій */
    BUDGET_DEADLINE_MISS      = 1u << 11  /* секція вибігла за відведений час */
};

/* Порушення, після яких пристрій не має права продовжувати штатну роботу. */
#define BUDGET_CRITICAL_MASK                                                   \
    (BUDGET_STACK_OVERFLOW | BUDGET_VDD_BROWNOUT | BUDGET_THERMAL_TRIP |       \
     BUDGET_HEAP_FRAGMENTED)

typedef enum {
    BUDGET_SEVERITY_OK = 0,
    BUDGET_SEVERITY_WARNING,
    BUDGET_SEVERITY_CRITICAL
} budget_severity_t;

budget_severity_t budget_severity_of(budget_flags_t flags);

/* Назва одного біта; для невідомого біта повертає "?". */
const char *budget_flag_name(budget_flags_t single_flag);

/*
 * Складає перелік піднятих бітів у рядок через кому.
 * Повертає кількість записаних символів без завершального нуля; вихід завжди
 * нуль-термінований, якщо cap > 0.
 */
size_t budget_flags_format(budget_flags_t flags, char *out, size_t cap);

#endif /* BUDGET_TYPES_H */
