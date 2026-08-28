#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/timex.h>

int schedule_leap_insertion(void) {
    struct timex tx;
    memset(&tx, 0, sizeof(tx));

    // Зчитуємо поточні параметри ядра
    if (adjtimex(&tx) < 0) {
        perror("Помилка зчитування параметрів через adjtimex");
        return -1;
    }

    // Додаємо прапорець вставки та знімаємо прапорець видалення
    tx.modes = ADJ_STATUS;
    tx.status |= STA_INS;
    tx.status &= ~STA_DEL;

    int state = adjtimex(&tx);
    if (state < 0) {
        if (errno == EPERM) {
            fprintf(stderr, "Помилка: потрібні права CAP_SYS_TIME для керування годинником!\n");
        } else {
            perror("Помилка запису нового статусу в adjtimex");
        }
        return -1;
    }

    printf("Прапорець STA_INS успішно встановлено. Поточний стан ядра: %d (TIME_INS)\n", state);
    return 0;
}
