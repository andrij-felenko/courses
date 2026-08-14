# ⚙️ Асинхронний зчитувач evdev та створення віртуального пристрою uinput

Розробка низькорівневих системних утиліт під Linux — таких як сервери макросів, віртуальні клавіатури, транслятори жестових команд, емулятори геймпадів (Steam Input) або сервери віддаленого робочого столу (VNC/RDP) — вимагає одночасного асинхронного зчитування подій від кількох символьних файлів `/dev/input/eventN` та інжекції обробленого потоку назад у ядро через `/dev/uinput`.

Використання окремого POSIX-потоку (thread) для кожного файлового дескриптора пристрою у мультипристроєвих конфігураціях призводить до перевитрати ресурсів пам'яті та ускладнює міжпотокову синхронізацію часових позначок. Стандартним архітектурним підходом під Linux є поєднання неблокуючого вводу-виводу (`O_NONBLOCK`) із мультиплексуванням файлових дескрипторів через підсистему `epoll`.

### 1. Архітектурні вимоги та виклики реалізації

Під час розробки асинхронного демона обробки подій `evdev` розробник повинен реалізувати п'ять обов'язкових етапів обробки:

1. **Конфігурація неблокуючого режиму (`O_NONBLOCK`):** Відкриття символьного вузла `/dev/input/eventN` виконується з прапорцями `open(path, O_RDONLY | O_NONBLOCK)`. Це гарантує, що у випадку відсутності подій у буфері ядра системний виклик `read()` не зупинить потік виконання, а негайно поверне помилку `-EAGAIN` або `-EWOULDBLOCK`.
2. **Атомарне читання кадру структур:** Розмір буфера для `read()` повинен бути суворо кратним `sizeof(struct input_event)`. Спроба передати буфер неповного розміру поверне помилку `-EINVAL`. За один виклик `read()` ядро віддає масив з кількох подій, які відносяться до одного або кількох кадрів `EV_SYN`.
3. **Обробка переповнення буфера (`SYN_DROPPED`):** Якщо процес простору користувача тимчасово блокується і не встигає зчитувати дані (наприклад, через високе навантаження на CPU), кільцевий буфер ядра переповнюється. Драйвер ядра скидає застарілі події та надсилає спеціальний кадр з `type = EV_SYN` та `code = SYN_DROPPED`. Отримавши цей кадр, клієнт зобов'язаний скинути свій внутрішній стан і заново опитувати ядро про поточний стан усіх кнопок та осей за допомогою `ioctl(fd, EVIOCGKEY, ...)` та `ioctl(fd, EVIOCGABS, ...)`.
4. **Конфігурація віртуального пристрою uinput:** Створення пристрою у ядрі через `/dev/uinput` вимагає суворого дотримання послідовності викликів: відкриття вузла → оголошення capabilities через `UI_SET_EVBIT` та `UI_SET_KEYBIT` → заповнення структури `struct uinput_setup` → виконання `UI_DEV_CREATE`.
5. **Безпечне завершення та демонтаж:** При зупинці сигналами `SIGINT` або `SIGTERM` процес повинен викликати `ioctl(ufd, UI_DEV_DESTROY)` та закрити файлові дескриптори, щоб ядро видалило символьний вузол з VFS.

### 2. Приклад реалізації мовами C та C++

У прикладі нижче реалізовано асинхронний демон, який відкриває вказаний вузол `evdev`, додає його до об'єкта `epoll`, створює віртуальну клавіатуру через `uinput` і транслює потік подій. Якщо користувач натискає клавішу `KEY_A`, демон підміняє її код на `KEY_B` перед інжекцією у віртуальний пристрій.

:::tabs
```c
/* C Implementation: epoll + evdev reader + uinput injector */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/epoll.h>
#include <sys/ioctl.h>
#include <linux/input.h>
#include <linux/uinput.h>

#define MAX_EVENTS 10
#define EVENT_BUFFER_SIZE 32

static int setup_uinput_device(void) {
    int ufd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);
    if (ufd < 0) {
        perror("Failed to open /dev/uinput");
        return -1;
    }

    if (ioctl(ufd, UI_SET_EVBIT, EV_KEY) < 0 ||
        ioctl(ufd, UI_SET_KEYBIT, KEY_A) < 0 ||
        ioctl(ufd, UI_SET_KEYBIT, KEY_B) < 0 ||
        ioctl(ufd, UI_SET_EVBIT, EV_SYN) < 0) {
        perror("Failed to set uinput capabilities");
        close(ufd);
        return -1;
    }

    struct uinput_setup usetup;
    memset(&usetup, 0, sizeof(usetup));
    usetup.id.bustype = BUS_USB;
    usetup.id.vendor = 0x1234;
    usetup.id.product = 0x5678;
    snprintf(usetup.name, UINPUT_MAX_NAME_SIZE, "Virtual Test Keyboard");

    if (ioctl(ufd, UI_DEV_SETUP, &usetup) < 0 ||
        ioctl(ufd, UI_DEV_CREATE) < 0) {
        perror("Failed to create uinput device");
        close(ufd);
        return -1;
    }

    return ufd;
}

static void process_input_events(int ev_fd, int ufd) {
    struct input_event ev[EVENT_BUFFER_SIZE];
    ssize_t bytes_read = read(ev_fd, ev, sizeof(ev));

    if (bytes_read < 0) {
        if (errno != EAGAIN && errno != EWOULDBLOCK) {
            perror("Read error on evdev node");
        }
        return;
    }

    size_t count = (size_t)bytes_read / sizeof(struct input_event);
    for (size_t i = 0; i < count; ++i) {
        if (ev[i].type == EV_SYN && ev[i].code == SYN_DROPPED) {
            fprintf(stderr, "Warning: Buffer overflow, SYN_DROPPED received!\n");
            /* У реальному коді тут виконується EVIOCGKEY для синхронізації стану */
            continue;
        }

        printf("Event: type=%u, code=%u, value=%d\n", ev[i].type, ev[i].code, ev[i].value);

        /* Якщо натиснуто KEY_A — модифікуємо і відправляємо KEY_B у uinput */
        if (ev[i].type == EV_KEY && ev[i].code == KEY_A) {
            struct input_event mod_ev = ev[i];
            mod_ev.code = KEY_B;
            if (write(ufd, &mod_ev, sizeof(mod_ev)) < 0) {
                perror("Failed to write to uinput");
            }
        } else {
            if (write(ufd, &ev[i], sizeof(ev[i])) < 0) {
                perror("Failed to passthrough event to uinput");
            }
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s /dev/input/eventN\n", argv[0]);
        return EXIT_FAILURE;
    }

    int ev_fd = open(argv[1], O_RDONLY | O_NONBLOCK);
    if (ev_fd < 0) {
        perror("Failed to open input device");
        return EXIT_FAILURE;
    }

    int ufd = setup_uinput_device();
    if (ufd < 0) {
        close(ev_fd);
        return EXIT_FAILURE;
    }

    int epoll_fd = epoll_create1(EPOLL_CLOEXEC);
    if (epoll_fd < 0) {
        perror("Failed to create epoll instance");
        close(ufd);
        close(ev_fd);
        return EXIT_FAILURE;
    }

    struct epoll_event ev_spec;
    memset(&ev_spec, 0, sizeof(ev_spec));
    ev_spec.events = EPOLLIN;
    ev_spec.data.fd = ev_fd;

    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, ev_fd, &ev_spec) < 0) {
        perror("Failed to add ev_fd to epoll");
        close(epoll_fd);
        ioctl(ufd, UI_DEV_DESTROY);
        close(ufd);
        close(ev_fd);
        return EXIT_FAILURE;
    }

    printf("Listening for input events on %s...\n", argv[1]);
    struct epoll_event events[MAX_EVENTS];

    for (int loop = 0; loop < 20; ++loop) {
        int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, 2000);
        if (nfds < 0) {
            if (errno == EINTR) continue;
            perror("epoll_wait failed");
            break;
        }

        for (int n = 0; n < nfds; ++n) {
            if (events[n].data.fd == ev_fd) {
                process_input_events(ev_fd, ufd);
            }
        }
    }

    /* Clean exit */
    close(epoll_fd);
    ioctl(ufd, UI_DEV_DESTROY);
    close(ufd);
    close(ev_fd);
    return EXIT_SUCCESS;
}
```
```cpp
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
```
:::

### 3. Порівняння підходів та аналіз працездатності

1. **Керування ресурсами через RAII (C++):** Реалізація мовою C++ використовує обгортку `UniqueFd` для керування файловими дескрипторами та клас `VirtualDevice` для утримання ресурсу `/dev/uinput`. Це гарантує, що при виникненні винятків чи раптовому поверненні з функції деструктор автоматично викличе `UI_DEV_DESTROY` та `close()`. Реалізація мовою C вимагає явного керування ресурсами на кожній гілці помилок.
2. **Безпека типів з `std::span` (C++20):** Використання `std::span<const input_event>` дозволяє ітеруватися по масиву зчитаних подій без використання системних вказівників чи ручного обчислення зміщень байтів.
3. **Налаштування прав udev та безпека системних викликів:** За замовчуванням файли пристроїв `/dev/input/eventN` та `/dev/uinput` доступні для читання й запису лише користувачу `root` або членам групи `input`. Для запуску демонів від імені звичайного користувача у системну конфігурацію додається правило udev (`/etc/udev/rules.d/99-uinput.rules`):

```ini
KERNEL=="uinput", MODE="0660", GROUP="input"
```

### 4. Динамічне відслідковування hotplug через libudev

У реальних виробничих системних сервісах набір пристроїв `/dev/input/eventN` не є статичним. Користувачі підключають та відключають USB-клавіатури, Bluetooth-миші та тачпади під час роботи системи.

Для підтримки гарячого підключення (hotplug) цикл подій `epoll` доповнюють сокетом `libudev`. Демон створює монітор `udev_monitor_new_from_netlink(udev, "udev")`, підписується на підсистему `"input"` та додає файловий дескриптор сокета `udev_monitor_get_fd()` до того самого об'єкта `epoll`.

Коли в систему вставляється новий USB-пристрій, `epoll_wait()` спрацьовує на дескрипторі udev, демон зчитує повідомлення `udev_monitor_receive_device()`, перевіряє наявність властивості `ID_INPUT_KEYBOARD` або `ID_INPUT_MOUSE`, відкриває новий `/dev/input/eventN` і додає його дескриптор до циклу `epoll`. При відключенні пристрою виклик `read()` повертає `0` або помилку `-ENODEV`, після чого дескриптор видаляється з `epoll` та закривається.

### 5. Обробка системних сигналів через signalfd

Для забезпечення коректного переривання та безпечного демонтажу віртуальних пристроїв `uinput` при отриманні сигналів `SIGINT` або `SIGTERM` рекомендується уникнути класичних асинхронних обробників `signal()`. 

Натомість сигнальний маскувальний дескриптор створюється через `signalfd()` і реєструється в `epoll`. Це дозволяє обробляти сигнали завершення в тому самому однопотоковому циклі `epoll_wait()`, гарантуючи послідовне виконання `UI_DEV_DESTROY` без ризику стану гонитви (race condition).

### 6. Перевірка властивостей пристроїв через sysfs без відкриття /dev/input

Перед відкриттям файлів у `/dev/input/eventN` демону часто потрібно дізнатися текстові характеристики та параметри пристрою без використання системних викликів `ioctl` на бінарному вузлі.

Псевдофайлова система `sysfs` надає повне відображення дерева підсистеми вводу за шляхом `/sys/class/input/eventN/device/`. Кожен такий каталог містить текстові атрибути:
- `name`: Текстова назва пристрою (наприклад, `"AT Translated Set 2 keyboard"`).
- `phys`: Фізична топологія шини.
- `uniq`: Унікальний серійний номер.
- `properties`: Бітова маска властивостей `INPUT_PROP_*` у шістнадцятирічному форматі.
- `capabilities/ev`: Бітова маска типів подій `EV_*` (наприклад, `"120013"` — біти `EV_SYN`, `EV_KEY`, `EV_MSC`, `EV_LED`, `EV_REP`).
- `capabilities/key`: Шестнадцятирічна бітова маска всіх підтримуваних кодів кнопок.

Програма може зчитати ці текстові файли стандартними функціями `fopen()` / `fgets()`, відфільтрувати некорисні джерела (наприклад, кнопка живлення `Power Button`) і відкрити викликом `open()` лише ті файли `/dev/input/eventN`, які дійсно відповідають цільовій клавіатурі або миші.
