/* C: Зчитування контексту безпеки процесу та файлу через libselinux */
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <selinux/selinux.h>

int main(int argc, char *argv[]) {
    char *process_con = NULL;
    char *file_con = NULL;

    /* 1. Перевірка активності SELinux у ядрі */
    int enabled = is_selinux_enabled();
    if (enabled < 0) {
        perror("Помилка під час перевірки стану SELinux");
        return 1;
    } else if (enabled == 0) {
        printf("SELinux вимкнено або не підтримується на цій системі.\n");
        return 0;
    }

    printf("SELinux активний. Режим Enforcing: %d\n", security_getenforce());

    /* 2. Отримання контексту поточного процесу з /proc/self/attr/current */
    if (getcon(&process_con) < 0) {
        perror("Помилка виконання getcon");
        return 1;
    }
    printf("Контекст поточного процесу: %s\n", process_con);

    /* 3. Отримання контексту файлу через розширений атрибут security.selinux */
    const char *target_file = (argc > 1) ? argv[1] : "/etc/passwd";
    if (getfilecon(target_file, &file_con) < 0) {
        perror("Помилка виконання getfilecon");
        freecon(process_con);
        return 1;
    }
    printf("Контекст файлу (%s): %s\n", target_file, file_con);

    /* 4. Звільнення пам'яті, виділеної бібліотекою libselinux */
    freecon(process_con);
    freecon(file_con);
    return 0;
}
