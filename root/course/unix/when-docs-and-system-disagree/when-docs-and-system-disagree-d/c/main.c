/* Діагностичний аудит середовища та розв'язання команд на POSIX C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <limits.h>
#include <sys/stat.h>
#include <locale.h>

void inspect_locale(void)
{
    const char *loc = setlocale(LC_ALL, "");
    printf("[1] Системна локаль: %s\n", loc ? loc : "не визначено");
    const char *collate = getenv("LC_COLLATE");
    printf("    LC_COLLATE: %s\n", collate ? collate : "(за замовчуванням)");
}

void resolve_command(const char *cmd_name)
{
    printf("[2] Дослідження команди: %s\n", cmd_name);
    
    /* Якщо вказано прямий шлях */
    if (strchr(cmd_name, '/')) {
        char resolved[PATH_MAX];
        if (realpath(cmd_name, resolved)) {
            printf("    Прямий шлях знайдено: %s\n", resolved);
        } else {
            perror("    Помилка realpath");
        }
        return;
    }

    const char *path_env = getenv("PATH");
    if (!path_env) {
        fprintf(stderr, "    Змінна PATH відсутня!\n");
        return;
    }

    char *path_copy = strdup(path_env);
    if (!path_copy) {
        perror("strdup");
        return;
    }

    char *dir = strtok(path_copy, ":");
    int found_count = 0;

    while (dir != NULL) {
        char full_path[PATH_MAX];
        snprintf(full_path, sizeof(full_path), "%s/%s", dir, cmd_name);

        if (access(full_path, X_OK) == 0) {
            char real_bin[PATH_MAX];
            if (realpath(full_path, real_bin)) {
                printf("    Знайдено у PATH [%d]: %s -> %s\n", ++found_count, full_path, real_bin);
            } else {
                printf("    Знайдено у PATH [%d]: %s\n", ++found_count, full_path);
            }
        }
        dir = strtok(NULL, ":");
    }

    if (found_count == 0) {
        printf("    Команду '%s' не знайдено у жодному каталозі PATH.\n", cmd_name);
    }

    free(path_copy);
}

int main(int argc, char *argv[])
{
    const char *target = (argc > 1) ? argv[1] : "grep";
    printf("=== Системний аудит середовища виконання ===\n");
    inspect_locale();
    resolve_command(target);
    return 0;
}
