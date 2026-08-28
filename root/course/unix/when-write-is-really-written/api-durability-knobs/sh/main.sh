# Підрахунок кількості викликів fsync/fdatasync за процесами
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_fsync,tracepoint:syscalls:sys_enter_fdatasync { @[comm, probe] = count(); }'

# Фіксація блокових запитів із прапорцями PREFLUSH та FUA
sudo bpftrace -e '
tracepoint:block:block_rq_issue {
    $is_flush = args->rwbs & 1; // бітовий прапорець FLUSH/FUA
    if ($is_flush) {
        printf("PID %d (%s) -> Пристрій %s: Операція %s, Сектор %llu, Розмір %u байтів\n",
               pid, comm, args->dev, args->rwbs, args->sector, args->nr_bytes);
    }
}'
