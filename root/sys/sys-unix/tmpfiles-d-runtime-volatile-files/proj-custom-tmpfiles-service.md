# ⚙️ Реалізація сервісу з волотильним каталогом: C, C++ та конфігурація systemd

Практична реалізація системного сервісу з використанням ізольованого волотильного каталогу описує повний архітектурний цикл взаємодії між декларативними специфікаціями `tmpfiles.d`, службовим юнітом системного менеджера `systemd` та програмним кодом системного демона на мовах C та C++.

Розробка сучасних системних служб у середовищі Linux вимагає чіткого дотримання принципу найменших привілеїв. Демон не повинен працювати від імені суперкористувача `root`, а його рантайм-стан (доменні сокети UNIX, PID-файли та файли поточного стану) має розміщуватися у виділеному каталозі всередині тимчасової файлової системи `/run`. Оскільки каталог `/run` монтується у пам'яті як `tmpfs` і повністю очищується при кожному перезавантаженні операційної системи, демон покладається на сервіс `systemd-tmpfiles`, який створює необхідну структуру каталогів із належними правами доступу до моменту фактичного запуску коду демона.

---

### 1. Декларативна конфігурація tmpfiles.d

На першому етапі створюється конфігураційний файл специфікації `/usr/lib/tmpfiles.d/appdaemon.conf`. Цей файл описує правила створення волотильного каталогу `/run/appdaemon` та початкових службових файлів під час стадіювання завантаження системи. Декларативний підхід звільняє розробника від написання низькорівневих скриптів ініціалізації мовою Bash та усуває можливі проблеми з відсутністю каталогів після рестарту вузла.

У файлі конфігурації оголошуються наступні правила:

```text
# /usr/lib/tmpfiles.d/appdaemon.conf
# Тип  Шлях                  Режим  Власник    Група      Вік  Аргумент
d      /run/appdaemon        0755   appuser    appuser    -    -
f      /run/appdaemon/status 0644   appuser    appuser    -    Initializing...
```

Перший рядок конфігурації (тип `d`) вказує на необхідність створення каталогу `/run/appdaemon` із вісімковими правами доступу `0755`. Власником каталогу виступає системний користувач `appuser` та одноіменна група `appuser`. Другий рядок (тип `f`) створює початковий файл стану `/run/appdaemon/status` із правами `0644` та записує в нього текстовий індикатор початкової ініціалізації. Завдяки цьому під час старту службового процесу каталог уже існує і має суворо визначеного власника.

Якщо у системі виникає потреба обмежити доступ до рантайм-каталогу лише для службового користувача без надання прав на читання іншим користувачам (Others), режим змінюється на `0700` чи `0750`. При цьому `systemd-tmpfiles` автоматично застосовує виправлення прав доступу при кожному запуску команди створення, навіть якщо сам каталог вже був створений раніше.

---

### 2. Конфігурація службового юніта systemd

Для забезпечення правильної послідовності завантаження створюється файл системного юніта `/usr/lib/systemd/system/appdaemon.service`. Юніт явним чином оголошує залежність від служби `systemd-tmpfiles-setup.service`, що гарантує існування каталогу `/run/appdaemon` до моменту виклику виконуваного бінарного файлу. 

Залежність від мережевих цілей `After=network.target` забезпечує готовність підсистеми міжпроцесної взаємодії до моменту підняття прикладного процесу.

Нижче наведено повний текст конфігурації сервісу:

```ini
[Unit]
Description=Application Service with Volatile Runtime Directory
Wants=systemd-tmpfiles-setup.service
After=systemd-tmpfiles-setup.service network.target

[Service]
Type=simple
User=appuser
Group=appuser
ExecStart=/usr/bin/appdaemon
Restart=on-failure
ProtectSystem=full
ProtectHome=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

У цій конфігурації директива `After=systemd-tmpfiles-setup.service` гарантує, що `systemd` зачекає завершення роботи парсера `tmpfiles.d`. Параметри пісочниці `ProtectSystem=full` та `PrivateTmp=true` додатково ізолюють демон від модифікації системних каталогів `/usr` та `/etc`, причому демон може вільно працювати зі своїм виділеним каталогом у `/run/appdaemon`.

Параметр `PrivateTmp=true` монтує приватні ізольовані каталоги `/tmp` та `/var/tmp` для даного сервісу через простори імен файлової системи (mount namespaces). Однак це не впливає на глобальний рантайм-каталог `/run/appdaemon`, оскільки `/run` є спільним для всіх процесів системи і служить саме для міжпроцесної взаємодії IPC (англ. *Inter-Process Communication*).

---

### 3. Програмна реалізація демона (C та C++)

Програми системного рівня на мовах C та C++ підключаються до підготовленого волотильного каталогу `/run/appdaemon`, створюють сокет міжпроцесної взаємодії (UNIX domain socket) за шляхом `/run/appdaemon/service.sock` та встановлюють суворі права доступу для запобігання несанкціонованому підключенню інших процесів.

При створенні сокета Unix у волотильному каталозі необхідно враховувати особливості файлової системи `tmpfs`:
1. Усі об'єкти типу сокет створюються системним викликом `bind()`. Файл сокета при цьому з'являється у файловій системі як спеціальний запис.
2. Якщо файл сокета вже існує у каталозі (наприклад, після падіння попереднього екземпляра демона), виклик `bind()` зупиняється з помилкою `EADDRINUSE`. Тому програма повинна явним чином перевірити і вилучити застарілий сокет через `unlink()` до моменту прив'язки.
3. Права доступу на сокет встановлюються викликом `chmod()`. Права `0660` гарантують, що читати та писати у сокет зможе лише власник `appuser` та члени групи `appuser`.

Вкладка для C використовує класичний POSIX API з системними викликами `socket()`, `bind()` та `chmod()`, вимагаючи явного очищення ресурсів. Вкладка для C++20 застосовує концепцію RAII (англ. *Resource Acquisition Is Initialization*), огортаючи сокет у клас `ScopedUnixSocket`, який автоматично закриває дескриптор та видаляє файл сокета з рантайм-каталогу при виході з області видимості.

:::tabs
```c
/* C (POSIX API) — Серверний сокет у волотильному каталозі */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/stat.h>
#include <errno.h>

#define SOCKET_PATH "/run/appdaemon/service.sock"

int create_secure_socket(const char *path) {
    int server_fd = -1;
    struct sockaddr_un addr;

    /* Видаляємо застарілий сокет, якщо він лишився після аварійного завершення */
    unlink(path);

    server_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket failed");
        return -1;
    }

    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, path, sizeof(addr.sun_path) - 1);

    /* Прив'язуємо сокет до шляху у волотильному каталозі */
    if (bind(server_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind failed");
        close(server_fd);
        return -1;
    }

    /* Обмежуємо права доступу до сокета лише для власника та групи */
    if (chmod(path, 0660) < 0) {
        perror("chmod failed");
        close(server_fd);
        unlink(path);
        return -1;
    }

    if (listen(server_fd, 5) < 0) {
        perror("listen failed");
        close(server_fd);
        unlink(path);
        return -1;
    }

    return server_fd;
}

int main(void) {
    printf("Starting appdaemon inside /run/appdaemon...\n");
    int listen_fd = create_secure_socket(SOCKET_PATH);
    if (listen_fd < 0) {
        fprintf(stderr, "Failed to initialize server socket\n");
        return EXIT_FAILURE;
    }

    printf("Daemon is listening on %s\n", SOCKET_PATH);

    /* Основний цикл обробки мережевих подій та запитів клієнтів */
    /* ... */

    close(listen_fd);
    unlink(SOCKET_PATH);
    return EXIT_SUCCESS;
}
```
```cpp
// C++20 — Ідіоматична реалізація з RAII та обробкою помилок
#include <iostream>
#include <string_view>
#include <filesystem>
#include <system_error>
#include <expected>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>

namespace fs = std::filesystem;

class ScopedUnixSocket {
public:
    explicit ScopedUnixSocket(int fd, fs::path socket_path)
        : fd_(fd), path_(std::move(socket_path)) {}

    ~ScopedUnixSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        std::error_code ec;
        fs::remove(path_, ec);
    }

    ScopedUnixSocket(const ScopedUnixSocket&) = delete;
    ScopedUnixSocket& operator=(const ScopedUnixSocket&) = delete;

    ScopedUnixSocket(ScopedUnixSocket&& other) noexcept
        : fd_(other.fd_), path_(std::move(other.path_)) {
        other.fd_ = -1;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }
    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    int fd_{-1};
    fs::path path_;
};

std::expected<ScopedUnixSocket, std::string> create_server_socket(const fs::path& socket_path) {
    std::error_code ec;
    fs::remove(socket_path, ec);

    int fd = ::socket(AF_UNIX, SOCK_STREAM, 0);
    if (fd < 0) {
        return std::unexpected("Failed to create AF_UNIX socket");
    }

    sockaddr_un addr{};
    addr.sun_family = AF_UNIX;
    if (socket_path.string().length() >= sizeof(addr.sun_path)) {
        ::close(fd);
        return std::unexpected("Socket path is too long");
    }
    std::copy(socket_path.string().begin(), socket_path.string().end(), addr.sun_path);

    if (::bind(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
        ::close(fd);
        return std::unexpected("Failed to bind socket to path: " + socket_path.string());
    }

    fs::permissions(socket_path, 
                    fs::perms::owner_read | fs::perms::owner_write |
                    fs::perms::group_read | fs::perms::group_write,
                    fs::perm_options::replace, ec);
    if (ec) {
        ::close(fd);
        fs::remove(socket_path, ec);
        return std::unexpected("Failed to set socket permissions: " + ec.message());
    }

    if (::listen(fd, 5) < 0) {
        ::close(fd);
        fs::remove(socket_path, ec);
        return std::unexpected("Failed to listen on socket");
    }

    return ScopedUnixSocket(fd, socket_path);
}

int main() {
    const fs::path socket_path = "/run/appdaemon/service.sock";
    std::cout << "Starting appdaemon C++ engine...\n";

    auto server_socket = create_server_socket(socket_path);
    if (!server_socket) {
        std::cerr << "Initialization error: " << server_socket.error() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "Daemon is listening safely on " << server_socket->path() << '\n';

    // Автоматичне очищення сокета та файлового дескриптора при виході завдяки RAII
    return EXIT_SUCCESS;
}
```
:::

---

### 4. Інструкція з ручного тестування та налагодження

Для діагностики та ручного виклику правил `tmpfiles.d` використовується утиліта `systemd-tmpfiles`. Адміністратор системи має змогу виконувати тестування конфігурацій без перезавантаження операційної системи.

Нижче наведено послідовність команд для перевірки створюваної структури:

```bash
# 1. Перевірка синтаксису конфігурації у тестовому режимі без внесення змін (dry-run)
systemd-tmpfiles --create --dry-run /etc/tmpfiles.d/appdaemon.conf

# 2. Фактичне застосування конфігураційних правил до файлової системи
systemd-tmpfiles --create /etc/tmpfiles.d/appdaemon.conf

# 3. Перевірка атрибутів створеного каталогу та файлу стану
ls -ld /run/appdaemon
ls -l /run/appdaemon/status

# 4. Моделювання виконання процедури очищення тимчасових файлів
systemd-tmpfiles --clean /etc/tmpfiles.d/appdaemon.conf
```

Використання прапорця `--dry-run` виводить у консоль усі системні виклики (`mkdir`, `chmod`, `chown`), які планує виконати `systemd-tmpfiles`, дозволяючи виявити синтаксичні помилки або конфлікти прав доступу до їх фактичного застосування в операційній системі. Робота у даному тестовому режимі є стандартним інструментом верифікації для пакетних розробників дистрибутивів Linux.

Розбір консольного виводу при успішному виконанні команди `--create` дозволяє переконатися у відсутності попереджень про відсутність системних користувачів чи конфлікти масок доступу. Якщо у конфігураційному файлі вказано користувача, якого ще не створено у системі (наприклад, через відсутність юніта `systemd-sysusers`), утиліта повертає застереження у лог і створює каталог із власником `root:root` як захисний запобіжник.
