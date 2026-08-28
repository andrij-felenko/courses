#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <stdint.h>

/* ── 1. Єдине джерело правди (Майстер-таблиця) ── */
#define TELEMETRY_COMMAND_TABLE(X) \
    X(CMD_PING,       0x01, "ping",       false) \
    X(CMD_GET_STATUS, 0x02, "get_status", false) \
    X(CMD_SET_CONFIG, 0x03, "set_config", true)  \
    X(CMD_REBOOT,     0xFF, "reboot",     true)

/* ── 2. Генерація перелічення (Enum) ── */
typedef enum {
#define X(name, code, str, auth) name = code,
    TELEMETRY_COMMAND_TABLE(X)
#undef X
    CMD_INVALID = 0x00
} TelemetryCmd;

/* ── 3. Генерація функції Enum -> String ── */
static const char* telemetry_cmd_to_str(TelemetryCmd cmd) {
    switch (cmd) {
#define X(name, code, str, auth) case name: return str;
        TELEMETRY_COMMAND_TABLE(X)
#undef X
        default: return "UNKNOWN";
    }
}

/* ── 4. Генерація перевірки вимоги автентифікації ── */
static bool telemetry_cmd_requires_auth(TelemetryCmd cmd) {
    switch (cmd) {
#define X(name, code, str, auth) case name: return auth;
        TELEMETRY_COMMAND_TABLE(X)
#undef X
        default: return true; /* Безпечний дефолт */
    }
}

/* ── 5. Генерація функції String -> Enum (Парсер) ── */
static TelemetryCmd telemetry_str_to_cmd(const char* str) {
    if (!str) return CMD_INVALID;

#define X(name, code, str_val, auth) \
    if (strcmp(str, str_val) == 0) return name;
    TELEMETRY_COMMAND_TABLE(X)
#undef X

    return CMD_INVALID;
}

int main(void) {
    const char* input_command = "set_config";
    TelemetryCmd cmd = telemetry_str_to_cmd(input_command);

    if (cmd != CMD_INVALID) {
        printf("Знайдено команду: %s (код: 0x%02X)\n",
               telemetry_cmd_to_str(cmd), (unsigned int)cmd);
        printf("Потрібна автентифікація: %s\n",
               telemetry_cmd_requires_auth(cmd) ? "ТАК" : "НІ");
    } else {
        printf("Команду «%s» не розпізнано!\n", input_command);
    }
    return 0;
}
