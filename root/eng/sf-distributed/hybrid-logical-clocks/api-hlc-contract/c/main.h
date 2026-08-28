#ifndef HLC_CONTRACT_H
#define HLC_CONTRACT_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Статуси виконання операцій */
typedef enum {
    HLC_STATUS_OK                 = 0, /* Успішна операція */
    HLC_STATUS_ERR_DRIFT_EXCEEDED = 1, /* Фізичний час повідомлення перевищує поріг max_drift */
    HLC_STATUS_ERR_OVERFLOW       = 2, /* Переповнення логічного лічильника в межах тіку */
    HLC_STATUS_ERR_INVALID_ARG    = 3  /* Недійсні вказівники або параметри */
} hlc_status_t;

/* Структура канонічної мітки часу */
typedef struct {
    uint64_t physical_ms; /* Старша компонента l (мс) */
    uint32_t logical;     /* Молодша компонента c */
    uint32_t node_id;     /* Ідентифікатор вузла */
} hlc_timestamp_t;

/* Непрозорий дескриптор рушія годинника */
typedef struct hlc_engine hlc_engine_t;

/* Створення та знищення екземпляра рушія */
hlc_engine_t* hlc_engine_create(uint32_t node_id, uint64_t max_drift_ms);
void          hlc_engine_destroy(hlc_engine_t* engine);

/* Генерація мітки для локальної події або відправки */
hlc_status_t hlc_now(hlc_engine_t* engine, hlc_timestamp_t* out_ts);

/* Оновлення стану при отриманні вхідного пакета */
hlc_status_t hlc_update(hlc_engine_t* engine, const hlc_timestamp_t* remote_ts, hlc_timestamp_t* out_ts);

/* Повне лексикографічне порівняння двох міток */
/* Повертає -1 якщо a < b, 0 якщо a == b, +1 якщо a > b */
int hlc_compare(const hlc_timestamp_t* a, const hlc_timestamp_t* b);

/* Серіалізація та десеріалізація 64-бітного бінарного формату */
uint64_t hlc_serialize_wire64(const hlc_timestamp_t* ts);
void     hlc_deserialize_wire64(uint64_t wire, uint32_t node_id, hlc_timestamp_t* out_ts);

#ifdef __cplusplus
}
#endif

#endif /* HLC_CONTRACT_H */
