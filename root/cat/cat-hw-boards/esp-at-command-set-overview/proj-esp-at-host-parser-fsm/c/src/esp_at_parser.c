#include "esp_at_parser.h"
#include <string.h>

/**
 * @file esp_at_parser.c
 * @brief Реалізація FSM-парсера AT-відповідей з таблицею станів та обробкою таймаутів.
 */

/* Приватні прототипи функцій-обробників станів FSM */
static void handle_state_idle(esp_at_parser_t *parser, uint8_t byte);
static void handle_state_search_cr(esp_at_parser_t *parser, uint8_t byte);
static void handle_state_search_lf(esp_at_parser_t *parser, uint8_t byte);
static void handle_state_processing_line(esp_at_parser_t *parser, uint8_t byte);
static void handle_state_timeout_recovery(esp_at_parser_t *parser, uint8_t byte);

/* Приватна допоміжна функція аналізу завершеного рядка */
static void parse_completed_line(esp_at_parser_t *parser);

/**
 * @brief Таблиця станів FSM з вказівниками на відповідні функції-обробники.
 */
static const esp_at_state_handler_t state_table[ESP_AT_STATE_MAX] = {
    [ESP_AT_STATE_IDLE]             = handle_state_idle,
    [ESP_AT_STATE_SEARCH_CR]        = handle_state_search_cr,
    [ESP_AT_STATE_SEARCH_LF]        = handle_state_search_lf,
    [ESP_AT_STATE_PROCESSING_LINE]  = handle_state_processing_line,
    [ESP_AT_STATE_TIMEOUT_RECOVERY] = handle_state_timeout_recovery
};

void esp_at_parser_init(esp_at_parser_t *parser, ring_buffer_t *rx_buf, uint32_t (*get_time_ms)(void)) {
    if (parser == NULL) {
        return;
    }
    memset(parser, 0, sizeof(esp_at_parser_t));
    parser->rx_buf = rx_buf;
    parser->get_system_time_ms = get_time_ms;
    parser->state = ESP_AT_STATE_IDLE;
    parser->line_len = 0;
    parser->is_waiting_response = false;
    parser->timeout_period_ms = 0;
}

void esp_at_parser_set_user_data(esp_at_parser_t *parser, void *user_data) {
    if (parser != NULL) {
        parser->user_data = user_data;
    }
}

void esp_at_parser_register_callbacks(esp_at_parser_t *parser,
                                       esp_at_status_cb_t on_ok,
                                       esp_at_status_cb_t on_error,
                                       esp_at_status_cb_t on_busy,
                                       esp_at_status_cb_t on_timeout) {
    if (parser == NULL) {
        return;
    }
    parser->on_ok = on_ok;
    parser->on_error = on_error;
    parser->on_busy = on_busy;
    parser->on_timeout = on_timeout;
}

void esp_at_parser_register_line_callback(esp_at_parser_t *parser, esp_at_line_cb_t on_line) {
    if (parser != NULL) {
        parser->on_line = on_line;
    }
}

void esp_at_parser_start_command(esp_at_parser_t *parser, uint32_t timeout_ms) {
    if (parser == NULL) {
        return;
    }
    parser->line_len = 0;
    parser->line_buf[0] = '\0';
    parser->state = ESP_AT_STATE_IDLE;
    parser->timeout_period_ms = timeout_ms;
    parser->is_waiting_response = true;

    if (parser->get_system_time_ms != NULL) {
        uint32_t now = parser->get_system_time_ms();
        parser->command_start_time_ms = now;
        parser->last_char_time_ms = now;
    }
}

void esp_at_parser_process_byte(esp_at_parser_t *parser, uint8_t byte) {
    if (parser == NULL) {
        return;
    }

    if (parser->get_system_time_ms != NULL) {
        parser->last_char_time_ms = parser->get_system_time_ms();
    }

    /* Викликаємо обробник поточного стану з таблиці станів */
    if (parser->state < ESP_AT_STATE_MAX && state_table[parser->state] != NULL) {
        state_table[parser->state](parser, byte);
    } else {
        /* При некоректному стані виконуємо відновлення */
        esp_at_parser_reset(parser);
    }
}

void esp_at_parser_process_buffer(esp_at_parser_t *parser) {
    if (parser == NULL || parser->rx_buf == NULL) {
        return;
    }

    uint8_t byte;
    /* Посимвольне вилучення байтів з кільцевого буфера без блокування */
    while (ring_buffer_pop(parser->rx_buf, &byte)) {
        esp_at_parser_process_byte(parser, byte);
    }
}

void esp_at_parser_check_timeout(esp_at_parser_t *parser) {
    if (parser == NULL || !parser->is_waiting_response || parser->get_system_time_ms == NULL) {
        return;
    }

    uint32_t current_time = parser->get_system_time_ms();
    uint32_t elapsed = current_time - parser->command_start_time_ms;

    if (elapsed >= parser->timeout_period_ms) {
        /* Фіксуємо виникнення таймауту очікування */
        parser->state = ESP_AT_STATE_TIMEOUT_RECOVERY;
        parser->is_waiting_response = false;

        if (parser->on_timeout != NULL) {
            parser->on_timeout(ESP_AT_STATUS_TIMEOUT, parser->user_data);
        }

        esp_at_parser_reset(parser);
    }
}

void esp_at_parser_reset(esp_at_parser_t *parser) {
    if (parser == NULL) {
        return;
    }
    parser->state = ESP_AT_STATE_IDLE;
    parser->line_len = 0;
    parser->line_buf[0] = '\0';
}

esp_at_state_t esp_at_parser_get_state(const esp_at_parser_t *parser) {
    if (parser == NULL) {
        return ESP_AT_STATE_IDLE;
    }
    return parser->state;
}

bool esp_at_parser_is_busy(const esp_at_parser_t *parser) {
    if (parser == NULL) {
        return false;
    }
    return parser->is_waiting_response;
}

/* --- Обробники станів FSM --- */

static void handle_state_idle(esp_at_parser_t *parser, uint8_t byte) {
    /* Пропускаємо початкові символи переводу рядка \r та \n у стані IDLE */
    if (byte == '\r' || byte == '\n') {
        return;
    }

    /* Накопичуємо перший символ та переходимо у стан пошуку CR (\r) */
    parser->line_len = 0;
    parser->line_buf[parser->line_len++] = (char)byte;
    parser->line_buf[parser->line_len] = '\0';
    parser->state = ESP_AT_STATE_SEARCH_CR;
}

static void handle_state_search_cr(esp_at_parser_t *parser, uint8_t byte) {
    if (byte == '\r') {
        /* Знайшли термінатор \r, переходимо до очікування \n */
        parser->state = ESP_AT_STATE_SEARCH_LF;
    } else if (byte == '\n') {
        /* Деякі пристрої надсилають лише \n - обробляємо як завершення рядка */
        parser->line_buf[parser->line_len] = '\0';
        parser->state = ESP_AT_STATE_PROCESSING_LINE;
        parse_completed_line(parser);
    } else {
        /* Додаємо символ до буфера рядка із запобіганням переповненню */
        if (parser->line_len < (ESP_AT_LINE_BUF_SIZE - 1)) {
            parser->line_buf[parser->line_len++] = (char)byte;
            parser->line_buf[parser->line_len] = '\0';
        } else {
            /* При переповненні рядка обнуляємо буфер для захисту пам'яті */
            esp_at_parser_reset(parser);
        }
    }
}

static void handle_state_search_lf(esp_at_parser_t *parser, uint8_t byte) {
    if (byte == '\n') {
        /* Повний рядок розпізнано (\r\n) */
        parser->line_buf[parser->line_len] = '\0';
        parser->state = ESP_AT_STATE_PROCESSING_LINE;
        parse_completed_line(parser);
    } else {
        /* Якщо після \r іде не \n, додаємо \r та новий символ */
        if (parser->line_len < (ESP_AT_LINE_BUF_SIZE - 2)) {
            parser->line_buf[parser->line_len++] = '\r';
            parser->line_buf[parser->line_len++] = (char)byte;
            parser->line_buf[parser->line_len] = '\0';
            parser->state = ESP_AT_STATE_SEARCH_CR;
        } else {
            esp_at_parser_reset(parser);
        }
    }
}

static void handle_state_processing_line(esp_at_parser_t *parser, uint8_t byte) {
    /* Під час аналізу поточний символ не вимагається, переходимо до IDLE */
    (void)byte;
    parser->state = ESP_AT_STATE_IDLE;
}

static void handle_state_timeout_recovery(esp_at_parser_t *parser, uint8_t byte) {
    (void)byte;
    esp_at_parser_reset(parser);
}

/* --- Приватна функція розбору виділеного рядка --- */

static void parse_completed_line(esp_at_parser_t *parser) {
    if (parser->line_len == 0) {
        parser->state = ESP_AT_STATE_IDLE;
        return;
    }

    /* Сповіщаємо про зчитаний рядок через line callback, якщо він зареєстрований */
    if (parser->on_line != NULL) {
        parser->on_line(parser->line_buf, parser->line_len, parser->user_data);
    }

    /* Перевірка статусних відповідей ESP-AT */
    if (strcmp(parser->line_buf, "OK") == 0) {
        parser->is_waiting_response = false;
        if (parser->on_ok != NULL) {
            parser->on_ok(ESP_AT_STATUS_OK, parser->user_data);
        }
    } else if (strcmp(parser->line_buf, "ERROR") == 0 || strcmp(parser->line_buf, "FAIL") == 0) {
        parser->is_waiting_response = false;
        if (parser->on_error != NULL) {
            parser->on_error(ESP_AT_STATUS_ERROR, parser->user_data);
        }
    } else if (strncmp(parser->line_buf, "busy", 4) == 0 || strncmp(parser->line_buf, "BUSY", 4) == 0) {
        if (parser->on_busy != NULL) {
            parser->on_busy(ESP_AT_STATUS_BUSY, parser->user_data);
        }
    }

    /* Скидаємо стан для розбору наступного рядка */
    parser->state = ESP_AT_STATE_IDLE;
    parser->line_len = 0;
    parser->line_buf[0] = '\0';
}
