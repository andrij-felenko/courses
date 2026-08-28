# Трасування всіх поданих SQE та їхніх результатів за допомогою bpftrace
$ sudo bpftrace -e '
tracepoint:io_uring:io_uring_submit_sqe {
    @start[args->user_data] = nsecs;
}
tracepoint:io_uring:io_uring_complete {
    $dur = nsecs - @start[args->user_data];
    @latency_us = hist($dur / 1000);
    delete(@start[args->user_data]);
}'
