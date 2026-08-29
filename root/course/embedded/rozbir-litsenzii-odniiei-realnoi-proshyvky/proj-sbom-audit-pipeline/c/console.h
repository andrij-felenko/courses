/* console.h — мінімальна службова консоль поверх UART або USB CDC.
 *
 * Транспорт консоль не знає: застосунок віддає їй функцію виводу, а байти
 * заносить по одному з переривання чи з задачі-читача. Так той самий модуль
 * працює і на голому UART, і на віртуальному COM-порту USB.
 */
#ifndef CONSOLE_H
#define CONSOLE_H

#include <stddef.h>

/* Довжина рядка команди. Більше в службовій консолі не треба, а буфер лежить
 * у .bss назавжди, тому кожен зайвий байт тут — це байт SRAM. */
#define CLI_LINE_MAX 96

typedef void (*cli_out_fn)(const char *text);

typedef enum {
    CLI_OK = 0,
    CLI_ERR_EMPTY,       /* порожній рядок — мовчки ігноруємо        */
    CLI_ERR_UNKNOWN,     /* невідома команда                        */
    CLI_ERR_ARGS,        /* аргумент є, але не той                  */
    CLI_ERR_OVERFLOW     /* рядок довший за CLI_LINE_MAX            */
} cli_status_t;

typedef cli_status_t (*cli_handler_fn)(const char *args, cli_out_fn out);

typedef struct {
    const char *name;
    const char *help;
    cli_handler_fn run;
} cli_command_t;

/* Прив'язати консоль до виводу; друкує банер і запрошення. */
void cli_console_init(cli_out_fn out);

/* Один прийнятий байт. Викликається з задачі-читача, не з ISR:
 * усередині є друк, а він блокує. */
void cli_console_feed(char c);

/* Виконати готовий рядок. Рядок модифікується на місці (розрізаємо на
 * команду й аргументи), тому константи сюди передавати не можна. */
cli_status_t cli_console_execute(char *line);

const char *cli_status_text(cli_status_t status);

#endif /* CONSOLE_H */
