#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

#define STATUS_PATH "/mnt/demo_fs/control/status"
#define INFO_PATH   "/mnt/demo_fs/info"

static void read_file(const char *path) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", path, strerror(errno));
        return;
    }

    char buf[512];
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    if (n >= 0) {
        buf[n] = '\0';
        printf("--- Вміст %s ---\n%s", path, buf);
    } else {
        fprintf(stderr, "Помилка читання з %s: %s\n", path, strerror(errno));
    }
    close(fd);
}

static void write_status(const char *path, int new_val) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття на запис %s: %s\n", path, strerror(errno));
        return;
    }

    char buf[32];
    int len = snprintf(buf, sizeof(buf), "%d\n", new_val);
    ssize_t written = write(fd, buf, len);
    if (written < 0) {
        fprintf(stderr, "Помилка запису у %s: %s\n", path, strerror(errno));
    } else {
        printf("Успішно записано %d у %s\n", new_val, path);
    }
    close(fd);
}

int main(void) {
    printf("1. Читання інформаційного вузла:\n");
    read_file(INFO_PATH);

    printf("\n2. Поточне значення лічильника:\n");
    read_file(STATUS_PATH);

    printf("\n3. Оновлення значення лічильника на 500:\n");
    write_status(STATUS_PATH, 500);

    printf("\n4. Перевірка оновленого значення:\n");
    read_file(STATUS_PATH);

    return 0;
}
