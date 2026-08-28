#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/serial.h>
#include <system_error>

void set_low_latency(int fd) {
    struct serial_struct serial{};
    if (::ioctl(fd, TIOCGSERIAL, &serial) < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка отримання параметрів TIOCGSERIAL");
    }
    serial.flags |= ASYNC_LOW_LATENCY;
    if (::ioctl(fd, TIOCSSERIAL, &serial) < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка встановлення ASYNC_LOW_LATENCY");
    }
}
