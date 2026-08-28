siginfo_t si;
si.si_pid = 0;                 /* переносний спосіб побачити «нікого» */

if (waitid(P_PID, child, &si, WEXITED | WNOHANG) < 0) {
    perror("waitid");          /* −1: справжня помилка */
} else if (si.si_pid == 0) {
    /* нуль і порожній si_pid: дитина ще жива, це не помилка */
} else if (si.si_code == CLD_EXITED) {
    printf("код %d\n", si.si_status);
} else {
    printf("сигнал %d, причина %d\n", si.si_status, si.si_code);
}
