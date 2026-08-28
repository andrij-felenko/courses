static int lab_flood(long fence)
{
    struct rlimit rl;
    getrlimit(RLIMIT_NPROC, &rl);
    printf("було: RLIMIT_NPROC м'який %ld, жорсткий %ld\n",
           (long)rl.rlim_cur, (long)rl.rlim_max);

    rl.rlim_cur = fence;                  /* власна огорожа, нижча за системну */
    if (setrlimit(RLIMIT_NPROC, &rl) < 0) { perror("setrlimit"); return 1; }
    printf("поставили собі: %ld\n", fence);

    int made = 0;
    for (;;) {
        pid_t p = fork();
        if (p == 0) _exit(0);
        if (p < 0) {
            int e = errno;
            printf("fork зупинився на %d зомбі: %s\n", made, strerror(e));
            break;
        }
        made++;
        wait_until_zombie(p);
    }
    if (made == 0)
        printf("огорожа нижча за поточне число процесів користувача — підніми її\n");

    int reaped = 0, status;
    while (waitpid(-1, &status, 0) > 0)
        reaped++;
    printf("прибрано: %d\n", reaped);
    return 0;
}
