struct tick_sched {
    struct hrtimer          sched_timer;
    enum tick_nohz_mode     nohz_mode;
    ktime_t                 last_tick;
    ktime_t                 next_tick;
    unsigned int            inidle      : 1;
    unsigned int            tick_stopped: 1;
    unsigned long           idle_jiffies;
    unsigned long           idle_calls;
    unsigned long           idle_sleeps;
    ktime_t                 idle_entrytime;
    atomic_t                tick_dep_mask;
    unsigned long           check_clocks;
};
