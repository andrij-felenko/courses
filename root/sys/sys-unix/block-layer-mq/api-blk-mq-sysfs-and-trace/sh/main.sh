sudo bpftrace -e '
tracepoint:block:block_rq_issue
{
    @start[args->dev, args->sector] = nsecs;
}

tracepoint:block:block_rq_complete
/@start[args->dev, args->sector]/
{
    $lat_us = (nsecs - @start[args->dev, args->sector]) / 1000;
    @latency_us = hist($lat_us);
    delete(@start[args->dev, args->sector]);
}

END
{
    clear(@start);
}
'
