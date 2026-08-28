#include <stdint.h>
#include <string.h>
#include <stdbool.h>

typedef struct {
    char param_id[17];
    float expected_value;
    uint8_t param_type;
    uint32_t send_timestamp_ms;
    uint8_t retry_count;
    bool is_pending;
} param_write_transaction_t;

// Перевірка надходження ехо-відповіді PARAM_VALUE
bool verify_param_ack(param_write_transaction_t *tx, const char *recv_id, float recv_val) {
    if (!tx->is_pending) return false;
    
    // Порівняння ідентифікаторів
    if (strncmp(tx->param_id, recv_id, 16) == 0) {
        // Успішне підтвердження — транзакцію закрито
        tx->is_pending = false;
        return true;
    }
    return false;
}
