struct trace_event_raw_sched_switch {
    struct trace_entry ent;        /* Загальний заголовок події ftrace (4 байти) */
    char prev_comm[16];
    pid_t prev_pid;
    int prev_prio;
    long prev_state;
    char next_comm[16];
    pid_t next_pid;
    int next_prio;
    char __data[];                 /* Область для динамічних рядків змінної довжини */
};
