#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

/* Оголошення C-API */
typedef void (*data_ready_cb)(const uint8_t* data, size_t len, void* user_data);
void stream_register_handler(data_ready_cb cb, void* user_data);

/* Структура користувацького контексту в C-коді */
typedef struct ConsumerContext {
    size_t total_received;
    FILE*  log_file;
} ConsumerContext;

/* Звичайна C-функція зворотного виклику */
static void on_data_chunk(const uint8_t* data, size_t len, void* user_data) {
    ConsumerContext* ctx = (ConsumerContext*)user_data;
    if (ctx && data) {
        ctx->total_received += len;
        fprintf(ctx->log_file, "Отримано %zu байтів (разом: %zu)\n", len, ctx->total_received);
    }
}

int main(void) {
    ConsumerContext app_state;
    app_state.total_received = 0;
    app_state.log_file = stdout;

    /* Реєструємо функцію та покажчик на стан */
    stream_register_handler(on_data_chunk, &app_state);
    return 0;
}
