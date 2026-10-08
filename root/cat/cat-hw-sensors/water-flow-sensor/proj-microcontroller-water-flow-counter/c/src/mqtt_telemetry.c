#include "mqtt_telemetry.h"
#include <stdio.h>
#include <string.h>

static char g_client_id[64];
static char g_broker_ip[64];
static uint16_t g_port = 1883;
static bool g_mqtt_initialized = false;

bool mqtt_telemetry_init(const char *client_id, const char *broker_ip, uint16_t port) {
    if (client_id == NULL || broker_ip == NULL) {
        return false;
    }

    strncpy(g_client_id, client_id, sizeof(g_client_id) - 1);
    g_client_id[sizeof(g_client_id) - 1] = '\0';

    strncpy(g_broker_ip, broker_ip, sizeof(g_broker_ip) - 1);
    g_broker_ip[sizeof(g_broker_ip) - 1] = '\0';

    g_port = port;
    g_mqtt_initialized = true;
    return true;
}

int mqtt_telemetry_serialize_json(const mqtt_telemetry_payload_t *payload, char *buffer, size_t buffer_size) {
    if (payload == NULL || buffer == NULL || buffer_size == 0) {
        return -1;
    }

    int written = snprintf(
        buffer,
        buffer_size,
        "{"
        "\"device_id\":\"%s\","
        "\"flow_rate_lpm\":%.2f,"
        "\"total_volume_l\":%.3f,"
        "\"total_pulses\":%llu,"
        "\"power_good\":%s,"
        "\"uptime_ms\":%u"
        "}",
        g_client_id,
        (double)payload->flow_rate_lpm,
        payload->total_volume_liters,
        (unsigned long long)payload->total_pulses,
        payload->power_good ? "true" : "false",
        (unsigned int)payload->uptime_ms
    );

    if (written < 0 || (size_t)written >= buffer_size) {
        return -1;
    }

    return written;
}

bool mqtt_telemetry_publish(const char *topic, const char *json_payload, int qos, bool retain) {
    if (!g_mqtt_initialized || topic == NULL || json_payload == NULL) {
        return false;
    }

    (void)qos;
    (void)retain;

    /* Імітація неблокуючої відправки пакета у мережевий стек (TCP/IP socket або LwIP) */
    printf("[MQTT SENT] Topic: '%s' | Payload: %s\n", topic, json_payload);
    return true;
}

bool mqtt_telemetry_send_flow_report(const water_flow_metrics_t *metrics, bool power_good) {
    if (metrics == NULL) {
        return false;
    }

    mqtt_telemetry_payload_t payload = {
        .flow_rate_lpm = metrics->flow_rate_lpm,
        .total_volume_liters = metrics->total_volume_liters,
        .total_pulses = metrics->total_pulse_count,
        .power_good = power_good,
        .uptime_ms = metrics->last_update_ms
    };

    char json_buf[MQTT_MAX_PAYLOAD_LEN];
    int len = mqtt_telemetry_serialize_json(&payload, json_buf, sizeof(json_buf));
    if (len < 0) {
        return false;
    }

    return mqtt_telemetry_publish("v1/devices/me/telemetry/water", json_buf, 1, false);
}
