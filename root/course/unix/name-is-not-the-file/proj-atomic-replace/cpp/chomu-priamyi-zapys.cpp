#include <fcntl.h>
#include <unistd.h>
#include <string_view>

// Наївний прямий перезапис: обнуляє інод перед записом
void unsafe_write(std::string_view payload) {
    int fd = ::open("/etc/app/config.json", O_WRONLY | O_TRUNC);
    if (fd >= 0) {
        ::write(fd, payload.data(), payload.size());
        ::close(fd);
    }
}
