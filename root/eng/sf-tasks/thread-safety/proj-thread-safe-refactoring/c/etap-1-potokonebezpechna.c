#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Прихований статичний стан розбору та глобальні лічильники */
static char *g_last_token_ptr = NULL;
static unsigned long g_total_bytes = 0;
static unsigned long g_error_count = 0;

char *log_parser_next_token_unsafe(char *log_line, const char *delimiter) {
    if (log_line != NULL) {
        g_last_token_ptr = log_line;
    }
    if (g_last_token_ptr == NULL || *g_last_token_ptr == '\0') {
        return NULL;
    }

    char *start = g_last_token_ptr;
    char *end = strpbrk(start, delimiter);
    if (end != NULL) {
        *end = '\0';
        g_last_token_ptr = end + 1;
    } else {
        g_last_token_ptr = NULL;
    }
    return start;
}

void log_parser_record_metric_unsafe(int status_code, unsigned long bytes) {
    g_total_bytes += bytes;
    if (status_code >= 400) {
        g_error_count++;
    }
}
