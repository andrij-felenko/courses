# ⚙️ Практична реалізація демона перехоплення FAN_OPEN_PERM та FAN_OPEN_EXEC_PERM

Ця вставка містить повноцінні приклади реалізації сервісу (демона) моніторингу файлової системи мовами C та C++, який синхронно перехоплює спроби відкриття та виконання файлів за допомогою `FAN_OPEN_PERM` і `FAN_OPEN_EXEC_PERM`. У ній детально розібрано практичний алгоритм обробки подій, аналізу файлів через дескриптори ядра, передачу відповідей `FAN_ALLOW` / `FAN_DENY`, а також запобігання підступним пасткам: витокам дескрипторів та взаємному блокуванню демона (self-deadlock).

## Архітектурний алгоритм демона перехоплення

Демон синхронного захисту працює за п'ятикроковим циклом обробки. Кожен крок виконує суворо визначену функцію у забезпеченні безпеки та цілісності файлової системи:

1. **Ініціалізація групи:** Виклик `fanotify_init()` із прапорцями `FAN_CLASS_CONTENT | FAN_CLOEXEC` для створення перехоплюючого файлового дескриптора. Клас `FAN_CLASS_CONTENT` гарантує, що демон отримуватиме події дозволу та зможе блокувати системні виклики VFS.
2. **Встановлення мітки:** Виклик `fanotify_mark()` із маскою `FAN_OPEN_PERM | FAN_OPEN_EXEC_PERM` на потрібну точку монтування (наприклад, `/tmp` або `/home`). Прапорець `FAN_MARK_MOUNT` вказує ядру моніторити абсолютно всі файли на змонтованому томі.
3. **Цикл читання подій:** Читання вирівняного буфера метаданих `struct fanotify_event_metadata` через системний виклик `read()`. Оскільки ядро може повернути кілька подій за один виклик, демон ітерує по буферу за допомогою макросів `FAN_EVENT_OK` та `FAN_EVENT_NEXT`.
4. **Аналіз та фільтрація:** 
   - Перевірка, чи не належить PID події самому демону (`e->pid == getpid()`), для відсікання рекурсивних зациклень.
   - Аналіз бінарного вмісту файлу через наданий ядром дескриптор `e->fd` (наприклад, читання заголовків Magic Bytes або вирахування хеш-суми SHA-256).
   - Опціональна перевірка атрибутів процесу викликача через огляд файлу `/proc/<pid>/cmdline` або аналіз контексту безпеки.
5. **Вердикт та очищення:** Запис структури `struct fanotify_response` (`FAN_ALLOW` або `FAN_DENY`) у дескриптор fanotify та обов'язкове закриття `close(e->fd)`.

---

## Реалізація демона: C та C++

У наведених вкладках продемонстровано реалізацію демона безпеки. У вкладці **C** застосовано низькорівневі системні виклики POSIX із ручним управлінням ресурсами, а у вкладці **C++** — ідіоматичний підхід із використанням RAII-обгортки для файлових дескрипторів, концепцій `std::string_view` та автоматичного звільнення ресурсів при виникненні виключень.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/fanotify.h>
#include <sys/stat.h>

#define BUF_SIZE 4096

static void handle_perm_event(int fanotify_fd, const struct fanotify_event_metadata *e) {
    struct fanotify_response resp;
    resp.fd = e->fd;
    resp.response = FAN_ALLOW;

    /* Пастка 1: Ігноруємо операції самого демона, щоб уникнути взаємного блокування */
    if (e->pid == getpid()) {
        write(fanotify_fd, &resp, sizeof(resp));
        close(e->fd);
        return;
    }

    /* Аналізуємо файл за допомогою дескриптора, відданого ядром */
    char magic[4] = {0};
    ssize_t bytes_read = pread(e->fd, magic, sizeof(magic), 0);

    /* Забороняємо виконання файлів, якщо вони починаються з сигнатури небезпечного скрипту */
    if (bytes_read >= 4 && magic[0] == 'B' && magic[1] == 'A' && magic[2] == 'D' && magic[3] == '!') {
        printf("[GUARD] БЛОКУВАННЯ: Процес PID=%d намагався відкрити заборонений файл (FD=%d)\n",
               e->pid, e->fd);
        resp.response = FAN_DENY;
    } else {
        printf("[GUARD] ДОЗВОЛЕНО: Процес PID=%d відкрив файл (FD=%d)\n", e->pid, e->fd);
        resp.response = FAN_ALLOW;
    }

    /* Надсилаємо вердикт ядру */
    if (write(fanotify_fd, &resp, sizeof(resp)) < 0) {
        perror("write(fanotify_response)");
    }

    /* Обов'язково закриваємо файловий дескриптор події */
    close(e->fd);
}

int main(int argc, char *argv[]) {
    const char *target_path = (argc > 1) ? argv[1] : "/tmp";

    /* Ініціалізація групи fanotify з класом перевірки вмісту */
    int fanotify_fd = fanotify_init(FAN_CLASS_CONTENT | FAN_CLOEXEC, O_RDONLY | O_CLOEXEC);
    if (fanotify_fd < 0) {
        perror("fanotify_init");
        return 1;
    }

    /* Ставимо мітку перехоплення відкриття та виконання на вказаний шлях */
    if (fanotify_mark(fanotify_fd, FAN_MARK_ADD | FAN_MARK_MOUNT,
                      FAN_OPEN_PERM | FAN_OPEN_EXEC_PERM,
                      AT_FDCWD, target_path) < 0) {
        perror("fanotify_mark");
        close(fanotify_fd);
        return 1;
    }

    printf("[GUARD] Демон запущено. Перехоплення FAN_OPEN_PERM на %s...\n", target_path);

    /* Буфер для читання подій, вирівняний по межі метаданих */
    char buf[BUF_SIZE] __attribute__((aligned(__alignof__(struct fanotify_event_metadata))));

    for (;;) {
        ssize_t len = read(fanotify_fd, buf, sizeof(buf));
        if (len < 0) {
            if (errno == EINTR) continue;
            perror("read(fanotify_fd)");
            break;
        }

        const struct fanotify_event_metadata *metadata = (const struct fanotify_event_metadata *)buf;
        while (FAN_EVENT_OK(metadata, len)) {
            if (metadata->vers != FANOTIFY_METADATA_VERSION) {
                fprintf(stderr, "Невідповідність версії метаданих fanotify!\n");
                close(fanotify_fd);
                return 1;
            }

            if (metadata->mask & (FAN_OPEN_PERM | FAN_OPEN_EXEC_PERM)) {
                handle_perm_event(fanotify_fd, metadata);
            }

            metadata = FAN_EVENT_NEXT(metadata, len);
        }
    }

    close(fanotify_fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <memory>
#include <stdexcept>
#include <system_error>
#include <string>
#include <cstring>
#include <cerrno>
#include <unistd.h>
#include <fcntl.h>
#include <sys/fanotify.h>
#include <sys/stat.h>

namespace guard {

// RAII обгортка для безпечного управління файловими дескрипторами (RAII)
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

class FanotifyGuard {
    UniqueFd fanotify_fd_;
    pid_t daemon_pid_;

    void process_event(const fanotify_event_metadata& event) {
        // Упаковуємо дескриптор події в RAII обгортку для автоматичного закриття при виході
        UniqueFd event_fd(event.fd);
        fanotify_response response{event.fd, FAN_ALLOW};

        // Запобігання рекурсивному блокуванню власного процесу
        if (event.pid == daemon_pid_) {
            ::write(fanotify_fd_.get(), &response, sizeof(response));
            return;
        }

        char magic[4] = {0};
        ssize_t bytes_read = ::pread(event_fd.get(), magic, sizeof(magic), 0);

        if (bytes_read >= 4 && std::string_view(magic, 4) == "BAD!") {
            std::cout << "[GUARD-CPP] БЛОКУВАННЯ: PID=" << event.pid 
                      << " намагався відкрити заблокований вміст\n";
            response.response = FAN_DENY;
        } else {
            std::cout << "[GUARD-CPP] ДОЗВОЛЕНО: PID=" << event.pid << '\n';
            response.response = FAN_ALLOW;
        }

        if (::write(fanotify_fd_.get(), &response, sizeof(response)) < 0) {
            std::cerr << "Помилка надсилання рішення ядру: " << std::strerror(errno) << '\n';
        }
        // event_fd деструктор автоматично закриває дескриптор події
    }

public:
    explicit FanotifyGuard(const std::string& target_path) 
        : daemon_pid_(::getpid()) {
        
        int fd = ::fanotify_init(FAN_CLASS_CONTENT | FAN_CLOEXEC, O_RDONLY | O_CLOEXEC);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "fanotify_init failed");
        }
        fanotify_fd_.reset(fd);

        if (::fanotify_mark(fanotify_fd_.get(), FAN_MARK_ADD | FAN_MARK_MOUNT,
                           FAN_OPEN_PERM | FAN_OPEN_EXEC_PERM,
                           AT_FDCWD, target_path.c_str()) < 0) {
            throw std::system_error(errno, std::generic_category(), "fanotify_mark failed");
        }

        std::cout << "[GUARD-CPP] Моніторинг увімкнено на: " << target_path << '\n';
    }

    void run() {
        alignas(fanotify_event_metadata) char buffer[4096];

        while (true) {
            ssize_t len = ::read(fanotify_fd_.get(), buffer, sizeof(buffer));
            if (len < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "read failed");
            }

            const auto* metadata = reinterpret_cast<const fanotify_event_metadata*>(buffer);
            while (FAN_EVENT_OK(metadata, len)) {
                if (metadata->vers != FANOTIFY_METADATA_VERSION) {
                    throw std::runtime_error("Mismatched fanotify metadata version");
                }

                if (metadata->mask & (FAN_OPEN_PERM | FAN_OPEN_EXEC_PERM)) {
                    process_event(*metadata);
                }

                metadata = FAN_EVENT_NEXT(metadata, len);
            }
        }
    }
};

} // namespace guard

int main(int argc, char* argv[]) {
    try {
        const std::string path = (argc > 1) ? argv[1] : "/tmp";
        guard::FanotifyGuard daemon(path);
        daemon.run();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка демона: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

---

## Типові пастки та крайні випадки (Edge Cases)

При розробці виробничих демонів перехоплення файлових операцій необхідно враховувати шість критичних архітектурних пасток:

### 1. Пастка взаємного блокування (Self-Deadlock)
Якщо демон безпеки під час обробки події звертається до файлу на тій самій файловій системі, де встановлено мітку, його власний виклик `open()` згенерує нову подію `FAN_OPEN_PERM`. Оскільки демон у цей час заблокований у очікуванні `read()` або обробки попередньої події, новий виклик VFS зупинить потік демона. Виникає класичне зациклення: демон чекає відповіді від самого себе.

- **Рішення:** Завжди перевіряти `event.pid == getpid()`. Якщо операцію ініціював сам демон, негайно повертати `FAN_ALLOW`. Також перевірку вмісту файлу слід виконувати **виключно через анонімний дескриптор `event.fd`**, наданий ядром, а не відкривати файл повторно за шляхом!

### 2. Витік файлових дескрипторів (FD Leak)
Для кожної події дозволу ядро створює новий анонімний файловий дескриптор у таблиці процесів демона. Якщо демон відповість ядру через `write()`, але забуде викликати `close(e->fd)`, таблиця файлових дескрипторів демона вичерпається протягом кількох хвилин (`EMFILE`). У C++ варіанті ця проблема вирішується обгорткою RAII (`UniqueFd`), яка гарантує виклик `close()` при виході з області видимості.

### 3. Аварійне завершення демона (Daemon Crash)
Якщо демон перехоплення аварійно завершує роботу (наприклад, через `SIGKILL` або падіння `segmentation fault`) у мить, коли десятки прикладних процесів заблоковані в ядрі у очікуванні `FAN_OPEN_PERM`, ядро Linux автоматично знищує fanotify-групу — і саме відповідає за померлого: у `fanotify_release()` кожна подія дозволу (і та, що чекала в черзі, і та, що вже пішла на розгляд) дістає вердикт **`FAN_ALLOW`**, тож заблоковані виклики `open()` просто завершуються успішно. Система не стає, але захист із цієї миті вимкнений — падіння демона треба ловити наглядом за службою (`Restart=always` у `systemd`), а не сподіванням на помилку в прикладній програмі.

### 4. Вирівнювання буфера у пам'яті
Дескриптор fanotify повертає бінарний потік даних. Читання буфера, не вирівняного по межі `struct fanotify_event_metadata`, на архітектурах ARM або RISC-V призведе до помилки bus error (`SIGBUS`). У C необхідно використовувати `__attribute__((aligned(...)))`, а в C++11 — специфікатор `alignas(...)`.

### 5. Багатопотокова обробка подій (Multi-threading)
При високому навантаженні один потік демона може стати вузьким місцем. Високонавантажені антивірусні сканери використовують масив потоків-воркерів. Головний потік читає події з `fanotify_fd` і передає файлові дескриптори `event.fd` у чергу потоків-обробників. Кожен воркер сканує файл, надсилає відповідь `FAN_ALLOW` або `FAN_DENY` у той самий `fanotify_fd` та закриває дескриптор події. Оскільки системний виклик `write()` у дескриптор fanotify є потокобезпечним (thread-safe) у ядрі Linux, кілька воркерів можуть паралельно надсилати рішення щодо різних файлів.

### 6. Обробка переривань системних викликів (`EINTR`)
При роботі з блокуючим читанням з `fanotify_fd` надходження системних сигналів (наприклад, `SIGCHLD` або `SIGHUP`) може перервати системний виклик `read()`, у результаті чого він поверне `-1`, а `errno` дорівнюватиме `EINTR`. Демон повинен обробляти цей випадок у циклі та продовжувати очікування подій через `continue`, а не завершувати роботу сервісу з помилкою.
