typedef struct {
    const char     *name;
    int64_t         period_ns;
    struct timespec due;           /* АБСОЛЮТНИЙ наступний строк, CLOCK_MONOTONIC */
    void          (*run)(void);
} job;

static job    *heap[4096];
static size_t  hn;

static int ts_before(struct timespec a, struct timespec b)
{
    return a.tv_sec != b.tv_sec ? a.tv_sec < b.tv_sec : a.tv_nsec < b.tv_nsec;
}

static void sift_up(size_t i)
{
    while (i && ts_before(heap[i]->due, heap[(i - 1) / 2]->due)) {
        job *t = heap[i]; heap[i] = heap[(i - 1) / 2]; heap[(i - 1) / 2] = t;
        i = (i - 1) / 2;
    }
}

static void sift_down(size_t i)
{
    for (;;) {
        size_t l = 2 * i + 1, r = l + 1, m = i;
        if (l < hn && ts_before(heap[l]->due, heap[m]->due)) m = l;
        if (r < hn && ts_before(heap[r]->due, heap[m]->due)) m = r;
        if (m == i) return;
        job *t = heap[i]; heap[i] = heap[m]; heap[m] = t;
        i = m;
    }
}

static void heap_push(job *j) { heap[hn] = j; hn++; sift_up(hn - 1); }

static void arm_head(int tfd)
{
    struct itimerspec its = {0};                  /* it_interval = 0 → строк одноразовий */
    if (hn == 0) { timerfd_settime(tfd, 0, &its, NULL); return; }   /* {0,0} роззброює */

    its.it_value = heap[0]->due;
    if (its.it_value.tv_sec == 0 && its.it_value.tv_nsec == 0)
        its.it_value.tv_nsec = 1;                 /* рівний нуль означав би «роззброїти» */
    timerfd_settime(tfd, TFD_TIMER_ABSTIME, &its, NULL);
}

static void timer_ready(int tfd)
{
    uint64_t ticks;
    if (read(tfd, &ticks, sizeof ticks) != (ssize_t)sizeof ticks && errno != EAGAIN)
        perror("read(timerfd)");

    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);

    while (hn && !ts_before(now, heap[0]->due)) {          /* поки корінь уже дозрів */
        job *j = heap[0];
        j->run();
        do  j->due = ts_add_ns(j->due, j->period_ns);      /* фаза — від НОМІНАЛУ */
        while (!ts_before(now, j->due));                   /* політика «пропустити» */
        sift_down(0);
    }
    arm_head(tfd);
}
