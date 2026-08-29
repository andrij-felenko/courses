#include "link.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* --- Мінімальний розбір JSON ---------------------------------------------
   Повноцінний парсер у прошивці зайвий: формат наказу ми задаємо самі,
   полів чотири, а пам'яті на дерево вузлів немає. Дістаємо поля напряму. */

static const char *field_tail(const char *json, const char *key)
{
    char pattern[24];
    const char *p;

    if (snprintf(pattern, sizeof pattern, "\"%s\"", key) >= (int)sizeof pattern) {
        return NULL;                     /* надто довгий ключ — не наш формат */
    }
    p = strstr(json, pattern);
    if (p == NULL) {
        return NULL;
    }
    p += strlen(pattern);
    while (*p == ' ' || *p == '\t') {
        ++p;
    }
    if (*p != ':') {
        return NULL;
    }
    ++p;
    while (*p == ' ' || *p == '\t') {
        ++p;
    }
    return p;
}

static bool field_str(const char *json, const char *key, char *out, size_t cap)
{
    const char *p = field_tail(json, key);
    size_t n = 0;

    if (p == NULL || *p != '"') {
        return false;
    }
    ++p;
    while (*p != '\0' && *p != '"') {
        if (n + 1 >= cap) {
            return false;                /* краще відмовити, ніж мовчки обрізати ID */
        }
        out[n++] = *p++;
    }
    if (*p != '"') {
        return false;
    }
    out[n] = '\0';
    return n > 0;
}

static bool field_long(const char *json, const char *key, long *out)
{
    const char *p = field_tail(json, key);
    char *end = NULL;
    long value;

    if (p == NULL) {
        return false;
    }
    value = strtol(p, &end, 10);
    if (end == p) {
        return false;
    }
    *out = value;
    return true;
}

const char *link_parse_reason(link_parse_t rc)
{
    switch (rc) {
    case LINK_PARSE_OK:           return "ok";
    case LINK_PARSE_NOT_JSON:     return "кадр не схожий на JSON";
    case LINK_PARSE_NO_CMD_ID:    return "немає поля cmd_id";
    case LINK_PARSE_NO_TARGET:    return "немає поля target_pct";
    case LINK_PARSE_TARGET_RANGE: return "target_pct поза межами 0..100";
    default:                      return "невідома вада кадру";
    }
}

link_parse_t link_parse_downlink(const char *payload, downlink_cmd_t *out)
{
    long target = 0;
    long issued = 0;
    long ttl = 0;

    memset(out, 0, sizeof *out);

    if (payload == NULL || strchr(payload, '{') == NULL) {
        return LINK_PARSE_NOT_JSON;
    }
    if (!field_str(payload, "cmd_id", out->cmd_id, sizeof out->cmd_id)) {
        return LINK_PARSE_NO_CMD_ID;
    }
    if (!field_long(payload, "target_pct", &target)) {
        return LINK_PARSE_NO_TARGET;
    }
    if (target < 0 || target > 100) {
        return LINK_PARSE_TARGET_RANGE;
    }
    out->target_pct = (int)target;

    /* Часові поля не обов'язкові: без них наказ вважаємо свіжим на хвилину. */
    out->issued_at_sec = field_long(payload, "issued_at", &issued) ? (uint32_t)issued : 0u;
    out->ttl_sec = field_long(payload, "ttl_sec", &ttl) ? (uint32_t)ttl : 60u;
    return LINK_PARSE_OK;
}

/* --- Публікація ----------------------------------------------------------
   На платі тут стоїть esp_mqtt_client_publish(client, topic, json, 0, 1, 0)
   з QoS 1: брокер повторює кадр, доки не отримає PUBACK. На стенді ту саму
   роль виконує звичайний stdout — його читає mosquitto_sub у статті. */

void link_publish_ack(const char *cmd_id, const char *status)
{
    printf("[MQTT -> devices/zone1/cmd/ack] {\"cmd_id\":\"%s\",\"status\":\"%s\"}\n",
           cmd_id, status);
    fflush(stdout);
}

void link_publish_status(const char *cmd_id, const char *state,
                         int progress_pct, int value_pct, int err)
{
    printf("[MQTT -> devices/zone1/cmd/status] {\"cmd_id\":\"%s\",\"state\":\"%s\","
           "\"progress_pct\":%d,\"value_pct\":%d,\"err\":%d}\n",
           cmd_id, state, progress_pct, value_pct, err);
    fflush(stdout);
}

void link_publish_nack(const char *reason)
{
    printf("[MQTT -> devices/zone1/cmd/nack] {\"reason\":\"%s\"}\n", reason);
    fflush(stdout);
}
