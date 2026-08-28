/* repl_sync.c — Інтерактивний REPL із автодоповненням на C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <readline/readline.h>
#include <readline/history.h>

static const char *const COMMANDS[] = {
    "SELECT", "INSERT", "UPDATE", "DELETE",
    "CREATE", "DROP", "SHOW", "HELP", "EXIT", NULL
};

static const char *const TABLES[] = {
    "users", "accounts", "orders", "audit_log", NULL
};

/* Генератор варіантів команд для першого слова */
static char *command_generator(const char *text, int state) {
    static int list_index, len;
    const char *name;

    if (!state) {
        list_index = 0;
        len = (int)strlen(text);
    }

    while ((name = COMMANDS[list_index++]) != NULL) {
        if (strncasecmp(name, text, len) == 0) {
            return strdup(name);
        }
    }
    return NULL;
}

/* Генератор варіантів імен таблиць для наступних аргументів */
static char *table_generator(const char *text, int state) {
    static int list_index, len;
    const char *name;

    if (!state) {
        list_index = 0;
        len = (int)strlen(text);
    }

    while ((name = TABLES[list_index++]) != NULL) {
        if (strncasecmp(name, text, len) == 0) {
            return strdup(name);
        }
    }
    return NULL;
}

/* Диспетчер автодоповнення: перевіряє позицію слова в буфері */
static char **custom_completion(const char *text, int start, int end) {
    (void)end;
    /* Вимикаємо стандартне доповнення імен файлів при відсутності збігів */
    rl_attempted_completion_over = 1;

    /* Якщо слово на початку рядка — доповнюємо команду */
    if (start == 0) {
        return rl_completion_matches(text, command_generator);
    }

    /* Якщо перед словом уже введено команду — доповнюємо імена таблиць */
    return rl_completion_matches(text, table_generator);
}

/* Обробник сигналу SIGINT (Ctrl+C): скидає поточний рядок без аварійного виходу */
static void handle_sigint(int sig) {
    (void)sig;
    write(1, "\n", 1);
    rl_on_new_line();
    rl_replace_line("", 0);
    rl_redisplay();
}

int main(void) {
    const char *hist_file = ".repl_history";
    struct sigaction sa;
    char *line;

    /* Реєстрація безпечного обробника сигналів переривання */
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_sigint;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGINT, &sa, NULL);

    /* Ініціалізація диспетчера доповнень та імені утиліти для inputrc */
    rl_attempted_completion_function = custom_completion;
    rl_readline_name = "MiniDB";

    /* Завантаження історії з диска */
    read_history(hist_file);

    printf("MiniDB Console (GNU Readline). Введіть HELP або EXIT.\n");

    while ((line = readline("minidb> ")) != NULL) {
        /* Пропуск порожніх рядків без збереження в історію */
        if (*line == '\0') {
            free(line);
            continue;
        }

        /* Додавання змістовного рядка в історію */
        add_history(line);

        if (strcasecmp(line, "EXIT") == 0 || strcasecmp(line, "QUIT") == 0) {
            free(line);
            break;
        }

        if (strcasecmp(line, "HELP") == 0) {
            printf("Доступні команди: SELECT, INSERT, UPDATE, DELETE, SHOW, HELP, EXIT\n");
        } else {
            printf("[Виконано]: %s\n", line);
        }

        free(line);
    }

    /* Персистентне збереження та обрізка файлу історії до 100 записів */
    write_history(hist_file);
    history_truncate_file(hist_file, 100);
    printf("\nСеанс завершено.\n");
    return 0;
}
