#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

typedef struct {
    unsigned long mem_total_kb;
    unsigned long mem_free_kb;
    unsigned long mem_avail_kb;
    unsigned long dirty_kb;
    unsigned long sreclaim_kb;
    double psi_some_avg10;
    double psi_full_avg10;
} SysMemInfo;

typedef struct {
    pid_t pid;
    unsigned long vsz_kb;
    unsigned long rss_kb;
    unsigned long pss_kb;
    unsigned long priv_clean_kb;
    unsigned long priv_dirty_kb;
    unsigned long shared_clean_kb;
    unsigned long shared_dirty_kb;
    unsigned long swap_kb;
    unsigned long swap_pss_kb;
    int oom_score;
    int oom_score_adj;
} ProcMemInfo;

static int read_sys_mem(SysMemInfo *sys) {
    memset(sys, 0, sizeof(*sys));
    FILE *f = fopen("/proc/meminfo", "r");
    if (!f) return -1;

    char *line = NULL;
    size_t len = 0;
    while (getline(&line, &len, f) != -1) {
        sscanf(line, "MemTotal: %lu kB", &sys->mem_total_kb);
        sscanf(line, "MemFree: %lu kB", &sys->mem_free_kb);
        sscanf(line, "MemAvailable: %lu kB", &sys->mem_avail_kb);
        sscanf(line, "Dirty: %lu kB", &sys->dirty_kb);
        sscanf(line, "SReclaimable: %lu kB", &sys->sreclaim_kb);
    }
    free(line);
    fclose(f);

    FILE *psi = fopen("/proc/pressure/memory", "r");
    if (psi) {
        char buf[256];
        while (fgets(buf, sizeof(buf), psi)) {
            if (strncmp(buf, "some", 4) == 0) {
                sscanf(buf, "some avg10=%lf", &sys->psi_some_avg10);
            } else if (strncmp(buf, "full", 4) == 0) {
                sscanf(buf, "full avg10=%lf", &sys->psi_full_avg10);
            }
        }
        fclose(psi);
    }
    return 0;
}

static int read_proc_mem(pid_t pid, ProcMemInfo *proc) {
    memset(proc, 0, sizeof(*proc));
    proc->pid = pid;

    char path[128];
    snprintf(path, sizeof(path), "/proc/%d/smaps_rollup", pid);
    FILE *f = fopen(path, "r");
    if (!f) return -1;

    char *line = NULL;
    size_t len = 0;
    while (getline(&line, &len, f) != -1) {
        sscanf(line, "Rss: %lu kB", &proc->rss_kb);
        sscanf(line, "Pss: %lu kB", &proc->pss_kb);
        sscanf(line, "Private_Clean: %lu kB", &proc->priv_clean_kb);
        sscanf(line, "Private_Dirty: %lu kB", &proc->priv_dirty_kb);
        sscanf(line, "Shared_Clean: %lu kB", &proc->shared_clean_kb);
        sscanf(line, "Shared_Dirty: %lu kB", &proc->shared_dirty_kb);
        sscanf(line, "Swap: %lu kB", &proc->swap_kb);
        sscanf(line, "SwapPss: %lu kB", &proc->swap_pss_kb);
    }
    free(line);
    fclose(f);

    snprintf(path, sizeof(path), "/proc/%d/status", pid);
    f = fopen(path, "r");
    if (f) {
        line = NULL;
        len = 0;
        while (getline(&line, &len, f) != -1) {
            sscanf(line, "VmSize: %lu kB", &proc->vsz_kb);
        }
        free(line);
        fclose(f);
    }

    snprintf(path, sizeof(path), "/proc/%d/oom_score", pid);
    f = fopen(path, "r");
    if (f) {
        if (fscanf(f, "%d", &proc->oom_score) != 1) proc->oom_score = 0;
        fclose(f);
    }

    snprintf(path, sizeof(path), "/proc/%d/oom_score_adj", pid);
    f = fopen(path, "r");
    if (f) {
        if (fscanf(f, "%d", &proc->oom_score_adj) != 1) proc->oom_score_adj = 0;
        fclose(f);
    }
    return 0;
}

static void print_report(const SysMemInfo *sys, const ProcMemInfo *proc) {
    unsigned long uss_kb = proc->priv_clean_kb + proc->priv_dirty_kb;
    unsigned long shared_total_kb = proc->shared_clean_kb + proc->shared_dirty_kb;

    printf("===================================================================\n");
    printf("  ЗВЕДЕНИЙ ЗВІТ СПОЖИВАННЯ ПАМ'ЯТІ ДЛЯ PID %d\n", proc->pid);
    printf("===================================================================\n\n");

    printf("--- [1] СИСТЕМНИЙ КОНТЕКСТ (/proc/meminfo, PSI) ---\n");
    printf("  RAM Загалом:     %8lu МіБ | Вільна (Free):   %8lu МіБ\n",
           sys->mem_total_kb / 1024, sys->mem_free_kb / 1024);
    printf("  Доступна (Avail):%8lu МіБ | Брудна (Dirty):  %8lu МіБ\n",
           sys->mem_avail_kb / 1024, sys->dirty_kb / 1024);
    printf("  Slab (Reclaim):  %8lu МіБ | Тиск PSI (10с):  some=%.2f%% full=%.2f%%\n\n",
           sys->sreclaim_kb / 1024, sys->psi_some_avg10, sys->psi_full_avg10);

    printf("--- [2] СТАН АДРЕСНОГО ПРОСТОРУ ПРОЦЕСУ ---\n");
    printf("  VSZ (Віртуальний): %8lu МіБ  (повна довжина карти адрес VMA)\n", proc->vsz_kb / 1024);
    printf("  RSS (Резидентний): %8lu МіБ  (заселені сторінки в таблицях PTE)\n", proc->rss_kb / 1024);
    printf("  PSS (Пропорційний):%8lu МіБ  (чесна частка: USS + Shared / N)\n", proc->pss_kb / 1024);
    printf("  USS (Винятковий):  %8lu МіБ  (належить виключно цьому процесу)\n\n", uss_kb / 1024);

    printf("--- [3] РОЗКЛАДКА СТОРІНОК ЗА СТАТУСОМ ЗВІЛЬНЕННЯ ---\n");
    printf("  Приватні брудні (Private_Dirty): %8lu МіБ  [КУПА/СТЕК: вивільнення в RAM негайне]\n",
           proc->priv_dirty_kb / 1024);
    printf("  Приватні чисті  (Private_Clean): %8lu МіБ  [КОД/ФАЙЛИ: скидаються без запису]\n",
           proc->priv_clean_kb / 1024);
    printf("  Спільні сторінки (Shared Total): %8lu МіБ  [LIBC/SHMEM: спільні з іншими]\n",
           shared_total_kb / 1024);
    printf("  Витіснено в своп (Swap / SwapPSS):%7lu / %lu МіБ\n\n",
           proc->swap_kb / 1024, proc->swap_pss_kb / 1024);

    printf("--- [4] ОЦІНКА РИЗИКУ ТА ПОВЕДІНКИ OOM-KILLER ---\n");
    printf("  Поточний OOM Score:     %5d (бали ймовірності знищення: 0..1000)\n", proc->oom_score);
    printf("  Поправка OOM Score Adj: %5d (налаштування пріоритету: -1000..+1000)\n", proc->oom_score_adj);
    printf("  Реальний виграш від ліквідації: %lu МіБ фізичної RAM\n", proc->priv_dirty_kb / 1024);
    printf("===================================================================\n");
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <PID>\n", argv[0]);
        return 1;
    }

    pid_t pid = (pid_t)atoi(argv[1]);
    if (pid <= 0) {
        fprintf(stderr, "Помилка: некоректний PID %s\n", argv[1]);
        return 1;
    }

    SysMemInfo sys;
    if (read_sys_mem(&sys) != 0) {
        perror("Помилка читання /proc/meminfo");
        return 1;
    }

    ProcMemInfo proc;
    if (read_proc_mem(pid, &proc) != 0) {
        fprintf(stderr, "Помилка читання даних для PID %d: %s\n", pid, strerror(errno));
        return 1;
    }

    print_report(&sys, &proc);
    return 0;
}
