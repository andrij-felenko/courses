struct psi_group {
    /* Попроцесорні масиви лічильників */
    struct psi_group_cpu __percpu *pcpu;

    /* Фоновий таймер обчислення згладжених метрик */
    struct timer_list poll_timer;
    u64 poll_min_update;

    /* Збережені згладжені значення avg10, avg60, avg300 */
    unsigned long avg[NR_PSI_STATES][3];
    u64 total[NR_PSI_STATES];

    /* Список зареєстрованих користувацьких тригерів */
    struct list_head triggers;
    u32 trigger_mask;
};
