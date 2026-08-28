#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <sys/types.h>
#include <limits.h>

// Структура для збереження метрик процесу
typedef struct {
    pid_t pid;
    char comm[256];
    char state;
    pid_t ppid;
    unsigned long utime;
    unsigned long stime;
    long num_threads;
    unsigned long vsize;
    long rss_pages;
} process_stat_t;

// Безпечний розбір /proc/[pid]/stat
int read_process_stat(pid_t pid, process_stat_t *info) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/stat", pid);

    FILE *f = fopen(path, "r");
    if (!f) return -1; // Процес міг завершитися (ENOENT)

    char buf[2048];
    if (!fgets(buf, sizeof(buf), f)) {
        fclose(f);
        return -1;
    }
    fclose(f);

    // Двопрохідний пошук: перша '(' та остання ')'
    char *first_paren = strchr(buf, '(');
    char *last_paren = strrchr(buf, ')');

    if (!first_paren || !last_paren || first_paren >= last_paren) {
        return -1; // Пошкоджений рядок stat
    }

    // Зчитуємо PID до першої дужки
    info->pid = (pid_t)atoi(buf);

    // Безпечно копіюємо comm всередині дужок
    size_t comm_len = last_paren - (first_paren + 1);
    if (comm_len >= sizeof(info->comm)) comm_len = sizeof(info->comm) - 1;
    strncpy(info->comm, first_paren + 1, comm_len);
    info->comm[comm_len] = '\0';

    // Розбираємо поля після останньої закриваючої дужки
    // Поле після ')' — це state (#3), далі ppid (#4) тощо.
    char *rest = last_paren + 2; // Пропускаємо ") "
    int assigned = sscanf(rest,
        "%c %d %*d %*d %*d %*d %*u %*u %*u %*u %*u %lu %lu %*d %*d %*d %*d %ld %*d %*u %lu %ld",
        &info->state,
        &info->ppid,
        &info->utime,
        &info->stime,
        &info->num_threads,
        &info->vsize,
        &info->rss_pages);

    return (assigned == 7) ? 0 : -1;
}

// Читання командного рядка з нуль-байтами
void print_process_cmdline(pid_t pid) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/cmdline", pid);

    FILE *f = fopen(path, "rb");
    if (!f) return;

    char buf[1024];
    size_t n = fread(buf, 1, sizeof(buf) - 1, f);
    fclose(f);

    if (n == 0) {
        printf("Cmdline: [ядерний потік або порожньо]\n");
        return;
    }

    // Замінюємо внутрішні нуль-байти на пробіли для виводу
    for (size_t i = 0; i < n - 1; i++) {
        if (buf[i] == '\0') buf[i] = ' ';
    }
    buf[n] = '\0';
    printf("Cmdline: %s\n", buf);
}

// Інспекція відкритих файлових дескрипторів
void inspect_process_fds(pid_t pid) {
    char dirpath[64];
    snprintf(dirpath, sizeof(dirpath), "/proc/%d/fd", pid);

    DIR *d = opendir(dirpath);
    if (!d) return;

    printf("Відкриті дескриптори /proc/%d/fd:\n", pid);
    struct dirent *dir;
    int count = 0;
    while ((dir = readdir(d)) != NULL) {
        if (dir->d_name[0] == '.') continue;

        char linkpath[PATH_MAX];
        char targetpath[PATH_MAX];
        snprintf(linkpath, sizeof(linkpath), "%s/%s", dirpath, dir->d_name);

        // readlink() повертає ціль магічного посилання без нуль-байта в кінці
        ssize_t len = readlink(linkpath, targetpath, sizeof(targetpath) - 1);
        if (len != -1) {
            targetpath[len] = '\0';
            printf("  fd %s -> %s\n", dir->d_name, targetpath);
            count++;
        }
        if (count >= 5) { // Обмежуємо вивід першими 5 для лаконічності
            printf("  ... (показано перші 5)\n");
            break;
        }
    }
    closedir(d);
}

int main() {
    pid_t my_pid = getpid();
    process_stat_t stat_info;

    printf("=== Інспекція поточного процесу (PID: %d) ===\n", my_pid);

    if (read_process_stat(my_pid, &stat_info) == 0) {
        printf("Comm:    %s\n", stat_info.comm);
        printf("State:   %c\n", stat_info.state);
        printf("PPID:    %d\n", stat_info.ppid);
        printf("Threads: %ld\n", stat_info.num_threads);
        printf("VSize:   %lu KB\n", stat_info.vsize / 1024);
        printf("RSS:     %ld сторінок\n", stat_info.rss_pages);
    } else {
        fprintf(stderr, "Помилка зчитування stat\n");
    }

    print_process_cmdline(my_pid);
    inspect_process_fds(my_pid);

    return 0;
}
