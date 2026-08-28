/* Приклад використання Syslog C API */
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <syslog.h>

int main(void) {
    /* Ініціалізуємо підключення: додаємо PID та виводимо на stderr у разі потреби */
    openlog("demo_service", LOG_PID | LOG_PERROR, LOG_DAEMON);

    /* Налаштовуємо маску: ігноруємо LOG_DEBUG */
    setlogmask(LOG_UPTO(LOG_INFO));

    syslog(LOG_INFO, "Службу успішно запущено.");

    FILE *f = fopen("/nonexistent/file.txt", "r");
    if (!f) {
        /* %m автоматично підставить опис errno (strerror) */
        syslog(LOG_ERR, "Не вдалося відкрити конфігураційний файл: %m");
    }

    /* Це повідомлення буде відфільтровано на боці клієнта функцією setlogmask */
    syslog(LOG_DEBUG, "Це налагоджувальне повідомлення не потрапить у лог.");

    closelog();
    return 0;
}
