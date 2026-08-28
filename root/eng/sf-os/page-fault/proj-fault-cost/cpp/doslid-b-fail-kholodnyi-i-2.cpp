static void exp_willneed(int fd) {
    mark m;
    std::size_t n = FSIZE / PGSZ;
    chill(fd);
    char *p = static_cast<char*>(mmap(nullptr, FSIZE, PROT_READ, MAP_PRIVATE, fd, 0));

    mark_begin(m);
    madvise(p, FSIZE, MADV_WILLNEED);
    mark_end(m, "madvise(MADV_WILLNEED)");

    double t0 = now();
    while (resident(p, FSIZE) < n && now() - t0 < 5.0) {
        struct timespec ts{0, 1000000};
        nanosleep(&ts, nullptr);
    }
    std::cout << "  прогрівання: " << std::fixed << std::setprecision(1)
              << ((now() - t0) * 1e3) << " мс, резидентних " << resident(p, FSIZE) << " з " << n << "\n";

    mark_begin(m); touch_seq(p, FSIZE, false); mark_end(m, "  обхід");
    munmap(p, FSIZE);
}
