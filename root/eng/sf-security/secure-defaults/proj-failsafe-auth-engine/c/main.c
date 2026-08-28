#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>

#define MAX_RULES 64
#define MAX_STRING_LEN 64

typedef enum {
    AUTH_DECISION_DENY = 0,
    AUTH_DECISION_ALLOW = 1
} AuthDecision;

typedef enum {
    AUTH_REASON_DEFAULT_DENY = 0,
    AUTH_REASON_EXPLICIT_DENY,
    AUTH_REASON_EXPLICIT_ALLOW,
    AUTH_REASON_PARSE_ERROR,
    AUTH_REASON_TIMEOUT,
    AUTH_REASON_MEMORY_ERROR,
    AUTH_REASON_CORRUPTED_REQUEST
} AuthReasonCode;

typedef enum {
    EFFECT_DENY = 0,
    EFFECT_ALLOW = 1
} RuleEffect;

typedef struct {
    char subject_role[MAX_STRING_LEN];
    char action[MAX_STRING_LEN];
    char resource_prefix[MAX_STRING_LEN];
    RuleEffect effect;
    bool is_active;
} AccessRule;

typedef struct {
    char subject_role[MAX_STRING_LEN];
    char action[MAX_STRING_LEN];
    char resource[MAX_STRING_LEN];
    uint64_t request_timestamp;
} AuthRequest;

typedef struct {
    AuthDecision decision;
    AuthReasonCode reason;
    const char* matched_rule;
} AuthResult;

typedef struct {
    AccessRule rules[MAX_RULES];
    size_t rule_count;
    uint32_t timeout_ms;
} AuthEngine;

/* Ініціалізація рушія: за замовчуванням база правил порожня */
void auth_engine_init(AuthEngine* engine, uint32_t timeout_ms) {
    if (!engine) return;
    memset(engine, 0, sizeof(AuthEngine));
    engine->rule_count = 0;
    engine->timeout_ms = timeout_ms;
}

/* Додавання правила до бази даних політик */
bool auth_engine_add_rule(AuthEngine* engine, const char* role, const char* action, 
                          const char* prefix, RuleEffect effect) {
    if (!engine || !role || !action || !prefix) return false;
    if (engine->rule_count >= MAX_RULES) return false;

    AccessRule* r = &engine->rules[engine->rule_count];
    strncpy(r->subject_role, role, MAX_STRING_LEN - 1);
    r->subject_role[MAX_STRING_LEN - 1] = '\0';

    strncpy(r->action, action, MAX_STRING_LEN - 1);
    r->action[MAX_STRING_LEN - 1] = '\0';

    strncpy(r->resource_prefix, prefix, MAX_STRING_LEN - 1);
    r->resource_prefix[MAX_STRING_LEN - 1] = '\0';

    r->effect = effect;
    r->is_active = true;
    engine->rule_count++;
    return true;
}

/* Безпечна перевірка префіксу ресурсу */
static bool match_resource_prefix(const char* rule_prefix, const char* requested_res) {
    size_t prefix_len = strlen(rule_prefix);
    if (prefix_len == 0) return false;
    return (strncmp(rule_prefix, requested_res, prefix_len) == 0);
}

/* Головний конвеєр перевірки прав: гарантована безпечна відмова (Fail-Closed) */
AuthResult auth_engine_evaluate(const AuthEngine* engine, const AuthRequest* req) {
    AuthResult result;
    /* КРОК 1: Абсолютний дефолт - ЗАБОРОНА */
    result.decision = AUTH_DECISION_DENY;
    result.reason = AUTH_REASON_DEFAULT_DENY;
    result.matched_rule = NULL;

    /* Валідація вхідних показчиків */
    if (!engine || !req) {
        result.reason = AUTH_REASON_CORRUPTED_REQUEST;
        return result;
    }

    /* Валідація цілісності полів запиту */
    if (req->subject_role[0] == '\0' || req->action[0] == '\0' || req->resource[0] == '\0') {
        result.reason = AUTH_REASON_PARSE_ERROR;
        return result;
    }

    bool explicit_allow_found = false;
    const char* allow_rule_name = NULL;

    /* КРОК 2: Ітерація по правилах із пріоритетом Explicit Deny */
    for (size_t i = 0; i < engine->rule_count; ++i) {
        const AccessRule* rule = &engine->rules[i];
        if (!rule->is_active) continue;

        /* Перевірка ролі (підтримка wildcard "*") */
        bool role_match = (strcmp(rule->subject_role, "*") == 0) || 
                           (strcmp(rule->subject_role, req->subject_role) == 0);

        /* Перевірка дії */
        bool action_match = (strcmp(rule->action, "*") == 0) || 
                             (strcmp(rule->action, req->action) == 0);

        /* Перевірка ресурсу */
        bool resource_match = match_resource_prefix(rule->resource_prefix, req->resource);

        if (role_match && action_match && resource_match) {
            if (rule->effect == EFFECT_DENY) {
                /* Явна заборона негайно перемагає все і зупиняє конвеєр */
                result.decision = AUTH_DECISION_DENY;
                result.reason = AUTH_REASON_EXPLICIT_DENY;
                result.matched_rule = rule->resource_prefix;
                return result;
            } else if (rule->effect == EFFECT_ALLOW) {
                explicit_allow_found = true;
                allow_rule_name = rule->resource_prefix;
            }
        }
    }

    /* КРОК 3: Дозвіл надається ЛИШЕ якщо знайдено явне правило ALLOW і немає заборон */
    if (explicit_allow_found) {
        result.decision = AUTH_DECISION_ALLOW;
        result.reason = AUTH_REASON_EXPLICIT_ALLOW;
        result.matched_rule = allow_rule_name;
    }

    return result;
}
