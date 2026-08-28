/* 1. poll() справді спить, доки огорожа стоїть */
static void demo_wakeup(void)
{
        struct timespec t0, t1;
        int tl = timeline_open();
        int f  = fence_create(tl, 1);
        struct pollfd p = { .fd = f, .events = POLLIN };
        pid_t kid;

        printf("щойно створена: готова=%d\n", fence_ready(f));

        clock_gettime(CLOCK_MONOTONIC, &t0);
        kid = fork();
        if (kid < 0)
                die("fork");
        if (kid == 0) {                  /* дитина успадкувала дескриптор шкали */
                usleep(300 * 1000);
                timeline_inc(tl, 1);
                _exit(0);
        }

        if (poll(&p, 1, 5000) != 1)      /* ось тут потік справді спить */
                die("poll не дочекався");
        clock_gettime(CLOCK_MONOTONIC, &t1);
        printf("прокинувся через %.0f мс, revents=0x%x\n",
               (t1.tv_sec - t0.tv_sec) * 1e3 + (t1.tv_nsec - t0.tv_nsec) / 1e6,
               p.revents);

        waitpid(kid, NULL, 0);
        close(f);
        close(tl);
}

/* 2. злита огорожа падає разом з ОСТАННЬОЮ */
static void demo_merge(void)
{
        int a = timeline_open(), b = timeline_open();   /* два різні контексти */
        int fa = fence_create(a, 5), fb = fence_create(b, 3);
        int fm = fence_merge("a+b", fa, fb);

        fence_info("злита:", fm);
        printf("спокій:      A=%d B=%d злита=%d\n",
               fence_ready(fa), fence_ready(fb), fence_ready(fm));
        timeline_inc(a, 5);
        printf("після INC A: A=%d B=%d злита=%d\n",
               fence_ready(fa), fence_ready(fb), fence_ready(fm));
        timeline_inc(b, 3);
        printf("після INC B: A=%d B=%d злита=%d\n",
               fence_ready(fa), fence_ready(fb), fence_ready(fm));
        fence_info("злита:", fm);

        close(fm); close(fb); close(fa); close(b); close(a);
}

/* 3. дві огорожі однієї шкали злиття згортає в одну */
static void demo_same_context(void)
{
        int tl = timeline_open();
        int f7 = fence_create(tl, 7), f9 = fence_create(tl, 9);
        int fm = fence_merge("c7+c9", f7, f9);

        fence_info("один контекст:", fm);
        close(fm); close(f9); close(f7); close(tl);
}

/* 4. шкала пішла — огорожа однаково падає, але з помилкою */
static void demo_release(void)
{
        int tl = timeline_open();
        int f  = fence_create(tl, 1);

        close(tl);                       /* «залізо» зникло, не дійшовши до 1 */
        printf("шкали більше немає: готова=%d\n", fence_ready(f));
        fence_info("сирота:", f);
        close(f);
}

int main(void)
{
        demo_wakeup();
        demo_merge();
        demo_same_context();
        demo_release();
        return 0;
}
