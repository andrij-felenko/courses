/* latency.h — модель бюджету затримки телекерованого комплексу.
 *
 * Тракт (pipeline) — це впорядкований список ланок від події до наслідку:
 * від руху стика до зміни тяги, або від фотона на матриці до світіння
 * пікселя в окулярах. Кожна ланка вміє сказати три числа: скільки часу
 * вона з'їдає у найкращому, типовому й найгіршому випадку.
 *
 * Пам'ять не виділяється ніде: структура тракту самодостатня й лягає
 * на стек бортового діагностичного модуля.
 */
#ifndef LATENCY_H
#define LATENCY_H

#include <stdbool.h>
#include <stddef.h>

/* Довших трактів у бюджеті не буває: якщо ланок більше, тракт треба
   різати на два незалежні (команди окремо, відео окремо). */
#define LAT_MAX_STAGES 20

typedef enum {
    LAT_FIXED,    /* стала: час у дроті, час обчислення, час у повітрі */
    LAT_PERIODIC, /* квантування тактом: чекання наступного циклу */
    LAT_BAND      /* вилка min..typ..max: фізика з розкидом */
} lat_kind;

typedef enum {
    LAT_ELECTRONIC, /* цифра й радіо: те, що інженер може прискорити */
    LAT_PHYSICAL    /* інерція гвинта, експозиція, час відгуку пікселя */
} lat_domain;

typedef enum {
    LAT_OK = 0,
    LAT_ERR_FULL,  /* у тракті вже LAT_MAX_STAGES ланок */
    LAT_ERR_ORDER, /* вилка задана хибно */
    LAT_ERR_RATE,  /* частота такту або люфт фазування хибні */
    LAT_ERR_LINK,  /* параметри шини хибні */
    LAT_ERR_EMPTY  /* у тракті немає ланки потрібного типу */
} lat_status;

const char *lat_strerror(lat_status st);

typedef struct {
    const char *name;
    lat_kind    kind;
    lat_domain  domain;
    double      min_ms;
    double      typ_ms;
    double      max_ms;
    double      period_ms; /* період такту для LAT_PERIODIC, інакше 0 */
    bool        synced;    /* тайм-слот зафазовано з попередньою ланкою */
    lat_status  defect;    /* конструктор не аварійно завершує — він позначає */
} lat_stage;

/* --- Конструктори ланок -------------------------------------------------
 * Конструктор нічого не друкує й нічого не перериває: хибні аргументи він
 * запам'ятовує в полі defect, а відмовляє вже lat_pipeline_add. Так виклик
 * лишається виразом, який можна писати таблицею просто в коді конфігурації.
 */

/* Стала затримка: обчислення мікшера, комутація ключів, час у повітрі. */
lat_stage lat_fixed(const char *name, double ms);

/* Вилка: фізика з розкидом (розгін гвинта, час експозиції, декодер). */
lat_stage lat_band(const char *name, double min_ms, double typ_ms, double max_ms);

/* Квантування тактом частоти rate_hz.
 * Незафазована ланка: подія рівноймовірно падає всередину періоду, тож
 * min = 0, typ = T/2, max = T.
 * Зафазована (EdgeTX Mixer Sync, растр аналогових окулярів за синхросигналом):
 * квант згортається до сталого зсуву slack_ms — саме в цьому весь виграш.
 */
lat_stage lat_periodic(const char *name, double rate_hz, bool synced, double slack_ms);

/* Час фізичної видачі кадру в асинхронну шину: SBUS, CRSF, будь-який UART.
 * bits_per_byte враховує старт/стоп/парність (для 8-E-2 це 11, для 8-N-1 — 10).
 */
lat_stage lat_serial(const char *name, size_t frame_bytes, double baud_bps,
                     unsigned bits_per_byte);

/* Позначає ланку фізичною: її не прискорити ні прошивкою, ні швидшим МК. */
lat_stage lat_physical(lat_stage st);

/* --- Тракт --------------------------------------------------------------- */

typedef struct {
    const char *title;
    lat_stage   stages[LAT_MAX_STAGES];
    size_t      count;
} lat_pipeline;

void       lat_pipeline_init(lat_pipeline *p, const char *title);
lat_status lat_pipeline_add(lat_pipeline *p, lat_stage st);

typedef struct {
    double min_ms;
    double typ_ms;
    double max_ms;
    double jitter_ms;         /* max - min: розмах, який контур бачить як шум */
    double electronic_typ_ms; /* що можна прискорити інженерією */
    double physical_typ_ms;   /* що впирається у фізику */
} lat_budget;

lat_budget lat_budget_of(const lat_pipeline *p);
/* Контур оператора замикається через два тракти: команда туди, картинка назад. */
lat_budget lat_budget_sum(lat_budget a, lat_budget b);

/* Найтовща ланка за найгіршим випадком — з неї починають боротьбу за лаг.
 * share (може бути NULL) отримує її частку від max усього тракту. */
lat_status lat_bottleneck(const lat_pipeline *p, const lat_stage **out, double *share);

/* Найбільший часовий квант серед тактових ланок: закон пляшкового горла
 * каже оптимізувати саме його, а не мікросекунди DShot. */
lat_status lat_worst_quantum(const lat_pipeline *p, const lat_stage **out);

/* --- Динаміка замкненого контуру ---------------------------------------- */

/* Чиста затримка дає лінійно наростальний фазовий зсув: 360° · f · t. */
double lat_phase_shift_deg(double delay_ms, double control_hz);

typedef enum {
    LAT_PIO_SAFE,    /* запас за фазою є */
    LAT_PIO_WATCH,   /* оператор уже відчуває «гуму» на ручці */
    LAT_PIO_UNSTABLE /* зворотний зв'язок став позитивним: розгойдування */
} lat_pio;

lat_pio     lat_pio_verdict(double phase_deg);
const char *lat_pio_text(lat_pio verdict);

/* Скільки метрів апарат проходить наосліп за час затримки. */
double lat_blind_distance_m(double delay_ms, double speed_mps);

#endif /* LATENCY_H */
