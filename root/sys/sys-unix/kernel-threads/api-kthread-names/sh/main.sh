# відстежити, які саме функції виконуються у kworker та скільки часу вони займають
sudo bpftrace -e '
tracepoint:workqueue:workqueue_execute_start {
    @start[args->work] = nsecs;
}
tracepoint:workqueue:workqueue_execute_end {
    $duration = (nsecs - @start[args->work]) / 1000;
    @us[ksym(args->function)] = hist($duration);
    delete(@start[args->work]);
}'
