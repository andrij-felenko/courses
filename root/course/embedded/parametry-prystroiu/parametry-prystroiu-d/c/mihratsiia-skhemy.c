// Покрокова міграція схем конфігурації (C99)
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

// Схема v1: перша версія прошивки
typedef struct {
    char     wifi_ssid[32];
    char     wifi_pass[32];
    uint32_t server_ip_raw;
    uint32_t report_interval_s;
} __attribute__((packed)) cfg_schema_v1_t;

// Схема v2: додано порт брокера та рівень QoS
typedef struct {
    char     wifi_ssid[32];
    char     wifi_pass[32];
    uint32_t server_ip_raw;
    uint32_t report_interval_s;
    uint16_t mqtt_port;      // Нове поле
    uint8_t  mqtt_qos;       // Нове поле
    uint8_t  reserved;
} __attribute__((packed)) cfg_schema_v2_t;

// Схема v3: перехід на доменні імена та прапорець TLS
typedef struct {
    char     wifi_ssid[32];
    char     wifi_pass[32];
    char     server_host[64]; // Замість сирого IP
    uint32_t report_interval_s;
    uint16_t mqtt_port;
    uint8_t  mqtt_qos;
    uint8_t  tls_enable;      // Нове поле
} __attribute__((packed)) cfg_schema_v3_t;

bool migrate_v1_to_v2(const cfg_schema_v1_t *old_c, cfg_schema_v2_t *new_c) {
    memset(new_c, 0, sizeof(cfg_schema_v2_t));
    memcpy(new_c->wifi_ssid, old_c->wifi_ssid, 32);
    memcpy(new_c->wifi_pass, old_c->wifi_pass, 32);
    new_c->server_ip_raw = old_c->server_ip_raw;
    new_c->report_interval_s = old_c->report_interval_s;
    
    // Ініціалізація нових полів безпечними дефолтами
    new_c->mqtt_port = 1883;
    new_c->mqtt_qos = 1;
    return true;
}

bool migrate_v2_to_v3(const cfg_schema_v2_t *old_c, cfg_schema_v3_t *new_c) {
    memset(new_c, 0, sizeof(cfg_schema_v3_t));
    memcpy(new_c->wifi_ssid, old_c->wifi_ssid, 32);
    memcpy(new_c->wifi_pass, old_c->wifi_pass, 32);
    new_c->report_interval_s = old_c->report_interval_s;
    new_c->mqtt_port = old_c->mqtt_port;
    new_c->mqtt_qos = old_c->mqtt_qos;
    
    // Трансформація старого IPv4 у строковий хост
    const uint8_t *ip = (const uint8_t*)&old_c->server_ip_raw;
    snprintf(new_c->server_host, sizeof(new_c->server_host), "%u.%u.%u.%u", ip[0], ip[1], ip[2], ip[3]);
    
    // За замовчуванням вмикаємо TLS для версії 3
    new_c->tls_enable = 1;
    return true;
}
