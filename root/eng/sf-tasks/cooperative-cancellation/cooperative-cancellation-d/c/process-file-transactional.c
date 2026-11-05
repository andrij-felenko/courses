/* Приклад транзакційного відкату та очищення ресурсів у C */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <unistd.h>

typedef struct {
    atomic_bool cancel_requested;
} cancel_token_t;

bool process_file_transactional(const char *temp_path, const char *final_path, cancel_token_t *token) {
    FILE *f = fopen(temp_path, "w");
    if (!f) return false;

    bool success = false;
    for (int step = 0; step < 100; ++step) {
        /* Точка скасування (checkpoint) */
        if (atomic_load(&token->cancel_requested)) {
            printf("Отримано сигнал скасування у точці %d. Починаємо відкат...\n", step);
            goto cleanup;
        }

        fprintf(f, "Порція даних %d\n", step);
        usleep(10000); /* Імітація роботи */
    }

    success = true;

cleanup:
    /* Блок гарантованого очищення ресурсів */
    if (f) {
        fclose(f);
    }

    if (!success) {
        /* Транзакційний відкат: видалення незавершеного тимчасового файла */
        unlink(temp_path);
        printf("Транзакційний відкат виконано: тимчасовий файл видалено.\n");
    } else {
        rename(temp_path, final_path);
        printf("Транзакцію успішно зафіксовано.\n");
    }

    return success;
}
