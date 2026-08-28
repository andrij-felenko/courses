/* Приклад реєстрації генератора варіантів через GNU Readline мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <readline/readline.h>
#include <readline/history.h>

static const char *commands[] = {
    "status", "start", "stop", "restart", "reload", "isolate", NULL
};

/* Генератор-ітератор: повертає один варіант за виклик */
static char *command_generator(const char *text, int state) {
    static int list_index, len;
    const char *name;

    if (!state) {
        list_index = 0;
        len = strlen(text);
    }

    while ((name = commands[list_index++])) {
        if (strncmp(name, text, len) == 0) {
            return strdup(name);
        }
    }
    return NULL;
}

/* Хук верхнього рівня для розпізнавання контексту */
static char **custom_completion(const char *text, int start, int end) {
    /* Якщо слово на початку рядка (start == 0) — доповнюємо команди */
    if (start == 0) {
        return rl_completion_matches(text, command_generator);
    }
    /* Інакше дозволяємо Readline виконати стандартне доповнення файлів */
    return NULL;
}

int main(void) {
    rl_attempted_completion_function = custom_completion;
    
    char *input;
    while ((input = readline("my-shell> ")) != NULL) {
        if (*input) {
            add_history(input);
            printf("Виконання: %s\n", input);
        }
        free(input);
    }
    return 0;
}
