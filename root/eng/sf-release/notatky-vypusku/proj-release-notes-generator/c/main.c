#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

#define MAX_ENTRIES 128
#define MAX_STR_LEN 256

typedef enum {
    CAT_BREAKING = 0,
    CAT_SECURITY,
    CAT_FEATURE,
    CAT_FIX,
    CAT_IGNORE,
    CAT_COUNT
} Category;

typedef struct {
    char type[32];
    char scope[32];
    char description[MAX_STR_LEN];
    char cve[32];
    bool is_breaking;
    Category category;
} CommitEntry;

static void trim_spaces(char *str) {
    char *end;
    while (isspace((unsigned char)*str)) str++;
    end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;
    *(end + 1) = '\0';
}

static CommitEntry parse_commit(const char *raw_line) {
    CommitEntry entry;
    memset(&entry, 0, sizeof(entry));
    entry.category = CAT_IGNORE;

    char buffer[MAX_STR_LEN * 2];
    strncpy(buffer, raw_line, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';

    /* Перевірка наявності мітки вразливості CVE */
    const char *cve_pos = strstr(buffer, "CVE-");
    if (cve_pos) {
        int i = 0;
        while (cve_pos[i] && !isspace((unsigned char)cve_pos[i]) && cve_pos[i] != ')' && i < 31) {
            entry.cve[i] = cve_pos[i];
            i++;
        }
        entry.cve[i] = '\0';
    }

    /* Перевірка футера або маркера BREAKING CHANGE */
    if (strstr(buffer, "BREAKING CHANGE:") != NULL) {
        entry.is_breaking = true;
    }

    char *colon = strchr(buffer, ':');
    if (!colon) return entry;

    *colon = '\0';
    char *header = buffer;
    char *desc = colon + 1;
    while (isspace((unsigned char)*desc)) desc++;
    strncpy(entry.description, desc, sizeof(entry.description) - 1);

    /* Розбір типу, скоупу та знака оклику */
    char *open_paren = strchr(header, '(');
    char *close_paren = strchr(header, ')');
    char *excl = strchr(header, '!');

    if (excl) {
        entry.is_breaking = true;
    }

    if (open_paren && close_paren && close_paren > open_paren) {
        *open_paren = '\0';
        *close_paren = '\0';
        strncpy(entry.type, header, sizeof(entry.type) - 1);
        strncpy(entry.scope, open_paren + 1, sizeof(entry.scope) - 1);
    } else {
        if (excl) *excl = '\0';
        strncpy(entry.type, header, sizeof(entry.type) - 1);
    }

    trim_spaces(entry.type);
    trim_spaces(entry.scope);
    trim_spaces(entry.description);

    /* Визначення результуючої категорії */
    if (entry.is_breaking) {
        entry.category = CAT_BREAKING;
    } else if (entry.cve[0] != '\0' || strcmp(entry.type, "sec") == 0 || strcmp(entry.scope, "sec") == 0) {
        entry.category = CAT_SECURITY;
    } else if (strcmp(entry.type, "feat") == 0) {
        entry.category = CAT_FEATURE;
    } else if (strcmp(entry.type, "fix") == 0) {
        entry.category = CAT_FIX;
    } else {
        entry.category = CAT_IGNORE;
    }

    return entry;
}

void generate_release_notes(const char *version, const char *date, const char *raw_commits[], size_t count) {
    CommitEntry entries[MAX_ENTRIES];
    size_t valid_count = 0;

    for (size_t i = 0; i < count && valid_count < MAX_ENTRIES; ++i) {
        CommitEntry e = parse_commit(raw_commits[i]);
        if (e.category != CAT_IGNORE) {
            entries[valid_count++] = e;
        }
    }

    printf("# Нотатки випуску %s (%s)\n\n", version, date);

    const char *headers[CAT_COUNT] = {
        "## 🔴 Обов'язкові дії та несумісні зміни (Breaking Changes)",
        "## 🔒 Бюлетені безпеки (Security Advisories)",
        "## ✨ Нові можливості (Features)",
        "## 🐛 Виправлення дефектів (Bug Fixes)",
        ""
    };

    for (int cat = 0; cat < CAT_IGNORE; ++cat) {
        bool has_items = false;
        for (size_t i = 0; i < valid_count; ++i) {
            if (entries[i].category == (Category)cat) {
                if (!has_items) {
                    printf("%s\n\n", headers[cat]);
                    has_items = true;
                }
                if (entries[i].scope[0] != '\0') {
                    printf("- **%s:** %s", entries[i].scope, entries[i].description);
                } else {
                    printf("- %s", entries[i].description);
                }

                if (entries[i].cve[0] != '\0') {
                    printf(" (`%s`)", entries[i].cve);
                }
                printf("\n");
            }
        }
        if (has_items) printf("\n");
    }
}

int main(void) {
    const char *sample_commits[] = {
        "feat(can)!: перейти на бітову швидкість CAN-FD 2 Мбіт/с",
        "fix(adc): виправити дрейф нульового рівня входу АЦП",
        "fix(sec): усунути переповнення буфера Modbus (CVE-2026-4412)",
        "chore(ci): оновити версію компілятора GCC до 14.2",
        "feat(telemetry): додати періодичний звіт про стан акумулятора",
        "docs(readme): оновити схему підключення UART"
    };
    size_t count = sizeof(sample_commits) / sizeof(sample_commits[0]);

    generate_release_notes("v3.2.0", "2026-08-28", sample_commits, count);
    return 0;
}
