siginfo_t {
    int          si_signo;   /* номер сигналу — той самий, що в першому аргументі */
    int          si_errno;   /* errno події, якщо ядро його дає; здебільшого 0     */
    int          si_code;    /* ХТО або ЩО породило сигнал                          */
    pid_t        si_pid;     /* pid відправника   (SI_USER, SI_QUEUE, SI_TKILL, SIGCHLD) */
    uid_t        si_uid;     /* реальний uid відправника                            */
    int          si_status;  /* код виходу або номер сигналу нащадка      (SIGCHLD) */
    void        *si_addr;    /* адреса збою  (SIGSEGV, SIGBUS, SIGILL, SIGFPE, SIGTRAP) */
    union sigval si_value;   /* значення від sigqueue(3): .sival_int / .sival_ptr   */
    long         si_band;    /* яка саме подія вводу-виводу      (SIGIO / SIGPOLL)  */
    int          si_fd;      /* дескриптор                       (SIGIO / SIGPOLL)  */
}
