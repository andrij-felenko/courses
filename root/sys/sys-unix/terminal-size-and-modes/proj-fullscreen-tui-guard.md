# ⚙️ Надійний каркас TUI: перехоплення SIGWINCH, перехід у сирий режим і гарантоване відновлення

Повноекранні програми у терміналі (текстові редактори на зразок `vim` чи `neovim`, системні монітори `htop` та `btop`, файлові менеджери `ranger` чи `mc`) працюють у принципово іншому режимі взаємодії з операційною системою, ніж звичайні утиліти командного рядка. Звичайна програма спирається на лінійну дисципліну термінала за замовчуванням: операційна система сама буферизує ввід по рядках, відображає натиснуті символи на екрані та друкує текст послідовно зверху вниз. Інтерактивний TUI-додаток (англ. *Text User Interface*), навпаки, бере на себе повний контроль над кожним байтом вводу, кожною коміркою екрана та зміною розмірів вікна.

Будь-яка помилка в організації життєвого циклу такого додатка має миттєві деструктивні наслідки: якщо програма аварійно завершується або переривається сигналом без коректного відновлення стану, термінал користувача залишається «зламаним». Літери не відображаються під час введення, натискання Enter зсуває текст драбинкою без повернення до початку рядка, а сам курсор стає невидимим.

Нижче наведено детальний розбір архітектури та повноцінну реалізацію надійного каркаса TUI мовами C та сучасним ідіоматичним C++ (стандарт C++23), який гарантує безпечне керування терміналом за будь-яких умов.

## Архітектурний патерн захисного каркаса

Надійний каркас TUI-додатка реалізує кінцевий автомат (state machine) із трьома основними фазами:

1. **Фаза ініціалізації та захоплення:**
   - Перевірка дескриптора через `isatty(STDIN_FILENO)` для переконання, що програма виконується в інтерактивному сеансі, а не через конвеєр чи перенаправлення у файл.
   - Збереження оригінального стану термінальної лінії за допомогою виклику `tcgetattr(fd, &orig_termios)`.
   - Реєстрація функції відновлення в системній таблиці `atexit()`.
   - Налаштування перехоплення термінальних та аварійних сигналів (`SIGINT`, `SIGTERM`, `SIGHUP`, `SIGSEGV`, `SIGBUS`, `SIGABRT`).
   - Переведення термінала у сирий режим (Raw Mode) шляхом вимкнення канонічної буферизації (`~ICANON`), відлуння (`~ECHO`), системної пост-обробки виводу (`~OPOST`) та керування потоком (`~IXON`). Застосування конфігурації здійснюється через `tcsetattr(fd, TCSAFLUSH, &raw_termios)`.
   - Відправка керуючих послідовностей активації альтернативного екранного буфера `\e[?1049h` та приховування текстового курсора `\e[?25l`.

2. **Головний цикл подій (Event Loop):**
   - Визначення поточної геометрії вікна через `ioctl(fd, TIOCGWINSZ, &ws)` із запасним варіантом (fallback) на змінні оточення `LINES`/`COLUMNS` або стандартний розмір 80×24.
   - Мультиплексування вводу з клавіатури та подій зміни розміру екрана за допомогою `signalfd(2)` та `select(2)` (або `poll`/`epoll`). Це дозволяє уникнути стану перегонів (race conditions) та небезпечних операцій всередині класичних асинхронних обробників сигналів.
   - Динамічне перерахування внутрішніх координат та перемалювання інтерфейсу при отриманні сигналу `SIGWINCH`.

3. **Гарантоване відновлення (Teardown):**
   - Відновлення видимості курсора `\e[?25h`, повернення до основного екранного буфера `\e[?1049l` та скидання атрибутів кольору й стилів `\e[0m`.
   - Відновлення оригінальних прапорців `termios` через `tcsetattr(fd, TCSAFLUSH, &orig_termios)`.
   - Якщо відновлення викликане аварійним сигналом (`SIGSEGV`, `SIGBUS`), обробник скидає диспозицію сигналу на `SIG_DFL` і повторно надсилає його процесу через `raise(sig)`, щоб операційна система зберегла правильний код завершення та згенерувала дамп пам'яті (core dump).

## Чому signalfd надійніший за класичний обробник

У стандарті POSIX традиційний обробник сигналу, встановлений через `sigaction`, виконується асинхронно, перериваючи потік виконання програми у довільній точці. Всередині такого обробника дозволено викликати виключно асинхронно-безпечні функції (англ. *async-signal-safe functions*). Будь-який виклик функцій виділення пам'яті (`malloc`, `free`), операцій форматованого виводу (`printf`, `std::cout`) або логування під час роботи обробника `SIGWINCH` чи `SIGINT` може призвести до мертвого блокування (deadlock) внутрішніх м'ютексів стандартної бібліотеки C (`glibc`).

У Linux системний виклик `signalfd(2)` перетворює отримання сигналів на подію звичайного файлового дескриптора. Заблокувавши сигнали у масці процесу через `sigprocmask(SIG_BLOCK, ...)`, програма зчитує структури `struct signalfd_siginfo` безпосередньо у головному циклі опитування подій. Це перетворює обробку `SIGWINCH` та сигналів завершення на синхронну операцію, усуваючи будь-який ризик порушення реентерабельності.

Флаги `SFD_NONBLOCK` та `SFD_CLOEXEC` при створенні `signalfd` є обов'язковими:
- `SFD_NONBLOCK` гарантує, що спроба читання з дескриптора сигналів не заблокує процес, якщо сигнал уже було вилучено іншим потоком або оброблено.
- `SFD_CLOEXEC` автоматично закриває файловий дескриптор при виклику будь-якої функції сімейства `exec`, запобігаючи витоку дескриптора у дочірні процеси.

## Крайові випадки та поведінка під час збоїв

Під час практичної розробки TUI-додатків необхідно враховувати чотири типові нештатні ситуації:

1. **Миттєвий розрив SSH-сесії або закриття вікна емулятора (`SIGHUP`):**
   Коли графічне вікно емулятора закривається, псевдотермінал знищується, а ядро надсилає активному процесу сигнал `SIGHUP` (Hangup). Якщо програма не перехоплює `SIGHUP`, вона завершується миттєво. Наш каркас блокує `SIGHUP` у масці `signalfd` і коректно перериває головний цикл, виконуючи очищення ресурсів.

2. **Зміна розміру вікна під час очікування операцій введення-виведення:**
   Якщо користувач змінює розмір вікна, системний виклик `select` або `poll` завершується з помилкою `EINTR` (якщо використовуються традиційні обробники) або повертає готовність дескриптора `sfd` (при використанні `signalfd`). Головний цикл негайно перечитує структуру `struct winsize` та адаптує розмітку буфера під нові розміри.

3. **Обробка сигналів призупинення процесу (`SIGTSTP` і `SIGCONT`):**
   При натисканні `Ctrl+Z` термінал повинен бути повернений у канонічний режим, а альтернативний буфер — вимкнено до того, як процес засне. Після пробудження командою `fg` процес отримує `SIGCONT`, заново налаштовує сирий режим, відновлює альтернативний екран, опитує геометрію та повністю перемальовує вікно.

4. **Розбір багатобайтових керуючих послідовностей (Escape Sequences):**
   Натискання спеціальних клавіш (стрілки, `Home`, `End`, функціональні клавіші `F1`–`F12`) генерує не поодинокі байти, а послідовності вигляду `\e[A`, `\e[B`, `\e[1;5C`. Прапорці `c_cc[VMIN] = 1` та `c_cc[VTIME] = 0` гарантують, що програма отримує перший байт негайно, після чого розбирач вхідного потоку може швидко зчитати наступні байти послідовності.

## Реалізація каркаса TUI на мовах C та C++23

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <signal.h>
#include <sys/ioctl.h>
#include <sys/signalfd.h>
#include <sys/select.h>
#include <termios.h>

/* Глобальний контекст для безпечного аварійного відновлення */
static struct {
    int tty_fd;
    struct termios orig_termios;
    bool is_raw;
    bool is_alt_screen;
} g_term_state = { -1, {0}, false, false };

/* Процедура гарантованого скидання стану термінала */
static void terminal_cleanup(void) {
    if (g_term_state.tty_fd < 0) {
        return;
    }

    /* 1. Показуємо курсор, повертаємо основний екран і скидаємо оформлення */
    if (g_term_state.is_alt_screen) {
        const char restore_seq[] = "\x1b[?25h\x1b[?1049l\x1b[0m";
        (void)write(g_term_state.tty_fd, restore_seq, sizeof(restore_seq) - 1);
        g_term_state.is_alt_screen = false;
    }

    /* 2. Відновлюємо початкові параметри лінії termios */
    if (g_term_state.is_raw) {
        (void)tcsetattr(g_term_state.tty_fd, TCSAFLUSH, &g_term_state.orig_termios);
        g_term_state.is_raw = false;
    }
}

/* Обробник критичних сигналів: скидає стан і дозволяє ядру створити core dump */
static void emergency_signal_handler(int sig) {
    terminal_cleanup();

    /* Скидаємо дію на стандартну та перевикликаємо сигнал */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = SIG_DFL;
    sigemptyset(&sa.sa_mask);
    sigaction(sig, &sa, NULL);
    raise(sig);
}

/* Опитування поточної геометрії вікна з ланцюжком fallback */
static bool get_window_size(int fd, int *out_rows, int *out_cols) {
    struct winsize ws;
    if (ioctl(fd, TIOCGWINSZ, &ws) == 0 && ws.ws_row > 0 && ws.ws_col > 0) {
        *out_rows = ws.ws_row;
        *out_cols = ws.ws_col;
        return true;
    }

    /* Fallback 1: змінні середовища LINES та COLUMNS */
    const char *env_lines = getenv("LINES");
    const char *env_cols = getenv("COLUMNS");
    if (env_lines && env_cols) {
        int r = atoi(env_lines);
        int c = atoi(env_cols);
        if (r > 0 && c > 0) {
            *out_rows = r;
            *out_cols = c;
            return true;
        }
    }

    /* Fallback 2: стандартне значення VT100 */
    *out_rows = 24;
    *out_cols = 80;
    return false;
}

/* Перемалювання простого інформаційного кадру */
static void render_screen(int fd, int rows, int cols, int frame_count) {
    char buf[1024];
    /* Очищення екрана та переміщення курсора у лівий верхній кут */
    const char clear_cmd[] = "\x1b[2J\x1b[H";
    (void)write(fd, clear_cmd, sizeof(clear_cmd) - 1);

    /* Рядок заголовка */
    int len = snprintf(buf, sizeof(buf),
        "\x1b[1;37;44m TUI Guard Demo \x1b[0m — Розмір: \x1b[1;32m%d×%d\x1b[0m | Кадр: \x1b[1;33m#%d\x1b[0m\r\n",
        cols, rows, frame_count);
    (void)write(fd, buf, len);

    /* Інструкція для користувача */
    const char *msg1 = "Натисніть 'q' для виходу або змініть розмір вікна емулятора.\r\n";
    (void)write(fd, msg1, strlen(msg1));

    /* Статусний рядок у нижній частині вікна */
    len = snprintf(buf, sizeof(buf), "\x1b[%d;1H\x1b[7m [Q: Вихід] | [SIGWINCH: signalfd active] \x1b[0m", rows);
    (void)write(fd, buf, len);
}

int main(void) {
    /* 1. Перевірка інтерактивності */
    if (!isatty(STDIN_FILENO)) {
        fprintf(stderr, "Помилка: програма вимагає інтерактивного термінала.\n");
        return EXIT_FAILURE;
    }
    g_term_state.tty_fd = STDIN_FILENO;

    /* 2. Збереження початкового стану termios */
    if (tcgetattr(g_term_state.tty_fd, &g_term_state.orig_termios) == -1) {
        perror("tcgetattr");
        return EXIT_FAILURE;
    }

    /* 3. Реєстрація очищення в atexit */
    if (atexit(terminal_cleanup) != 0) {
        fprintf(stderr, "Не вдалося зареєструвати atexit handler.\n");
        return EXIT_FAILURE;
    }

    /* 4. Встановлення перехоплення фатальних збоїв */
    struct sigaction sa_fault;
    memset(&sa_fault, 0, sizeof(sa_fault));
    sa_fault.sa_handler = emergency_signal_handler;
    sigemptyset(&sa_fault.sa_mask);
    sa_fault.sa_flags = SA_RESETHAND;
    sigaction(SIGSEGV, &sa_fault, NULL);
    sigaction(SIGBUS, &sa_fault, NULL);
    sigaction(SIGABRT, &sa_fault, NULL);

    /* 5. Блокування сигналів для синхронного читання через signalfd */
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGWINCH);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGTERM);
    sigaddset(&mask, SIGHUP);

    if (sigprocmask(SIG_BLOCK, &mask, NULL) == -1) {
        perror("sigprocmask");
        return EXIT_FAILURE;
    }

    int sfd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (sfd == -1) {
        perror("signalfd");
        return EXIT_FAILURE;
    }

    /* 6. Налаштування сирого режиму termios */
    struct termios raw = g_term_state.orig_termios;
    raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
    raw.c_oflag &= ~(OPOST);
    raw.c_cflag |= (CS8);
    raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
    raw.c_cc[VMIN] = 1;
    raw.c_cc[VTIME] = 0;

    if (tcsetattr(g_term_state.tty_fd, TCSAFLUSH, &raw) == -1) {
        perror("tcsetattr raw");
        close(sfd);
        return EXIT_FAILURE;
    }
    g_term_state.is_raw = true;

    /* 7. Активація альтернативного буфера та приховування курсора */
    const char enter_seq[] = "\x1b[?1049h\x1b[?25l";
    (void)write(g_term_state.tty_fd, enter_seq, sizeof(enter_seq) - 1);
    g_term_state.is_alt_screen = true;

    /* 8. Головний цикл опитування */
    int rows = 24, cols = 80, frame = 0;
    get_window_size(g_term_state.tty_fd, &rows, &cols);
    render_screen(g_term_state.tty_fd, rows, cols, ++frame);

    bool running = true;
    while (running) {
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(STDIN_FILENO, &read_fds);
        FD_SET(sfd, &read_fds);
        int max_fd = (STDIN_FILENO > sfd ? STDIN_FILENO : sfd) + 1;

        if (select(max_fd, &read_fds, NULL, NULL, NULL) == -1) {
            if (errno == EINTR) continue;
            perror("select");
            break;
        }

        /* Обробка системних сигналів */
        if (FD_ISSET(sfd, &read_fds)) {
            struct signalfd_siginfo fdsi;
            ssize_t s = read(sfd, &fdsi, sizeof(fdsi));
            if (s == sizeof(fdsi)) {
                if (fdsi.ssi_signo == SIGWINCH) {
                    get_window_size(g_term_state.tty_fd, &rows, &cols);
                    render_screen(g_term_state.tty_fd, rows, cols, ++frame);
                } else if (fdsi.ssi_signo == SIGINT || fdsi.ssi_signo == SIGTERM || fdsi.ssi_signo == SIGHUP) {
                    running = false;
                }
            }
        }

        /* Обробка вводу користувача */
        if (FD_ISSET(STDIN_FILENO, &read_fds)) {
            char ch;
            if (read(STDIN_FILENO, &ch, 1) == 1) {
                if (ch == 'q' || ch == 'Q') {
                    running = false;
                } else {
                    render_screen(g_term_state.tty_fd, rows, cols, ++frame);
                }
            }
        }
    }

    close(sfd);
    /* terminal_cleanup() викликається автоматично через atexit */
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <format>
#include <expected>
#include <system_error>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/signalfd.h>
#include <sys/select.h>
#include <termios.h>
#include <csignal>

namespace sys {

struct WindowSize {
    unsigned short rows{24};
    unsigned short cols{80};
    unsigned short x_pixel{0};
    unsigned short y_pixel{0};
};

// RAII-вартовий термінала: повністю контролює життєвий цикл сирого режиму та буферів
class TerminalGuard {
public:
    // Фабричний метод для безпечного захоплення дескриптора термінала
    static std::expected<TerminalGuard, std::error_code> acquire(int fd = STDIN_FILENO) noexcept {
        if (!isatty(fd)) {
            return std::unexpected(std::make_error_code(std::errc::not_a_tty));
        }

        struct termios orig{};
        if (::tcgetattr(fd, &orig) == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        struct termios raw = orig;
        raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
        raw.c_oflag &= ~(OPOST);
        raw.c_cflag |= (CS8);
        raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
        raw.c_cc[VMIN] = 1;
        raw.c_cc[VTIME] = 0;

        if (::tcsetattr(fd, TCSAFLUSH, &raw) == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        // Активація альтернативного екранного буфера та приховування курсора
        constexpr std::string_view enter_seq = "\x1b[?1049h\x1b[?25l";
        [[maybe_unused]] auto _ = ::write(fd, enter_seq.data(), enter_seq.size());

        return TerminalGuard(fd, orig);
    }

    // Деструктор гарантує відновлення термінала при будь-якому виході з області видимості
    ~TerminalGuard() noexcept {
        restore();
    }

    TerminalGuard(const TerminalGuard&) = delete;
    TerminalGuard& operator=(const TerminalGuard&) = delete;

    TerminalGuard(TerminalGuard&& other) noexcept
        : fd_(other.fd_), orig_termios_(other.orig_termios_), active_(other.active_) {
        other.active_ = false;
    }

    TerminalGuard& operator=(TerminalGuard&& other) noexcept {
        if (this != &other) {
            restore();
            fd_ = other.fd_;
            orig_termios_ = other.orig_termios_;
            active_ = other.active_;
            other.active_ = false;
        }
        return *this;
    }

    [[nodiscard]] std::expected<WindowSize, std::error_code> query_size() const noexcept {
        struct winsize ws{};
        if (::ioctl(fd_, TIOCGWINSZ, &ws) == 0 && ws.ws_row > 0 && ws.ws_col > 0) {
            return WindowSize{ws.ws_row, ws.ws_col, ws.ws_xpixel, ws.ws_ypixel};
        }

        // Fallback на змінні середовища оточення
        const char* lines = std::getenv("LINES");
        const char* cols = std::getenv("COLUMNS");
        if (lines && cols) {
            int r = std::atoi(lines);
            int c = std::atoi(cols);
            if (r > 0 && c > 0) {
                return WindowSize{static_cast<unsigned short>(r), static_cast<unsigned short>(c), 0, 0};
            }
        }

        return WindowSize{24, 80, 0, 0};
    }

    void render_frame(const WindowSize& size, int frame_count) const noexcept {
        std::string frame;
        frame.reserve(1024);
        frame += "\x1b[2J\x1b[H"; // Очищення екрана та перехід у 1,1
        frame += std::format("\x1b[1;37;44m C++23 TUI Guard \x1b[0m — Розмір: \x1b[1;32m{}×{}\x1b[0m | Кадр: \x1b[1;33m#{}\x1b[0m\r\n",
                             size.cols, size.rows, frame_count);
        frame += "Натисніть 'q' для виходу або змініть розмір вікна емулятора.\r\n";
        frame += std::format("\x1b[{};1H\x1b[7m [Q: Quit] | [RAII Guard: Active] \x1b[0m", size.rows);

        [[maybe_unused]] auto _ = ::write(fd_, frame.data(), frame.size());
    }

private:
    TerminalGuard(int fd, const struct termios& orig) noexcept
        : fd_(fd), orig_termios_(orig), active_(true) {}

    void restore() noexcept {
        if (!active_ || fd_ < 0) return;

        constexpr std::string_view restore_seq = "\x1b[?25h\x1b[?1049l\x1b[0m";
        [[maybe_unused]] auto _ = ::write(fd_, restore_seq.data(), restore_seq.size());
        ::tcsetattr(fd_, TCSAFLUSH, &orig_termios_);
        active_ = false;
    }

    int fd_{-1};
    struct termios orig_termios_{};
    bool active_{false};
};

} // namespace sys

int main() {
    auto guard_res = sys::TerminalGuard::acquire();
    if (!guard_res) {
        std::cerr << "Помилка ініціалізації термінала: " << guard_res.error().message() << '\n';
        return EXIT_FAILURE;
    }
    auto& guard = *guard_res;

    // Налаштування signalfd для синхронного опрацювання подій ядра
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGWINCH);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGTERM);

    if (::sigprocmask(SIG_BLOCK, &mask, nullptr) == -1) {
        std::perror("sigprocmask");
        return EXIT_FAILURE;
    }

    int sfd = ::signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (sfd == -1) {
        std::perror("signalfd");
        return EXIT_FAILURE;
    }

    auto size = guard.query_size().value_or(sys::WindowSize{24, 80, 0, 0});
    int frame_count = 0;
    guard.render_frame(size, ++frame_count);

    bool running = true;
    while (running) {
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(STDIN_FILENO, &read_fds);
        FD_SET(sfd, &read_fds);
        int max_fd = std::max(STDIN_FILENO, sfd) + 1;

        if (::select(max_fd, &read_fds, nullptr, nullptr, nullptr) == -1) {
            if (errno == EINTR) continue;
            break;
        }

        if (FD_ISSET(sfd, &read_fds)) {
            struct signalfd_siginfo fdsi{};
            if (::read(sfd, &fdsi, sizeof(fdsi)) == sizeof(fdsi)) {
                if (fdsi.ssi_signo == SIGWINCH) {
                    size = guard.query_size().value_or(sys::WindowSize{24, 80, 0, 0});
                    guard.render_frame(size, ++frame_count);
                } else if (fdsi.ssi_signo == SIGINT || fdsi.ssi_signo == SIGTERM) {
                    running = false;
                }
            }
        }

        if (FD_ISSET(STDIN_FILENO, &read_fds)) {
            char ch{};
            if (::read(STDIN_FILENO, &ch, 1) == 1) {
                if (ch == 'q' || ch == 'Q') {
                    running = false;
                } else {
                    guard.render_frame(size, ++frame_count);
                }
            }
        }
    }

    ::close(sfd);
    // guard автоматично викликає деструктор тут, надійно відновлюючи стан оболонки
    return EXIT_SUCCESS;
}
```
:::
