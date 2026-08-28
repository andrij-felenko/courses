#include "engine_api.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Користувацька структура стану для зворотного виклику */
typedef struct AppStats {
    size_t total_processed;
    int chunk_count;
} AppStats;

static void on_progress(size_t bytes, void* user_data) {
    AppStats* stats = (AppStats*)user_data;
    if (stats) {
        stats->total_processed += bytes;
        stats->chunk_count++;
        printf("[C Client] Оброблено фрагмент: %zu байтів (разом: %zu, викликів: %d)\n",
               bytes, stats->total_processed, stats->chunk_count);
    }
}

int main(void) {
    engine_ctx_t* ctx = NULL;
    engine_status_t st = engine_create("XOR-FAST", &ctx);
    if (st != ENGINE_STATUS_OK) {
        fprintf(stderr, "[C Client] Помилка створення: %s\n", engine_get_last_error());
        return EXIT_FAILURE;
    }

    AppStats stats = { 0, 0 };
    st = engine_set_progress_callback(ctx, on_progress, &stats, NULL);
    if (st != ENGINE_STATUS_OK) {
        fprintf(stderr, "[C Client] Помилка реєстрації callback: %s\n", engine_get_last_error());
        engine_destroy(ctx);
        return EXIT_FAILURE;
    }

    const uint8_t payload[] = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08 };
    uint8_t buffer[32];
    size_t out_len = sizeof(buffer);

    st = engine_process(ctx, payload, sizeof(payload), buffer, &out_len);
    if (st != ENGINE_STATUS_OK) {
        fprintf(stderr, "[C Client] Помилка обробки: %s\n", engine_get_last_error());
        engine_destroy(ctx);
        return EXIT_FAILURE;
    }

    printf("[C Client] Успішно отримано %zu байтів. Перший байт результату: 0x%02X\n",
           out_len, buffer[0]);

    engine_destroy(ctx);
    return EXIT_SUCCESS;
}
