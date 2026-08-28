bpftrace -e '
tracepoint:fuse:fuse_request_send {
  @op[args->unique] = args->opcode;
  @t0[args->unique] = nsecs;
}
tracepoint:fuse:fuse_request_end /@t0[args->unique]/ {
  $op = @op[args->unique];
  @us[$op]    = hist((nsecs - @t0[args->unique]) / 1000);
  @bytes[$op] = sum(args->len);
  delete(@t0, args->unique); delete(@op, args->unique);
}'
