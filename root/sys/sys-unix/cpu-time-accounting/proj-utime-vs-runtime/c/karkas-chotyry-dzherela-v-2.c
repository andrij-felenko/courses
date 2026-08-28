/* Джерело 1: точна сума планувальника, наносекунди, без жодної вибірки. */
static double cpu_clock(clockid_t id)
{
    struct timespec ts;
    if (clock_gettime(id, &ts) < 0) return -1.0;
    return (double)ts.tv_sec + ts.tv_nsec / 1e9;
}

/* Джерело 2: поділ на режими в мікросекундах. */
static void rusage_pair(int who, double *u, double *s)
{
    struct rusage r;
    if (getrusage(who, &r) < 0) { *u = *s = -1.0; return; }
    *u = (double)r.ru_utime.tv_sec + r.ru_utime.tv_usec / 1e6;
    *s = (double)r.ru_stime.tv_sec + r.ru_stime.tv_usec / 1e6;
}

/* Джерело 3: поля 14 і 15 у stat — той самий поділ, але в тиках USER_HZ.
   Розбирати можна лише від ОСТАННЬОЇ дужки: друге поле — ім'я команди,
   і ядро друкує його як є, разом із пробілами й дужками всередині. */
static int proc_stat_cpu(const char *path, double *u, double *s)
{
    char buf[1024];
    if (slurp(path, buf, sizeof buf) < 0) return -1;
    char *p = strrchr(buf, ')');
    if (!p) return -1;

    unsigned long ut = 0, st = 0;
    /* після "») " ідуть поля 3…: state ppid pgrp session tty tpgid flags
       minflt cminflt majflt cmajflt utime stime */
    if (sscanf(p + 2, "%*c %*d %*d %*d %*d %*d %*u %*lu %*lu %*lu %*lu %lu %lu",
               &ut, &st) != 2) return -1;
    *u = ut / clk_tck();
    *s = st / clk_tck();
    return 0;
}

/* Джерело 4: перше число schedstat — se.sum_exec_runtime у наносекундах,
   узяте з поля задачі як є. Файл існує лише при CONFIG_SCHED_INFO;
   немає файлу — немає числа, і це НЕ те саме, що нуль. */
static int proc_runtime(const char *path, double *rt)
{
    char buf[128];
    if (slurp(path, buf, sizeof buf) < 0) return -1;
    unsigned long long ns = 0;
    if (sscanf(buf, "%llu", &ns) != 1) return -1;
    *rt = ns / 1e9;
    return 0;
}
