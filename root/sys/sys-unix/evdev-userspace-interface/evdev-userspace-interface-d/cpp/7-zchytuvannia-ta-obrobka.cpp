#include <iostream>
#include <string_view>
#include <system_error>
#include <array>
#include <fcntl.h>
#include <unistd.h>
#include <linux/input.h>

class EvdevReader {
    int fd_{-1};
public:
    explicit EvdevReader(std::string_view path) {
        fd_ = ::open(path.data(), O_RDONLY);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to open evdev device");
        }
    }

    ~EvdevReader() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    EvdevReader(const EvdevReader&) = delete;
    EvdevReader& operator=(const EvdevReader&) = delete;

    void run_loop() {
        struct input_event ev{};
        while (true) {
            ssize_t bytes_read = ::read(fd_, &ev, sizeof(ev));
            if (bytes_read < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "Read error from evdev");
            }

            if (bytes_read != sizeof(ev)) {
                std::cerr << "Incomplete input_event struct read\n";
                continue;
            }

            switch (ev.type) {
                case EV_KEY:
                    std::cout << "[KEY] Code: " << ev.code << ", Value: " << ev.value
                              << " (" << (ev.value == 1 ? "Pressed" : ev.value == 0 ? "Released" : "Repeat") << ")\n";
                    break;
                case EV_REL:
                    std::cout << "[REL] Axis: " << ev.code << ", Delta: " << ev.value << '\n';
                    break;
                case EV_ABS:
                    std::cout << "[ABS] Axis: " << ev.code << ", Value: " << ev.value << '\n';
                    break;
                case EV_SYN:
                    if (ev.code == SYN_REPORT) {
                        std::cout << "--- SYN_REPORT ---\n";
                    } else if (ev.code == SYN_DROPPED) {
                        std::cout << "⚠️ WARNING: SYN_DROPPED detected!\n";
                    }
                    break;
                default:
                    break;
            }
        }
    }
};

int main(int argc, char* argv[]) {
    const char* path = (argc > 1) ? argv[1] : "/dev/input/event0";
    try {
        std::cout << "Opening " << path << "...\n";
        EvdevReader reader(path);
        reader.run_loop();
    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
