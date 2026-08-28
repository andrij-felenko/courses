#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <stdint.h>

#define ZFS_DEV_PATH "/dev/zfs"
#define KEY_SIZE_BYTES 32

/* Спрощена структура параметрів ioctl для взаємодії з /dev/zfs */
typedef struct zfs_cmd_args {
    char zc_name[256];
    char zc_value[1024];
    uint64_t zc_cookie;
    uint64_t zc_objset_type;
    uint64_t zc_keystatus;
    uint64_t zc_keyformat;
} zfs_cmd_args_t;

/* Отримання описувача символьного пристрою ZFS */
static int open_zfs_control(void) {
    int fd = open(ZFS_DEV_PATH, O_RDWR);
    if (fd < 0) {
        perror("Помилка відкриття /dev/zfs");
    }
    return fd;
}

/* Зчитати бінарний 256-бітний ключ із файла */
static int read_raw_key_file(const char *key_path, unsigned char *key_buffer) {
    int fd = open(key_path, O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття файла ключа %s: %s\n", key_path, strerror(errno));
        return -1;
    }

    ssize_t bytes_read = read(fd, key_buffer, KEY_SIZE_BYTES);
    close(fd);

    if (bytes_read != KEY_SIZE_BYTES) {
        fprintf(stderr, "Некоректний розмір ключа (%zd байтів, очікується 32)\n", bytes_read);
        return -1;
    }
    return 0;
}

/* Завантаження майстер-ключа датасету в ядро */
static int load_zfs_key(int zfs_fd, const char *dataset_name, const unsigned char *raw_key) {
    zfs_cmd_args_t cmd;
    memset(&cmd, 0, sizeof(cmd));

    strncpy(cmd.zc_name, dataset_name, sizeof(cmd.zc_name) - 1);
    cmd.zc_keyformat = 1; /* KeyFormat: Raw 256-bit binary */
    memcpy(cmd.zc_value, raw_key, KEY_SIZE_BYTES);

    /* Відправка розширюваної команди завантаження ключа ZFS_IOC_LOAD_KEY */
    /* Виклик ioctl повертає 0 при успішному розгортанні Master Key у пам'яті ядра */
    if (ioctl(zfs_fd, 0x5a01, &cmd) != 0) {
        if (errno == EEXIST) {
            printf("Ключ для датасету %s вже завантажено в ядро.\n", dataset_name);
            return 0;
        }
        fprintf(stderr, "Помилка ioctl ZFS_IOC_LOAD_KEY для %s: %s\n", dataset_name, strerror(errno));
        return -1;
    }

    printf("Успішно завантажено Майстер-ключ для датасету: %s\n", dataset_name);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <dataset_name> <key_file_path>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *dataset_name = argv[1];
    const char *key_file_path = argv[2];
    unsigned char raw_key[KEY_SIZE_BYTES];

    if (read_raw_key_file(key_file_path, raw_key) != 0) {
        return EXIT_FAILURE;
    }

    int zfs_fd = open_zfs_control();
    if (zfs_fd < 0) {
        return EXIT_FAILURE;
    }

    int result = load_zfs_key(zfs_fd, dataset_name, raw_key);

    /* Явне очищення ключа в користувацькій пам'яті для безпеки */
    explicit_bzero(raw_key, sizeof(raw_key));
    close(zfs_fd);

    return (result == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}
