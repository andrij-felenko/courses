#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int status_code;
    char message[128];
} StatusPayload;

// Глобальний RCU-вказівник
_Atomic(StatusPayload *) global_status_ptr = NULL;

// Макроси публікації та зчитування у стилі Linux Kernel RCU
#define RCU_ASSIGN_POINTER(target, value) \
    atomic_store_explicit(&(target), (value), memory_order_release)

#define RCU_DEREFERENCE(target) \
    atomic_load_explicit(&(target), memory_order_consume)

// Публікація нового стану письменником
void publish_status(int status, const char *msg) {
    StatusPayload *new_payload = (StatusPayload *)malloc(sizeof(StatusPayload));
    new_payload->status_code = status;
    strncpy(new_payload->message, msg, sizeof(new_payload->message) - 1);
    new_payload->message[sizeof(new_payload->message) - 1] = '\0';

    // RCU Assign Pointer: store-release бар'єр гарантує, що поля status_code та message
    // зафіксуються в пам'яті ДО того, як новий вказівник стане видимим для інших ядер
    RCU_ASSIGN_POINTER(global_status_ptr, new_payload);
}

// Безпечне читання пасивним читачем
int read_status_code(char *out_msg, size_t max_len) {
    // RCU Dereference: load-consume бар'єр встановлює залежність за даними
    StatusPayload *ptr = RCU_DEREFERENCE(global_status_ptr);
    if (!ptr) {
        return -1;
    }

    // Доступ до полів гарантовано відбувається ПІСЛЯ отримання дійсного вказівника
    int code = ptr->status_code;
    if (out_msg && max_len > 0) {
        strncpy(out_msg, ptr->message, max_len - 1);
        out_msg[max_len - 1] = '\0';
    }
    return code;
}
