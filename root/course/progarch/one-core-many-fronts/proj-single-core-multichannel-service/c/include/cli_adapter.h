#ifndef CLI_ADAPTER_H
#define CLI_ADAPTER_H

#include "inbound_port.h"

/**
 * @file cli_adapter.h
 * @brief Драйвуючий адаптер командного рядка (CLI Driving Adapter).
 *
 * Транслює параметри командного рядка (--room, --temp, --token) у виклик
 * вхідного порту та відображає доменні результати у системні коди завершення.
 */

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Коди завершення процесу для консольного інтерфейсу.
 */
typedef enum {
    CLI_EXIT_SUCCESS = 0,        /**< Команду успішно виконано прикладним ядром */
    CLI_EXIT_INVALID_SYNTAX = 1, /**< Синтаксична помилка або відсутність обов'язкових прапорців */
    CLI_EXIT_INVALID_ARG = 2,    /**< Доменна помилка валідації аргументів ядром */
    CLI_EXIT_UNAUTHORIZED = 3,   /**< Помилка авторизації доступу */
    CLI_EXIT_OUT_OF_RANGE = 4,   /**< Порушення бізнес-правила діапазону температур */
    CLI_EXIT_INTERNAL_ERROR = 5  /**< Системна або внутрішня помилка ядра */
} cli_exit_code_t;

/**
 * @brief Запускає обробку аргументів командного рядка через вхідний порт.
 *
 * @param port Покажчик на контракт вхідного порту ядра.
 * @param argc Кількість аргументів командного рядка.
 * @param argv Масив рядків аргументів.
 * @return int Код завершення процесу (cli_exit_code_t).
 */
int cli_adapter_run(inbound_port_t *port, int argc, char **argv);

#ifdef __cplusplus
}
#endif

#endif /* CLI_ADAPTER_H */
