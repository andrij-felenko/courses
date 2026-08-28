#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <ctype.h>
#include <math.h>

#define SCPI_MAX_RESPONSE_BUFFER  512
#define SCPI_ERROR_QUEUE_CAPACITY 8

// Стандартні коди помилок SCPI
typedef enum {
    SCPI_OK                     = 0,
    SCPI_ERR_SYNTAX_ERROR       = -100,
    SCPI_ERR_INVALID_SEPARATOR  = -103,
    SCPI_ERR_UNDEFINED_HEADER   = -113,
    SCPI_ERR_EXECUTION_ERROR    = -200,
    SCPI_ERR_DATA_OUT_OF_RANGE  = -222,
    SCPI_ERR_QUEUE_OVERFLOW     = -350,
    SCPI_ERR_QUERY_INTERRUPTED  = -410,
    SCPI_ERR_QUERY_UNTERMINATED = -420
} scpi_error_code_t;

// Структура запису про помилку
typedef struct {
    int16_t code;
    char    message[40];
} scpi_error_record_t;

// Кільцевий буфер черги помилок FIFO
typedef struct {
    scpi_error_record_t entries[SCPI_ERROR_QUEUE_CAPACITY];
    uint8_t head;
    uint8_t tail;
    uint8_t count;
} scpi_error_queue_t;

// Регістри стану IEEE 488.2
typedef struct {
    uint8_t stb; // Байт стану Status Byte
    uint8_t sre; // Маска дозволу Service Request Enable
    uint8_t esr; // Регістр подій Event Status Register
    uint8_t ese; // Маска дозволу Event Status Enable
} scpi_status_registers_t;

// Попереднє оголошення контексту парсера
typedef struct scpi_engine scpi_engine_t;

// Тип функції-обробника команди
typedef scpi_error_code_t (*scpi_command_handler_t)(scpi_engine_t *engine, const char *args);

// Дескриптор зареєстрованої команди
typedef struct {
    const char            *pattern;  // Шаблон (напр., ":SOURce:VOLTage")
    bool                   is_query; // Прапорець: чи є команда запитом (?)
    scpi_command_handler_t handler;  // Покажчик на функцію дії
} scpi_command_desc_t;

// Головний контекст ядра SCPI
struct scpi_engine {
    const scpi_command_desc_t *commands;
    size_t                     command_count;
    char                       response_buf[SCPI_MAX_RESPONSE_BUFFER];
    size_t                     response_len;
    scpi_error_queue_t         errors;
    scpi_status_registers_t    status;
    char                       current_path[64]; // Збережений контекст підсистеми
    void                      *device_ctx;      // Покажчик на апаратну структуру
};

// Ініціалізація черги помилок
static void scpi_error_queue_init(scpi_error_queue_t *q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
}

// Додавання помилки в чергу FIFO
void scpi_error_push(scpi_engine_t *engine, int16_t code, const char *msg) {
    scpi_error_queue_t *q = &engine->errors;
    
    // Встановлення відповідного біта в регістрі ESR
    if (code <= -100 && code > -200) {
        engine->status.esr |= (1 << 5); // Command Error (CME)
    } else if (code <= -200 && code > -300) {
        engine->status.esr |= (1 << 4); // Execution Error (EXE)
    } else if (code <= -400 && code > -500) {
        engine->status.esr |= (1 << 2); // Query Error (QYE)
    }

    if (q->count >= SCPI_ERROR_QUEUE_CAPACITY) {
        // Переповнення черги
        uint8_t last = (q->head == 0) ? (SCPI_ERROR_QUEUE_CAPACITY - 1) : (q->head - 1);
        q->entries[last].code = SCPI_ERR_QUEUE_OVERFLOW;
        strncpy(q->entries[last].message, "Queue overflow", sizeof(q->entries[last].message) - 1);
        return;
    }

    q->entries[q->head].code = code;
    strncpy(q->entries[q->head].message, msg, sizeof(q->entries[q->head].message) - 1);
    q->entries[q->head].message[sizeof(q->entries[q->head].message) - 1] = '\0';
    
    q->head = (q->head + 1) % SCPI_ERROR_QUEUE_CAPACITY;
    q->count++;

    // Встановлення біта EAV (Error Available) у STB
    engine->status.stb |= (1 << 2);
}

// Вичитування помилки з черги FIFO
static void scpi_error_pop(scpi_engine_t *engine, int16_t *out_code, char *out_msg, size_t max_len) {
    scpi_error_queue_t *q = &engine->errors;
    if (q->count == 0) {
        *out_code = 0;
        strncpy(out_msg, "No error", max_len - 1);
        out_msg[max_len - 1] = '\0';
        engine->status.stb &= ~(1 << 2); // Скидання біта EAV
        return;
    }

    *out_code = q->entries[q->tail].code;
    strncpy(out_msg, q->entries[q->tail].message, max_len - 1);
    out_msg[max_len - 1] = '\0';

    q->tail = (q->tail + 1) % SCPI_ERROR_QUEUE_CAPACITY;
    q->count--;

    if (q->count == 0) {
        engine->status.stb &= ~(1 << 2); // Скидання EAV, якщо черга спорожніла
    }
}

// Запис текстової відповіді у вихідний буфер
void scpi_write_response_str(scpi_engine_t *engine, const char *str) {
    size_t len = strlen(str);
    if (engine->response_len + len < sizeof(engine->response_buf) - 1) {
        memcpy(engine->response_buf + engine->response_len, str, len);
        engine->response_len += len;
        engine->response_buf[engine->response_len] = '\0';
        engine->status.stb |= (1 << 4); // Встановлення біта MAV (Message Available)
    }
}

// Зіставлення одного сегмента мнемоніки за правилом Short/Long Form
static bool scpi_match_segment(const char *token, size_t tok_len, const char *pattern, size_t pat_len) {
    size_t short_len = 0;
    while (short_len < pat_len && isupper((unsigned char)pattern[short_len])) {
        short_len++;
    }
    if (short_len == 0) short_len = pat_len;

    // Перевірка відповідності короткій формі
    if (tok_len == short_len) {
        for (size_t i = 0; i < short_len; ++i) {
            if (toupper((unsigned char)token[i]) != toupper((unsigned char)pattern[i])) {
                return false;
            }
        }
        return true;
    }

    // Перевірка відповідності довгій формі
    if (tok_len == pat_len) {
        for (size_t i = 0; i < pat_len; ++i) {
            if (toupper((unsigned char)token[i]) != toupper((unsigned char)pattern[i])) {
                return false;
            }
        }
        return true;
    }

    return false;
}

// Повне порівняння ієрархічного шляху вузлів
static bool scpi_match_command_path(const char *tok, size_t tok_len, const char *pat) {
    const char *p_curr = pat;
    const char *t_curr = tok;
    size_t t_rem = tok_len;

    while (*p_curr != '\0' && t_rem > 0) {
        if (*p_curr == ':') {
            if (*t_curr != ':') return false;
            p_curr++;
            t_curr++;
            t_rem--;
            continue;
        }

        const char *p_next = strchr(p_curr, ':');
        size_t p_seg_len = (p_next != NULL) ? (size_t)(p_next - p_curr) : strlen(p_curr);

        size_t t_seg_len = 0;
        while (t_seg_len < t_rem && t_curr[t_seg_len] != ':') {
            t_seg_len++;
        }

        if (!scpi_match_segment(t_curr, t_seg_len, p_curr, p_seg_len)) {
            return false;
        }

        p_curr += p_seg_len;
        t_curr += t_seg_len;
        t_rem -= t_seg_len;
    }

    return (*p_curr == '\0' && t_rem == 0);
}

// Швидкісний числовий парсер типу <NRf> із підтримкою суфіксів масштабування
bool scpi_extract_numeric(const char *str, double *out_val) {
    if (!str || !out_val) return false;
    while (isspace((unsigned char)*str)) str++;
    if (*str == '\0') return false;

    char *endptr = NULL;
    double val = strtod(str, &endptr);
    if (endptr == str) return false;

    while (isspace((unsigned char)*endptr)) endptr++;

    if (*endptr != '\0') {
        char sfx[16] = {0};
        size_t idx = 0;
        while (endptr[idx] && !isspace((unsigned char)endptr[idx]) && idx < 15) {
            sfx[idx] = (char)toupper((unsigned char)endptr[idx]);
            idx++;
        }
        sfx[idx] = '\0';

        if (strcmp(sfx, "KV") == 0 || strcmp(sfx, "KHZ") == 0 || strcmp(sfx, "KOHM") == 0) {
            val *= 1e3;
        } else if (strcmp(sfx, "MV") == 0 || strcmp(sfx, "MA") == 0 || strcmp(sfx, "MS") == 0) {
            val *= 1e-3;
        } else if (strcmp(sfx, "UV") == 0 || strcmp(sfx, "UA") == 0 || strcmp(sfx, "US") == 0) {
            val *= 1e-6;
        } else if (strcmp(sfx, "NV") == 0 || strcmp(sfx, "NA") == 0 || strcmp(sfx, "NS") == 0) {
            val *= 1e-9;
        } else if (strcmp(sfx, "MHZ") == 0 || strcmp(sfx, "MOHM") == 0) {
            val *= 1e6;
        }
    }

    *out_val = val;
    return true;
}

// Обробка одного підповідомлення (одна атомарна команда)
static void scpi_dispatch_single(scpi_engine_t *engine, const char *cmd_start, size_t cmd_len) {
    while (cmd_len > 0 && isspace((unsigned char)*cmd_start)) {
        cmd_start++;
        cmd_len--;
    }
    if (cmd_len == 0) return;

    // Відокремлення заголовка від аргументів за першим пробілом
    const char *args = cmd_start;
    size_t header_len = 0;
    while (header_len < cmd_len && !isspace((unsigned char)cmd_start[header_len])) {
        header_len++;
    }

    args = cmd_start + header_len;
    size_t args_len = cmd_len - header_len;
    while (args_len > 0 && isspace((unsigned char)*args)) {
        args++;
        args_len--;
    }

    bool is_query = (header_len > 0 && cmd_start[header_len - 1] == '?');
    size_t match_len = is_query ? (header_len - 1) : header_len;

    // Створення тимчасового нуль-термінованого буфера аргументів на стеку
    char args_buf[128];
    if (args_len >= sizeof(args_buf)) {
        scpi_error_push(engine, SCPI_ERR_SYNTAX_ERROR, "Argument too long");
        return;
    }
    memcpy(args_buf, args, args_len);
    args_buf[args_len] = '\0';

    bool found = false;
    for (size_t i = 0; i < engine->command_count; ++i) {
        const scpi_command_desc_t *cmd = &engine->commands[i];
        if (cmd->is_query != is_query) continue;

        if (scpi_match_command_path(cmd_start, match_len, cmd->pattern)) {
            found = true;
            scpi_error_code_t err = cmd->handler(engine, args_buf);
            if (err != SCPI_OK) {
                scpi_error_push(engine, err, "Execution error");
            }
            break;
        }
    }

    if (!found) {
        scpi_error_push(engine, SCPI_ERR_UNDEFINED_HEADER, "Undefined header");
    }
}

// Головна точка входу: розбір вхідного рядка з урахуванням розділювача ';'
void scpi_engine_execute(scpi_engine_t *engine, const char *raw_line) {
    if (!engine || !raw_line) return;

    engine->response_len = 0;
    engine->response_buf[0] = '\0';

    const char *curr = raw_line;
    while (*curr != '\0' && *curr != '\n' && *curr != '\r') {
        const char *semicolon = strchr(curr, ';');
        size_t chunk_len = (semicolon != NULL) ? (size_t)(semicolon - curr) : strlen(curr);

        // Якщо рядок закінчується переведенням рядка, обрізаємо його
        const char *nl = strpbrk(curr, "\r\n");
        if (nl != NULL && (semicolon == NULL || nl < semicolon)) {
            chunk_len = (size_t)(nl - curr);
        }

        scpi_dispatch_single(engine, curr, chunk_len);

        if (semicolon != NULL && (nl == NULL || semicolon < nl)) {
            curr = semicolon + 1;
        } else {
            break;
        }
    }

    // Якщо сформовано відповідь, додаємо кінцевий символ '\n'
    if (engine->response_len > 0) {
        scpi_write_response_str(engine, "\n");
    }
}

// Прикладний контекст контролера навантаження / джерела
typedef struct {
    double set_voltage;
    double set_current;
    bool   output_state;
} lab_power_supply_t;

// Обробники стандартних та вимірювальних команд
static scpi_error_code_t cb_idn_q(scpi_engine_t *eng, const char *args) {
    (void)args;
    scpi_write_response_str(eng, "OpenHardware,PSU-Core,SN20260828,v1.2.0");
    return SCPI_OK;
}

static scpi_error_code_t cb_rst(scpi_engine_t *eng, const char *args) {
    (void)args;
    lab_power_supply_t *psu = (lab_power_supply_t*)eng->device_ctx;
    psu->set_voltage = 0.0;
    psu->set_current = 0.5;
    psu->output_state = false;
    return SCPI_OK;
}

static scpi_error_code_t cb_syst_err_q(scpi_engine_t *eng, const char *args) {
    (void)args;
    int16_t code = 0;
    char msg[48] = {0};
    scpi_error_pop(eng, &code, msg, sizeof(msg));
    char buf[64];
    snprintf(buf, sizeof(buf), "%d,\"%s\"", code, msg);
    scpi_write_response_str(eng, buf);
    return SCPI_OK;
}

static scpi_error_code_t cb_sour_volt(scpi_engine_t *eng, const char *args) {
    lab_power_supply_t *psu = (lab_power_supply_t*)eng->device_ctx;
    double val = 0.0;
    if (!scpi_extract_numeric(args, &val)) {
        return SCPI_ERR_SYNTAX_ERROR;
    }
    if (val < 0.0 || val > 30.0) {
        return SCPI_ERR_DATA_OUT_OF_RANGE;
    }
    psu->set_voltage = val;
    return SCPI_OK;
}

static scpi_error_code_t cb_sour_volt_q(scpi_engine_t *eng, const char *args) {
    (void)args;
    lab_power_supply_t *psu = (lab_power_supply_t*)eng->device_ctx;
    char buf[32];
    snprintf(buf, sizeof(buf), "%.4f", psu->set_voltage);
    scpi_write_response_str(eng, buf);
    return SCPI_OK;
}

static scpi_error_code_t cb_outp_stat(scpi_engine_t *eng, const char *args) {
    lab_power_supply_t *psu = (lab_power_supply_t*)eng->device_ctx;
    if (strncasecmp(args, "ON", 2) == 0 || strcmp(args, "1") == 0) {
        psu->output_state = true;
    } else if (strncasecmp(args, "OFF", 3) == 0 || strcmp(args, "0") == 0) {
        psu->output_state = false;
    } else {
        return SCPI_ERR_SYNTAX_ERROR;
    }
    return SCPI_OK;
}

static scpi_error_code_t cb_outp_stat_q(scpi_engine_t *eng, const char *args) {
    (void)args;
    lab_power_supply_t *psu = (lab_power_supply_t*)eng->device_ctx;
    scpi_write_response_str(eng, psu->output_state ? "1" : "0");
    return SCPI_OK;
}

// Статична таблиця командного простору
static const scpi_command_desc_t g_system_command_table[] = {
    {"*IDN",                 true,  cb_idn_q},
    {"*RST",                 false, cb_rst},
    {":SYSTem:ERRor",        true,  cb_syst_err_q},
    {":SOURce:VOLTage",      false, cb_sour_volt},
    {":SOURce:VOLTage",      true,  cb_sour_volt_q},
    {":OUTPut:STATe",        false, cb_outp_stat},
    {":OUTPut:STATe",        true,  cb_outp_stat_q}
};

int main(void) {
    lab_power_supply_t psu_hardware = {0.0, 0.5, false};
    scpi_engine_t scpi;
    memset(&scpi, 0, sizeof(scpi));
    scpi.commands = g_system_command_table;
    scpi.command_count = sizeof(g_system_command_table) / sizeof(g_system_command_table[0]);
    scpi.device_ctx = &psu_hardware;
    scpi_error_queue_init(&scpi.errors);

    printf("=== Запуск тесту вбудованого ядра SCPI (C99) ===\n");

    const char *test_sequence[] = {
        "*IDN?",
        ":SOUR:VOLT 15.75V",
        ":SOURce:VOLTage?",
        ":OUTP:STAT ON",
        ":OUTP:STAT?",
        ":SOUR:VOLT 60.0V", // Помилка -222: вихід за межі діапазону
        ":BAD:PATH:CMD?",   // Помилка -113: невідомий заголовок
        ":SYST:ERR?",
        ":SYST:ERR?",
        ":SYST:ERR?"
    };

    for (size_t i = 0; i < sizeof(test_sequence)/sizeof(test_sequence[0]); ++i) {
        printf(">> %s\n", test_sequence[i]);
        scpi_engine_execute(&scpi, test_sequence[i]);
        if (scpi.response_len > 0) {
            printf("<< %s", scpi.response_buf);
        }
    }

    return 0;
}
