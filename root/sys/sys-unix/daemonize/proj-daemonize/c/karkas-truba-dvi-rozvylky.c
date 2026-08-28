static void parent_wait_and_exit(int rfd, pid_t mid)
{
    struct ready_msg m;
    ssize_t n;

    do {
        n = read(rfd, &m, sizeof m);
    } while (n < 0 && errno == EINTR);     /* сигнал не має ламати очікування */

    int st = 0;
    (void)waitpid(mid, &st, 0);            /* B — ще наша дитина, заберемо код */

    if (n == (ssize_t)sizeof m && m.tag == 'R')
        _exit(0);                          /* єдиний шлях до нуля */

    if (n == (ssize_t)sizeof m && m.tag == 'E')
        fprintf(stderr, "служба не піднялася на кроці «%s»: %s\n",
                m.stage, strerror(m.err));
    else if (n == 0)
        fprintf(stderr, "служба померла на старті, нічого не сказавши\n");
    else
        fprintf(stderr, "невиразна відповідь від служби\n");

    fflush(stderr);
    _exit(1);
}
