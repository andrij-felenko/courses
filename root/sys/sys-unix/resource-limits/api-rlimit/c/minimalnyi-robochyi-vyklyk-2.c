/* Довести м'який ліміт щонайменше до `want`, не вище виданої стелі.
   Повертає 0, якщо після виклику межа не менша за want, 1 — якщо стеля нижча. */
static int raise_soft(int resource, rlim_t want)
{
    struct rlimit rl;

    if (prlimit(0, resource, NULL, &rl) != 0)
        return -1;
    if (rl.rlim_cur == RLIM_INFINITY || rl.rlim_cur >= want)
        return 0;                       /* уже досить, нічого не робимо */

    int capped = 0;
    if (rl.rlim_max != RLIM_INFINITY && rl.rlim_max < want) {
        want = rl.rlim_max;             /* вище жорсткого не стрибнемо */
        capped = 1;
    }
    rl.rlim_cur = want;
    if (prlimit(0, resource, &rl, NULL) != 0)
        return -1;
    return capped;
}
