#include "esp8266_ssl.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>

/* Локальні допоміжні функції */

static void send_raw_data(esp8266_ssl_ctx_t *ctx, const uint8_t *data, size_t len) {
    if (ctx && ctx->tx_fn && data && len > 0) {
        ctx->tx_fn(data, len);
    }
}

static void send_raw_string(esp8266_ssl_ctx_t *ctx, const char *str) {
    if (str) {
        send_raw_data(ctx, (const uint8_t*)str, strlen(str));
    }
}

static esp8266_ssl_status_t wait_for_reply(esp8266_ssl_ctx_t *ctx,
                                            const char *expected_reply,
                                            uint32_t timeout_ms) {
    uint32_t start_time = ctx->ticks_fn();

    while ((ctx->ticks_fn() - start_time) < timeout_ms) {
        if (ring_buffer_find_pattern(ctx->rx_rb, expected_reply) >= 0) {
            return ESP8266_SSL_OK;
        }

        if (ring_buffer_find_pattern(ctx->rx_rb, "ERROR\r\n") >= 0 ||
            ring_buffer_find_pattern(ctx->rx_rb, "FAIL\r\n") >= 0) {
            ctx->state = ESP8266_SSL_STATE_ERROR;
            return ESP8266_SSL_ERROR;
        }

        if (ring_buffer_find_pattern(ctx->rx_rb, "CLOSED\r\n") >= 0) {
            ctx->is_connected = false;
            if (strcmp(expected_reply, "CLOSED\r\n") == 0) {
                return ESP8266_SSL_OK;
            }
            ctx->state = ESP8266_SSL_STATE_ERROR;
            return ESP8266_SSL_ERR_CLOSED;
        }

        if (ctx->delay_fn) {
            ctx->delay_fn(1);
        }
    }

    ctx->state = ESP8266_SSL_STATE_ERROR;
    return ESP8266_SSL_TIMEOUT;
}

static esp8266_ssl_status_t send_at_command(esp8266_ssl_ctx_t *ctx,
                                            const char *cmd,
                                            const char *expected_reply,
                                            uint32_t timeout_ms) {
    ring_buffer_clear(ctx->rx_rb);
    send_raw_string(ctx, cmd);
    send_raw_string(ctx, "\r\n");
    return wait_for_reply(ctx, expected_reply, timeout_ms);
}

static void append_payload_to_response(http_response_t *resp, const uint8_t *data, size_t len) {
    if (!resp || !data || len == 0) {
        return;
    }

    /* Якщо заголовки HTTP ще не розібрано, шукаємо межу \r\n\r\n */
    if (!resp->headers_parsed) {
        for (size_t i = 0; i < len; ++i) {
            /* Переносимо байти по одному для визначення кінця заголовків */
            if (resp->body_len < resp->body_capacity - 1) {
                resp->body_buf[resp->body_len++] = data[i];
                resp->body_buf[resp->body_len] = '\0';
            }

            /* Шукаємо \r\n\r\n у накопиченому буфері */
            char *hdr_end = strstr((char*)resp->body_buf, "\r\n\r\n");
            if (hdr_end) {
                size_t hdr_len = (size_t)(hdr_end - (char*)resp->body_buf) + 4;

                /* Розбір рядок статусу: HTTP/1.1 200 OK */
                char *first_line = (char*)resp->body_buf;
                char *space1 = strchr(first_line, ' ');
                if (space1) {
                    resp->status_code = atoi(space1 + 1);
                    char *space2 = strchr(space1 + 1, ' ');
                    if (space2) {
                        char *line_end = strstr(space2, "\r\n");
                        if (line_end) {
                            size_t txt_len = (size_t)(line_end - (space2 + 1));
                            if (txt_len >= sizeof(resp->status_text)) {
                                txt_len = sizeof(resp->status_text) - 1;
                            }
                            memcpy(resp->status_text, space2 + 1, txt_len);
                            resp->status_text[txt_len] = '\0';
                        }
                    }
                }

                /* Зміщуємо корисне навантаження тіла на початок буфера */
                size_t leftover = resp->body_len - hdr_len;
                if (leftover > 0) {
                    memmove(resp->body_buf, resp->body_buf + hdr_len, leftover);
                }
                resp->body_len = leftover;
                resp->body_buf[resp->body_len] = '\0';
                resp->headers_parsed = true;

                /* Копіюємо решту байтів з поточного кадру в тіло */
                size_t remaining_bytes = len - (i + 1);
                if (remaining_bytes > 0) {
                    size_t to_copy = remaining_bytes;
                    if (resp->body_len + to_copy > resp->body_capacity - 1) {
                        to_copy = resp->body_capacity - 1 - resp->body_len;
                    }
                    memcpy(resp->body_buf + resp->body_len, data + i + 1, to_copy);
                    resp->body_len += to_copy;
                    resp->body_buf[resp->body_len] = '\0';
                }
                break;
            }
        }
    } else {
        /* Заголовки вже розібрано, дописуємо безпосередньо у буфер тіла */
        size_t to_copy = len;
        if (resp->body_len + to_copy > resp->body_capacity - 1) {
            to_copy = resp->body_capacity - 1 - resp->body_len;
        }
        memcpy(resp->body_buf + resp->body_len, data, to_copy);
        resp->body_len += to_copy;
        resp->body_buf[resp->body_len] = '\0';
    }
}

static esp8266_ssl_status_t parse_ipd_stream(esp8266_ssl_ctx_t *ctx,
                                             http_response_t *response,
                                             uint32_t timeout_ms) {
    ctx->state = ESP8266_SSL_STATE_WAIT_RESPONSE;
    uint32_t start_time = ctx->ticks_fn();

    while ((ctx->ticks_fn() - start_time) < timeout_ms) {
        /* Перевірка наявності кадру +IPD, */
        int ipd_pos = ring_buffer_find_pattern(ctx->rx_rb, "+IPD,");
        if (ipd_pos >= 0) {
            /* Пропускаємо префікс "+IPD," */
            ring_buffer_skip(ctx->rx_rb, (size_t)ipd_pos + 5);

            /* Зчитуємо числову довжину кадру до двоеточія ':' */
            char len_buf[16] = {0};
            size_t len_idx = 0;
            uint8_t ch = 0;
            bool colon_found = false;
            uint32_t parse_start = ctx->ticks_fn();

            while ((ctx->ticks_fn() - parse_start) < 2000) {
                if (ring_buffer_pop(ctx->rx_rb, &ch)) {
                    if (ch == ':') {
                        colon_found = true;
                        break;
                    }
                    if (isdigit(ch) && len_idx < sizeof(len_buf) - 1) {
                        len_buf[len_idx++] = (char)ch;
                    }
                } else if (ctx->delay_fn) {
                    ctx->delay_fn(1);
                }
            }

            if (colon_found && len_idx > 0) {
                size_t frame_len = (size_t)strtoul(len_buf, NULL, 10);
                ctx->state = ESP8266_SSL_STATE_READING_IPD;

                /* Накопичуємо frame_len байтів з буфера */
                uint8_t temp_chunk[128];
                size_t read_accumulated = 0;
                uint32_t frame_start = ctx->ticks_fn();

                while (read_accumulated < frame_len && (ctx->ticks_fn() - frame_start) < 5000) {
                    size_t to_read = frame_len - read_accumulated;
                    if (to_read > sizeof(temp_chunk)) {
                        to_read = sizeof(temp_chunk);
                    }

                    size_t chunk_bytes = ring_buffer_pop_bytes(ctx->rx_rb, temp_chunk, to_read);
                    if (chunk_bytes > 0) {
                        read_accumulated += chunk_bytes;
                        if (response) {
                            append_payload_to_response(response, temp_chunk, chunk_bytes);
                        }
                    } else if (ctx->delay_fn) {
                        ctx->delay_fn(1);
                    }
                }
            }
        }

        /* Перевірка на закриття сокета сервером */
        if (ring_buffer_find_pattern(ctx->rx_rb, "CLOSED\r\n") >= 0) {
            ctx->is_connected = false;
            if (response) {
                response->is_complete = true;
            }
            break;
        }

        if (ctx->delay_fn) {
            ctx->delay_fn(2);
        }
    }

    ctx->state = ESP8266_SSL_STATE_IDLE;
    return (response && response->headers_parsed) ? ESP8266_SSL_OK : ESP8266_SSL_ERROR;
}

/* Публічні функції API */

void http_response_init(http_response_t *resp, uint8_t *body_buf, size_t body_cap) {
    if (!resp) return;
    resp->status_code = 0;
    resp->status_text[0] = '\0';
    resp->headers_parsed = false;
    resp->is_complete = false;
    resp->body_buf = body_buf;
    resp->body_len = 0;
    resp->body_capacity = body_cap;
    if (resp->body_buf && resp->body_capacity > 0) {
        resp->body_buf[0] = '\0';
    }
}

void http_response_clear(http_response_t *resp) {
    if (!resp) return;
    resp->status_code = 0;
    resp->status_text[0] = '\0';
    resp->headers_parsed = false;
    resp->is_complete = false;
    resp->body_len = 0;
    if (resp->body_buf && resp->body_capacity > 0) {
        resp->body_buf[0] = '\0';
    }
}

esp8266_ssl_status_t esp8266_ssl_init(esp8266_ssl_ctx_t *ctx,
                                       ring_buffer_t *rx_rb,
                                       esp8266_uart_tx_fn tx_fn,
                                       esp8266_get_ticks_ms_fn ticks_fn,
                                       esp8266_delay_ms_fn delay_fn) {
    if (!ctx || !rx_rb || !tx_fn || !ticks_fn) {
        return ESP8266_SSL_ERROR;
    }

    ctx->rx_rb = rx_rb;
    ctx->tx_fn = tx_fn;
    ctx->ticks_fn = ticks_fn;
    ctx->delay_fn = delay_fn;
    ctx->state = ESP8266_SSL_STATE_IDLE;
    ctx->is_connected = false;
    ctx->state_timer = ctx->ticks_fn();

    memset(&ctx->tls_config, 0, sizeof(esp8266_tls_config_t));
    ctx->tls_config.auth_mode = ESP8266_TLS_AUTH_NONE;
    ctx->tls_config.buffer_size = 4096;
    ctx->tls_config.handshake_timeout_ms = 15000;

    return ESP8266_SSL_OK;
}

esp8266_ssl_status_t esp8266_ssl_configure_tls(esp8266_ssl_ctx_t *ctx,
                                                const esp8266_tls_config_t *config) {
    if (!ctx || !config) {
        return ESP8266_SSL_ERROR;
    }

    ctx->state = ESP8266_SSL_STATE_CONFIGURING_TLS;
    char cmd_buf[160];

    /* 1. Налаштування режиму верифікації SSL/TLS: AT+CIPSSLCCONF=<mode> */
    snprintf(cmd_buf, sizeof(cmd_buf), "AT+CIPSSLCCONF=%d", (int)config->auth_mode);
    if (send_at_command(ctx, cmd_buf, "OK\r\n", 3000) != ESP8266_SSL_OK) {
        return ESP8266_SSL_ERROR;
    }

    /* 2. Налаштування SNI (Server Name Indication): AT+CIPSSLCSNI="<hostname>" */
    if (strlen(config->sni_hostname) > 0) {
        snprintf(cmd_buf, sizeof(cmd_buf), "AT+CIPSSLCSNI=\"%s\"", config->sni_hostname);
        if (send_at_command(ctx, cmd_buf, "OK\r\n", 3000) != ESP8266_SSL_OK) {
            return ESP8266_SSL_ERROR;
        }
    }

    /* 3. Конфігурація розміру буфера TLS: AT+CIPSSLCSZ=<size> */
    if (config->buffer_size > 0) {
        snprintf(cmd_buf, sizeof(cmd_buf), "AT+CIPSSLCSZ=%u", (unsigned int)config->buffer_size);
        if (send_at_command(ctx, cmd_buf, "OK\r\n", 3000) != ESP8266_SSL_OK) {
            return ESP8266_SSL_ERROR;
        }
    }

    memcpy(&ctx->tls_config, config, sizeof(esp8266_tls_config_t));
    ctx->state = ESP8266_SSL_STATE_IDLE;
    return ESP8266_SSL_OK;
}

esp8266_ssl_status_t esp8266_ssl_connect(esp8266_ssl_ctx_t *ctx,
                                         const char *host,
                                         uint16_t port,
                                         uint32_t timeout_ms) {
    if (!ctx || !host) {
        return ESP8266_SSL_ERROR;
    }

    ctx->state = ESP8266_SSL_STATE_CONNECTING;
    char cmd_buf[192];
    snprintf(cmd_buf, sizeof(cmd_buf), "AT+CIPSTART=\"SSL\",\"%s\",%u", host, (unsigned int)port);

    ring_buffer_clear(ctx->rx_rb);
    send_raw_string(ctx, cmd_buf);
    send_raw_string(ctx, "\r\n");

    uint32_t start_time = ctx->ticks_fn();
    while ((ctx->ticks_fn() - start_time) < timeout_ms) {
        if (ring_buffer_find_pattern(ctx->rx_rb, "CONNECT\r\n") >= 0 ||
            ring_buffer_find_pattern(ctx->rx_rb, "OK\r\n") >= 0) {
            ctx->is_connected = true;
            ctx->state = ESP8266_SSL_STATE_IDLE;
            return ESP8266_SSL_OK;
        }

        if (ring_buffer_find_pattern(ctx->rx_rb, "CLOSED\r\n") >= 0 ||
            ring_buffer_find_pattern(ctx->rx_rb, "ERROR\r\n") >= 0) {
            ctx->state = ESP8266_SSL_STATE_ERROR;
            return ESP8266_SSL_ERR_HANDSHAKE;
        }

        if (ctx->delay_fn) {
            ctx->delay_fn(2);
        }
    }

    ctx->state = ESP8266_SSL_STATE_ERROR;
    return ESP8266_SSL_TIMEOUT;
}

esp8266_ssl_status_t esp8266_ssl_close(esp8266_ssl_ctx_t *ctx) {
    if (!ctx) {
        return ESP8266_SSL_ERROR;
    }

    if (!ctx->is_connected) {
        return ESP8266_SSL_OK;
    }

    ctx->state = ESP8266_SSL_STATE_CLOSING;
    esp8266_ssl_status_t res = send_at_command(ctx, "AT+CIPCLOSE", "OK\r\n", 3000);
    ctx->is_connected = false;
    ctx->state = ESP8266_SSL_STATE_IDLE;
    return res;
}

esp8266_ssl_status_t esp8266_ssl_http_get(esp8266_ssl_ctx_t *ctx,
                                           const char *host,
                                           uint16_t port,
                                           const char *path,
                                           http_response_t *response,
                                           uint32_t timeout_ms) {
    if (!ctx || !host || !path || !response) {
        return ESP8266_SSL_ERROR;
    }

    http_response_clear(response);

    /* Автоматичне встановлення SNI якщо хост змінився */
    if (strcmp(ctx->tls_config.sni_hostname, host) != 0) {
        esp8266_tls_config_t cfg = ctx->tls_config;
        strncpy(cfg.sni_hostname, host, sizeof(cfg.sni_hostname) - 1);
        cfg.sni_hostname[sizeof(cfg.sni_hostname) - 1] = '\0';
        if (esp8266_ssl_configure_tls(ctx, &cfg) != ESP8266_SSL_OK) {
            return ESP8266_SSL_ERROR;
        }
    }

    /* Відкриття SSL-сокету */
    if (esp8266_ssl_connect(ctx, host, port, timeout_ms) != ESP8266_SSL_OK) {
        return ESP8266_SSL_ERR_HANDSHAKE;
    }

    /* Формування HTTP GET пакета */
    char http_req[512];
    int req_len = snprintf(http_req, sizeof(http_req),
                           "GET %s HTTP/1.1\r\n"
                           "Host: %s\r\n"
                           "User-Agent: ESP8266-C-SSL-Driver/1.0\r\n"
                           "Connection: close\r\n\r\n",
                           path, host);

    if (req_len < 0 || req_len >= (int)sizeof(http_req)) {
        esp8266_ssl_close(ctx);
        return ESP8266_SSL_ERROR;
    }

    /* Фаза 1: Резервування довжини AT+CIPSEND=<len> */
    ctx->state = ESP8266_SSL_STATE_SENDING_CMD;
    char cmd_send[32];
    snprintf(cmd_send, sizeof(cmd_send), "AT+CIPSEND=%d", req_len);

    if (send_at_command(ctx, cmd_send, ">", 3000) != ESP8266_SSL_OK) {
        esp8266_ssl_close(ctx);
        return ESP8266_SSL_ERROR;
    }

    /* Фаза 2: Відправка сирого корисного навантаження HTTP після символу '>' */
    ctx->state = ESP8266_SSL_STATE_SENDING_PAYLOAD;
    ring_buffer_clear(ctx->rx_rb);
    send_raw_string(ctx, http_req);

    if (wait_for_reply(ctx, "SEND OK\r\n", 5000) != ESP8266_SSL_OK) {
        esp8266_ssl_close(ctx);
        return ESP8266_SSL_ERROR;
    }

    /* Потоковий розбір вхідних кадрів +IPD */
    esp8266_ssl_status_t status = parse_ipd_stream(ctx, response, timeout_ms);
    esp8266_ssl_close(ctx);
    return status;
}

esp8266_ssl_status_t esp8266_ssl_http_post(esp8266_ssl_ctx_t *ctx,
                                            const char *host,
                                            uint16_t port,
                                            const char *path,
                                            const char *content_type,
                                            const uint8_t *body,
                                            size_t body_len,
                                            http_response_t *response,
                                            uint32_t timeout_ms) {
    if (!ctx || !host || !path || !content_type || !response) {
        return ESP8266_SSL_ERROR;
    }

    http_response_clear(response);

    if (strcmp(ctx->tls_config.sni_hostname, host) != 0) {
        esp8266_tls_config_t cfg = ctx->tls_config;
        strncpy(cfg.sni_hostname, host, sizeof(cfg.sni_hostname) - 1);
        cfg.sni_hostname[sizeof(cfg.sni_hostname) - 1] = '\0';
        if (esp8266_ssl_configure_tls(ctx, &cfg) != ESP8266_SSL_OK) {
            return ESP8266_SSL_ERROR;
        }
    }

    if (esp8266_ssl_connect(ctx, host, port, timeout_ms) != ESP8266_SSL_OK) {
        return ESP8266_SSL_ERR_HANDSHAKE;
    }

    /* Формування заголовків HTTP POST */
    char hdr_buf[512];
    int hdr_len = snprintf(hdr_buf, sizeof(hdr_buf),
                           "POST %s HTTP/1.1\r\n"
                           "Host: %s\r\n"
                           "User-Agent: ESP8266-C-SSL-Driver/1.0\r\n"
                           "Content-Type: %s\r\n"
                           "Content-Length: %zu\r\n"
                           "Connection: close\r\n\r\n",
                           path, host, content_type, body_len);

    if (hdr_len < 0 || hdr_len >= (int)sizeof(hdr_buf)) {
        esp8266_ssl_close(ctx);
        return ESP8266_SSL_ERROR;
    }

    size_t total_payload_len = (size_t)hdr_len + body_len;

    /* Фаза 1: Резервування довжини для всього пакета (заголовки + тіло) */
    ctx->state = ESP8266_SSL_STATE_SENDING_CMD;
    char cmd_send[32];
    snprintf(cmd_send, sizeof(cmd_send), "AT+CIPSEND=%zu", total_payload_len);

    if (send_at_command(ctx, cmd_send, ">", 3000) != ESP8266_SSL_OK) {
        esp8266_ssl_close(ctx);
        return ESP8266_SSL_ERROR;
    }

    /* Фаза 2: Передача заголовків та тіла після запрошення '>' */
    ctx->state = ESP8266_SSL_STATE_SENDING_PAYLOAD;
    ring_buffer_clear(ctx->rx_rb);
    send_raw_string(ctx, hdr_buf);
    if (body && body_len > 0) {
        send_raw_data(ctx, body, body_len);
    }

    if (wait_for_reply(ctx, "SEND OK\r\n", 5000) != ESP8266_SSL_OK) {
        esp8266_ssl_close(ctx);
        return ESP8266_SSL_ERROR;
    }

    esp8266_ssl_status_t status = parse_ipd_stream(ctx, response, timeout_ms);
    esp8266_ssl_close(ctx);
    return status;
}

void esp8266_ssl_process(esp8266_ssl_ctx_t *ctx) {
    if (!ctx) return;

    /* Аварійне скидання стану та сесії при виникненні помилки FSM */
    if (ctx->state == ESP8266_SSL_STATE_ERROR) {
        if (ctx->is_connected) {
            esp8266_ssl_close(ctx);
        }
        ctx->state = ESP8266_SSL_STATE_IDLE;
    }
}

esp8266_ssl_state_t esp8266_ssl_get_state(const esp8266_ssl_ctx_t *ctx) {
    return ctx ? ctx->state : ESP8266_SSL_STATE_ERROR;
}
