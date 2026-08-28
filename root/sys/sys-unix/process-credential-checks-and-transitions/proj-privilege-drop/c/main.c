#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/prctl.h>
#include <grp.h>
#include <pwd.h>
#include <errno.h>

// Безпечне остаточне скидання привілеїв до цільового користувача
int drop_privileges_permanently(const char *username) {
    if (username == NULL) {
        errno = EINVAL;
        return -1;
    }

    // Отримання запису з бази даних користувачів /etc/passwd
    struct passwd *pw = getpwnam(username);
    if (pw == NULL) {
        fprintf(stderr, "Помилка: користувача %s не знайдено в /etc/passwd\n", username);
        return -1;
    }

    uid_t target_uid = pw->pw_uid;
    gid_t target_gid = pw->pw_gid;

    // Крок 1: Ініціалізація додаткових груп цільового користувача
    // initgroups викликає setgroups під капотом, включаючи всі групи з /etc/group
    if (initgroups(username, target_gid) != 0) {
        perror("Помилка initgroups");
        return -1;
    }

    // Крок 2: Зміна GID (Real, Effective, Saved)
    if (setresgid(target_gid, target_gid, target_gid) != 0) {
        perror("Помилка setresgid");
        return -1;
    }

    // Крок 3: Зміна UID (Real, Effective, Saved)
    // Увага: цей виклик виконується ОСТАННІМ серед змін ідентифікаторів,
    // бо після нього процес втрачає привілей CAP_SETGID!
    if (setresuid(target_uid, target_uid, target_uid) != 0) {
        perror("Помилка setresuid (можливо досягнуто NPROC)");
        return -1;
    }

    // Крок 4: Верифікація неможливості підвищення привілеїв
    if (seteuid(0) != -1 || errno != EPERM) {
        fprintf(stderr, "КРИТИЧНА ПОМИЛКА БЕЗПЕКИ: процес зміг відновити euid 0!\n");
        return -1;
    }

    // Крок 5: Вимкнення створення core dump для захисту чутливих даних у пам'яті
    if (prctl(PR_SET_DUMPABLE, 0, 0, 0, 0) != 0) {
        perror("Помилка prctl(PR_SET_DUMPABLE)");
        return -1;
    }

    return 0;
}
