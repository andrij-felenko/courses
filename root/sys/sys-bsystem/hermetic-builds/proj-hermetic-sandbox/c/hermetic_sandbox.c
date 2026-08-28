/* hermetic_sandbox.c - герметичний раннер дій компіляції на системних викликах Linux */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sched.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/wait.h>

static int write_control_file(const char *path, const char *value) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) return -1;

    size_t len = strlen(value);
    ssize_t written = write(fd, value, len);
    close(fd);
    return (written == (ssize_t)len) ? 0 : -1;
}

static int configure_user_namespace(uid_t host_uid, gid_t host_gid) {
    /* Вимикаємо setgroups перед записом gid_map */
    if (write_control_file("/proc/self/setgroups", "deny") != 0) {
        perror("Помилка запису в /proc/self/setgroups");
        return -1;
    }

    char map_buffer[64];

    /* Мапування UID: віртуальний 0 -> реальний host_uid */
    snprintf(map_buffer, sizeof(map_buffer), "0 %u 1\n", host_uid);
    if (write_control_file("/proc/self/uid_map", map_buffer) != 0) {
        perror("Помилка налаштування uid_map");
        return -1;
    }

    /* Мапування GID: віртуальний 0 -> реальний host_gid */
    snprintf(map_buffer, sizeof(map_buffer), "0 %u 1\n", host_gid);
    if (write_control_file("/proc/self/gid_map", map_buffer) != 0) {
        perror("Помилка налаштування gid_map");
        return -1;
    }

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Використання: %s <каталог_входів> <каталог_виходів> <команда> [аргументи...]\n", argv[0]);
        return 1;
    }

    const char *inputs_dir = argv[1];
    const char *outputs_dir = argv[2];
    char **cmd_argv = &argv[3];

    uid_t host_uid = getuid();
    gid_t host_gid = getgid();

    /* Створення набору ізольованих просторів імен */
    int clone_flags = CLONE_NEWUSER | CLONE_NEWNS | CLONE_NEWNET | CLONE_NEWIPC | CLONE_NEWUTS;
    if (unshare(clone_flags) != 0) {
        perror("Системний виклик unshare() завершився помилкою");
        return 1;
    }

    /* Ініціалізація прав у новому просторі користувачів */
    if (configure_user_namespace(host_uid, host_gid) != 0) {
        fprintf(stderr, "Не вдалося ініціалізувати простір користувача\n");
        return 1;
    }

    /* Перетворення дерева монтування на приватне для усунення витоків точок монтування */
    if (mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) != 0) {
        perror("Помилка mount(MS_PRIVATE)");
        return 1;
    }

    /* Створення тимчасового кореня пісочниці у віртуальній пам'яті */
    const char *sandbox_root = "/tmp/hermetic_sandbox_root";
    mkdir(sandbox_root, 0755);

    if (mount("tmpfs", sandbox_root, "tmpfs", 0, "size=128M,mode=0755") != 0) {
        perror("Помилка монтування tmpfs для кореня пісочниці");
        return 1;
    }

    /* Створення робочих каталогів всередині нового кореня */
    char path_buffer[512];
    snprintf(path_buffer, sizeof(path_buffer), "%s/src", sandbox_root);
    mkdir(path_buffer, 0755);

    snprintf(path_buffer, sizeof(path_buffer), "%s/out", sandbox_root);
    mkdir(path_buffer, 0755);

    snprintf(path_buffer, sizeof(path_buffer), "%s/tmp", sandbox_root);
    mkdir(path_buffer, 0777);

    /* Підключення вхідних сирців у режимі тільки для читання (Read-Only) */
    snprintf(path_buffer, sizeof(path_buffer), "%s/src", sandbox_root);
    if (mount(inputs_dir, path_buffer, NULL, MS_BIND | MS_REC, NULL) != 0) {
        perror("Помилка bind-монтування каталогу входів");
        return 1;
    }
    if (mount(NULL, path_buffer, NULL, MS_BIND | MS_REMOUNT | MS_RDONLY | MS_REC, NULL) != 0) {
        perror("Помилка перемонтування входів у режимі тільки для читання");
        return 1;
    }

    /* Підключення каталогу виходів у режимі читання та запису */
    snprintf(path_buffer, sizeof(path_buffer), "%s/out", sandbox_root);
    if (mount(outputs_dir, path_buffer, NULL, MS_BIND | MS_REC, NULL) != 0) {
        perror("Помилка bind-монтування каталогу виходів");
        return 1;
    }

    /* Зміна кореня файлової системи */
    if (chroot(sandbox_root) != 0) {
        perror("Помилка системного виклику chroot()");
        return 1;
    }
    if (chdir("/src") != 0) {
        perror("Помилка переходу до каталогу /src");
        return 1;
    }

    /* Фіксоване, стандартизоване середовище змінних */
    char *hermetic_environment[] = {
        "PATH=/bin:/usr/bin",
        "LANG=C.UTF-8",
        "LC_ALL=C.UTF-8",
        "TMPDIR=/tmp",
        NULL
    };

    /* Виконання команди компілятора в ізольованому середовищі */
    execvpe(cmd_argv[0], cmd_argv, hermetic_environment);

    perror("Помилка запуску цільової команди через execvpe()");
    return 1;
}
