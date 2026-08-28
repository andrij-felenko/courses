int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "вжиток: %s <точка-монтування> <вікно-мс> [--sync]\n", argv[0]);
        return 2;
    }
    const char *mp = argv[1];
    unsigned window_ms = (unsigned)strtoul(argv[2], NULL, 10);
    int presync = (argc > 3 && strcmp(argv[3], "--sync") == 0);

    char probe[PATH_MAX];
    snprintf(probe, sizeof probe, "%s/freeze-probe.tmp", mp);

    int fd = open(mp, O_RDONLY | O_DIRECTORY);   /* дескриптор ТОЧКИ МОНТУВАННЯ */
    if (fd < 0) { perror("open точки монтування"); return 1; }

    pid_t writer = spawn_writer(probe);
    if (writer < 0) return 1;
    pid_t dog = spawn_watchdog(mp, window_ms + 5000);   /* СТОРОЖ — ДО заморожування */
    if (dog < 0) { kill(writer, SIGKILL); waitpid(writer, NULL, 0); return 1; }

    struct timespec warmup = { 0, 200000000L };
    nanosleep(&warmup, NULL);                    /* дати писареві розігнатися */

    if (presync) syncfs(fd);                     /* виносимо масу брудних сторінок ЗА вікно */

    double t0 = now_ms();
    if (ioctl(fd, FIFREEZE, 0) < 0) {
        fprintf(stderr, "FIFREEZE: %s\n", strerror(errno));
        kill(dog, SIGKILL); kill(writer, SIGKILL);
        return 1;
    }
    double t1 = now_ms();

    /* ═══ ВІКНО. Сюди підставляють знімок. Писати в цю ФС не можна нічого. ═══ */
    struct timespec hold = { window_ms / 1000,
                             (long)(window_ms % 1000) * 1000000L };
    nanosleep(&hold, NULL);

    double t2 = now_ms();
    int thawed = (ioctl(fd, FITHAW, 0) == 0);
    double t3 = now_ms();
    if (!thawed) fprintf(stderr, "FITHAW: %s\n", strerror(errno));

    if (thawed) kill(dog, SIGKILL);   /* сторожа знімаємо ЛИШЕ після успішного відтавання */

    fprintf(stderr, "FIFREEZE %.1f мс | утримання %.1f мс | FITHAW %.1f мс | вікно %.1f мс\n",
            t1 - t0, t2 - t1, t3 - t2, t3 - t0);

    kill(writer, SIGTERM);
    waitpid(writer, NULL, 0);
    waitpid(dog, NULL, 0);
    unlink(probe);
    close(fd);
    return 0;
}
