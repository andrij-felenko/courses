/* dwt.h — блок DWT ядра Cortex-M (M3/M4/M7): лічильник тактів і лічильники подій.
 *
 * Це шар голого заліза: карта регістрів на приватній периферійній шині (PPB),
 * увімкнення CYCCNT і програмне розширення 8-розрядних лічильників подій до
 * 32 розрядів. Усе inline: виклик коштує кілька тактів, а профілювальник
 * вимірює інтервали в десятки мікросекунд — власний шум має бути мізерним.
 */
#ifndef DWT_H
#define DWT_H

#include <stdbool.h>
#include <stdint.h>

/* CoreDebug: без TRCENA логіка трасування знеструмлена і DWT не відповідає */
#define CORE_DEBUG_DEMCR    (*(volatile uint32_t *)0xE000EDFCU)
#define DEMCR_TRCENA        (1UL << 24)

/* Блок DWT, база 0xE0001000 */
#define DWT_CTRL            (*(volatile uint32_t *)0xE0001000U)
#define DWT_CYCCNT          (*(volatile uint32_t *)0xE0001004U)
#define DWT_CPICNT          (*(volatile uint32_t *)0xE0001008U)
#define DWT_EXCCNT          (*(volatile uint32_t *)0xE000100CU)
#define DWT_SLEEPCNT        (*(volatile uint32_t *)0xE0001010U)
#define DWT_LSUCNT          (*(volatile uint32_t *)0xE0001014U)
#define DWT_FOLDCNT         (*(volatile uint32_t *)0xE0001018U)
/* CoreSight Lock Access: на Cortex-M7 без ключа запис у DWT мовчки гине */
#define DWT_LAR             (*(volatile uint32_t *)0xE0001FB0U)
#define DWT_LAR_KEY         0xC5ACCE55U

/* Біти DWT_CTRL */
#define DWT_CTRL_CYCCNTENA   (1UL << 0)
#define DWT_CTRL_EXCTRCENA   (1UL << 16)
#define DWT_CTRL_CPIEVTENA   (1UL << 17)
#define DWT_CTRL_EXCEVTENA   (1UL << 18)
#define DWT_CTRL_SLEEPEVTENA (1UL << 19)
#define DWT_CTRL_LSUEVTENA   (1UL << 20)
#define DWT_CTRL_FOLDEVTENA  (1UL << 21)
#define DWT_CTRL_NOPRFCNT    (1UL << 24) /* 1 — лічильників подій немає */
#define DWT_CTRL_NOCYCCNT    (1UL << 25) /* 1 — CYCCNT не реалізовано */

/* Найдешевше читання: одна інструкція LDR по PPB. */
static inline uint32_t dwt_cyccnt(void)
{
    return DWT_CYCCNT;
}

/* Читання з бар'єрами — коли важливо, щоб мітка не переїхала через
 * досліджуваний код при -O2. Коштує на кілька тактів дорожче. */
static inline uint32_t dwt_cyccnt_serialized(void)
{
    uint32_t value;
    __asm__ volatile("" ::: "memory");        /* заборона перестановки компілятором */
    __asm__ volatile("dsb 0xF" ::: "memory"); /* завершити всі доступи до пам'яті */
    __asm__ volatile("isb 0xF" ::: "memory"); /* скинути конвеєр вибірки */
    value = DWT_CYCCNT;
    __asm__ volatile("" ::: "memory");
    return value;
}

static inline bool dwt_has_cycle_counter(void)
{
    return (DWT_CTRL & DWT_CTRL_NOCYCCNT) == 0UL;
}

static inline bool dwt_has_event_counters(void)
{
    return (DWT_CTRL & DWT_CTRL_NOPRFCNT) == 0UL;
}

/* Вмикає CYCCNT і перевіряє, що він справді лічить: на частині ядер без
 * під'єднаного відладчика домен трасування лишається без живлення, і тоді
 * регістр читається як сталий нуль. Мовчазний нуль гірший за чесне false. */
static inline bool dwt_enable_cycle_counter(void)
{
    uint32_t before;

    CORE_DEBUG_DEMCR |= DEMCR_TRCENA;
    DWT_LAR = DWT_LAR_KEY; /* на ядрах без замка запис нешкідливий */

    if (!dwt_has_cycle_counter()) {
        return false;
    }

    DWT_CYCCNT = 0U;
    DWT_CTRL |= DWT_CTRL_CYCCNTENA;

    before = dwt_cyccnt();
    for (volatile int i = 0; i < 8; ++i) {
        /* коротка затримка, щоб лічильник устиг зрушити */
    }
    return dwt_cyccnt() != before;
}

/* Лічильники подій конвеєра рахують лише коли ввімкнено їхній біт EVTENA. */
static inline void dwt_enable_event_counters(void)
{
    if (!dwt_has_event_counters()) {
        return;
    }
    DWT_CPICNT = 0U;
    DWT_EXCCNT = 0U;
    DWT_SLEEPCNT = 0U;
    DWT_LSUCNT = 0U;
    DWT_FOLDCNT = 0U;
    DWT_CTRL |= DWT_CTRL_CPIEVTENA | DWT_CTRL_EXCEVTENA | DWT_CTRL_SLEEPEVTENA |
                DWT_CTRL_LSUEVTENA | DWT_CTRL_FOLDEVTENA;
}

/* Лічильники подій — 8-розрядні: крутяться через нуль кожні 256 підрахованих
 * тактів. Тримаємо копію останнього байта й доліковуємо беззнакову різницю в
 * 32-розрядний накопичувач. Розширення точне, поки між двома викликами
 * dwt_events_sample() назбирується менш ніж 256 подій: для EXCCNT і LSUCNT
 * достатньо смикати вибірку на кожному перемиканні контексту, а от довгий
 * tickless-сон SLEEPCNT цим способом не полічить — там потрібні пакети
 * переповнення ITM або власний облік RTOS. */
typedef struct {
    uint8_t last_cpi;
    uint8_t last_exc;
    uint8_t last_sleep;
    uint8_t last_lsu;
    uint8_t last_fold;
    uint32_t cpi_cyc;   /* такти простою конвеєра на багатотактових інструкціях */
    uint32_t exc_cyc;   /* стекінг, анстекінг і код обробників переривань */
    uint32_t sleep_cyc; /* такти, проведені ядром у WFI/WFE */
    uint32_t lsu_cyc;   /* очікування блоку завантаження/збереження */
    uint32_t fold_cyc;  /* «згорнуті» переходи, виконані без витрати такту */
} dwt_events_t;

static inline void dwt_events_reset(dwt_events_t *events)
{
    events->last_cpi = (uint8_t)DWT_CPICNT;
    events->last_exc = (uint8_t)DWT_EXCCNT;
    events->last_sleep = (uint8_t)DWT_SLEEPCNT;
    events->last_lsu = (uint8_t)DWT_LSUCNT;
    events->last_fold = (uint8_t)DWT_FOLDCNT;
    events->cpi_cyc = 0U;
    events->exc_cyc = 0U;
    events->sleep_cyc = 0U;
    events->lsu_cyc = 0U;
    events->fold_cyc = 0U;
}

static inline void dwt_events_sample(dwt_events_t *events)
{
    const uint8_t cpi = (uint8_t)DWT_CPICNT;
    const uint8_t exc = (uint8_t)DWT_EXCCNT;
    const uint8_t slp = (uint8_t)DWT_SLEEPCNT;
    const uint8_t lsu = (uint8_t)DWT_LSUCNT;
    const uint8_t fld = (uint8_t)DWT_FOLDCNT;

    /* різниця в 8 розрядах коректна й через переповнення — той самий
     * додатковий код, що й для 32-розрядного CYCCNT */
    events->cpi_cyc += (uint8_t)(cpi - events->last_cpi);
    events->exc_cyc += (uint8_t)(exc - events->last_exc);
    events->sleep_cyc += (uint8_t)(slp - events->last_sleep);
    events->lsu_cyc += (uint8_t)(lsu - events->last_lsu);
    events->fold_cyc += (uint8_t)(fld - events->last_fold);

    events->last_cpi = cpi;
    events->last_exc = exc;
    events->last_sleep = slp;
    events->last_lsu = lsu;
    events->last_fold = fld;
}

#endif /* DWT_H */
