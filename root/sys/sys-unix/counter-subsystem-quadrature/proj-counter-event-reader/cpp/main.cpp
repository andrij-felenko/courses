#include <iostream>
#include <vector>
#include <memory>
#include <system_error>
#include <fstream>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <sys/ioctl.h>
#include <linux/counter.h>

namespace counter {

class CounterDevice {
public:
    explicit CounterDevice(const char* device_path) {
        int raw_fd = ::open(device_path, O_RDWR);
        if (raw_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити пристрій counter");
        }
        fd_ = std::unique_ptr<int, FdCloser>(new int(raw_fd));
    }

    void add_watch(uint8_t event_type, uint8_t channel) {
        struct counter_watch watch{};
        watch.event = event_type;
        watch.channel = channel;
        watch.component.type = COUNTER_COMPONENT_NONE;

        if (::ioctl(*fd_, COUNTER_ADD_WATCH_IOCTL, &watch) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка додавання counter watch");
        }
    }

    void enable_events() {
        if (::ioctl(*fd_, COUNTER_ENABLE_EVENTS_IOCTL) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка включення подій counter");
        }
    }

    std::vector<struct counter_event> read_events(int timeout_ms) {
        struct pollfd pfd{};
        pfd.fd = *fd_;
        pfd.events = POLLIN;

        int ret = ::poll(&pfd, 1, timeout_ms);
        if (ret < 0) {
            if (errno == EINTR) {
                return {};
            }
            throw std::system_error(errno, std::generic_category(), "Помилка виконання poll()");
        }

        std::vector<struct counter_event> events;
        if (ret > 0 && (pfd.revents & POLLIN)) {
            struct counter_event buffer[16];
            ssize_t bytes = ::read(*fd_, buffer, sizeof(buffer));
            if (bytes < 0) {
                if (errno == EOVERFLOW) {
                    std::cerr << "Увага: переповнення кільцевого буфера подій ядра (EOVERFLOW)\n";
                    resynchronize_sysfs();
                    return {};
                }
                throw std::system_error(errno, std::generic_category(), "Помилка читання подій counter");
            }
            size_t count = static_cast<size_t>(bytes) / sizeof(struct counter_event);
            events.assign(buffer, buffer + count);
        }
        return events;
    }

    uint64_t resynchronize_sysfs() {
        std::ifstream sysfs_file("/sys/bus/counter/devices/counter0/count0/count");
        uint64_t absolute_count = 0;
        if (sysfs_file >> absolute_count) {
            std::cout << "[Синхронізація] sysfs absolute count: " << absolute_count << "\n";
        } else {
            std::cerr << "[Помилка] Не вдалося зчитати sysfs count для ресинхронізації\n";
        }
        return absolute_count;
    }

private:
    struct FdCloser {
        void operator()(int* fd) const {
            if (fd && *fd >= 0) {
                ::close(*fd);
                delete fd;
            }
        }
    };

    std::unique_ptr<int, FdCloser> fd_;
};

} // namespace counter

int main() {
    try {
        counter::CounterDevice dev("/dev/counter0");

        /* Налаштування спостереження за подійним потоком */
        dev.add_watch(COUNTER_EVENT_OVERFLOW, 0);
        dev.add_watch(COUNTER_EVENT_INDEX, 0);
        dev.enable_events();

        std::cout << "C++ Читач подій /dev/counter0 запущено.\n";

        uint64_t last_ts = 0;
        uint64_t last_val = 0;
        const double ppr = 4096.0;

        for (int i = 0; i < 10; ++i) {
            auto events = dev.read_events(5000);
            for (const auto& ev : events) {
                std::cout << "[Час: " << ev.timestamp << " нс] "
                          << "Watch ID: " << static_cast<int>(ev.watch_id)
                          << " | Значення: " << ev.value
                          << " | Канал: " << static_cast<int>(ev.channel) << "\n";

                if (last_ts > 0 && ev.timestamp > last_ts) {
                    double dt = static_cast<double>(ev.timestamp - last_ts) / 1e9;
                    double dv = static_cast<double>(ev.value - last_val);
                    double rpm = (dv / (ppr * 4.0)) / (dt / 60.0);
                    std::cout << "  -> Швидкість: " << rpm << " RPM (dt = " << dt << " с)\n";
                }
                last_ts = ev.timestamp;
                last_val = ev.value;
            }
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка роботи з counter: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
