typedef struct {
    uint64_t total_added;     /* Загальна кількість запланованих таймерів */
    uint64_t total_cancelled; /* Кількість скасованих таймерів */
    uint64_t total_expired;   /* Кількість виконаних таймерів */
    uint64_t total_cascaded;  /* Кількість елементів, що пройшли каскадування */
    uint32_t active_count;    /* Кількість активних таймерів у системі */
} timer_wheel_stats_t;

tw_status_t timer_wheel_get_stats(
    const timer_wheel_t *wheel,
    timer_wheel_stats_t *out_stats
);
