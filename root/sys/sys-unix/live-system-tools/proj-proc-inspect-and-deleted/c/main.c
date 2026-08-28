/* C Implementation: /proc Inspector and Deleted File Detector */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <ctype.h>
#include <errno.h>

#define PROC_PATH_MAX 512
#define BUFFER_SIZE 4096

typedef struct {
    pid_t pid;
    pid_t ppid;
    char comm[256];
    char state;
    unsigned long utime;
    unsigned long stime;
    unsigned long vsize;
    long rss;
} ProcessStat;

int is_numeric_dir(const char *name) {
    while (*name) {
        if (!isdigit((unsigned char)*name)) return 0;
        name++;
    }
    return 1;
}

int parse_proc_stat(pid_t pid, ProcessStat *pstat) {
    char stat_path[PROC_PATH_MAX];
    snprintf(stat_path, sizeof(stat_path), "/proc/%d/stat", pid);

    FILE *f = fopen(stat_path, "r");
    if (!f) return -1;

    char buffer[BUFFER_SIZE];
    if (!fgets(buffer, sizeof(buffer), f)) {
        fclose(f);
        return -1;
    }
    fclose(f);

    /* Пошук меж імені comm: перша '(' та остання ')' */
    char *open_paren = strchr(buffer, '(');
    char *close_paren = strrchr(buffer, ')');
    if (!open_paren || !close_paren || close_paren < open_paren) {
        return -1;
    }

    pstat->pid = pid;
    size_t comm_len = (size_t)(close_paren - open_paren - 1);
    if (comm_len >= sizeof(pstat->comm)) comm_len = sizeof(pstat->comm) - 1;
    strncpy(pstat->comm, open_paren + 1, comm_len);
    pstat->comm[comm_len] = '\0';

    /* Зчитування полів після останньої дужки */
    char *rest = close_paren + 2;
    int items = sscanf(rest,
        "%c %d %*d %*d %*d %*d %*u %*u %*u %*u %*u %lu %lu %*d %*d %*d %*d %*d %*d %*u %lu %ld",
        &pstat->state,
        &pstat->ppid,
        &pstat->utime,
        &pstat->stime,
        &pstat->vsize,
        &pstat->rss);

    return (items == 6) ? 0 : -1;
}

void check_deleted_fds(pid_t pid, const char *comm) {
    char fd_dir_path[PROC_PATH_MAX];
    snprintf(fd_dir_path, sizeof(fd_dir_path), "/proc/%d/fd", pid);

    DIR *dir = opendir(fd_dir_path);
    if (!dir) return; /* Можлива відмова у правах доступу для чужих процесів */

    struct dirent *entry;
    char link_target[PROC_PATH_MAX];
    char symlink_path[PROC_PATH_MAX];

    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') continue;

        snprintf(symlink_path, sizeof(symlink_path), "/proc/%d/fd/%s", pid, entry->d_name);
        ssize_t len = readlink(symlink_path, link_target, sizeof(link_target) - 1);
        if (len <= 0) continue;
        link_target[len] = '\0';

        /* Перевірка чи містить посилання мітку '(deleted)' */
        if (strstr(link_target, "(deleted)") != NULL) {
            struct stat st;
            off_t file_size = 0;
            if (stat(symlink_path, &st) == 0) {
                file_size = st.st_size;
            }

            printf("[DELETED FILE LEAK] PID: %-6d | Comm: %-15s | FD: %-3s | Size: %10ld bytes | File: %s\n",
                   pid, comm, entry->d_name, (long)file_size, link_target);
        }
    }
    closedir(dir);
}

int main(void) {
    DIR *proc_dir = opendir("/proc");
    if (!proc_dir) {
        perror("Failed to open /proc");
        return 1;
    }

    printf("=== SCANNING SYSTEM PROCESSES & UNLINKED OPEN FILES ===\n");
    struct dirent *entry;
    while ((entry = readdir(proc_dir)) != NULL) {
        if (!is_numeric_dir(entry->d_name)) continue;

        pid_t pid = (pid_t)atoi(entry->d_name);
        ProcessStat pstat;
        if (parse_proc_stat(pid, &pstat) == 0) {
            /* Якщо процес у стані D (дисковий сон), виводимо окреме попередження */
            if (pstat.state == 'D') {
                printf("[UNINTERRUPTIBLE D-STATE] PID: %-6d | Comm: %-15s | PPID: %-6d\n",
                       pstat.pid, pstat.comm, pstat.ppid);
            }

            /* Перевіряємо відкриті файлові дескриптори на витоки */
            check_deleted_fds(pid, pstat.comm);
        }
    }

    closedir(proc_dir);
    return 0;
}
