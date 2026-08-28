#include <stdio.h>
#include <string.h>
#include <stdbool.h>

typedef struct {
    char pk[64];
    char sk[64];
    char payload[128];
} table_record_t;

void build_user_pk(char *out_buf, size_t max_len, int user_id) {
    snprintf(out_buf, max_len, "USER#%d", user_id);
}

void build_order_sk(char *out_buf, size_t max_len, const char *date, int order_id) {
    snprintf(out_buf, max_len, "ORDER#%s#%04d", date, order_id);
}

bool matches_prefix(const char *sk, const char *prefix) {
    return strncmp(sk, prefix, strlen(prefix)) == 0;
}
