#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

typedef enum {
    STATE_INACTIVE,
    STATE_PENDING,
    STATE_FIRING,
    STATE_RESOLVED
} AlertState;

const char* state_to_str(AlertState s) {
    switch (s) {
        case STATE_INACTIVE: return "INACTIVE";
        case STATE_PENDING:  return "PENDING";
        case STATE_FIRING:   return "FIRING";
        case STATE_RESOLVED: return "RESOLVED";
        default:             return "UNKNOWN";
    }
}

typedef struct {
    char key[64];
    char val[64];
} Label;

typedef struct {
    char name[64];
    Label labels[8];
    int label_count;
    int for_seconds;
    AlertState state;
    time_t state_change_time;
    uint64_t fingerprint;
} AlertRuleC;

// Хешування рядка алгоритмом FNV-1a
uint64_t fnv1a_hash(const char* str, uint64_t hash) {
    const uint64_t prime = 0x100000001b3ULL;
    while (*str) {
        hash ^= (uint8_t)(*str++);
        hash *= prime;
    }
    return hash;
}

uint64_t compute_c_fingerprint(const AlertRuleC* r) {
    uint64_t hash = 0xcbf29ce484222325ULL;
    for (int i = 0; i < r->label_count; ++i) {
        hash = fnv1a_hash(r->labels[i].key, hash);
        hash ^= 0xff;
        hash = fnv1a_hash(r->labels[i].val, hash);
        hash ^= 0xfe;
    }
    return hash;
}

void rule_init(AlertRuleC* r, const char* name, int for_sec) {
    strncpy(r->name, name, sizeof(r->name) - 1);
    r->label_count = 0;
    r->for_seconds = for_sec;
    r->state = STATE_INACTIVE;
    r->state_change_time = 0;
    r->fingerprint = 0;
}

void rule_add_label(AlertRuleC* r, const char* k, const char* v) {
    if (r->label_count < 8) {
        strncpy(r->labels[r->label_count].key, k, 63);
        strncpy(r->labels[r->label_count].val, v, 63);
        r->label_count++;
    }
    r->fingerprint = compute_c_fingerprint(r);
}

void rule_evaluate(AlertRuleC* r, bool condition_met, time_t now) {
    switch (r->state) {
        case STATE_INACTIVE:
            if (condition_met) {
                if (r->for_seconds == 0) {
                    r->state = STATE_FIRING;
                    r->state_change_time = now;
                    printf("[DISPATCH] Alert: %s | State: FIRING | Fingerprint: %llx\n", 
                           r->name, (unsigned long long)r->fingerprint);
                } else {
                    r->state = STATE_PENDING;
                    r->state_change_time = now;
                }
            }
            break;

        case STATE_PENDING:
            if (!condition_met) {
                r->state = STATE_INACTIVE;
                r->state_change_time = now;
            } else if ((now - r->state_change_time) >= r->for_seconds) {
                r->state = STATE_FIRING;
                r->state_change_time = now;
                printf("[DISPATCH] Alert: %s | State: FIRING | Fingerprint: %llx\n", 
                       r->name, (unsigned long long)r->fingerprint);
            }
            break;

        case STATE_FIRING:
            if (!condition_met) {
                r->state = STATE_RESOLVED;
                r->state_change_time = now;
                printf("[DISPATCH] Alert: %s | State: RESOLVED | Normalization\n", r->name);
                r->state = STATE_INACTIVE;
            }
            break;

        case STATE_RESOLVED:
            r->state = condition_met ? STATE_PENDING : STATE_INACTIVE;
            r->state_change_time = now;
            break;
    }
}

int main(void) {
    AlertRuleC r;
    rule_init(&r, "DiskSpaceLow", 3);
    rule_add_label(&r, "mount", "/var/lib/data");
    rule_add_label(&r, "tier", "storage");

    time_t t = 1000;
    printf("--- t=1000: Condition true -> State PENDING ---\n");
    rule_evaluate(&r, true, t);

    printf("--- t=1002: Condition true (< 3s) -> State PENDING ---\n");
    rule_evaluate(&r, true, t + 2);

    printf("--- t=1004: Condition true (>= 3s) -> State FIRING ---\n");
    rule_evaluate(&r, true, t + 4);

    printf("--- t=1010: Condition false -> State RESOLVED ---\n");
    rule_evaluate(&r, false, t + 10);

    return 0;
}
