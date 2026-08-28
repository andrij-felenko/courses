struct psi_group_cpu {
    /* Кількість потоків у кожному стані на цьому CPU */
    unsigned int tasks[NR_PSI_TASK_COUNTS];

    /* Бітова маска активних станів тиску */
    u32 state_mask;

    /* Часові мітки та накопичений час у мікросекундах */
    u64 state_start;
    u64 times[NR_PSI_STATES];
};
