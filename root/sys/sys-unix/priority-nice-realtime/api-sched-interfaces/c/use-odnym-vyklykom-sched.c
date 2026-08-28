struct sched_attr {
    __u32 size;              /* sizeof(struct sched_attr) — заповнити обов'язково */
    __u32 sched_policy;      /* SCHED_*                                            */
    __u64 sched_flags;       /* SCHED_FLAG_*                                       */
    __s32 sched_nice;        /* −20 … 19                                           */
    __u32 sched_priority;    /* 1 … 99                                             */
    __u64 sched_runtime;     /* нс                                                 */
    __u64 sched_deadline;    /* нс                                                 */
    __u64 sched_period;      /* нс                                                 */
    __u32 sched_util_min;    /* 0 … 1024 — підказка про завантаження               */
    __u32 sched_util_max;
};
