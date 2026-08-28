/* user_service_v2.h — Фаза 2: Застарівання */
#ifndef USER_SERVICE_V2_H
#define USER_SERVICE_V2_H

#include "user_service.h"

#if defined(__GNUC__) || defined(__clang__)
#  define DEPRECATED_MSG(msg) __attribute__((deprecated(msg)))
#elif defined(_MSC_VER)
#  define DEPRECATED_MSG(msg) __declspec(deprecated(msg))
#else
#  define DEPRECATED_MSG(msg)
#endif

/* Атрибут сигналізує розробнику під час збірки клієнтського проєкту */
DEPRECATED_MSG("user_service_get_by_id is deprecated. Migrate to user_service_find. Removal in v3.0.")
int user_service_get_by_id(const char* user_id, user_profile_t* out_profile);

int user_service_find(const user_lookup_request_t* req, user_profile_t* out_profile);

/* Структура для аудиту міграції через телеметрію */
typedef struct {
    unsigned long legacy_calls_count;
    unsigned long v2_calls_count;
} migration_metrics_t;

void user_service_get_metrics(migration_metrics_t* out_metrics);

#endif
