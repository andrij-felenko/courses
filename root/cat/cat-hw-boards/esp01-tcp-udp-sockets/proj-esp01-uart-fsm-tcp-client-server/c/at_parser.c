#include "at_parser.h"
#include <string.h>
#include <stdlib.h>

void at_parser_init(at_parser_t *parser, void *user_ctx) {
    if (!parser) return;
    memset(parser, 0, sizeof(at_parser_t));
    parser->state = AT_STATE_LINE_ACCUMULATE;
    parser->user_ctx = user_ctx;
}

void at_parser_set_callbacks(at_parser_t *parser, 
                            at_evt_ok_cb_t on_ok, 
                            at_evt_error_cb_t on_error, 
                            at_evt_ipd_cb_t on_ipd) {
    if (!parser) return;
    parser->on_ok = on_ok;
    parser->on_error = on_error;
    parser->on_ipd_data = on_ipd;
}

static void parse_line_complete(at_parser_t *parser) {
    // Завершуємо рядок нульовим символом
    parser->line_buf[parser->line_idx] = '\0';
    
    // Перевірка станів відповідальних статусів
    if (strcmp(parser->line_buf, "OK") == 0) {
        if (parser->on_ok) {
            parser->on_ok(parser->user_ctx);
        }
    } else if (strcmp(parser->line_buf, "ERROR") == 0) {
        if (parser->on_error) {
            parser->on_error(parser->user_ctx);
        }
    }
    
    // Скидаємо індекс для нового рядка
    parser->line_idx = 0;
}

void at_parser_process_char(at_parser_t *parser, char ch) {
    if (!parser) return;
    
    switch (parser->state) {
        case AT_STATE_LINE_ACCUMULATE:
            if (ch == '\r') {
                // Пропускаємо \r, чекаємо \n
                break;
            }
            if (ch == '\n') {
                if (parser->line_idx > 0) {
                    parse_line_complete(parser);
                }
                break;
            }
            
            // Накопичуємо символ у буфері
            if (parser->line_idx < (AT_PARSER_LINE_BUF_SIZE - 1)) {
                parser->line_buf[parser->line_idx++] = ch;
                parser->line_buf[parser->line_idx] = '\0';
                
                // Детекція префікса "+IPD," вбудованого повідомлення
                if (strncmp(parser->line_buf, "+IPD,", 5) == 0) {
                    parser->ipd_link_id = 0;
                    parser->ipd_expected_len = 0;
                    parser->ipd_received_len = 0;
                    parser->line_idx = 0; // Скидаємо буфер
                    parser->state = AT_STATE_IPD_LINK_ID;
                }
            } else {
                // Захист від переповнення буфера: скидаємо накопичений рядок
                parser->line_idx = 0;
            }
            break;
            
        case AT_STATE_IPD_LINK_ID:
            if (ch >= '0' && ch <= '9') {
                parser->ipd_link_id = (uint8_t)(ch - '0');
            } else if (ch == ',') {
                // Переходимо до зчитання довжини пакета
                parser->state = AT_STATE_IPD_LENGTH;
            } else {
                // Збій формату: повертаємося до накопичення рядків
                parser->line_idx = 0;
                parser->state = AT_STATE_LINE_ACCUMULATE;
            }
            break;
            
        case AT_STATE_IPD_LENGTH:
            if (ch >= '0' && ch <= '9') {
                parser->ipd_expected_len = parser->ipd_expected_len * 10 + (uint16_t)(ch - '0');
            } else if (ch == ':') {
                // Захист від перевищення розміру внутрішнього бінарного буфера
                if (parser->ipd_expected_len > AT_PARSER_IPD_MAX_PAYLOAD) {
                    parser->ipd_expected_len = AT_PARSER_IPD_MAX_PAYLOAD;
                }
                parser->ipd_received_len = 0;
                parser->state = AT_STATE_IPD_PAYLOAD;
            } else {
                // Невалідний символ у полі довжини
                parser->line_idx = 0;
                parser->state = AT_STATE_LINE_ACCUMULATE;
            }
            break;
            
        case AT_STATE_IPD_PAYLOAD:
            if (parser->ipd_received_len < parser->ipd_expected_len) {
                parser->ipd_buf[parser->ipd_received_len++] = (uint8_t)ch;
            }
            
            // Якщо всі бінарні дані отримано
            if (parser->ipd_received_len >= parser->ipd_expected_len) {
                if (parser->on_ipd_data) {
                    parser->on_ipd_data(parser->ipd_link_id, 
                                        parser->ipd_buf, 
                                        parser->ipd_received_len, 
                                        parser->user_ctx);
                }
                // Повертаємося до початкового стану розбору рядків
                parser->line_idx = 0;
                parser->state = AT_STATE_LINE_ACCUMULATE;
            }
            break;
    }
}
