#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <math.h>

#define MAX_ENTRIES 16
#define MAX_KEY_LEN 32

/* Статус результату операції */
typedef enum {
    RECON_OK = 0,
    RECON_NO_DRIFT = 1,
    RECON_VERSION_CONFLICT = 2,
    RECON_ACTUATION_FAILED = 3,
    RECON_RATE_LIMITED = 4
} ReconStatus;

/* Типи значень у сховищі стану */
typedef enum {
    VAL_TYPE_INT,
    VAL_TYPE_DOUBLE,
    VAL_TYPE_BOOL
} ValueType;

/* Універсальний елемент стану */
typedef struct {
    char key[MAX_KEY_LEN];
    ValueType type;
    union {
        int64_t i_val;
        double  d_val;
        bool    b_val;
    } as;
    bool is_null; /* Tombstone (видалення) */
} StateProperty;

/* Документ стану вузла */
typedef struct {
    StateProperty properties[MAX_ENTRIES];
    size_t count;
    uint64_t version;
    uint64_t timestamp_sec;
} StateDocument;

/* Дельта-запис розбіжності */
typedef struct {
    char key[MAX_KEY_LEN];
    StateProperty desired_val;
    StateProperty reported_val;
    bool requires_action;
} DriftItem;

/* Конфігурація відкату та захисту */
typedef struct {
    uint32_t base_backoff_ms;
    uint32_t max_backoff_ms;
    uint32_t current_attempt;
    double   analog_deadband; /* Зона нечутливості */
} ReconcilerPolicy;

/* Ініціалізація документа стану */
void state_doc_init(StateDocument* doc, uint64_t version) {
    doc->count = 0;
    doc->version = version;
    doc->timestamp_sec = (uint64_t)time(NULL);
}

/* Додавання або оновлення властивості */
void state_doc_set_double(StateDocument* doc, const char* key, double val) {
    for (size_t i = 0; i < doc->count; ++i) {
        if (strncmp(doc->properties[i].key, key, MAX_KEY_LEN) == 0) {
            doc->properties[i].type = VAL_TYPE_DOUBLE;
            doc->properties[i].as.d_val = val;
            doc->properties[i].is_null = false;
            return;
        }
    }
    if (doc->count < MAX_ENTRIES) {
        strncpy(doc->properties[doc->count].key, key, MAX_KEY_LEN - 1);
        doc->properties[doc->count].type = VAL_TYPE_DOUBLE;
        doc->properties[doc->count].as.d_val = val;
        doc->properties[doc->count].is_null = false;
        doc->count++;
    }
}

/* Обчислення експоненційного відкату з повним випадковим джитером (Full Jitter) */
uint32_t calculate_backoff_with_jitter(ReconcilerPolicy* policy) {
    uint32_t exp_limit = (uint32_t)pow(2.0, (double)policy->current_attempt) * policy->base_backoff_ms;
    if (exp_limit > policy->max_backoff_ms) {
        exp_limit = policy->max_backoff_ms;
    }
    if (exp_limit == 0) return 0;
    /* Full Jitter: випадкове число в діапазоні [0, exp_limit] */
    uint32_t jittered = (uint32_t)(rand() % exp_limit);
    return jittered;
}

/* Обчислення дрейфу між бажаним та звітованим станами */
size_t detect_drift(const StateDocument* desired,
                    const StateDocument* reported,
                    const ReconcilerPolicy* policy,
                    DriftItem* out_drifts,
                    size_t max_drifts) {
    size_t drift_count = 0;

    for (size_t i = 0; i < desired->count && drift_count < max_drifts; ++i) {
        const StateProperty* d_prop = &desired->properties[i];
        const StateProperty* r_prop = NULL;

        /* Пошук відповідної властивості у звітованому стані */
        for (size_t j = 0; j < reported->count; ++j) {
            if (strncmp(reported->properties[j].key, d_prop->key, MAX_KEY_LEN) == 0) {
                r_prop = &reported->properties[j];
                break;
            }
        }

        /* Випадок 1: Властивість відсутня у звіті */
        if (!r_prop) {
            strncpy(out_drifts[drift_count].key, d_prop->key, MAX_KEY_LEN - 1);
            out_drifts[drift_count].desired_val = *d_prop;
            out_drifts[drift_count].reported_val.is_null = true;
            out_drifts[drift_count].requires_action = true;
            drift_count++;
            continue;
        }

        /* Випадок 2: Порівняння значень з урахуванням зони нечутливості */
        if (d_prop->type == VAL_TYPE_DOUBLE && r_prop->type == VAL_TYPE_DOUBLE) {
            double diff = fabs(d_prop->as.d_val - r_prop->as.d_val);
            if (diff > policy->analog_deadband) {
                strncpy(out_drifts[drift_count].key, d_prop->key, MAX_KEY_LEN - 1);
                out_drifts[drift_count].desired_val = *d_prop;
                out_drifts[drift_count].reported_val = *r_prop;
                out_drifts[drift_count].requires_action = true;
                drift_count++;
            }
        }
    }
    return drift_count;
}

/* Імітація апаратного актуатора */
bool apply_hardware_actuation(const char* key, double target_val) {
    /* Безпечне встановлення фізичного значення в апаратуру */
    printf("  [Актуватор C] Застосування %s -> %.2f\n", key, target_val);
    return true;
}

/* Основний цикл узгодження (Reconciliation Loop Step) */
ReconStatus reconcile_step(const StateDocument* desired,
                          StateDocument* reported,
                          ReconcilerPolicy* policy,
                          uint64_t expected_version) {
    /* Крок 1: Перевірка оптимістичного блокування */
    if (desired->version < expected_version) {
        printf("  [Помилка C] Застаріла версія бажаного стану: %llu < %llu\n",
               (unsigned long long)desired->version,
               (unsigned long long)expected_version);
        return RECON_VERSION_CONFLICT;
    }

    /* Крок 2: Виявлення дрейфу */
    DriftItem drifts[MAX_ENTRIES];
    size_t num_drifts = detect_drift(desired, reported, policy, drifts, MAX_ENTRIES);

    if (num_drifts == 0) {
        policy->current_attempt = 0;
        return RECON_NO_DRIFT;
    }

    printf("  [Дрейф C] Знайдено розбіжностей: %zu. Початок узгодження...\n", num_drifts);

    /* Крок 3: Застосування дій до актуаторів */
    for (size_t i = 0; i < num_drifts; ++i) {
        if (drifts[i].requires_action) {
            bool ok = apply_hardware_actuation(drifts[i].key, drifts[i].desired_val.as.d_val);
            if (!ok) {
                policy->current_attempt++;
                uint32_t backoff = calculate_backoff_with_jitter(policy);
                printf("  [Збій C] Актуація не вдалася, повтор через %u мс\n", backoff);
                return RECON_ACTUATION_FAILED;
            }
            /* Оновлення локального звітованого стану */
            state_doc_set_double(reported, drifts[i].key, drifts[i].desired_val.as.d_val);
        }
    }

    /* Крок 4: Фіксація звіту та інкремент версії */
    reported->version = desired->version;
    reported->timestamp_sec = (uint64_t)time(NULL);
    policy->current_attempt = 0;
    return RECON_OK;
}
