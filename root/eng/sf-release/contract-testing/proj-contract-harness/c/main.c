#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_FIELDS 16
#define MAX_INTERACTIONS 8
#define MAX_USERS 32

/* Типи даних для структурного зіставлення полів контракту */
typedef enum {
    FIELD_TYPE_STRING,
    FIELD_TYPE_INT,
    FIELD_TYPE_FLOAT
} field_type_t;

/* Очікуване поле у відповіді постачальника */
typedef struct {
    char key[32];
    field_type_t type;
    bool required;
} field_rule_t;

/* Модель однієї взаємодії контракту */
typedef struct {
    const char *state_description;
    const char *method;
    const char *path;
    int expected_status;
    field_rule_t rules[MAX_FIELDS];
    size_t rule_count;
} contract_interaction_t;

/* Простий DTO запиту та відповіді */
typedef struct {
    char method[8];
    char path[64];
} http_request_t;

typedef struct {
    char key[32];
    char val[64];
    field_type_t inferred_type;
} json_pair_t;

typedef struct {
    int status_code;
    json_pair_t fields[MAX_FIELDS];
    size_t field_count;
} http_response_t;

/* ── Модель та бізнес-логіка постачальника (Provider) ── */

typedef struct {
    int user_id;
    char username[32];
    double balance;
    bool active;
} user_record_t;

static user_record_t g_db[MAX_USERS];
static size_t g_user_count = 0;

/* Обробники станів постачальника (Provider States) */
static void state_user_42_exists_and_active(void) {
    g_user_count = 0;
    g_db[0].user_id = 42;
    strncpy(g_db[0].username, "andrij", sizeof(g_db[0].username));
    g_db[0].balance = 1250.75;
    g_db[0].active = true;
    g_user_count = 1;
}

static void state_no_users_exist(void) {
    g_user_count = 0;
}

/* Реалізація контролера постачальника */
static http_response_t provider_handle_request(const http_request_t *req) {
    http_response_t res;
    memset(&res, 0, sizeof(res));

    if (strcmp(req->method, "GET") == 0 && strncmp(req->path, "/users/", 7) == 0) {
        int uid = atoi(req->path + 7);
        for (size_t i = 0; i < g_user_count; ++i) {
            if (g_db[i].user_id == uid && g_db[i].active) {
                res.status_code = 200;
                
                /* Поле user_id (int) */
                strncpy(res.fields[0].key, "user_id", 31);
                snprintf(res.fields[0].val, 63, "%d", g_db[i].user_id);
                res.fields[0].inferred_type = FIELD_TYPE_INT;
                
                /* Поле balance (float) */
                strncpy(res.fields[1].key, "balance", 31);
                snprintf(res.fields[1].val, 63, "%.2f", g_db[i].balance);
                res.fields[1].inferred_type = FIELD_TYPE_FLOAT;
                
                /* Додаткове поле постачальника, якого споживач не просив */
                strncpy(res.fields[2].key, "server_time", 31);
                snprintf(res.fields[2].val, 63, "1714567890");
                res.fields[2].inferred_type = FIELD_TYPE_INT;
                
                res.field_count = 3;
                return res;
            }
        }
        res.status_code = 404;
        strncpy(res.fields[0].key, "error_code", 31);
        strncpy(res.fields[0].val, "USER_NOT_FOUND", 63);
        res.fields[0].inferred_type = FIELD_TYPE_STRING;
        res.field_count = 1;
        return res;
    }

    res.status_code = 400;
    return res;
}

/* ── Раннер верифікації контракту ── */

typedef void (*state_handler_fn)(void);

typedef struct {
    const char *state_name;
    state_handler_fn handler;
} state_registry_entry_t;

static state_registry_entry_t g_state_registry[] = {
    { "user 42 exists and is active", state_user_42_exists_and_active },
    { "no users exist in database", state_no_users_exist },
};
static const size_t g_state_registry_size = sizeof(g_state_registry) / sizeof(g_state_registry[0]);

static bool verify_interaction(const contract_interaction_t *interaction) {
    printf("[RUN] Взаємодія: '%s' -> %s %s\n",
           interaction->state_description, interaction->method, interaction->path);

    /* 1. Пошук та виконання Provider State */
    state_handler_fn state_fn = NULL;
    for (size_t i = 0; i < g_state_registry_size; ++i) {
        if (strcmp(g_state_registry[i].state_name, interaction->state_description) == 0) {
            state_fn = g_state_registry[i].handler;
            break;
        }
    }

    if (!state_fn) {
        printf("  [FAIL] Не знайдено обробника для стану: '%s'\n", interaction->state_description);
        return false;
    }
    state_fn();

    /* 2. Виконання запиту проти постачальника */
    http_request_t req;
    strncpy(req.method, interaction->method, sizeof(req.method) - 1);
    strncpy(req.path, interaction->path, sizeof(req.path) - 1);
    http_response_t res = provider_handle_request(&req);

    /* 3. Звірка статус-коду */
    if (res.status_code != interaction->expected_status) {
        printf("  [FAIL] Статус-код не збігається: очікували %d, отримали %d\n",
               interaction->expected_status, res.status_code);
        return false;
    }

    /* 4. Звірка полів тіла за правилами контракту */
    for (size_t r = 0; r < interaction->rule_count; ++r) {
        const field_rule_t *rule = &interaction->rules[r];
        bool found = false;

        for (size_t f = 0; f < res.field_count; ++f) {
            if (strcmp(res.fields[f].key, rule->key) == 0) {
                found = true;
                if (res.fields[f].inferred_type != rule->type) {
                    printf("  [FAIL] Поле '%s': невідповідність типу (очікували %d, маємо %d)\n",
                           rule->key, rule->type, res.fields[f].inferred_type);
                    return false;
                }
                break;
            }
        }

        if (!found && rule->required) {
            printf("  [FAIL] Обов'язкове поле '%s' відсутнє у відповіді постачальника!\n", rule->key);
            return false;
        }
    }

    printf("  [OK] Контракт виконано успішно (статус %d, перевірено правил: %zu)\n",
           res.status_code, interaction->rule_count);
    return true;
}

int main(void) {
    /* Оголошення контракту споживача (Pact interactions) */
    contract_interaction_t contract[2];
    memset(contract, 0, sizeof(contract));

    /* Взаємодія 1: успішне отримання балансу */
    contract[0].state_description = "user 42 exists and is active";
    contract[0].method = "GET";
    contract[0].path = "/users/42";
    contract[0].expected_status = 200;
    
    strncpy(contract[0].rules[0].key, "user_id", 31);
    contract[0].rules[0].type = FIELD_TYPE_INT;
    contract[0].rules[0].required = true;

    strncpy(contract[0].rules[1].key, "balance", 31);
    contract[0].rules[1].type = FIELD_TYPE_FLOAT;
    contract[0].rules[1].required = true;
    contract[0].rule_count = 2;

    /* Взаємодія 2: неіснуючий користувач */
    contract[1].state_description = "no users exist in database";
    contract[1].method = "GET";
    contract[1].path = "/users/999";
    contract[1].expected_status = 404;

    strncpy(contract[1].rules[0].key, "error_code", 31);
    contract[1].rules[0].type = FIELD_TYPE_STRING;
    contract[1].rules[0].required = true;
    contract[1].rule_count = 1;

    /* Прогін верифікації у CI */
    printf("=== ЗАПУСК ВЕРИФІКАЦІЇ КОНТРАКТУ ПОСТАЧАЛЬНИКОМ ===\n");
    size_t passed = 0;
    for (size_t i = 0; i < 2; ++i) {
        if (verify_interaction(&contract[i])) {
            passed++;
        }
    }

    printf("Підсумок: %zu з 2 взаємодій успішно верифіковано.\n", passed);
    return (passed == 2) ? 0 : 1;
}
