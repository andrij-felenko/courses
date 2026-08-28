#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <errno.h>

#define BATCH_CAPACITY 64
#define MAX_PARALLEL_WORKERS 4

typedef struct {
    char *items[BATCH_CAPACITY + 2];
    int count;
} BatchBuffer;

static void init_batch(BatchBuffer *b, const char *command) {
    b->items[0] = strdup(command);
    b->count = 1;
}

static void free_batch_payload(BatchBuffer *b) {
    for (int i = 1; i < b->count; ++i) {
        free(b->items[i]);
    }
    b->count = 1;
}

static void drain_workers(int *active_workers, int block_for_slot) {
    while (*active_workers > 0) {
        int status = 0;
        int flags = block_for_slot ? 0 : WNOHANG;
        pid_t pid = waitpid(-1, &status, flags);
        if (pid > 0) {
            (*active_workers)--;
            if (block_for_slot) break;
        } else {
            break;
        }
    }
}

static void dispatch_batch(BatchBuffer *b, int *active_workers) {
    if (b->count <= 1) return;

    b->items[b->count] = NULL;

    while (*active_workers >= MAX_PARALLEL_WORKERS) {
        drain_workers(active_workers, 1);
    }

    pid_t pid = fork();
    if (pid == 0) {
        /* Дочірній процес: заміна образу процесу на цільову команду */
        execvp(b->items[0], b->items);
        _exit(127);
    } else if (pid > 0) {
        (*active_workers)++;
        free_batch_payload(b);
    } else {
        perror("fork");
    }
}

static void traverse_tree(const char *dir_path, BatchBuffer *b, int *active_workers) {
    DIR *dir = opendir(dir_path);
    if (!dir) return;

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        char full_path[4096];
        int len = snprintf(full_path, sizeof(full_path), "%s/%s", dir_path, entry->d_name);
        if (len >= (int)sizeof(full_path)) continue;

        struct stat st;
        if (lstat(full_path, &st) == -1) continue;

        if (S_ISDIR(st.st_mode)) {
            traverse_tree(full_path, b, active_workers);
        } else if (S_ISREG(st.st_mode)) {
            /* Фільтр: файли з розширенням .log */
            const char *dot = strrchr(entry->d_name, '.');
            if (dot && strcmp(dot, ".log") == 0) {
                b->items[b->count++] = strdup(full_path);
                if (b->count > BATCH_CAPACITY) {
                    dispatch_batch(b, active_workers);
                }
            }
        }
    }
    closedir(dir);
}

int main(int argc, char *argv[]) {
    const char *start_dir = (argc > 1) ? argv[1] : ".";
    BatchBuffer batch;
    init_batch(&batch, "gzip");

    int active_workers = 0;
    traverse_tree(start_dir, &batch, &active_workers);

    /* Відправлення фінального залишку накопичених аргументів */
    dispatch_batch(&batch, &active_workers);

    /* Очікування завершення всіх активних воркерів */
    while (active_workers > 0) {
        drain_workers(&active_workers, 1);
    }

    free(batch.items[0]);
    return 0;
}
