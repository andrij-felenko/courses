# ⚙️ Дослідник середовища без термінала: від перевірки `isatty()` до безпечного введення пароля

Коли фоновий процес у cron, системний сервіс або автоматизований крок у CI/CD раптово аварійно завершується під час спроби прочитати пароль чи токен доступу, проблема зазвичай полягає в наївній роботі з терміналом. Типові утиліти відкривають файл `/dev/tty`, очікуючи прямого зв'язку з людиною за клавіатурою, але в середовищі без керуючого термінала системний виклик `open()` негайно повертає помилку `ENXIO: No such device or address`.

У цьому практичному проекті розроблено повнофункціональну інженерну утиліту `headless_probe`. Вона призначена для глибокої діагностики термінального контексту, інспекції структур ядра, аналізу режимів буферизації та безпечного зчитування секретних даних у будь-якому середовищі виконання.

## Архітектура та інженерні задачі утиліти

Розробка надійних фонових утиліт вимагає чіткого розмежування інтерактивного та автоматизованого режимів роботи. Програма `headless_probe` реалізує комплексну перевірку стану середовища, розв'язуючи п'ять ключових задач:

1. **Подескрипторна інспекція стандартних потоків:** За допомогою бібліотечного виклику `isatty(3)` утиліта окремо перевіряє стан дескрипторів `0` (`stdin`), `1` (`stdout`) та `2` (`stderr`). Це дозволяє точно зафіксувати асиметричні конфігурації, коли вхідний потік перенаправлено з файлу чи каналу, але вивід помилок залишається на терміналі.
2. **Низькорівневий аналіз ядра через `/proc/self/stat`:** Програма парсить сьоме числове поле (`tty_nr`) псевдофайлу `/proc/self/stat`. Це число безпосередньо відображає поле `signal->tty` у структурі `task_struct` ядра Linux. Значення `0` однозначно доводить, що процес від'єднано від керуючого термінала на рівні ядра, тоді як будь-яке додатне значення вказує на старший і молодший номери прив'язаного символьного пристрою.
3. **Пряме зондування точки доступу `/dev/tty`:** Програма виконує тестове відкриття файлу `/dev/tty`. При цьому використовуються обов'язкові системні прапорці `O_NOCTTY` (щоб лідер сеансу випадково не захопив термінал на системах із семантикою System V) та `O_CLOEXEC` (щоб дескриптор автоматично закривався при викликах `execve`).
4. **Адаптивний збір секретних даних:** Реалізовано стійкий алгоритм отримання пароля або токена. Якщо термінал доступний, утиліта тимчасово відключає прапорець `ECHO` у структурі `termios`, зчитує пароль без відображення символів на екрані та скидає буфер за допомогою `TCSAFLUSH`. Якщо ж системний виклик `open("/dev/tty")` повертає помилку `ENXIO`, функція не завершується аварійно, а здійснює плавний автоматичний перехід (*fallback*) на читання з конвеєра `stdin`.
5. **Захист від застрягання діагностичних журналів:** Першою ж дією у функції `main` програма примусово перемикає стандартний вивід у режим лінійної буферизації (`_IOLBF`) через `setvbuf(3)`. Це гарантує, що під час роботи всередині конвеєрів, Docker чи юнітів systemd кожен рядок логу відправлятиметься в системний виклик `write()` негайно після появи символу `\n`.

## Особливості реалізації та парсингу `/proc`

Під час читання `/proc/self/stat` виникає відома пастка: друге поле файлу містить назву виконуваного файлу в круглих дужках (наприклад, `1234 (my daemon) S ...`). Оскільки назва програми може містити довільні пробіли та круглі дужки, просте використання `scanf("%d %s ...")` призводить до зсуву колонок і хибного результату.

Утиліта використовує надійний алгоритм:
1. Зчитує вміст `/proc/self/stat` у локальний буфер фіксованого розміру через прямий системний виклик `read(2)`.
2. Знаходить **останнє** входження символу закриваючої дужки `)` за допомогою функції `strrchr()`.
3. Парсить числові поля (стан процесу, `ppid`, `pgrp`, `session`, `tty_nr`), починаючи з позиції одразу за знайденою дужкою. Це гарантує коректне вилучення `tty_nr` навіть для процесів із нестандартними назвами або скриптів інтерпретаторів.

## Робота з термінальними атрибутами termios

Для безпечного введення паролів недостатньо просто прочитати рядок. Інтерактивний термінал за замовчуванням працює в режимі «луни» (*echoing*), коли кожен натиснутий символ негайно відправляється назад на екран.

Утиліта виконує захищений протокол взаємодії:
- Отримує поточну конфігурацію лінії викликом `tcgetattr()`.
- Створює модифіковану копію структури, скидаючи біт `ECHO` у полі локальних прапорців `c_lflag`.
- Застосовує зміни дією `TCSAFLUSH`, яка чекає завершення передачі всіх вихідних даних і скидає всі незчитані вхідні символи в буфері драйвера TTY.
- Після зчитування рядка функція гарантовано відновлює початкові атрибути термінала, щоб термінал користувача не залишився в «засліпленому» стані після завершення програми.

У версії на C++20 ручне керування дескрипторами замінено на RAII-обгортку `UniqueFd`, а коди помилок повертаються через сучасний шаблон `std::expected` замість магічних чисел, що виключає витоки ресурсів та ігнорування системних помилок.

## Повний джерельний код мовами C та C++20

:::tabs
```c
/* headless_probe.c
   cc -std=c11 -D_GNU_SOURCE -Wall -Wextra -o headless_probe headless_probe.c */

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>

/* Структура звіту про стан термінального контексту */
struct terminal_status {
    int stdin_is_tty;
    int stdout_is_tty;
    int stderr_is_tty;
    int dev_tty_fd;
    int dev_tty_errno;
    int kernel_tty_nr;
};

/* Читання поля tty_nr (7-ме поле) з /proc/self/stat */
static int read_kernel_tty_nr(void)
{
    int fd = open("/proc/self/stat", O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        return -1;
    }

    char buf[512];
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);

    if (n <= 0) {
        return -1;
    }
    buf[n] = '\0';

    /* Пропускаємо PID та назву програми у дужках (наприклад: "12345 (bash) S ...") */
    char *rparen = strrchr(buf, ')');
    if (!rparen) {
        return -1;
    }

    char state;
    int ppid, pgrp, session, tty_nr = 0;
    if (sscanf(rparen + 1, " %c %d %d %d %d", &state, &ppid, &pgrp, &session, &tty_nr) != 5) {
        return -1;
    }

    return tty_nr;
}

/* Збір повної діагностики середовища */
static struct terminal_status inspect_environment(void)
{
    struct terminal_status st;
    st.stdin_is_tty = isatty(STDIN_FILENO);
    st.stdout_is_tty = isatty(STDOUT_FILENO);
    st.stderr_is_tty = isatty(STDERR_FILENO);
    st.kernel_tty_nr = read_kernel_tty_nr();

    /* Спроба відкрити керуючий термінал процесу */
    st.dev_tty_fd = open("/dev/tty", O_RDWR | O_NOCTTY | O_CLOEXEC);
    if (st.dev_tty_fd < 0) {
        st.dev_tty_errno = errno;
    } else {
        st.dev_tty_errno = 0;
    }

    return st;
}

/* Безпечне читання пароля з вимкненням луни (якщо доступний TTY)
   або читання з stdin у неінтерактивному режимі */
static int read_secret_safe(char *buf, size_t max_len, const char *prompt)
{
    int tty_fd = open("/dev/tty", O_RDWR | O_NOCTTY | O_CLOEXEC);

    if (tty_fd >= 0) {
        /* Інтерактивний шлях: є прямий зв'язок з терміналом */
        struct termios orig_termios, raw_termios;
        tcgetattr(tty_fd, &orig_termios);
        raw_termios = orig_termios;
        raw_termios.c_lflag &= ~(ECHO); /* Вимикаємо відображення символів */

        tcsetattr(tty_fd, TCSAFLUSH, &raw_termios);
        dprintf(tty_fd, "%s", prompt);

        char *res = fgets(buf, (int)max_len, fdopen(tty_fd, "r"));
        tcsetattr(tty_fd, TCSAFLUSH, &orig_termios);
        dprintf(tty_fd, "\n");
        close(tty_fd);

        if (!res) {
            return -1;
        }
    } else if (errno == ENXIO || errno == ENOENT || errno == ENODEV) {
        /* Неінтерактивний шлях (headless): читаємо з пайпу stdin */
        fprintf(stderr, "[headless] Термінала немає (/dev/tty: %s). Читаємо секрет зі stdin...\n",
                strerror(errno));
        if (!fgets(buf, (int)max_len, stdin)) {
            return -1;
        }
    } else {
        perror("open(/dev/tty)");
        return -1;
    }

    /* Прибираємо символ нового рядка наприкінці */
    size_t len = strlen(buf);
    if (len > 0 && buf[len - 1] == '\n') {
        buf[len - 1] = '\0';
    }

    return 0;
}

int main(void)
{
    /* Запобігаємо зависанню логів: перемикаємо stdout на лінійну буферизацію */
    setvbuf(stdout, NULL, _IOLBF, 0);

    struct terminal_status st = inspect_environment();

    printf("=== ДІАГНОСТИКА ТЕРМІНАЛЬНОГО КОНТЕКСТУ ===\n");
    printf("STDIN  (fd 0) isatty: %s\n", st.stdin_is_tty ? "ТАК (термінал)" : "НІ (пайп/файл/null)");
    printf("STDOUT (fd 1) isatty: %s\n", st.stdout_is_tty ? "ТАК (термінал)" : "НІ (пайп/файл/null)");
    printf("STDERR (fd 2) isatty: %s\n", st.stderr_is_tty ? "ТАК (термінал)" : "НІ (пайп/файл/null)");
    printf("Ядро (proc stat tty_nr): %d %s\n",
           st.kernel_tty_nr,
           st.kernel_tty_nr == 0 ? "(керуючий термінал ВІДСУТНІЙ)" : "(прив'язаний до пристрою)");

    if (st.dev_tty_fd >= 0) {
        printf("open(\"/dev/tty\"): УСПІХ (отримано fd %d)\n", st.dev_tty_fd);
        close(st.dev_tty_fd);
    } else {
        printf("open(\"/dev/tty\"): ПОМИЛКА errno=%d (%s)\n",
               st.dev_tty_errno, strerror(st.dev_tty_errno));
        if (st.dev_tty_errno == ENXIO) {
            printf("  -> Підтверджено ENXIO: процес виконується у фоні / без сеансу TTY.\n");
        }
    }

    printf("\n--- ТЕСТ ВВЕДЕННЯ ПАРОЛЯ ---\n");
    char secret[64] = {0};
    if (read_secret_safe(secret, sizeof(secret), "Введіть пароль: ") == 0) {
        printf("Секрет успішно отримано (довжина: %zu байтів).\n", strlen(secret));
    } else {
        fprintf(stderr, "Помилка читання секрету!\n");
        return 1;
    }

    return 0;
}
```
```cpp
// headless_probe.cpp
// g++ -std=c++20 -Wall -Wextra -o headless_probe headless_probe.cpp

#include <array>
#include <cerrno>
#include <cstring>
#include <expected>
#include <fcntl.h>
#include <fstream>
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <system_error>
#include <termios.h>
#include <unistd.h>

namespace sys {

// RAII обгортка для володіння файловим дескриптором
class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_{-1} {}
    explicit UniqueFd(int fd) noexcept : fd_{fd} {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }

    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    explicit operator bool() const noexcept { return valid(); }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_;
};

struct TerminalStatus {
    bool stdin_is_tty{false};
    bool stdout_is_tty{false};
    bool stderr_is_tty{false};
    int kernel_tty_nr{0};
    bool dev_tty_accessible{false};
    int dev_tty_error{0};
};

// Читання tty_nr з /proc/self/stat
[[nodiscard]] std::expected<int, std::error_code> get_kernel_tty_nr() {
    std::ifstream stat_file("/proc/self/stat");
    if (!stat_file.is_open()) {
        return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
    }

    std::string line;
    if (!std::getline(stat_file, line)) {
        return std::unexpected(std::make_error_code(std::errc::io_error));
    }

    const auto rparen = line.rfind(')');
    if (rparen == std::string::npos || rparen + 2 >= line.size()) {
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));
    }

    std::string_view rest{line.data() + rparen + 2, line.size() - (rparen + 2)};
    char state{};
    int ppid{}, pgrp{}, session{}, tty_nr{};
    if (sscanf(rest.data(), "%c %d %d %d %d", &state, &ppid, &pgrp, &session, &tty_nr) != 5) {
        return std::unexpected(std::make_error_code(std::errc::protocol_error));
    }

    return tty_nr;
}

// Повний аудит контексту виконання
[[nodiscard]] TerminalStatus inspect_environment() {
    TerminalStatus status;
    status.stdin_is_tty = (::isatty(STDIN_FILENO) == 1);
    status.stdout_is_tty = (::isatty(STDOUT_FILENO) == 1);
    status.stderr_is_tty = (::isatty(STDERR_FILENO) == 1);

    auto tty_res = get_kernel_tty_nr();
    status.kernel_tty_nr = tty_res.value_or(-1);

    UniqueFd tty_fd{::open("/dev/tty", O_RDWR | O_NOCTTY | O_CLOEXEC)};
    if (tty_fd) {
        status.dev_tty_accessible = true;
        status.dev_tty_error = 0;
    } else {
        status.dev_tty_accessible = false;
        status.dev_tty_error = errno;
    }

    return status;
}

// Безпечне отримання пароля
[[nodiscard]] std::expected<std::string, std::error_code>
read_secret_safe(std::string_view prompt) {
    UniqueFd tty_fd{::open("/dev/tty", O_RDWR | O_NOCTTY | O_CLOEXEC)};

    if (tty_fd) {
        // Інтерактивний термінал доступний
        struct termios orig_termios{}, raw_termios{};
        ::tcgetattr(tty_fd.get(), &orig_termios);
        raw_termios = orig_termios;
        raw_termios.c_lflag &= ~static_cast<tcflag_t>(ECHO);

        ::tcsetattr(tty_fd.get(), TCSAFLUSH, &raw_termios);
        ::dprintf(tty_fd.get(), "%.*s", static_cast<int>(prompt.size()), prompt.data());

        std::array<char, 256> buf{};
        FILE* fp = ::fdopen(tty_fd.get(), "r");
        char* res = fp ? ::fgets(buf.data(), static_cast<int>(buf.size()), fp) : nullptr;

        ::tcsetattr(tty_fd.get(), TCSAFLUSH, &orig_termios);
        ::dprintf(tty_fd.get(), "\n");

        if (!res) {
            return std::unexpected(std::make_error_code(std::errc::io_error));
        }

        std::string secret{buf.data()};
        if (!secret.empty() && secret.back() == '\n') {
            secret.pop_back();
        }
        return secret;
    }

    if (errno == ENXIO || errno == ENOENT || errno == ENODEV) {
        // Headless режим: безпечний fallback на стандартний ввід
        std::cerr << "[headless] /dev/tty недоступний (" << std::strerror(errno)
                  << "). Читаємо секрет зі stdin...\n";
        std::string secret;
        if (!std::getline(std::cin, secret)) {
            return std::unexpected(std::make_error_code(std::errc::io_error));
        }
        return secret;
    }

    return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
}

} // namespace sys

int main() {
    // Вмикаємо лінійну буферизацію для уникнення застрягання логів у пайпах
    ::setvbuf(stdout, nullptr, _IOLBF, 0);

    const auto status = sys::inspect_environment();

    std::cout << "=== ДІАГНОСТИКА ТЕРМІНАЛЬНОГО КОНТЕКСТУ (C++20) ===\n";
    std::cout << "STDIN  isatty: " << (status.stdin_is_tty ? "ТАК" : "НІ") << "\n";
    std::cout << "STDOUT isatty: " << (status.stdout_is_tty ? "ТАК" : "НІ") << "\n";
    std::cout << "STDERR isatty: " << (status.stderr_is_tty ? "ТАК" : "НІ") << "\n";
    std::cout << "Kernel tty_nr: " << status.kernel_tty_nr
              << (status.kernel_tty_nr == 0 ? " (керуючий термінал ВІДСУТНІЙ)" : "") << "\n";

    if (status.dev_tty_accessible) {
        std::cout << "open(\"/dev/tty\"): УСПІХ\n";
    } else {
        std::cout << "open(\"/dev/tty\"): ПОМИЛКА " << status.dev_tty_error << " ("
                  << std::strerror(status.dev_tty_error) << ")\n";
        if (status.dev_tty_error == ENXIO) {
            std::cout << "  -> ENXIO: гарантовано неінтерактивне середовище.\n";
        }
    }

    std::cout << "\n--- ТЕСТ ВВЕДЕННЯ ПАРОЛЯ ---\n";
    auto secret = sys::read_secret_safe("Введіть токен доступу: ");
    if (secret) {
        std::cout << "Секрет успішно зчитано! Довжина: " << secret->size() << " байтів.\n";
    } else {
        std::cerr << "Помилка читання секрету: " << secret.error().message() << "\n";
        return 1;
    }

    return 0;
}
```
:::

## Покроковий розбір поведінки у різних середовищах

Щоб наочно побачити відмінності в поведінці ядра, протестуємо зібрану утиліту в трьох типових сценаріях експлуатації:

### Сценарій 1: Інтерактивний виклик у сеансі користувача
Під час звичайного запуску в терміналі всі три стандартні дескриптори вказують на псевдотермінал `/dev/pts/X`. Поле `tty_nr` містить ненульове число, а відкриття `/dev/tty` проходить успішно. Утиліта відключає ехо й запитує пароль у користувача.

```console
$ ./headless_probe
=== ДІАГНОСТИКА ТЕРМІНАЛЬНОГО КОНТЕКСТУ ===
STDIN  (fd 0) isatty: ТАК (термінал)
STDOUT (fd 1) isatty: ТАК (термінал)
STDERR (fd 2) isatty: ТАК (термінал)
Ядро (proc stat tty_nr): 34820 (прив'язаний до пристрою)
open("/dev/tty"): УСПІХ (отримано fd 3)

--- ТЕСТ ВВЕДЕННЯ ПАРОЛЯ ---
Введіть пароль: 
Секрет успішно отримано (довжина: 12 байтів).
```

### Сценарій 2: Виклик у конвеєрі (емуляція неповного перенаправлення)
Якщо програма працює всередині конвеєра (`cat data | ./headless_probe | cat`), дескриптори `0` і `1` перетворюються на анонімні канали (`pipe`), тому `isatty()` для них повертає `0`. Проте процес усе ще залишається у сеансі термінала, тому `kernel_tty_nr` ненульовий, а відкриття `/dev/tty` залишається успішним.

```console
$ echo "secret123" | ./headless_probe | cat
=== ДІАГНОСТИКА ТЕРМІНАЛЬНОГО КОНТЕКСТУ ===
STDIN  (fd 0) isatty: НІ (пайп/файл/null)
STDOUT (fd 1) isatty: НІ (пайп/файл/null)
STDERR (fd 2) isatty: ТАК (термінал)
Ядро (proc stat tty_nr): 34820 (прив'язаний до пристрою)
open("/dev/tty"): УСПІХ (отримано fd 3)
```

### Сценарій 3: Справжнє безтермінальне середовище (setsid / cron / systemd)
Якщо запустити утиліту через системну команду `setsid`, процес буде ізольовано в новому сеансі без керуючого термінала. Значення `tty_nr` у ядрі стає рівним `0`. Спроба відкрити `/dev/tty` негайно повертає код помилки `ENXIO`, активуючи резервний механізм читання секрету зі стандартного вводу без аварійного завершення програми.

```console
$ echo "my_api_key" | setsid ./headless_probe
=== ДІАГНОСТИКА ТЕРМІНАЛЬНОГО КОНТЕКСТУ ===
STDIN  (fd 0) isatty: НІ (пайп/файл/null)
STDOUT (fd 1) isatty: НІ (пайп/файл/null)
STDERR (fd 2) isatty: НІ (пайп/файл/null)
Ядро (proc stat tty_nr): 0 (керуючий термінал ВІДСУТНІЙ)
open("/dev/tty"): ПОМИЛКА errno=6 (No such device or address)
  -> Підтверджено ENXIO: процес виконується у фоні / без сеансу TTY.

--- ТЕСТ ВВЕДЕННЯ ПАРОЛЯ ---
[headless] Термінала немає (/dev/tty: No such device or address). Читаємо секрет зі stdin...
Секрет успішно отримано (довжина: 10 байтів).
```
