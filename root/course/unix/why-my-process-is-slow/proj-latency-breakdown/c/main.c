#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>

typedef struct {
    unsigned long long utime_ticks;
    unsigned long long stime_ticks;
    unsigned long long minflt;
    unsigned long long majflt;
    unsigned long long sched_cpu_ns;
    unsigned long long sched_wait_ns;
    unsigned long long sched_switches;
    unsigned long long vol_ctxt;
    unsigned long long nonvol_ctxt;
    struct timespec timestamp;
} ProcessMetrics;

static double timespec_diff_sec(const struct timespec *start, const struct timespec *end) {
    return (double)(end->tv_sec - start->tv_sec) +
           (double)(end->tv_nsec - start->tv_nsec) / 1e9;
}

static int read_proc_stat(pid_t pid, ProcessMetrics *m) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/stat", pid);
    FILE *f = fopen(path, "r");
    if (!f) return -1;

    char buffer[2048];
    if (!fgets(buffer, sizeof(buffer), f)) {
        fclose(f);
        return -1;
    }
    fclose(f);

    /* Знаходимо останню закриваючу дужку для безпечного парсингу після назви процесу */
    char *paren = strrchr(buffer, ')');
    if (!paren) return -1;

    char state;
    int ppid, pgrp, session, tty_nr, tpgid;
    unsigned int flags;

    int matched = sscanf(paren + 2,
        "%c %d %d %d %d %d %u %llu %*u %llu %*u %llu %llu",
        &state, &ppid, &pgrp, &session, &tty_nr, &tpgid,
        &flags, &m->minflt, &m->majflt, &m->utime_ticks, &m->stime_ticks);

    return (matched >= 11) ? 0 : -1;
}

static int read_proc_schedstat(pid_t pid, ProcessMetrics *m) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/schedstat", pid);
    FILE *f = fopen(path, "r");
    if (!f) return -1;

    int matched = fscanf(f, "%llu %llu %llu",
                         &m->sched_cpu_ns, &m->sched_wait_ns, &m->sched_switches);
    fclose(f);
    return (matched == 3) ? 0 : -1;
}

static int read_proc_status(pid_t pid, ProcessMetrics *m) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/status", pid);
    FILE *f = fopen(path, "r");
    if (!f) return -1;

    char line[256];
    m->vol_ctxt = 0;
    m->nonvol_ctxt = 0;

    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "voluntary_ctxt_switches:", 24) == 0) {
            sscanf(line + 24, "%llu", &m->vol_ctxt);
        } else if (strncmp(line, "nonvoluntary_ctxt_switches:", 27) == 0) {
            sscanf(line + 27, "%llu", &m->nonvol_ctxt);
        }
    }
    fclose(f);
    return 0;
}

static int collect_metrics(pid_t pid, ProcessMetrics *m) {
    if (read_proc_stat(pid, m) != 0) return -1;
    if (read_proc_schedstat(pid, m) != 0) {
        m->sched_cpu_ns = 0;
        m->sched_wait_ns = 0;
        m->sched_switches = 0;
    }
    if (read_proc_status(pid, m) != 0) return -1;
    clock_gettime(CLOCK_MONOTONIC, &m->timestamp);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <PID> [інтервал_секунд]\n", argv[0]);
        return 1;
    }

    pid_t pid = (pid_t)atoi(argv[1]);
    int interval_sec = (argc >= 3) ? atoi(argv[2]) : 1;
    if (interval_sec < 1) interval_sec = 1;

    long clk_tck = sysconf(_SC_CLK_TCK);
    if (clk_tck <= 0) clk_tck = 100;

    ProcessMetrics prev, curr;
    if (collect_metrics(pid, &prev) != 0) {
        fprintf(stderr, "Помилка доступу до процесу з PID %d: %s\n", pid, strerror(errno));
        return 1;
    }

    printf("Моніторинг бюджету часу для PID %d (CLK_TCK=%ld, інтервал=%d с)...\n",
           pid, clk_tck, interval_sec);
    printf("--------------------------------------------------------------------------------\n");

    while (1) {
        sleep((unsigned int)interval_sec);
        if (collect_metrics(pid, &curr) != 0) {
            printf("Процес %d завершився або став недоступним.\n", pid);
            break;
        }

        double dt = timespec_diff_sec(&prev.timestamp, &curr.timestamp);
        if (dt <= 0.0) dt = 0.001;

        double utime_sec = (double)(curr.utime_ticks - prev.utime_ticks) / (double)clk_tck;
        double stime_sec = (double)(curr.stime_ticks - prev.stime_ticks) / (double)clk_tck;
        double sched_wait_sec = (double)(curr.sched_wait_ns - prev.sched_wait_ns) / 1e9;
        
        double cpu_total_sec = utime_sec + stime_sec;
        double off_cpu_sec = dt - cpu_total_sec - sched_wait_sec;
        if (off_cpu_sec < 0.0) off_cpu_sec = 0.0;

        double user_pct = (utime_sec / dt) * 100.0;
        double sys_pct  = (stime_sec / dt) * 100.0;
        double wait_pct = (sched_wait_sec / dt) * 100.0;
        double off_pct  = (off_cpu_sec / dt) * 100.0;

        unsigned long long vol_diff = curr.vol_ctxt - prev.vol_ctxt;
        unsigned long long nonvol_diff = curr.nonvol_ctxt - prev.nonvol_ctxt;
        unsigned long long minflt_diff = curr.minflt - prev.minflt;
        unsigned long long majflt_diff = curr.majflt - prev.majflt;

        printf("[Δt=%.2fs] CPU: usr=%.1f%% sys=%.1f%% | SchedWait=%.1f%% | OffCPU=%.1f%% | Ctxt: vol=%llu/s nonvol=%llu/s | Flt: min=%llu maj=%llu\n",
               dt, user_pct, sys_pct, wait_pct, off_pct,
               (unsigned long long)(vol_diff / dt),
               (unsigned long long)(nonvol_diff / dt),
               minflt_diff, majflt_diff);

        /* Автоматична діагностика вузького місця */
        if (user_pct > 60.0) {
            printf("  ↳ ДІАГНОЗ: CPU-Bound (User). Гарячі цикли або обчислення в коді програми.\n");
        } else if (sys_pct > 40.0) {
            printf("  ↳ ДІАГНОЗ: System-Bound. Надмірна кількість системних викликів або сторінкових збоїв.\n");
        } else if (wait_pct > 20.0) {
            printf("  ↳ ДІАГНОЗ: Scheduler Starvation. Процес чекає черги до процесора через нестачу ядер.\n");
        } else if (majflt_diff > 10) {
            printf("  ↳ ДІАГНОЗ: Paging / Swap Bottleneck. Часті значні сторінкові збої з диска.\n");
        } else if (off_pct > 70.0 && vol_diff > 1000) {
            printf("  ↳ ДІАГНОЗ: High Concurrency / I/O Blocking. Часті добровільні блокування на сокетах або м'ютексах.\n");
        } else if (off_pct > 70.0) {
            printf("  ↳ ДІАГНОЗ: Idle / Sleep. Процес здебільшого спить або чекає зовнішніх подій.\n");
        }

        prev = curr;
    }

    return 0;
}
