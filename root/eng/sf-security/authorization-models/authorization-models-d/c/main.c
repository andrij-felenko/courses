#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>

#define MAX_ROLES_PER_USER   8
#define MAX_PERMS_PER_ROLE   16
#define MAX_NAME_LEN         32
#define CACHE_SIZE           256
#define CACHE_TTL_SEC        10

/* Бітові маски операцій */
typedef enum {
    PERM_NONE   = 0,
    PERM_READ   = (1 << 0),
    PERM_WRITE  = (1 << 1),
    PERM_DELETE = (1 << 2),
    PERM_ADMIN  = (1 << 3)
} PermissionFlags;

/* Вердикт авторизації */
typedef enum {
    AUTHZ_DENY = 0,
    AUTHZ_PERMIT = 1,
    AUTHZ_ERROR_TIMEOUT = -1,
    AUTHZ_ERROR_INTERNAL = -2
} AuthzVerdict;

/* Структура ролі та закріплених дозволів */
typedef struct {
    char name[MAX_NAME_LEN];
    uint32_t allowed_permissions;
} RoleDefinition;

/* Суб'єкт із контекстом */
typedef struct {
    char user_id[MAX_NAME_LEN];
    char roles[MAX_ROLES_PER_USER][MAX_NAME_LEN];
    size_count_t role_count;
    char department[MAX_NAME_LEN];
    uint32_t clearance_level;
} SubjectContext;

/* Захищений ресурс */
typedef struct {
    char resource_id[MAX_NAME_LEN];
    char department[MAX_NAME_LEN];
    uint32_t classification_level;
    char owner_id[MAX_NAME_LEN];
} ResourceDescriptor;

/* Контекст середовища (ABAC) */
typedef struct {
    time_t request_time;
    bool is_corporate_network;
    uint32_t risk_score;
} EnvironmentContext;

/* Запис L1-кешу вердиктів */
typedef struct {
    uint64_t query_hash;
    AuthzVerdict verdict;
    time_t expires_at;
    bool valid;
} CacheEntry;

/* Движок PDP */
typedef struct {
    RoleDefinition roles[16];
    size_t role_count;
    CacheEntry cache[CACHE_SIZE];
    uint64_t cache_hits;
    uint64_t cache_misses;
} PolicyDecisionPoint;

/* Простий 64-бітний хеш FNV-1a для кешування */
static uint64_t hash_query(const char *user, const char *res, PermissionFlags act) {
    uint64_t hash = 14695981039346656037ULL;
    const char *p = user;
    while (*p) { hash = (hash ^ (uint8_t)*p++) * 1099511628211ULL; }
    p = res;
    while (*p) { hash = (hash ^ (uint8_t)*p++) * 1099511628211ULL; }
    hash = (hash ^ (uint8_t)act) * 1099511628211ULL;
    return hash;
}

/* Ініціалізація PDP */
void pdp_init(PolicyDecisionPoint *pdp) {
    memset(pdp, 0, sizeof(PolicyDecisionPoint));
    
    /* Реєстрація базових ролей */
    strncpy(pdp->roles[0].name, "admin", MAX_NAME_LEN);
    pdp->roles[0].allowed_permissions = PERM_READ | PERM_WRITE | PERM_DELETE | PERM_ADMIN;
    
    strncpy(pdp->roles[1].name, "editor", MAX_NAME_LEN);
    pdp->roles[1].allowed_permissions = PERM_READ | PERM_WRITE;
    
    strncpy(pdp->roles[2].name, "viewer", MAX_NAME_LEN);
    pdp->roles[2].allowed_permissions = PERM_READ;
    
    pdp->role_count = 3;
}

/* Оцінка політики (Core Evaluation) */
static AuthzVerdict pdp_evaluate_rules(
    const PolicyDecisionPoint *pdp,
    const SubjectContext *sub,
    const ResourceDescriptor *res,
    PermissionFlags action,
    const EnvironmentContext *env
) {
    /* 1. ABAC: Перевірка рівня ризику та мережевого периметра */
    if (env->risk_score > 80 || !env->is_corporate_network) {
        if (action & (PERM_WRITE | PERM_DELETE | PERM_ADMIN)) {
            return AUTHZ_DENY; /* Критичні дії поза офісом або під ризиком заборонено */
        }
    }

    /* 2. MAC: Перевірка рівня допуску (No Read-Up / No Write-Down) */
    if (sub->clearance_level < res->classification_level) {
        return AUTHZ_DENY; /* Допуск суб'єкта нижчий за гриф ресурсу */
    }

    /* 3. DAC: Власник ресурсу має повний доступ у межах свого відділу */
    if (strncmp(sub->user_id, res->owner_id, MAX_NAME_LEN) == 0 &&
        strncmp(sub->department, res->department, MAX_NAME_LEN) == 0) {
        return AUTHZ_PERMIT;
    }

    /* 4. RBAC: Збір дозволів за всіма активними ролями суб'єкта */
    uint32_t cumulative_permissions = PERM_NONE;
    for (size_t i = 0; i < sub->role_count; i++) {
        for (size_t r = 0; r < pdp->role_count; r++) {
            if (strncmp(sub->roles[i], pdp->roles[r].name, MAX_NAME_LEN) == 0) {
                cumulative_permissions |= pdp->roles[r].allowed_permissions;
            }
        }
    }

    /* 5. ABAC: Дозволи ролі діють лише в межах одного департаменту */
    if (strncmp(sub->department, res->department, MAX_NAME_LEN) == 0) {
        if ((cumulative_permissions & action) == action) {
            return AUTHZ_PERMIT;
        }
    }

    /* За замовчанням — сувора відмова (Fail-Close / Deny-by-default) */
    return AUTHZ_DENY;
}

/* Публічний інтерфейс PDP з L1-кешуванням */
AuthzVerdict pdp_decide(
    PolicyDecisionPoint *pdp,
    const SubjectContext *sub,
    const ResourceDescriptor *res,
    PermissionFlags action,
    const EnvironmentContext *env
) {
    if (!sub || !res || !env) {
        return AUTHZ_DENY; /* Fail-Close при невалідних вхідних даних */
    }

    uint64_t q_hash = hash_query(sub->user_id, res->resource_id, action);
    size_t cache_idx = q_hash % CACHE_SIZE;

    /* Перевірка кешу */
    CacheEntry *entry = &pdp->cache[cache_idx];
    if (entry->valid && entry->query_hash == q_hash) {
        if (env->request_time <= entry->expires_at) {
            pdp->cache_hits++;
            return entry->verdict;
        }
    }

    /* Кеш-промах: обчислення вердикту */
    pdp->cache_misses++;
    AuthzVerdict verdict = pdp_evaluate_rules(pdp, sub, res, action, env);

    /* Запис у кеш */
    entry->query_hash = q_hash;
    entry->verdict = verdict;
    entry->expires_at = env->request_time + CACHE_TTL_SEC;
    entry->valid = true;

    return verdict;
}

/* Точка застосування (PEP): перехоплення та виконання */
bool pep_enforce(
    PolicyDecisionPoint *pdp,
    const SubjectContext *sub,
    const ResourceDescriptor *res,
    PermissionFlags action,
    const EnvironmentContext *env
) {
    AuthzVerdict verdict = pdp_decide(pdp, sub, res, action, env);

    /* Аудит запиту */
    printf("[AUDIT] User: %-8s | Res: %-12s | Act: %u | Verdict: %s\n",
           sub->user_id, res->resource_id, action,
           (verdict == AUTHZ_PERMIT) ? "PERMIT" : "DENY");

    return (verdict == AUTHZ_PERMIT);
}

int main(void) {
    PolicyDecisionPoint pdp;
    pdp_init(&pdp);

    time_t now = time(NULL);

    SubjectContext alice = {
        .user_id = "alice",
        .roles = {"editor"},
        .role_count = 1,
        .department = "finance",
        .clearance_level = 3
    };

    SubjectContext bob = {
        .user_id = "bob",
        .roles = {"viewer"},
        .role_count = 1,
        .department = "marketing",
        .clearance_level = 1
    };

    ResourceDescriptor doc_budget = {
        .resource_id = "budget_2026",
        .department = "finance",
        .classification_level = 2,
        .owner_id = "alice"
    };

    EnvironmentContext corporate_env = {
        .request_time = now,
        .is_corporate_network = true,
        .risk_score = 10
    };

    EnvironmentContext untrusted_env = {
        .request_time = now,
        .is_corporate_network = false,
        .risk_score = 85
    };

    printf("=== Демонстрація роботи авторизаційного ядра (C99) ===\n\n");

    /* Тест 1: Аліса пише у свій фінансовий документ у корпоративній мережі */
    pep_enforce(&pdp, &alice, &doc_budget, PERM_WRITE, &corporate_env);

    /* Тест 2: Повторний запит Аліси (має влучити в L1-кеш) */
    pep_enforce(&pdp, &alice, &doc_budget, PERM_WRITE, &corporate_env);

    /* Тест 3: Аліса намагається писати з публічної ненадійної мережі (ABAC блок) */
    pep_enforce(&pdp, &alice, &doc_budget, PERM_WRITE, &untrusted_env);

    /* Тест 4: Боб з іншого відділу намагається читати фінансовий бюджет (Відмова) */
    pep_enforce(&pdp, &bob, &doc_budget, PERM_READ, &corporate_env);

    printf("\nСтатистика L1-кешу: Hits = %llu, Misses = %llu\n",
           (unsigned long long)pdp.cache_hits, (unsigned long long)pdp.cache_misses);

    return 0;
}
