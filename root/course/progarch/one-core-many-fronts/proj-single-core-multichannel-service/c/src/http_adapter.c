#include "http_adapter.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#ifdef _WIN32
#include <winsock2.h>
#define socket_recv(fd, buf, len) recv((SOCKET)(fd), (char *)(buf), (int)(len), 0)
#define socket_send(fd, buf, len) send((SOCKET)(fd), (const char *)(buf), (int)(len), 0)
#else
#include <unistd.h>
#include <sys/socket.h>
#define socket_recv(fd, buf, len) recv(fd, buf, len, 0)
#define socket_send(fd, buf, len) send(fd, buf, len, 0)
#endif

/**
 * @file http_adapter.c
 * @brief Реалізація драйвуючого HTTP-обробника клієнтських сокетів.
 */

#define HTTP_BUF_SIZE 4096

/**
 * @brief Допоміжна функція пошуку підрядка без урахування регістру символів.
 */
static const char *case_str_search(const char *haystack, const char *needle) {
    if (!haystack || !needle) return NULL;
    size_t needle_len = strlen(needle);
    while (*haystack) {
        size_t i = 0;
        while (needle[i] && tolower((unsigned char)haystack[i]) == tolower((unsigned char)needle[i])) {
            i++;
        }
        if (i == needle_len) return haystack;
        haystack++;
    }
    return NULL;
}

/**
 * @brief Видобуває значення текстового поля JSON з тіла запиту.
 */
static bool parse_json_string_field(const char *json, const char *field, char *out_val, size_t max_len) {
    char pattern[64];
    snprintf(pattern, sizeof(pattern), "\"%s\"", field);
    const char *pos = strstr(json, pattern);
    if (!pos) return false;

    pos += strlen(pattern);
    while (*pos && (*pos == ' ' || *pos == '\t' || *pos == ':')) pos++;
    if (*pos != '\"') return false;
    pos++;

    size_t idx = 0;
    while (*pos && *pos != '\"' && idx + 1 < max_len) {
        out_val[idx++] = *pos++;
    }
    out_val[idx] = '\0';
    return (*pos == '\"');
}

/**
 * @brief Видобуває числове значення з плаваючою крапкою з JSON-поля.
 */
static bool parse_json_double_field(const char *json, const char *field, double *out_val) {
    char pattern[64];
    snprintf(pattern, sizeof(pattern), "\"%s\"", field);
    const char *pos = strstr(json, pattern);
    if (!pos) return false;

    pos += strlen(pattern);
    while (*pos && (*pos == ' ' || *pos == '\t' || *pos == ':')) pos++;
    if (!*pos) return false;

    char *endptr = NULL;
    *out_val = strtod(pos, &endptr);
    return (endptr != pos);
}

/**
 * @brief Відправляє сформовану HTTP-відповідь у клієнтський сокет.
 */
static int send_http_response(int fd, int status_code, const char *reason_phrase, const char *json_body) {
    char header_buf[1024];
    size_t body_len = strlen(json_body);

    int hdr_len = snprintf(header_buf, sizeof(header_buf),
        "HTTP/1.1 %d %s\r\n"
        "Content-Type: application/json; charset=utf-8\r\n"
        "Content-Length: %zu\r\n"
        "Connection: close\r\n"
        "\r\n",
        status_code, reason_phrase, body_len);

    if (socket_send(fd, header_buf, hdr_len) < 0) return -1;
    if (socket_send(fd, json_body, body_len) < 0) return -1;
    return 0;
}

int http_adapter_handle_fd(inbound_port_t *port, int client_fd) {
    if (!port || client_fd < 0) {
        return -1;
    }

    char req_buf[HTTP_BUF_SIZE];
    ssize_t bytes = socket_recv(client_fd, req_buf, sizeof(req_buf) - 1);
    if (bytes <= 0) {
        return -1;
    }
    req_buf[bytes] = '\0';

    /* 1. Синтаксичний розбір першого рядка запиту (Request Line) */
    char method[16] = {0};
    char path[128] = {0};
    char version[16] = {0};

    if (sscanf(req_buf, "%15s %127s %15s", method, path, version) != 3) {
        send_http_response(client_fd, 400, "Bad Request", "{\"error\":\"bad_request\",\"message\":\"Помилка синтаксису HTTP-запиту\"}\r\n");
        return 0;
    }

    if (strcmp(method, "POST") != 0) {
        send_http_response(client_fd, 400, "Bad Request", "{\"error\":\"bad_request\",\"message\":\"Підтримується лише метод POST\"}\r\n");
        return 0;
    }

    if (strcmp(path, "/api/climate") != 0 && strcmp(path, "/climate") != 0) {
        send_http_response(client_fd, 400, "Bad Request", "{\"error\":\"bad_request\",\"message\":\"Невідомий ресурс API\"}\r\n");
        return 0;
    }

    /* 2. Пошук і розбір заголовка авторизації */
    char auth_token[CLIMATE_AUTH_TOKEN_LEN] = {0};
    const char *auth_hdr = case_str_search(req_buf, "Authorization:");
    if (auth_hdr) {
        auth_hdr += strlen("Authorization:");
        while (*auth_hdr == ' ' || *auth_hdr == '\t') auth_hdr++;
        if (strncmp(auth_hdr, "Bearer ", 7) == 0) {
            auth_hdr += 7;
        }
        size_t t_idx = 0;
        while (*auth_hdr && *auth_hdr != '\r' && *auth_hdr != '\n' && *auth_hdr != ' ' && t_idx + 1 < sizeof(auth_token)) {
            auth_token[t_idx++] = *auth_hdr++;
        }
        auth_token[t_idx] = '\0';
    }

    /* 3. Пошук тіла запиту (після подвійного перенесення рядка) */
    const char *body = strstr(req_buf, "\r\n\r\n");
    if (body) {
        body += 4;
    } else {
        body = strstr(req_buf, "\n\n");
        if (body) body += 2;
    }

    if (!body || *body == '\0') {
        send_http_response(client_fd, 400, "Bad Request", "{\"error\":\"bad_request\",\"message\":\"Тіло HTTP-запиту порожнє\"}\r\n");
        return 0;
    }

    /* 4. Парсинг JSON-параметрів "room" та "temp" */
    char room_id[CLIMATE_ROOM_ID_LEN] = {0};
    double target_temp = 0.0;

    if (!parse_json_string_field(body, "room", room_id, sizeof(room_id)) ||
        !parse_json_double_field(body, "temp", &target_temp)) {
        send_http_response(client_fd, 400, "Bad Request",
                           "{\"error\":\"bad_request\",\"message\":\"Помилка синтаксису JSON або відсутні поля 'room'/'temp'\"}\r\n");
        return 0;
    }

    /* 5. Трансляція в нейтральну команду ядра та виклик вхідного порту */
    climate_cmd_t cmd;
    memset(&cmd, 0, sizeof(cmd));
    strncpy(cmd.room_id, room_id, sizeof(cmd.room_id) - 1);
    cmd.target_temp_c = target_temp;
    strncpy(cmd.auth_token, auth_token, sizeof(cmd.auth_token) - 1);

    climate_result_t result;
    memset(&result, 0, sizeof(result));

    core_status_t status = inbound_port_execute(port, &cmd, &result);

    /* 6. Трансляція результату ядра у відповідний протокольний HTTP-код (200, 400, 401, 422) */
    char json_resp[512];
    switch (status) {
        case CORE_STATUS_OK:
            snprintf(json_resp, sizeof(json_resp),
                     "{\"status\":\"ok\",\"room\":\"%s\",\"previous_temp\":%.2f,\"current_temp\":%.2f,\"message\":\"%s\"}\r\n",
                     cmd.room_id, result.previous_temp_c, result.current_temp_c, result.message);
            send_http_response(client_fd, 200, "OK", json_resp);
            break;

        case CORE_STATUS_INVALID_ARG:
            snprintf(json_resp, sizeof(json_resp),
                     "{\"error\":\"bad_request\",\"message\":\"%s\"}\r\n", result.message);
            send_http_response(client_fd, 400, "Bad Request", json_resp);
            break;

        case CORE_STATUS_UNAUTHORIZED:
            snprintf(json_resp, sizeof(json_resp),
                     "{\"error\":\"unauthorized\",\"message\":\"%s\"}\r\n", result.message);
            send_http_response(client_fd, 401, "Unauthorized", json_resp);
            break;

        case CORE_STATUS_OUT_OF_RANGE:
            snprintf(json_resp, sizeof(json_resp),
                     "{\"error\":\"unprocessable_entity\",\"message\":\"%s\"}\r\n", result.message);
            send_http_response(client_fd, 422, "Unprocessable Entity", json_resp);
            break;

        case CORE_STATUS_INTERNAL_ERROR:
        default:
            snprintf(json_resp, sizeof(json_resp),
                     "{\"error\":\"internal_server_error\",\"message\":\"%s\"}\r\n", result.message);
            send_http_response(client_fd, 500, "Internal Server Error", json_resp);
            break;
    }

    return 0;
}
