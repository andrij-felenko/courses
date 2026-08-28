#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <systemd/sd-daemon.h>

int main(void) {
    printf("Starting worker initialization...\n");

    // Імітація тривалої підготовки (завантаження даних, прив'язка до портів)
    sleep(2);

    // Сповіщаємо systemd про готовність та передаємо початковий статус
    int res = sd_notify(0, "READY=1\nSTATUS=Worker initialized, awaiting jobs.");
    if (res < 0) {
        fprintf(stderr, "Failed to send notification: %d\n", res);
    } else if (res == 0) {
        printf("NOTIFY_SOCKET is not set. Running standalone.\n");
    } else {
        printf("Notification successfully sent to systemd.\n");
    }

    // Головний цикл програми
    for (int i = 0; i < 5; ++i) {
        sleep(1);
        sd_notify(0, "WATCHDOG=1");
    }

    sd_notify(0, "STOPPING=1\nSTATUS=Shutting down gracefully.");
    return 0;
}
