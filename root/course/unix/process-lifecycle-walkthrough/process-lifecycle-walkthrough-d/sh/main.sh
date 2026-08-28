sudo bpftrace -e '
tracepoint:sched:sched_process_fork {
    printf("[FORK] Батько %s (%d) породив дитину %s (%d)\n",
           args->parent_comm, args->parent_pid, args->child_comm, args->child_pid);
}
tracepoint:sched:sched_process_exec {
    printf("[EXEC] Процес %d запустив файл %s\n", pid, args->filename);
}
tracepoint:sched:sched_process_exit {
    printf("[EXIT] Процес %s (%d) завершується (код %d)\n",
           comm, pid, curtask->exit_code >> 8);
}
tracepoint:sched:sched_process_free {
    printf("[FREE] Дескриптор task_struct процесу %d остаточно знищено (reaped)\n",
           args->pid);
}'
