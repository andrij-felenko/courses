#include <string.h>
#include <stdbool.h>
#include <stdio.h>

typedef struct {
    int signal_strength;
    int bit_error_rate;
} CsqResponse;

bool parse_csq_c(char* response, CsqResponse* out) {
    // Вхід: "+CSQ: 24,99\r\nOK"
    // Небезпечно: strtok модифікує вхідний рядок, записуючи '\0'
    char* prefix = strstr(response, "+CSQ: ");
    if (!prefix) return false;

    char* token = strtok(prefix + 6, ",\r\n");
    if (!token) return false;
    out->signal_strength = 0;
    while (*token >= '0' && *token <= '9') {
        out->signal_strength = out->signal_strength * 10 + (*token - '0');
        token++;
    }

    token = strtok(NULL, ",\r\n");
    if (!token) return false;
    out->bit_error_rate = 0;
    while (*token >= '0' && *token <= '9') {
        out->bit_error_rate = out->bit_error_rate * 10 + (*token - '0');
        token++;
    }
    return true;
}
