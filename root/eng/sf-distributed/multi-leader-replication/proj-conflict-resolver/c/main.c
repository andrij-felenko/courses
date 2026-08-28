#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_NODES 8
#define MAX_SIBLINGS 4
#define MAX_VAL_LEN 64

/* Результат порівняння причинності */
typedef enum {
    CAUSAL_IDENTICAL,
    CAUSAL_DOMINATES,      /* Локальний стан новіший за вхідний */
    CAUSAL_IS_DOMINATED,   /* Вхідний стан новіший за локальний (пряме оновлення) */
    CAUSAL_CONCURRENT      /* Справжній конфлікт: паралельні незалежні записи */
} CausalRelation;

/* Політика розв'язання конфліктів */
typedef enum {
    STRATEGY_LWW,          /* Last-Write-Wins за фізичною міткою часу */
    STRATEGY_SIBLINGS,     /* Збереження розгалужень для злиття на читанні */
    STRATEGY_FIELD_MERGE   /* Поколонне / полями об'єднання (CRDT-like) */
} ConflictStrategy;

/* Версійний вектор */
typedef struct {
    uint64_t counters[MAX_NODES];
} VersionVector;

/* Окремий варіант значення (ревізія) */
typedef struct {
    char value[MAX_VAL_LEN];
    VersionVector vv;
    uint64_t timestamp_ms;
    uint32_t origin_node;
} RecordRevision;

/* Сховище запису для одного ключа */
typedef struct {
    char key[32];
    RecordRevision siblings[MAX_SIBLINGS];
    size_t sibling_count;
} DatabaseRecord;

/* Ініціалізація вектора */
void vv_init(VersionVector *vv) {
    memset(vv->counters, 0, sizeof(vv->counters));
}

/* Інкремент лічильника свого вузла */
void vv_increment(VersionVector *vv, uint32_t node_id) {
    if (node_id < MAX_NODES) {
        vv->counters[node_id]++;
    }
}

/* Об'єднання векторів (компонентний максимум) */
void vv_merge(VersionVector *dest, const VersionVector *src) {
    for (size_t i = 0; i < MAX_NODES; i++) {
        if (src->counters[i] > dest->counters[i]) {
            dest->counters[i] = src->counters[i];
        }
    }
}

/* Порівняння двох версійних векторів */
CausalRelation vv_compare(const VersionVector *a, const VersionVector *b) {
    bool a_greater = false;
    bool b_greater = false;

    for (size_t i = 0; i < MAX_NODES; i++) {
        if (a->counters[i] > b->counters[i]) {
            a_greater = true;
        } else if (a->counters[i] < b->counters[i]) {
            b_greater = true;
        }
    }

    if (!a_greater && !b_greater) return CAUSAL_IDENTICAL;
    if (a_greater && !b_greater)  return CAUSAL_DOMINATES;
    if (!a_greater && b_greater)  return CAUSAL_IS_DOMINATED;
    return CAUSAL_CONCURRENT;
}

/* Локальний запис на вузлі */
void record_local_write(DatabaseRecord *rec, const char *new_val, 
                        uint32_t local_node_id, uint64_t now_ms) {
    VersionVector next_vv;
    vv_init(&next_vv);

    /* Акумулюємо знання з усіх поточних siblings */
    for (size_t i = 0; i < rec->sibling_count; i++) {
        vv_merge(&next_vv, &rec->siblings[i].vv);
    }
    vv_increment(&next_vv, local_node_id);

    /* Запис схлопує всі старі версії в одну нову */
    rec->sibling_count = 1;
    strncpy(rec->siblings[0].value, new_val, MAX_VAL_LEN - 1);
    rec->siblings[0].value[MAX_VAL_LEN - 1] = '\0';
    rec->siblings[0].vv = next_vv;
    rec->siblings[0].timestamp_ms = now_ms;
    rec->siblings[0].origin_node = local_node_id;
}

/* Застосування вхідного пакета реплікації */
bool record_apply_remote(DatabaseRecord *rec, const RecordRevision *incoming,
                         ConflictStrategy strategy) {
    if (rec->sibling_count == 0) {
        rec->siblings[0] = *incoming;
        rec->sibling_count = 1;
        return true;
    }

    /* 1. Перевіряємо вхідний запис проти кожного локального sibling */
    bool incoming_is_obsolete = true;
    bool any_concurrent = false;
    size_t survived_count = 0;
    RecordRevision survived[MAX_SIBLINGS];

    for (size_t i = 0; i < rec->sibling_count; i++) {
        CausalRelation rel = vv_compare(&rec->siblings[i].vv, &incoming->vv);

        switch (rel) {
            case CAUSAL_IDENTICAL:
            case CAUSAL_DOMINATES:
                /* Локальний стан уже знає або перевищує вхідний */
                survived[survived_count++] = rec->siblings[i];
                break;

            case CAUSAL_IS_DOMINATED:
                /* Вхідний запис витісняє локальний застарілий */
                incoming_is_obsolete = false;
                break;

            case CAUSAL_CONCURRENT:
                /* Паралельний незалежний запис */
                incoming_is_obsolete = false;
                any_concurrent = true;
                survived[survived_count++] = rec->siblings[i];
                break;
        }
    }

    if (incoming_is_obsolete && !any_concurrent) {
        /* Вхідний запис відкинуто як застарілий дублікат */
        return false;
    }

    if (!any_concurrent && !incoming_is_obsolete) {
        /* Пряме оновлення без конфлікту: вхідний замінює все застаріле */
        rec->siblings[0] = *incoming;
        rec->sibling_count = 1;
        return true;
    }

    /* 2. Обробка конкурентного конфлікту за обраною стратегією */
    if (strategy == STRATEGY_LWW) {
        /* Знаходимо переможця за часом (з tie-breaker за ID вузла) */
        RecordRevision winner = *incoming;
        for (size_t i = 0; i < survived_count; i++) {
            if (survived[i].timestamp_ms > winner.timestamp_ms ||
               (survived[i].timestamp_ms == winner.timestamp_ms && 
                survived[i].origin_node > winner.origin_node)) {
                winner = survived[i];
            }
        }
        /* Зливаємо вектори, щоб зафіксувати знання обох гілок */
        for (size_t i = 0; i < survived_count; i++) {
            vv_merge(&winner.vv, &survived[i].vv);
        }
        vv_merge(&winner.vv, &incoming->vv);

        rec->siblings[0] = winner;
        rec->sibling_count = 1;
        return true;
    } 
    else if (strategy == STRATEGY_SIBLINGS) {
        /* Додаємо вхідний варіант до списку збережених гілок */
        if (survived_count < MAX_SIBLINGS) {
            survived[survived_count++] = *incoming;
        }
        rec->sibling_count = survived_count;
        for (size_t i = 0; i < survived_count; i++) {
            rec->siblings[i] = survived[i];
        }
        return true;
    }
    else if (strategy == STRATEGY_FIELD_MERGE) {
        /* CRDT-злиття: конкатенація неперетинних частин */
        RecordRevision merged;
        snprintf(merged.value, MAX_VAL_LEN, "%s+%s", survived[0].value, incoming->value);
        vv_init(&merged.vv);
        vv_merge(&merged.vv, &survived[0].vv);
        vv_merge(&merged.vv, &incoming->vv);
        merged.timestamp_ms = (incoming->timestamp_ms > survived[0].timestamp_ms) 
                              ? incoming->timestamp_ms : survived[0].timestamp_ms;
        merged.origin_node = incoming->origin_node;

        rec->siblings[0] = merged;
        rec->sibling_count = 1;
        return true;
    }

    return false;
}
