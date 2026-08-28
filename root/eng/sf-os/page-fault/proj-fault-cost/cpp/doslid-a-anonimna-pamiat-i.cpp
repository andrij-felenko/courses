static void exp_anon() {
    mark m;
    std::cout << "A. анонімна пам'ять, 1 ГіБ = 262144 сторінок по 4 КіБ\n";

    mark_begin(m);
    char *p = static_cast<char*>(mmap(nullptr, ANON, PROT_READ | PROT_WRITE,
                                      MAP_PRIVATE | MAP_ANONYMOUS, -1, 0));
    mark_end(m, "mmap (ліниво)");

    madvise(p, ANON, MADV_NOHUGEPAGE);

    mark_begin(m); touch_seq(p, ANON, true); mark_end(m, "перший дотик");
    mark_begin(m); touch_seq(p, ANON, true); mark_end(m, "другий прохід");
    munmap(p, ANON);

    mark_begin(m);
    p = static_cast<char*>(mmap(nullptr, ANON, PROT_READ | PROT_WRITE,
                                MAP_PRIVATE | MAP_ANONYMOUS | MAP_POPULATE, -1, 0));
    mark_end(m, "mmap + MAP_POPULATE");
    mark_begin(m); touch_seq(p, ANON, true); mark_end(m, "перший дотик по ній");
    munmap(p, ANON);

    p = static_cast<char*>(mmap(nullptr, ANON, PROT_READ | PROT_WRITE,
                                MAP_PRIVATE | MAP_ANONYMOUS, -1, 0));
    madvise(p, ANON, MADV_NOHUGEPAGE);
    mark_begin(m);
    madvise(p, ANON, MADV_POPULATE_WRITE);
    mark_end(m, "madvise(MADV_POPULATE_WRITE)");
    munmap(p, ANON);
}
