/* user_service.c — Реалізація Фази 1 (Expand) */
#include "user_service.h"
#include <string.h>

/* Внутрішній рушій пошуку у сховищі */
static int storage_find_internal(const char* tenant, const char* uid, unsigned int flags, user_profile_t* out) {
    if (!tenant || !uid || !out) return -1;
    (void)flags; /* Прапорці зарезервовані для майбутньої фільтрації */
    
    /* Імітація читання даних користувача */
    if (strcmp(uid, "usr_101") == 0) {
        strncpy(out->name, "Тарас Шевченко", MAX_NAME_LEN - 1);
        strncpy(out->email, "taras@example.ua", MAX_NAME_LEN - 1);
        out->name[MAX_NAME_LEN - 1] = '\0';
        out->email[MAX_NAME_LEN - 1] = '\0';
        out->is_active = true;
        return 0;
    }
    return -2; /* Запис не знайдено */
}

int user_service_find(const user_lookup_request_t* req, user_profile_t* out_profile) {
    if (!req || !req->user_id) return -1;
    const char* tenant = req->tenant_id ? req->tenant_id : DEFAULT_TENANT_ID;
    return storage_find_internal(tenant, req->user_id, req->flags, out_profile);
}

/* Старий метод трансформується у тонкий адаптер (Shim) */
int user_service_get_by_id(const char* user_id, user_profile_t* out_profile) {
    user_lookup_request_t req;
    req.user_id = user_id;
    req.tenant_id = DEFAULT_TENANT_ID;
    req.flags = 0;
    return user_service_find(&req, out_profile);
}
