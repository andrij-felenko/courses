#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <regex.h>
#include <stdbool.h>

typedef enum {
    CMD_SUBST,
    CMD_PRINT,
    CMD_DELETE,
    CMD_HOLD_COPY,
    CMD_HOLD_APPEND,
    CMD_GET_COPY,
    CMD_GET_APPEND,
    CMD_EXCHANGE,
    CMD_NEXT_APPEND
} CommandType;

typedef struct {
    CommandType type;
    int line_addr;          /* 0 якщо адреси за номером немає */
    char *regex_addr_str;
    regex_t regex_addr;
    bool has_regex_addr;
    char *subst_pattern;
    char *subst_replacement;
    bool subst_global;
} SedCommand;

typedef struct {
    char *pattern_space;
    size_t pattern_len;
    size_t pattern_cap;

    char *hold_space;
    size_t hold_len;
    size_t hold_cap;

    size_t line_number;
    bool quiet_mode;
    bool deleted;
    bool subst_success;
} SedEngine;

static void buf_set(char **buf, size_t *len, size_t *cap, const char *src) {
    size_t slen = strlen(src);
    if (slen + 1 > *cap) {
        *cap = slen + 64;
        *buf = (char *)realloc(*buf, *cap);
    }
    memcpy(*buf, src, slen + 1);
    *len = slen;
}

static void buf_append(char **buf, size_t *len, size_t *cap, char sep, const char *src) {
    size_t slen = strlen(src);
    size_t needed = *len + (sep ? 1 : 0) + slen + 1;
    if (needed > *cap) {
        *cap = needed + 64;
        *buf = (char *)realloc(*buf, *cap);
    }
    if (sep && *len > 0) {
        (*buf)[(*len)++] = sep;
    }
    memcpy(*buf + *len, src, slen + 1);
    *len += slen;
}

static void engine_init(SedEngine *eng, bool quiet) {
    eng->pattern_space = (char *)malloc(128);
    eng->pattern_space[0] = '\0';
    eng->pattern_len = 0;
    eng->pattern_cap = 128;

    eng->hold_space = (char *)malloc(128);
    eng->hold_space[0] = '\0';
    eng->hold_len = 0;
    eng->hold_cap = 128;

    eng->line_number = 0;
    eng->quiet_mode = quiet;
    eng->deleted = false;
    eng->subst_success = false;
}

static void engine_free(SedEngine *eng) {
    free(eng->pattern_space);
    free(eng->hold_space);
}

static bool perform_subst(SedEngine *eng, const char *pattern, const char *rep, bool global) {
    regex_t re;
    if (regcomp(&re, pattern, REG_EXTENDED) != 0) {
        return false;
    }

    regmatch_t match;
    const char *cursor = eng->pattern_space;
    char *result = NULL;
    size_t res_len = 0, res_cap = 0;
    bool replaced = false;

    while (regexec(&re, cursor, 1, &match, 0) == 0) {
        replaced = true;
        size_t prefix_len = match.rm_so;
        size_t match_len = match.rm_eo - match.rm_so;
        size_t rep_len = strlen(rep);

        size_t needed = res_len + prefix_len + rep_len + 1;
        if (needed > res_cap) {
            res_cap = needed + 128;
            result = (char *)realloc(result, res_cap);
        }

        memcpy(result + res_len, cursor, prefix_len);
        res_len += prefix_len;
        memcpy(result + res_len, rep, rep_len);
        res_len += rep_len;
        result[res_len] = '\0';

        cursor += match.rm_eo;
        if (!global) {
            break;
        }
        if (match_len == 0 && *cursor != '\0') {
            result[res_len++] = *cursor;
            result[res_len] = '\0';
            cursor++;
        }
    }

    if (replaced) {
        size_t suffix_len = strlen(cursor);
        size_t needed = res_len + suffix_len + 1;
        if (needed > res_cap) {
            res_cap = needed;
            result = (char *)realloc(result, res_cap);
        }
        memcpy(result + res_len, cursor, suffix_len + 1);
        res_len += suffix_len;

        free(eng->pattern_space);
        eng->pattern_space = result;
        eng->pattern_len = res_len;
        eng->pattern_cap = res_cap;
    } else {
        free(result);
    }

    regfree(&re);
    return replaced;
}

static void execute_command(SedEngine *eng, SedCommand *cmd, FILE *in) {
    /* Перевірка адреси за номером рядка */
    if (cmd->line_addr > 0 && (size_t)cmd->line_addr != eng->line_number) {
        return;
    }
    /* Перевірка адреси за регулярним виразом */
    if (cmd->has_regex_addr) {
        if (regexec(&cmd->regex_addr, eng->pattern_space, 0, NULL, 0) != 0) {
            return;
        }
    }

    switch (cmd->type) {
        case CMD_SUBST:
            if (perform_subst(eng, cmd->subst_pattern, cmd->subst_replacement, cmd->subst_global)) {
                eng->subst_success = true;
            }
            break;
        case CMD_PRINT:
            puts(eng->pattern_space);
            break;
        case CMD_DELETE:
            eng->deleted = true;
            break;
        case CMD_HOLD_COPY:
            buf_set(&eng->hold_space, &eng->hold_len, &eng->hold_cap, eng->pattern_space);
            break;
        case CMD_HOLD_APPEND:
            buf_append(&eng->hold_space, &eng->hold_len, &eng->hold_cap, '\n', eng->pattern_space);
            break;
        case CMD_GET_COPY:
            buf_set(&eng->pattern_space, &eng->pattern_len, &eng->pattern_cap, eng->hold_space);
            break;
        case CMD_GET_APPEND:
            buf_append(&eng->pattern_space, &eng->pattern_len, &eng->pattern_cap, '\n', eng->hold_space);
            break;
        case CMD_EXCHANGE: {
            char *tmp_buf = eng->pattern_space;
            size_t tmp_len = eng->pattern_len;
            size_t tmp_cap = eng->pattern_cap;
            eng->pattern_space = eng->hold_space;
            eng->pattern_len = eng->hold_len;
            eng->pattern_cap = eng->hold_cap;
            eng->hold_space = tmp_buf;
            eng->hold_len = tmp_len;
            eng->hold_cap = tmp_cap;
            break;
        }
        case CMD_NEXT_APPEND: {
            char *next_line = NULL;
            size_t ncap = 0;
            ssize_t nread = getline(&next_line, &ncap, in);
            if (nread > 0) {
                if (next_line[nread - 1] == '\n') next_line[--nread] = '\0';
                buf_append(&eng->pattern_space, &eng->pattern_len, &eng->pattern_cap, '\n', next_line);
                eng->line_number++;
            }
            free(next_line);
            break;
        }
    }
}

int main(void) {
    SedEngine eng;
    engine_init(&eng, false);

    SedCommand cmds[2];
    cmds[0].type = CMD_SUBST;
    cmds[0].line_addr = 0;
    cmds[0].has_regex_addr = false;
    cmds[0].subst_pattern = "WARN";
    cmds[0].subst_replacement = "ALERT";
    cmds[0].subst_global = true;

    cmds[1].type = CMD_PRINT;
    cmds[1].line_addr = 0;
    cmds[1].has_regex_addr = false;

    char *line = NULL;
    size_t linecap = 0;
    ssize_t linelen;

    while ((linelen = getline(&line, &linecap, stdin)) > 0) {
        if (line[linelen - 1] == '\n') {
            line[--linelen] = '\0';
        }
        eng.line_number++;
        eng.deleted = false;
        buf_set(&eng.pattern_space, &eng.pattern_len, &eng.pattern_cap, line);

        for (int i = 0; i < 2; ++i) {
            execute_command(&eng, &cmds[i], stdin);
            if (eng.deleted) break;
        }

        if (!eng.deleted && !eng.quiet_mode) {
            puts(eng.pattern_space);
        }
    }

    free(line);
    engine_free(&eng);
    return 0;
}
