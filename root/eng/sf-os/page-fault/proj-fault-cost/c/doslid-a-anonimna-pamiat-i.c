static void exp_anon(void)
{
    struct mark m;
    char *p;

    puts("A. анонімна пам'ять, 1 ГіБ = 262144 сторінок по 4 КіБ");

    mark_begin(&m);
    p = mmap(NULL, ANON, PROT_READ | PROT_WRITE,
             MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    mark_end(&m, "mmap (ліниво)");

    /* Прибиваємо великі сторінки: інакше збоїв буде 512, а не 262144,
       і дослід міряв би налаштування машини, а не сторінковий збій. */
    madvise(p, ANON, MADV_NOHUGEPAGE);

    mark_begin(&m); touch_seq(p, ANON, 1); mark_end(&m, "перший дотик");
    mark_begin(&m); touch_seq(p, ANON, 1); mark_end(&m, "другий прохід");
    munmap(p, ANON);

    mark_begin(&m);
    p = mmap(NULL, ANON, PROT_READ | PROT_WRITE,
             MAP_PRIVATE | MAP_ANONYMOUS | MAP_POPULATE, -1, 0);
    mark_end(&m, "mmap + MAP_POPULATE");
    mark_begin(&m); touch_seq(p, ANON, 1); mark_end(&m, "перший дотик по ній");
    munmap(p, ANON);

    p = mmap(NULL, ANON, PROT_READ | PROT_WRITE,
             MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    madvise(p, ANON, MADV_NOHUGEPAGE);
    mark_begin(&m);
    madvise(p, ANON, MADV_POPULATE_WRITE);
    mark_end(&m, "madvise(MADV_POPULATE_WRITE)");
    munmap(p, ANON);
}
