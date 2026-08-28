#include <unistd.h>
#include <fcntl.h>

void sanitize_standard_descriptors(void) {
    int null_fd = open("/dev/null", O_RDWR);
    if (null_fd < 0) return;

    // Перенаправляємо 0, 1, 2 на /dev/null
    dup2(null_fd, STDIN_FILENO);
    dup2(null_fd, STDOUT_FILENO);
    dup2(null_fd, STDERR_FILENO);

    if (null_fd > STDERR_FILENO) {
        close(null_fd);
    }
}
