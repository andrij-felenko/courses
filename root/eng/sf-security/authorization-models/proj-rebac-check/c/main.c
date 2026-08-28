#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_NAME 64
#define MAX_RULES 8
#define MAX_NODES 256
#define MAX_TUPLES 128

// ── Модель даних: вершина, суб'єкт, кортеж зв'язку ─────────────────────────

typedef struct {
    char object[MAX_NAME];
    char relation[MAX_NAME];
} Userset;

typedef struct {
    bool is_user;
    char user[MAX_NAME];
    Userset set;
} Subject;

typedef struct {
    char object[MAX_NAME];
    char relation[MAX_NAME];
    Subject subject;
} Tuple;

typedef enum {
    RULE_THIS,
    RULE_COMPUTED,
    RULE_WALK
} RuleKind;

typedef struct {
    RuleKind kind;
    char rel[MAX_NAME];
    char via[MAX_NAME];
    char then[MAX_NAME];
} Rule;

typedef struct {
    char ns[MAX_NAME];
    char rel[MAX_NAME];
    Rule rules[MAX_RULES];
    size_t rule_count;
} SchemaEntry;

typedef struct {
    SchemaEntry entries[32];
    size_t count;
} Schema;

typedef struct {
    Tuple tuples[MAX_TUPLES];
    size_t count;
    int trips;
} MemoryStore;

typedef struct {
    bool allowed;
    int depth;
    int trips;
} CheckResult;

// ── Допоміжні функції ключів та пошуку схеми ───────────────────────────────

static void make_key(char *buf, size_t sz, const char *obj, const char *rel) {
    snprintf(buf, sz, "%s#%s", obj, rel);
}

static void get_namespace(char *buf, size_t sz, const char *obj) {
    const char *colon = strchr(obj, ':');
    if (colon) {
        size_t len = (size_t)(colon - obj);
        if (len >= sz) len = sz - 1;
        strncpy(buf, obj, len);
        buf[len] = '\0';
    } else {
        strncpy(buf, obj, sz - 1);
        buf[sz - 1] = '\0';
    }
}

static const SchemaEntry* find_schema(const Schema *s, const char *ns, const char *rel) {
    for (size_t i = 0; i < s->count; i++) {
        if (strcmp(s->entries[i].ns, ns) == 0 && strcmp(s->entries[i].rel, rel) == 0) {
            return &s->entries[i];
        }
    }
    return NULL;
}

// ── Читання пачки ключів зі сховища ────────────────────────────────────────

static size_t store_read_many(MemoryStore *store, const Userset *want, size_t want_count,
                              Subject out_rows[MAX_NODES][MAX_RULES], size_t out_counts[MAX_NODES]) {
    store->trips++;
    for (size_t i = 0; i < want_count; i++) {
        out_counts[i] = 0;
        char req_key[MAX_NAME * 2];
        make_key(req_key, sizeof(req_key), want[i].object, want[i].relation);

        for (size_t t = 0; t < store->count; t++) {
            char tup_key[MAX_NAME * 2];
            make_key(tup_key, sizeof(tup_key), store->tuples[t].object, store->tuples[t].relation);
            if (strcmp(req_key, tup_key) == 0 && out_counts[i] < MAX_RULES) {
                out_rows[i][out_counts[i]++] = store->tuples[t].subject;
            }
        }
    }
    return want_count;
}

// ── Локальне замикання похідних правил: нуль походів у сховище ──────────────

static size_t close_computed(const Schema *schema, const Userset *frontier, size_t frontier_len,
                             Userset *out_nodes, size_t max_out) {
    char seen[MAX_NODES][MAX_NAME * 2];
    size_t seen_count = 0;
    Userset stack[MAX_NODES];
    size_t stack_len = 0;
    size_t out_len = 0;

    for (size_t i = 0; i < frontier_len && stack_len < MAX_NODES; i++) {
        stack[stack_len++] = frontier[i];
    }

    while (stack_len > 0) {
        Userset curr = stack[--stack_len];
        char k[MAX_NAME * 2];
        make_key(k, sizeof(k), curr.object, curr.relation);

        bool already = false;
        for (size_t i = 0; i < seen_count; i++) {
            if (strcmp(seen[i], k) == 0) { already = true; break; }
        }
        if (already) continue;

        if (seen_count < MAX_NODES) {
            strncpy(seen[seen_count++], k, sizeof(seen[0]) - 1);
        }
        if (out_len < max_out) {
            out_nodes[out_len++] = curr;
        }

        char ns[MAX_NAME];
        get_namespace(ns, sizeof(ns), curr.object);
        const SchemaEntry *se = find_schema(schema, ns, curr.relation);
        if (se) {
            for (size_t r = 0; r < se->rule_count; r++) {
                if (se->rules[r].kind == RULE_COMPUTED && stack_len < MAX_NODES) {
                    Userset next = {0};
                    strncpy(next.object, curr.object, sizeof(next.object) - 1);
                    strncpy(next.relation, se->rules[r].rel, sizeof(next.relation) - 1);
                    stack[stack_len++] = next;
                }
            }
        }
    }
    return out_len;
}

// ── Обхід графа ReBAC рівнями ───────────────────────────────────────────────

static bool check_rebac(const Schema *schema, MemoryStore *store, const char *user,
                        Userset start, int max_depth, bool memo, CheckResult *res) {
    char global_seen[MAX_NODES][MAX_NAME * 2];
    size_t global_seen_cnt = 0;

    char start_k[MAX_NAME * 2];
    make_key(start_k, sizeof(start_k), start.object, start.relation);
    strncpy(global_seen[global_seen_cnt++], start_k, sizeof(global_seen[0]) - 1);

    Userset frontier[MAX_NODES];
    size_t frontier_cnt = 1;
    frontier[0] = start;

    for (int depth = 0; depth < max_depth; depth++) {
        if (frontier_cnt == 0) {
            res->allowed = false;
            res->depth = depth;
            res->trips = store->trips;
            return true; // Граф вичерпано, чесна відмова
        }

        Userset nodes[MAX_NODES];
        size_t node_cnt = close_computed(schema, frontier, frontier_cnt, nodes, MAX_NODES);

        // (1) Зібрати ключі для батч-читання
        Userset want[MAX_NODES];
        size_t want_cnt = 0;

        for (size_t i = 0; i < node_cnt; i++) {
            char ns[MAX_NAME];
            get_namespace(ns, sizeof(ns), nodes[i].object);
            const SchemaEntry *se = find_schema(schema, ns, nodes[i].relation);
            if (!se) continue;

            for (size_t r = 0; r < se->rule_count; r++) {
                Userset req = {0};
                if (se->rules[r].kind == RULE_THIS) {
                    req = nodes[i];
                } else if (se->rules[r].kind == RULE_WALK) {
                    strncpy(req.object, nodes[i].object, sizeof(req.object) - 1);
                    strncpy(req.relation, se->rules[r].via, sizeof(req.relation) - 1);
                } else {
                    continue;
                }

                char rk[MAX_NAME * 2];
                make_key(rk, sizeof(rk), req.object, req.relation);
                bool exists = false;
                for (size_t w = 0; w < want_cnt; w++) {
                    char wk[MAX_NAME * 2];
                    make_key(wk, sizeof(wk), want[w].object, want[w].relation);
                    if (strcmp(rk, wk) == 0) { exists = true; break; }
                }
                if (!exists && want_cnt < MAX_NODES) {
                    want[want_cnt++] = req;
                }
            }
        }

        // (2) Один похід у сховище на рівень
        Subject rows[MAX_NODES][MAX_RULES];
        size_t row_counts[MAX_NODES];
        store_read_many(store, want, want_cnt, rows, row_counts);

        // (3) Обробка результатів та формування наступного фронту
        Userset next_frontier[MAX_NODES];
        size_t next_cnt = 0;

        for (size_t i = 0; i < node_cnt; i++) {
            char ns[MAX_NAME];
            get_namespace(ns, sizeof(ns), nodes[i].object);
            const SchemaEntry *se = find_schema(schema, ns, nodes[i].relation);
            if (!se) continue;

            for (size_t r = 0; r < se->rule_count; r++) {
                char search_key[MAX_NAME * 2];
                if (se->rules[r].kind == RULE_THIS) {
                    make_key(search_key, sizeof(search_key), nodes[i].object, nodes[i].relation);
                } else if (se->rules[r].kind == RULE_WALK) {
                    make_key(search_key, sizeof(search_key), nodes[i].object, se->rules[r].via);
                } else {
                    continue;
                }

                for (size_t w = 0; w < want_cnt; w++) {
                    char wk[MAX_NAME * 2];
                    make_key(wk, sizeof(wk), want[w].object, want[w].relation);
                    if (strcmp(wk, search_key) != 0) continue;

                    for (size_t row_idx = 0; row_idx < row_counts[w]; row_idx++) {
                        Subject s = rows[w][row_idx];
                        if (se->rules[r].kind == RULE_THIS) {
                            if (s.is_user) {
                                if (strcmp(s.user, user) == 0) {
                                    res->allowed = true;
                                    res->depth = depth;
                                    res->trips = store->trips;
                                    return true;
                                }
                            } else {
                                char sk[MAX_NAME * 2];
                                make_key(sk, sizeof(sk), s.set.object, s.set.relation);
                                bool seen_before = false;
                                if (memo) {
                                    for (size_t g = 0; g < global_seen_cnt; g++) {
                                        if (strcmp(global_seen[g], sk) == 0) { seen_before = true; break; }
                                    }
                                }
                                if (!seen_before && next_cnt < MAX_NODES) {
                                    if (memo && global_seen_cnt < MAX_NODES) {
                                        strncpy(global_seen[global_seen_cnt++], sk, sizeof(global_seen[0]) - 1);
                                    }
                                    next_frontier[next_cnt++] = s.set;
                                }
                            }
                        } else if (se->rules[r].kind == RULE_WALK) {
                            if (!s.is_user) {
                                Userset walked = {0};
                                strncpy(walked.object, s.set.object, sizeof(walked.object) - 1);
                                strncpy(walked.relation, se->rules[r].then, sizeof(walked.relation) - 1);

                                char wk_next[MAX_NAME * 2];
                                make_key(wk_next, sizeof(wk_next), walked.object, walked.relation);
                                bool seen_before = false;
                                if (memo) {
                                    for (size_t g = 0; g < global_seen_cnt; g++) {
                                        if (strcmp(global_seen[g], wk_next) == 0) { seen_before = true; break; }
                                    }
                                }
                                if (!seen_before && next_cnt < MAX_NODES) {
                                    if (memo && global_seen_cnt < MAX_NODES) {
                                        strncpy(global_seen[global_seen_cnt++], wk_next, sizeof(global_seen[0]) - 1);
                                    }
                                    next_frontier[next_cnt++] = walked;
                                }
                            }
                        }
                    }
                }
            }
        }

        frontier_cnt = next_cnt;
        for (size_t f = 0; f < next_cnt; f++) {
            frontier[f] = next_frontier[f];
        }
    }

    res->allowed = false;
    res->depth = max_depth;
    res->trips = store->trips;
    return false; // Перевищено межу глибини
}
