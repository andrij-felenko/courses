# ⚙️ Створення живучого фонового процесу: демонізація та ізоляція сесії

Коли програма має виконувати тривалу фонову роботу незалежно від користувацького сеансу чи мережевого з'єднання SSH, простого запуску у фоні оболонки через амперсанд (`./worker &`) недостатньо. Такий процес залишається у тому самому сеансі, ділить спільний дескриптор термінала і загине при першому ж розриві зв'язку. Щоб процес отримав повну живучість, він повинен пройти канонічну процедуру **демонізації (daemonization)**: створити новий сеанс ядра, від'єднатися від керівного термінала та ізолювати стандартні потоки введення-виведення.

---

## 1. Архітектурний патерн подвійного розгалуження (Double Fork)

Класичний алгоритм демонізації Unix складається з восьми суворо впорядкованих кроків, кожен з яких усуває конкретну залежність від батьківського середовища:

```
[Батьківський процес (у терміналі)]
          │
          ▼ fork() #1
[Дочірній процес #1] ────> Батько завершується (exit(0)), термінал звільняється
          │
          ▼ setsid()  ───> Створення нового сеансу (SID = PID), втрата controlling TTY
          │
          ▼ fork() #2 ───> Гарантія: процес більше НЕ є лідером сесії
[Дочірній процес #2] ────> Процес #1 завершується (exit(0))
          │
          ├──> umask(0)          ─── Скидання маски прав доступу до файлів
          ├──> chdir("/")        ─── Звільнення точки монтування файлової системи
          ├──> signal(SIGHUP, …) ─── Встановлення власного обробника або SIG_IGN
          └──> dup2(/dev/null)   ─── Перенаправлення stdin, stdout, stderr (fd 0, 1, 2)
```

Розглянемо причини кожного кроку:
1. **Перший `fork()`**: гарантує, що викликаючий процес гарантовано **не є лідером групи процесів** (`PID != PGID`). Це обов'язкова умова системного виклику `setsid()`, інакше виклик поверне помилку `EPERM`. Одночасно завершення батьківського процесу повертає керування в командний рядок оболонки, звільняючи термінал для нових команд користувача.
2. **Виклик `setsid()`**: процес стає лідером нового сеансу і нової групи процесів. Його зв'язок із попереднім керівним терміналом анулюється: у системній структурі `signal_struct` ядра вказівник на `tty` скидається в `NULL`.
3. **Другий `fork()`**: новостворений процес стає дочірнім процесом лідера сеансу, тобто сам **вже не є лідером сеансу**. У традиційних системах System V Unix процес, який є лідером сеансу, міг випадково знову отримати керівний термінал при першому відкритті будь-якого файлу пристрою термінала (якщо не вказано прапорець `O_NOCTTY`). Другий `fork()` робить повторне захоплення TTY неможливим у принципі.
4. **Скидання `umask(0)`**: успадкована маска створення файлів від оболонки може несподівано обмежити права на створювані демоном сокети, логи чи тимчасові файли (наприклад, маска `0077` блокує доступ усім, крім власника).
5. **Зміна каталогу `chdir("/")`**: процес утримує відкритим свій поточний робочий каталог. Якщо запустити демон з підмонтованого розділу (наприклад, `/mnt/usb`), операційна система заблокує демонтування цього накопичувача через зайнятість вузла файлової системи.
6. **Ізоляція стандартних файлових дескрипторів**: дескриптори `0` (`stdin`), `1` (`stdout`) та `2` (`stderr`) перенаправляються у `/dev/null` або призначений лог-файл через системний виклик `dup2()`.

---

## 2. Реалізація демонізатора

Нижче наведено повноцінну реалізацію системного демонізатора мовами C та ідіоматичним C++20.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <signal.h>
#include <string.h>
#include <errno.h>
#include <time.h>

static volatile sig_atomic_t g_running = 1;
static volatile sig_atomic_t g_reload_requested = 0;

static void handle_sigterm(int signum) {
    (void)signum;
    g_running = 0;
}

static void handle_sighup(int signum) {
    (void)signum;
    g_reload_requested = 1;
}

int daemonize_process(const char *work_dir, const char *log_path) {
    /* 1. Скидання маски створення файлів */
    umask(0);

    /* 2. Перший fork: відокремлення від оболонки */
    pid_t pid = fork();
    if (pid < 0) {
        return -1;
    }
    if (pid > 0) {
        _exit(0); /* Завершуємо оригінального батька */
    }

    /* 3. Створення нового сеансу (втрата controlling TTY) */
    if (setsid() < 0) {
        return -1;
    }

    /* 4. Другий fork: позбавлення статусу лідера сесії */
    pid = fork();
    if (pid < 0) {
        return -1;
    }
    if (pid > 0) {
        _exit(0); /* Завершуємо першого нащадка (лідера сесії) */
    }

    /* 5. Зміна робочого каталогу на безпечний */
    if (chdir(work_dir ? work_dir : "/") < 0) {
        return -1;
    }

    /* 6. Налаштування обробників сигналів */
    struct sigaction sa_term;
    memset(&sa_term, 0, sizeof(sa_term));
    sa_term.sa_handler = handle_sigterm;
    sigemptyset(&sa_term.sa_mask);
    sigaction(SIGTERM, &sa_term, NULL);

    struct sigaction sa_hup;
    memset(&sa_hup, 0, sizeof(sa_hup));
    sa_hup.sa_handler = handle_sighup;
    sigemptyset(&sa_hup.sa_mask);
    sigaction(SIGHUP, &sa_hup, NULL);

    /* 7. Ізоляція стандартних файлових дескрипторів */
    int null_fd = open("/dev/null", O_RDWR);
    if (null_fd < 0) {
        return -1;
    }

    int log_fd = null_fd;
    if (log_path != NULL) {
        log_fd = open(log_path, O_WRONLY | O_CREAT | O_APPEND, 0644);
        if (log_fd < 0) {
            log_fd = null_fd;
        }
    }

    /* stdin -> /dev/null */
    dup2(null_fd, STDIN_FILENO);
    /* stdout -> log_file або /dev/null */
    dup2(log_fd, STDOUT_FILENO);
    /* stderr -> log_file або /dev/null */
    dup2(log_fd, STDERR_FILENO);

    if (null_fd > 2) {
        close(null_fd);
    }
    if (log_fd > 2 && log_fd != null_fd) {
        close(log_fd);
    }

    return 0;
}

int main(void) {
    if (daemonize_process("/", "/tmp/daemon_worker.log") < 0) {
        perror("daemonize failed");
        return 1;
    }

    printf("Daemon started successfully with PID %d\n", getpid());
    fflush(stdout);

    while (g_running) {
        if (g_reload_requested) {
            g_reload_requested = 0;
            printf("SIGHUP received: reloading configuration at %ld\n", (long)time(NULL));
            fflush(stdout);
        }
        sleep(2);
    }

    printf("SIGTERM received: shutting down gracefully\n");
    fflush(stdout);
    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <filesystem>
#include <system_error>
#include <csignal>
#include <atomic>
#include <thread>
#include <chrono>
#include <memory>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

namespace system_daemon {

std::atomic<bool> g_running{true};
std::atomic<bool> g_reload_requested{false};

void handle_signal(int signum) noexcept {
    if (signum == SIGTERM) {
        g_running.store(false, std::memory_order_relaxed);
    } else if (signum == SIGHUP) {
        g_reload_requested.store(true, std::memory_order_relaxed);
    }
}

class FileDescriptorWrapper {
public:
    explicit FileDescriptorWrapper(int fd) noexcept : fd_(fd) {}
    ~FileDescriptorWrapper() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    FileDescriptorWrapper(const FileDescriptorWrapper&) = delete;
    FileDescriptorWrapper& operator=(const FileDescriptorWrapper&) = delete;
    FileDescriptorWrapper(FileDescriptorWrapper&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    FileDescriptorWrapper& operator=(FileDescriptorWrapper&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

private:
    int fd_{-1};
};

class DaemonIsolation {
public:
    static void isolate(const std::filesystem::path& work_dir, const std::filesystem::path& log_path) {
        ::umask(0);

        pid_t pid1 = ::fork();
        if (pid1 < 0) {
            throw std::system_error(errno, std::generic_category(), "First fork failed");
        }
        if (pid1 > 0) {
            ::_exit(0);
        }

        if (::setsid() < 0) {
            throw std::system_error(errno, std::generic_category(), "setsid failed");
        }

        pid_t pid2 = ::fork();
        if (pid2 < 0) {
            throw std::system_error(errno, std::generic_category(), "Second fork failed");
        }
        if (pid2 > 0) {
            ::_exit(0);
        }

        std::filesystem::current_path(work_dir);

        setup_signals();
        redirect_standard_io(log_path);
    }

private:
    static void setup_signals() {
        struct sigaction sa{};
        sa.sa_handler = handle_signal;
        ::sigemptyset(&sa.sa_mask);

        if (::sigaction(SIGTERM, &sa, nullptr) < 0 || ::sigaction(SIGHUP, &sa, nullptr) < 0) {
            throw std::system_error(errno, std::generic_category(), "Signal registration failed");
        }
    }

    static void redirect_standard_io(const std::filesystem::path& log_path) {
        FileDescriptorWrapper null_fd(::open("/dev/null", O_RDWR));
        if (!null_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Failed to open /dev/null");
        }

        FileDescriptorWrapper log_fd(::open(log_path.c_str(), O_WRONLY | O_CREAT | O_APPEND, 0644));
        int target_out_fd = log_fd.valid() ? log_fd.get() : null_fd.get();

        if (::dup2(null_fd.get(), STDIN_FILENO) < 0 ||
            ::dup2(target_out_fd, STDOUT_FILENO) < 0 ||
            ::dup2(target_out_fd, STDERR_FILENO) < 0) {
            throw std::system_error(errno, std::generic_category(), "dup2 file descriptor redirection failed");
        }
    }
};

} // namespace system_daemon

int main() {
    try {
        system_daemon::DaemonIsolation::isolate("/", "/tmp/daemon_worker_cpp.log");

        std::cout << "Modern C++ Daemon running with PID " << ::getpid() << std::endl;

        while (system_daemon::g_running.load(std::memory_order_relaxed)) {
            if (system_daemon::g_reload_requested.exchange(false, std::memory_order_relaxed)) {
                std::cout << "Reloading config via SIGHUP at " 
                          << std::chrono::system_clock::now().time_since_epoch().count() 
                          << std::endl;
            }
            std::this_thread::sleep_for(std::chrono::seconds(2));
        }

        std::cout << "Daemon shutting down cleanly." << std::endl;
    } catch (const std::exception& ex) {
        return 1;
    }
    return 0;
}
```
:::

---

## 3. Перевірка стану ізоляції через `/proc` та `strace`

Після запуску скомпільованого демона стан його прив'язки до ядра можна перевірити через псевдофайлову систему `/proc`:

```bash
$ ./daemon_worker
$ ps -o pid,ppid,pgid,sid,tty,stat,cmd -C daemon_worker
    PID    PPID    PGID     SID TT       STAT CMD
  24891       1   24890   24890 ?        Ss   ./daemon_worker
```

Аналіз значень у таблиці процесів показує досягнутий стан:
- **`PPID = 1`**: процес осиротів і був підібраний кореневим менеджером процесів системи (`init` або `systemd`);
- **`SID == PGID`**: процес функціонує в окремому ізольованому сеансі;
- **`TT = ?`**: поле термінала порожнє, що свідчить про відсутність керівного термінала (`controlling TTY = NULL`);
- **`STAT = Ss`**: прапорець `s` позначає лідера сесії або процес, який працює у власному відокремленому сигнальному просторі.

Також можна перевірити стан дескрипторів процесу за посиланням у каталозі `/proc/24891/fd/`:

```bash
$ ls -l /proc/24891/fd/
lr-x------ 1 user user 64 Aug 25 12:00 0 -> /dev/null
l-wx------ 1 user user 64 Aug 25 12:00 1 -> /tmp/daemon_worker.log
l-wx------ 1 user user 64 Aug 25 12:00 2 -> /tmp/daemon_worker.log
```

Усі стандартні потоки відв'язано від псевдотермінала `/dev/pts/N`, тому будь-яке закриття термінальних вікон, емуляторів або обрив SSH-сесій не вплине на життєвий цикл процесу.

---

## 4. Критичні підводні камені демонізації

Під час практичної розробки системних фонових процесів найчастіше припускаються таких небезпечних помилок:

1. **Небезпека незакритого робочого каталогу**:
   Якщо демон запущено, наприклад, у каталозі `/mnt/storage/service`, поточний робочий каталог процесу тримає точку монтування активною (`busy`). Системний адміністратор не зможе демонтувати диск (`umount /mnt/storage`), поки демон працює. Виклик `chdir("/")` переміщує процес у корінь системи, звільняючи всі знімні та мережеві томи.

2. **Захоплення fd 0, 1 або 2 сторонніми бібліотеками**:
   Якщо замість `dup2(null_fd, STDIN_FILENO)` просто закрити дескриптор викликом `close(0)`, дескриптор під номером `0` стає вільним у дескрипторній таблиці процесу. Коли сторонній модуль (наприклад, драйвер бази даних чи криптографічна бібліотека) викличе перший `open()` або `socket()`, ядро Linux виділить для нового сокета найменший доступний номер — тобто дескриптор `0`. Наступний виклик `read(STDIN_FILENO, ...)` несподівано прочитає мережевий сокет, а випадковий виклик `printf()` запише текстовий лог прямо у клієнтський потік даних, порушивши протокол. Відкриття `/dev/null` на позиціях 0, 1 та 2 гарантує надійний захист від колізії номерів.

3. **Спадкування зайвих файлових дескрипторів**:
   За замовчуванням дескриптори відкритих файлів успадковуються дочірніми процесами через `fork()`. Якщо батьківська оболонка чи програма-ініціатор мала відкриті дескриптори файлів, сокетів чи анонімних каналів без прапорця `O_CLOEXEC`, демон утримуватиме їх відкритими нескінченно довго. Щоб запобігти витоку ресурсів, перед виконанням циклу демона рекомендується закривати всі зайві дескриптори, просканувавши каталог `/proc/self/fd` або використавши системний виклик `close_range(3, ~0U, 0)`.

4. **Сучасний контекст: Демонізація проти `systemd`**:
   У сучасних дистрибутивах Linux подвійне розгалуження більше не є обов'язковим для системних служб. Диспетчер `systemd` самостійно створює ізольовані середовища (cgroups), керує дескрипторами введення-виведення через журнал (`systemd-journald`) та відстежує процеси за допомогою механізму контрольних груп. Для служб `systemd` часто достатньо конфігурації `Type=exec` або `Type=simple`, де процес залишається на передньому плані свого cgroup, а всі турботи про сесії та перенаправлення дескрипторів бере на себе ініціалізаційний демон PID 1. Проте для автономних консольних утиліт та інструментів самостійної фонової обробки подвійний `fork()` із `setsid()` залишається золотим стандартом надійності.
