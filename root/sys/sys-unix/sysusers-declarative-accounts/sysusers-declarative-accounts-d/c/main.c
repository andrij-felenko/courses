#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <pwd.h>
#include <shadow.h>
#include <errno.h>

/* Перевірка стану системного користувача за допомогою стандартного C API */
int check_system_user(const char *username, uid_t *out_uid) {
    struct passwd *pw = getpwnam(username);
    if (pw == NULL) {
        if (errno == 0) {
            /* Користувача не знайдено */
            return 0;
        }
        perror("Помилка при виклику getpwnam");
        return -1;
    }
    
    if (out_uid != NULL) {
        *out_uid = pw->pw_uid;
    }
    return 1;
}
