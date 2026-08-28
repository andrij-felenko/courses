// Ідіоматичний приклад C++20 (ioctl ABI v2 з RAII та шаблонами)
#include <iostream>
#include <string_view>
#include <array>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <cerrno>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <poll.h>
#include <linux/gpio.h>

namespace sys {
    // Обгортка RAII для файлового дескриптора
    class UniqueFd {
        int fd_{-1};
    public:
        constexpr UniqueFd() noexcept = default;
        explicit UniqueFd(int fd) noexcept : fd_(fd) {}
        ~UniqueFd() { reset(); }

        UniqueFd(const UniqueFd&) = delete;
        UniqueFd& operator=(const UniqueFd&) = delete;

        UniqueFd(UniqueFd&& o) noexcept : fd_(o.release()) {}
        UniqueFd& operator=(UniqueFd&& o) noexcept {
            if (this != &o) { reset(o.release()); }
            return *this;
        }

        [[nodiscard]] int get() const noexcept { return fd_; }
        [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
        [[nodiscard]] int release() noexcept {
            int tmp = fd_;
            fd_ = -1;
            return tmp;
        }
        void reset(int new_fd = -1) noexcept {
            if (fd_ >= 0) { ::close(fd_); }
            fd_ = new_fd;
        }
    };
}

int main() {
    sys::UniqueFd chip_fd{::open("/dev/gpiochip0", O_RDWR | O_CLOEXEC)};
    if (!chip_fd.valid()) {
        std::cerr << "Не вдалося відкрити /dev/gpiochip0: " 
                  << std::generic_category().message(errno) << '\n';
        return EXIT_FAILURE;
    }

    ::gpio_v2_line_request req{};
    req.offsets[0] = 17;
    req.offsets[1] = 27;
    req.num_lines = 2;
    std::strncpy(req.consumer, "cpp-raw-ioctl-demo", sizeof(req.consumer) - 1);

    req.config.flags = GPIO_V2_LINE_FLAG_INPUT |
                       GPIO_V2_LINE_FLAG_EDGE_RISING |
                       GPIO_V2_LINE_FLAG_EDGE_FALLING;

    req.config.num_attrs = 2;
    
    // Атрибут 0: Output + Pull-Up для лінії 17 (mask = 0x01)
    req.config.attrs[0].attr.id = GPIO_V2_LINE_ATTR_ID_FLAGS;
    req.config.attrs[0].attr.flags = GPIO_V2_LINE_FLAG_OUTPUT | GPIO_V2_LINE_FLAG_BIAS_PULL_UP;
    req.config.attrs[0].mask = 0x01;

    // Атрибут 1: Debounce 5000 мкс для лінії 27 (mask = 0x02)
    req.config.attrs[1].attr.id = GPIO_V2_LINE_ATTR_ID_DEBOUNCE;
    req.config.attrs[1].attr.debounce_period_us = 5000;
    req.config.attrs[1].mask = 0x02;

    if (::ioctl(chip_fd.get(), GPIO_V2_GET_LINE_IOCTL, &req) < 0) {
        std::cerr << "Помилка ioctl GET_LINE: " << std::generic_category().message(errno) << '\n';
        return EXIT_FAILURE;
    }

    sys::UniqueFd line_fd{req.fd};
    std::cout << "Отримано Line FD (" << line_fd.get() << "). Встановлюємо HIGH на 17...\n";

    ::gpio_v2_line_values vals{};
    vals.mask = 0x01;
    vals.bits = 0x01;

    if (::ioctl(line_fd.get(), GPIO_V2_LINE_SET_VALUES_IOCTL, &vals) < 0) {
        std::cerr << "Помилка SET_VALUES: " << std::generic_category().message(errno) << '\n';
    }

    ::pollfd pfd{.fd = line_fd.get(), .events = POLLIN, .revents = 0};
    std::cout << "Очікування події переривання (10 с таймаут)...\n";

    if (int ret = ::poll(&pfd, 1, 10000); ret > 0 && (pfd.revents & POLLIN)) {
        ::gpio_v2_line_event event{};
        if (::read(line_fd.get(), &event, sizeof(event)) == sizeof(event)) {
            std::cout << "ПОДІЯ C++! Timestamp: " << event.timestamp_ns << " нс, "
                      << "Фронт: " << (event.id == GPIO_V2_LINE_EVENT_RISING_EDGE ? "RISING" : "FALLING")
                      << ", Пін: " << event.offset << ", SeqNo: " << event.seqno << '\n';
        }
    }

    // Звільнення ресурсів відбудеться автоматично завдяки RAII-деструкторам UniqueFd
    return EXIT_SUCCESS;
}
