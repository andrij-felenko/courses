/* f2fs_ops.c — керування прибиранням та атомарним записом F2FS на C.
 * Збірка: cc -O2 -o f2fs_ops f2fs_ops.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <linux/f2fs_fs.h>

/* Перевірка підтримки ioctl F2FS та стану прикріплення файлу */
int check_file_pin_status(int fd) {
    uint32_t pin_state = 0;
    if (ioctl(fd, F2FS_IOC_GET_PIN_FILE, &pin_state) < 0) {
        if (errno == ENOTTY || errno == EOPNOTSUPP) {
            fprintf(stderr, "Файлова система не підтримує ioctl F2FS\n");
        } else {
            perror("F2FS_IOC_GET_PIN_FILE failed");
        }
        return -1;
    }
    printf("Стан прикріплення (pin): %s\n", pin_state ? "прикріплено" : "вільний");
    return pin_state;
}

/* Запуск атомарної транзакції запису в базу даних */
int execute_atomic_transaction(int fd, const char *data, size_t len) {
    /* 1. Початок атомарної транзакції */
    if (ioctl(fd, F2FS_IOC_START_ATOMIC_WRITE) < 0) {
        perror("F2FS_IOC_START_ATOMIC_WRITE failed");
        return -1;
    }

    /* 2. Запис даних у файл (іде в нові сегменти лога) */
    ssize_t written = write(fd, data, len);
    if (written < 0 || (size_t)written != len) {
        perror("Запис не вдався, скасовуємо транзакцію");
        /* Відкат транзакції при помилці */
        ioctl(fd, F2FS_IOC_ABORT_ATOMIC_WRITE);
        return -1;
    }

    /* 3. Фіксація транзакції (атомарне оновлення покажчиків метаданих) */
    if (ioctl(fd, F2FS_IOC_COMMIT_ATOMIC_WRITE) < 0) {
        perror("F2FS_IOC_COMMIT_ATOMIC_WRITE failed");
        ioctl(fd, F2FS_IOC_ABORT_ATOMIC_WRITE);
        return -1;
    }

    printf("Атомарну транзакцію успішно зафіксовано (%zd байтів)\n", written);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_файла_на_f2fs>\n", argv[0]);
        return 1;
    }

    int fd = open(argv[1], O_RDWR | O_CREAT, 0644);
    if (fd < 0) {
        perror("open failed");
        return 1;
    }

    /* Перевіряємо статус */
    check_file_pin_status(fd);

    /* Демонстрація атомарного запису */
    const char *payload = "TRANSACTION_DATA_BLOCK_HEADER_F2FS_ATOMIC";
    execute_atomic_transaction(fd, payload, strlen(payload));

    /* Спроба запустити прибирача у фоновому режимі (потрібен CAP_SYS_ADMIN) */
    uint32_t sync_gc = 0; /* 0 — фоновий прохід, 1 — синхронний */
    if (ioctl(fd, F2FS_IOC_GARBAGE_COLLECT, &sync_gc) == 0) {
        printf("Фоновий прибирач F2FS успішно активовано\n");
    } else {
        printf("F2FS_IOC_GARBAGE_COLLECT повернув: %s (потрібні привілеї CAP_SYS_ADMIN)\n",
               strerror(errno));
    }

    close(fd);
    return 0;
}
