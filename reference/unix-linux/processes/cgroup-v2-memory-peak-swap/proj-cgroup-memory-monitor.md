# ⚙️ Моніторинг лімітів та подій пам'яті cgroup v2 на C та C++

Ця вставка містить практичні приклади програм мовами C та C++, які показують, як системні сервіси та контейнерні рантайми взаємодіють з інтерфейсом cgroups v2 memory. Вона необхідна розробникам системного програмного забезпечення, системним програмістам та авторам контейнерних оркестраторів, яким потрібно налаштовувати ліміти пам'яті програмно та відстежувати події перевищення порогів (`memory.high`, `memory.max`, `oom_kill`) у реальному часі без постійного активного опитування (polling), використовуючи системний виклик `epoll()`.

## 1. Архітектура асинхронного моніторингу подій у cgroups v2

У багатьох практичних сценаріях розробники демонів та демонів-супервізорів роблять помилку, періодично зчитуючи вміст файлу `memory.events` у нескінченному циклі з затримкою `sleep()`. Такий підхід створює зайве навантаження на систему через постійне створення контексту системних викликів й водночас не гарантує миттєвої реакції на сплески споживання пам'яті, оскільки подія може відбутися та зникнути між інтервалами опитування.

Контролер пам'яті в cgroups v2 реалізує асинхронну семантику сповіщень на основі підсистеми `kernfs`. Коли у ядрі відбувається подія, що змінює лічильники у файлі `memory.events` (наприклад, перевищення м'якої межі `memory.high`, виклик direct reclaim при досягненні `memory.max` або спрацьовування cgroup OOM Killer), ядро надсилає сповіщення на файловий дескриптор.

З погляду системних викликів POSIX/Linux файли подій у cgroupfs не повертають звичного `EPOLLIN` при зміні, оскільки вони не є звичайними файлами із потоком даних. Натомість ядро виставляє виняткову подію `EPOLLPRI` (Out-of-band data або виняткові дані) та прапорець `EPOLLERR`.

Для відловлювання таких подій програма відкриває файл `memory.events` у неблокуючому режимі (`O_RDONLY | O_NONBLOCK`) і реєструє отриманий файловий дескриптор у селекторі `epoll()` з маскою подій `EPOLLPRI | EPOLLERR`. Коли у ядрі відбувається інкремент будь-якого лічильника, системний виклик `epoll_wait()` миттєво розблоковує потік виконання, дозволяючи прочитати оновлені текстові метрики без жодних затримок.

## 2. Послідовність дій системного монітора

Наведений нижче практичний приклад реалізує повну послідовність кроків управління та моніторингу cgroup пам'яті:

1. **Створення каталогу cgroup:** Програма створює новий каталог cgroup за шляхом `/sys/fs/cgroup/test_memcg`. Якщо каталог вже існує (наприклад, після попереднього запуску), помилка `EEXIST` обробляється коректно без зупинки виконання.
2. **Конфігурування межових лімітів пам'яті:** Програма записує у файл `memory.high` значення 50 МБ (52428800 байтів), а у файл `memory.max` значення 100 МБ (104857600 байтів). Це створює двостадійну схему захисту: при перетині 50 МБ ядро почне застосовувати затримки (throttling), а при спробі перевищити 100 МБ спрацює режим прямого витіснення або OOM Killer.
3. **Ініціалізація epoll та відкриття файлу подій:** Файл `memory.events` відкривається прапорцем `O_NONBLOCK`. Дескриптор додається до селектора `epoll()` за допомогою виклику `epoll_ctl()` з реєстрацією маски `EPOLLPRI`.
4. **Цикл очікування та обробка сповіщень:** У системному виклику `epoll_wait()` потік блокується на вказаний таймаут (5 секунд). При поверненні виклику програма перевіряє код повернення: якщо `n > 0`, відбулася ядерна подія cgroup; якщо `n == 0`, сплив таймаут і виконується планове опитування.
5. **Зчитання та аналіз показників:** Після розблокування програма виконує повернення позиції читання на початок файлу (`lseek(fd, 0, SEEK_SET)`) та зчитує оновлений вміст `memory.events`, а також поточні значення `memory.current` та `memory.peak`.

Даний механізм лежить в основі системних оркестраторів (наприклад, Kubelet у Kubernetes, systemd resource monitors, або автоскейлерів контейнерних платформ), які реагують на виникнення тиску на пам'ять до того, як ядро вдасться до примусового знищення процесів.

Нижче наведено робочі реалізації мовами C та C++ у вигляді незалежних ідіоматичних блоків.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/epoll.h>
#include <errno.h>

#define CGROUP_PATH "/sys/fs/cgroup/test_memcg"
#define MAX_EVENTS 5
#define BUFFER_SIZE 1024

static int write_cgroup_file(const char *subpath, const char *value) {
    char fullpath[256];
    snprintf(fullpath, sizeof(fullpath), "%s/%s", CGROUP_PATH, subpath);
    
    int fd = open(fullpath, O_WRONLY);
    if (fd < 0) {
        perror("open for write failed");
        return -1;
    }
    
    ssize_t len = strlen(value);
    if (write(fd, value, len) != len) {
        perror("write to cgroup file failed");
        close(fd);
        return -1;
    }
    
    close(fd);
    return 0;
}

static void read_and_print_file(const char *subpath, const char *label) {
    char fullpath[256];
    char buf[BUFFER_SIZE];
    snprintf(fullpath, sizeof(fullpath), "%s/%s", CGROUP_PATH, subpath);
    
    int fd = open(fullpath, O_RDONLY);
    if (fd < 0) return;
    
    ssize_t bytes = read(fd, buf, sizeof(buf) - 1);
    if (bytes > 0) {
        buf[bytes] = '\0';
        printf("--- %s (%s) ---\n%s", label, subpath, buf);
    }
    close(fd);
}

int main(void) {
    // 1. Створення каталогу cgroup
    if (mkdir(CGROUP_PATH, 0755) < 0 && errno != EEXIST) {
        perror("mkdir cgroup failed");
        return EXIT_FAILURE;
    }
    printf("Cgroup створено: %s\n", CGROUP_PATH);

    // 2. Налаштування memory.high (50MB) та memory.max (100MB)
    if (write_cgroup_file("memory.high", "52428800") < 0 ||
        write_cgroup_file("memory.max", "104857600") < 0) {
        fprintf(stderr, "Помилка встановлення лімітів пам'яті\n");
        return EXIT_FAILURE;
    }

    // 3. Відкриття memory.events для моніторингу через epoll
    char events_path[256];
    snprintf(events_path, sizeof(events_path), "%s/memory.events", CGROUP_PATH);
    int events_fd = open(events_path, O_RDONLY | O_NONBLOCK);
    if (events_fd < 0) {
        perror("open memory.events failed");
        return EXIT_FAILURE;
    }

    int epoll_fd = epoll_create1(0);
    if (epoll_fd < 0) {
        perror("epoll_create1 failed");
        close(events_fd);
        return EXIT_FAILURE;
    }

    struct epoll_event ev;
    ev.events = EPOLLPRI | EPOLLERR;
    ev.data.fd = events_fd;
    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, events_fd, &ev) < 0) {
        perror("epoll_ctl failed");
        close(epoll_fd);
        close(events_fd);
        return EXIT_FAILURE;
    }

    printf("Монітор запущено. Очікування подій cgroup memory...\n");

    // 4. Цикл очікування подій
    struct epoll_event ready_events[MAX_EVENTS];
    int n = epoll_wait(epoll_fd, ready_events, MAX_EVENTS, 5000); // 5 секунд таймаут
    if (n < 0) {
        perror("epoll_wait failed");
    } else if (n == 0) {
        printf("Таймаут очікування подій. Опитування поточних показників:\n");
    } else {
        printf("Отримано сповіщення про зміну memory.events!\n");
    }

    // Зчитуємо та показуємо поточний стан
    read_and_print_file("memory.events", "Події пам'яті");
    read_and_print_file("memory.current", "Поточне споживання RAM");
    read_and_print_file("memory.peak", "Пікове споживання RAM");

    // Очищення ресурсів
    close(epoll_fd);
    close(events_fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <array>
#include <filesystem>
#include <system_error>
#include <cerrno>
#include <memory>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/epoll.h>

namespace fs = std::filesystem;

class ScopedFd {
    int m_fd{-1};
public:
    explicit ScopedFd(int fd) : m_fd(fd) {}
    ~ScopedFd() {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
    }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            if (m_fd >= 0) ::close(m_fd);
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }
};

class CgroupMemoryMonitor {
    fs::path m_cgroupPath;

    void writeControlFile(std::string_view filename, std::string_view value) {
        fs::path target = m_cgroupPath / filename;
        std::ofstream ofs(target);
        if (!ofs) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Не вдалося відкрити " + target.string());
        }
        ofs << value;
        if (!ofs) {
            throw std::runtime_error("Помилка запису у " + target.string());
        }
    }

    void printControlFile(std::string_view filename, std::string_view label) const {
        fs::path target = m_cgroupPath / filename;
        std::ifstream ifs(target);
        if (!ifs) return;

        std::string content((std::istreambuf_iterator<char>(ifs)),
                             std::istreambuf_iterator<char>());
        std::cout << "--- " << label << " (" << filename << ") ---\n" << content;
    }

public:
    explicit CgroupMemoryMonitor(fs::path path) : m_cgroupPath(std::move(path)) {}

    void setup(uint64_t highBytes, uint64_t maxBytes) {
        std::error_code ec;
        fs::create_directories(m_cgroupPath, ec);
        if (ec) {
            throw std::system_error(ec, "Не вдалося створити cgroup каталог");
        }
        std::cout << "Cgroup створено: " << m_cgroupPath << "\n";

        writeControlFile("memory.high", std::to_string(highBytes));
        writeControlFile("memory.max", std::to_string(maxBytes));
    }

    void monitorEvents(int timeoutMs) {
        fs::path eventsPath = m_cgroupPath / "memory.events";
        ScopedFd eventsFd(::open(eventsPath.c_str(), O_RDONLY | O_NONBLOCK));
        if (!eventsFd.valid()) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Помилка відкриття memory.events");
        }

        ScopedFd epollFd(::epoll_create1(0));
        if (!epollFd.valid()) {
            throw std::system_error(errno, std::generic_category(), 
                                   "epoll_create1 failed");
        }

        struct epoll_event ev{};
        ev.events = EPOLLPRI | EPOLLERR;
        ev.data.fd = eventsFd.get();
        if (::epoll_ctl(epollFd.get(), EPOLL_CTL_ADD, eventsFd.get(), &ev) < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "epoll_ctl failed");
        }

        std::cout << "Очікування подій пам'яті через epoll...\n";
        std::array<struct epoll_event, 4> readyEvents{};
        int n = ::epoll_wait(epollFd.get(), readyEvents.data(), readyEvents.size(), timeoutMs);

        if (n < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_wait failed");
        } else if (n == 0) {
            std::cout << "Таймаут очікування. Поточні метрики:\n";
        } else {
            std::cout << "Подію виявлено! Оновлені дані cgroup:\n";
        }

        printControlFile("memory.events", "Події пам'яті");
        printControlFile("memory.current", "Поточне споживання RAM");
        printControlFile("memory.peak", "Пікове споживання RAM");
    }
};

int main() {
    try {
        CgroupMemoryMonitor monitor("/sys/fs/cgroup/test_memcg_cpp");
        monitor.setup(52428800, 104857600); // 50MB high, 100MB max
        monitor.monitorEvents(5000);
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

## 3. Детальний аналіз реалізації C та C++

Обидві реалізації забезпечують однаковий алгоритмічний контракт, але демонструють відмінні підходи до керування ресурсами відповідно до ідіом кожної мови:

- **У реалізації мовою C:**
  - Керування файловими дескрипторами виконується вручну через явний виклик `close()`.
  - Усі системні виклики перевіряються на від'ємне значення (`< 0`), а помилки виводяться за допомогою функцій `perror()` або `fprintf(stderr, ...)`.
  - Робота із шляхами у віртуальній файловій системі `cgroupfs` здійснюється за допомогою безпечного форматування рядків через `snprintf()`, що запобігає переповненню буфера.

- **У реалізації мовою C++:**
  - Використовується RAII-обгортка `ScopedFd`, яка гарантує автоматичне закриття файлового дескриптора при виході з області видимості, включаючи випадки виникнення винятків (exception safety).
  - Для створення каталогів та побудови шляхів застосовується стандартний модуль `<filesystem>` (`std::filesystem::path`), що робить код стійким до роздільників шляхів.
  - Усі помилки системних викликів перетворюються у стандартні винятки `std::system_error`, що дозволяє централізовано обробляти збої у головному блоці `try-catch`.

## 4. Ключові особливості та крайові випадки реалізації

Під час розробки моніторів пам'яті cgroup v2 у системних сервісах слід враховувати такі важливі особливості роботи ядра:

1. **Необхідність скидання позиції файлу (seek to start):** У виклику `epoll()` файловий дескриптор `memory.events` сигналізує про виняткову подію. Однак після першого зчитування вмісту позиція файлового вказівника опиняється в кінці файлу (`EOF`). При наступному спрацюванні `epoll_wait()` спроба виклику `read()` повернула б 0 байтів. Щоб прочитати оновлені події без повторного закриття та відкриття файлу, необхідно обов'язково виконати позиціонування на початок за допомогою виклику `lseek(fd, 0, SEEK_SET)` або використовувати `pread()` / `pread64()`.
2. **Делегування прав доступу (Delegation in Rootless Cgroups):** Створення та модифікація каталогів у `/sys/fs/cgroup` стандартно вимагає привілеїв суперкористувача (`root`). Для роботи безпривілейованих демонів системний сервіс (наприклад `systemd-logind` або `systemd --user`) повинен передати каталог cgroup у власність UID цього користувача разом із файлами `cgroup.procs`, `cgroup.threads` і `cgroup.subtree_control`.
3. **Обробка таймаутів та порівняння метрик:** Подія `EPOLLPRI` виставляється підсистемою `kernfs`, на якій побудовано `cgroupfs`, у момент інкременту лічильника. Монітор повинен зберегти зчитаний вміст у власному внутрішньому стані та провести парсинг текстових рядків, порівнявши попередні й нові значення метрик `high`, `max` та `oom_kill`, щоб визначити точний тип події ядра.
4. **Видалення cgroup та обробка сигналів виходу:** Якщо моніторингова cgroup видаляється зовнішнім оркестратором під час очікування в `epoll_wait()`, системний виклик повертає прапорець `EPOLLHUP`. Програма повинна обробляти `EPOLLHUP` як сигнал про завершення життєвого циклу cgroup і коректно вивільняти всі відкриті файлові дескриптори.

## 5. Інтеграція з подійними петлями та BPF

У промислових системних сервісах (таких як `cgroupd`, `cadvisor` чи `datadog-agent`) опитування файлів подій cgroup інтегрується у головну подійну петлю додатка (Event Loop), побудовану на `libuv`, `asio` або сирому `epoll()`.

Завдяки тому, що файловий дескриптор `memory.events` є стандартним дескриптором POSIX, його можна легко реєструвати разом із мережевими сокетами чи сигналами процесів. Це дозволяє створювати єдину асинхронну архітектуру моніторингу ресурсів без виділення окремих потоків під кожен контролер пам'яті.

Крім того, сучасні системи спостереження комбінують `epoll()` з трасуванням ядра через eBPF (`kprobe:mem_cgroup_handle_over_high` або точки трасування підсистеми `vmscan`), що дозволяє фіксувати не лише факт інкременту лічильника в `memory.events`, але й конкретні стеки викликів (stack traces) процесів у ядрі, які спровокували перевищення ліміту.
