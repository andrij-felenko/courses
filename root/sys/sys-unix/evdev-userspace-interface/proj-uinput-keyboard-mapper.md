# ⚙️ Практичний перепризначувач клавіш на базі evdev та uinput

Цей проект показує побудову повнофункціональної утиліти для простору користувача, яка перехоплює події від фізичної клавіатури через `evdev` за допомогою монопольного захоплення `EVIOCGRAB`, модифікує події на льоту (наприклад, перетворює натискання клавіші `Caps Lock` у `Escape`) та ретранслює їх у систему через віртуальний пристрій `uinput`. Такий підхід працює універсально на рівні ядра Linux і не залежить від дисплейного сервера (X11, Wayland чи віртуальна консоль TTY).

## Архітектурний задум та конвеєр обробки

Головною проблемою традиційних утиліт перепризначення клавіш (таких як `xmodmap` чи `setxkbmap`) є їхня жорстка прив'язка до застарілої графічної підсистеми X11. Вони не працюють у сесіях Wayland (GNOME Mutter, KDE KWin, Sway) і абсолютно недієві у текстовій консолі Linux.

Використання комбінації `evdev` та `uinput` дозволяє перехоплювати події на найнижчому рівні ядра:

```
[Фізична клавіатура] ──► /dev/input/eventX (evdev)
                                │
                                ▼ (EVIOCGRAB: монопольне захоплення)
                     [Програма-перепризначувач]
                                │ (заміна KEY_CAPSLOCK -> KEY_ESC)
                                ▼
                        /dev/uinput (uinput) ──► [Віртуальна клавіатура] ──► [Система]
```

Процес перехоплення складається з п'яти послідовних кроків:

1. **Відкриття дескрипторів та режим файлу:** Програма відкриває пристрій джерела `/dev/input/eventX` у режимі читання та пристрій створення віртуальних пристроїв `/dev/uinput` у режимі запису із прапорцем `O_NONBLOCK`. Прапорець `O_NONBLOCK` важливий для запобігання блокуванню потоку запису, якщо буфер ядра `uinput` тимчасово заповнений.
2. **Конфігурація віртуального пристрою (Handshake):** За допомогою викликів `ioctl(UI_SET_EVBIT)` та `ioctl(UI_SET_KEYBIT)` програма оголошує ядру, що новий віртуальний пристрій є клавіатурою і підтримує весь діапазон стандартних клавіш від `KEY_RESERVED` до `KEY_MAX`. Ядро будує внутрішню маску можливостей для майбутньої реєстрації.
3. **Реєстрація у підсистемі uinput:** Програма заповнює структуру `uinput_setup`, передаючи назву «Virtual Remapped Keyboard» та довільні Vendor/Product ID (`0x1234/0x5678`), після чого викликає `UI_DEV_SETUP` та `UI_DEV_CREATE`. Ядро створює новий системний вузол у псевдофайловій системі `/sys/devices/virtual/input/inputX` та динамічно виділяє мінорний номер для нового пристрою `/dev/input/eventY`.
4. **Монопольне захоплення (EVIOCGRAB):** Програма викликає `ioctl(g_src_fd, EVIOCGRAB, 1)`. Це виключає передачу оригінальних подій фізичної клавіатури до системного графічного сервера, запобігаючи подвійному реагуванню на натискання `Caps Lock`. Усі події надходять виключно у кільцевий буфер файлового дескриптора нашої програми.
5. **Цикл ретрансляції та обробка сигналів:** Програма у безкінечному циклі зчитує структури `input_event`. Якщо код події дорівнює `KEY_CAPSLOCK`, вона замінює його на `KEY_ESC` і записує модифіковану структуру у дескриптор `/dev/uinput`.

## Покроковий перебіг подій при натисканні клавіші

Щоб зрозуміти, як відбувається трансформація події у часі, розглянемо послідовність дій при натисканні клавіші `Caps Lock`:

- Користувач натискає фізичну кнопку `Caps Lock`. Драйвер клавіатури генерує переривання, й Input Core передає в буфер `evdev` дві структури: `EV_KEY KEY_CAPSLOCK 1` (натиснуто) та `EV_SYN SYN_REPORT 0` (кінець фрейму).
- Наша програма прокидається від виклику `read()`, зчитує обидві структури і модифікує першу: змінює `code` з `KEY_CAPSLOCK` (`58`) на `KEY_ESC` (`1`).
- Програма викликає `write()` у дескриптор `/dev/uinput`, надсилаючи пару `EV_KEY KEY_ESC 1` та `EV_SYN SYN_REPORT 0`.
- Драйвер `uinput` приймає запис і передає його назад у підсистему Input Core, яка розсилає подію натискання `Escape` усім активним слухачам (наприклад, активному вікну у Wayland чи терміналу).
- Користувач відпускає фізичну кнопку. Драйвер генерує `EV_KEY KEY_CAPSLOCK 0` та `EV_SYN SYN_REPORT 0`. Програма підміняє код на `KEY_ESC 0` і записує у `/dev/uinput`.

## Обробка крайніх випадків та динамічне підключення

У реальних виробничих умовах перепризначувач клавіш мусить враховувати додаткові фактори надійності:

- **Гаряче відключення (Hotplug Removal):** Якщо користувач висмикує USB-клавіатуру під час роботи програми, виклик `read()` повертає помилку `-ENODEV`. Програма повинна коректно закрити дескриптор джерела, знищити віртуальний пристрій через `UI_DEV_DESTROY` і перейти в режим очікування подій від `udev` (через `netlink` сокет `libudev`), щоб повторно захопити пристрій після його повторного підключення.
- **Збереження стану модифікаторів (Shift, Ctrl, Alt):** При виконанні складувальній заміні (наприклад, перетворенні одночасного натискання `Caps Lock + H` у ліву стрілку `KEY_LEFT`) програма зобов'язана відстежувати бітову маску утримуваних клавіш за допомогою `EVIOCGKEY`, щоб не пропустити подію відпускання клавіші-модифікатора.
- **Налаштування пріоритету процесу (Realtime Priority):** Оскільки перепризначувач лежить безпосередньо на шляху введення, будь-яка затримка у його плануванні призведе до лагу вводу (Input Lag). Рекомендується виставляти пріоритет процесу через `sched_setscheduler()` із політикою `SCHED_FIFO` або `SCHED_RR`.

## Реалізація проекту (C та C++)

Приклад нижче містить два ідіоматичних варіанти реалізації: у стилі стандартного C (з явним розбором ресурсів та обробкою сигналів) та у стилі C++ (із використанням RAII-обгортальників для файлових дескрипторів та автоматичного очищення ресурсів).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <linux/input.h>
#include <linux/uinput.h>

static int g_src_fd = -1;
static int g_uinput_fd = -1;

static void cleanup_and_exit(int sig) {
    (void)sig;
    if (g_src_fd >= 0) {
        // Звільняємо монопольне захоплення перед виходом
        ioctl(g_src_fd, EVIOCGRAB, 0);
        close(g_src_fd);
    }
    if (g_uinput_fd >= 0) {
        ioctl(g_uinput_fd, UI_DEV_DESTROY);
        close(g_uinput_fd);
    }
    printf("\n[KeyMapper] Пристрій звільнено. Завершення роботи.\n");
    exit(0);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s /dev/input/eventX\n", argv[0]);
        return 1;
    }

    const char *src_device = argv[1];
    g_src_fd = open(src_device, O_RDONLY);
    if (g_src_fd < 0) {
        perror("Не вдалося відкрити джерельний пристрій evdev");
        return 1;
    }

    g_uinput_fd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);
    if (g_uinput_fd < 0) {
        perror("Не вдалося відкрити /dev/uinput");
        close(g_src_fd);
        return 1;
    }

    // Декларація типів подій та клавіш для віртуального пристрою
    ioctl(g_uinput_fd, UI_SET_EVBIT, EV_KEY);
    ioctl(g_uinput_fd, UI_SET_EVBIT, EV_SYN);
    for (int i = 0; i < KEY_MAX; ++i) {
        ioctl(g_uinput_fd, UI_SET_KEYBIT, i);
    }

    struct uinput_setup usetup;
    memset(&usetup, 0, sizeof(usetup));
    usetup.id.bustype = BUS_USB;
    usetup.id.vendor = 0x1234;
    usetup.id.product = 0x5678;
    strcpy(usetup.name, "Virtual Remapped Keyboard");

    if (ioctl(g_uinput_fd, UI_DEV_SETUP, &usetup) < 0 ||
        ioctl(g_uinput_fd, UI_DEV_CREATE) < 0) {
        perror("Помилка створення пристрою uinput");
        close(g_src_fd);
        close(g_uinput_fd);
        return 1;
    }

    // Реєстрація системних сигналів для безпечного виходу
    signal(SIGINT, cleanup_and_exit);
    signal(SIGTERM, cleanup_and_exit);

    // Монопольне захоплення джерельного пристрою
    if (ioctl(g_src_fd, EVIOCGRAB, 1) < 0) {
        perror("Не вдалося виконати EVIOCGRAB на клавіатурі");
        cleanup_and_exit(1);
    }

    printf("[KeyMapper] Успішно захоплено %s. Натисніть Ctrl+C для виходу.\n", src_device);
    printf("[KeyMapper] Перетворюємо Caps Lock (код %d) -> Escape (код %d)\n", KEY_CAPSLOCK, KEY_ESC);

    struct input_event ev;
    while (read(g_src_fd, &ev, sizeof(ev)) > 0) {
        if (ev.type == EV_KEY) {
            if (ev.code == KEY_CAPSLOCK) {
                ev.code = KEY_ESC; // Заміна CapsLock на Escape
            }
        }
        if (write(g_uinput_fd, &ev, sizeof(ev)) < 0) {
            perror("Помилка запису події в uinput");
            break;
        }
    }

    cleanup_and_exit(0);
    return 0;
}
```
```cpp
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
```
:::

## Пастки та підводні камені (Traps & Pitfalls)

1. **Зависання блокування клавіатури при аварійному виході.** Якщо програма виконує `EVIOCGRAB` і падає через помилку пам'яті (`SIGSEGV`) чи неперехоплений виняток, ядро автоматично звільняє захоплення під час закриття дескриптора файлу. Проте якщо програма зависає у нескінченному циклі без обробки `SIGINT` (Ctrl+C), користувач повністю втрачає можливість вводити команди з клавіатури. Для запобігання цьому обов'язково реалізуйте очищення в деструкторах RAII або обробниках сигналів.
2. **Аварійне зациклення подій (Infinite Feedback Loop).** Якщо віртуальний пристрій `uinput` створить нову клавіатуру, а ваш перепризначувач за помилкою відкриє `/dev/input/eventX` *цього ж* віртуального пристрою замість фізичного, ви викличете нескінченну рекурсію подій, яка заблокує один з ядер процесора на 100%. Перевіряйте ідентифікатори `EVIOCGID` або ім'я пристрою `EVIOCGNAME` перед викликом `EVIOCGRAB`.
3. **Права доступу `/dev/uinput`.** За замовчуванням у більшості дистрибутивів Linux пристрій `/dev/uinput` має права `0600 root:root`. Для запуску перепризначувача від імені звичайного користувача слід додати правило `udev` у файл `/etc/udev/rules.d/99-uinput.rules`:
   ```text
   KERNEL=="uinput", MODE="0660", GROUP="input", OPTIONS+="static_node=uinput"
   ```
