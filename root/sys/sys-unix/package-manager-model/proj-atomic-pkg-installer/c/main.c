#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/file.h>

#define TEMP_SUFFIX ".dpkg-new"
#define LOCK_FILE "/tmp/pkg_installer.lock"
#define BUFFER_SIZE 4096

typedef struct {
    const char *target_path;
    const char *payload_data;
    size_t payload_len;
    mode_t permissions;
} package_file_t;

/* Захоплення глобального блокування інсталятора */
static int acquire_system_lock(void) {
    int lock_fd = open(LOCK_FILE, O_RDWR | O_CREAT, 0600);
    if (lock_fd < 0) {
        perror("[ERROR] Не вдалося відкрити lock-файл");
        return -1;
    }
    if (flock(lock_fd, LOCK_EX | LOCK_NB) < 0) {
        fprintf(stderr, "[ERROR] Інший процес пакетного менеджера вже виконується.\n");
        close(lock_fd);
        return -1;
    }
    return lock_fd;
}

/* Звільнення блокування */
static void release_system_lock(int lock_fd) {
    if (lock_fd >= 0) {
        flock(lock_fd, LOCK_UN);
        close(lock_fd);
        unlink(LOCK_FILE);
    }
}

/* Виконує атомарну інсталяцію одного файла пакунка */
int install_package_file_atomic(const package_file_t *file) {
    char temp_path[4096];
    int fd = -1;
    ssize_t bytes_written;
    int res = -1;

    /* Створення шляху до тимчасового файла у тому ж каталозі */
    snprintf(temp_path, sizeof(temp_path), "%s%s", file->target_path, TEMP_SUFFIX);

    /* 1. Відкриваємо тимчасовий файл для запису (O_CREAT | O_WRONLY | O_TRUNC | O_NOFOLLOW) */
    fd = open(temp_path, O_WRONLY | O_CREAT | O_TRUNC | O_NOFOLLOW, file->permissions);
    if (fd < 0) {
        fprintf(stderr, "[ERROR] Не вдалося створити тимчасовий файл %s: %s\n",
                temp_path, strerror(errno));
        return -1;
    }

    /* 2. Записуємо корисне навантаження (payload) */
    bytes_written = write(fd, file->payload_data, file->payload_len);
    if (bytes_written < 0 || (size_t)bytes_written != file->payload_len) {
        fprintf(stderr, "[ERROR] Збій запису payload у файл %s: %s\n",
                temp_path, strerror(errno));
        goto err_cleanup;
    }

    /* 3. Примусово скидаємо сторінковий кеш на фізичний диск */
    if (fsync(fd) < 0) {
        fprintf(stderr, "[ERROR] Збій fsync для файла %s: %s\n",
                temp_path, strerror(errno));
        goto err_cleanup;
    }

    /* Закриваємо файловий дескриптор перед rename */
    close(fd);
    fd = -1;

    /* 4. Атомарна заміна існуючого файла новим через rename(2) */
    if (rename(temp_path, file->target_path) < 0) {
        fprintf(stderr, "[ERROR] Не вдалося перейменувати %s у %s: %s\n",
                temp_path, file->target_path, strerror(errno));
        unlink(temp_path);
        return -1;
    }

    printf("[SUCCESS] Файл %s успішно інстальовано атомарно.\n", file->target_path);
    return 0;

err_cleanup:
    if (fd >= 0) {
        close(fd);
    }
    unlink(temp_path);
    return res;
}

int main(void) {
    int lock_fd = acquire_system_lock();
    if (lock_fd < 0) {
        return EXIT_FAILURE;
    }

    package_file_t pkg_bin = {
        .target_path = "/tmp/my_app_binary",
        .payload_data = "#!/bin/sh\necho 'Hello from atomic package!'\n",
        .payload_len = 46,
        .permissions = 0755
    };

    int status = install_package_file_atomic(&pkg_bin);

    release_system_lock(lock_fd);
    return status == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
