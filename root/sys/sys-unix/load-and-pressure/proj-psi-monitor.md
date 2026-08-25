# ⚙️ Демон очікування ресурсів на базі PSI та epoll

Уставку присвячено створенню високопродуктивного системного демона моніторингу тиску на оперативну пам'ять та дискову підсистему Linux за допомогою тригерів PSI та подійного циклу `epoll()`.

## 1. Архітектура та принцип роботи демона

Традиційні моніторингові утиліти опитують метрики ядра (polling) з інтервалом в 1, 5 або 10 секунд. Такий підхід створює два фундаментальних дефекти у системній архітектурі моніторингу:
1. **Невиправдані накладні витрати**: постійний виклик `cat` або читання псевдофайлів `/proc/` даремно витрачає ресурси процесора та переключає контекст користувач/ядро навіть тоді, коли в системі все спокійно.
2. **Неможливість виявити короткочасні сплески (сліпа пляма)**: короткочасний сплеск тиску ресурсу (наприклад, 100 мс деструктивного голодування RAM під час пікового навантаження) буде повністю пропущений між періодичними викликами опитування.

Демон реального часу використовує подієву модель PSI. Він реєструє пороговий тригер у ядрі через спеціальний виклик `write()`, після чого засинає в системному виклику `epoll_wait()`. Ядро Linux розбудить процес лише тоді, коли накопичена затримка виконання процесів перевищить заданий поріг усередині вікна спостереження.

## 2. Механізм взаємодії з VFS та обробка подій

Процес реєстрації тригера PSI складається з трьох послідовних кроків:
1. **Відкриття файлового дескриптора**: процес відкриває відповідний вузол (наприклад, `/proc/pressure/memory` або `/sys/fs/cgroup/system.slice/memory.pressure`) у режимі `O_RDWR` або `O_WRONLY`.
2. **Запис специфікації тригера**: через системний виклик `write()` ядру передається рядок виду `"some 150000 1000000"`, де `150000` — поріг голодування у мікросекундах (150 мс), а `1000000` — розмір рухомого вікна (1 секунда).
3. **Реєстрація в подійному циклі epoll**: відкритий файловий дескриптор додається до контексту `epoll` із маскою подій **`EPOLLPRI`** (події високого пріоритету).

Коли ядро фіксує перевищення порогу затримок, воно пробуджує всі процеси, заблоковані у `epoll_wait()`. Після цього демон може зчитати поточні метрики тиску або підключити автоматичний сценарій реагування (наприклад, скидання внутрішнього кешу програми, призупинення другорядних фонових задач або виклику OOM killer для завислої контрольної групи).

## 3. Реалізація демона у мовах C та C++

Нижче наведено повністю робочий код демона. У вкладці **C** застосовано класичний процедурний підхід POSIX із прямими системними викликами, явним звільненням ресурсів та перевіркою кодів помилок. У вкладці **C++** реалізовано сучасні ідіоми C++20: концепцію RAII (Resource Acquisition Is Initialization) для автоматичного управління файловими дескрипторами, `std::string_view`, шаблони та обробку винятків.

:::tabs
```c
/* psi_monitor.c — Демон спостереження за тиском пам'яті на C (POSIX) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/epoll.h>
#include <sys/types.h>

#define MAX_EVENTS 8
#define BUFFER_SIZE 256

/* Налаштування тригера: 150 мс затримки в 1-секундному вікні */
static const char *TRIGGER_SPEC = "some 150000 1000000";
static const char *PRESSURE_PATH = "/proc/pressure/memory";

static int setup_psi_trigger(const char *path, const char *spec) {
    int fd = open(path, O_RDWR | O_CLOEXEC);
    if (fd < 0) {
        perror("Помилка відкриття вузла PSI");
        return -1;
    }

    ssize_t written = write(fd, spec, strlen(spec));
    if (written < 0) {
        perror("Помилка реєстрації тригера PSI");
        close(fd);
        return -1;
    }

    return fd;
}

static void read_current_pressure(const char *path) {
    int fd = open(path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) return;

    char buf[BUFFER_SIZE];
    ssize_t bytes = read(fd, buf, sizeof(buf) - 1);
    if (bytes > 0) {
        buf[bytes] = '\0';
        printf("--- Поточні метрики тиску ---\n%s-----------------------------\n", buf);
    }
    close(fd);
}

int main(void) {
    printf("[PSI Monitor] Запуск демона спостереження...\n");

    int psi_fd = setup_psi_trigger(PRESSURE_PATH, TRIGGER_SPEC);
    if (psi_fd < 0) {
        fprintf(stderr, "Критична помилка: не вдалося налаштувати PSI тригер.\n");
        return EXIT_FAILURE;
    }

    int epoll_fd = epoll_create1(EPOLL_CLOEXEC);
    if (epoll_fd < 0) {
        perror("Помилка створення epoll");
        close(psi_fd);
        return EXIT_FAILURE;
    }

    struct epoll_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.events = EPOLLPRI; // Враховуємо лише події підвищеного пріоритету (PSI trigger)
    ev.data.fd = psi_fd;

    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, psi_fd, &ev) < 0) {
        perror("Помилка додавання fd до epoll");
        close(epoll_fd);
        close(psi_fd);
        return EXIT_FAILURE;
    }

    printf("[PSI Monitor] Тригер успішно встановлено: \"%s\" для %s\n", TRIGGER_SPEC, PRESSURE_PATH);
    printf("[PSI Monitor] Очікування подій тиску...\n");

    struct epoll_event events[MAX_EVENTS];
    int running = 1;
    int alert_count = 0;

    while (running) {
        int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, -1);
        if (nfds < 0) {
            if (errno == EINTR) continue;
            perror("Помилка epoll_wait");
            break;
        }

        for (int i = 0; i < nfds; ++i) {
            if (events[i].data.fd == psi_fd && (events[i].events & EPOLLPRI)) {
                alert_count++;
                printf("\n⚠️  [СПЛЕКСТ ТИСКУ #%d] Тригер PSI спрацював! Пам'ять зазнає затримок!\n", alert_count);
                read_current_pressure(PRESSURE_PATH);
            }
        }
    }

    close(epoll_fd);
    close(psi_fd);
    return EXIT_SUCCESS;
}
```
```cpp
// psi_monitor.cpp — Демон спостереження за тиском пам'яті на C++20 (RAII)
#include <iostream>
#include <string>
#include <string_view>
#include <array>
#include <system_error>
#include <stdexcept>
#include <utility>
#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>

namespace sys {

// RAII-обгортка для безпечного управління файловими дескрипторами
class unique_fd {
    int m_fd{-1};

public:
    constexpr unique_fd() noexcept = default;
    explicit unique_fd(int fd) noexcept : m_fd(fd) {}
    ~unique_fd() { reset(); }

    unique_fd(const unique_fd&) = delete;
    unique_fd& operator=(const unique_fd&) = delete;

    unique_fd(unique_fd&& other) noexcept : m_fd(std::exchange(other.m_fd, -1)) {}
    unique_fd& operator=(unique_fd&& other) noexcept {
        if (this != &other) {
            reset();
            m_fd = std::exchange(other.m_fd, -1);
        }
        return *this;
    }

    void reset(int new_fd = -1) noexcept {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
        m_fd = new_fd;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }
};

} // namespace sys

class psi_monitor {
    static constexpr std::string_view TRIGGER_SPEC = "some 150000 1000000";
    static constexpr std::string_view PRESSURE_PATH = "/proc/pressure/memory";

    sys::unique_fd m_psi_fd;
    sys::unique_fd m_epoll_fd;

public:
    psi_monitor() {
        int fd = ::open(PRESSURE_PATH.data(), O_RDWR | O_CLOEXEC);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити вузол PSI");
        }
        m_psi_fd.reset(fd);

        ssize_t written = ::write(m_psi_fd.get(), TRIGGER_SPEC.data(), TRIGGER_SPEC.size());
        if (written < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося зареєструвати тригер PSI");
        }

        int efd = ::epoll_create1(EPOLL_CLOEXEC);
        if (efd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося створити epoll instance");
        }
        m_epoll_fd.reset(efd);

        epoll_event ev{};
        ev.events = EPOLLPRI;
        ev.data.fd = m_psi_fd.get();

        if (::epoll_ctl(m_epoll_fd.get(), EPOLL_CTL_ADD, m_psi_fd.get(), &ev) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка додавання fd до epoll");
        }
    }

    void run() {
        std::cout << "[PSI Monitor C++] Тригер активовано: " << TRIGGER_SPEC << '\n';
        std::cout << "[PSI Monitor C++] Очікування на події тиску...\n";

        std::array<epoll_event, 8> events{};
        size_t alerts = 0;

        while (true) {
            int nfds = ::epoll_wait(m_epoll_fd.get(), events.data(), static_cast<int>(events.size()), -1);
            if (nfds < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "Помилка epoll_wait");
            }

            for (int i = 0; i < nfds; ++i) {
                if (events[i].data.fd == m_psi_fd.get() && (events[i].events & EPOLLPRI)) {
                    alerts++;
                    std::cout << "\n⚠️  [СПЛЕКСТ ТИСКУ #" << alerts << "] Сигнал тригера PSI! Аналіз пам'яті...\n";
                    print_metrics();
                }
            }
        }
    }

private:
    void print_metrics() const {
        sys::unique_fd fd(::open(PRESSURE_PATH.data(), O_RDONLY | O_CLOEXEC));
        if (!fd.valid()) return;

        std::array<char, 256> buf{};
        ssize_t bytes = ::read(fd.get(), buf.data(), buf.size() - 1);
        if (bytes > 0) {
            buf[bytes] = '\0';
            std::cout << "--- Поточний стан тиску ---\n" << buf.data() << "----------------------------\n";
        }
    }
};

int main() {
    try {
        psi_monitor daemon;
        daemon.run();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка демона: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

## 4. Аналіз практичних крайових випадків та пасток

При імплементації тригерів PSI у промислових випускних системах необхідно враховувати декілька системних нюансів:

### 4.1. Автоматичне пригнічення сповіщень (Rate Limiting)
Ядро Linux гарантує, що тригер не буде генерувати події `POLLPRI` частіше ніж один раз за період заданого вікна `window_us`. Якщо поріг 150 мс у 1-секундному вікні перевищено на 200-й мілісекунді, ви отримаєте сповіщення негайно. Однак наступна подія буде згенерована лише після того, як завершиться поточне вікно і розпочнеться нове вікно з новим перевищенням порогу. Це запобігає зацикленню обробника подій та перевантаженню процесора.

### 4.2. Прапорці відношення файлових дескрипторів (O_CLOEXEC)
Оскільки моніторингові демони часто запускають дочірні процеси для ліквідації аварій (наприклад, через виклики `fork()` та `execve()`), усі відкриті дескриптори PSI та epoll повинні мати встановлений прапорець **`O_CLOEXEC`** (або `epoll_create1(EPOLL_CLOEXEC)`). У разі відсутності цього прапорця дочірні процеси успадкують тригерні дескриптори, що призведе до витоку ресурсів та небажаних блокувань VFS.

### 4.3. Обробка помилок при зміні конфігурації cgroup
Якщо ваш демон відстежує тиск ресурсу для конкретного контейнера за шляхом `/sys/fs/cgroup/.../memory.pressure`, при знищенні або перезапуску цього контейнера файловий дескриптор поверне подійну помилку `EPOLLERR` або `EPOLLHUP`. Обробник демона повинен корректно обробляти ці прапорці, видаляти дескриптор із подійного циклу `epoll` та закривати його без паніки програми.

## 5. Промислове застосування: Інтеграція з systemd-oomd

Сучасні системні менеджери, такі як `systemd`, використовують подібну логіку тригерів PSI у демоні `systemd-oomd`. Демон `systemd-oomd` підписується на події `memory.pressure` для кожної cgroup у системі.

Конфігурація `systemd-oomd` у файлі `/etc/systemd/oomd.conf`:
```ini
[OOM]
DefaultMemoryPressureLimit=60%
DefaultMemoryPressureDurationSec=30s
```

Коли cgroup перевищує поріг тиску `DefaultMemoryPressureLimit` протягом тривалості `DefaultMemoryPressureDurationSec`, `systemd-oomd` надсилає сигнал `SIGKILL` до найбільшого процесу всередині цієї cgroup, вилучаючи лише конкретний проблемний контейнер і зберігаючи стабільність решти системи.

## 6. Компіляція, тестування та перевірка демона

### 6.1. Збирання проекту

Для компіляції обох версій використайте стандартний інструментарій GCC / Clang у системі Linux:

```bash
# Компіляція версії на мові C
$ gcc -O2 -Wall -Wextra psi_monitor.c -o psi_monitor_c

# Компіляція версії на мові C++ (потрібна підтримка C++20)
$ g++ -O2 -Wall -Wextra -std=c++20 psi_monitor.cpp -o psi_monitor_cpp
```

### 6.2. Симуляція тиску на оперативну пам'ять

Щоб перевірити роботу демона та викликати спрацьовування тригера PSI, запустіть утиліту `stress-ng` або `stress` у сусідньому терміналі для створення штучного голодування RAM та активного витіснення файлового кешу:

```bash
# Запуск демона в першому терміналі
$ ./psi_monitor_cpp

# Генерація тиску на пам'ять у другому терміналі
$ stress-ng --vm 4 --vm-bytes 80% --timeout 10s
```

Результат виконання демона:
```syslog
[PSI Monitor C++] Тригер активовано: some 150000 1000000
[PSI Monitor C++] Очікування на події тиску...

⚠️  [СПЛЕКСТ ТИСКУ #1] Сигнал тригера PSI! Аналіз пам'яті...
--- Поточний стан тиску ---
some avg10=22.40 avg60=5.10 avg300=1.02 total=4520102
full avg10=11.15 avg60=2.30 avg300=0.45 total=1204890
----------------------------
```

Цей приклад демонструє, як розробники можуть створювати превентивні демони утилізації ресурсів (наприклад, скидання внутрішніх кешів програми при перших ознаках `memory/some`), запобігаючи неконтрольованому завершенню процесів через OOM Killer.
