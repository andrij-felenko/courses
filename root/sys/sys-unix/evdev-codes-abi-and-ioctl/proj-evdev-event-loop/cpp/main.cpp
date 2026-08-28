/* C++17/20 Implementation: RAII, std::span, Smart Pointers & Type Safety */
#include <iostream>
#include <vector>
#include <array>
#include <string>
#include <string_view>
#include <optional>
#include <span>
#include <memory>
#include <system_error>
#include <cerrno>
#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>
#include <sys/ioctl.h>
#include <linux/input.h>
#include <linux/uinput.h>

class UniqueFd {
    int fd_{-1};
public:
    constexpr UniqueFd() noexcept = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    explicit operator bool() const noexcept { return valid(); }

    int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

class VirtualDevice {
    UniqueFd ufd_;
public:
    static std::optional<VirtualDevice> create(std::string_view name) {
        UniqueFd fd{::open("/dev/uinput", O_WRONLY | O_NONBLOCK)};
        if (!fd) {
            std::perror("Failed to open /dev/uinput");
            return std::nullopt;
        }

        if (::ioctl(fd.get(), UI_SET_EVBIT, EV_KEY) < 0 ||
            ::ioctl(fd.get(), UI_SET_KEYBIT, KEY_A) < 0 ||
            ::ioctl(fd.get(), UI_SET_KEYBIT, KEY_B) < 0 ||
            ::ioctl(fd.get(), UI_SET_EVBIT, EV_SYN) < 0) {
            std::perror("Failed to set uinput capabilities");
            return std::nullopt;
        }

        struct uinput_setup usetup{};
        usetup.id.bustype = BUS_USB;
        usetup.id.vendor = 0x1234;
        usetup.id.product = 0x5678;
        name.copy(usetup.name, UINPUT_MAX_NAME_SIZE - 1);

        if (::ioctl(fd.get(), UI_DEV_SETUP, &usetup) < 0 ||
            ::ioctl(fd.get(), UI_DEV_CREATE) < 0) {
            std::perror("Failed to create uinput device");
            return std::nullopt;
        }

        return VirtualDevice{std::move(fd)};
    }

    explicit VirtualDevice(UniqueFd ufd) : ufd_(std::move(ufd)) {}

    ~VirtualDevice() {
        if (ufd_) {
            ::ioctl(ufd_.get(), UI_DEV_DESTROY);
        }
    }

    VirtualDevice(VirtualDevice&&) noexcept = default;
    VirtualDevice& operator=(VirtualDevice&&) noexcept = default;

    bool emit(const input_event& ev) const noexcept {
        return ::write(ufd_.get(), &ev, sizeof(ev)) == sizeof(ev);
    }
};

class EvdevLoop {
    UniqueFd epoll_fd_;
    UniqueFd event_fd_;
    VirtualDevice vdev_;

public:
    static std::optional<EvdevLoop> create(std::string_view path) {
        UniqueFd ev_fd{::open(path.data(), O_RDONLY | O_NONBLOCK)};
        if (!ev_fd) {
            std::perror("Failed to open input device");
            return std::nullopt;
        }

        auto vdev = VirtualDevice::create("CPP Virtual Keyboard");
        if (!vdev) return std::nullopt;

        UniqueFd ep_fd{::epoll_create1(EPOLL_CLOEXEC)};
        if (!ep_fd) {
            std::perror("Failed to create epoll instance");
            return std::nullopt;
        }

        struct epoll_event ev_spec{};
        ev_spec.events = EPOLLIN;
        ev_spec.data.fd = ev_fd.get();

        if (::epoll_ctl(ep_fd.get(), EPOLL_CTL_ADD, ev_fd.get(), &ev_spec) < 0) {
            std::perror("Failed to add fd to epoll");
            return std::nullopt;
        }

        return EvdevLoop{std::move(ep_fd), std::move(ev_fd), std::move(*vdev)};
    }

    EvdevLoop(UniqueFd ep_fd, UniqueFd ev_fd, VirtualDevice vdev)
        : epoll_fd_(std::move(ep_fd)), event_fd_(std::move(ev_fd)), vdev_(std::move(vdev)) {}

    void run_once(int timeout_ms = 1000) {
        std::array<epoll_event, 8> ep_events{};
        int nfds = ::epoll_wait(epoll_fd_.get(), ep_events.data(), static_cast<int>(ep_events.size()), timeout_ms);

        if (nfds < 0) {
            if (errno != EINTR) std::perror("epoll_wait failed");
            return;
        }

        for (int i = 0; i < nfds; ++i) {
            if (ep_events[i].data.fd == event_fd_.get()) {
                drain_events();
            }
        }
    }

private:
    void drain_events() {
        std::array<input_event, 32> buffer{};
        ssize_t bytes = ::read(event_fd_.get(), buffer.data(), buffer.size() * sizeof(input_event));

        if (bytes < 0) {
            if (errno != EAGAIN && errno != EWOULDBLOCK) {
                std::perror("evdev read error");
            }
            return;
        }

        std::span<const input_event> events{buffer.data(), static_cast<size_t>(bytes) / sizeof(input_event)};
        for (const auto& ev : events) {
            if (ev.type == EV_SYN && ev.code == SYN_DROPPED) {
                std::cerr << "Warning: SYN_DROPPED buffer overflow!\n";
                continue;
            }

            std::cout << "Event: type=" << ev.type << " code=" << ev.code << " value=" << ev.value << "\n";

            input_event out_ev = ev;
            if (ev.type == EV_KEY && ev.code == KEY_A) {
                out_ev.code = KEY_B;
            }
            vdev_.emit(out_ev);
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " /dev/input/eventN\n";
        return EXIT_FAILURE;
    }

    auto loop = EvdevLoop::create(argv[1]);
    if (!loop) return EXIT_FAILURE;

    std::cout << "Listening for events using C++20 EvdevLoop...\n";
    for (int i = 0; i < 10; ++i) {
        loop->run_once(2000);
    }

    return EXIT_SUCCESS;
}
