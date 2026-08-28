/* user_service_v3.h — Фаза 3: Чистий контракт v3.0 */
#ifndef USER_SERVICE_V3_H
#define USER_SERVICE_V3_H

#include <stddef.h>
#include <stdbool.h>

#define MAX_NAME_LEN 128

typedef struct {
    const char* user_id;
    const char* tenant_id;
    unsigned int flags;
} user_lookup_request_t;

typedef struct {
    char name[MAX_NAME_LEN];
    char email[MAX_NAME_LEN];
    bool is_active;
} user_profile_t;

/* Єдиний цільовий метод: старий user_service_get_by_id вилучено повністю */
int user_service_find(const user_lookup_request_t* req, user_profile_t* out_profile);

#endif /* USER_SERVICE_H */
