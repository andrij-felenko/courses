#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <dirent.h>
#include <errno.h>

#define BUF_SIZE 4096

typedef struct {
    int pid;
    char comm[256];
    char state[64];
    long vm_rss_kb;
    char exe_path[1024];
    int open_fds_count;
} proc_info_t;

int inspect_process(int pid, proc_info_t *info) {
    if (!info || pid <= 0) return -1;
    memset(info, 0, sizeof(proc_info_t));
    info->pid = pid;

    // 1. Отримання шляху до виконуваного файлу через magic symlink /proc/[pid]/exe
    char path_buf[256];
    snprintf(path_buf, sizeof(path_buf), "/proc/%d/exe", pid);
    ssize_t len = readlink(path_buf, info->exe_path, sizeof(info->exe_path) - 1);
    if (len != -1) {
        info->exe_path[len] = '\0';
    } else {
        strncpy(info->exe_path, "<недоступно або недостатньо прав>", sizeof(info->exe_path) - 1);
    }

    // 2. Читання та парсинг /proc/[pid]/status
    snprintf(path_buf, sizeof(path_buf), "/proc/%d/status", pid);
    int fd = open(path_buf, O_RDONLY);
    if (fd < 0) {
        return -1; // Процес не існує або немає прав доступу
    }

    char buffer[BUF_SIZE];
    ssize_t bytes_read = read(fd, buffer, sizeof(buffer) - 1);
    close(fd);

    if (bytes_read <= 0) return -1;
    buffer[bytes_read] = '\0';

    // Розбір рядків Name, State, VmRSS
    char *line = strtok(buffer, "\n");
    while (line != NULL) {
        if (strncmp(line, "Name:", 5) == 0) {
            sscanf(line + 5, "%255s", info->comm);
        } else if (strncmp(line, "State:", 6) == 0) {
            strncpy(info->state, line + 6, sizeof(info->state) - 1);
        } else if (strncmp(line, "VmRSS:", 6) == 0) {
            sscanf(line + 6, "%ld", &info->vm_rss_kb);
        }
        line = strtok(NULL, "\n");
    }

    // 3. Підрахунок відкритих файлових дескрипторів у /proc/[pid]/fd
    snprintf(path_buf, sizeof(path_buf), "/proc/%d/fd", pid);
    DIR *dir = opendir(path_buf);
    if (dir) {
        struct dirent *entry;
        while ((entry = readdir(dir)) != NULL) {
            if (entry->d_name[0] != '.') {
                info->open_fds_count++;
            }
        }
        closedir(dir);
    } else {
        info->open_fds_count = -1; // Відсутні права на перегляд fd
    }

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <PID>\n", argv[0]);
        return EXIT_FAILURE;
    }

    int pid = atoi(argv[1]);
    proc_info_t info;

    if (inspect_process(pid, &info) != 0) {
        fprintf(stderr, "Не вдалося зчитати дані для PID %d: %s\n", pid, strerror(errno));
        return EXIT_FAILURE;
    }

    printf("=== Інспекція процесу PID %d ===\n", info.pid);
    printf("Назва:       %s\n", info.comm);
    printf("Стан:        %s\n", info.state);
    printf("Шлях бінарн: %s\n", info.exe_path);
    printf("Пам'ять RSS: %ld КБ\n", info.vm_rss_kb);
    if (info.open_fds_count >= 0) {
        printf("Дескриптори: %d відкритих fd\n", info.open_fds_count);
    } else {
        printf("Дескриптори: <немає доступу до /proc/%d/fd>\n", info.pid);
    }

    return EXIT_SUCCESS;
}
