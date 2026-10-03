#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "esp8266_ssl.h"

/* Статичний буфер для кільцевого буфера UART RX */
static uint8_t rx_buffer_storage[2048];
static ring_buffer_t g_rx_rb;

/* Симуляція системного таймера (мілісекунди) */
static uint32_t simulated_get_ticks_ms(void) {
#if defined(_WIN32) || defined(_WIN64)
    return (uint32_t)clock();
#else
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint32_t)(ts.tv_sec * 1000 + ts.tv_nsec / 1000000);
#endif
}

/* Симуляція пауз мікроконтролера */
static void simulated_delay_ms(uint32_t ms) {
    uint32_t start = simulated_get_ticks_ms();
    while ((simulated_get_ticks_ms() - start) < ms) {
        /* Очікування */
    }
}

/* Мок-емуляція відповідей ESP8266 AT-інтерпретатора у кільцевий буфер */
static void simulated_uart_tx(const uint8_t *data, size_t len) {
    char cmd[512] = {0};
    if (len < sizeof(cmd)) {
        memcpy(cmd, data, len);
        cmd[len] = '\0';
    }

    printf("[UART TX -> ESP8266]: %s", cmd);
    if (strchr(cmd, '\n') == NULL) {
        printf("\n");
    }

    /* Емуляція асинхронної відповіді модуля ESP8266 на AT-команди */
    if (strstr(cmd, "AT+CIPSSLCCONF") != NULL ||
        strstr(cmd, "AT+CIPSSLCSNI") != NULL ||
        strstr(cmd, "AT+CIPSSLCSZ") != NULL ||
        strstr(cmd, "AT+CIPCLOSE") != NULL) {
        const char *resp = "OK\r\n";
        ring_buffer_push_bytes(&g_rx_rb, (const uint8_t*)resp, strlen(resp));
    }
    else if (strstr(cmd, "AT+CIPSTART") != NULL) {
        const char *resp = "CONNECT\r\n\r\nOK\r\n";
        ring_buffer_push_bytes(&g_rx_rb, (const uint8_t*)resp, strlen(resp));
    }
    else if (strstr(cmd, "AT+CIPSEND") != NULL) {
        const char *resp = "> ";
        ring_buffer_push_bytes(&g_rx_rb, (const uint8_t*)resp, strlen(resp));
    }
    else if (strstr(cmd, "GET ") != NULL) {
        const char *resp_ok = "SEND OK\r\n";
        const char *ipd_data = "+IPD,135:HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 31\r\n\r\n{\"status\":\"ok\",\"sensor\":\"temp\"}CLOSED\r\n";
        ring_buffer_push_bytes(&g_rx_rb, (const uint8_t*)resp_ok, strlen(resp_ok));
        ring_buffer_push_bytes(&g_rx_rb, (const uint8_t*)ipd_data, strlen(ipd_data));
    }
    else if (strstr(cmd, "POST ") != NULL) {
        const char *resp_ok = "SEND OK\r\n";
        const char *ipd_data = "+IPD,142:HTTP/1.1 201 Created\r\nContent-Type: application/json\r\nContent-Length: 35\r\n\r\n{\"result\":\"created\",\"id\":10042}CLOSED\r\n";
        ring_buffer_push_bytes(&g_rx_rb, (const uint8_t*)resp_ok, strlen(resp_ok));
        ring_buffer_push_bytes(&g_rx_rb, (const uint8_t*)ipd_data, strlen(ipd_data));
    }
}

int main(void) {
    printf("====================================================\n");
    printf("  C-Driver ESP8266 SSL/TLS AT-Command Controller    \n");
    printf("====================================================\n\n");

    /* 1. Ініціалізація кільцевого буфера RX */
    if (!ring_buffer_init(&g_rx_rb, rx_buffer_storage, sizeof(rx_buffer_storage))) {
        printf("[ERROR] Невдала ініціалізація RingBuffer!\n");
        return EXIT_FAILURE;
    }

    /* 2. Ініціалізація контексту C-драйвера ESP8266 SSL */
    esp8266_ssl_ctx_t ssl_ctx;
    if (esp8266_ssl_init(&ssl_ctx,
                         &g_rx_rb,
                         simulated_uart_tx,
                         simulated_get_ticks_ms,
                         simulated_delay_ms) != ESP8266_SSL_OK) {
        printf("[ERROR] Невдала ініціалізація контексту SSL!\n");
        return EXIT_FAILURE;
    }

    /* 3. Конфігурація режимів SSL/TLS */
    esp8266_tls_config_t tls_cfg;
    memset(&tls_cfg, 0, sizeof(tls_cfg));
    tls_cfg.auth_mode = ESP8266_TLS_AUTH_VERIFY_SERVER; /* Верифікація CA-сертифіката */
    strncpy(tls_cfg.sni_hostname, "api.example.com", sizeof(tls_cfg.sni_hostname) - 1);
    tls_cfg.buffer_size = 4096;
    tls_cfg.handshake_timeout_ms = 10000;

    printf("[1] Налаштування параметрів SSL (AT+CIPSSLCCONF, SNI, Buffer Size)...\n");
    if (esp8266_ssl_configure_tls(&ssl_ctx, &tls_cfg) == ESP8266_SSL_OK) {
        printf("[OK] Параметри TLS успішно застосовано.\n\n");
    } else {
        printf("[FAIL] Помилка налаштування TLS!\n\n");
    }

    /* 4. Виконання захищеного HTTPS GET запиту */
    uint8_t response_body_buf[1024];
    http_response_t http_resp;
    http_response_init(&http_resp, response_body_buf, sizeof(response_body_buf));

    printf("[2] Виконання HTTPS GET запиту на https://api.example.com/v1/telemetry...\n");
    esp8266_ssl_status_t status_get = esp8266_ssl_http_get(&ssl_ctx,
                                                            "api.example.com",
                                                            443,
                                                            "/v1/telemetry",
                                                            &http_resp,
                                                            15000);

    if (status_get == ESP8266_SSL_OK) {
        printf("\n---> [Отримано HTTPS GET відповідь]:\n");
        printf("     HTTP Status Code: %d (%s)\n", http_resp.status_code, http_resp.status_text);
        printf("     Тіло відповіді (%zu байтів): %s\n\n", http_resp.body_len, (char*)http_resp.body_buf);
    } else {
        printf("[FAIL] Помилка виконання HTTPS GET: %d\n\n", (int)status_get);
    }

    /* 5. Виконання захищеного HTTPS POST запиту */
    http_response_clear(&http_resp);
    const char *post_payload = "{\"device_id\":\"mcu_node_01\",\"value\":25.4}";

    printf("[3] Виконання HTTPS POST запиту на https://api.example.com/v1/data...\n");
    esp8266_ssl_status_t status_post = esp8266_ssl_http_post(&ssl_ctx,
                                                              "api.example.com",
                                                              443,
                                                              "/v1/data",
                                                              "application/json",
                                                              (const uint8_t*)post_payload,
                                                              strlen(post_payload),
                                                              &http_resp,
                                                              15000);

    if (status_post == ESP8266_SSL_OK) {
        printf("\n---> [Отримано HTTPS POST відповідь]:\n");
        printf("     HTTP Status Code: %d (%s)\n", http_resp.status_code, http_resp.status_text);
        printf("     Тіло відповіді (%zu байтів): %s\n\n", http_resp.body_len, (char*)http_resp.body_buf);
    } else {
        printf("[FAIL] Помилка виконання HTTPS POST: %d\n\n", (int)status_post);
    }

    /* 6. Обробка періодичного FSM-автомата */
    esp8266_ssl_process(&ssl_ctx);

    printf("====================================================\n");
    printf("  Демонстрацію C-драйвера успішно завершено!         \n");
    printf("====================================================\n");

    return EXIT_SUCCESS;
}
