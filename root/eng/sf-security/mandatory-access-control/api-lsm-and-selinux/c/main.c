#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <selinux/selinux.h>
#include <selinux/context.h>

/* Отримання та детальний розбір безпекового контексту процесу */
static bool inspect_current_process(void) {
    char *raw_ctx = NULL;
    if (getcon(&raw_ctx) < 0 || !raw_ctx) {
        perror("Помилка виклику getcon()");
        return false;
    }

    printf("Поточний контекст процесу: %s\n", raw_ctx);

    /* Розбір рядка контексту через структуру context_t */
    context_t con = context_new(raw_ctx);
    if (con) {
        printf("  ├── Користувач: %s\n", context_user_get(con));
        printf("  ├── Роль:       %s\n", context_role_get(con));
        printf("  ├── Домен/Тип:  %s\n", context_type_get(con));
        printf("  └── Рівень MLS: %s\n", context_range_get(con) ? context_range_get(con) : "s0");
        context_free(con);
    }

    freecon(raw_ctx);
    return true;
}

/* Зчитування розширеного атрибута security.selinux для файлу */
static bool inspect_file_label(const char *filepath) {
    char *file_ctx = NULL;
    if (getfilecon(filepath, &file_ctx) < 0 || !file_ctx) {
        perror("Помилка виклику getfilecon()");
        return false;
    }

    printf("Мітка безпеки [%s]: %s\n", filepath, file_ctx);
    freecon(file_ctx);
    return true;
}

int main(void) {
    /* 1. Перевірка активності модуля SELinux у ядрі */
    if (!is_selinux_enabled()) {
        puts("Підсистема SELinux вимкнена або не підтримується ядром.");
        return 0;
    }

    /* 2. Визначення робочого режиму */
    const int enforce_mode = security_getenforce();
    printf("Режим роботи SELinux: %s (код: %d)\n",
           enforce_mode == 1 ? "Enforcing" : (enforce_mode == 0 ? "Permissive" : "Disabled"),
           enforce_mode);

    /* 3. Інспекція процесу */
    if (!inspect_current_process()) {
        return 1;
    }

    /* 4. Інспекція файлу */
    if (!inspect_file_label("/etc/shadow")) {
        return 1;
    }

    return 0;
}
