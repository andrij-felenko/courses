#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Вказівник на функцію-перехідник у C: приймає контекст та аргумент */
typedef void (*c_callback_t)(void* user_data, int event_id);

/* Структура для зберігання обробника події */
typedef struct {
    void* user_data;
    c_callback_t invoke;
    void (*destroy)(void* user_data);
} c_event_handler_t;

/* Приклад 1: Простий обробник без стану */
void simple_trampoline(void* user_data, int event_id) {
    (void)user_data;
    printf("[C Simple] Received event: %d\n", event_id);
}

/* Приклад 2: Обробник зі станом (структура у купі) */
typedef struct {
    char prefix[32];
    int counter;
} logger_context_t;

void logger_trampoline(void* user_data, int event_id) {
    logger_context_t* ctx = (logger_context_t*)user_data;
    ctx->counter++;
    printf("[C Logger %s #%d] Event ID: %d\n", ctx->prefix, ctx->counter, event_id);
}

void logger_destroy(void* user_data) {
    free(user_data);
}

/* Ініціалізація обробника зі станом */
c_event_handler_t create_logger(const char* prefix) {
    logger_context_t* ctx = (logger_context_t*)malloc(sizeof(logger_context_t));
    strncpy(ctx->prefix, prefix, sizeof(ctx->prefix) - 1);
    ctx->prefix[sizeof(ctx->prefix) - 1] = '\0';
    ctx->counter = 0;

    c_event_handler_t handler;
    handler.user_data = ctx;
    handler.invoke = logger_trampoline;
    handler.destroy = logger_destroy;
    return handler;
}

void execute_c_handler(const c_event_handler_t* handler, int event_id) {
    if (handler->invoke) {
        handler->invoke(handler->user_data, event_id);
    }
}

void free_c_handler(c_event_handler_t* handler) {
    if (handler->destroy && handler->user_data) {
        handler->destroy(handler->user_data);
        handler->user_data = NULL;
    }
}

int main(void) {
    c_event_handler_t h1 = { NULL, simple_trampoline, NULL };
    c_event_handler_t h2 = create_logger("NetworkSubsystem");

    execute_c_handler(&h1, 101);
    execute_c_handler(&h2, 202);
    execute_c_handler(&h2, 203);

    free_c_handler(&h2);
    return 0;
}
