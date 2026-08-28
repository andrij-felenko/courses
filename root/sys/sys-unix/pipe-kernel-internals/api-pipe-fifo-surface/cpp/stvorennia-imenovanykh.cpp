#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string_view>
#include <system_error>

void create_named_fifo(std::string_view path, mode_t mode = 0666) {
    if (::mkfifo(path.data(), mode) < 0 && errno != EEXIST) {
        throw std::system_error(errno, std::generic_category(), "mkfifo failed");
    }
}
