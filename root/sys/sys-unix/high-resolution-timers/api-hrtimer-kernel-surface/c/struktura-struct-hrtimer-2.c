struct hrtimer_clock_base {
    struct hrtimer_cpu_base *cpu_base;
    unsigned int            index;
    clockid_t               clockid;
    seqcount_raw_spinlock_t seq;
    struct hrtimer          *running;
    struct timerqueue_head  active;
    ktime_t                 (*get_time)(void);
    ktime_t                 offset;
};
