/*
 * Сценарій життя зв'язаного вузла на настільній машині:
 * доба без зв'язку → дельти з порушеним порядком → узгодження заліза →
 * коротке вікно радіозв'язку → дренаж буфера телеметрії.
 */
#include <stdio.h>
#include <string.h>

#include "shadow_json.h"
#include "state_manager.h"

/* Імітація вузького радіоканалу: у вікні зв'язку поміщається лише кілька пакетів. */
typedef struct {
    int window;   /* скільки пакетів іще прийме канал */
    int total;
} radio_link_t;

static bool radio_publish(const telemetry_entry_t *entry, void *ctx)
{
    radio_link_t *link = (radio_link_t *)ctx;

    if (link->window <= 0) {
        return false; /* вікно скінчилося: модем не встиг, решта лишається в буфері */
    }
    link->window--;
    link->total++;

    printf("    t=%lu temp=%.2f P=%u Вт%s\n",
           (unsigned long)entry->timestamp,
           (double)entry->measured_temperature,
           (unsigned int)entry->current_power_watts,
           ((entry->flags & TELEMETRY_FLAG_FROM_CACHE) != 0u) ? " [з буфера]" : "");
    return true;
}

static void print_fields(const char *prefix, uint32_t mask)
{
    static const config_field_t all[] = { FIELD_TARGET_TEMP, FIELD_FAN_RPM, FIELD_HEATING };
    size_t i;

    printf("%s", prefix);
    if (mask == 0u) {
        printf(" (немає)\n");
        return;
    }
    for (i = 0u; i < (sizeof(all) / sizeof(all[0])); ++i) {
        if ((mask & (uint32_t)all[i]) != 0u) {
            printf(" %s", config_field_str(all[i]));
        }
    }
    printf("\n");
}

static void feed_delta(state_agent_t *agent, const char *doc)
{
    shadow_delta_t delta;
    delta_result_t result;
    int fields;

    fields = shadow_json_parse_delta(doc, strlen(doc), &delta);
    if (fields < 0) {
        printf("  %-44s → покручений документ\n", doc);
        return;
    }

    result = state_agent_apply_delta(agent, &delta);
    printf("  %-44s → %s\n", doc, delta_result_str(result));
}

int main(void)
{
    node_config_t boot = { 21.0f, 1200u, true, 4u };
    state_agent_t agent;
    radio_link_t link = { 0, 0 };
    char payload[128];
    uint32_t applied;
    size_t sent;
    uint32_t t;

    state_agent_init(&agent, &boot);

    puts("== 1. Розділення мережі: вузол у полі, каналу немає ==");
    for (t = 0u; t < 40u; ++t) {
        telemetry_entry_t sample;
        sample.timestamp = 1000u + (t * 10u);
        sample.measured_temperature = 20.5f + (0.1f * (float)(t % 5u));
        sample.current_power_watts = (uint16_t)(800u + t);
        sample.flags = 0u;
        (void)state_agent_record_telemetry(&agent, &sample);
    }
    printf("  у буфері %u звітів, затерто найстаріших %lu\n",
           (unsigned int)telemetry_queue_count(&agent.queue),
           (unsigned long)telemetry_queue_dropped(&agent.queue));

    sent = state_agent_drain_telemetry(&agent, radio_publish, &link);
    printf("  спроба дренажу без зв'язку: відправлено %lu\n", (unsigned long)sent);

    puts("\n== 2. Дельти тіні: дублі, обгін пакетів, небезпечні значення ==");
    feed_delta(&agent, "{\"version\":7,\"temp\":24.5}");
    feed_delta(&agent, "{\"version\":5,\"temp\":18.0}");
    feed_delta(&agent, "{\"version\":9,\"fan\":5200}");
    feed_delta(&agent, "{\"version\":9,\"fan\":2400,\"heat\":false}");
    feed_delta(&agent, "{\"temp\":30.0}");
    feed_delta(&agent, "{\"version\":11,\"temp\":ой}");
    printf("  відкинуто застарілих %lu, поза межами %lu\n",
           (unsigned long)agent.stale_rejected,
           (unsigned long)agent.range_rejected);

    puts("\n== 3. Узгодження заліза ==");
    print_fields("  дельта до застосування:", state_agent_pending_fields(&agent));
    applied = state_agent_reconcile_hardware(&agent);
    print_fields("  записано в залізо:     ", applied);
    printf("  active: %.1f °C, %u об/хв, нагрів %s, версія %lu\n",
           (double)agent.active.target_temperature,
           (unsigned int)agent.active.fan_speed_rpm,
           agent.active.heating_enabled ? "увімкнено" : "вимкнено",
           (unsigned long)agent.applied_sequence);
    print_fields("  залишок дельти:        ", state_agent_pending_fields(&agent));

    puts("\n== 4. Канал повернувся: звіт про стан і дренаж буфера ==");
    state_agent_set_connection(&agent, CONN_CONNECTED);

    if (state_agent_reported_dirty(&agent)) {
        if (shadow_json_build_reported(&agent, payload, sizeof(payload)) > 0) {
            printf("  publish shadow/update: %s\n", payload);
            state_agent_mark_reported_sent(&agent);
        } else {
            puts("  буфер payload замалий — звіт відкладено");
        }
    }

    link.window = 5; /* коротке вікно: модем встиг лише п'ять пакетів */
    sent = state_agent_drain_telemetry(&agent, radio_publish, &link);
    printf("  вікно 1: відправлено %lu, у буфері лишилось %u\n",
           (unsigned long)sent, (unsigned int)telemetry_queue_count(&agent.queue));

    link.window = 100; /* канал стабілізувався */
    sent = state_agent_drain_telemetry(&agent, radio_publish, &link);
    printf("  вікно 2: відправлено %lu, у буфері лишилось %u\n",
           (unsigned long)sent, (unsigned int)telemetry_queue_count(&agent.queue));

    printf("\n  усього доїхало в хмару: %d звітів\n", link.total);
    return 0;
}
