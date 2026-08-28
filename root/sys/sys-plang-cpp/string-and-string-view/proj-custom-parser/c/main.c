// C11: Аналогічний парсер з використанням вказівників та довжин (Zero-Copy)
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

typedef struct {
    const char* ptr;
    size_t      len;
} StringViewC;

typedef struct {
    StringViewC timestamp;
    StringViewC level;
    StringViewC module;
    StringViewC message;
} LogEntryC;

static bool parse_tag(const char** cursor, const char* end, StringViewC* out) {
    const char* open = memchr(*cursor, '[', end - *cursor);
    if (!open) return false;

    const char* close = memchr(open + 1, ']', end - (open + 1));
    if (!close) return false;

    out->ptr = open + 1;
    out->len = close - (open + 1);

    *cursor = close + 1;
    return true;
}

bool parse_line_c(const char* line, size_t line_len, LogEntryC* out) {
    const char* cursor = line;
    const char* end = line + line_len;

    if (!parse_tag(&cursor, end, &out->timestamp)) return false;
    if (!parse_tag(&cursor, end, &out->level)) return false;
    if (!parse_tag(&cursor, end, &out->module)) return false;

    // Пропускаємо пробіли для повідомлення
    while (cursor < end && (*cursor == ' ' || *cursor == '\t')) {
        cursor++;
    }

    out->message.ptr = cursor;
    out->message.len = end - cursor;

    return true;
}

void print_sv(const char* label, StringViewC sv) {
    printf("%s: %.*s\n", label, (int)sv.len, sv.ptr);
}

int main(void) {
    const char log_data[] = 
        "[2026-08-14T19:00:00.123] [ERROR] [NETWORKING] Socket connection reset by peer\n"
        "[2026-08-14T19:00:00.125] [INFO] [DATABASE] Query executed successfully";

    size_t total_len = sizeof(log_data) - 1;
    size_t line_start = 0;

    while (line_start < total_len) {
        const char* current = log_data + line_start;
        const char* next_line = memchr(current, '\n', total_len - line_start);
        size_t line_len = next_line ? (size_t)(next_line - current) : (total_len - line_start);

        LogEntryC entry;
        if (parse_line_c(current, line_len, &entry)) {
            printf("Parsed Log Entry (C):\n");
            print_sv("  Time   ", entry.timestamp);
            print_sv("  Level  ", entry.level);
            print_sv("  Module ", entry.module);
            print_sv("  Message", entry.message);
            printf("\n");
        }

        line_start += line_len + 1;
    }
    return 0;
}
