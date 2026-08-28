/* Приклад на мові C: Аналіз стека, перевірка O_CLOEXEC та розрахунок ARG_MAX */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/auxv.h>
#include <sys/wait.h>

extern char **environ;

void dump_stack_and_environment(int argc, char *argv[]) {
    printf("=== Process Context Dump (PID: %d) ===\n", getpid());
    printf("Number of arguments (argc): %d\n", argc);

    for (int i = 0; i < argc; ++i) {
        printf("  argv[%d] at address %p -> %s\n", i, (void*)argv[i], argv[i]);
    }

    printf("\n--- Environment Variables (first 5 entries) ---\n");
    for (int i = 0; environ[i] != NULL && i < 5; ++i) {
        printf("  env[%d] at address %p -> %s\n", i, (void*)environ[i], environ[i]);
    }

    printf("\n--- Auxiliary Vector Kernel Metadata ---\n");
    printf("  Page Size (AT_PAGESZ) : %lu bytes\n", getauxval(AT_PAGESZ));
    printf("  Entry Point (AT_ENTRY): 0x%lx\n", getauxval(AT_ENTRY));
    printf("  ELF Base (AT_BASE)    : 0x%lx\n", getauxval(AT_BASE));
    printf("  Secure Mode (AT_SECURE): %lu\n", getauxval(AT_SECURE));

    long arg_max = sysconf(_SC_ARG_MAX);
    printf("  System ARG_MAX Limit  : %ld bytes\n\n", arg_max);
}

void verify_descriptor_inheritance(void) {
    printf("=== Testing Descriptor Inheritance & O_CLOEXEC ===\n");

    /* Створення звичайного дескриптора */
    int fd_leaked = open("/dev/null", O_RDONLY);
    /* Створення дескриптора із захистом від витоку */
    int fd_protected = open("/dev/null", O_RDONLY | O_CLOEXEC);

    if (fd_leaked < 0 || fd_protected < 0) {
        perror("Failed to open /dev/null");
        return;
    }

    printf("Created fd_leaked = %d (normal), fd_protected = %d (O_CLOEXEC)\n",
           fd_leaked, fd_protected);

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork failed");
        return;
    }

    if (pid == 0) {
        /* Дитячий процес заступає виконувати /bin/true */
        char *child_argv[] = { "true", NULL };
        printf("[Child PID %d] Executing execve(/bin/true)...\n", getpid());
        fflush(stdout);

        execve("/bin/true", child_argv, environ);

        perror("execve failed");
        _exit(EXIT_FAILURE);
    } else {
        int status = 0;
        waitpid(pid, &status, 0);
        printf("[Parent] Child finished with exit code %d\n", WEXITSTATUS(status));

        close(fd_leaked);
        close(fd_protected);
    }
}

int main(int argc, char *argv[]) {
    dump_stack_and_environment(argc, argv);
    
    /* Якщо програма викликана без додаткових прапорців, запускаємо тест */
    if (argc == 1) {
        verify_descriptor_inheritance();
    }

    return EXIT_SUCCESS;
}
