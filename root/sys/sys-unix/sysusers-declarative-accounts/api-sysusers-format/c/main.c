#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

#define MAX_LINE_LEN 512
#define MAX_FIELD_LEN 128

typedef enum {
    ENTRY_USER = 'u',
    ENTRY_GROUP = 'g',
    ENTRY_MEMBER = 'm',
    ENTRY_RANGE = 'r',
    ENTRY_UNKNOWN = 0
} sysuser_type_t;

typedef struct {
    sysuser_type_t type;
    char name[MAX_FIELD_LEN];
    char id[MAX_FIELD_LEN];
    char gecos[MAX_FIELD_LEN];
    char home[MAX_FIELD_LEN];
    char shell[MAX_FIELD_LEN];
    bool force_fatal;
} sysuser_entry_t;

static void trim_leading_ws(const char **str) {
    while (**str && isspace((unsigned char)**str)) {
        (*str)++;
    }
}

static bool parse_token(const char **cursor, char *buffer, size_t buf_size) {
    trim_leading_ws(cursor);
    if (**cursor == '\0') {
        return false;
    }

    size_t idx = 0;
    bool in_quotes = false;

    while (**cursor != '\0') {
        char ch = **cursor;
        if (ch == '"') {
            in_quotes = !in_quotes;
            (*cursor)++;
            continue;
        }
        if (!in_quotes && isspace((unsigned char)ch)) {
            break;
        }
        if (idx < buf_size - 1) {
            buffer[idx++] = ch;
        }
        (*cursor)++;
    }
    buffer[idx] = '\0';
    return true;
}

bool parse_sysusers_line(const char *line, sysuser_entry_t *entry) {
    if (!line || !entry) return false;
    memset(entry, 0, sizeof(*entry));

    const char *cursor = line;
    trim_leading_ws(&cursor);

    if (*cursor == '\0' || *cursor == '#') {
        return false; // Коментар або порожній рядок
    }

    char type_tok[MAX_FIELD_LEN] = {0};
    if (!parse_token(&cursor, type_tok, sizeof(type_tok))) return false;

    if (strlen(type_tok) != 1) return false;
    entry->type = (sysuser_type_t)type_tok[0];

    if (!parse_token(&cursor, entry->name, sizeof(entry->name))) return false;

    // Перевірка прапорця !
    if (entry->name[0] == '!') {
        entry->force_fatal = true;
        memmove(entry->name, entry->name + 1, strlen(entry->name));
    }

    if (entry->type == ENTRY_USER) {
        parse_token(&cursor, entry->id, sizeof(entry->id));
        parse_token(&cursor, entry->gecos, sizeof(entry->gecos));
        parse_token(&cursor, entry->home, sizeof(entry->home));
        parse_token(&cursor, entry->shell, sizeof(entry->shell));
    } else if (entry->type == ENTRY_GROUP || entry->type == ENTRY_RANGE) {
        parse_token(&cursor, entry->id, sizeof(entry->id));
    } else if (entry->type == ENTRY_MEMBER) {
        parse_token(&cursor, entry->id, sizeof(entry->id)); // Назва групи
    }

    return true;
}
