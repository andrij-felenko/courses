#include <systemd/sd-daemon.h>
#include <stdio.h>
#include <unistd.h>

int main(void) {
    /* Налаштовуємо буферизацію */
    setvbuf(stdout, NULL, _IOLBF, 0);

    printf("Ініціалізація компонентів...\n");
    sleep(1); /* Емуляція завантаження */

    /* Повідомляємо systemd про повну готовність */
    sd_notify(0, "READY=1\nSTATUS=Обробка клієнтських запитів");

    /* Головний цикл обробки */
    while (1) {
        sleep(10);
    }
    return 0;
}
