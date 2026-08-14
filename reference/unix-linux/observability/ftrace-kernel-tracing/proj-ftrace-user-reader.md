# ⚙️ Програма зчитування подій ftrace через tracefs

Кільцевий буфер ftrace (`ftrace ring buffer`) є високопродуктивною підсистемою ядра Linux, яка зберігає бінарні траси функцій та подій у lock-less посторінкових кільцевих структурах даних для кожного процесора (per-CPU). Програмний доступ до цих даних із юзерпростору здійснюється через віртуальну файлову систему `tracefs`, де текстові та бінарні інтерфейси (`trace_pipe` і `trace_pipe_raw`) надають потік подій ядра в реальному часі. Пряме програмне керування цим інтерфейсом мовами C та C++ передбачає послідовне вимкнення запису на час конфігурації, налаштування динамічних фільтрів системних викликів, потокове зчитування блоків подій та суворе відновлення початкового стану ядра за допомогою обробників сигналів `SIGINT`/`SIGTERM` або деструкторів RAII.

## 1. Архітектура юзерпростірного читача та життєвий цикл

Пряма взаємодія з підсистемою ftrace з програм юзерпростору спирається на читання й запис віртуальних файлів `tracefs`. Моніторингова утиліта повинна дотримуватися суворого порядку операцій, щоб уникнути втрати подій або створення надмірних накладних витрат у ядрі.

### Послідовність етапів конфігурації

1. **Перевірка моніторингового середовища:** Перевіряється наявність віртуальної файлової системи `tracefs`, змонтованої за шляхом `/sys/kernel/tracing` або `/sys/kernel/debug/tracing`. Для виконання запису у файли керування програма повинна запускатися з правами суперкористувача (`root`) або мати системну капсулу `CAP_SYS_ADMIN` (чи `CAP_PERFMON` на сучасних версіях ядра Linux).
2. **Тимчасове заниження активності (`tracing_on=0`):** Запис значення `0` у файл `tracing_on` гарантує, що під час зміни трасера та фільтрів кільцевий буфер не буде заповнюватися некоректними чи проміжними подіями, які могли б викривити статистику.
3. **Очищення та налаштування фільтрів:** Очищається вміст файлу `set_ftrace_filter`, після чого у нього записується шаблон імен функцій для моніторингу (наприклад, `do_sys_openat2` для відстеження відкриття файлів у ядрі).
4. **Вибір плагіна трасування:** У файл `current_tracer` записується назва трасера (`function` або `function_graph`).
5. **Активація підсистеми (`tracing_on=1`):** Відновлюється запис подій у кільцевий буфер ядра.
6. **Потокове зчитування:** Відкривається файл `trace_pipe` у режимі тільки для читання (`O_RDONLY`). Програма входить у цикл зчитування даних блок за блоком.
7. **Безпечна деактивація (Clean Teardown):** При отриманні сигналу завершення програма зупиняє запис у буфер, повертає значення `nop` у файл `current_tracer` та очищає фільтри.

### Механіка файлового вводу-виводу та мультиплексування: `trace_pipe` vs `trace_pipe_raw`

При розробці системних утиліт важливо розуміти різницю між текстовими та бінарними файлами зчитування ftrace:
- **Текстовий файл `trace_pipe`:** Надає вже відформатовані ядром текстові рядки. Читання з цього файлу є блокуючою операцією. При виконанні виклику `read()` потік утиліти засинає в очікуванні появи нових подій у кільцевому буфері. Для опитування кількох файлів або підключення до тайм-аутів можна використовувати системні виклики мультиплексування `poll()` або `epoll()`, оскільки дескриптор `trace_pipe` підтримує сигналізацію `POLLIN`.
- **Бінарний файл `per_cpu/cpu*/trace_pipe_raw`:** Використовується високопродуктивними утилітами типу `trace-cmd`. Він віддає сирі бінарні сторінки кільцевого буфера ядра без форматування в текстові рядки, що суттєво зменшує накладні витрати CPU.

### Обробка переривань та системних сигналів

Найнебезпечнішою помилкою при розробці утиліт керування ftrace є некоректне завершення програми (наприклад, через необроблений збій пам'яті або аварійну зупинку користувачем за допомогою Ctrl+C), внаслідок якого трасер функцій залишається увімкненим у ядрі. Це призводить до постійного витрачання ресурсів CPU та накопичення логів у пам'яті.

Щоб запобігти цьому:
- У версії мовою C використовують перехоплення сигналів `SIGINT` та `SIGTERM` через масив `struct sigaction` і атомарний прапорець `volatile sig_atomic_t g_running`. Після виходу з циклу читання програма обов'язково виконує блок `cleanup`.
- У версії мовою C++ застосовують паттерн **RAII (Resource Acquisition Is Initialization)**. Клас `TracefsSession` автоматично гарантує відновлення параметрів ядра у своєму деструкторі — навіть якщо у процесі виконання буде згенеровано виняток `std::exception`.

## 2. Реалізація мовами C та C++

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <errno.h>

#define TRACEFS_PATH "/sys/kernel/tracing"
#define BUF_SIZE 4096

static volatile sig_atomic_t g_running = 1;

static void handle_signal(int sig)
{
    (void)sig;
    g_running = 0;
}

static int write_tracefs(const char *rel_path, const char *val)
{
    char full_path[512];
    snprintf(full_path, sizeof(full_path), "%s/%s", TRACEFS_PATH, rel_path);
    
    int fd = open(full_path, O_WRONLY | O_TRUNC);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", full_path, strerror(errno));
        return -1;
    }
    
    ssize_t len = strlen(val);
    if (write(fd, val, len) != len) {
        fprintf(stderr, "Помилка запису '%s' у %s: %s\n", val, full_path, strerror(errno));
        close(fd);
        return -1;
    }
    
    close(fd);
    return 0;
}

int main(void)
{
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_signal;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    printf("[+] Налаштування ftrace через tracefs...\n");

    /* 1. Вимикаємо трасування на час налаштування */
    if (write_tracefs("tracing_on", "0") < 0) return 1;

    /* 2. Очищаємо попередній фільтр */
    if (write_tracefs("set_ftrace_filter", "") < 0) return 1;

    /* 3. Встановлюємо фільтр на функції відкриття файлів */
    if (write_tracefs("set_ftrace_filter", "do_sys_open*") < 0) return 1;

    /* 4. Активуємо плагін function */
    if (write_tracefs("current_tracer", "function") < 0) return 1;

    /* 5. Увімкаємо трасування */
    if (write_tracefs("tracing_on", "1") < 0) return 1;

    printf("[+] ftrace активовано. Зчитування trace_pipe (Ctrl+C для виходу)...\n");

    char pipe_path[512];
    snprintf(pipe_path, sizeof(pipe_path), "%s/trace_pipe", TRACEFS_PATH);
    int pipe_fd = open(pipe_path, O_RDONLY);
    if (pipe_fd < 0) {
        fprintf(stderr, "Помилка відкриття trace_pipe: %s\n", strerror(errno));
        goto cleanup;
    }

    char buffer[BUF_SIZE];
    while (g_running) {
        ssize_t bytes_read = read(pipe_fd, buffer, sizeof(buffer) - 1);
        if (bytes_read > 0) {
            buffer[bytes_read] = '\0';
            printf("%s", buffer);
            fflush(stdout);
        } else if (bytes_read < 0) {
            if (errno == EINTR) continue;
            fprintf(stderr, "Помилка читання з trace_pipe: %s\n", strerror(errno));
            break;
        }
    }

    close(pipe_fd);

cleanup:
    printf("\n[+] Деактивація ftrace та відновлення стану ядра...\n");
    write_tracefs("tracing_on", "0");
    write_tracefs("current_tracer", "nop");
    write_tracefs("set_ftrace_filter", "");
    printf("[+] Завершено успішно.\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <csignal>
#include <system_error>
#include <memory>
#include <vector>
#include <array>
#include <fcntl.h>
#include <unistd.h>

namespace fs = std::filesystem;

namespace ftrace {

static volatile std::sig_atomic_t g_stop_requested = 0;

void signal_handler(int) {
    g_stop_requested = 1;
}

class TracefsSession {
public:
    explicit TracefsSession(fs::path tracefs_root = "/sys/kernel/tracing")
        : root_path_(std::move(tracefs_root))
    {
        if (!fs::exists(root_path_)) {
            throw std::runtime_error("tracefs не змонтовано за шляхом: " + root_path_.string());
        }
        
        // Зберігаємо початкові налаштування для відновлення в деструкторі (RAII)
        stop_tracing();
        set_file_content("set_ftrace_filter", "");
        set_file_content("set_ftrace_notrace", "");
    }

    ~TracefsSession() noexcept {
        try {
            stop_tracing();
            set_file_content("current_tracer", "nop");
            set_file_content("set_ftrace_filter", "");
            std::cout << "[+] RAII: Ресурси tracefs успішно відновлено.\n";
        } catch (const std::exception& e) {
            std::cerr << "[-] Помилка в деструкторі TracefsSession: " << e.what() << '\n';
        }
    }

    // Заборона копіювання (семантика володіння ресурсом)
    TracefsSession(const TracefsSession&) = delete;
    TracefsSession& operator=(const TracefsSession&) = delete;

    void configure_function_tracer(std::string_view filter_pattern) {
        stop_tracing();
        set_file_content("set_ftrace_filter", filter_pattern);
        set_file_content("current_tracer", "function");
    }

    void start_tracing() {
        set_file_content("tracing_on", "1");
    }

    void stop_tracing() {
        set_file_content("tracing_on", "0");
    }

    void stream_pipe() {
        const auto pipe_path = root_path_ / "trace_pipe";
        int fd = ::open(pipe_path.c_str(), O_RDONLY);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити trace_pipe");
        }

        std::array<char, 4096> buffer{};
        while (!g_stop_requested) {
            ssize_t count = ::read(fd, buffer.data(), buffer.size() - 1);
            if (count > 0) {
                buffer[static_cast<size_t>(count)] = '\0';
                std::cout.write(buffer.data(), count);
                std::cout.flush();
            } else if (count < 0) {
                if (errno == EINTR) continue;
                ::close(fd);
                throw std::system_error(errno, std::generic_category(), "Помилка читання з trace_pipe");
            }
        }
        ::close(fd);
    }

private:
    fs::path root_path_;

    void set_file_content(std::string_view relative_file, std::string_view value) {
        const auto target = root_path_ / relative_file;
        std::ofstream ofs(target);
        if (!ofs.is_open()) {
            throw std::runtime_error("Не вдалося відкрити файл керування: " + target.string());
        }
        ofs << value;
        if (!ofs) {
            throw std::runtime_error("Помилка запису в файл керування: " + target.string());
        }
    }
};

} // namespace ftrace

int main() {
    std::signal(SIGINT, ftrace::signal_handler);
    std::signal(SIGTERM, ftrace::signal_handler);

    try {
        std::cout << "[+] Ініціалізація RAII-сесії ftrace...\n";
        ftrace::TracefsSession session;

        session.configure_function_tracer("do_sys_open*");
        session.start_tracing();

        std::cout << "[+] Моніторинг відкриття файлів через tracefs (Ctrl+C для виходу)...\n";
        session.stream_pipe();

    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка виконання: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

## 3. Глибокий аналіз реалізації та розбір відмінностей

Детальний аналіз двох ідіоматичних реалізацій показує принципові відмінності між підходами мов C та C++ до системного програмування під Linux.

### Управління ресурсами та гарантії виходу

- **Реалізація мовою C:** Використовує процедурну декомпозицію та явну обробку кожної помилки системного виклику (`open`, `write`). Для повернення ядра у початковий стан застосовується перехід за міткою `goto cleanup`. Якщо системний виклик `write()` повертає помилку `EINTR` або `EACCES`, програма переходить до очищення. Недоліком підходу на C є небезпека пропустити виклик очищення при додаванні нових гілок коду.
- **Реалізація мовою C++ (RAII):** Обгортає стан сесії трасування у клас `TracefsSession`. Конструктор класу ініціалізує середовище, а деструктор `~TracefsSession()` несе виключну відповідальність за очищення параметрів ядра (`tracing_on=0`, `current_tracer=nop`). Оскільки деструктори об'єктів із автоматичною тривалістю зберігання викликаються гарантовано при виході з блоку `try` чи генерації винятку, код C++ гарантує відсутність витоків ресурсів трасування у ядрі.

### Безпека маніпуляцій зі шляхами та файловий ввід-вивід

- **Робота зі шляхами у C:** Спирається на символьні масиви фіксованого розміру (`char full_path[512]`) та функції форматування `snprintf`. Це створює ризик переповнення буфера або відсікання довгих шляхів, якщо файлова система `tracefs` змонтована за нестандартною адресою.
- **Робота зі шляхами у C++:** Застосовує тип `std::filesystem::path`, який атомарно обробляє роздільники шляхів та перевіряє існування каталогу за допомогою `std::filesystem::exists()`. Для передачі аргументів без створення тимчасових копій рядків у пам'яті використовується тип `std::string_view`.

### Обробка помилок та системних сигналів

Обидві утиліти встановлюють обробники сигналів `SIGINT` та `SIGTERM`. Сигнальний обробник перемикає прапорець `g_stop_requested`, що призводить до безпечного завершення циклу `read()` на файловому дескрипторі `trace_pipe`. У варіанті на C++ виклики функцій стандарту POSIX (`open`, `read`) обгорнуті у генерацію `std::system_error` із системними категоріями помилок, що дозволяє отримувати вичерпний текстовий опис причини відмови.
