/* C: Тестовий демон для перевірки обмежень SELinux Type Enforcement */
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

int main(void) {
    printf("=== Запуск перевірки доступу демона mydaemon ===\n");

    /* 1. Спроба запису у власний лог-файл (Дозволено правилом allow у mydaemon.te) */
    const char *log_path = "/var/log/mydaemon.log";
    int log_fd = open(log_path, O_WRONLY | O_CREAT | O_APPEND, 0640);
    if (log_fd < 0) {
        fprintf(stderr, "[ПОМИЛКА] Запис у лог %s відхилено: %s\n", log_path, strerror(errno));
    } else {
        const char *msg = "Демон успішно стартував і записав лог під доменом mydaemon_t.\n";
        write(log_fd, msg, strlen(msg));
        close(log_fd);
        printf("[ОК] Запис у власний лог-файл пройшов успішно.\n");
    }

    /* 2. Спроба читання чужого файла /etc/shadow (Заборонено політики SELinux TE) */
    const char *shadow_path = "/etc/shadow";
    int shadow_fd = open(shadow_path, O_RDONLY);
    if (shadow_fd < 0) {
        printf("[ОК] Спробу читання %s заблоковано SELinux! Причина: %s (errno=%d)\n", 
               shadow_path, strerror(errno), errno);
    } else {
        fprintf(stderr, "[УВАГА] Порушення безпеки: демон зміг прочитати %s!\n", shadow_path);
        close(shadow_fd);
    }

    return 0;
}
