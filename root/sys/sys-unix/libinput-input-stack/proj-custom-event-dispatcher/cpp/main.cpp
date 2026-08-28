#include <iostream>
#include <memory>
#include <string_view>
#include <format>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>
#include <libudev.h>
#include <libinput.h>
#include <linux/input-event-codes.h>

/* RAII-делетери для C-структур бібліотек */
struct UdevDeleter {
    void operator()(udev* u) const noexcept { if (u) udev_unref(u); }
};

struct LibinputDeleter {
    void operator()(libinput* li) const noexcept { if (li) libinput_unref(li); }
};

struct EventDeleter {
    void operator()(libinput_event* ev) const noexcept { if (ev) libinput_event_destroy(ev); }
};

/* Обгортка дескриптора epoll за ідіомою RAII */
class EpollHandle {
    int fd_{-1};
public:
    EpollHandle() {
        fd_ = epoll_create1(EPOLL_CLOEXEC);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_create1 failed");
        }
    }
    ~EpollHandle() noexcept {
        if (fd_ >= 0) close(fd_);
    }
    [[nodiscard]] int get() const noexcept { return fd_; }

    void add(int target_fd, uint32_t events) const {
        epoll_event ev{};
        ev.events = events;
        ev.data.fd = target_fd;
        if (epoll_ctl(fd_, EPOLL_CTL_ADD, target_fd, &ev) < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_ctl ADD failed");
        }
    }
};

/* Головний клас керування та диспетчеризації вводу */
class InputManager {
    static int openRestricted(const char* path, int flags, void* /*user_data*/) noexcept {
        int fd = open(path, flags | O_CLOEXEC | O_NONBLOCK);
        return (fd < 0) ? -errno : fd;
    }

    static void closeRestricted(int fd, void* /*user_data*/) noexcept {
        close(fd);
    }

    static constexpr libinput_interface iface_{
        .open_restricted = openRestricted,
        .close_restricted = closeRestricted,
    };

    std::unique_ptr<udev, UdevDeleter> udev_;
    std::unique_ptr<libinput, LibinputDeleter> li_;
    EpollHandle epoll_;

    void configureDevice(libinput_device* dev) const {
        const char* name = libinput_device_get_name(dev);
        const char* sysname = libinput_device_get_sysname(dev);
        std::cout << std::format("[+] Підключено пристрій: {} (вузол {})\n", name, sysname);

        if (libinput_device_config_tap_get_finger_count(dev) > 0) {
            libinput_device_config_tap_set_enabled(dev, LIBINPUT_CONFIG_TAP_ENABLED);
            libinput_device_config_tap_set_button_map(dev, LIBINPUT_CONFIG_TAP_MAP_LRM);
            std::cout << "    -> Tap-to-click активовано (LRM)\n";
        }

        if (libinput_device_config_dwt_is_available(dev)) {
            libinput_device_config_dwt_set_enabled(dev, LIBINPUT_CONFIG_DWT_ENABLED);
            std::cout << "    -> Блокування при наборі (DWT) увімкнено\n";
        }

        if (libinput_device_config_scroll_has_natural_scroll(dev)) {
            libinput_device_config_scroll_set_natural_scroll_enabled(dev, 1);
            std::cout << "    -> Природну прокрутку (Natural Scroll) активовано\n";
        }
    }

    void handleEvent(libinput_event* raw_ev) const {
        auto type = libinput_event_get_type(raw_ev);
        auto* dev = libinput_event_get_device(raw_ev);

        switch (type) {
        case LIBINPUT_EVENT_DEVICE_NOTIFY:
            configureDevice(dev);
            break;

        case LIBINPUT_EVENT_KEYBOARD_KEY: {
            auto* k = libinput_event_get_keyboard_event(raw_ev);
            uint32_t key = libinput_event_keyboard_get_key(k);
            auto state = libinput_event_keyboard_get_key_state(k);
            std::cout << std::format("[KEY] Код: {}, Стан: {}\n",
                                     key, state == LIBINPUT_KEY_STATE_PRESSED ? "НАТИСНУТО" : "ВІДПУЩЕНО");
            break;
        }

        case LIBINPUT_EVENT_POINTER_MOTION: {
            auto* p = libinput_event_get_pointer_event(raw_ev);
            double dx = libinput_event_pointer_get_dx(p);
            double dy = libinput_event_pointer_get_dy(p);
            double raw_dx = libinput_event_pointer_get_dx_unaccelerated(p);
            double raw_dy = libinput_event_pointer_get_dy_unaccelerated(p);
            std::cout << std::format("[POINTER] Прискорений ({:.2f}, {:.2f}) | Сирий ({:.2f}, {:.2f})\n",
                                     dx, dy, raw_dx, raw_dy);
            break;
        }

        case LIBINPUT_EVENT_GESTURE_SWIPE_BEGIN:
        case LIBINPUT_EVENT_GESTURE_SWIPE_UPDATE:
        case LIBINPUT_EVENT_GESTURE_SWIPE_END: {
            auto* g = libinput_event_get_gesture_event(raw_ev);
            int fingers = libinput_event_gesture_get_finger_count(g);
            double dx = libinput_event_gesture_get_dx(g);
            double dy = libinput_event_gesture_get_dy(g);
            std::string_view phase = (type == LIBINPUT_EVENT_GESTURE_SWIPE_BEGIN) ? "ПОЧАТОК" :
                                     (type == LIBINPUT_EVENT_GESTURE_SWIPE_UPDATE) ? "РУХ" : "КІНЕЦЬ";
            std::cout << std::format("[SWIPE {}] Пальців: {}, вектор: ({:.2f}, {:.2f})\n",
                                     phase, fingers, dx, dy);
            break;
        }

        case LIBINPUT_EVENT_GESTURE_PINCH_BEGIN:
        case LIBINPUT_EVENT_GESTURE_PINCH_UPDATE:
        case LIBINPUT_EVENT_GESTURE_PINCH_END: {
            auto* g = libinput_event_get_gesture_event(raw_ev);
            double scale = libinput_event_gesture_get_scale(g);
            double angle = libinput_event_gesture_get_angle_delta(g);
            std::string_view phase = (type == LIBINPUT_EVENT_GESTURE_PINCH_BEGIN) ? "ПОЧАТОК" :
                                     (type == LIBINPUT_EVENT_GESTURE_PINCH_UPDATE) ? "МАСШТАБ" : "КІНЕЦЬ";
            std::cout << std::format("[PINCH {}] Коефіцієнт: {:.4f}, Кут: {:.2f}°\n",
                                     phase, scale, angle);
            break;
        }

        default:
            break;
        }
    }

public:
    InputManager(std::string_view seat = "seat0") {
        udev_.reset(udev_new());
        if (!udev_) {
            throw std::runtime_error("Failed to initialize udev context");
        }

        li_.reset(libinput_udev_create_context(&iface_, nullptr, udev_.get()));
        if (!li_) {
            throw std::runtime_error("Failed to create libinput context");
        }

        if (libinput_udev_assign_seat(li_.get(), seat.data()) != 0) {
            throw std::runtime_error("Failed to assign seat to libinput");
        }

        epoll_.add(libinput_get_fd(li_.get()), EPOLLIN);
    }

    void run() {
        std::cout << "=== Диспетчер вводу запущено (C++20, epoll) ===\n";
        epoll_event events[8];

        while (true) {
            int n = epoll_wait(epoll_.get(), events, 8, -1);
            if (n < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "epoll_wait failed");
            }

            if (libinput_dispatch(li_.get()) != 0) {
                throw std::runtime_error("libinput_dispatch returned error");
            }

            while (libinput_event* ev = libinput_get_event(li_.get())) {
                std::unique_ptr<libinput_event, EventDeleter> managed_ev(ev);
                handleEvent(managed_ev.get());
            }
        }
    }
};

int main() {
    try {
        InputManager manager("seat0");
        manager.run();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
