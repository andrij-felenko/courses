#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

// Типи мережевих режимів для генерації AT+CIPSEND
typedef struct {
    bool is_multiplex;     // CIPMUX=1
    uint8_t link_id;       // 0..4 (використовується при is_multiplex == true)
    uint16_t length;       // Розмір payload N
    const char* remote_ip; // NULL для стандартного TCP, або IP-адреса для UDP
    uint16_t remote_port;  // Порт для UDP
} CipsendParam;

size_t build_cipsend_command(const CipsendParam* param, char* buffer, size_t max_len) {
    if (!param || !buffer) return 0;

    int written = 0;
    if (param->remote_ip != NULL && strlen(param->remote_ip) > 0) {
        // Динамічний UDP-режим із вказуванням цільового вузла
        if (param->is_multiplex) {
            written = snprintf(buffer, max_len, "AT+CIPSEND=%u,%u,\"%s\",%u\r\n",
                               param->link_id, param->length, param->remote_ip, param->remote_port);
        } else {
            written = snprintf(buffer, max_len, "AT+CIPSEND=%u,\"%s\",%u\r\n",
                               param->length, param->remote_ip, param->remote_port);
        }
    } else {
        // Стандартний режим для встановленого TCP-з'єднання
        if (param->is_multiplex) {
            written = snprintf(buffer, max_len, "AT+CIPSEND=%u,%u\r\n",
                               param->link_id, param->length);
        } else {
            written = snprintf(buffer, max_len, "AT+CIPSEND=%u\r\n",
                               param->length);
        }
    }
    return (written > 0 && (size_t)written < max_len) ? (size_t)written : 0;
}
