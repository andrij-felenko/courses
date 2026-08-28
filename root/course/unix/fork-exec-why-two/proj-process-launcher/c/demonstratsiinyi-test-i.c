#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/wait.h>

/* Прототип лаунчера */
int launch_process(const ProcessConfig *cfg, pid_t *out_pid);

int main(void) {
    printf("=== ТЕСТУВАННЯ СИСТЕМНОГО ЛАУНЧЕРА ===\n\n");

    /* Тест 1: Спроба запуску неіснуючого бінарного файлу */
    {
        char *argv[] = { "nonexistent_binary_xyz", NULL };
        ProcessConfig cfg = {
            .executable = "nonexistent_binary_xyz",
            .argv = argv
        };
        pid_t pid;
        int res = launch_process(&cfg, &pid);
        printf("[Тест 1: Неіснуючий файл] Результат: %d, errno: %d (%s)\n",
               res, errno, strerror(errno));
        if (res == -1 && errno == ENOENT) {
            printf("  -> УСПІХ: батько точно визначив помилку ENOENT!\n");
        }
    }

    /* Тест 2: Успішний запуск утиліти echo з передачею аргументів */
    {
        char *argv[] = { "echo", "Привіт із безпечного лаунчера!", NULL };
        ProcessConfig cfg = {
            .executable = "echo",
            .argv = argv
        };
        pid_t pid;
        int res = launch_process(&cfg, &pid);
        printf("\n[Тест 2: Успішний запуск echo] Результат: %d, PID: %d\n", res, pid);
        if (res == 0) {
            int status;
            waitpid(pid, &status, 0);
            printf("  -> УСПІХ: процес завершився з кодом %d\n", WEXITSTATUS(status));
        }
    }

    /* Тест 3: Обмеження пам'яті (RLIMIT_AS) */
    {
        char *argv[] = { "ls", "-la", NULL };
        ProcessConfig cfg = {
            .executable = "ls",
            .argv = argv,
            .max_memory_bytes = 1024 * 1024 /* Лише 1 МБ віртуальної пам'яті */
        };
        pid_t pid;
        int res = launch_process(&cfg, &pid);
        printf("\n[Тест 3: Обмеження пам'яті 1 МБ] Результат: %d, PID/errno: %d\n", res, pid);
        if (res == 0) {
            int status;
            waitpid(pid, &status, 0);
            printf("  -> Підпроцес завершився (можливий збій динамічного лінкера через ліміт пам'яті)\n");
        }
    }

    return 0;
}
