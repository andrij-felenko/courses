#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>

// Результат розбору портів
typedef struct {
    int port;
    bool is_valid;
} PortResult;

// Структура підсумкової конфігурації
typedef struct {
    unsigned short port;
} ServerConfig;

// Очищення пробілів на початку та в кінці C-рядка
static const char* trim_leading(const char* str) {
    while (*str && isspace((unsigned char)*str)) str++;
    return str;
}

// Пошук розділювача '=' та виділення значення
static bool extract_value(const char* line, const char* expected_key, char* out_val, size_t max_len) {
    const char* trimmed = trim_leading(line);
    size_t key_len = strlen(expected_key);
    
    if (strncmp(trimmed, expected_key, key_len) != 0) return false;
    
    const char* eq = strchr(trimmed + key_len, '=');
    if (!eq) return false;
    
    const char* val_start = trim_leading(eq + 1);
    size_t val_len = strlen(val_start);
    while (val_len > 0 && isspace((unsigned char)val_start[val_len - 1])) {
        val_len--;
    }
    
    if (val_len >= max_len) return false;
    strncpy(out_val, val_start, val_len);
    out_val[val_len] = '\0';
    return true;
}

// Розбір числа та перевірка діапазону [1..65535]
static PortResult parse_and_validate_port(const char* val_str) {
    PortResult res = {0, false};
    char* endptr = NULL;
    long val = strtol(val_str, &endptr, 10);
    
    if (endptr == val_str || *endptr != '\0') return res; // Збій парсингу
    if (val < 1 || val > 65535) return res; // Вихід за межі
    
    res.port = (int)val;
    res.is_valid = true;
    return res;
}

// Головна функція парсингу у C
bool parse_server_port_c(const char* config_line, ServerConfig* out_config) {
    char val_buf[64];
    if (!extract_value(config_line, "port", val_buf, sizeof(val_buf))) {
        return false;
    }
    
    PortResult port_res = parse_and_validate_port(val_buf);
    if (!port_res.is_valid) {
        return false;
    }
    
    out_config->port = (unsigned short)port_res.port;
    return true;
}
