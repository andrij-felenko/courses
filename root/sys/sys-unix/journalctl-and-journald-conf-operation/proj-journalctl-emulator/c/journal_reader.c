/* journal_reader.c — читач логів systemd мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <systemd/sd-journal.h>

#define MAX_CURSOR_LEN 512

static void print_field(sd_journal *j, const char *field_name) {
    const void *data = NULL;
    size_t length = 0;

    int r = sd_journal_get_data(j, field_name, &data, &length);
    if (r < 0) {
        if (r == -ENOENT) {
            printf("  %s: <відсутнє>\n", field_name);
        } else {
            fprintf(stderr, "Помилка читання поля %s: %s\n", field_name, strerror(-r));
        }
        return;
    }

    /* Зчитуване поле повертається у форматі 'FIELD_NAME=value' */
    const char *eq = memchr(data, '=', length);
    if (eq) {
        size_t val_len = length - (eq - (const char*)data) - 1;
        printf("  %s: %.*s\n", field_name, (int)val_len, eq + 1);
    }
}

int main(int argc, char *argv[]) {
    const char *target_unit = (argc > 1) ? argv[1] : "sshd.service";
    sd_journal *j = NULL;

    /* 1. Відкриття локального журналу */
    int r = sd_journal_open(&j, SD_JOURNAL_LOCAL_ONLY);
    if (r < 0) {
        fprintf(stderr, "Не вдалося відкрити журнал: %s\n", strerror(-r));
        return EXIT_FAILURE;
    }

    printf("=== Аналіз логів юніта: %s ===\n", target_unit);

    /* 2. Додавання умов фільтрації */
    char match_buf[256];
    snprintf(match_buf, sizeof(match_buf), "_SYSTEMD_UNIT=%s", target_unit);

    r = sd_journal_add_match(j, match_buf, 0);
    if (r < 0) {
        fprintf(stderr, "Помилка встановлення фільтра юніта: %s\n", strerror(-r));
        sd_journal_close(j);
        return EXIT_FAILURE;
    }

    /* 3. Позиціонування на кінець журналу */
    r = sd_journal_seek_tail(j);
    if (r < 0) {
        fprintf(stderr, "Помилка позиціонування tail: %s\n", strerror(-r));
        sd_journal_close(j);
        return EXIT_FAILURE;
    }

    /* 4. Читання записів у зворотному напрямку */
    int count = 0;
    while ((r = sd_journal_previous(j)) > 0 && count < 5) {
        count++;
        printf("\nЗапис #%d:\n", count);

        print_field(j, "_SYSTEMD_UNIT");
        print_field(j, "_PID");
        print_field(j, "_UID");
        print_field(j, "PRIORITY");
        print_field(j, "MESSAGE");

        /* Отримання курсора для збереження стану */
        char *cursor = NULL;
        if (sd_journal_get_cursor(j, &cursor) >= 0) {
            printf("  Cursor: %s\n", cursor);
            free(cursor); // Курсор виділено динамічно бібліотекою
        }
    }

    if (r < 0) {
        fprintf(stderr, "Помилка ітерації журналу: %s\n", strerror(-r));
    }

    /* 5. Чисте звільнення ресурсів */
    sd_journal_close(j);
    return EXIT_SUCCESS;
}
