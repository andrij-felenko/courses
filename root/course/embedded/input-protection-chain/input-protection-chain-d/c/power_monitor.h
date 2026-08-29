/* power_monitor.h — програмний нагляд за вхідним живленням.
 *
 * Модуль замикає ланцюг апаратного захисту з боку прошивки: читає напругу шини
 * через дільник 110к/10к і АЦП, тримає вікно між UVLO та OVLO з гістерезисом,
 * керує ключем дозволу навантаження (PIN_PWR_ENABLE) і приймає сигнал аварії
 * від eFuse (PIN_FAULT_IRQ). Апаратура в модуль не заходить: усе, що йому
 * потрібно ззовні, — код АЦП, час у мілісекундах і зворотний виклик ключа.
 */
#ifndef POWER_MONITOR_H
#define POWER_MONITOR_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    PWR_OFF = 0,      /* ключ розімкнено, чекаємо доброї напруги */
    PWR_SETTLING,     /* напруга у вікні, витримуємо перед вмиканням */
    PWR_ON,           /* ключ замкнено, навантаження живиться */
    PWR_FAULT_UVLO,   /* просідання нижче порогу — чекаємо на авто-повтор */
    PWR_FAULT_OVLO,   /* перенапруга — чекаємо на авто-повтор */
    PWR_FAULT_EFUSE,  /* прийшов FLT від eFuse */
    PWR_LOCKOUT       /* серія аварій вичерпала ліміт повторів: засув */
} pwr_state_t;

typedef enum {
    PWR_OK = 0,
    PWR_ERR_ARG,     /* нульовий покажчик */
    PWR_ERR_CONFIG   /* конфігурація суперечлива або вироджена */
} pwr_err_t;

typedef struct {
    /* Вимірювальний тракт: R_top = 110 кОм, R_bottom = 10 кОм, V_ref = 3.3 В */
    uint32_t div_top_ohm;
    uint32_t div_bottom_ohm;
    uint16_t vref_mv;
    uint16_t adc_full_scale;  /* 4095 для 12-бітного АЦП */
    uint8_t  filter_shift;    /* IIR-згладжування: стала 1/2^shift */

    /* Вікно безпеки. Пороги спрацьовування й повернення рознесені гістерезисом,
     * інакше напруга, що тремтить біля порога, дає брязкіт ключа. */
    uint32_t uvlo_trip_mv;    /* нижче цього — вимикаємо (16 500) */
    uint32_t uvlo_clear_mv;   /* вище цього — знову дозволяємо (18 000) */
    uint32_t ovlo_clear_mv;   /* нижче цього — знову дозволяємо (30 500) */
    uint32_t ovlo_trip_mv;    /* вище цього — вимикаємо (32 000) */

    uint16_t confirm_samples; /* скільки вибірок поспіль підтверджують аварію */
    uint16_t settle_samples;  /* витримка у вікні перед вмиканням ключа */

    uint32_t retry_delay_ms;  /* пауза перед авто-повтором після аварії */
    uint32_t retry_window_ms; /* тиша такої довжини обнуляє лічильник повторів */
    uint8_t  retry_limit;     /* скільки повторів дозволено; 0 — без ліміту */
} pwr_config_t;

typedef struct {
    uint32_t samples;
    uint32_t uvlo_events;
    uint32_t ovlo_events;
    uint32_t efuse_events;
    uint32_t lockouts;
    uint32_t starts;      /* скільки разів ключ вмикався */
    uint32_t v_min_mv;
    uint32_t v_max_mv;
} pwr_stats_t;

typedef struct {
    pwr_config_t cfg;
    void       (*set_enable)(void *ctx, bool on);
    void        *ctx;

    pwr_state_t state;
    pwr_state_t pending_fault;   /* яка саме аварія набирає підтвердження */

    uint32_t filtered_q8;        /* стан IIR-фільтра у форматі Q8 */
    bool     primed;             /* фільтр уже заряджений першою вибіркою */
    uint32_t voltage_mv;         /* остання відфільтрована напруга шини */

    uint16_t confirm_count;      /* вибірок поспіль поза вікном */
    uint16_t settle_count;       /* вибірок поспіль у вікні */

    uint32_t retry_at_ms;
    uint32_t last_fault_ms;
    uint8_t  retries_used;

    volatile uint8_t efuse_flag; /* ставить переривання, знімає on_sample */
    bool     enabled;            /* поточний стан PIN_PWR_ENABLE */
    pwr_stats_t stats;
} pwr_monitor_t;

/* Ініціалізація. Конфігурацію копіюємо всередину, ключ одразу розмикаємо. */
pwr_err_t pwr_monitor_init(pwr_monitor_t *mon,
                           const pwr_config_t *cfg,
                           void (*set_enable)(void *ctx, bool on),
                           void *ctx);

/* Викликається з переривання PIN_FAULT_IRQ: лише ставить прапорець. */
void pwr_monitor_efuse_isr(pwr_monitor_t *mon);

/* Одна вибірка АЦП у момент часу now_ms. Уся логіка живе тут. */
pwr_err_t pwr_monitor_on_sample(pwr_monitor_t *mon, uint16_t adc_code, uint32_t now_ms);

/* Зняти засув (втручання оператора чи команда згори). true — засув справді був. */
bool pwr_monitor_clear_lockout(pwr_monitor_t *mon, uint32_t now_ms);

pwr_state_t        pwr_monitor_state(const pwr_monitor_t *mon);
uint32_t           pwr_monitor_voltage_mv(const pwr_monitor_t *mon);
bool               pwr_monitor_output_enabled(const pwr_monitor_t *mon);
const pwr_stats_t *pwr_monitor_stats(const pwr_monitor_t *mon);
const char        *pwr_state_name(pwr_state_t state);

#endif /* POWER_MONITOR_H */
