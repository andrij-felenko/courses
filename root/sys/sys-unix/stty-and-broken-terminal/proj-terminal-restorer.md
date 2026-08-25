# ⚙️ Надійний менеджер сирого режиму TTY: обробка сигналів, Job Control та RAII

Будь-яка консольна програма, що перемикає термінал у сирий режим (raw mode) для посимвольного вводу або побудови інтерфейсу TUI, бере на себе повну відповідальність за стан системної дисципліни лінії. Якщо процес завершиться аварійно, буде перерваний асинхронним сигналом або тимчасово призупинений користувачем через комбінацію `Ctrl+Z`, термінал залишиться у спотвореному стані для батьківської оболонки.

Цей проект надає вичерпний інженерний аналіз, архітектурні вимоги та готові виробничі реалізації мовами C та C++ у вкладках `:::tabs`. Вони демонструють гарантоване відновлення початкового стану структури `termios` при будь-яких сценаріях виходу, обробку сигналів завершення (`SIGINT`, `SIGTERM`, `SIGHUP`, `SIGQUIT`), а також коректну взаємодію з підсистемою керування завданнями операційної системи (Job Control) при зупинці процесу (`SIGTSTP`) та його поверненні на передній план (`SIGCONT`).

## Інженерні виклики та вектори загроз

Створення надійного менеджера термінала стикається з чотирма критичними векторами загроз:

1. **Асинхронні сигнали завершення:** Якщо користувач натискає `Ctrl+C` (у сирому режимі це байт `0x03`, але якщо увімкнено `ISIG` — це сигнал `SIGINT`) або адміністратор надсилає процесу сигнал `SIGTERM`/`SIGHUP`, стандартний обробник ядра негайно знищує процес. Якщо програма не перехопила ці сигнали, виклик відновлення термінала ніколи не відбудеться.
2. **Вимоги асинхронно-сигнальної безпеки (Async-Signal Safety):** Всередині обробника сигналу суворо заборонено викликати небезпечні функції стандартної бібліотеки: `printf()`, `malloc()`, `free()`, `exit()`, методи потоків введення-виведення C++ `std::cout` та оператори виділення пам'яті `new`/`delete`. Спроба виділити пам'ять в обробнику під час переривання іншого виклику `malloc()` гарантовано призводить до мертвого блокування (дедлоку). Єдиним легітимним способом відновлення є прямий виклик функції `tcsetattr()`, яка офіційно входить до переліку безпечних функцій стандарту POSIX.
3. **Механіка керування завданнями (Job Control):** Коли користувач натискає `Ctrl+Z`, ядро надсилає активному процесу сигнал `SIGTSTP`. Якщо програма просто проігнорує сигнал, зупинка не відбудеться. Якщо програма засне без скидання налаштувань, командна оболонка `bash` прокинеться і виведе свій промпт у термінал, який усе ще перебуває у сирому режимі (без відлуння та канонічного вводу). Тому обробник `SIGTSTP` зобов'язаний тимчасово відновити канонічний стан, скинути свій обробник на `SIG_DFL`, розблокувати сигнал і повторно надіслати `SIGTSTP` самому собі. Після повернення процесу на передній план командою `fg` ядро надсилає сигнал `SIGCONT`, обробник якого повторно застосовує сирий режим.
4. **Винятки та розгортання стека (Stack Unwinding у C++):** У разі виникнення винятку в бізнес-логіці програми об'єкт-охоронець (Guard) повинен автоматично викликати деструктор і відновити параметри `termios` до того, як виняток призведе до виходу з функції `main()`.

## Повні виробничі реалізації

Нижче наведено порівняльні реалізації мовами C та C++ у вкладках `:::tabs`. Реалізація мовою C спирається на функції зворотного виклику `atexit()`, атомарні прапорці `sig_atomic_t` та пряму роботу зі структурами `sigaction`. Реалізація мовою C++ інкапсулює стан у клас `TerminalGuard` за ідіомою RAII, забезпечуючи нульові витоки ресурсів та повну безпеку винятків.

:::tabs
```c
/* ==========================================================================
 * safe_terminal.c — Надійний менеджер сирого режиму TTY мовою C.
 * Гарантоване відновлення termios через atexit, sigaction та Job Control.
 * ========================================================================== */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <termios.h>
#include <signal.h>
#include <errno.h>

/* Глобальний збережений стан термінала та атомарні прапорці */
static struct termios g_orig_termios;
static struct termios g_raw_termios;
static volatile sig_atomic_t g_is_raw = 0;

/* Асинхронно-сигнально безпечне відновлення початкового стану */
static void restore_terminal_raw(void)
{
    if (g_is_raw) {
        /* tcsetattr належить до переліку Async-Signal-Safe функцій POSIX */
        tcsetattr(STDIN_FILENO, TCSANOW, &g_orig_termios);
        g_is_raw = 0;
    }
}

/* Обробник atexit() для штатного завершення процесу */
static void on_exit_cleanup(void)
{
    restore_terminal_raw();
}

/* Обробник фатальних сигналів (SIGINT, SIGTERM, SIGHUP, SIGQUIT) */
static void on_fatal_signal(int signo)
{
    int saved_errno = errno;
    restore_terminal_raw();

    /* Скидаємо дію на типову (SIG_DFL) та повторно надсилаємо сигнал */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = SIG_DFL;
    sigemptyset(&sa.sa_mask);
    sigaction(signo, &sa, NULL);

    sigset_t unblock_mask;
    sigemptyset(&unblock_mask);
    sigaddset(&unblock_mask, signo);
    sigprocmask(SIG_UNBLOCK, &unblock_mask, NULL);

    raise(signo);
    errno = saved_errno;
}

/* Обробник призупинення процесу (Job Control: Ctrl+Z) */
static void on_tstp_signal(int signo)
{
    (void)signo;
    int saved_errno = errno;

    /* 1. Повертаємо канонічний режим термінала для оболонки */
    restore_terminal_raw();

    /* 2. Скидаємо обробник на SIG_DFL, щоб ядро призупинило процес */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = SIG_DFL;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGTSTP, &sa, NULL);

    sigset_t unblock_mask;
    sigemptyset(&unblock_mask);
    sigaddset(&unblock_mask, SIGTSTP);
    sigprocmask(SIG_UNBLOCK, &unblock_mask, NULL);

    /* 3. Надсилаємо SIGTSTP самі собі — процес зупиняється */
    raise(SIGTSTP);

    /* 4. Коли процес повертають на передній план (команда fg),
     * виконання поновлюється з цієї точки. Відновлюємо наш обробник. */
    sa.sa_handler = on_tstp_signal;
    sigaction(SIGTSTP, &sa, NULL);

    errno = saved_errno;
}

/* Обробник поновлення процесу з фону (Job Control: fg / SIGCONT) */
static void on_cont_signal(int signo)
{
    (void)signo;
    int saved_errno = errno;

    /* Повторно перемикаємо термінал у сирий режим */
    if (!g_is_raw) {
        tcsetattr(STDIN_FILENO, TCSAFLUSH, &g_raw_termios);
        g_is_raw = 1;
    }

    errno = saved_errno;
}

/* Налаштування обробників усіх сигналів */
static int setup_signal_handlers(void)
{
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));

    sa.sa_handler = on_fatal_signal;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;

    int fatal_signals[] = { SIGINT, SIGTERM, SIGHUP, SIGQUIT };
    for (size_t i = 0; i < sizeof(fatal_signals) / sizeof(fatal_signals[0]); ++i) {
        if (sigaction(fatal_signals[i], &sa, NULL) < 0) {
            return -1;
        }
    }

    sa.sa_handler = on_tstp_signal;
    if (sigaction(SIGTSTP, &sa, NULL) < 0) {
        return -1;
    }

    sa.sa_handler = on_cont_signal;
    if (sigaction(SIGCONT, &sa, NULL) < 0) {
        return -1;
    }

    return 0;
}

/* Активація сирого режиму TTY */
static int enable_raw_mode(void)
{
    if (!isatty(STDIN_FILENO)) {
        errno = ENOTTY;
        return -1;
    }

    if (tcgetattr(STDIN_FILENO, &g_orig_termios) < 0) {
        return -1;
    }

    if (atexit(on_exit_cleanup) != 0) {
        return -1;
    }

    if (setup_signal_handlers() < 0) {
        return -1;
    }

    g_raw_termios = g_orig_termios;
    cfmakeraw(&g_raw_termios);

    /* Читання від 1 байта без часового ліміту */
    g_raw_termios.c_cc[VMIN] = 1;
    g_raw_termios.c_cc[VTIME] = 0;

    if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &g_raw_termios) < 0) {
        return -1;
    }

    g_is_raw = 1;
    return 0;
}

int main(void)
{
    if (enable_raw_mode() < 0) {
        perror("Помилка ініціалізації термінала");
        return EXIT_FAILURE;
    }

    const char intro[] = "Сирий режим активовано. Натискайте будь-які клавіші (q — вихід, Ctrl+Z — тест Job Control):\r\n";
    (void)write(STDOUT_FILENO, intro, sizeof(intro) - 1);

    unsigned char c = 0;
    while (1) {
        ssize_t n = read(STDIN_FILENO, &c, 1);
        if (n < 0) {
            if (errno == EINTR) {
                continue; /* Перервано сигналом, продовжуємо цикл */
            }
            break;
        }
        if (n == 0) {
            break; /* Кінцевий EOF */
        }

        if (c == 'q') {
            const char msg[] = "\r\nОтримано команду виходу 'q'. Відновлення термінала...\r\n";
            (void)write(STDOUT_FILENO, msg, sizeof(msg) - 1);
            break;
        }

        char buf[64];
        int len = snprintf(buf, sizeof(buf), "Код байта: 0x%02X ('%c')\r\n", c, (c >= 32 && c <= 126) ? c : '.');
        if (len > 0) {
            (void)write(STDOUT_FILENO, buf, (size_t)len);
        }
    }

    return EXIT_SUCCESS;
}
```
```cpp
// ==========================================================================
// safe_terminal.cpp — Ідіоматичний RAII-менеджер сирого режиму C++.
// Автоматичне відновлення в деструкторі, безпека винятків та обробка сигналів.
// ==========================================================================

#include <iostream>
#include <string_view>
#include <vector>
#include <array>
#include <memory>
#include <system_error>
#include <csignal>
#include <cstring>
#include <unistd.h>
#include <termios.h>

namespace tty {

class TerminalGuard {
public:
    TerminalGuard() {
        if (::isatty(STDIN_FILENO) == 0) {
            throw std::system_error(errno, std::generic_category(), "STDIN не є терміналом");
        }

        if (::tcgetattr(STDIN_FILENO, &m_orig_termios) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося отримати termios");
        }

        s_active_instance = this;
        setup_signals();

        m_raw_termios = m_orig_termios;
        ::cfmakeraw(&m_raw_termios);
        m_raw_termios.c_cc[VMIN] = 1;
        m_raw_termios.c_cc[VTIME] = 0;

        if (::tcsetattr(STDIN_FILENO, TCSAFLUSH, &m_raw_termios) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося встановити сирий режим");
        }

        m_is_raw = true;
    }

    ~TerminalGuard() noexcept {
        restore_raw();
        s_active_instance = nullptr;
    }

    TerminalGuard(const TerminalGuard&) = delete;
    TerminalGuard& operator=(const TerminalGuard&) = delete;
    TerminalGuard(TerminalGuard&&) = delete;
    TerminalGuard& operator=(TerminalGuard&&) = delete;

    void restore_raw() noexcept {
        if (m_is_raw) {
            ::tcsetattr(STDIN_FILENO, TCSANOW, &m_orig_termios);
            m_is_raw = false;
        }
    }

    void enable_raw() noexcept {
        if (!m_is_raw) {
            ::tcsetattr(STDIN_FILENO, TCSAFLUSH, &m_raw_termios);
            m_is_raw = true;
        }
    }

    [[nodiscard]] bool is_raw() const noexcept {
        return m_is_raw;
    }

private:
    struct termios m_orig_termios{};
    struct termios m_raw_termios{};
    bool m_is_raw{false};

    inline static TerminalGuard* s_active_instance{nullptr};

    static void signal_handler(int signo) noexcept {
        int saved_errno = errno;
        if (s_active_instance != nullptr) {
            s_active_instance->restore_raw();
        }

        struct sigaction sa{};
        sa.sa_handler = SIG_DFL;
        ::sigemptyset(&sa.sa_mask);
        ::sigaction(signo, &sa, nullptr);

        sigset_t unblock_mask;
        ::sigemptyset(&unblock_mask);
        ::sigaddset(&unblock_mask, signo);
        ::sigprocmask(SIG_UNBLOCK, &unblock_mask, nullptr);

        ::raise(signo);
        errno = saved_errno;
    }

    static void tstp_handler(int signo) noexcept {
        (void)signo;
        int saved_errno = errno;
        if (s_active_instance != nullptr) {
            s_active_instance->restore_raw();
        }

        struct sigaction sa{};
        sa.sa_handler = SIG_DFL;
        ::sigemptyset(&sa.sa_mask);
        ::sigaction(SIGTSTP, &sa, nullptr);

        sigset_t unblock_mask;
        ::sigemptyset(&unblock_mask);
        ::sigaddset(&unblock_mask, SIGTSTP);
        ::sigprocmask(SIG_UNBLOCK, &unblock_mask, nullptr);

        ::raise(SIGTSTP);

        sa.sa_handler = tstp_handler;
        ::sigaction(SIGTSTP, &sa, nullptr);
        errno = saved_errno;
    }

    static void cont_handler(int signo) noexcept {
        (void)signo;
        int saved_errno = errno;
        if (s_active_instance != nullptr) {
            s_active_instance->enable_raw();
        }
        errno = saved_errno;
    }

    static void setup_signals() {
        struct sigaction sa{};
        sa.sa_handler = signal_handler;
        ::sigemptyset(&sa.sa_mask);
        sa.sa_flags = 0;

        constexpr std::array<int, 4> fatal_signals = { SIGINT, SIGTERM, SIGHUP, SIGQUIT };
        for (int sig : fatal_signals) {
            if (::sigaction(sig, &sa, nullptr) < 0) {
                throw std::system_error(errno, std::generic_category(), "sigaction failed");
            }
        }

        sa.sa_handler = tstp_handler;
        if (::sigaction(SIGTSTP, &sa, nullptr) < 0) {
            throw std::system_error(errno, std::generic_category(), "sigaction SIGTSTP failed");
        }

        sa.sa_handler = cont_handler;
        if (::sigaction(SIGCONT, &sa, nullptr) < 0) {
            throw std::system_error(errno, std::generic_category(), "sigaction SIGCONT failed");
        }
    }
};

} // namespace tty

int main() {
    try {
        tty::TerminalGuard term_guard;

        std::string_view intro = "C++ RAII термінал активовано. Натисніть 'q' для виходу або Ctrl+Z для перевірки:\r\n";
        ::write(STDOUT_FILENO, intro.data(), intro.size());

        unsigned char ch = 0;
        while (true) {
            ssize_t n = ::read(STDIN_FILENO, &ch, 1);
            if (n < 0) {
                if (errno == EINTR) {
                    continue;
                }
                break;
            }
            if (n == 0) {
                break;
            }

            if (ch == 'q') {
                std::string_view exit_msg = "\r\nВихід за запитом користувача.\r\n";
                ::write(STDOUT_FILENO, exit_msg.data(), exit_msg.size());
                break;
            }

            std::string out = "Отримано байт: 0x" + std::to_string(static_cast<int>(ch)) + "\r\n";
            ::write(STDOUT_FILENO, out.data(), out.size());
        }
    } catch (const std::exception& ex) {
        std::cerr << "Виняток: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## Детальний розбір реалізації та пасток виконання

1. **Координація сигналів та екземпляра класу в C++:**
   Статичний покажчик `s_active_instance` пов'язує C-сумісний сигнальний обробник `signal_handler` із живим об'єктом `TerminalGuard`. Оскільки зміна покажчика відбувається в головному потоці під час створення та знищення об'єкта, а сигнал доставляється в контексті цього ж потоку, гонки даних між потоками відсутні. Під час розвантаження об'єкта покажчик обнуляється, запобігаючи використанню повислого посилання.

2. **Збереження та відновлення змінної errno:**
   Системний виклик `tcsetattr()`, здійснений всередині сигнального обробника, у разі помилки може перезаписати глобальну змінну `errno`. Якщо в момент приходу сигналу основний потік програми щойно отримав помилку у системному виклику (наприклад, `EAGAIN` у `poll`), незбережений `errno` призведе до спотворення стану основного циклу. Локальна змінна `saved_errno` гарантує відновлення точного значення помилки перед виходом з обробника.

3. **Коректне призупинення через raise(SIGTSTP):**
   Поширена помилка початківців — обробляти `SIGTSTP` без повторної відправки сигналу ядра. Якщо просто скинути налаштування термінала й вийти з обробника, процес продовжить виконуватися. Якщо викликати `pause()`, процес перейде у стан нескінченного сну, але оболонка не дізнається про зупинку завдання і не виведе командне запрошення. Єдиний стандартизований шлях — відновити `SIG_DFL`, зняти маску блокування сигналу через `sigprocmask()` і викликати `raise(SIGTSTP)`. Ядро зафіксує перехід процесу в стан `TASK_STOPPED`, надішле батьківській оболонці сповіщення `SIGCHLD` і поверне користувачеві керування терміналом.

4. **Компіляція та перевірка:**
   Обидва файли компілюються стандартними компіляторами GCC або Clang з максимальним рівнем попереджень без жодних додаткових прапорців лінкування:

```bash
# Компіляція версії мовою C
gcc -Wall -Wextra -pedantic -std=c11 safe_terminal.c -o safe_terminal_c

# Компіляція версії мовою C++
g++ -Wall -Wextra -pedantic -std=c++20 safe_terminal.cpp -o safe_terminal_cpp
```

## Покроковий протокол перевірки та тестування

Для верифікації надійності створеного модуля рекомендується провести чотири контрольні тести в окремій термінальній сесії:

1. **Тест штатного виходу:** Запустіть скомпільовану програму, введіть кілька довільних символів і натисніть клавішу `q`. Переконайтеся, що після завершення програми прапорці `stty -a` показують `echo` та `icanon`.
2. **Тест переривання сигналом `SIGINT` (`Ctrl+C`):** Запустіть програму та надішліть сигнал `SIGINT` (або виконайте `kill -INT <pid>` із сусідньої консолі). Програма повинна миттєво завершитися, а оболонка повинна залишитися у повністю робочому стані з активним відлунням.
3. **Тест фонування через `Ctrl+Z`:** Запустіть програму та натисніть `Ctrl+Z`. Оболонка повинна вивести повідомлення про зупинку завдання `[1]+ Stopped`. Наберіть будь-яку команду в оболонці (наприклад, `ls`) — відлуння та переведення рядків мають працювати бездоганно. Після цього введіть команду `fg` — програма повинна повернутися у сирий режим і продовжити зчитувати поодинокі байти.
4. **Тест раптового закриття емулятора (`SIGHUP`):** Запустіть програму всередині мультиплексора `tmux` або вкладки емулятора та примусово закрийте вікно. Перевірте через системний журнал або інший термінал, що процес коректно перехопив `SIGHUP`, відновив дескриптор і не залишив завислих зомбі-сесій.
