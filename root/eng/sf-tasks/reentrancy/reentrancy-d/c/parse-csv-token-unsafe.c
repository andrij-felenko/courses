#include <stdio.h>
#include <string.h>
#include <stdbool.h>

// НЕРЕЕНТЕРАБЕЛЬНИЙ ПАРСЕР: зберігає позицію у статичних змінних.
// Спроба розібрати другий рядок всередині цикла розбору першого рядка
// або переривання обробником сигналів повністю зруйнує стан.
char* parse_csv_token_unsafe(char* input, char delimiter) {
    static char* current_ptr = NULL; // Неявний статичний стан!

    if (input != NULL) {
        current_ptr = input;
    }

    if (current_ptr == NULL || *current_ptr == '\0') {
        return NULL;
    }

    char* token_start = current_ptr;
    while (*current_ptr != '\0' && *current_ptr != delimiter) {
        current_ptr++;
    }

    if (*current_ptr == delimiter) {
        *current_ptr = '\0';
        current_ptr++;
    }

    return token_start;
}

// РЕЕНТЕРАБЕЛЬНИЙ ПАРСЕР: весь стан винесено у структуру контексту.
typedef struct {
    char* current_ptr;
    char delimiter;
    size_t tokens_parsed;
} csv_parser_ctx_t;

void csv_parser_init(csv_parser_ctx_t* ctx, char* input, char delimiter) {
    if (ctx) {
        ctx->current_ptr = input;
        ctx->delimiter = delimiter;
        ctx->tokens_parsed = 0;
    }
}

char* parse_csv_token_reentrant(csv_parser_ctx_t* ctx) {
    if (!ctx || !ctx->current_ptr || *ctx->current_ptr == '\0') {
        return NULL;
    }

    char* token_start = ctx->current_ptr;
    while (*ctx->current_ptr != '\0' && *ctx->current_ptr != ctx->delimiter) {
        ctx->current_ptr++;
    }

    if (*ctx->current_ptr == ctx->delimiter) {
        *ctx->current_ptr = '\0';
        ctx->current_ptr++;
    }

    ctx->tokens_parsed++;
    return token_start;
}
