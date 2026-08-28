TRACE_EVENT(sched_switch,
    TP_PROTO(bool preempt, struct task_struct *prev, struct task_struct *next),
    TP_ARGS(preempt, prev, next),

    TP_STRUCT__entry(
        __array( char, prev_comm, TASK_COMM_LEN )
        __field( pid_t, prev_pid )
        __field( pid_t, next_pid )
    ),

    TP_fast_assign(
        memcpy(__entry->prev_comm, prev->comm, TASK_COMM_LEN);
        __entry->prev_pid = prev->pid;
        __entry->next_pid = next->pid;
    ),

    TP_printk("prev_comm=%s prev_pid=%d ==> next_pid=%d",
        __entry->prev_comm, __entry->prev_pid, __entry->next_pid)
);
