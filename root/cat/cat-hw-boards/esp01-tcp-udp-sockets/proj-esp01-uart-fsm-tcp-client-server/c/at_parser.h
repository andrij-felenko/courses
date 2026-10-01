#ifndef AT_PARSER_H
#define AT_PARSER_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define AT_PARSER_LINE_BUF_SIZE 64
#define AT_PARSER_IPD_MAX_PAYLOAD 512

// Стани скінченного автомата розбору асинхронного потоку UART
typedef enum {
    AT_STATE_LINE_ACCUMULATE, // Накопичення текстового рядка до \r\n
    AT_STATE_IPD_LINK_ID,     // Зчитання ідентифікатора сокета (+IPD,<link_id>)
    AT_STATE_IPD_LENGTH,      // Зчитання довжини корисного навантаження (+IPD,...,<len>:)
    AT_STATE_IPD_PAYLOAD      // Прийом бінарного корисного навантаження пакета
} at_parser_state_t;

// Зворотні функції (колбеки) для повідомлення хост-системи про події
typedef void (*at_evt_ok_cb_t)(void *user_ctx);
typedef void (*at_evt_error_cb_t)(void *user_ctx);
typedef void (*at_evt_ipd_cb_t)(uint8_t link_id, const uint8_t *data, uint16_t len, void *user_ctx);

// Контекст скінченного автомата розбору AT-подій
typedef struct {
    at_parser_state_t state;
    
    // Текстовий буфер для рядків команд
    char line_buf[AT_PARSER_LINE_BUF_SIZE];
    uint16_t line_idx;
    
    // Поля розбору префікса +IPD
    uint8_t ipd_link_id;
    uint16_t ipd_expected_len;
    uint16_t ipd_received_len;
    uint8_t ipd_buf[AT_PARSER_IPD_MAX_PAYLOAD];
    
    // Колбеки обробки подій
    at_evt_ok_cb_t on_ok;
    at_evt_error_cb_t on_error;
    at_evt_ipd_cb_t on_ipd_data;
    void *user_ctx;
} at_parser_t;

// Ініціалізація структури парсера
void at_parser_init(at_parser_t *parser, void *user_ctx);

// Реєстрація колбеків подій
void at_parser_set_callbacks(at_parser_t *parser, 
                            at_evt_ok_cb_t on_ok, 
                            at_evt_error_cb_t on_error, 
                            at_evt_ipd_cb_t on_ipd);

// Посимвольне оброблення вхідного байта з UART
void at_parser_process_char(at_parser_t *parser, char ch);

#endif // AT_PARSER_H
