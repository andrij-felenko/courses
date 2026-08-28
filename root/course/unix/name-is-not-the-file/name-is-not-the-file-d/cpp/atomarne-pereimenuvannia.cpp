#include <fcntl.h>
#include <unistd.h>
#include <string_view>

// Небезпечний прямий перезапис: обнуляє інод перед записом
void unsafe_overwrite(std::string_view new_config) {
    int fd = ::open("/etc/app/config.json", O_WRONLY | O_TRUNC);
    if (fd >= 0) {
        ::write(fd, new_config.data(), new_config.size());
        ::close(fd);
    }
}
