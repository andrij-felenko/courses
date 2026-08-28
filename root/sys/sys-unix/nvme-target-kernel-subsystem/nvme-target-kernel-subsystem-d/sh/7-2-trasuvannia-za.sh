# Вимірювання затримки виконання команд у мікросекундах через eBPF.
# Обидві точки трасування віддають ctrl_id, qid і cid — цієї трійки досить,
# щоб звести початок і завершення однієї й тієї самої команди.
bpftrace -e '
tracepoint:nvmet:nvmet_req_init {
    @start[args->ctrl_id, args->qid, args->cid] = nsecs;
}
tracepoint:nvmet:nvmet_req_complete /@start[args->ctrl_id, args->qid, args->cid]/ {
    $lat = (nsecs - @start[args->ctrl_id, args->qid, args->cid]) / 1000;
    @us = hist($lat);
    delete(@start[args->ctrl_id, args->qid, args->cid]);
}'
