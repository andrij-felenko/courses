#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <sysexits.h>
#include <unistd.h>

void analyze_process_status(int wstatus) {
    if (WIFEXITED(wstatus)) {
        int code = WEXITSTATUS(wstatus);
        printf("[C] Процес завершився нормально. Код виходу: %d\n", code);
        switch (code) {
            case EX_OK:
                printf("  Результат: Успіх (EX_OK).\n");
                break;
            case EX_USAGE:
                printf("  Причина: Некоректні параметри командного рядка (EX_USAGE).\n");
                break;
            case EX_NOINPUT:
                printf("  Причина: Вхідний файл відсутній або недоступний (EX_NOINPUT).\n");
                break;
            case EX_UNAVAILABLE:
                printf("  Причина: Необхідний сервіс недоступний (EX_UNAVAILABLE).\n");
                break;
            default:
                printf("  Причина: Специфічний код програми (%d).\n", code);
                break;
        }
    } else if (WIFSIGNALED(wstatus)) {
        int sig = WTERMSIG(wstatus);
        printf("[C] Процес вбито сигналом: %d\n", sig);
        if (WCOREDUMP(wstatus)) {
            printf("  Увага: Ядро згенерувало образ пам'яті (core dump).\n");
        }
        printf("  Еквівалентний код для оболонки ($?): %d\n", 128 + sig);
    } else if (WIFSTOPPED(wstatus)) {
        printf("[C] Процес зупинено сигналом Job Control: %d\n", WSTOPSIG(wstatus));
    }
}
