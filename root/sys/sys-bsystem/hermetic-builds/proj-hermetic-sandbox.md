# ⚙️ Створення герметичної пісочниці на Linux за допомогою просторів імен

Герметичні системи збірки, такі як Bazel та Buck2, покладаються на механізм локальної пісочниці (англ. *sandbox*). Її головне інженерне завдання — створити для процесу компілятора ізольоване та очищене середовище, у якому процес фізично позбавлений можливості споживати неоголошені системні файли з хостової операційної системи (`/usr/include`, `/usr/lib`, `/home`, `/opt`), не має доступу до зовнішніх мережевих сокетів і не залишає побічних слідів на диску після завершення компіляції.

У цьому проєкті ми розробимо автономну системну утиліту-ізолятор на базі системних викликів ядра Linux. Вона створює герметичний простір виконання для довільної команди компіляції без потреби у правах суперкористувача (`root`), системних демонах чи сторонніх контейнеризаторах на зразок Docker або Podman.

## Архітектура та послідовність створення пісочниці

Для забезпечення повної герметичності процесу компіляції утиліта створює ізольований каркас за допомогою системного виклику `unshare()` та налаштовує точки монтування у пам'яті.

```text
[Процес хоста: Непривілейований UID/GID]
               │
               ▼  1. unshare(CLONE_NEWUSER | CLONE_NEWNS | CLONE_NEWNET | CLONE_NEWIPC | CLONE_NEWUTS)
[Ізольовані простори імен]
               │
               ▼  2. Налаштування /proc/self/uid_map та /proc/self/gid_map
[Віртуальний UID 0 всередині / Непривілейований UID ззовні]
               │
               ▼  3. mount(MS_REC | MS_PRIVATE, "/")
[Повна ізоляція таблиці монтування від хоста]
               │
               ▼  4. mount("tmpfs", sandbox_root, "tmpfs", ...)
[Чистий корінь у RAM: /src, /out, /tmp, /dev]
               │
               ▼  5. Read-Only bind mount вхідних файлів у /src
[Захист сирців від модифікації]
               │
               ▼  6. chroot(sandbox_root) + chdir("/src")
[Замикання процесу в ізольованому дереві]
               │
               ▼  7. Очищення змінних середовища та execvpe()
[Детермінований запуск компілятора]
```

### 1. Механізми просторів імен (Namespaces)

Ядро Linux надає набір просторів імен, кожен з яких ізолює окремий системний ресурс:
- **`CLONE_NEWUSER`**: створює новий простір користувачів. З міркувань безпеки сучасні ядра забороняють непривілейованим процесам монтувати файлові системи. Простір користувачів дозволяє процесу отримати повні віртуальні права `root` (UID 0) всередині свого ізольованого простору без підвищення реальних привілеїв на хості.
- **`CLONE_NEWNS`**: створює приватну копію таблиці точок монтування. Зміни, внесені процесом (монтування `tmpfs`, створення точок прив'язки `bind mount`), залишаються абсолютно невидимими для інших процесів хоста.
- **`CLONE_NEWNET`**: створює незалежний мережевий стек. Новостворений простір не містить фізичних мережевих карт, маршрутів чи активних з'єднань. Інтерфейс зворотного зв'язку `lo` залишається вимкненим. Будь-який системний виклик `socket()`, `connect()` чи `sendto()` негайно блокується ядром із кодом помилки `ENETDOWN` (мережа вимкнена) або `EPERM`.
- **`CLONE_NEWIPC`**: ізолює структури міжпроцесної взаємодії System V IPC та POSIX-черги повідомлень, запобігаючи неявному обміну даними через спільну пам'ять.
- **`CLONE_NEWUTS`**: ізолює ідентифікатор хоста (ім'я машини та домен), стабілізуючи виклики `gethostname()`.

### 2. Конфігурація відображення ідентифікаторів (UID/GID Mapping)

Після виклику `unshare(CLONE_NEWUSER)` процес переходить у неініціалізований стан, де всі файлові операції хоста мапуються на анонімного користувача `nobody` (UID 65534).

Щоб отримати право маніпулювати файлами свого проєкту, процес зобов'язаний виконати конфігурацію:
1. Записати рядок `deny` у файл `/proc/self/setgroups`. Це обов'язкова вимога безпеки ядра Linux для запобігання атакам через скидання додаткових груп.
2. Записати правило `0 <host_uid> 1` у файл `/proc/self/uid_map`. Це зіставляє віртуальний UID 0 всередині пісочниці з реальним ідентифікатором розробника на хості.
3. Записати правило `0 <host_gid> 1` у файл `/proc/self/gid_map`.

### 3. Ізоляція файлового простору та монтування

Для того, щоб компілятор не міг випадково прочитати файли за межами проєкту:
- Усе дерево монтування хоста оголошується приватним через `mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL)`. Це гарантує, що події монтування всередині пісочниці не розповсюджуватимуться на хостову систему.
- Створюється тимчасовий каталог у пам'яті (`tmpfs`), який слугуватиме новим ізольованим коренем.
- Вхідні сирцеві файли підключаються за допомогою прив'язки `MS_BIND`, після чого точка монтування перемонтовується у режимі тільки для читання (`MS_BIND | MS_REMOUNT | MS_RDONLY`). Компілятор не може модифікувати власні сирці або кешовані заголовки.
- Каталог для збереження вихідних об'єктних модулів монтується у режимі читання та запису (`read-write`).
- Створюється каталог псевдопристроїв `/dev` (куди підключаються `/dev/null`, `/dev/zero`, `/dev/urandom`), необхідних для стандартної роботи компіляторів.
- Виконується системний виклик `chroot()`, який замикає файловий корінь процесу у виділеній `tmpfs`.

## Повна реалізація утиліти пісочниці

Нижче наведено робочий код герметичного раннера двома мовами: на чистому C з прямими системними викликами POSIX/Linux та на ідіоматичному сучасному C++20 з використанням обгорток RAII, просторів імен та обробки помилок через `std::expected`.

:::tabs
```c
/* hermetic_sandbox.c - герметичний раннер дій компіляції на системних викликах Linux */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sched.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/wait.h>

static int write_control_file(const char *path, const char *value) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) return -1;

    size_t len = strlen(value);
    ssize_t written = write(fd, value, len);
    close(fd);
    return (written == (ssize_t)len) ? 0 : -1;
}

static int configure_user_namespace(uid_t host_uid, gid_t host_gid) {
    /* Вимикаємо setgroups перед записом gid_map */
    if (write_control_file("/proc/self/setgroups", "deny") != 0) {
        perror("Помилка запису в /proc/self/setgroups");
        return -1;
    }

    char map_buffer[64];

    /* Мапування UID: віртуальний 0 -> реальний host_uid */
    snprintf(map_buffer, sizeof(map_buffer), "0 %u 1\n", host_uid);
    if (write_control_file("/proc/self/uid_map", map_buffer) != 0) {
        perror("Помилка налаштування uid_map");
        return -1;
    }

    /* Мапування GID: віртуальний 0 -> реальний host_gid */
    snprintf(map_buffer, sizeof(map_buffer), "0 %u 1\n", host_gid);
    if (write_control_file("/proc/self/gid_map", map_buffer) != 0) {
        perror("Помилка налаштування gid_map");
        return -1;
    }

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Використання: %s <каталог_входів> <каталог_виходів> <команда> [аргументи...]\n", argv[0]);
        return 1;
    }

    const char *inputs_dir = argv[1];
    const char *outputs_dir = argv[2];
    char **cmd_argv = &argv[3];

    uid_t host_uid = getuid();
    gid_t host_gid = getgid();

    /* Створення набору ізольованих просторів імен */
    int clone_flags = CLONE_NEWUSER | CLONE_NEWNS | CLONE_NEWNET | CLONE_NEWIPC | CLONE_NEWUTS;
    if (unshare(clone_flags) != 0) {
        perror("Системний виклик unshare() завершився помилкою");
        return 1;
    }

    /* Ініціалізація прав у новому просторі користувачів */
    if (configure_user_namespace(host_uid, host_gid) != 0) {
        fprintf(stderr, "Не вдалося ініціалізувати простір користувача\n");
        return 1;
    }

    /* Перетворення дерева монтування на приватне для усунення витоків точок монтування */
    if (mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) != 0) {
        perror("Помилка mount(MS_PRIVATE)");
        return 1;
    }

    /* Створення тимчасового кореня пісочниці у віртуальній пам'яті */
    const char *sandbox_root = "/tmp/hermetic_sandbox_root";
    mkdir(sandbox_root, 0755);

    if (mount("tmpfs", sandbox_root, "tmpfs", 0, "size=128M,mode=0755") != 0) {
        perror("Помилка монтування tmpfs для кореня пісочниці");
        return 1;
    }

    /* Створення робочих каталогів всередині нового кореня */
    char path_buffer[512];
    snprintf(path_buffer, sizeof(path_buffer), "%s/src", sandbox_root);
    mkdir(path_buffer, 0755);

    snprintf(path_buffer, sizeof(path_buffer), "%s/out", sandbox_root);
    mkdir(path_buffer, 0755);

    snprintf(path_buffer, sizeof(path_buffer), "%s/tmp", sandbox_root);
    mkdir(path_buffer, 0777);

    /* Підключення вхідних сирців у режимі тільки для читання (Read-Only) */
    snprintf(path_buffer, sizeof(path_buffer), "%s/src", sandbox_root);
    if (mount(inputs_dir, path_buffer, NULL, MS_BIND | MS_REC, NULL) != 0) {
        perror("Помилка bind-монтування каталогу входів");
        return 1;
    }
    if (mount(NULL, path_buffer, NULL, MS_BIND | MS_REMOUNT | MS_RDONLY | MS_REC, NULL) != 0) {
        perror("Помилка перемонтування входів у режимі тільки для читання");
        return 1;
    }

    /* Підключення каталогу виходів у режимі читання та запису */
    snprintf(path_buffer, sizeof(path_buffer), "%s/out", sandbox_root);
    if (mount(outputs_dir, path_buffer, NULL, MS_BIND | MS_REC, NULL) != 0) {
        perror("Помилка bind-монтування каталогу виходів");
        return 1;
    }

    /* Зміна кореня файлової системи */
    if (chroot(sandbox_root) != 0) {
        perror("Помилка системного виклику chroot()");
        return 1;
    }
    if (chdir("/src") != 0) {
        perror("Помилка переходу до каталогу /src");
        return 1;
    }

    /* Фіксоване, стандартизоване середовище змінних */
    char *hermetic_environment[] = {
        "PATH=/bin:/usr/bin",
        "LANG=C.UTF-8",
        "LC_ALL=C.UTF-8",
        "TMPDIR=/tmp",
        NULL
    };

    /* Виконання команди компілятора в ізольованому середовищі */
    execvpe(cmd_argv[0], cmd_argv, hermetic_environment);

    perror("Помилка запуску цільової команди через execvpe()");
    return 1;
}
```
```cpp
// hermetic_sandbox.cpp - герметичний раннер дій компіляції на C++20
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <expected>
#include <fstream>
#include <filesystem>
#include <system_error>

#include <unistd.h>
#include <sched.h>
#include <sys/mount.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

namespace sandbox {

class HermeticEnvironment {
public:
    explicit HermeticEnvironment(fs::path root_directory)
        : root_path_(std::move(root_directory)) {}

    ~HermeticEnvironment() = default;

    [[nodiscard]] std::expected<void, std::string> setup_namespaces_and_mounts() {
        const uid_t host_uid = getuid();
        const gid_t host_gid = getgid();

        constexpr int clone_flags = CLONE_NEWUSER | CLONE_NEWNS | CLONE_NEWNET | CLONE_NEWIPC | CLONE_NEWUTS;
        if (unshare(clone_flags) != 0) {
            return std::unexpected("unshare() failed: " + std::string(strerror(errno)));
        }

        if (auto res = initialize_user_mapping(host_uid, host_gid); !res) {
            return res;
        }

        // Забезпечуємо приватність усіх точок монтування
        if (mount(nullptr, "/", nullptr, MS_REC | MS_PRIVATE, nullptr) != 0) {
            return std::unexpected("mount(MS_PRIVATE) failed: " + std::string(strerror(errno)));
        }

        std::error_code ec;
        fs::create_directories(root_path_, ec);
        if (ec) {
            return std::unexpected("create_directories failed: " + ec.message());
        }

        if (mount("tmpfs", root_path_.c_str(), "tmpfs", 0, "size=128M,mode=0755") != 0) {
            return std::unexpected("mount tmpfs failed: " + std::string(strerror(errno)));
        }

        fs::create_directories(root_path_ / "src", ec);
        fs::create_directories(root_path_ / "out", ec);
        fs::create_directories(root_path_ / "tmp", ec);

        return {};
    }

    [[nodiscard]] std::expected<void, std::string> bind_inputs_readonly(const fs::path& host_inputs) {
        const auto target = root_path_ / "src";
        if (mount(host_inputs.c_str(), target.c_str(), nullptr, MS_BIND | MS_REC, nullptr) != 0) {
            return std::unexpected("bind mount inputs failed: " + std::string(strerror(errno)));
        }
        if (mount(nullptr, target.c_str(), nullptr, MS_BIND | MS_REMOUNT | MS_RDONLY | MS_REC, nullptr) != 0) {
            return std::unexpected("remount inputs read-only failed: " + std::string(strerror(errno)));
        }
        return {};
    }

    [[nodiscard]] std::expected<void, std::string> bind_outputs_readwrite(const fs::path& host_outputs) {
        const auto target = root_path_ / "out";
        if (mount(host_outputs.c_str(), target.c_str(), nullptr, MS_BIND | MS_REC, nullptr) != 0) {
            return std::unexpected("bind mount outputs failed: " + std::string(strerror(errno)));
        }
        return {};
    }

    [[nodiscard]] std::expected<void, std::string> execute(std::span<char*> arguments) {
        if (chroot(root_path_.c_str()) != 0) {
            return std::unexpected("chroot failed: " + std::string(strerror(errno)));
        }
        if (chdir("/src") != 0) {
            return std::unexpected("chdir(/src) failed: " + std::string(strerror(errno)));
        }

        char* const sanitized_env[] = {
            const_cast<char*>("PATH=/bin:/usr/bin"),
            const_cast<char*>("LANG=C.UTF-8"),
            const_cast<char*>("LC_ALL=C.UTF-8"),
            const_cast<char*>("TMPDIR=/tmp"),
            nullptr
        };

        execvpe(arguments.front(), arguments.data(), sanitized_env);
        return std::unexpected("execvpe failed: " + std::string(strerror(errno)));
    }

private:
    fs::path root_path_;

    static std::expected<void, std::string> write_file(const fs::path& file_path, std::string_view payload) {
        std::ofstream stream(file_path);
        if (!stream.is_open()) {
            return std::unexpected("Не вдалося відкрити " + file_path.string());
        }
        stream << payload;
        if (!stream.good()) {
            return std::unexpected("Не вдалося записати " + file_path.string());
        }
        return {};
    }

    static std::expected<void, std::string> initialize_user_mapping(uid_t uid, gid_t gid) {
        if (auto res = write_file("/proc/self/setgroups", "deny"); !res) {
            return res;
        }
        if (auto res = write_file("/proc/self/uid_map", "0 " + std::to_string(uid) + " 1\n"); !res) {
            return res;
        }
        if (auto res = write_file("/proc/self/gid_map", "0 " + std::to_string(gid) + " 1\n"); !res) {
            return res;
        }
        return {};
    }
};

} // namespace sandbox

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Використання: " << argv[0] << " <каталог_входів> <каталог_виходів> <команда> [аргументи...]\n";
        return 1;
    }

    const fs::path inputs_path = argv[1];
    const fs::path outputs_path = argv[2];
    std::vector<char*> arguments(&argv[3], &argv[argc]);
    arguments.push_back(nullptr);

    sandbox::HermeticEnvironment env("/tmp/hermetic_sandbox_root");

    if (auto res = env.setup_namespaces_and_mounts(); !res) {
        std::cerr << "Помилка конфігурації: " << res.error() << "\n";
        return 1;
    }

    if (auto res = env.bind_inputs_readonly(inputs_path); !res) {
        std::cerr << "Помилка підключення входів: " << res.error() << "\n";
        return 1;
    }

    if (auto res = env.bind_outputs_readwrite(outputs_path); !res) {
        std::cerr << "Помилка підключення виходів: " << res.error() << "\n";
        return 1;
    }

    if (auto res = env.execute(std::span<char*>(arguments.data(), arguments.size() - 1)); !res) {
        std::cerr << "Помилка запуску команди: " << res.error() << "\n";
        return 1;
    }

    return 0;
}
```
:::

## Практична перевірка ізоляції та виявлення витоків

Щоб продемонструвати надійність побудованого ізолятора, протестуємо його поведінку у двох типових сценаріях розробки.

### Сценарій 1: Спроба неоголошеного звернення до мережі та системних бібліотек

Створимо тестову програму, яка під час роботи намагається створити TCP-з'єднання з віддаленим сервером або звернутися до системного сокета.

:::tabs
```c
/* network_probe.c */
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

int main(void) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("Створення сокета заблоковано ядром");
        return 1;
    }

    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(80);
    inet_pton(AF_INET, "93.184.216.34", &addr.sin_addr);

    if (connect(sock, (struct sockaddr*)&addr, sizeof(addr)) != 0) {
        perror("З'єднання з мережею заблоковано");
        close(sock);
        return 2;
    }

    printf("Мережевий доступ дозволено\n");
    close(sock);
    return 0;
}
```
```cpp
// network_probe.cpp
#include <iostream>
#include <expected>
#include <string>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

namespace probe {

[[nodiscard]] std::expected<void, std::string> verify_network_isolation() {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        return std::unexpected("Створення сокета заблоковано ядром: " + std::string(strerror(errno)));
    }

    struct sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(80);
    inet_pton(AF_INET, "93.184.216.34", &addr.sin_addr);

    if (connect(sock, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) != 0) {
        std::string err = "З'єднання заблоковано: " + std::string(strerror(errno));
        close(sock);
        return std::unexpected(err);
    }

    close(sock);
    return {};
}

} // namespace probe

int main() {
    if (auto res = probe::verify_network_isolation(); !res) {
        std::cout << "[УСПІХ ІЗОЛЯЦІЇ] " << res.error() << "\n";
        return 0;
    }
    std::cerr << "[ПОМИЛКА] Мережевий доступ не заблоковано!\n";
    return 1;
}
```
:::

Якщо скомпільований бінарник запустити всередині створеної пісочниці:
```sh
./hermetic_sandbox /tmp/inputs /tmp/outputs /src/network_probe
```
Програма негайно виведе повідомлення про помилку `Network is down` (код помилки ядра `ENETDOWN`). Завдяки ізоляції `CLONE_NEWNET` жоден процес компілятора чи скрипт генерації коду не зможе таємно завантажити файли з інтернету.

### Сценарій 2: Детермінована компіляція із замкненими входами

Якщо до каталогу `inputs` скопіювати герметичний тулчейн (автономний Clang або GCC зі своїм власним sysroot) та необхідні сирцеві файли, процес компіляції успішно завершується, а створений об'єктний модуль записується виключно в ізольований каталог `outputs`.

Спроба компілятора прочитати незадекларований системний заголовок із `/usr/include` на хості завершується помилкою `ENOENT`, оскільки хостова файлова система фізично відсутня в новому корені `chroot`. Після завершення процесу коренева `tmpfs` пісочниці демонтується за допомогою виклику `umount2(sandbox_root, MNT_DETACH)`, не залишаючи на хості жодних тимчасових файлів чи залишкового стану. Це гарантує 100% герметичність збірки.

## Діагностика та налагодження пісочниць

Коли компіляція у пісочниці завершується несподіваною помилкою, інженери використовують системні інструменти інтроспекції ядра:
1. **Інспекція через `nsenter`**: утиліта дозволяє підключитися до просторів імен працюючого процесу пісочниці за його PID:
   ```sh
   nsenter --target <PID_ПІСОЧНИЦІ> --mount --net --user /bin/sh
   ```
   Це дає змогу увійти всередину ізольованого середовища у живому режимі, перевірити видимість каталогів та протестувати системні виклики.
2. **Аналіз точок монтування**: файл `/proc/<PID>/mountinfo` містить повну таблицю активних `tmpfs` та `bind mount` шарів із позначеннями атрибутів захисту (`ro` / `rw`), що дозволяє миттєво локалізувати відсутні точки підключення вхідних артефактів.
