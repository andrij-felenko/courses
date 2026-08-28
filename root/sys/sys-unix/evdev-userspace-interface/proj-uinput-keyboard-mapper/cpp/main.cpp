#include <iostream>
#include <string_view>
#include <system_error>
#include <csignal>
#include <cstring>
#include <atomic>
#include <fcntl.h>
#include <unistd.h>
#include <linux/input.h>
#include <linux/uinput.h>

class SafeFd {
    int fd_{-1};
public:
    explicit SafeFd(int fd = -1) : fd_(fd) {}
    ~SafeFd() { reset(); }

    SafeFd(const SafeFd&) = delete;
    SafeFd& operator=(const SafeFd&) = delete;

    SafeFd(SafeFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    SafeFd& operator=(SafeFd&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

class UInputDevice {
    SafeFd fd_;
public:
    explicit UInputDevice(std::string_view name) {
        int raw_fd = ::open("/dev/uinput", O_WRONLY | O_NONBLOCK);
        if (raw_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to open /dev/uinput");
        }
        fd_.reset(raw_fd);

        ::ioctl(fd_.get(), UI_SET_EVBIT, EV_KEY);
        ::ioctl(fd_.get(), UI_SET_EVBIT, EV_SYN);
        for (int i = 0; i < KEY_MAX; ++i) {
            ::ioctl(fd_.get(), UI_SET_KEYBIT, i);
        }

        struct uinput_setup usetup{};
        usetup.id.bustype = BUS_USB;
        usetup.id.vendor = 0x1234;
        usetup.id.product = 0x5678;
        std::strncpy(usetup.name, name.data(), UINPUT_MAX_NAME_SIZE - 1);

        if (::ioctl(fd_.get(), UI_DEV_SETUP, &usetup) < 0 ||
            ::ioctl(fd_.get(), UI_DEV_CREATE) < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to create uinput device");
        }
    }

    ~UInputDevice() {
        if (fd_.valid()) {
            ::ioctl(fd_.get(), UI_DEV_DESTROY);
        }
    }

    void emit(const struct input_event& ev) {
        if (::write(fd_.get(), &ev, sizeof(ev)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to write event to uinput");
        }
    }
};

class EvdevGrabber {
    SafeFd fd_;
    bool grabbed_{false};
public:
    explicit EvdevGrabber(const char* path) {
        int raw_fd = ::open(path, O_RDONLY);
        if (raw_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to open input device");
        }
        fd_.reset(raw_fd);

        if (::ioctl(fd_.get(), EVIOCGRAB, 1) < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to EVIOCGRAB device");
        }
        grabbed_ = true;
    }

    ~EvdevGrabber() {
        if (grabbed_ && fd_.valid()) {
            ::ioctl(fd_.get(), EVIOCGRAB, 0);
        }
    }

    [[nodiscard]] int fd() const noexcept { return fd_.get(); }
};

static std::atomic<bool> g_running{true};

static void signal_handler(int) {
    g_running = false;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " /dev/input/eventX\n";
        return 1;
    }

    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    try {
        EvdevGrabber input_src(argv[1]);
        UInputDevice virtual_kbd("RAII Virtual Keyboard");

        std::cout << "[KeyMapper C++] Successfully grabbed " << argv[1] << ". Press Ctrl+C to exit.\n";

        struct input_event ev{};
        while (g_running) {
            ssize_t n = ::read(input_src.fd(), &ev, sizeof(ev));
            if (n < 0) {
                if (errno == EINTR) continue;
                break;
            }
            if (n == sizeof(ev)) {
                if (ev.type == EV_KEY && ev.code == KEY_CAPSLOCK) {
                    ev.code = KEY_ESC;
                }
                virtual_kbd.emit(ev);
            }
        }
    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << '\n';
        return 1;
    }

    std::cout << "[KeyMapper C++] Clean shutdown completed.\n";
    return 0;
}
