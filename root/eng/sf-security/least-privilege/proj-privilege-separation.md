# ⚙️ Архітектура розділення привілеїв: безпечний сокетний демон

Ця вставка містить робочий інженерний приклад побудови мережевого сервісу з архітектурним розділенням привілеїв (Privilege Separation Pattern), де парсинг недовірених даних виноситься в ізольований дочірній процес із нульовими привілеями, а робота з файловою системою та автентифікацією контролюється батьківським монітором через захищений канал IPC.

## Постановка інженерної задачі

Традиційний монолітний демон стартує з правами користувача `root` (щоб відкрити привілейований TCP-порт або прочитати конфіденційний файл ключів) і продовжує обробляти вхідні клієнтські мережеві запити в тому самому привілейованому адресному просторі. Будь-яка помилка обробки пам'яті в парсері мережевих пакетів (переповнення буфера, використання пам'яті після звільнення, помилка форматування рядка) надає зловмиснику повний контроль над усією операційною системою.

Мета проєкту — розділити демон на два незалежні процеси з різними рівнями довіри:
1. **Привілейований монітор (Broker / Supervisor):** утримує дескриптор конфігурації та виконує критичні системні операції. Монітор не контактує безпосередньо з мережевим потоком байтів.
2. **Непривілейований воркер (Sandboxed Worker):** отримує сирий сокет клієнта, скидає всі права (перехід на UID `nobody`, очищення додаткових груп, блокування `PR_SET_NO_NEW_PRIVS`, нульові capabilities) та взаємодіє з монітором суворо через локальний канал IPC за фіксованим протоколом.

## Архітектурна схема взаємодії

```
+------------------------------------+          IPC (UNIX Domain Socket)          +------------------------------------+
|       Привілейований монітор       | <========================================> |      Непривілейований воркер       |
|            (UID 0 / root)          |                                            |          (UID 65534 / nobody)      |
|  - Відкриття файлів логів          |     Структуровані запити: AUTH, LOG        |  - Парсинг клієнтських байтів      |
|  - Перевірка автентичності (PAM)   |                                            |  - 0 capabilities, NO_NEW_PRIVS    |
+------------------------------------+                                            +------------------------------------+
```

Зв'язок між процесами організується через пару неіменованих сокетів `socketpair(AF_UNIX, SOCK_STREAM, 0)`. Цей канал створюється до моменту деескалації прав, завдяки чому обидві сторони мають двосторонній повнодуплексний зв'язок без необхідності відкривати додаткові файли чи порти у файловій системі.

## Передача файлових дескрипторів через `SCM_RIGHTS`

У повномасштабних серверах (наприклад, OpenSSH або високопродуктивних HTTP-серверах) привілейований батьківський процес виконує системний виклик `accept()` на привілейованому порті, а потім передає готовий клієнтський файловий дескриптор непривілейованому воркеру через керуюче повідомлення `sendmsg` із типом допоміжних даних `SCM_RIGHTS`.

Ядро операційної системи дублює запис у системній таблиці відкритих файлів і створює новий числовий дескриптор у таблиці цільового процесу-воркера. Після цього воркер може самостійно читати й записувати дані в клієнтське з'єднання, не маючи жодних прав на відкриття нових мережевих сокетів чи прослуховування портів.

Нижче наведено парні функції передачі та прийому файлового дескриптора через сокет домену Unix:

:::tabs
```c
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>

int send_fd(int socket_fd, int fd_to_send) {
    struct msghdr msg;
    memset(&msg, 0, sizeof(msg));

    char dummy = 'F';
    struct iovec iov;
    iov.iov_base = &dummy;
    iov.iov_len = sizeof(dummy);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    char cmsg_buf[CMSG_SPACE(sizeof(int))];
    memset(cmsg_buf, 0, sizeof(cmsg_buf));
    msg.msg_control = cmsg_buf;
    msg.msg_controllen = sizeof(cmsg_buf);

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));
    memcpy(CMSG_DATA(cmsg), &fd_to_send, sizeof(int));

    return (sendmsg(socket_fd, &msg, 0) >= 0) ? 0 : -1;
}

int recv_fd(int socket_fd) {
    struct msghdr msg;
    memset(&msg, 0, sizeof(msg));

    char dummy = 0;
    struct iovec iov;
    iov.iov_base = &dummy;
    iov.iov_len = sizeof(dummy);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    char cmsg_buf[CMSG_SPACE(sizeof(int))];
    memset(cmsg_buf, 0, sizeof(cmsg_buf));
    msg.msg_control = cmsg_buf;
    msg.msg_controllen = sizeof(cmsg_buf);

    if (recvmsg(socket_fd, &msg, 0) <= 0) {
        return -1;
    }

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    if (!cmsg || cmsg->cmsg_type != SCM_RIGHTS) {
        return -1;
    }

    int received_fd = -1;
    memcpy(&received_fd, CMSG_DATA(cmsg), sizeof(int));
    return received_fd;
}
```
```cpp
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <cstring>
#include <expected>
#include <system_error>

namespace security {

[[nodiscard]] auto send_file_descriptor(int socket_fd, int fd_to_send) noexcept 
    -> std::expected<void, std::error_code> 
{
    struct msghdr msg{};
    char dummy = 'F';
    struct iovec iov{ .iov_base = &dummy, .iov_len = sizeof(dummy) };
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    char cmsg_buf[CMSG_SPACE(sizeof(int))]{};
    msg.msg_control = cmsg_buf;
    msg.msg_controllen = sizeof(cmsg_buf);

    struct cmsghdr* cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));
    std::memcpy(CMSG_DATA(cmsg), &fd_to_send, sizeof(int));

    if (::sendmsg(socket_fd, &msg, 0) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

[[nodiscard]] auto receive_file_descriptor(int socket_fd) noexcept 
    -> std::expected<int, std::error_code> 
{
    struct msghdr msg{};
    char dummy = 0;
    struct iovec iov{ .iov_base = &dummy, .iov_len = sizeof(dummy) };
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    char cmsg_buf[CMSG_SPACE(sizeof(int))]{};
    msg.msg_control = cmsg_buf;
    msg.msg_controllen = sizeof(cmsg_buf);

    if (::recvmsg(socket_fd, &msg, 0) <= 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    struct cmsghdr* cmsg = CMSG_FIRSTHDR(&msg);
    if (!cmsg || cmsg->cmsg_type != SCM_RIGHTS) {
        return std::unexpected(std::make_error_code(std::errc::bad_message));
    }

    int received_fd = -1;
    std::memcpy(&received_fd, CMSG_DATA(cmsg), sizeof(int));
    return received_fd;
}

} // namespace security
```
:::

## Реалізація сокетного демона з деескалацією

Нижче наведено повну архітектуру монітора й воркера з передачею структурованих команд:

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/prctl.h>
#include <sys/wait.h>
#include <grp.h>

#define UNPRIV_UID 65534 /* nobody */
#define UNPRIV_GID 65534 /* nogroup */

enum IpcCommand {
    CMD_LOG_MESSAGE = 1,
    CMD_AUTH_CHECK  = 2,
    CMD_EXIT        = 3
};

struct IpcMessage {
    int command;
    int payload_len;
    char buffer[256];
};

/* Скидання прав процесу до абсолютного мінімуму */
static int drop_worker_privileges(void) {
    /* 1. Очищення списку додаткових груп */
    if (setgroups(0, NULL) == -1) {
        perror("setgroups");
        return -1;
    }

    /* 2. Скидання реального, ефективного та збереженого GID */
    if (setresgid(UNPRIV_GID, UNPRIV_GID, UNPRIV_GID) == -1) {
        perror("setresgid");
        return -1;
    }

    /* 3. Скидання реального, ефективного та збереженого UID */
    if (setresuid(UNPRIV_UID, UNPRIV_UID, UNPRIV_UID) == -1) {
        perror("setresuid");
        return -1;
    }

    /* 4. Заборона отримання будь-яких нових привілеїв у майбутньому */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
        perror("prctl(PR_SET_NO_NEW_PRIVS)");
        return -1;
    }

    return 0;
}

/* Логіка ізольованого воркера */
static void run_sandboxed_worker(int ipc_fd) {
    if (drop_worker_privileges() != 0) {
        fprintf(stderr, "Помилка деескалації прав воркера\n");
        close(ipc_fd);
        _exit(1);
    }

    /* Воркер парсить вхідні дані та формує IPC-запит до монітора */
    struct IpcMessage msg;
    memset(&msg, 0, sizeof(msg));
    msg.command = CMD_LOG_MESSAGE;
    
    const char *event_text = "З'єднання оброблено в ізольованому воркері";
    msg.payload_len = (int)strlen(event_text);
    strncpy(msg.buffer, event_text, sizeof(msg.buffer) - 1);

    if (write(ipc_fd, &msg, sizeof(msg)) != sizeof(msg)) {
        perror("worker write to ipc");
        close(ipc_fd);
        _exit(1);
    }

    close(ipc_fd);
    _exit(0);
}

/* Логіка привілейованого монітора */
static void run_privileged_monitor(int ipc_fd, pid_t worker_pid) {
    struct IpcMessage msg;
    ssize_t bytes_read = read(ipc_fd, &msg, sizeof(msg));

    if (bytes_read == sizeof(msg)) {
        if (msg.command == CMD_LOG_MESSAGE) {
            msg.buffer[sizeof(msg.buffer) - 1] = '\0';
            printf("[MONITOR LOG] Отримано подію від PID %d: %s\n",
                   worker_pid, msg.buffer);
        }
    } else {
        fprintf(stderr, "Помилка читання IPC повідомлення\n");
    }

    close(ipc_fd);

    int status = 0;
    waitpid(worker_pid, &status, 0);
}

int main(void) {
    int sv[2];
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, sv) == -1) {
        perror("socketpair");
        return 1;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        close(sv[0]);
        close(sv[1]);
        return 1;
    }

    if (pid == 0) {
        /* Дочірній процес: закриваємо кінцівку монітора */
        close(sv[0]);
        run_sandboxed_worker(sv[1]);
    } else {
        /* Батьківський процес: закриваємо кінцівку воркера */
        close(sv[1]);
        run_privileged_monitor(sv[0], pid);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <array>
#include <string_view>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/prctl.h>
#include <sys/wait.h>
#include <grp.h>

namespace security {

constexpr uid_t kUnprivilegedUid = 65534; // nobody
constexpr gid_t kUnprivilegedGid = 65534; // nogroup

enum class Command : int32_t {
    LogMessage = 1,
    AuthCheck  = 2,
    Exit       = 3
};

struct alignas(8) IpcPacket {
    Command command{Command::LogMessage};
    int32_t payload_len{0};
    std::array<char, 256> buffer{};
};

// RAII-обгортка для файлового дескриптора
class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_(-1) {}
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
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_;
};

// Безпечне скидання привілеїв процесу
[[nodiscard]] auto drop_privileges() noexcept -> std::expected<void, std::error_code> {
    if (::setgroups(0, nullptr) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    if (::setresgid(kUnprivilegedGid, kUnprivilegedGid, kUnprivilegedGid) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    if (::setresuid(kUnprivilegedUid, kUnprivilegedUid, kUnprivilegedUid) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

void run_sandboxed_worker(UniqueFd ipc_socket) {
    if (auto res = drop_privileges(); !res) {
        std::cerr << "Помилка деескалації воркера: " << res.error().message() << '\n';
        ::_exit(1);
    }

    IpcPacket packet{};
    packet.command = Command::LogMessage;
    
    constexpr std::string_view msg = "Подія оброблена в C++ RAII пісочниці";
    packet.payload_len = static_cast<int32_t>(msg.size());
    std::memcpy(packet.buffer.data(), msg.data(), msg.size());

    const auto written = ::write(ipc_socket.get(), &packet, sizeof(packet));
    if (written != sizeof(packet)) {
        ::_exit(1);
    }

    ::_exit(0);
}

void run_privileged_monitor(UniqueFd ipc_socket, pid_t worker_pid) {
    IpcPacket packet{};
    const auto read_bytes = ::read(ipc_socket.get(), &packet, sizeof(packet));

    if (read_bytes == sizeof(packet) && packet.command == Command::LogMessage) {
        std::string_view msg_view(packet.buffer.data(), 
                                  std::min<size_t>(packet.payload_len, packet.buffer.size() - 1));
        std::cout << "[MONITOR LOG] Подія від PID " << worker_pid << ": " << msg_view << '\n';
    }

    ipc_socket.reset();

    int status = 0;
    ::waitpid(worker_pid, &status, 0);
}

} // namespace security

int main() {
    std::array<int, 2> sv{-1, -1};
    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, sv.data()) == -1) {
        std::cerr << "socketpair failed: " << std::strerror(errno) << '\n';
        return 1;
    }

    security::UniqueFd monitor_fd(sv[0]);
    security::UniqueFd worker_fd(sv[1]);

    const pid_t pid = ::fork();
    if (pid < 0) {
        std::cerr << "fork failed: " << std::strerror(errno) << '\n';
        return 1;
    }

    if (pid == 0) {
        monitor_fd.reset();
        security::run_sandboxed_worker(std::move(worker_fd));
    } else {
        worker_fd.reset();
        security::run_privileged_monitor(std::move(monitor_fd), pid);
    }

    return 0;
}
```
:::

## Гарантії безпеки та підводні камені реалізації

Під час проєктування виробничих систем із розділенням привілеїв необхідно враховувати такі інженерні аспекти:

1. **Непривілейована поверхня атаки:** Якщо в коді `run_sandboxed_worker` виникне експлуатована вразливість, нападник опиняється в процесі з UID `65534`, без прав запису у файлову систему, без доступу до інших процесів та без можливості виконати `setuid`-бінарники через `PR_SET_NO_NEW_PRIVS`.
2. **Суворий парсинг IPC та захист від заплутаного заступника:** Монітор ніколи не виконує сирих системних команд або скриптів, отриманих від воркера. Кожне повідомлення має суворий бінарний формат фіксованого розміру з обов'язковою валідацією полів `command` та `payload_len`. Якщо скомпрометований воркер надсилає запит на читання файлу, монітор перевіряє права запитувача за власним внутрішнім білим списком дозволених шляхів, а не довіряє воркеру на слово ([Confused Deputy](root:sf-security/confused-deputy)).
3. **Закриття дескрипторів та витік ресурсів:** Батьківський процес зобов'язаний негайно закрити кінець сокета `sv[1]`, а дочірній — `sv[0]`. Залишений відкритим дескриптор заважає коректному виявленню завершення з'єднання (EOF) при падінні одного з процесів і може призвести до взаємного блокування (deadlock). Крім того, усі відкриті до виклику `fork` дескриптори конфіденційних файлів конфігурації повинні мати прапорець `O_CLOEXEC` або бути явно закриті у воркері перед початком обробки мережевих даних.
4. **Обробка сигналів `SIGPIPE` та `SIGCHLD`:** Завершення воркера через критичну помилку не повинно аварійно зупиняти монітор. Монітор обробляє сигнал `SIGCHLD` для перезапуску воркера та ігнорує `SIGPIPE` при спробі запису в закритий сокет IPC.
5. **Валідація меж буферів у протоколі обміну:** Усі рядкові поля, передані через спільний буфер повідомлень `IpcMessage`, обов'язково термінуються нульовим байтом безпосередньо на стороні монітора перед передачею в системні логи або функції виводу. Неприпустимо покладатися на те, що ізольований воркер надіслав коректно сформований C-рядок.

## Промислові патерни використання

Архітектура розділення привілеїв є стандартом де-факто для безпечних системних демонів та складного прикладного програмного забезпечення:
- **OpenSSH (PrivSep):** Процес `sshd` ділиться на привілейованого батька, який перевіряє ключі та керує сесіями через PAM, і недоваженого сина `sshd [net]`, який виконує криптографічний обмін Diffie-Hellman та обробку пакетів SSH. Злам мережевого парсера в OpenSSH не надає зловмиснику прав root.
- **vsftpd:** Один із перших FTP-демонів, побудований на моделі двох процесів: привілейований брокер відкриває порти даних (20/21) та створює сокети, а непривілейований процес обслуговує сесію в ізольованому `chroot`-каталозі.
- **Chromium / Сучасні браузери:** Багатопроцесна модель браузера (Browser Process vs Renderer Process). Вкладка, яка парсить складний HTML/JS/DOM, працює в пісочниці під строгим Seccomp-фільтром і надсилає запити до GPU та диска виключно через брокер за протоколом IPC Mojo. Навіть повне виконання довільного коду в рушії JavaScript (V8) не дає нападнику вийти за межі пісочниці без експлуатації другої вразливості в самому ядрі ОС чи брокері.
