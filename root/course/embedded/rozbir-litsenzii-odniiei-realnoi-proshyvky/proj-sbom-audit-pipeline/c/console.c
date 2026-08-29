/* console.c — збирання рядка з потоку байтів і диспетчер команд. */
#include "console.h"
#include "cli_license.h"

#include <stddef.h>
#include <string.h>

#define CLI_PROMPT "fw> "

static cli_out_fn s_out;
static char s_line[CLI_LINE_MAX];
static size_t s_len;
static int s_overflow;          /* рядок переповнено — дочікуємо кінця й лаємось */

static cli_status_t cmd_help(const char *args, cli_out_fn out);

/* Таблиця команд лежить тут, а не в модулі ліцензій: команд із часом більшає,
 * а help має бачити їх усі. */
static const cli_command_t k_commands[] = {
    { "license", "склад прошивки й ліцензії; license <назва> — подробиці", cli_cmd_license },
    { "about",   "виріб, версія, хеш паспорта SBOM",                        cli_cmd_about   },
    { "help",    "цей перелік",                                             cmd_help        },
};

static const size_t k_command_count = sizeof(k_commands) / sizeof(k_commands[0]);

const char *cli_status_text(cli_status_t status)
{
    switch (status) {
    case CLI_OK:           return "ok";
    case CLI_ERR_EMPTY:    return "порожній рядок";
    case CLI_ERR_UNKNOWN:  return "невідома команда, спробуйте help";
    case CLI_ERR_ARGS:     return "хибний аргумент";
    case CLI_ERR_OVERFLOW: return "рядок задовгий, його відкинуто";
    default:               return "невідома помилка";
    }
}

static cli_status_t cmd_help(const char *args, cli_out_fn out)
{
    (void)args;
    out("\r\nДоступні команди:\r\n");
    for (size_t i = 0; i < k_command_count; ++i) {
        out("  ");
        out(k_commands[i].name);
        out("\t— ");
        out(k_commands[i].help);
        out("\r\n");
    }
    return CLI_OK;
}

void cli_console_init(cli_out_fn out)
{
    s_out = out;
    s_len = 0;
    s_overflow = 0;
    if (s_out == NULL) {
        return;         /* без виводу консоль просто мовчить, але не падає */
    }
    s_out("\r\n");
    s_out("Службова консоль прошивки. help — перелік команд.\r\n");
    s_out(CLI_PROMPT);
}

cli_status_t cli_console_execute(char *line)
{
    if (line == NULL || s_out == NULL) {
        return CLI_ERR_EMPTY;
    }

    char *name = line;
    while (*name == ' ' || *name == '\t') {
        ++name;
    }
    if (*name == '\0') {
        return CLI_ERR_EMPTY;
    }

    /* Розрізаємо на ім'я команди й решту рядка. */
    char *args = name;
    while (*args != '\0' && *args != ' ' && *args != '\t') {
        ++args;
    }
    if (*args != '\0') {
        *args = '\0';
        ++args;
        while (*args == ' ' || *args == '\t') {
            ++args;
        }
    }

    for (size_t i = 0; i < k_command_count; ++i) {
        if (strcmp(name, k_commands[i].name) == 0) {
            return k_commands[i].run(args, s_out);
        }
    }
    return CLI_ERR_UNKNOWN;
}

void cli_console_feed(char c)
{
    if (s_out == NULL) {
        return;
    }

    if (c == '\r' || c == '\n') {
        s_out("\r\n");
        cli_status_t status;

        if (s_overflow) {
            status = CLI_ERR_OVERFLOW;
        } else {
            s_line[s_len] = '\0';
            status = cli_console_execute(s_line);
        }

        if (status != CLI_OK && status != CLI_ERR_EMPTY) {
            s_out("помилка: ");
            s_out(cli_status_text(status));
            s_out("\r\n");
        }
        s_len = 0;
        s_overflow = 0;
        s_out(CLI_PROMPT);
        return;
    }

    /* Забій: стираємо символ і на екрані теж. */
    if (c == '\b' || c == 0x7F) {
        if (s_len > 0 && !s_overflow) {
            --s_len;
            s_out("\b \b");
        }
        return;
    }

    /* Ctrl-C — кинути набране. */
    if (c == 0x03) {
        s_len = 0;
        s_overflow = 0;
        s_out("^C\r\n");
        s_out(CLI_PROMPT);
        return;
    }

    /* Керівні байти в буфер не пускаємо: термінали шлють escape-послідовності
     * стрілок, і без фільтра вони пролізли б у назву команди. */
    if ((unsigned char)c < 0x20 || (unsigned char)c == 0x1B) {
        return;
    }

    if (s_len + 1 >= sizeof(s_line)) {
        s_overflow = 1;     /* решту рядка дочитуємо й викидаємо цілком */
        return;
    }
    s_line[s_len++] = c;
    char echo[2] = { c, '\0' };
    s_out(echo);
}
