#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>

/* Копіювання вмісту відкритого дескриптора у новий файл */
static int rescue_descriptor(pid_t pid, int fd, const char *target_name, const char *dest_directory) {
    char proc_link[256];
    char out_path[512];
    char clean_name[256];

    snprintf(proc_link, sizeof(proc_link), "/proc/%d/fd/%d", pid, fd);

    /* Очищаємо суфікс " (deleted)" з отриманого шляху */
    strncpy(clean_name, target_name, sizeof(clean_name) - 1);
    clean_name[sizeof(clean_name) - 1] = '\0';
    char *del_marker = strstr(clean_name, " (deleted)");
    if (del_marker) *del_marker = '\0';

    /* Витягуємо базове ім'я файлу */
    char *base = strrchr(clean_name, '/');
    const char *filename = base ? base + 1 : clean_name;
    if (strlen(filename) == 0) filename = "unnamed_rescued_file";

    snprintf(out_path, sizeof(out_path), "%s/rescued_pid%d_fd%d_%s", dest_directory, pid, fd, filename);

    /* Відкриваємо дескриптор напряму через magic link */
    int in_fd = open(proc_link, O_RDONLY | O_CLOEXEC);
    if (in_fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", proc_link, strerror(errno));
        return -1;
    }

    int out_fd = open(out_path, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0640);
    if (out_fd < 0) {
        fprintf(stderr, "Не вдалося створити цільовий файл %s: %s\n", out_path, strerror(errno));
        close(in_fd);
        return -1;
    }

    char buffer[65536];
    ssize_t bytes_read;
    size_t total_rescued = 0;

    while ((bytes_read = read(in_fd, buffer, sizeof(buffer))) > 0) {
        char *ptr = buffer;
        ssize_t to_write = bytes_read;
        while (to_write > 0) {
            ssize_t written = write(out_fd, ptr, to_write);
            if (written < 0) {
                if (errno == EINTR) continue;
                fprintf(stderr, "Помилка запису даних у %s: %s\n", out_path, strerror(errno));
                close(in_fd);
                close(out_fd);
                return -1;
            }
            ptr += written;
            to_write -= written;
        }
        total_rescued += (size_t)bytes_read;
    }

    close(in_fd);
    close(out_fd);

    printf("✓ [ВРЯТОВАНО] PID %d, FD %d -> %s (розмір: %lu байтів)\n", pid, fd, out_path, (unsigned long)total_rescued);
    return 0;
}

/* Сканування таблиці дескрипторів конкретного процесу */
int scan_process_descriptors(pid_t pid, const char *dest_directory) {
    char fd_dir_path[256];
    snprintf(fd_dir_path, sizeof(fd_dir_path), "/proc/%d/fd", pid);

    DIR *dir = opendir(fd_dir_path);
    if (!dir) {
        return -1;
    }

    struct dirent *entry;
    int rescued_count = 0;

    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') continue;

        int fd_num = atoi(entry->d_name);
        char link_path[512];
        char target_buf[1024];

        snprintf(link_path, sizeof(link_path), "%s/%s", fd_dir_path, entry->d_name);
        ssize_t len = readlink(link_path, target_buf, sizeof(target_buf) - 1);
        if (len < 0) continue;
        target_buf[len] = '\0';

        /* Перевіряємо наявність мітки (deleted) у розв'язаному шляху */
        if (strstr(target_buf, "(deleted)") != NULL) {
            printf("! Знайдено відкритий видалений файл: PID %d, FD %d -> %s\n", pid, fd_num, target_buf);
            if (rescue_descriptor(pid, fd_num, target_buf, dest_directory) == 0) {
                rescued_count++;
            }
        }
    }

    closedir(dir);
    return rescued_count;
}
