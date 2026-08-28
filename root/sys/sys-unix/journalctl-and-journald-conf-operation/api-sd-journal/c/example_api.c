/* example_api.c — повний приклад відправки та фільтрації C API */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <systemd/sd-journal.h>

void send_structured_log_c(void) {
    int res = sd_journal_send(
        "MESSAGE=Старт обробки транзакції клієнта",
        "PRIORITY=%d", LOG_NOTICE,
        "TRANSACTION_ID=TX-9948201",
        "AMOUNT_CENT=150000",
        "CURRENCY=UAH",
        "CODE_FILE=%s", __FILE__,
        "CODE_LINE=%d", __LINE__,
        NULL
    );

    if (res < 0) {
        fprintf(stderr, "Не вдалося відправити лог у journald: %s\n", strerror(-res));
    }
}

void poll_journal_events_c(void) {
    sd_journal *j = NULL;
    if (sd_journal_open(&j, SD_JOURNAL_LOCAL_ONLY) < 0) return;

    /* Фільтруємо логи системного сервісу sshd */
    sd_journal_add_match(j, "_SYSTEMD_UNIT=sshd.service", 0);
    sd_journal_seek_tail(j);

    printf("Очікування нових подій від sshd.service...\n");
    for (int i = 0; i < 3; ++i) {
        /* Чекаємо нових даних на сокеті (таймаут 5 секунд) */
        int r = sd_journal_wait(j, 5000000);
        if (r == SD_JOURNAL_NOP) {
            printf("Таймаут очікування подій...\n");
            continue;
        }

        while (sd_journal_next(j) > 0) {
            const void *msg = NULL;
            size_t len = 0;
            if (sd_journal_get_data(j, "MESSAGE", &msg, &len) >= 0) {
                printf("Нова подія: %.*s\n", (int)len, (const char*)msg);
            }
        }
    }

    sd_journal_close(j);
}
