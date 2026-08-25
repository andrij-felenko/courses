# ⚙️ Моніторинг створення вузлів пристроїв у devtmpfs та обробка uevent

Обіцянку ядра «коли подія `add` долетіла до вас, вузол у `/dev` уже існує» неможливо перевірити читанням коду — її треба зловити на живій системі. Для цього потрібна невелика утиліта простору користувача: підписатися на ядровий сокет `NETLINK_KOBJECT_UEVENT`, дочекатися події гарячого підключення чи вилучення обладнання, зібрати з поля `DEVNAME` шлях у `/dev` і тієї ж миті звірити метадані вузла (`st_rdev`, `st_mode`, `st_uid`, `st_gid`) з мажорним і мінорним номерами, які ядро надіслало в самій події. Розбіжність між ними — і є те, що ми шукаємо.

## Архітектурний задум та системні виклики

Створивши новий вузол у файловій системі `devtmpfs`, підсистема ядра `driver core` розсилає слухачам текстовий пакет через протокол `NETLINK_KOBJECT_UEVENT`. Звідси й порядок кроків програми:

1. **Створення сокета Netlink:** Відкриває сокет з сімейства `AF_NETLINK` (або `PF_NETLINK`), вказуючи тип `SOCK_RAW` та специфічний ядровий протокол `NETLINK_KOBJECT_UEVENT`.
2. **Підписка на групи трансляції:** Заповнює структуру `struct sockaddr_nl`, де у полі `nl_groups` вказує бітову маску `1` (що відповідає групі ядрових трансляцій `kernel uevent multicast group`), і прив'язує сокет викликом `bind()`.
3. **Обробка буфера повідомлення:** У нескінченному циклі зчитує з сокета сирий потік байтів у буфер за допомогою системного виклику `recv()`. Буфер містить послідовність рядків, розділених нульовим байтом (`\0`), у форматі `KEY=VALUE` (зокрема `ACTION`, `DEVNAME`, `SUBSYSTEM`, `SEQNUM`, `MAJOR`, `MINOR`).
4. **Перевірка у devtmpfs:** При отриманні події `ACTION=add` програма витягує відносний шлях з `DEVNAME` (наприклад, `bus/usb/001/005` або `nvme0n1p1`), будує абсолютний шлях `/dev/<DEVNAME>` та виконує системний виклик `lstat()`.
5. **Валідація метаданих:** Витягує з поля `st.st_rdev` мажорний та мінорний номери за допомогою канонічних макросів `major()` та `minor()`, зіставляючи їх із числовими значеннями `MAJOR` та `MINOR`, які були відправлені ядром через Netlink.

## Практична реалізація: мови C та C++

Нижче наведено робочі реалізації монітора мовами C (стандарт C11) та C++ (стандарт C++20):

:::tabs
```c
/* devtmpfs_inspector.c — Перехоплення uevent та перевірка вузлів у devtmpfs (C) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <linux/netlink.h>

#define UEVENT_BUFFER_SIZE 8192

static void inspect_devtmpfs_node(const char *devname, unsigned int expected_maj, unsigned int expected_min) {
    char full_path[512];
    struct stat st;

    snprintf(full_path, sizeof(full_path), "/dev/%s", devname);

    /* Використовуємо lstat, щоб не слідувати за можливими символьними посиланнями */
    if (lstat(full_path, &st) < 0) {
        fprintf(stderr, "  [VFS Check] Failed to lstat path %s: %s (node missing in devtmpfs)\n",
                full_path, strerror(errno));
        return;
    }

    unsigned int actual_maj = major(st.st_rdev);
    unsigned int actual_min = minor(st.st_rdev);

    const char *type_str = S_ISCHR(st.st_mode) ? "CHARACTER" :
                           S_ISBLK(st.st_mode) ? "BLOCK" : "OTHER";

    printf("  [VFS Check] Path: %s\n", full_path);
    printf("              Type: %s | Mode: 0%o | UID: %d | GID: %d\n",
           type_str, st.st_mode & 07777, st.st_uid, st.st_gid);
    printf("              Major:Minor -> Kernel: %u:%u | devtmpfs: %u:%u\n",
           expected_maj, expected_min, actual_maj, actual_min);

    if (actual_maj == expected_maj && actual_min == expected_min) {
        printf("              STATUS: MATCH (devtmpfs node verified successfully)\n");
    } else {
        printf("              STATUS: MISMATCH (Kernel and devtmpfs dev_t differ!)\n");
    }
}

int main(void) {
    int fd = socket(PF_NETLINK, SOCK_RAW, NETLINK_KOBJECT_UEVENT);
    if (fd < 0) {
        perror("socket(PF_NETLINK) failed");
        return EXIT_FAILURE;
    }

    /* Налаштовуємо більший розмір приймального буфера сокета */
    int rcvbuf = 1024 * 1024;
    if (setsockopt(fd, SOL_SOCKET, SO_RCVBUFFORCE, &rcvbuf, sizeof(rcvbuf)) < 0) {
        setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));
    }

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;
    sa.nl_groups = 1; /* Kernel Multicast uevents group */

    if (bind(fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("bind failed");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("=== Listening for Kernel Uevents and inspecting devtmpfs (/dev) ===\n");

    char buffer[UEVENT_BUFFER_SIZE];
    while (1) {
        ssize_t len = recv(fd, buffer, sizeof(buffer) - 1, 0);
        if (len <= 0) {
            if (len < 0 && errno == EINTR) continue;
            perror("recv failed");
            break;
        }

        buffer[len] = '\0';

        char *action = NULL;
        char *devname = NULL;
        unsigned int maj = 0, min = 0;

        char *ptr = buffer;
        while (ptr < buffer + len) {
            if (strncmp(ptr, "ACTION=", 7) == 0) action = ptr + 7;
            else if (strncmp(ptr, "DEVNAME=", 8) == 0) devname = ptr + 8;
            else if (strncmp(ptr, "MAJOR=", 6) == 0) maj = (unsigned int)atoi(ptr + 6);
            else if (strncmp(ptr, "MINOR=", 6) == 0) min = (unsigned int)atoi(ptr + 6);

            ptr += strlen(ptr) + 1;
        }

        if (action && devname) {
            printf("\n[NETLINK Event] Action: %s | Devname: %s | DevT: %u:%u\n",
                   action, devname, maj, min);

            if (strcmp(action, "add") == 0) {
                /* Оборонна пауза: ядро гарантує, що вузол уже створено (див. розбір нижче) */
                usleep(1000);
                inspect_devtmpfs_node(devname, maj, min);
            }
        }
    }

    close(fd);
    return EXIT_SUCCESS;
}
```
```cpp
// devtmpfs_inspector.cpp — Перехоплення uevent та перевірка вузлів у devtmpfs (C++)
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <system_error>
#include <thread>
#include <chrono>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <linux/netlink.h>

namespace fs = std::filesystem;

class NetlinkSocket {
    int fd_ = -1;

public:
    explicit NetlinkSocket(int protocol) {
        fd_ = ::socket(PF_NETLINK, SOCK_RAW, protocol);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to create netlink socket");
        }

        int rcvbuf = 1024 * 1024;
        ::setsockopt(fd_, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));

        sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;
        sa.nl_groups = 1;

        if (::bind(fd_, reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "Failed to bind netlink socket");
        }
    }

    ~NetlinkSocket() {
        if (fd_ >= 0) ::close(fd_);
    }

    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;

    [[nodiscard]] int get() const noexcept { return fd_; }
};

struct UeventPayload {
    std::string action;
    std::string devname;
    unsigned int major_num = 0;
    unsigned int minor_num = 0;
};

static void inspect_node(const UeventPayload& event) {
    fs::path full_path = fs::path("/dev") / event.devname;

    struct stat st;
    if (::lstat(full_path.c_str(), &st) < 0) {
        std::cerr << "  [VFS Check] Failed to lstat path: " << full_path << " (Node absent in devtmpfs)\n";
        return;
    }

    const unsigned int actual_maj = major(st.st_rdev);
    const unsigned int actual_min = minor(st.st_rdev);
    const std::string_view type_str = S_ISCHR(st.st_mode) ? "CHARACTER" :
                                      S_ISBLK(st.st_mode) ? "BLOCK" : "OTHER";

    std::cout << "  [VFS Check] Path: " << full_path.string() << "\n"
              << "              Type: " << type_str << " | Mode: 0" << std::oct << (st.st_mode & 07777) << std::dec
              << " | UID: " << st.st_uid << " | GID: " << st.st_gid << "\n"
              << "              Major:Minor -> Kernel: " << event.major_num << ":" << event.minor_num
              << " | devtmpfs: " << actual_maj << ":" << actual_min << "\n";

    if (actual_maj == event.major_num && actual_min == event.minor_num) {
        std::cout << "              STATUS: MATCH (Verified)\n";
    } else {
        std::cout << "              STATUS: MISMATCH!\n";
    }
}

int main() {
    try {
        NetlinkSocket socket(NETLINK_KOBJECT_UEVENT);
        std::cout << "=== [C++] Listening for Kernel Uevents and inspecting devtmpfs (/dev) ===\n";

        std::vector<char> buffer(8192);
        while (true) {
            ssize_t len = ::recv(socket.get(), buffer.data(), buffer.size() - 1, 0);
            if (len <= 0) {
                if (len < 0 && errno == EINTR) continue;
                break;
            }
            buffer[len] = '\0';   // остання пара KEY=VALUE теж мусить мати свій '\0'

            UeventPayload event;
            size_t offset = 0;

            while (offset < static_cast<size_t>(len)) {
                std::string_view item(buffer.data() + offset);
                if (item.starts_with("ACTION=")) {
                    event.action = item.substr(7);
                } else if (item.starts_with("DEVNAME=")) {
                    event.devname = item.substr(8);
                } else if (item.starts_with("MAJOR=")) {
                    event.major_num = std::stoul(std::string(item.substr(6)));
                } else if (item.starts_with("MINOR=")) {
                    event.minor_num = std::stoul(std::string(item.substr(6)));
                }
                offset += item.size() + 1;
            }

            if (!event.action.empty() && !event.devname.empty()) {
                std::cout << "\n[Uevent] Action: " << event.action << " | Devname: " << event.devname
                          << " | Major:Minor: " << event.major_num << ":" << event.minor_num << "\n";

                if (event.action == "add") {
                    // Оборонна пауза: ядро гарантує, що вузол уже створено (див. розбір нижче)
                    std::this_thread::sleep_for(std::chrono::milliseconds(1));
                    inspect_node(event);
                }
            }
        }
    } catch (const std::exception& ex) {
        std::cerr << "Fatal Error: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

## Покроковий розбір реалізації та аналіз C/C++ конструкцій

Обидві версії роблять те саме, але кожна — засобами своєї мови, і різниця між ними якраз повчальна:

### Покроковий аналіз С-версії:

1. **Створення сокета (`socket`):** Виклик `socket(PF_NETLINK, SOCK_RAW, NETLINK_KOBJECT_UEVENT)` запитує у ядра спеціалізований сокет керування. Сокети Netlink не використовують мережевий стек IP, а виступають у ролі ефективного міжпроцесного зв'язку (IPC) між ядром та простором користувача.
2. **Керування розширенням буфера (`setsockopt`):** За допомогою `SO_RCVBUFFORCE` програма запитує збільшення приймального буфера ядра до 1 МіБ. Якщо процес не має привілею `CAP_NET_ADMIN`, функція робить відкат до виклику `SO_RCVBUF`, і тоді запит буде обрізано стелею `net.core.rmem_max`. Це захищає утиліту від втрати подій (помилка `ENOBUFS`) при масовому підключенні пристроїв.
3. **Прив'язка до сокета (`bind`):** Поле `sa.nl_groups = 1` каже ядру транслювати цій програмі всі широкомовні події `uevent`.
4. **Розпакування пакетів:** Оскільки ядро надсилає буфер, де рядки `KEY=VALUE` відокремлені нульовим байтом `\0`, цикл `while (ptr < buffer + len)` послідовно пересуває вказівник `ptr` на `strlen(ptr) + 1`, зчитуючи всі ключі.
5. **Аналіз VFS за допомогою `lstat`:** Використовується саме `lstat()`, а не `stat()`. Якщо у каталозі `/dev` створено символічне посилання (наприклад, `udev` створив посилання), `stat()` повернув би атрибути цільового файла, тоді як `lstat()` повертає атрибути самого вузла у `devtmpfs`.

### Покроковий аналіз C++ версії:

1. **RAII-обгортка сокета (`NetlinkSocket`):** Клас `NetlinkSocket` інкапсулює файловий дескриптор сокета. Деструктор гарантовано викликає `close()`, усуваючи ризик витоку ресурсів при виникненні винятків (`std::system_error`).
2. **Розбір без копій через `std::string_view`:** Сам обхід пакета не копіює нічого — `item.starts_with()` та `item.substr()` дають легковагові зрізи `std::string_view` безпосередньо над сирим буфером `std::vector<char>`. Копія з'являється лише там, де значення треба пережити наступну ітерацію: `event.action` та `event.devname` — це вже `std::string`.
3. **Безпека шляхів із `<filesystem>`:** Збирання абсолютного шляху виконується за допомогою перевантаженого оператора `/` класу `std::filesystem::path` (`fs::path("/dev") / event.devname`), що гарантує коректність розділювачів каталогів у POSIX-середовищі.

## Глибокий аналіз пасток реалізації та крайніх випадків

Під час реалізації моніторів подій ядра та аналізу файлової системи `devtmpfs` розробники раз у раз наступають на ті самі кілька технічних тонкощів:

### 1. Чому вузол уже на місці — і коли `lstat()` усе одно провалиться

Спокуса вирішити, що між подією та файлом є перегони, велика — але їх немає. Усередині `device_add()` порядок жорсткий: спершу `devtmpfs_create_node()`, який **спить** на `wait_for_completion()`, доки `kdevtmpfs` не виконає `vfs_mknod()`, і лише потім `kobject_uevent(&dev->kobj, KOBJ_ADD)`. Отже, коли Netlink-пакет доходить до нашого `recv()`, вузол у `/dev` уже створено. Виклики `usleep(1000)` та `std::this_thread::sleep_for(1ms)` у коді вище — суто оборонні; прибрати їх безпечно.

Провалитися `lstat()` може з інших причин, і саме їх треба вміти відрізняти:

- **Події без вузла.** Більшість `uevent` приходить від пристроїв без `dev_t` (шини, класи, мережеві інтерфейси). У них немає ключа `DEVNAME` — код мусить пропускати такі пакети, а не вважати їх помилкою.
- **Не той `/dev`.** Якщо монітор запущено в контейнері або chroot, він бачить власну `tmpfs`, а не `devtmpfs` хоста, — Netlink-подія прилетить, а файла не буде ніколи.
- **Гонка на метаданих, а не на існуванні.** `udevd` міняє права та групу вже після події. Тому `st_mode` і `st_gid`, зчитані одразу, покажуть ядрові значення (`0600`, `root:root`), а секундою пізніше — вже правила `udev`. Читати їх як «остаточні» не можна.
- **`remove`.** На вилученні порядок дзеркальний: `devtmpfs_delete_node()` знімає вузол теж до розсилання події, тож `lstat()` на `ACTION=remove` законно повертає `ENOENT` — це не збій.

### 2. Розкодування номерів пристроїв (major та minor)

У сучасному ядрі Linux тип `dev_t` має розмірність 32 біти (історично 16 біт). Розподіл бітів у `dev_t` не є простими 16 бітами major і 16 бітами minor. Ядро використовує схему: 12 біт під major та 20 біт під minor.

Спроба самостійно виконувати бітові зсуви типу `(dev >> 8)` призводить до некоректного визначення мінорних номерів пристроїв, чий номер перевищує 255. Завжди слід використовувати канонічні макроси `#include <sys/sysmacros.h>`:

- `major(dev_t dev)` — розпаковує мажорний номер пристрою.
- `minor(dev_t dev)` — розпаковує мінорний номер пристрою.

### 3. Переповнення буфера сокета Netlink (ENOBUFS)

Під час масової ініціалізації обладнання (наприклад, під час підключення складного USB-концентратора або ініціалізації дискового масиву RAID) ядро відправляє сотні сповіщень `uevent` на секунду. Якщо сокет `NETLINK_KOBJECT_UEVENT` має стандартний розмір приймального буфера (типове значення `sysctl net.core.rmem_default` — 212 992 байти, тобто 208 КіБ), під час сплеску подій буфер переповнюється, і системний виклик `recv()` повертає помилку `ENOBUFS` (No buffer space available).

Для захисту від втрати подій утиліти повинні збільшувати розмір буфера сокета за допомогою системного виклику `setsockopt(fd, SOL_SOCKET, SO_RCVBUFFORCE, &rcvbuf, sizeof(rcvbuf))`. Прапор `SO_RCVBUFFORCE` дозволяє процесам із привілеями `CAP_NET_ADMIN` перевищувати системний ліміт `sysctl net.core.rmem_max`.

### 4. Практичне тестування утиліти в Linux

Для компіляції та запуску утиліти виконайте такі команди:

```bash
# Компіляція C-версії
gcc -O2 -Wall -Wextra devtmpfs_inspector.c -o devtmpfs_inspector_c

# Компіляція C++ версії
g++ -O2 -Wall -Wextra -std=c++20 devtmpfs_inspector.cpp -o devtmpfs_inspector_cpp

# Запуск монітора з правами root (необхідно для підписки на Netlink uevents)
sudo ./devtmpfs_inspector_c
```

Після запуску відкрийте сусіднє вікно терміналу та підключіть будь-який USB-накопичувач або створіть віртуальний loop-пристрій за допомогою команди `sudo losetup -f /tmp/dummy.img` (кожен із яких викликає `device_add()` у ядрі та генерує uevent). Монітор негайно перехопить подію створення та виведе верифікований стан вузла у `devtmpfs`.
