#include <unistd.h>
#include <fcntl.h>

int execute_via_fd(const char *path, char *const argv[], char *const envp[]) {
    // Відкриваємо файл лише для читання з прапорцем O_CLOEXEC
    int fd = open(path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        return -1;
    }
    // Запускаємо файл безпосередньо через дескриптор
    return fexecve(fd, argv, envp);
}
