#include <systemd/sd-daemon.h>

/* Повідомляємо systemd, що порт відкрито і сервіс готовий до роботи */
void notify_systemd_ready(void) {
    sd_notify(0, "READY=1\nSTATUS=Сервер обробляє клієнтські запити");
}

/* Періодичне надсилання сигналів сторожовому таймеру (Watchdog) */
void notify_systemd_watchdog(void) {
    sd_notify(0, "WATCHDOG=1");
}
