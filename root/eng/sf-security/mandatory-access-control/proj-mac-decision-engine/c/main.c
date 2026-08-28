#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define AVC_CACHE_SLOTS 256
#define MAX_RULES 128

/* Бітові маски дозволів */
#define PERM_READ    (1U << 0)
#define PERM_WRITE   (1U << 1)
#define PERM_EXECUTE (1U << 2)
#define PERM_APPEND  (1U << 3)

/* Ідентифікатори типів безпеки та класів */
typedef uint16_t security_id_t;
typedef uint32_t access_vector_t;

#define SECCLASS_FILE   1
#define SECCLASS_SOCKET 2
#define SECCLASS_DIR    3

/* Контекст безпеки: тип та рівень MLS (чутливість + бітова маска категорій) */
typedef struct {
    security_id_t type_id;
    uint8_t mls_sensitivity;
    uint64_t mls_categories;
} security_context_t;

/* Запис у таблиці правил Type Enforcement */
typedef struct {
    security_id_t src_type;
    security_id_t target_type;
    uint16_t target_class;
    access_vector_t allowed_permissions;
} te_rule_t;

/* Вузол кешу AVC */
typedef struct avc_node {
    security_id_t src_type;
    security_id_t target_type;
    uint16_t target_class;
    access_vector_t allowed;
    access_vector_t audit_allow;
    access_vector_t audit_deny;
    struct avc_node *next;
} avc_node_t;

/* Головна структура рушія безпеки */
typedef struct {
    te_rule_t rules[MAX_RULES];
    size_t rule_count;
    avc_node_t *cache[AVC_CACHE_SLOTS];
    uint64_t cache_hits;
    uint64_t cache_misses;
} security_engine_t;

/* Перевірка домінування MLS: (S_sens >= O_sens) && (S_cats ⊇ O_cats) */
static inline bool mls_dominate(const security_context_t *s, const security_context_t *o) {
    if (s->mls_sensitivity < o->mls_sensitivity) {
        return false;
    }
    return (s->mls_categories & o->mls_categories) == o->mls_categories;
}

/* Хеш-функція для трійки (src, target, class) */
static inline uint8_t avc_hash(security_id_t s, security_id_t t, uint16_t c) {
    uint32_t val = ((uint32_t)s << 16) ^ ((uint32_t)t << 8) ^ (uint32_t)c;
    val = ((val >> 16) ^ val) * 0x45d9f3b;
    val = ((val >> 16) ^ val) * 0x45d9f3b;
    val = (val >> 16) ^ val;
    return (uint8_t)(val % AVC_CACHE_SLOTS);
}

void security_engine_init(security_engine_t *eng) {
    eng->rule_count = 0;
    eng->cache_hits = 0;
    eng->cache_misses = 0;
    memset(eng->cache, 0, sizeof(eng->cache));
}

bool security_engine_add_rule(security_engine_t *eng, security_id_t src,
                              security_id_t target, uint16_t cl, access_vector_t perms) {
    if (eng->rule_count >= MAX_RULES) return false;
    eng->rules[eng->rule_count++] = (te_rule_t){src, target, cl, perms};
    return true;
}

/* Обчислення дозволів у Security Server (повільний шлях при Cache Miss) */
static access_vector_t security_compute_av(const security_engine_t *eng,
                                          security_id_t src, security_id_t target,
                                          uint16_t cl) {
    access_vector_t av = 0;
    for (size_t i = 0; i < eng->rule_count; ++i) {
        if (eng->rules[i].src_type == src &&
            eng->rules[i].target_type == target &&
            eng->rules[i].target_class == cl) {
            av |= eng->rules[i].allowed_permissions;
        }
    }
    return av;
}

/* Перевірка прав через AVC з автоматичним поповненням кешу */
bool avc_has_perm(security_engine_t *eng,
                  const security_context_t *subj,
                  const security_context_t *obj,
                  uint16_t target_class,
                  access_vector_t requested_perm) {
    /* 1. Перевірка MLS для операцій читання (No Read Up) */
    if ((requested_perm & (PERM_READ | PERM_EXECUTE)) && !mls_dominate(subj, obj)) {
        return false;
    }
    /* Перевірка MLS для операцій запису (No Write Down) */
    if ((requested_perm & (PERM_WRITE | PERM_APPEND)) && !mls_dominate(obj, subj)) {
        return false;
    }

    /* 2. Пошук у кеші AVC */
    uint8_t h = avc_hash(subj->type_id, obj->type_id, target_class);
    avc_node_t *curr = eng->cache[h];
    while (curr) {
        if (curr->src_type == subj->type_id &&
            curr->target_type == obj->type_id &&
            curr->target_class == target_class) {
            eng->cache_hits++;
            return (curr->allowed & requested_perm) == requested_perm;
        }
        curr = curr->next;
    }

    /* 3. Cache Miss: звернення до Security Server */
    eng->cache_misses++;
    access_vector_t allowed = security_compute_av(eng, subj->type_id, obj->type_id, target_class);

    /* 4. Додавання результату в кеш AVC */
    avc_node_t *new_node = (avc_node_t *)malloc(sizeof(avc_node_t));
    if (new_node) {
        new_node->src_type = subj->type_id;
        new_node->target_type = obj->type_id;
        new_node->target_class = target_class;
        new_node->allowed = allowed;
        new_node->audit_allow = 0;
        new_node->audit_deny = requested_perm;
        new_node->next = eng->cache[h];
        eng->cache[h] = new_node;
    }

    return (allowed & requested_perm) == requested_perm;
}

void security_engine_destroy(security_engine_t *eng) {
    for (size_t i = 0; i < AVC_CACHE_SLOTS; ++i) {
        avc_node_t *curr = eng->cache[i];
        while (curr) {
            avc_node_t *tmp = curr;
            curr = curr->next;
            free(tmp);
        }
        eng->cache[i] = NULL;
    }
}

int main(void) {
    security_engine_t engine;
    security_engine_init(&engine);

    /* Реєстрація типів системи */
    const security_id_t TYPE_HTTPD_T         = 10;
    const security_id_t TYPE_HTTPD_CONTENT_T = 20;
    const security_id_t TYPE_SHADOW_T        = 30;

    /* Правило політики: вебсервер httpd_t може читати контент httpd_sys_content_t */
    security_engine_add_rule(&engine, TYPE_HTTPD_T, TYPE_HTTPD_CONTENT_T,
                             SECCLASS_FILE, PERM_READ);

    /* Контексти безпеки процесів та файлів */
    security_context_t proc_ctx = { .type_id = TYPE_HTTPD_T, .mls_sensitivity = 0, .mls_categories = 0 };
    security_context_t html_ctx = { .type_id = TYPE_HTTPD_CONTENT_T, .mls_sensitivity = 0, .mls_categories = 0 };
    security_context_t shadow_ctx = { .type_id = TYPE_SHADOW_T, .mls_sensitivity = 0, .mls_categories = 0 };

    /* 1. Перша перевірка: промах кешу (Cache Miss) -> Дозволено */
    bool ok1 = avc_has_perm(&engine, &proc_ctx, &html_ctx, SECCLASS_FILE, PERM_READ);
    printf("1. httpd_t -> httpd_sys_content_t (читання): %s\n", ok1 ? "ДОЗВОЛЕНО" : "ЗАБОРОНЕНО");

    /* 2. Повторна перевірка: потрапляння в кеш (Cache Hit) -> Дозволено */
    bool ok2 = avc_has_perm(&engine, &proc_ctx, &html_ctx, SECCLASS_FILE, PERM_READ);
    printf("2. httpd_t -> httpd_sys_content_t (повторне читання): %s\n", ok2 ? "ДОЗВОЛЕНО" : "ЗАБОРОНЕНО");

    /* 3. Спроба доступу до системних паролів: Заборонено політикою */
    bool ok3 = avc_has_perm(&engine, &proc_ctx, &shadow_ctx, SECCLASS_FILE, PERM_READ);
    printf("3. httpd_t -> shadow_t (читання паролів): %s\n", ok3 ? "ДОЗВОЛЕНО" : "ЗАБОРОНЕНО");

    printf("Статистика роботи AVC: Влучань (Hits) = %llu, Промахів (Misses) = %llu\n",
           (unsigned long long)engine.cache_hits, (unsigned long long)engine.cache_misses);

    security_engine_destroy(&engine);
    return 0;
}
