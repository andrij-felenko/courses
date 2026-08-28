#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <string.h>

// Симуляція стану командної оболонки
typedef struct {
    int execution_counter;
    char current_working_dir[256];
} ShellContext;

void demonstrate_subshell_isolation(void) {
    ShellContext ctx;
    ctx.execution_counter = 0;
    strcpy(ctx.current_working_dir, "/var/log");

    // Створюємо спільний тимчасовий файл для перевірки дескрипторів
    int shared_fd = open("/tmp/subshell_test.log", O_CREAT | O_RDWR | O_TRUNC, 0644);
    if (shared_fd == -1) {
        perror("open failed");
        return;
    }

    printf("[Parent Before Fork] Counter: %d, CWD: %s\n", 
           ctx.execution_counter, ctx.current_working_dir);

    pid_t pid = fork();

    if (pid < 0) {
        perror("fork failed");
        close(shared_fd);
        return;
    }

    if (pid == 0) {
        // === Дочірній процес: Підоболонка (Subshell) ===
        printf("  [Subshell PID %d] Modifying context...\n", getpid());
        ctx.execution_counter = 999; // Модифікація скопійованої сторінки пам'яті
        strcpy(ctx.current_working_dir, "/tmp");

        const char *subshell_msg = "Line from subshell\n";
        write(shared_fd, subshell_msg, strlen(subshell_msg));

        printf("  [Subshell PID %d] Counter is now: %d, CWD: %s\n",
               getpid(), ctx.execution_counter, ctx.current_working_dir);

        close(shared_fd);
        exit(0); // Завершення підоболонки, пам'ять знищується ядром
    }

    // === Батьківський процес (Main Shell) ===
    int status;
    waitpid(pid, &status, 0); // Очікуємо завершення підоболонки

    const char *parent_msg = "Line from parent\n";
    // Зверніть увагу: зміщення (offset) зсунуто дочірнім процесом!
    write(shared_fd, parent_msg, strlen(parent_msg));

    printf("[Parent After Wait] Counter: %d (NOT 999!), CWD: %s\n",
           ctx.execution_counter, ctx.current_working_dir);

    // Перевіряємо розмір та вміст файлу
    lseek(shared_fd, 0, SEEK_SET);
    char buffer[256];
    ssize_t bytes_read = read(shared_fd, buffer, sizeof(buffer) - 1);
    if (bytes_read > 0) {
        buffer[bytes_read] = '\0';
        printf("[File Content Analysis]:\n%s", buffer);
    }

    close(shared_fd);
    unlink("/tmp/subshell_test.log");
}

int main(void) {
    demonstrate_subshell_isolation();
    return 0;
}
