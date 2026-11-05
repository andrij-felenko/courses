#include <stdio.h>
#include <string.h>

// Структура контексту, яка виділяється викликачем на стекі
typedef struct {
    char log_buffer[256];
    size_t write_pos;
} LogContext;

// Ініціалізація контексту перед використанням
void log_context_init(LogContext *ctx) {
    if (!ctx) return;
    ctx->write_pos = 0;
    ctx->log_buffer[0] = '\0';
}

// Повністю реентерабельна функція додавання тексту
void reentrant_log_append(LogContext *ctx, const char *text) {
    if (!ctx || !text) return;
    
    for (size_t i = 0; text[i] != '\0'; i++) {
        if (ctx->write_pos < sizeof(ctx->log_buffer) - 1) {
            ctx->log_buffer[ctx->write_pos] = text[i];
            ctx->write_pos++;
        }
    }
    ctx->log_buffer[ctx->write_pos] = '\0';
}

// Обробник сигналу використовує свій власний ізольований контекст на стекі
void safe_signal_handler(int sig) {
    (void)sig;
    LogContext signal_ctx;
    log_context_init(&signal_ctx);
    reentrant_log_append(&signal_ctx, "[SIGNAL_SAFE] Executed safely!");
}
