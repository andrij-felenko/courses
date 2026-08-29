#include "state_manager.h"

#include <math.h>
#include <string.h>

const char *delta_result_str(delta_result_t result)
{
    switch (result) {
        case DELTA_APPLIED:      return "прийнято";
        case DELTA_STALE:        return "застаріла версія — відкинуто";
        case DELTA_EMPTY:        return "порожня дельта";
        case DELTA_OUT_OF_RANGE: return "поза фізичними межами — відкинуто";
        case DELTA_BAD_ARG:      return "хибний аргумент";
        default:                 return "невідомо";
    }
}

const char *config_field_str(config_field_t field)
{
    switch (field) {
        case FIELD_TARGET_TEMP: return "уставка";
        case FIELD_FAN_RPM:     return "обертиВентилятора";
        case FIELD_HEATING:     return "нагрів";
        default:                return "?";
    }
}

void state_agent_init(state_agent_t *agent, const node_config_t *initial)
{
    if ((agent == NULL) || (initial == NULL)) {
        return;
    }

    memset(agent, 0, sizeof(*agent));

    /* На старті всі три погляди збігаються: іншої думки про залізо ще ніхто не має. */
    agent->desired  = *initial;
    agent->reported = *initial;
    agent->active   = *initial;

    agent->applied_sequence = initial->sequence_id;
    agent->conn = CONN_DISCONNECTED;
    telemetry_queue_init(&agent->queue);
}

void state_agent_set_connection(state_agent_t *agent, connection_state_t state)
{
    if (agent == NULL) {
        return;
    }
    agent->conn = state;
}

/* Перевірка фізичних меж — лише для полів, які дельта справді несе. */
static bool delta_within_limits(const shadow_delta_t *delta)
{
    if ((delta->fields & (uint32_t)FIELD_TARGET_TEMP) != 0u) {
        if ((delta->target_temperature < CFG_TEMP_MIN_C) ||
            (delta->target_temperature > CFG_TEMP_MAX_C) ||
            isnan(delta->target_temperature)) {
            return false;
        }
    }
    if ((delta->fields & (uint32_t)FIELD_FAN_RPM) != 0u) {
        if (delta->fan_speed_rpm > CFG_FAN_MAX_RPM) {
            return false;
        }
    }
    /* Логічне поле перевіряти нема на що: bool не буває поза межами. */
    return true;
}

delta_result_t state_agent_apply_delta(state_agent_t *agent, const shadow_delta_t *delta)
{
    if ((agent == NULL) || (delta == NULL)) {
        return DELTA_BAD_ARG;
    }
    if ((delta->fields & (uint32_t)FIELD_ALL) == 0u) {
        return DELTA_EMPTY;
    }

    /* Захист від гонок: у радіоканалі пакети дублюються й обганяють одне одного.
       Порівнюємо з версією ОСТАННЬОЇ ПРИЙНЯТОЇ дельти, а не з тією, що в залізі:
       інакше застарілий пакет проліз би у вікні між прийомом і застосуванням. */
    if (delta->sequence_id <= agent->desired.sequence_id) {
        agent->stale_rejected++;
        return DELTA_STALE;
    }

    if (!delta_within_limits(delta)) {
        /* Версію НЕ підвищуємо: дельта в хмарі лишиться ненульовою,
           і оператор побачить, що вузол уставку не прийняв. */
        agent->range_rejected++;
        return DELTA_OUT_OF_RANGE;
    }

    if ((delta->fields & (uint32_t)FIELD_TARGET_TEMP) != 0u) {
        agent->desired.target_temperature = delta->target_temperature;
    }
    if ((delta->fields & (uint32_t)FIELD_FAN_RPM) != 0u) {
        agent->desired.fan_speed_rpm = delta->fan_speed_rpm;
    }
    if ((delta->fields & (uint32_t)FIELD_HEATING) != 0u) {
        agent->desired.heating_enabled = delta->heating_enabled;
    }
    agent->desired.sequence_id = delta->sequence_id;

    return DELTA_APPLIED;
}

uint32_t state_agent_pending_fields(const state_agent_t *agent)
{
    uint32_t mask = 0u;

    if (agent == NULL) {
        return 0u;
    }

    if (fabsf(agent->desired.target_temperature - agent->active.target_temperature) >
        CFG_TEMP_EPSILON_C) {
        mask |= (uint32_t)FIELD_TARGET_TEMP;
    }
    if (agent->desired.fan_speed_rpm != agent->active.fan_speed_rpm) {
        mask |= (uint32_t)FIELD_FAN_RPM;
    }
    if (agent->desired.heating_enabled != agent->active.heating_enabled) {
        mask |= (uint32_t)FIELD_HEATING;
    }

    return mask;
}

uint32_t state_agent_reconcile_hardware(state_agent_t *agent)
{
    uint32_t mask;

    if (agent == NULL) {
        return 0u;
    }

    mask = state_agent_pending_fields(agent);

    if (mask == 0u) {
        /* Хмара могла повторити ту саму уставку новою версією: значення не змінилося,
           але відзвітувати про нову версію треба — інакше дельта не закриється. */
        if (agent->active.sequence_id != agent->desired.sequence_id) {
            agent->active.sequence_id   = agent->desired.sequence_id;
            agent->applied_sequence     = agent->desired.sequence_id;
            agent->reported             = agent->active;
            agent->reported_dirty       = true;
        }
        return 0u;
    }

    /* Тут у справжньому виробі йде запис у драйвери: шпаруватість ШІМ клапана,
       уставка ПІД-регулятора, реле котла. Пишемо лише те, що справді змінилося. */
    if ((mask & (uint32_t)FIELD_TARGET_TEMP) != 0u) {
        agent->active.target_temperature = agent->desired.target_temperature;
    }
    if ((mask & (uint32_t)FIELD_FAN_RPM) != 0u) {
        agent->active.fan_speed_rpm = agent->desired.fan_speed_rpm;
    }
    if ((mask & (uint32_t)FIELD_HEATING) != 0u) {
        agent->active.heating_enabled = agent->desired.heating_enabled;
    }

    agent->active.sequence_id = agent->desired.sequence_id;
    agent->applied_sequence   = agent->active.sequence_id;

    /* reported знімається з ФАКТИЧНОГО стану заліза, а не з бажаного:
       вузол звітує про те, що зробив, а не про те, що йому наказали. */
    agent->reported       = agent->active;
    agent->reported_dirty = true;

    return mask;
}

bool state_agent_record_telemetry(state_agent_t *agent, const telemetry_entry_t *entry)
{
    telemetry_entry_t stamped;

    if ((agent == NULL) || (entry == NULL)) {
        return false;
    }

    stamped = *entry;
    if ((agent->conn != CONN_CONNECTED) && (agent->conn != CONN_SYNCING)) {
        stamped.flags |= (uint8_t)TELEMETRY_FLAG_FROM_CACHE;
    }
    if (agent->active.heating_enabled) {
        stamped.flags |= (uint8_t)TELEMETRY_FLAG_HEATING;
    }

    return telemetry_queue_push(&agent->queue, &stamped);
}

size_t state_agent_drain_telemetry(state_agent_t *agent, telemetry_publish_fn publish, void *ctx)
{
    const telemetry_entry_t *item;
    size_t sent = 0u;

    if ((agent == NULL) || (publish == NULL)) {
        return 0u;
    }
    if ((agent->conn != CONN_CONNECTED) && (agent->conn != CONN_SYNCING)) {
        return 0u; /* каналу немає — черга просто чекає далі */
    }

    while ((item = telemetry_queue_peek(&agent->queue)) != NULL) {
        if (!publish(item, ctx)) {
            /* Вікно зв'язку скінчилося або брокер відмовив. Звіт НЕ вилучаємо:
               він поїде наступного разу. Це і є ціна доступності в моделі AP. */
            break;
        }
        (void)telemetry_queue_pop(&agent->queue);
        sent++;
    }

    return sent;
}

bool state_agent_reported_dirty(const state_agent_t *agent)
{
    return (agent != NULL) && agent->reported_dirty;
}

void state_agent_mark_reported_sent(state_agent_t *agent)
{
    if (agent != NULL) {
        agent->reported_dirty = false;
    }
}
