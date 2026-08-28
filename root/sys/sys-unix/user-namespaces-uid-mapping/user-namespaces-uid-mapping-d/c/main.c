#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>

static void write_file(const char *path, const char *text) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        perror("open failed");
        exit(EXIT_FAILURE);
    }
    if (write(fd, text, strlen(text)) != (ssize_t)strlen(text)) {
        perror("write failed");
        close(fd);
        exit(EXIT_FAILURE);
    }
    close(fd);
}

int main(void) {
    uid_t real_uid = getuid();
    gid_t real_gid = getgid();

    // 1. Створюємо новий User Namespace
    if (unshare(CLONE_NEWUSER) < 0) {
        perror("unshare(CLONE_NEWUSER) failed");
        return 1;
    }

    // 2. Блокуємо setgroups перед записом gid_map
    write_file("/proc/self/setgroups", "deny");

    // 3. Записуємо uid_map (відображаємо себе на root UID 0)
    char map_buf[128];
    snprintf(map_buf, sizeof(map_buf), "0 %d 1\n", real_uid);
    write_file("/proc/self/uid_map", map_buf);

    // 4. Записуємо gid_map (відображаємо свою групу на GID 0)
    snprintf(map_buf, sizeof(map_buf), "0 %d 1\n", real_gid);
    write_file("/proc/self/gid_map", map_buf);

    printf("Успішно перейшли у User Namespace:\n");
    printf("  getuid()  = %d\n", getuid());
    printf("  geteuid() = %d\n", geteuid());

    // Перевіряємо привілеї всередині середовища
    system("id");
    return 0;
}
