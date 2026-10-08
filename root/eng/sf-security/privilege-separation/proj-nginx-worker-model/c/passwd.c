#include <unistd.h>
#include <pwd.h>
#include <grp.h>
#include <stdio.h>
#include <stdlib.h>

extern char **environ;

void drop_privileges(const char *username, const char *jail_path) {
    struct passwd *pw = getpwnam(username);
    if (!pw) {
        perror("getpwnam");
        exit(EXIT_FAILURE);
    }

    // 1. Закриття некористуваних успадкованих дескрипторів (крім stdin, stdout, stderr та сокета IPC)
    for (int fd = 3; fd < 1024; ++fd) {
        close(fd);
    }

    // 2. Очищення змінних середовища оточення для запобігання витоку секретів
    if (clearenv() != 0) {
        environ = NULL;
    }

    // 3. Ізоляція файлової системи (chroot)
    if (chroot(jail_path) < 0 || chdir("/") < 0) {
        perror("chroot failed");
        exit(EXIT_FAILURE);
    }

    // 4. Скидання прав групи та користувача
    if (setgid(pw->pw_gid) < 0 || setuid(pw->pw_uid) < 0) {
        perror("setuid/setgid failed");
        exit(EXIT_FAILURE);
    }

    // 5. Перевірка: спроба відновити root має завершитися помилкою
    if (setuid(0) != -1) {
        fprintf(stderr, "ERROR: Able to regain root privileges!\n");
        exit(EXIT_FAILURE);
    }
}
