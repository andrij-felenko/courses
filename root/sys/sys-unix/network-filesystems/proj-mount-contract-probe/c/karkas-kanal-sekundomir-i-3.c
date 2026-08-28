static long rpc(const char *fmt, ...)
{
    char    req[2048], resp[2048];
    long    v;
    int     e;
    va_list ap;

    va_start(ap, fmt);
    vsnprintf(req, sizeof req, fmt, ap);
    va_end(ap);

    if (send_line(req) < 0 || recv_line(resp, sizeof resp) < 0) {
        fprintf(stderr, "керувальний канал обірвався на «%s»\n", req);
        exit(2);
    }
    if (sscanf(resp, "OK %ld",  &v) == 1) return v;
    if (sscanf(resp, "ERR %d",  &e) == 1) return -(long) e;
    fprintf(stderr, "незрозуміла відповідь: «%s»\n", resp);
    exit(2);
}
