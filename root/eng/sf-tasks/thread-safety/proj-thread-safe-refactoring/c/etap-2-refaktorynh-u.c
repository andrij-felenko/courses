#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Контекст розбору, що живе виключно на стеку викликача */
typedef struct {
    char *cursor;
} LogParserContext;

void log_parser_context_init(LogParserContext *ctx, char *log_line) {
    if (ctx != NULL) {
        ctx->cursor = log_line;
    }
}

char *log_parser_next_token_r(LogParserContext *ctx, const char *delimiter) {
    if (ctx == NULL || ctx->cursor == NULL || *ctx->cursor == '\0') {
        return NULL;
    }

    char *start = ctx->cursor;
    char *end = strpbrk(start, delimiter);
    if (end != NULL) {
        *end = '\0';
        ctx->cursor = end + 1;
    } else {
        ctx->cursor = NULL;
    }
    return start;
}
