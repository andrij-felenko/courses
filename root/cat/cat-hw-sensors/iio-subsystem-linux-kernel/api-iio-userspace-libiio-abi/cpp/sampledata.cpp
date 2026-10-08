#include <iostream>
#include <fcntl.h>
#include <unistd.h>
#include <cerrno>
#include <poll.h>
#include <cstdint>

struct SampleData {
    std::int16_t raw_x;
    std::int16_t raw_y;
    std::int16_t raw_z;
    std::int16_t pad;
    std::int64_t timestamp_ns;
};

int main() {
    int fd = ::open("/dev/iio:device0", O_RDONLY | O_NONBLOCK);
    if (fd < 0) {
        std::cerr << "Помилка відкриття файлового дескриптора IIO\n";
        return 1;
    }

    pollfd fds{.fd = fd, .events = POLLIN, .revents = 0};
    SampleData sample{};
    std::int64_t prev_timestamp = 0;

    for (int step = 0; step < 20; ++step) {
        int poll_ret = ::poll(&fds, 1, 500);
        if (poll_ret < 0) {
            if (errno == EINTR) continue;
            std::cerr << "Помилка poll()\n";
            break;
        }
        if (poll_ret == 0) {
            std::cout << "Немає нових даних (таймаут)\n";
            continue;
        }

        ssize_t bytes = ::read(fd, &sample, sizeof(sample));
        if (bytes < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) continue;
            std::cerr << "Помилка читання: " << errno << '\n';
            break;
        }

        if (bytes == sizeof(sample)) {
            if (prev_timestamp != 0) {
                std::int64_t dt = sample.timestamp_ns - prev_timestamp;
                if (dt > 15'000'000) {
                    std::cerr << "Увага: виявлено аномальний інтервал dt: " 
                              << dt << " нс\n";
                }
            }
            prev_timestamp = sample.timestamp_ns;
        }
    }

    ::close(fd);
    return 0;
}
