#ifndef STATE_MANAGER_H
#define STATE_MANAGER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "telemetry_queue.h"

/*
 * Агент розподіленого стану кінцевого вузла (термостат вентиляційної установки).
 *
 * Тримає три погляди на конфігурацію:
 *   desired — те, чого хоче хмара (прийшло дельтою тіні пристрою);
 *   active  — те, що справді залито в залізо (ШІМ клапана, реле котла);
 *   reported — те, про що вузол відзвітував (== active на момент звіту).
 * Розбіжність desired vs active і є локальна дельта, яку треба довести до заліза.
 */

/* Фізичні межі об'єкта: усе, що поза ними, до заліза не доходить. */
#define CFG_TEMP_MIN_C     5.0f
#define CFG_TEMP_MAX_C     40.0f
#define CFG_FAN_MAX_RPM    3000u
#define CFG_TEMP_EPSILON_C 0.05f /* дрібніша різниця — шум float, а не дельта */

typedef enum {
    CONN_DISCONNECTED = 0,
    CONN_CONNECTING,
    CONN_CONNECTED,
    CONN_SYNCING
} connection_state_t;

/* Поля документа тіні. Дельта несе ЛИШЕ змінені, тому потрібна маска присутності. */
typedef enum {
    FIELD_TARGET_TEMP = 1u << 0,
    FIELD_FAN_RPM     = 1u << 1,
    FIELD_HEATING     = 1u << 2
} config_field_t;

#define FIELD_ALL (FIELD_TARGET_TEMP | FIELD_FAN_RPM | FIELD_HEATING)

typedef struct {
    float    target_temperature;
    uint16_t fan_speed_rpm;
    bool     heating_enabled;
    uint32_t sequence_id;   /* монотонна версія тіні */
} node_config_t;

/* Часткова конфігурація: значущі лише ті поля, чий біт стоїть у fields. */
typedef struct {
    uint32_t fields;
    uint32_t sequence_id;
    float    target_temperature;
    uint16_t fan_speed_rpm;
    bool     heating_enabled;
} shadow_delta_t;

typedef enum {
    DELTA_APPLIED = 0,
    DELTA_STALE,        /* версія не новіша за вже прийняту — дубль або обгін пакетів */
    DELTA_EMPTY,        /* документ без жодного поля */
    DELTA_OUT_OF_RANGE, /* значення поза фізичними межами об'єкта */
    DELTA_BAD_ARG
} delta_result_t;

const char *delta_result_str(delta_result_t result);

/* Назва поля за одиничним бітом маски (для журналу). */
const char *config_field_str(config_field_t field);

typedef struct {
    node_config_t      desired;
    node_config_t      reported;
    node_config_t      active;
    connection_state_t conn;
    telemetry_queue_t  queue;
    uint32_t           applied_sequence; /* версія, що дійшла до заліза */
    uint32_t           stale_rejected;
    uint32_t           range_rejected;
    bool               reported_dirty;   /* reported чекає на публікацію в хмару */
} state_agent_t;

/* Публікатор одного звіту. false — канал не прийняв: звіт лишається в черзі. */
typedef bool (*telemetry_publish_fn)(const telemetry_entry_t *entry, void *ctx);

void state_agent_init(state_agent_t *agent, const node_config_t *initial);
void state_agent_set_connection(state_agent_t *agent, connection_state_t state);

/* Прийом дельти з топіка .../shadow/update/delta. */
delta_result_t state_agent_apply_delta(state_agent_t *agent, const shadow_delta_t *delta);

/* Маска полів, де desired розійшовся з active (те, що ще не в залізі). */
uint32_t state_agent_pending_fields(const state_agent_t *agent);

/* Запис у залізо; повертає маску справді застосованих полів. */
uint32_t state_agent_reconcile_hardware(state_agent_t *agent);

bool   state_agent_record_telemetry(state_agent_t *agent, const telemetry_entry_t *entry);
size_t state_agent_drain_telemetry(state_agent_t *agent, telemetry_publish_fn publish, void *ctx);

bool state_agent_reported_dirty(const state_agent_t *agent);
void state_agent_mark_reported_sent(state_agent_t *agent);

#endif /* STATE_MANAGER_H */
