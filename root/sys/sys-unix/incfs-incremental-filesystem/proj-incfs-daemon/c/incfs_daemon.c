/* incfs_daemon.c — Реалізація демона заповнення IncFS мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <stdint.h>
#include <errno.h>

/* Визначення базових структур IncFS */
#define INCFS_IOCTL_BASE 0x67

struct incfs_pending_read_info {
    uint64_t file_id_low;
    uint64_t file_id_high;
    uint32_t timestamp_us;
    uint32_t block_index;
};

struct incfs_fill_block {
    uint32_t block_index;
    uint32_t data_len;
    uint64_t data;
    uint8_t  compression;
    uint8_t  flags;
    uint16_t reserved;
};

struct incfs_fill_blocks {
    uint64_t count;
    uint64_t fill_blocks;
};

#define INCFS_IOC_FILL_BLOCKS _IOW(INCFS_IOCTL_BASE, 2, struct incfs_fill_blocks)

#define BLOCK_SIZE 4096

static int fill_single_block(int incfs_file_fd, uint32_t block_idx) {
    uint8_t buffer[BLOCK_SIZE];
    /* Заповнюємо тестовий блок 4KB впізнаваним паттерном 'A' */
    memset(buffer, 'A', BLOCK_SIZE);

    struct incfs_fill_block fb = {
        .block_index = block_idx,
        .data_len = BLOCK_SIZE,
        .data = (uint64_t)(uintptr_t)buffer,
        .compression = 0,
        .flags = 0,
        .reserved = 0
    };

    struct incfs_fill_blocks fbs = {
        .count = 1,
        .fill_blocks = (uint64_t)(uintptr_t)&fb
    };

    if (ioctl(incfs_file_fd, INCFS_IOC_FILL_BLOCKS, &fbs) < 0) {
        perror("ioctl INCFS_IOC_FILL_BLOCKS failed");
        return -errno;
    }

    printf("[IncFS Daemon C] Блок %u успішно заповнено (4096 байт)\n", block_idx);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_кореню_incfs>\n", argv[0]);
        return EXIT_FAILURE;
    }

    char pending_path[512];
    snprintf(pending_path, sizeof(pending_path), "%s/.pending_reads", argv[1]);

    int pending_fd = open(pending_path, O_RDONLY);
    if (pending_fd < 0) {
        perror("Не вдалося відкрити .pending_reads");
        return EXIT_FAILURE;
    }

    int dir_fd = open(argv[1], O_RDONLY | O_DIRECTORY);
    if (dir_fd < 0) {
        perror("Не вдалося відкрити дескриптор каталогу IncFS");
        close(pending_fd);
        return EXIT_FAILURE;
    }

    printf("[IncFS Daemon C] Демон запущено. Очікування подій на %s...\n", pending_path);

    struct pollfd pfd = {
        .fd = pending_fd,
        .events = POLLIN
    };

    while (1) {
        int ret = poll(&pfd, 1, 5000); /* Таймаут 5 секунд */
        if (ret < 0) {
            perror("Помилка poll()");
            break;
        } else if (ret == 0) {
            printf("[IncFS Daemon C] Таймаут poll(). Запитів немає...\n");
            continue;
        }

        if (pfd.revents & POLLIN) {
            struct incfs_pending_read_info req;
            ssize_t bytes_read = read(pending_fd, &req, sizeof(req));
            if (bytes_read == sizeof(req)) {
                printf("[IncFS Daemon C] Отримано запит: FileID=%llx%llx, Block=%u\n",
                       (unsigned long long)req.file_id_high,
                       (unsigned long long)req.file_id_low,
                       req.block_index);

                char id_path[64];
                snprintf(id_path, sizeof(id_path), ".index/%016llx%016llx",
                         (unsigned long long)req.file_id_high,
                         (unsigned long long)req.file_id_low);

                int file_fd = openat(dir_fd, id_path, O_RDWR | O_CLOEXEC);
                if (file_fd < 0) {
                    perror("Не вдалося відкрити файл за File ID");
                    continue;
                }

                fill_single_block(file_fd, req.block_index);
                close(file_fd);
            }
        }
    }

    close(dir_fd);
    close(pending_fd);
    return EXIT_SUCCESS;
}
