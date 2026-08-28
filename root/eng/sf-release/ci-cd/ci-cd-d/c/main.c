#include <stdbool.h>

bool is_feature_enabled(const char *flag_key, const void *user_context);
void execute_payment_v2(void *tx);
void execute_legacy_payment(void *tx);

void process_transaction(void *tx, const void *user_context) {
    if (is_feature_enabled("new_payment_v2", user_context)) {
        execute_payment_v2(tx);
    } else {
        execute_legacy_payment(tx);
    }
}
