#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>
#include <errno.h>

typedef struct {
    int pid;
    char comm[256];
    char state;
    int ppid;
    unsigned long utime;
    unsigned long stime;
    double utime_sec;
    double stime_sec;
    unsigned long vsize;
    long rss_pages;
    unsigned long long rss_bytes;
} proc_stat_t;

bool parse_proc_stat(const char *filepath, proc_stat_t *out_stat) {
    if (!filepath || !out_stat) return false;

    FILE *fp = fopen(filepath, "r");
    if (!fp) {
        perror("Помилка відкриття файлу proc stat");
        return false;
    }

    char buffer[2048];
    if (!fgets(buffer, sizeof(buffer), fp)) {
        fclose(fp);
        return false;
    }
    fclose(fp);

    // 1. Знаходимо першу відкриваючу дужку '(' та останню закриваючу ')'
    char *open_paren = strchr(buffer, '(');
    char *close_paren = strrchr(buffer, ')');

    if (!open_paren || !close_paren || close_paren <= open_paren) {
        return false;
    }

    // 2. Зчитуємо PID до першої дужки
    out_stat->pid = atoi(buffer);

    // 3. Зчитуємо comm між '(' та ')'
    size_t comm_len = close_paren - (open_paren + 1);
    if (comm_len >= sizeof(out_stat->comm)) {
        comm_len = sizeof(out_stat->comm) - 1;
    }
    strncpy(out_stat->comm, open_paren + 1, comm_len);
    out_stat->comm[comm_len] = '\0';

    // 4. Зчитуємо решту полів після останньої дужки ')'
    char *after_comm = close_paren + 1;

    int parsed = sscanf(after_comm,
                        " %c %d %*d %*d %*d %*d %*u %*u %*u %*u %*u %lu %lu %*d %*d %*d %*d %*d %*d %*llu %lu %ld",
                        &out_stat->state,
                        &out_stat->ppid,
                        &out_stat->utime,
                        &out_stat->stime,
                        &out_stat->vsize,
                        &out_stat->rss_pages);

    if (parsed != 6) {
        return false;
    }

    // 5. Конвертуємо тики годинника у секунди та сторінки у байти
    long clock_ticks = sysconf(_SC_CLK_TCK);
    if (clock_ticks <= 0) clock_ticks = 100;

    long page_size = sysconf(_SC_PAGESIZE);
    if (page_size <= 0) page_size = 4096;

    out_stat->utime_sec = (double)out_stat->utime / clock_ticks;
    out_stat->stime_sec = (double)out_stat->stime / clock_ticks;
    out_stat->rss_bytes = (unsigned long long)out_stat->rss_pages * page_size;

    return true;
}

int main(void) {
    proc_stat_t st;
    if (parse_proc_stat("/proc/self/stat", &st)) {
        printf("--- Результат розбору /proc/self/stat (C) ---\n");
        printf("PID:               %d\n", st.pid);
        printf("Comm:              %s\n", st.comm);
        printf("State:             %c\n", st.state);
        printf("PPID:              %d\n", st.ppid);
        printf("User Time:         %.2f sec (%lu ticks)\n", st.utime_sec, st.utime);
        printf("System Time:       %.2f sec (%lu ticks)\n", st.stime_sec, st.stime);
        printf("Virtual Memory:    %.2f MB (%lu bytes)\n", (double)st.vsize / (1024 * 1024), st.vsize);
        printf("RSS Memory:        %.2f MB (%llu bytes)\n", (double)st.rss_bytes / (1024 * 1024), st.rss_bytes);
    } else {
        fprintf(stderr, "Помилка парсингу /proc/self/stat\n");
        return 1;
    }
    return 0;
}
