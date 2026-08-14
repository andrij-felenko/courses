# ⚙️ Реалізація демона спостереження за /dev/kmsg мовами C та C++

У цій практичній вставці продемонстровано розробку фонового системного демона-спостерігача, який отримує повідомлення ядра Linux у реальному часі безпосередньо з розширеного інтерфейсу символьного пристрою `/dev/kmsg`. Програма застосовує асинхронну модель виводу та неблокуюче опитування подій через системний виклик `poll()`, правильно обробляє розриви послідовних номерів при переповненні кільцевого буфера ядра та розбирає текстові заголовки й метадані подій.

---

## Архітектура демона та прийоми роботи з `/dev/kmsg`

Підсистема журналювання ядра Linux надає простір користувача декілька альтернативних шляхів для зчитування повідомлень, проте символьний пристрій `/dev/kmsg` має суттєві переваги перед застарілими інтерфейсами `syslog(2)` та `/proc/kmsg`. По-перше, пристрій `/dev/kmsg` підтримує багатопотокову модель: кожен відкритий файловий дескриптор володіє власним незалежним покажчиком зчитування, тому кілька демонів спостереження можуть зчитувати той самий потік повідомлень одночасно, не викрадаючи записи один в одного. По-друге, цей інтерфейс повертає розширену метаінформацію, включаючи точний монотонний штамп часу у наносекундах (`CLOCK_MONOTONIC`), послідовний номер запису `seq` та словник атрибутів sysfs (`SUBSYSTEM`, `DEVICE`).

Розробка надійного демона спостереження вимагає дотримання кількох ключових правил роботи з асинхронними системними викликами:

1. **Режим неблокуючого доступу (`O_NONBLOCK`):** Пристрій відкривається з прапорцями `O_RDWR | O_NONBLOCK`. Завдяки цьому при спробі прочитати дані з порожнього буфера виклик `read()` не засинає, а повертає помилку `-1` із кодом `errno = EAGAIN` (або `EWOULDBLOCK`). Це дозволяє легко інтегрувати читач у головний цикл подій (event loop) на базі `poll()` або `epoll()`.

2. **Позиціонування покажчика читача (`SEEK_END`):** Одразу після відкриття файлового дескриптора демон виконує виклик `lseek(fd, 0, SEEK_END)`. За замовчуванням пристрій `/dev/kmsg` відкривається на найстарішому збереженому записі буфера ядра. Виклик `lseek` зі зміщенням до кінця пропускає накопичену історію та переміщує покажчик так, щоб демон отримував виключно **нові** повідомлення, які генеруватимуться ядром після моменту запуску програми.

3. **Обробка переповнення кільцевого буфера (`EPIPE`):** Кільцевий буфер ядра має фіксований розмір (`CONFIG_LOG_BUF_SHIFT`). Якщо ядро породжує нові повідомлення швидше, ніж демон простору користувача встигає їх обробляти, старі дескриптори витісняються й видаляються з пам'яті. У цей момент покажчик зчитування демона опиняється в позиції даних, яких більше не існує. При наступній спробі виконати `read()` ядро повертає помилку `-1` із значенням `errno = EPIPE`. Надійний демон не повинен завершувати роботу після цієї помилки: код мусить зафіксувати факт втрати частини записів у лозі та повторити виклик `read()`. Ядро автоматично скоригує покажчик демона на найстаріший доступний запис у буфері.

4. **Розбір метаданих та словника:** Кожна атомарна операція `read()` повертає ровно один запис ядра. Рядок має структуру `level,seq,nsec,flags;message\n`, після якої з нового рядка з відступом в один пробіл можуть іти ключі метаданих, такі як ` SUBSYSTEM=net` або ` DEVICE=+net:eth0`. Демон мусить правильно виділяти першу секцію до символу крапки з комою `;`, витягувати числові поля та парсити додаткові рядки.

5. **Інжектирування повідомлень із простору користувача:** Оскільки пристрій відкрито у режимі `O_RDWR`, демон може записувати власні рядки у `/dev/kmsg` за допомогою виклику `write()`. Рядок виду `<6>my_daemon: message` сприймається ядром як повноцінне повідомлення `KERN_INFO` від внутрішньої підсистеми і потрапляє у глобальний буфер логів з автоматично присвоєними мітками часу та послідовними номерами.

---

## Порівняння реалізацій мовами C та C++

Нижче наведено дві ідіоматичні реалізації демона спостереження.

C-версія побудована на системних викликах POSIX (`open`, `read`, `write`, `lseek`, `poll`), використовує масив `struct pollfd` для очікування подій I/O та пряму роботу з покажчиками пам'яті (`memchr`, `strstr`, `memcpy`).

C++ версія використовує сучасні концепції мови C++20/C++23:
- **Принцип RAII (Resource Acquisition Is Initialization):** Клас `FileDescriptor` автоматично закриває системний дескриптор у деструкторі через `close()`, виключаючи витік ресурсів при виникненні винятків чи передчасному виході з функції.
- **Вказівники рядків без виділення пам'яті у купі (`std::string_view`):** Замість копіювання рядків у динамічну пам'ять парсер працює з легкими неволодіючими зрізами пам'яті `std::string_view`, що кардинально знижує накладні витрати на роботу з пам'яттю та унеможливлює фрагментацію купи під час тривалої роботи демона.
- **Безпечне числове перетворення (`std::from_chars`):** Використовується замість застарілого та повільного `sscanf` для швидкого розбору послідовних номерів та наносекундних штампів часу.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <errno.h>
#include <stdbool.h>

#define KMSG_PATH "/dev/kmsg"
#define BUF_SIZE 8192

static const char *loglevel_to_string(int level) {
    switch (level & 0x07) {
        case 0: return "EMERG";
        case 1: return "ALERT";
        case 2: return "CRIT";
        case 3: return "ERR";
        case 4: return "WARN";
        case 5: return "NOTICE";
        case 6: return "INFO";
        case 7: return "DEBUG";
        default: return "UNK";
    }
}

static void parse_and_print_record(const char *buf, ssize_t len) {
    int level = 0;
    unsigned long long seq = 0;
    unsigned long long nsec = 0;
    char flags = '-';
    char message[4096] = {0};
    char subsystem[128] = "kernel";

    /* Шукаємо розділювач крапки з комою між заголовком та повідомленням */
    const char *semicolon = memchr(buf, ';', len);
    if (!semicolon) {
        return;
    }

    /* Розбираємо заголовок: level,seq,nsec,flags; */
    if (sscanf(buf, "%d,%llu,%llu,%c", &level, &seq, &nsec, &flags) < 3) {
        return;
    }

    /* Знаходимо кінець першого рядка (тексту повідомлення) */
    const char *msg_start = semicolon + 1;
    const char *newline = memchr(msg_start, '\n', len - (msg_start - buf));
    size_t msg_len = newline ? (size_t)(newline - msg_start) : strlen(msg_start);
    if (msg_len >= sizeof(message)) {
        msg_len = sizeof(message) - 1;
    }
    memcpy(message, msg_start, msg_len);
    message[msg_len] = '\0';

    /* Шукаємо словник метаданих у наступних рядках (наприклад, SUBSYSTEM=net) */
    if (newline && (size_t)(newline - buf) < (size_t)len) {
        const char *subsys_ptr = strstr(newline, " SUBSYSTEM=");
        if (subsys_ptr) {
            subsys_ptr += 11; /* Пропускаємо " SUBSYSTEM=" */
            const char *subsys_end = strchr(subsys_ptr, '\n');
            size_t subsys_len = subsys_end ? (size_t)(subsys_end - subsys_ptr) : strlen(subsys_ptr);
            if (subsys_len >= sizeof(subsystem)) {
                subsys_len = sizeof(subsystem) - 1;
            }
            memcpy(subsystem, subsys_ptr, subsys_len);
            subsystem[subsys_len] = '\0';
        }
    }

    double seconds = (double)nsec / 1000000000.0;
    printf("[%12.6f] [%-6s] [%-10s] (seq=%llu): %s\n",
           seconds, loglevel_to_string(level), subsystem, seq, message);
}

int main(void) {
    int fd = open(KMSG_PATH, O_RDWR | O_NONBLOCK);
    if (fd < 0) {
        perror("Failed to open " KMSG_PATH);
        return EXIT_FAILURE;
    }

    /* Зсуваємо позицію читача на кінець буфера, щоб бачити лише нові події */
    if (lseek(fd, 0, SEEK_END) < 0) {
        perror("Failed to lseek SEEK_END on " KMSG_PATH);
        close(fd);
        return EXIT_FAILURE;
    }

    /* Записуємо тестове повідомлення з простору користувача у журнал ядра */
    const char *hello_msg = "<6>kmsg_watcher: watcher daemon initialized successfully\n";
    if (write(fd, hello_msg, strlen(hello_msg)) < 0) {
        perror("Failed to write to " KMSG_PATH);
    }

    printf("Listening for new kernel messages on %s...\n", KMSG_PATH);

    struct pollfd pfd = {
        .fd = fd,
        .events = POLLIN
    };

    char buffer[BUF_SIZE];

    while (1) {
        int ret = poll(&pfd, 1, -1);
        if (ret < 0) {
            if (errno == EINTR) continue;
            perror("poll failed");
            break;
        }

        if (pfd.revents & POLLIN) {
            while (1) {
                ssize_t bytes_read = read(fd, buffer, sizeof(buffer) - 1);
                if (bytes_read < 0) {
                    if (errno == EAGAIN || errno == EWOULDBLOCK) {
                        break; /* Немає більше нових даних */
                    }
                    if (errno == EPIPE) {
                        fprintf(stderr, "WARN: Kernel log buffer overwritten, messages lost!\n");
                        continue; /* Автоматично перестрибуємо на доступні дані */
                    }
                    perror("read failed");
                    goto cleanup;
                }

                buffer[bytes_read] = '\0';
                parse_and_print_record(buffer, bytes_read);
            }
        }
    }

cleanup:
    close(fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <charconv>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <cerrno>
#include <cstring>

namespace kmsg {

// RAII обгортка для файлового дескриптора POSIX
class FileDescriptor {
    int fd_{-1};
public:
    explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
    ~FileDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

struct KernelRecord {
    int level{6};
    uint64_t sequence{0};
    uint64_t timestamp_nsec{0};
    char flags{'-'};
    std::string message;
    std::string subsystem{"kernel"};
};

constexpr std::string_view loglevel_to_string(int level) noexcept {
    switch (level & 0x07) {
        case 0: return "EMERG";
        case 1: return "ALERT";
        case 2: return "CRIT";
        case 3: return "ERR";
        case 4: return "WARN";
        case 5: return "NOTICE";
        case 6: return "INFO";
        case 7: return "DEBUG";
        default: return "UNK";
    }
}

class MessageParser {
public:
    static bool parse(std::string_view raw, KernelRecord& rec) {
        auto semicolon_pos = raw.find(';');
        if (semicolon_pos == std::string_view::npos) {
            return false;
        }

        std::string_view header = raw.substr(0, semicolon_pos);
        std::string_view payload = raw.substr(semicolon_pos + 1);

        // Парсимо розширене поле заголовка (level,seq,nsec,flags)
        auto comma1 = header.find(',');
        auto comma2 = header.find(',', comma1 + 1);
        auto comma3 = header.find(',', comma2 + 1);

        if (comma1 == std::string_view::npos || comma2 == std::string_view::npos) {
            return false;
        }

        std::from_chars(header.data(), header.data() + comma1, rec.level);
        std::from_chars(header.data() + comma1 + 1, header.data() + comma2, rec.sequence);

        if (comma3 != std::string_view::npos) {
            std::from_chars(header.data() + comma2 + 1, header.data() + comma3, rec.timestamp_nsec);
            if (comma3 + 1 < header.size()) {
                rec.flags = header[comma3 + 1];
            }
        } else {
            std::from_chars(header.data() + comma2 + 1, header.data() + header.size(), rec.timestamp_nsec);
        }

        // Текст повідомлення — перший рядок корисної ноші
        auto newline_pos = payload.find('\n');
        if (newline_pos != std::string_view::npos) {
            rec.message = payload.substr(0, newline_pos);

            // Шукаємо метадані SUBSYSTEM= у наступних рядках
            std::string_view metadata = payload.substr(newline_pos + 1);
            constexpr std::string_view subsys_prefix = " SUBSYSTEM=";
            auto subsys_pos = metadata.find(subsys_prefix);
            if (subsys_pos != std::string_view::npos) {
                auto subsys_start = subsys_pos + subsys_prefix.size();
                auto subsys_end = metadata.find('\n', subsys_start);
                if (subsys_end != std::string_view::npos) {
                    rec.subsystem = metadata.substr(subsys_start, subsys_end - subsys_start);
                } else {
                    rec.subsystem = metadata.substr(subsys_start);
                }
            } else {
                rec.subsystem = "kernel";
            }
        } else {
            rec.message = payload;
            rec.subsystem = "kernel";
        }

        return true;
    }
};

} // namespace kmsg

int main() {
    using namespace kmsg;

    int raw_fd = ::open("/dev/kmsg", O_RDWR | O_NONBLOCK);
    if (raw_fd < 0) {
        std::cerr << "Failed to open /dev/kmsg: " << std::strerror(errno) << '\n';
        return EXIT_FAILURE;
    }

    FileDescriptor kmsg_fd(raw_fd);

    if (::lseek(kmsg_fd.get(), 0, SEEK_END) < 0) {
        std::cerr << "Failed to lseek SEEK_END: " << std::strerror(errno) << '\n';
        return EXIT_FAILURE;
    }

    std::string_view init_msg = "<6>kmsg_watcher_cpp: C++ daemon initialized\n";
    if (::write(kmsg_fd.get(), init_msg.data(), init_msg.size()) < 0) {
        std::cerr << "Failed to write init message: " << std::strerror(errno) << '\n';
    }

    std::cout << "C++ watcher daemon listening on /dev/kmsg...\n";

    pollfd pfd{.fd = kmsg_fd.get(), .events = POLLIN, .revents = 0};
    std::vector<char> buffer(8192);

    while (true) {
        int poll_ret = ::poll(&pfd, 1, -1);
        if (poll_ret < 0) {
            if (errno == EINTR) continue;
            std::cerr << "Poll error: " << std::strerror(errno) << '\n';
            break;
        }

        if (pfd.revents & POLLIN) {
            while (true) {
                ssize_t bytes = ::read(kmsg_fd.get(), buffer.data(), buffer.size() - 1);
                if (bytes < 0) {
                    if (errno == EAGAIN || errno == EWOULDBLOCK) {
                        break; // Буфер спорожнів
                    }
                    if (errno == EPIPE) {
                        std::cerr << "WARN: Kernel log buffer overrun, messages skipped\n";
                        continue;
                    }
                    std::cerr << "Read error: " << std::strerror(errno) << '\n';
                    return EXIT_FAILURE;
                }

                buffer[bytes] = '\0';
                std::string_view raw_record(buffer.data(), static_cast<size_t>(bytes));

                KernelRecord rec;
                if (MessageParser::parse(raw_record, rec)) {
                    double sec = static_cast<double>(rec.timestamp_nsec) / 1e9;
                    std::cout << '[' << sec << "] ["
                              << loglevel_to_string(rec.level) << "] ["
                              << rec.subsystem << "] (seq=" << rec.sequence << "): "
                              << rec.message << '\n';
                }
            }
        }
    }

    return EXIT_SUCCESS;
}
```
:::

---

## Крайові випадки та пастки реалізації

Під час реалізації демона спостереження у реальних високонавантажених системах важливо враховувати кілька фундаментальних підводних каменів:

### 1. Буферизований та небуферизований вивід у просторі користувача
Стандартні функції друку `printf()` у C або `std::cout` у C++ за замовчуванням буферизують вивід, якщо вони спрямовані не у відкритий TTY-термінал, а в файл чи конвеєр (pipe). Якщо запуск демона відбувається під керуванням `systemd` або через конвеєр `watcher | tee log.txt`, логи можуть з'являтися із суттєвими затримками. Для усунення цієї проблеми обов'язково викликайте `fflush(stdout)` або використовуйте манипулятор `std::flush` після кожного зчитаного запису.

### 2. Захист від нескінченних циклів при збоях сигналів (EINTR)
Системний виклик `poll()` може бути перерваний асинхронним сигналом ОС (наприклад, `SIGCHLD` або `SIGHUP`), повертаючи значення `-1` з `errno = EINTR`. Демон мусить обробляти цей випадок у циклі й прозоро продовжувати опитування подій замість передчасного завершення роботи.

### 3. Атомарність читання записів у пам'яті
Операція `read()` над дескриптором `/dev/kmsg` завжди повертає ровно один повний запис. Якщо виділений буфер у просторі користувача (у нашому прикладі 8192 байти) є меншим за розмір запису ядра з усім словником метаданих sysfs, операція `read()` поверне помилку `EINVAL`. Тому буфер зчитування повинен мати гарантований запас розміру.

---

## Тестування та перевірка роботи

Для збірки та перевірки роботи розробленого демона в операційній системі Linux виконайте наступні команди:

```bash
# Збірка версій на C та C++
gcc -O2 -Wall -Wextra proj-kmsg-watcher.c -o watcher_c
g++ -O2 -Wall -Wextra -std=c++20 proj-kmsg-watcher.cpp -o watcher_cpp

# Запуск демона від імені суперкористувача для доступу до /dev/kmsg
sudo ./watcher_c
```

У сусідньому терміналі згенеруйте тестову подію в ядрі за допомогою утиліти `logger` або прямим записом у `/dev/kmsg`:
```bash
echo "<3>my_test_module: critical hardware fault simulated" | sudo tee /dev/kmsg
```

Демон спостереження миттєво відреагує на подію через виклик `poll()` та виведе відформатований рядок із точною міткою часу, підсистемою та текстом повідомлення.
