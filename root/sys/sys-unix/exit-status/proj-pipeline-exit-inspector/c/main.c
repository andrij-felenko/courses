#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#define MAX_COMMANDS 8

typedef struct {
    char *argv[16];
} Command;

typedef struct {
    int pid;
    int raw_wstatus;
    int exit_code;
} ProcessResult;

void execute_pipeline(Command cmds[], int cmd_count, int pipefail_enabled) {
    int pipes[MAX_COMMANDS - 1][2];
    ProcessResult results[MAX_COMMANDS];

    // 1. Створення масиву анонімних каналів pipe
    for (int i = 0; i < cmd_count - 1; i++) {
        if (pipe(pipes[i]) < 0) {
            perror("Системна помилка pipe");
            exit(1);
        }
    }

    // 2. Послідовний запуск дочірніх процесів через fork/exec
    for (int i = 0; i < cmd_count; i++) {
        pid_t pid = fork();
        if (pid < 0) {
            perror("Системна помилка fork");
            exit(1);
        }

        if (pid == 0) {
            // Дочірній процес: перенаправлення стандартних потоків вводу-виводу
            if (i > 0) {
                // Перенаправлення STDIN на читання з попереднього каналу
                if (dup2(pipes[i - 1][0], STDIN_FILENO) < 0) {
                    perror("dup2 stdin");
                    _exit(1);
                }
            }
            if (i < cmd_count - 1) {
                // Перенаправлення STDOUT на запис у поточний канал
                if (dup2(pipes[i][1], STDOUT_FILENO) < 0) {
                    perror("dup2 stdout");
                    _exit(1);
                }
            }

            // Закриття всіх копій файлових дескрипторів каналів у дочірньому процесі
            for (int j = 0; j < cmd_count - 1; j++) {
                close(pipes[j][0]);
                close(pipes[j][1]);
            }

            // Заміна образу процесу на цільову програму
            execvp(cmds[i].argv[0], cmds[i].argv);
            perror("Системна помилка execvp");
            _exit(127); // Код виходу POSIX: команду не знайдено
        }

        results[i].pid = pid;
    }

    // Батьківський процес повинен закрити всі копії дескрипторів каналів,
    // інакше дочірні процеси чекатимуть на EOF вічно!
    for (int i = 0; i < cmd_count - 1; i++) {
        close(pipes[i][0]);
        close(pipes[i][1]);
    }

    // 3. Збір та розпакування статусів завершення всіх елементів
    for (int i = 0; i < cmd_count; i++) {
        int wstatus;
        waitpid(results[i].pid, &wstatus, 0);
        results[i].raw_wstatus = wstatus;

        if (WIFEXITED(wstatus)) {
            results[i].exit_code = WEXITSTATUS(wstatus);
        } else if (WIFSIGNALED(wstatus)) {
            results[i].exit_code = 128 + WTERMSIG(wstatus);
        } else {
            results[i].exit_code = 1;
        }
    }

    // 4. Форматований вивід масиву PIPESTATUS
    printf("--- Системний аналіз конвеєра (PIPESTATUS) ---\n");
    for (int i = 0; i < cmd_count; i++) {
        printf("  Елемент [%s] (PID %d) -> Exit Code: %d\n", 
               cmds[i].argv[0], results[i].pid, results[i].exit_code);
    }

    // 5. Обчислення підсумкового статусу $?
    int final_status = 0;
    if (pipefail_enabled) {
        for (int i = 0; i < cmd_count; i++) {
            if (results[i].exit_code != 0) {
                final_status = results[i].exit_code;
                break;
            }
        }
    } else {
        final_status = results[cmd_count - 1].exit_code;
    }

    printf("Підсумковий код виходу оболонки ($?) (pipefail=%s): %d\n", 
           pipefail_enabled ? "ON" : "OFF", final_status);
}

int main(void) {
    Command pipeline[] = {
        {.argv = {"cat", "/nonexistent_file_12345", NULL}},
        {.argv = {"grep", "pattern", NULL}},
        {.argv = {"wc", "-l", NULL}}
    };

    printf("=== Сценарій 1: Запуск конвеєра у стандартному режимі POSIX ===\n");
    execute_pipeline(pipeline, 3, 0);

    printf("\n=== Сценарій 2: Запуск конвеєра у режимі pipefail ===\n");
    execute_pipeline(pipeline, 3, 1);

    return 0;
}
