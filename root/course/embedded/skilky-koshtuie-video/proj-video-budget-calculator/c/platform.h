#ifndef VIDEO_PLATFORM_H
#define VIDEO_PLATFORM_H

#include <stddef.h>

#include "budget.h"

/* Чи вміщується порахований бюджет у конкретне залізо. Цифри шини —
 * ПРАКТИЧНІ (з урахуванням накладних витрат контролера і refresh), а не
 * піковий добуток частоти на розрядність із рекламного аркуша. */
typedef struct {
    const char *name;
    double bus_mbytes_s; /* практична пропускна здатність шини пам'яті, МБ/с */
    double ram_mb;       /* пам'ять, доступна під кадрові буфери, МБ */
} platform_t;

typedef enum {
    FIT_OK = 0,        /* трафік у межах безпечної частки шини */
    FIT_RISKY,         /* понад 60 % шини: черги встигають голодувати на піках */
    FIT_BUS_OVERLOAD,  /* трафік більший за саму шину */
    FIT_NO_RAM         /* пул буферів не вміщується взагалі */
} platform_fit_t;

typedef struct {
    platform_fit_t verdict;
    double bus_load_percent;
    double ram_load_percent;
} platform_check_t;

/* Понад цю частку шини кадрові FIFO починають переповнюватись на піках
 * трафіку — запас потрібен під refresh, конкуренцію з CPU і сплески кодека. */
#define BUS_SAFE_PERCENT 60.0

const platform_t *platform_table(size_t *count);
platform_check_t  platform_check(const platform_t *platform, const video_budget_t *budget);
const char       *platform_fit_text(platform_fit_t fit);

#endif /* VIDEO_PLATFORM_H */
