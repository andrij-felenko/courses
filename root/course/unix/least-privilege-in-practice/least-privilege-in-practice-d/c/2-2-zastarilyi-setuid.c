#define _GNU_SOURCE
#include <unistd.h>
#include <grp.h>
#include <stdio.h>
#include <stdlib.h>

/* Безпечне незворотне скидання прав демона */
int drop_privileges_permanently(uid_t target_uid, gid_t target_gid) {
    /* 1. Скидаємо всі додаткові групи суперкористувача */
    if (setgroups(0, NULL) != 0) {
        perror("setgroups(0, NULL)");
        return -1;
    }

    /* 2. Атомарно встановлюємо Real, Effective та Saved GID */
    if (setresgid(target_gid, target_gid, target_gid) != 0) {
        perror("setresgid");
        return -1;
    }

    /* 3. Атомарно встановлюємо Real, Effective та Saved UID */
    if (setresuid(target_uid, target_uid, target_uid) != 0) {
        perror("setresuid");
        return -1;
    }

    /* 4. Перевірка: переконуємося, що повернення до root неможливе */
    if (setresuid(-1, 0, -1) == 0) {
        fprintf(stderr, "КРИТИЧНА ПОМИЛКА: вдалося відновити root UID!\n");
        abort();
    }

    return 0;
}
