# 📋 Довідник системних інтерфейсів та чеклист готовності програми до продакшену в Linux

Цей довідник містить вичерпний опис системних інтерфейсів, структур ядра, мережевих протоколів, конфігураційних контрактів та змінних середовища, необхідних для інтеграції програмного забезпечення з підсистемами Linux: менеджером служб `systemd`, сокетом структурованого журналу `journald`, специфікацією розташування файлів XDG Base Directory та моделлю обробки сигналів ядра POSIX.

---

### 1. Протокол сповіщень `sd_notify` та життєвий цикл процесу

Протокол сповіщень `sd_notify` забезпечує прямий канал зв'язку між процесом служби та підсистемою ініціалізації `systemd`. На відміну від застарілих методів виявлення готовності (таких як подвійне форкання процесу з записом PID-файлу або очікування відкриття мережевого порту через опитування), `sd_notify` є детермінованим протоколом передачі повідомлень через датаграмний сокет домену Unix (`AF_UNIX`, `SOCK_DGRAM`).

#### 1.1. Механізм передачі повідомлень через `NOTIFY_SOCKET`

Під час запуску служби з директивою `Type=notify` менеджер `systemd` створює приватний датаграмний сокет і передає шлях до нього у змінній середовища `NOTIFY_SOCKET`.

Шлях до сокета може бути двох типів:
1. **Звичайний шлях у файловій системі:** наприклад, `/run/systemd/notify/control-12345`. Служба відкриває цей файл як стандартний Unix-сокет.
2. **Абстрактний сокет Linux:** шлях починається із символу `@` (наприклад, `@/org/freedesktop/systemd1/notify/12345`). В адресному просторі сокетів Linux перший байт структури `sockaddr_un.sun_path` встановлюється в нульовий символ `\0`, що дозволяє відкривати сокет без прив'язки до файлової системи та уникати колізій прав доступу в ізольованих просторах імен `mount`.

Повідомлення формується у вигляді звичайного текстового буфера, що містить пари `КЛЮЧ=значення`, розділені символом переводу рядка `\n`. Максимальний рекомендований розмір одного датаграма становить 4096 байтів.

#### 1.2. Повний реєстр параметрів стану протоколу `sd_notify`

| Змінна стану | Тип значення | Опис семантики та реакція менеджера служб |
| :--- | :--- | :--- |
| `READY=1` | Прапорець | Служба повністю завершила початкову ініціалізацію: прочитала файли конфігурації, відкрила слухаючі сокети, підключилася до баз даних і готова обробляти клієнтські запити. Менеджер `systemd` переводить стан unit із `activating` у `active (running)` і розблоковує запуск залежних служб. |
| `RELOADING=1` | Прапорець | Служба почала процедуру гарячого перечитування конфігурації (наприклад, після сигналу `SIGHUP`). Менеджер переводить стан у `reloading`. Після завершення оновлення служба зобов'язана надіслати `READY=1`. |
| `STOPPING=1` | Прапорець | Процес перейшов до фази штатного завершення (graceful shutdown): припинив прийом нових запитів та дообробляє чергу задач. `systemd` очікує завершення процесу протягом інтервалу `TimeoutStopSec`. |
| `WATCHDOG=1` | Прапорець | Сигнал працездатності (keep-alive heartbeat). Служба зобов'язана регулярно відправляти цей прапорець, підтверджуючи, що головний цикл подій не заблокований. |
| `WATCHDOG_USEC=N` | Ціле число (мкс) | Запит на динамічну зміну періоду сторожового таймера. Використовується, коли службі тимчасово потрібен довший інтервал на виконання важкої блокуючої операції. |
| `STATUS=текст` | Текстовий рядок | Довільний однорядковий опис поточного стану (наприклад, `STATUS=Оброблено 15420 запитів, 12 активних сесій`). Рядок відображається в утиліті `systemctl status <unit>`. |
| `ERRNO=N` | Число (errno) | Числовий код помилки C-бібліотеки (`errno`), якщо процес ініціалізації зазнав невдачі і служба виходить з аварійним станом. |
| `MAINPID=PID` | Число (PID) | Сповіщення про зміну головного ідентифікатора процесу. Необхідно для служб-супервізорів, які створюють окремі робочі процеси для обробки трафіку. |
| `FDSTORE=1` | Прапорець + дескриптор | Запит на збереження файлового дескриптора у системному сховищі `systemd` через допоміжні керуючі дані `SCM_RIGHTS`. Дозволяє реалізувати безшовний перезапуск процесу (*zero-downtime reload*) без розриву активних клієнтських TCP-з'єднань. |
| `FDSTOREREMOVE=1` | Прапорець | Запит на вилучення та закриття раніше збереженого дескриптора зі сховища `systemd`. |
| `FDNAME=назва` | Рядок | Текстова мітка для збереженого дескриптора (наприклад, `FDNAME=http-listener`). |
| `BARRIER=1` | Прапорець | Запит синхронізації повідомлень. Дозволяє переконатися, що всі попередні сповіщення були повністю оброблені менеджером `systemd`. |

#### 1.3. Реалізація клієнта `sd_notify` без зовнішньої бібліотеки `libsystemd`

Використання офіційної бібліотеки `libsystemd` вимагає динамічного лінкування з `libsystemd.so` або підтягування важких залежностей. Нижче наведено повністю автономну, безпечну реалізацію протоколу, яка працює на будь-якому ядрі Linux із бібліотеками glibc або musl:

:::tabs
```c
#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <stddef.h>

/* Автономна відправка рядка стану в systemd через Unix-сокет */
int standalone_sd_notify(const char *state) {
    if (!state || !*state) {
        return 0;
    }

    const char *socket_path = getenv("NOTIFY_SOCKET");
    if (!socket_path) {
        return 0; /* Процес запущено не під керуванням systemd */
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;

    size_t path_len = strlen(socket_path);
    if (path_len >= sizeof(addr.sun_path)) {
        errno = ENAMETOOLONG;
        return -1;
    }

    /* Підтримка абстрактних сокетів Linux (починаються з символу @) */
    if (socket_path[0] == '@') {
        addr.sun_path[0] = '\0';
        memcpy(&addr.sun_path[1], &socket_path[1], path_len - 1);
    } else {
        memcpy(addr.sun_path, socket_path, path_len);
    }

    int fd = socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0) {
        return -1;
    }

    socklen_t addr_len = offsetof(struct sockaddr_un, sun_path) + path_len;
    ssize_t written = sendto(fd, state, strlen(state), MSG_NOSIGNAL,
                             (struct sockaddr *)&addr, addr_len);

    int saved_errno = errno;
    close(fd);

    if (written < 0) {
        errno = saved_errno;
        return -1;
    }

    return 1;
}
```
```cpp
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <cstdlib>
#include <cstring>
#include <cstddef>
#include <string_view>
#include <expected>
#include <system_error>

// Автономна відправка сповіщення в systemd засобами стандарту C++23
[[nodiscard]] std::expected<bool, std::error_code> standalone_sd_notify(std::string_view state) noexcept {
    if (state.empty()) {
        return false;
    }

    const char* socket_path = std::getenv("NOTIFY_SOCKET");
    if (!socket_path) {
        return false; // Службу запущено поза менеджером systemd
    }

    struct sockaddr_un addr{};
    addr.sun_family = AF_UNIX;

    const size_t path_len = std::strlen(socket_path);
    if (path_len >= sizeof(addr.sun_path)) {
        return std::unexpected(std::make_error_code(std::errc::filename_too_long));
    }

    // Обробка абстрактних сокетів Linux
    if (socket_path[0] == '@') {
        addr.sun_path[0] = '\0';
        std::memcpy(&addr.sun_path[1], &socket_path[1], path_len - 1);
    } else {
        std::memcpy(addr.sun_path, socket_path, path_len);
    }

    const int fd = ::socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    const auto addr_len = static_cast<socklen_t>(offsetof(struct sockaddr_un, sun_path) + path_len);
    const ssize_t written = ::sendto(fd, state.data(), state.size(), MSG_NOSIGNAL,
                                     reinterpret_cast<struct sockaddr*>(&addr), addr_len);

    const int saved_errno = errno;
    ::close(fd);

    if (written < 0) {
        return std::unexpected(std::error_code(saved_errno, std::generic_category()));
    }

    return true;
}
```
:::

---

### 2. Довідник директив безпеки та ізоляції `systemd.service`

Конфігураційний файл юніта `systemd` визначає параметри виконання, обмеження ресурсів через підсистему контрольних груп cgroups v2, фільтрацію системних викликів та конфігурацію просторів імен (Namespaces).

#### 2.1. Еталонний конфігураційний файл продакшен-служби

Нижче наведено еталонний файл служби `/usr/lib/systemd/system/production-daemon.service`, що реалізує принцип ешелонованої оборони (*defense in depth*):

```ini
[Unit]
Description=High-Performance Production Network Service
After=network-online.target time-sync.target
Wants=network-online.target
Documentation=man:production-daemon(8) https://example.com/docs

[Service]
Type=notify
ExecStart=/usr/bin/production-daemon --config=/etc/production-daemon/config.toml
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5s
TimeoutStopSec=30s
WatchdogSec=15s

# ── Ідентичність та права процесу ─────────────────────────────────────
DynamicUser=yes
User=production-daemon
Group=production-daemon
UMask=0027

# ── Ізоляція файлової системи ────────────────────────────────────────
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes
ProtectClock=yes
ProtectProc=invisible
ProcSubset=pid

# Декларація каталогів із збереженням прав доступу
RuntimeDirectory=production-daemon
StateDirectory=production-daemon
ConfigurationDirectory=production-daemon
LogsDirectory=production-daemon

# ── Мережа та обмеження викликів ядра ────────────────────────────────
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
RestrictNamespaces=yes
RestrictRealtime=yes
RestrictSUIDSGID=yes
MemoryDenyWriteExecute=yes
LockPersonality=yes
NoNewPrivileges=yes

# ── Декомпозиція можливостей (Linux Capabilities) ────────────────────
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_BIND_SERVICE

# ── Seccomp BPF фільтрація системних викликів ────────────────────────
SystemCallFilter=@system-service @network-io
SystemCallFilter=~@privileged @resources @mount @debug @reboot @swap
SystemCallArchitectures=native
SystemCallErrorNumber=EPERM

# ── Ліміти ресурсів cgroups v2 ────────────────────────────────────────
LimitNOFILE=65536
TasksMax=512
MemoryMax=1G
MemoryHigh=800M
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

#### 2.2. Детальний аналіз директив пісочниці та рівнів захисту

* **`DynamicUser=yes`**: підсистема `systemd` динамічно виділяє вільний числовий UID та GID із пулу користувацьких ідентифікаторів `61184..65519`. Процес не має запису в системних базах `/etc/passwd` або `/etc/shadow`. Після зупинки служби всі тимчасові файли, IPC-семафори та черги повідомлень автоматично видаляються ядром.
* **`ProtectSystem=strict`**: ядро створює новий простір імен монтувань (`CLONE_NEWNS`) для процесу, в якому вся ієрархія файлової системи (включаючи `/usr`, `/boot`, `/etc` та системні бібліотеки) монтується з прапорцем `MS_RDONLY`. Будь-яка спроба створення чи модифікації файлу призводить до системної помилки `EROFS` (Read-only file system).
* **`ProtectHome=yes`**: приховує каталоги користувачів `/home`, `/root` та `/run/user`, роблячи їх недоступними або порожніми для процесу служби.
* **`PrivateTmp=yes`**: виділяє для процесу повністю ізольовану файлову систему `/tmp` та `/var/tmp`, ізолюючи тимчасові файли від інших користувачів та процесів системи.
* **`PrivateDevices=yes`**: створює для процесу приватний простір імен пристроїв `/dev`, приховуючи фізичні блокові пристрої дисків (`/dev/sda`, `/dev/nvme0n1`), системну пам'ять (`/dev/mem`, `/dev/kmem`) та залишаючи доступними лише віртуальні псевдопристрої `/dev/null`, `/dev/zero`, `/dev/urandom`.
* **`ProtectKernelTunables=yes`**: монтує підсистеми `/proc/sys`, `/sys`, `/proc/sysrq-trigger`, `/proc/latency_stats` у режимі лише для читання, унеможливлюючи зміну глобальних параметрів ядра sysctl.
* **`ProtectKernelModules=yes`**: блокує системні виклики завантаження та вивантаження модулів ядра `init_module()`, `finit_module()`, `delete_module()`.
* **`ProtectControlGroups=yes`**: монтує файлову систему `/sys/fs/cgroup` у режимі `read-only`, забороняючи процесу модифікувати власні або чужі ліміти ресурсів.
* **`StateDirectory=production-daemon`**: створює персистентний каталог `/var/lib/production-daemon` і призначає його власником динамічного користувача служби. Тільки цей каталог доступний на читання та запис для збереження баз даних або стану між перезапусками.
* **`RuntimeDirectory=production-daemon`**: монтує тимчасовий каталог `/run/production-daemon` у віртуальній пам'яті `tmpfs`, куди служба може записувати свої Unix-сокети та пайпи. Каталог гарантовано знищується під час зупинки процесу.
* **`MemoryDenyWriteExecute=yes`**: реалізує апаратний інваріант безпеки `W^X` (Write XOR Execute). Блокує системні виклики `mmap()` та `mprotect()`, що намагаються встановити для однієї ділянки пам'яті одночасно прапорці запису та виконання (`PROT_WRITE | PROT_EXEC`). Повністю унеможливлює виконання шеллкоду на купі або в буферах процесу.
* **`NoNewPrivileges=yes`**: активує механізм ядра `PR_SET_NO_NEW_PRIVS`. Процес та всі його нащадки втрачають здатність підвищувати свої права через запуск виконуваних файлів із бітами `setuid`/`setgid` або файловими можливостями (*file capabilities*).
* **`RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6`**: забороняє створення сокетів небезпечних або застарілих протоколів (наприклад, `AF_NETLINK`, `AF_PACKET`, `AF_BLUETOOTH`, `AF_IPX`), захищаючи ядро від експлуатації вразливостей мережевих драйверів.
* **`SystemCallFilter=@system-service`**: генерує та завантажує в ядро фільтр Seccomp-BPF. Будь-яка спроба виконання заборонених викликів (наприклад, `ptrace`, `kexec_load`, `mount`, `reboot`, `swapoff`) негайно блокується поверненням помилки `EPERM` без краху всієї системи.

---

### 3. Специфікація каталогів XDG Base Directory

Для десктопних програм, CLI-утиліт та користувацьких служб шляхи до файлів конфігурації, кешу, стану та збережених даних повинні визначатися згідно зі специфікацією XDG Base Directory Specification.

#### 3.1. Змінні середовища та резервні значення

| Змінна середовища | Значення за замовчуванням | Характер даних та правила використання |
| :--- | :--- | :--- |
| `XDG_CONFIG_HOME` | `$HOME/.config` | Файли конфігурації та налаштування користувача. Мають зберігатися у текстових форматах (TOML, YAML, JSON) і бути придатними для копіювання між різними робочими станціями. |
| `XDG_DATA_HOME` | `$HOME/.local/share` | Довготривалі дані застосунку: бази даних SQLite, поштові скриньки, збережені файли проектів. Ці дані не повинні втрачатися під час очищення системи. |
| `XDG_STATE_HOME` | `$HOME/.local/state` | Стан сеансу: історія введених команд, позиції курсорів у редакторі, геометрія вікон. Втрата даних не ламає програму, але створює незручності для користувача. |
| `XDG_CACHE_HOME` | `$HOME/.cache` | Непостійні тимчасові дані: кеш веб-сторінок, скомпільовані шейдери, мініатюри зображень. Можуть бути видалені користувачем або скриптами очищення диску в будь-який момент. |
| `XDG_RUNTIME_DIR` | `/run/user/<UID>` | Тимчасові файли та сокети поточного сеансу користувача (файлова система `tmpfs` в оперативній пам'яті). Має права доступу `0700` і знищується при виході користувача з системи. |
| `XDG_CONFIG_DIRS` | `/etc/xdg` | Розділений двокрапками список системних каталогів для пошуку базових файлів конфігурації, якщо користувацькі налаштування відсутні. |
| `XDG_DATA_DIRS` | `/usr/local/share:/usr/share` | Розділений двокрапками перелік системних каталогів для пошуку ресурсів програми (`.desktop` ярлики, іконки, схеми MIME). |

#### 3.2. Алгоритм безпечного розв'язання шляхів конфігурації

Коректна реалізація пошуку файлів повинна враховувати як системний режим (FHS), так і користувацький (XDG).

Нижче наведено алгоритм визначення шляху до файлу конфігурації:

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <limits.h>

/* Отримання абсолютного шляху до файлу конфігурації програми */
int get_app_config_path(const char *app_name, char *out_path, size_t out_size) {
    if (!app_name || !out_path || out_size == 0) {
        return -1;
    }

    /* Якщо процес запущено від root або як системну службу — дивимось у /etc */
    if (geteuid() == 0) {
        int written = snprintf(out_path, out_size, "/etc/%s/config.toml", app_name);
        return (written > 0 && (size_t)written < out_size) ? 0 : -1;
    }

    /* Для звичайного користувача перевіряємо XDG_CONFIG_HOME */
    const char *xdg_config = getenv("XDG_CONFIG_HOME");
    if (xdg_config && *xdg_config) {
        int written = snprintf(out_path, out_size, "%s/%s/config.toml", xdg_config, app_name);
        return (written > 0 && (size_t)written < out_size) ? 0 : -1;
    }

    /* Резервний варіант: $HOME/.config */
    const char *home = getenv("HOME");
    if (!home || !*home) {
        return -1;
    }

    int written = snprintf(out_path, out_size, "%s/.config/%s/config.toml", home, app_name);
    return (written > 0 && (size_t)written < out_size) ? 0 : -1;
}
```
```cpp
#include <string>
#include <string_view>
#include <filesystem>
#include <cstdlib>
#include <unistd.h>
#include <expected>
#include <system_error>

namespace fs = std::filesystem;

// Отримання шляху до конфігурації засобами std::filesystem (C++23)
[[nodiscard]] std::expected<fs::path, std::error_code> get_app_config_path(std::string_view app_name) noexcept {
    if (app_name.empty()) {
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));
    }

    // Системні служби або root використовують ієрархію /etc
    if (::geteuid() == 0) {
        return fs::path("/etc") / app_name / "config.toml";
    }

    // Перевірка наявності змінної XDG_CONFIG_HOME
    const char* xdg_config = std::getenv("XDG_CONFIG_HOME");
    if (xdg_config && *xdg_config != '\0') {
        return fs::path(xdg_config) / app_name / "config.toml";
    }

    // Резервне значення $HOME/.config
    const char* home = std::getenv("HOME");
    if (!home || *home == '\0') {
        return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
    }

    return fs::path(home) / ".config" / app_name / "config.toml";
}
```
:::

---

### 4. Контракт обробки системних сигналів POSIX

Продакшен-програма зобов'язана реалізовувати детерміновану реакцію на сигнали операційної системи.

#### 4.1. Таблиця обробки сигналів

| Сигнал ядра | Джерело сигналу | Обов'язкова дія процесу |
| :--- | :--- | :--- |
| `SIGTERM` (`15`) | `systemctl stop`, Kubernetes, `kill` | **Graceful Shutdown**: припинити виклик `accept()`, завершити обробку поточних транзакцій, скинути дискові буфери та викликати `exit(0)`. |
| `SIGINT` (`2`) | Натискання `Ctrl+C` у терміналі | Аналогічно до `SIGTERM` для інтерактивних утиліт. |
| `SIGQUIT` (`3`) | `Ctrl+\` у терміналі | Аварійне завершення зі створенням дампу пам'яті (*core dump*) для діагностики. |
| `SIGHUP` (`1`) | Закриття керуючого TTY або `systemctl reload` | **Hot Reload**: перечитати конфігураційні файли з диска, перевідкрити логи, оновити сертифікати TLS без розриву активних з'єднань. |
| `SIGPIPE` (`13`) | Запис у сокет або пайп, закритий іншою стороною | **Ігнорувати (`SIG_IGN`)**: у протилежному випадку процес раптово завершиться під час запису в розірване TCP-з'єднання. Помилка обробляється через `errno == EPIPE`. |
| `SIGUSR1` (`10`) | Скрипти обслуговування (наприклад, `logrotate`) | Повторне відкриття файлових дескрипторів журналів після їхньої ротації на диску. |
| `SIGUSR2` (`12`) | Адміністратор або CI/CD | Запуск діагностичного профілювання або скидання внутрішніх метрик продуктивності. |
| `SIGCHLD` (`17`) | Завершення дочірнього процесу | Виклик `waitpid(-1, &status, WNOHANG)` у циклі для запобігання утворенню процесів-зомбі. |
| `SIGWINCH` (`28`)| Зміна розміру вікна емулятора термінала | Оновлення розмірів віртуального екрана (використовується в консольних TUI-інтерфейсах). |

#### 4.2. Безпечна робота з мережевими сокетами без падінь від `SIGPIPE`

При роботі з мережевими сокетами запис у дескриптор, який уже був закритий віддаленим клієнтом, призводить до надсилання ядром сигналу `SIGPIPE`. За замовчуванням дія цього сигналу — негайне аварійне завершення процесу без виклику деструкторів та функцій очищення.

Для запобігання падінню необхідно застосовувати комплексну стратегію захисту:

:::tabs
```c
#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/socket.h>
#include <signal.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>

/* Безпечна відправка даних у мережевий сокет */
ssize_t safe_socket_send(int fd, const void *buf, size_t len) {
    /* Передаємо прапорець MSG_NOSIGNAL, який забороняє генерацію SIGPIPE */
    ssize_t res = send(fd, buf, len, MSG_NOSIGNAL);
    if (res < 0) {
        if (errno == EPIPE || errno == ECONNRESET) {
            /* Клієнт розірвав з'єднання — фіксуємо подію та закриваємо сокет */
            fprintf(stderr, "<4>Клієнт достроково розірвав TCP-з'єднання\n");
        }
    }
    return res;
}

/* Ініціалізація глобального ігнорування SIGPIPE */
void init_signal_protection(void) {
    struct sigaction sa;
    sa.sa_handler = SIG_IGN;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGPIPE, &sa, NULL);
}
```
```cpp
#include <sys/types.h>
#include <sys/socket.h>
#include <csignal>
#include <unistd.h>
#include <cstddef>
#include <expected>
#include <system_error>
#include <iostream>
#include <span>

// Безпечна передача даних через сокет засобами C++23
[[nodiscard]] std::expected<size_t, std::error_code> safe_socket_send(int fd, std::span<const char> data) noexcept {
    const ssize_t res = ::send(fd, data.data(), data.size(), MSG_NOSIGNAL);
    if (res < 0) {
        const int err = errno;
        if (err == EPIPE || err == ECONNRESET) {
            std::cerr << "<4>Клієнт достроково закрив TCP-з'єднання\n";
        }
        return std::unexpected(std::error_code(err, std::generic_category()));
    }
    return static_cast<size_t>(res);
}

// Встановлення ігнорування SIGPIPE на рівні процесу
void init_signal_protection() noexcept {
    struct sigaction sa{};
    sa.sa_handler = SIG_IGN;
    ::sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    ::sigaction(SIGPIPE, &sa, nullptr);
}
```
:::

---

### 5. Структуроване журналювання через `journald`

`systemd-journald` надає можливість реєстрації подій із точною категоризацією за рівнями пріоритетів та прив'язкою до двійкових метаданих ядра.

#### 5.1. Префікси рівнів логування у стандартний потік виводу

Якщо служба пише повідомлення у потік `stdout`, рівень важливості вказується префіксом формату `<N>` на початку кожного рядка:

| Префікс | Рівень важливості | Семантика події |
| :--- | :--- | :--- |
| `<0>` | `emerg` (LOG_EMERG) | Система непридатна до використання (повний крах ядра чи сервісу). |
| `<1>` | `alert` (LOG_ALERT) | Потрібне негайне втручання чергового інженера (пошкодження бази). |
| `<2>` | `crit` (LOG_CRIT) | Критичний стан (відмова дискової підсистеми або вичерпання дескрипторів). |
| `<3>` | `err` (LOG_ERR) | Помилка обробки (збій клієнтського запиту, помилка валідації). |
| `<4>` | `warning` (LOG_WARNING) | Попередження (високе навантаження, затримка відповіді). |
| `<5>` | `notice` (LOG_NOTICE) | Нормальна, але суттєва подія (запуск/зупинка службового циклу). |
| `<6>` | `info` (LOG_INFO) | Звичайна робоча інформація (клієнт авторизувався, транзакцію записано). |
| `<7>` | `debug` (LOG_DEBUG) | Налагоджувальні діагностичні дані розробника. |

Приклад запису повідомлень у стандартні потоки виводу:

:::tabs
```c
#include <stdio.h>
#include <string.h>
#include <errno.h>

/* Друк структурованих повідомлень у stdout з префіксами для journald */
void log_service_events(const char *db_name, int port) {
    fprintf(stdout, "<6>Ініціалізація мережевого сервера на порту %d успішна\n", port);
    fprintf(stderr, "<3>Помилка відкриття файлу бази даних '%s': %s\n", 
            db_name, strerror(ENOENT));
    fflush(stdout);
    fflush(stderr);
}
```
```cpp
#include <iostream>
#include <string_view>
#include <format>

// Друк логів для journald мовою C++23
void log_service_events(std::string_view db_name, int port) {
    std::cout << std::format("<6>Ініціалізація мережевого сервера на порту {} успішна\n", port);
    std::cerr << std::format("<3>Помилка відкриття файлу бази даних '{}': файл не знайдено\n", db_name);
    std::cout.flush();
    std::cerr.flush();
}
```
:::

#### 5.2. Структурований формат Native Journald API

Пряме надсилання подій через сокет `/run/systemd/journal/socket` дозволяє передавати структуровані пари ключ-значення, за якими згодом можна виконувати точну фільтрацію без регулярних виразів:

```
MESSAGE=Клієнт успішно провів фінансову транзакцію
PRIORITY=6
TRANSACTION_ID=982341
USER_ID=4512
AMOUNT_UAH=1500.00
CODE_FILE=src/billing.c
CODE_LINE=142
CODE_FUNC=process_payment
```

Адміністратор фільтрує такі події в журналі за лічені мілісекунди:
```bash
journalctl _SYSTEMD_UNIT=production-daemon.service TRANSACTION_ID=982341 -o verbose
```
