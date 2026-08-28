/* c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

typedef enum {
    OWNERSHIP_STRONG,
    OWNERSHIP_INNER_SOURCE
} OwnershipMode;

typedef enum {
    VERDICT_ALLOW,
    VERDICT_NEED_REVIEW,
    VERDICT_REJECT
} Verdict;

typedef struct {
    char path_prefix[128];
    char owner_team[64];
    OwnershipMode mode;
} OwnershipRule;

typedef struct {
    OwnershipRule *rules;
    size_t count;
    size_t capacity;
} RuleTable;

RuleTable* rule_table_create(size_t capacity) {
    RuleTable *table = (RuleTable*)malloc(sizeof(RuleTable));
    if (!table) return NULL;
    table->rules = (OwnershipRule*)malloc(sizeof(OwnershipRule) * capacity);
    if (!table->rules) {
        free(table);
        return NULL;
    }
    table->count = 0;
    table->capacity = capacity;
    return table;
}

void rule_table_destroy(RuleTable *table) {
    if (!table) return;
    free(table->rules);
    free(table);
}

bool rule_table_add(RuleTable *table, const char *prefix, const char *owner, OwnershipMode mode) {
    if (!table || table->count >= table->capacity) return false;
    OwnershipRule *r = &table->rules[table->count++];
    strncpy(r->path_prefix, prefix, sizeof(r->path_prefix) - 1);
    r->path_prefix[sizeof(r->path_prefix) - 1] = '\0';
    strncpy(r->owner_team, owner, sizeof(r->owner_team) - 1);
    r->owner_team[sizeof(r->owner_team) - 1] = '\0';
    r->mode = mode;
    return true;
}

Verdict evaluate_file_change(const RuleTable *table, const char *file_path, 
                             const char *author_team, bool is_contract_broken) {
    if (!table || !file_path || !author_team) return VERDICT_REJECT;

    const OwnershipRule *best_rule = NULL;
    size_t max_match_len = 0;

    /* Пошук найспецифічнішого правила за принципом найдовшого збігу префікса */
    for (size_t i = 0; i < table->count; ++i) {
        const char *p = table->rules[i].path_prefix;
        size_t len = strlen(p);
        if (strncmp(file_path, p, len) == 0 && len > max_match_len) {
            max_match_len = len;
            best_rule = &table->rules[i];
        }
    }

    /* Якщо шлях не захищено жодним правилом — дозволяємо автоматично */
    if (!best_rule) {
        return VERDICT_ALLOW;
    }

    /* Якщо автор є членом команди-власника — повний доступ */
    if (strcmp(author_team, best_rule->owner_team) == 0) {
        return VERDICT_ALLOW;
    }

    /* Перевірка для сторонніх авторів (InnerSource контриб'юторів) */
    if (best_rule->mode == OWNERSHIP_STRONG) {
        return VERDICT_NEED_REVIEW;
    }

    /* Режим INNER_SOURCE: перевіряємо цілісність контракту */
    if (is_contract_broken) {
        return VERDICT_REJECT; /* Злам API-контракту стороннім автором заборонено */
    }

    return VERDICT_NEED_REVIEW; /* Автоматичне схвалення після CI перевірок */
}

int main(void) {
    RuleTable *table = rule_table_create(10);
    if (!table) return 1;

    rule_table_add(table, "src/core/crypto/", "sec-team", OWNERSHIP_STRONG);
    rule_table_add(table, "src/services/telemetry/", "platform-team", OWNERSHIP_INNER_SOURCE);

    printf("Test 1 (Owner PR): %d\n", 
           evaluate_file_change(table, "src/core/crypto/sha256.c", "sec-team", false));
    printf("Test 2 (External PR Strong): %d\n", 
           evaluate_file_change(table, "src/core/crypto/sha256.c", "billing-team", false));
    printf("Test 3 (InnerSource PR Contract OK): %d\n", 
           evaluate_file_change(table, "src/services/telemetry/ingest.c", "billing-team", false));
    printf("Test 4 (InnerSource PR Contract Broken): %d\n", 
           evaluate_file_change(table, "src/services/telemetry/ingest.c", "billing-team", true));

    rule_table_destroy(table);
    return 0;
}
