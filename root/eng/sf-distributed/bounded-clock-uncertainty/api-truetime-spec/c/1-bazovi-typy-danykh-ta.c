#include <stdint.h>
#include <stdbool.h>

/* Часовий інтервал TrueTime в наносекундах */
typedef struct {
    int64_t earliest_ns; /* Нижня межа довірчого інтервалу (t_local - ε) */
    int64_t latest_ns;   /* Верхня межа довірчого інтервалу (t_local + ε) */
} tt_interval_ns_t;

/* Статус джерела синхронізації */
typedef enum {
    TT_SOURCE_GPS_LOCKED      = 0, /* GNSS активний, сигнал PPS стабільний (ε < 10 мкс) */
    TT_SOURCE_PTP_LOCKED      = 1, /* Апаратний PTP IEEE 1588 активний (ε < 50 мкс) */
    TT_SOURCE_ATOMIC_HOLDOVER = 2, /* Робота від рубідієвого генератора без GPS (ε повільно росте) */
    TT_SOURCE_NTP_FALLBACK    = 3, /* Аварійний режим NTP (ε від 1 до 50 мс) */
    TT_SOURCE_UNSYNCHRONIZED  = 4  /* Критичний збій: перевищено ліміт безпеки MAX_UNCERTAINTY */
} tt_source_status_t;

/* Структура діагностики стану годинника */
typedef struct {
    tt_source_status_t status;
    int64_t current_uncertainty_ns;     /* Поточне значення ε в наносекундах */
    int64_t max_allowed_uncertainty_ns; /* Поріг аварійної паніки */
    int64_t time_since_last_sync_ns;    /* Час від останнього сеансу корекції */
    int32_t active_satellites;          /* Кількість відстежуваних супутників */
    double estimated_drift_ppm;         /* Оцінена швидкість локального дрейфу */
} tt_diagnostics_t;
