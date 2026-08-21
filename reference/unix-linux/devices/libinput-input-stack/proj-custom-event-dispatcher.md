# ⚙️ Реалізація власного диспетчера подій введення на основі libinput та epoll

Розробка власного графічного композитора, повноекранного ігрового рушія чи спеціалізованого інформаційного кіоску вимагає низькорівневої обробки подій вводу без залучення важких бібліотек віконних інтерфейсів. Написання власного коду для калібрування сенсорів, усунення шумів, розпізнавання жестів двома пальцями та захисту від долонь є надзвичайно трудомістким завданням. Бібліотека `libinput` бере на себе всю алгоритмічну складність, надаючи викликачу простий та уніфікований інтерфейс для інтеграції в системний цикл опитування [epoll](book:unix-linux/select-poll-epoll).

Нижче наведено повноцінну виробничу реалізацію сервісу вводу, який автоматично відстежує підключення нових пристроїв через [udev](book:unix-linux/udev-rules), налаштовує параметри тачпадів (увімкнення Tap-to-click, блокування при наборі тексту DWT та природну прокрутку) й транслює високорівневі жести щипка та свайпу.

---

## Архітектура та логіка роботи диспетчера

Програма побудована довкола наступних фундаментальних принципів:

1. **Безпечна взаємодія через інтерфейс зворотних викликів:** Бібліотека викликає користувацькі функції `open_restricted` та `close_restricted`. Це дозволяє у виробничих умовах передавати дескриптори від демона [logind](book:unix-linux/logind-sessions-seats) без надання процесу постійних прав `root`. Під час відкриття файлу обов'язково встановлюються прапорці `O_CLOEXEC` (запобігання витоку дескриптора у дочірні процеси) та `O_NONBLOCK` (неблокуючий ввід).
2. **Агрегований дескриптор сповіщень:** Замість додавання десятків окремих вузлів `/dev/input/event*` до `epoll`, програма реєструє єдиний дескриптор, повернутий функцією `libinput_get_fd()`. Коли ядро фіксує активність на будь-якому з пристроїв робочого місця `seat0`, цей дескриптор переходить у стан готовності до читання.
3. **Двоетапна диспетчеризація:**
   - Виклик `libinput_dispatch()` вичитує всі накопичені сирі структури `input_event` із системних буферів ядра та оновлює внутрішні фільтри й автомати жестів;
   - Цикл `while ((event = libinput_get_event(li)) != NULL)` витягує вже повністю розпізнані та нормалізовані семантичні події (натискання клавіш, вектори руху, масштаби щипків).
4. **Керування пам'яттю подій:** Кожна отримана подія є динамічно виділеною структурою. Викликач зобов'язаний звільнити її викликом `libinput_event_destroy()` (у C) або за допомогою RAII-обгортки `std::unique_ptr` (у C++).
5. **Динамічне виявлення пристроїв (Hotplug):** Завдяки зв'язці з `libudev` бібліотека автоматично підписується на події сокета `netlink` ядра. Коли користувач підключає нову USB-мишу або Bluetooth-тачпад, `libinput` самостійно відкриває новий вузол і генерує подію `LIBINPUT_EVENT_DEVICE_NOTIFY`, дозволяючи програмі застосувати налаштування на льоту.

---

## Повний вихідний код реалізації

:::tabs
```c
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
```
```cpp
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
```
:::

---

## Розбір критичних деталей та пасток реалізації

### 1. Небезпека блокуючих дескрипторів
Якщо у виклику `open()` випадково пропустити прапорець `O_NONBLOCK`, робота всієї системи вводу може заблокуватися. Коли ядро генерує потік подій від одного пристрою, спроба прочитати дані з іншого (який у цей момент мовчить) переведе потік диспетчера в нескінченне очікування. Саме тому `libinput` вимагає виключно неблокуючих файлових дескрипторів.

### 2. Витоки дескрипторів у багатопотокових середовищах
Прапорець `O_CLOEXEC` є обов'язковим для всіх дескрипторів сенсорних пристроїв. Якщо композитор запускає зовнішні процеси (наприклад, вікна програм клієнтів) через системні виклики `fork()` та `exec()`, відкриті дескриптори сенсорного заліза без `O_CLOEXEC` потраплять у простір дочірнього процесу. Це порушує модель ізоляції та створює вразливість перехоплення конфіденційного клавіатурного вводу (keylogging).

### 3. Очищення внутрішньої черги подій
Поширена помилка початківців — обробка лише однієї події за один сигнал готовності `epoll`. Оскільки ядро може надіслати пакет із 10–20 подій одночасно (наприклад, під час швидкого свайпу кількома пальцями), один виклик `libinput_dispatch()` додає до черги одразу всю пачку. Якщо викликач не вичистить чергу до кінця (поки `libinput_get_event()` не поверне `NULL`), події накопичуватимуться, створюючи зростаючу затримку (input lag) реакції інтерфейсу.

### 4. Фази жестів та обробка завершення
Події багатопальцевих жестів надходять строгими послідовностями: `BEGIN` → серія `UPDATE` → `END` (або `CANCEL`). Композитор зобов'язаний прив'язувати стан анімації вікна (наприклад, зсув віртуального робочого столу) до події `BEGIN`, плавно трансформувати графічні буфери під час `UPDATE`, а на етапі `END` перевіряти кінцеву швидкість і вектор. Якщо швидкість на момент `END` перевищує поріг інерції, композитор запускає кінетичний довід анімації (momentum animation); якщо ж жест переривається сторонньою подією (наприклад, опусканням четвертого пальця чи долоні), надходить `CANCEL`, за яким інтерфейс повертається у вихідний стан без перемикання екранів.

### 5. Автоматизоване тестування через uinput
Для перевірки коректності обробки жестів у середовищах неперервної інтеграції (CI/CD) немає потреби підключати фізичні тачпади. За допомогою модуля ядра [uinput](book:unix-linux/input-evdev) тестовий набір створює емульований тачпад, інжектує точну послідовність пакетів `input_event` (симулюючи дотик 3 пальців і свайп ліворуч) та перевіряє, чи диспетчер згенерував відповідну подію `LIBINPUT_EVENT_GESTURE_SWIPE_UPDATE` з очікуваним вектором зміщення.

### 6. Відмінності C та C++ реалізацій
У версії мовою C виділення та звільнення пам'яті подій і контекстів здійснюється вручну: забудьте виклик `libinput_event_destroy()` у будь-якій гілці `switch-case`, і програма за хвилину активного руху миші накопичить мегабайти витоку пам'яті. У C++ версії ресурсна безпека досягається за рахунок ідіоми RAII: користувацькі делетери `UdevDeleter`, `LibinputDeleter` та `EventDeleter` гарантують детерміноване звільнення об'єктів навіть у разі генерації винятків `std::system_error` під час системних збоїв `epoll`.
