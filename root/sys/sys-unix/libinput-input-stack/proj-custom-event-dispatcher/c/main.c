#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <poll.h>
#include <sys/epoll.h>
#include <libudev.h>
#include <libinput.h>
#include <linux/input-event-codes.h>

/* Функція безпечного відкриття пристроїв ядра */
static int open_restricted(const char *path, int flags, void *user_data) {
    (void)user_data;
    int fd = open(path, flags | O_CLOEXEC | O_NONBLOCK);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", path, strerror(errno));
        return -errno;
    }
    return fd;
}

/* Функція закриття дескриптора пристрою */
static void close_restricted(int fd, void *user_data) {
    (void)user_data;
    close(fd);
}

static const struct libinput_interface interface = {
    .open_restricted = open_restricted,
    .close_restricted = close_restricted,
};

/* Автоматичне налаштування параметрів пристрою під час його появи */
static void configure_device(struct libinput_device *dev) {
    const char *name = libinput_device_get_name(dev);
    printf("[+] Підключено пристрій: %s (вузол %s)\n",
           name, libinput_device_get_sysname(dev));

    /* Налаштування тачпада */
    if (libinput_device_config_tap_get_finger_count(dev) > 0) {
        /* Увімкнення Tap-to-click */
        libinput_device_config_tap_set_enabled(dev, LIBINPUT_CONFIG_TAP_ENABLED);
        /* Зіставлення: 1 палець — лівий клік, 2 — правий, 3 — середній */
        libinput_device_config_tap_set_button_map(dev, LIBINPUT_CONFIG_TAP_MAP_LRM);
        printf("    -> Tap-to-click активовано (LRM)\n");
    }

    if (libinput_device_config_dwt_is_available(dev)) {
        /* Блокування тачпада під час активного набору тексту */
        libinput_device_config_dwt_set_enabled(dev, LIBINPUT_CONFIG_DWT_ENABLED);
        printf("    -> Блокування при наборі (DWT) увімкнено\n");
    }

    if (libinput_device_config_scroll_has_natural_scroll(dev)) {
        /* Природна прокрутка (рух вмісту вслід за пальцями) */
        libinput_device_config_scroll_set_natural_scroll_enabled(dev, 1);
        printf("    -> Природну прокрутку (Natural Scroll) активовано\n");
    }
}

/* Обробка окремої високорівневої події */
static void handle_event(struct libinput_event *ev) {
    enum libinput_event_type type = libinput_event_get_type(ev);
    struct libinput_device *dev = libinput_event_get_device(ev);

    switch (type) {
    case LIBINPUT_EVENT_DEVICE_NOTIFY:
        configure_device(dev);
        break;

    case LIBINPUT_EVENT_KEYBOARD_KEY: {
        struct libinput_event_keyboard *k = libinput_event_get_keyboard_event(ev);
        uint32_t key = libinput_event_keyboard_get_key(k);
        enum libinput_key_state state = libinput_event_keyboard_get_key_state(k);
        printf("[KEY] Код: %u, Стан: %s\n", key,
               state == LIBINPUT_KEY_STATE_PRESSED ? "НАТИСНУТО" : "ВІДПУЩЕНО");
        break;
    }

    case LIBINPUT_EVENT_POINTER_MOTION: {
        struct libinput_event_pointer *p = libinput_event_get_pointer_event(ev);
        double dx = libinput_event_pointer_get_dx(p);
        double dy = libinput_event_pointer_get_dy(p);
        double raw_dx = libinput_event_pointer_get_dx_unaccelerated(p);
        double raw_dy = libinput_event_pointer_get_dy_unaccelerated(p);
        printf("[POINTER] Рух: прискорений (%.2f, %.2f) | сирий (%.2f, %.2f)\n",
               dx, dy, raw_dx, raw_dy);
        break;
    }

    case LIBINPUT_EVENT_GESTURE_SWIPE_BEGIN:
    case LIBINPUT_EVENT_GESTURE_SWIPE_UPDATE:
    case LIBINPUT_EVENT_GESTURE_SWIPE_END: {
        struct libinput_event_gesture *g = libinput_event_get_gesture_event(ev);
        int fingers = libinput_event_gesture_get_finger_count(g);
        double dx = libinput_event_gesture_get_dx(g);
        double dy = libinput_event_gesture_get_dy(g);
        const char *phase = (type == LIBINPUT_EVENT_GESTURE_SWIPE_BEGIN) ? "ПОЧАТОК" :
                            (type == LIBINPUT_EVENT_GESTURE_SWIPE_UPDATE) ? "РУХ" : "КІНЕЦЬ";
        printf("[SWIPE %s] Пальців: %d, вектор: (%.2f, %.2f)\n", phase, fingers, dx, dy);
        break;
    }

    case LIBINPUT_EVENT_GESTURE_PINCH_BEGIN:
    case LIBINPUT_EVENT_GESTURE_PINCH_UPDATE:
    case LIBINPUT_EVENT_GESTURE_PINCH_END: {
        struct libinput_event_gesture *g = libinput_event_get_gesture_event(ev);
        double scale = libinput_event_gesture_get_scale(g);
        double angle = libinput_event_gesture_get_angle_delta(g);
        const char *phase = (type == LIBINPUT_EVENT_GESTURE_PINCH_BEGIN) ? "ПОЧАТОК" :
                            (type == LIBINPUT_EVENT_GESTURE_PINCH_UPDATE) ? "МАСШТАБ" : "КІНЕЦЬ";
        printf("[PINCH %s] Коефіцієнт: %.4f, Зміна кута: %.2f°\n", phase, scale, angle);
        break;
    }

    default:
        break;
    }
}

int main(void) {
    struct udev *udev = udev_new();
    if (!udev) {
        fprintf(stderr, "Не вдалося ініціалізувати контекст udev\n");
        return EXIT_FAILURE;
    }

    struct libinput *li = libinput_udev_create_context(&interface, NULL, udev);
    if (!li) {
        fprintf(stderr, "Не вдалося створити контекст libinput\n");
        udev_unref(udev);
        return EXIT_FAILURE;
    }

    if (libinput_udev_assign_seat(li, "seat0") != 0) {
        fprintf(stderr, "Помилка прив'язки до seat0\n");
        libinput_unref(li);
        udev_unref(udev);
        return EXIT_FAILURE;
    }

    int libinput_fd = libinput_get_fd(li);
    int epoll_fd = epoll_create1(EPOLL_CLOEXEC);
    if (epoll_fd < 0) {
        perror("epoll_create1");
        libinput_unref(li);
        udev_unref(udev);
        return EXIT_FAILURE;
    }

    struct epoll_event ev_reg = {
        .events = EPOLLIN,
        .data.fd = libinput_fd
    };
    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, libinput_fd, &ev_reg) < 0) {
        perror("epoll_ctl");
        close(epoll_fd);
        libinput_unref(li);
        udev_unref(udev);
        return EXIT_FAILURE;
    }

    printf("=== Диспетчер вводу запущено (очікування подій seat0) ===\n");

    struct epoll_event ep_events[8];
    int running = 1;

    while (running) {
        int n = epoll_wait(epoll_fd, ep_events, 8, -1);
        if (n < 0) {
            if (errno == EINTR) continue;
            perror("epoll_wait");
            break;
        }

        /* Зчитування та обробка внутрішньої черги libinput */
        if (libinput_dispatch(li) != 0) {
            fprintf(stderr, "Помилка диспетчеризації libinput\n");
            break;
        }

        struct libinput_event *event;
        while ((event = libinput_get_event(li)) != NULL) {
            handle_event(event);
            libinput_event_destroy(event);
        }
    }

    close(epoll_fd);
    libinput_unref(li);
    udev_unref(udev);
    return EXIT_SUCCESS;
}
