#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    // Вектор аргументів: нульовим елементом має бути ім'я програми
    char *script_args[] = {
        "/usr/local/bin/backup-tool.sh",
        "--source", "/var/www/data",
        "--dest", "/var/backups",
        NULL
    };

    // Масив змінних середовища для нового процесу
    char *custom_env[] = {
        "PATH=/usr/bin:/bin:/usr/local/bin",
        "LOG_LEVEL=DEBUG",
        NULL
    };

    printf("Виклик execve для запуску сценарію...\n");
    // Якщо execve успішний, поточний процес заміщується новим образом
    if (execve(script_args[0], script_args, custom_env) == -1) {
        perror("Помилка execve");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
