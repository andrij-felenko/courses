#include <string.h>
#include <stdbool.h>
#include <stdint.h>

#define MAX_SSID_LEN        32
#define MAX_PASSPHRASE_LEN  64

typedef struct {
    char ssid[MAX_SSID_LEN + 1];
    char password[MAX_PASSPHRASE_LEN + 1];
    bool valid;
} wifi_config_payload_t;

/* Спрощений синтаксичний аналіз JSON корисного навантаження */
static const char* extract_json_string(const char *json, const char *key, char *out, size_t max_len) {
    char search_pattern[40];
    search_pattern[0] = '"';
    strncpy(&search_pattern[1], key, sizeof(search_pattern) - 4);
    strcat(search_pattern, "\":\"");
    
    const char *start = strstr(json, search_pattern);
    if (!start) return NULL;
    start += strlen(search_pattern);
    
    const char *end = strchr(start, '"');
    if (!end) return NULL;
    
    size_t len = (size_t)(end - start);
    if (len >= max_len) len = max_len - 1;
    
    memcpy(out, start, len);
    out[len] = '\0';
    return end + 1;
}

int http_handle_wifi_config_post(const char *body, size_t body_len,
                                 wifi_config_payload_t *out_config,
                                 char *response_buf, size_t resp_max)
{
    if (!body || body_len == 0 || !out_config || !response_buf) {
        return 400; // Bad Request
    }

    memset(out_config, 0, sizeof(wifi_config_payload_t));

    if (!extract_json_string(body, "ssid", out_config->ssid, MAX_SSID_LEN + 1)) {
        strncpy(response_buf, "{\"error\":\"Missing or invalid SSID\"}", resp_max);
        return 422; // Unprocessable Entity
    }

    /* Пароль може бути порожнім для відкритих мереж */
    extract_json_string(body, "password", out_config->password, MAX_PASSPHRASE_LEN + 1);

    out_config->valid = true;
    strncpy(response_buf, "{\"status\":\"accepted\",\"message\":\"Connecting to station...\"}", resp_max);
    return 200; // OK
}
