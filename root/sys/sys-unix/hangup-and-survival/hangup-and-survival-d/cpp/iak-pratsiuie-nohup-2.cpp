#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <system_error>

int out_fd = ::open("nohup.out", O_WRONLY | O_CREAT | O_APPEND, S_IRUSR | S_IWUSR);
if (out_fd < 0) {
    throw std::system_error(errno, std::generic_category(), "open nohup.out failed");
}
::dup2(out_fd, STDOUT_FILENO);
::dup2(out_fd, STDERR_FILENO);
::close(out_fd);
