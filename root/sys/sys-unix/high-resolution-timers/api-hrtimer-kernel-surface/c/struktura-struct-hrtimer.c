struct hrtimer {
    struct timerqueue_node  node;
    ktime_t                 _softexpires;
    enum hrtimer_restart    (*function)(struct hrtimer *);
    struct hrtimer_clock_base *base;
    u8                      state;
    u8                      is_rel;
    u8                      is_soft;
    u8                      is_hard;
};
