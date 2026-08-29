#include "shadow_json.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Шукає "ключ": і повертає вказівник на перший символ значення (або NULL). */
static const char *find_value(const char *doc, size_t len, const char *key)
{
    const size_t klen = strlen(key);
    size_t i;

    if ((doc == NULL) || (len < (klen + 3u))) {
        return NULL;
    }

    for (i = 0u; (i + klen + 2u) <= len; ++i) {
        size_t j;

        if (doc[i] != '"') {
            continue;
        }
        if (memcmp(&doc[i + 1u], key, klen) != 0) {
            continue;
        }
        if (doc[i + 1u + klen] != '"') {
            continue; /* збіг лише за префіксом — не наш ключ */
        }

        j = i + klen + 2u;
        while ((j < len) && ((doc[j] == ' ') || (doc[j] == '\t'))) {
            ++j;
        }
        if ((j >= len) || (doc[j] != ':')) {
            continue;
        }
        ++j;
        while ((j < len) && ((doc[j] == ' ') || (doc[j] == '\t'))) {
            ++j;
        }
        return (j < len) ? &doc[j] : NULL;
    }

    return NULL;
}

/* Копіює лексему значення до роздільника у NUL-термінований буфер. */
static bool copy_token(const char *start, const char *limit, char *out, size_t cap)
{
    size_t n = 0u;

    while ((start < limit) && ((n + 1u) < cap)) {
        const char c = *start;
        if ((c == ',') || (c == '}') || (c == ' ') || (c == '\t') ||
            (c == '\n') || (c == '\r')) {
            break;
        }
        out[n] = c;
        n++;
        start++;
    }
    out[n] = '\0';

    return n > 0u;
}

static bool parse_float(const char *start, const char *limit, float *out)
{
    char token[32];
    char *end = NULL;
    float value;

    if (!copy_token(start, limit, token, sizeof(token))) {
        return false;
    }
    value = strtof(token, &end);
    if ((end == NULL) || (*end != '\0')) {
        return false; /* у числі є сміття — документ покручений */
    }
    *out = value;
    return true;
}

static bool parse_u32(const char *start, const char *limit, uint32_t *out, uint32_t max)
{
    char token[32];
    char *end = NULL;
    unsigned long value;

    if (!copy_token(start, limit, token, sizeof(token))) {
        return false;
    }
    if ((token[0] == '-') || (token[0] == '+')) {
        return false;
    }
    value = strtoul(token, &end, 10);
    if ((end == NULL) || (*end != '\0') || (value > (unsigned long)max)) {
        return false;
    }
    *out = (uint32_t)value;
    return true;
}

static bool parse_bool(const char *start, const char *limit, bool *out)
{
    char token[8];

    if (!copy_token(start, limit, token, sizeof(token))) {
        return false;
    }
    if (strcmp(token, "true") == 0) {
        *out = true;
        return true;
    }
    if (strcmp(token, "false") == 0) {
        *out = false;
        return true;
    }
    return false;
}

int shadow_json_parse_delta(const char *doc, size_t len, shadow_delta_t *out)
{
    const char *limit;
    const char *value;
    uint32_t number;
    int fields = 0;

    if ((doc == NULL) || (out == NULL) || (len == 0u)) {
        return -1;
    }

    memset(out, 0, sizeof(*out));
    limit = doc + len;

    /* Версія обов'язкова: без неї немає захисту від застарілих пакетів,
       а отже й права застосовувати дельту до заліза. */
    value = find_value(doc, len, "version");
    if ((value == NULL) || !parse_u32(value, limit, &out->sequence_id, 0xFFFFFFFFu)) {
        return -1;
    }

    value = find_value(doc, len, "temp");
    if (value != NULL) {
        if (!parse_float(value, limit, &out->target_temperature)) {
            return -1;
        }
        out->fields |= (uint32_t)FIELD_TARGET_TEMP;
        fields++;
    }

    value = find_value(doc, len, "fan");
    if (value != NULL) {
        if (!parse_u32(value, limit, &number, 0xFFFFu)) {
            return -1;
        }
        out->fan_speed_rpm = (uint16_t)number;
        out->fields |= (uint32_t)FIELD_FAN_RPM;
        fields++;
    }

    value = find_value(doc, len, "heat");
    if (value != NULL) {
        if (!parse_bool(value, limit, &out->heating_enabled)) {
            return -1;
        }
        out->fields |= (uint32_t)FIELD_HEATING;
        fields++;
    }

    return fields;
}

int shadow_json_build_reported(const state_agent_t *agent, char *buf, size_t cap)
{
    int written;

    if ((agent == NULL) || (buf == NULL) || (cap == 0u)) {
        return -1;
    }

    written = snprintf(buf, cap,
                       "{\"state\":{\"reported\":"
                       "{\"temp\":%.1f,\"fan\":%u,\"heat\":%s}},\"version\":%lu}",
                       (double)agent->reported.target_temperature,
                       (unsigned int)agent->reported.fan_speed_rpm,
                       agent->reported.heating_enabled ? "true" : "false",
                       (unsigned long)agent->reported.sequence_id);

    if ((written < 0) || ((size_t)written >= cap)) {
        return -1; /* обрізаний JSON брокер відкине, а тінь лишиться неузгодженою */
    }
    return written;
}
