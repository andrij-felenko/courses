#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <dirent.h>
#include <errno.h>
#include <ftw.h>

#define TARGET_DIR "/tmp/disk_test_leak"
#define FILE_NAME "/tmp/disk_test_leak/phantom.bin"
#define ALLOC_SIZE (64 * 1024 * 1024) /* 64 МіБ */

static off_t g_dir_apparent_size = 0;

static int count_file_size(const char *fpath, const struct stat *sb, int typeflag) {
    if (typeflag == FTW_F) {
        g_dir_apparent_size += sb->st_blocks * 512;
    }
    return 0;
}

static off_t measure_directory_usage(const char *dir_path) {
    g_dir_apparent_size = 0;
    if (ftw(dir_path, count_file_size, 16) != 0) {
        perror("Помилка обходу дерева ftw");
        return -1;
    }
    return g_dir_apparent_size;
}

static void print_vfs_status(const char *path, const char *phase_label) {
    struct statvfs st;
    if (statvfs(path, &st) != 0) {
        perror("statvfs error");
        return;
    }

    unsigned long long total_bytes = (unsigned long long)st.f_blocks * st.f_frsize;
    unsigned long long free_bytes = (unsigned long long)st.f_bfree * st.f_frsize;
    unsigned long long avail_bytes = (unsigned long long)st.f_bavail * st.f_frsize;
    off_t du_bytes = measure_directory_usage(path);

    printf("\n[%s]\n", phase_label);
    printf("  Точка VFS:          %s\n", path);
    printf("  Загалом (VFS):      %10llu KiB (%llu MiB)\n", total_bytes / 1024, total_bytes / (1024 * 1024));
    printf("  Вільно (f_bfree):   %10llu KiB (%llu MiB)\n", free_bytes / 1024, free_bytes / (1024 * 1024));
    printf("  Доступно (f_bavail): %8llu KiB (%llu MiB)\n", avail_bytes / 1024, avail_bytes / (1024 * 1024));
    printf("  Каталог (du / ftw): %8lld KiB (%lld MiB)\n", (long long)du_bytes / 1024, (long long)du_bytes / (1024 * 1024));
}

int main(void) {
    mkdir(TARGET_DIR, 0755);

    print_vfs_status(TARGET_DIR, "ЕТАП 1: Початковий стан чистого каталогу");

    int fd = open(FILE_NAME, O_CREAT | O_RDWR | O_TRUNC, 0644);
    if (fd < 0) {
        perror("Не вдалося створити файл");
        return 1;
    }

    /* Виділяємо 64 МіБ реальних блоків на диску */
    if (posix_fallocate(fd, 0, ALLOC_SIZE) != 0) {
        /* Резервний варіант: послідовний запис буфера */
        char buffer[4096];
        memset(buffer, 0xAA, sizeof(buffer));
        for (size_t i = 0; i < ALLOC_SIZE / sizeof(buffer); ++i) {
            if (write(fd, buffer, sizeof(buffer)) != (ssize_t)sizeof(buffer)) {
                perror("write failed");
                close(fd);
                return 1;
            }
        }
    }
    fsync(fd);

    print_vfs_status(TARGET_DIR, "ЕТАП 2: Файл 64 MiB створено й записано на диск");

    /* Вилучаємо запис із каталогу: i_nlink падає до 0 */
    if (unlink(FILE_NAME) != 0) {
        perror("unlink failed");
        close(fd);
        return 1;
    }

    print_vfs_status(TARGET_DIR, "ЕТАП 3: Файл видалено через unlink(), але fd залишається ВІДКРИТИМ");

    printf("\n--> Спроба перевірити /proc/self/fd:\n");
    char fd_path[64];
    char link_target[256];
    snprintf(fd_path, sizeof(fd_path), "/proc/self/fd/%d", fd);
    ssize_t len = readlink(fd_path, link_target, sizeof(link_target) - 1);
    if (len > 0) {
        link_target[len] = '\0';
        printf("  Дескриптор %s вказує на: %s\n", fd_path, link_target);
    }

    printf("\n--> Відновлення місця на льоту: ftruncate(fd, 0)...\n");
    if (ftruncate(fd, 0) != 0) {
        perror("ftruncate failed");
    }

    print_vfs_status(TARGET_DIR, "ЕТАП 4: Дескриптор обнулено (блоки повернуто в суперблок)");

    close(fd);
    rmdir(TARGET_DIR);
    printf("\nТест успішно завершено. Ресурси коректно вивільнено.\n");
    return 0;
}
