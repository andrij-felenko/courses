# ⚙️ Проєкт захищеної пісочниці для парсингу з обмеженням системних викликів

Розбір ненадійних бінарних форматів даних (зображень, архівів, мультимедійних потоків чи мережевих пакетів) є найчастішим джерелом уразливостей пам'яті. Якщо парсер виконується у спільному адресному просторі головного застосунку, помилка виходу за межі масиву (Buffer Overflow) або використання пам'яті після звільнення (Use-After-Free) призводить до повної компрометації процесу.

У цьому проєкті ми будуємо повноцінну виробничу архітектуру розділення привілеїв: ненадійний парсер запускається в ізольованому дочірньому процесі, спілкується з майстер-процесом через пару UNIX-сокетів `socketpair(AF_UNIX, SOCK_SEQPACKET, 0)` та блокує всі небезпечні системні виклики за допомогою фільтра ядра **Seccomp-BPF** (Secure Computing Mode з інструкціями Berkeley Packet Filter). Будь-яка спроба зламаного парсера прочитати файл з диска, відкрити мережеве з'єднання або запустити інший процес (`execve`) призводить до негайного знищення воркера ядром ОС сигналом `SIGSYS`.

## Архітектурна схема пісочниці

Процес взаємодії між привілейованим майстром та безпривілейованим воркером побудований на п'яти чітких фазах:

```
[Головний процес (Master)]                             [Ізольований воркер (Parser)]
         │                                                            │
         ├── 1. socketpair(AF_UNIX, SOCK_SEQPACKET) ──────────────────┤
         ├── 2. fork() ───────────────────────────────────────────────┤
         │                                                            │ 3. prctl(PR_SET_NO_NEW_PRIVS)
         │                                                            │ 4. seccomp(SECCOMP_SET_MODE_FILTER)
         │                                                            │    (Дозволено лише read/write/exit)
         │                                                            │
         ├── 5. Передача сирого буфера через IPC-сокет ──────────────>│
         │                                                            │ 6. Парсинг ненадійних даних
         │<─ 7. Повернення структурованого результату (DTO) ──────────┤
```

### Модель загроз та інваріанти ізоляції

Під час проектування ми виходимо з найгіршого сценарію:
1. **Ненадійний вхідний потік:** Сирі байти надходять із відкритої мережі і можуть містити спеціально сформований експлойт для захоплення регістрів процесора та побудови ROP-ланцюжка (Return-Oriented Programming).
2. **Контур повної демаркації:** Дочірній процес позбавляється доступу до файлової системи, мережевих інтерфейсів, спільних сегментів пам'яті та системних журналів.
3. **Апаратне й ядерне обмеження:** Після активації BPF-фільтра ядро Linux перехоплює кожну спробу виконання інструкції `syscall`. Заборонено виклики `open`, `openat`, `creat`, `execve`, `fork`, `socket`, `connect`, `ptrace`, `kill`.
4. **Політика нульової толерантності:** Якщо у воркері виконується заборонений системний виклик, ядро негайно аварійно завершує процес дією `SECCOMP_RET_KILL_PROCESS`. Майстер-процес перехоплює сигнал `SIGSYS`, фіксує спробу атаки та продовжує штатну роботу.

## Механізм роботи віртуальної машини Seccomp-BPF

Фільтрація системних викликів у Linux спирається на класичну віртуальну машину BPF (cBPF). Віртуальна машина має два 32-бітні регістри: акумулятор `A` та індексний регістр `X`, а також невелику пам'ять із 16 комірок.

Коли процес здійснює системний виклик, ядро формує структуру `struct seccomp_data` у пам'яті ядра та передає її на вхід BPF-програмі:

```
struct seccomp_data {
    int nr;                    /* Номер системного виклику */
    __u32 arch;                /* Ідентифікатор архітектури CPU (AUDIT_ARCH_*) */
    __u64 instruction_pointer; /* Вказівник інструкції RIP/PC */
    __u64 args[6];             /* 6 аргументів системного виклику */
};
```

### Чому обов'язкова перевірка архітектури процесора (`arch`)

Найкритичніша помилка початківців при конструюванні BPF-фільтрів — відсутність перевірки поля `arch`. На 64-бітних процесорах x86-64 ядро підтримує зворотну сумісність із 32-бітними програмами x86 через інструкцію переривання `int 0x80` або режим сумісності. Номери системних викликів у 32-бітному та 64-бітному режимах не збігаються. Наприклад, системний виклик `exit_group` на x86-64 має номер 231, тоді як на x86 номер 231 відповідає виклику `sys_open`!

Якщо BPF-програма не перевірить, що поле `arch == AUDIT_ARCH_X86_64`, зловмисник зможе перемкнути сегмент коду в 32-бітний режим сумісності та викликати заборонений `open`, обійшовши фільтр. Тому перша інструкція нашого фільтра перевіряє архітектуру і миттєво вбиває процес при будь-якій невідповідності.

### Принцип дії `PR_SET_NO_NEW_PRIVS`

Перед завантаженням Seccomp-фільтра непривілейований процес зобов'язаний виконати системний виклик `prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)`.

Цей біт є монотонним прапорцем безпеки процесу. Щойно його встановлено, операційна система гарантує, що процес і жоден із його нащадків ніколи не зможуть отримати додаткові привілеї через запуск бінарних файлів із встановленими бітами `setuid` чи POSIX Capabilities (наприклад, через виклик `/usr/bin/sudo` чи `/usr/bin/ping`). Без встановлення `PR_SET_NO_NEW_PRIVS` ядро Linux дозволяє завантажувати BPF-фільтри лише процесам із повноваженням `CAP_SYS_ADMIN`, щоб запобігти маніпуляціям над системними утилітами.

## Вибір типу IPC-каналу: чому саме `SOCK_SEQPACKET`

Для обміну повідомленнями між майстром і пісочницею ми використовуємо пару локальних сокетів `socketpair(AF_UNIX, SOCK_SEQPACKET, 0)`. Розглянемо переваги цього вибору над іншими механізмами:

1. **`SOCK_STREAM` проти `SOCK_SEQPACKET`:** Потоковий сокет (`SOCK_STREAM`) склеює байти в єдиний потік без збереження меж повідомлень. Розробник змушений вручну реалізовувати протокол кадрування (довжина + тіло), що створює ризик помилок парсингу довжини в обох процесах. `SOCK_SEQPACKET` атомарно передає кожне повідомлення цілком, зберігаючи чіткі межі пакетів (Record Boundaries).
2. **`SOCK_DGRAM` проти `SOCK_SEQPACKET`:** Дейтаграмний сокет `SOCK_DGRAM` не встановлює з'єднання і може мовчки відкидати пакети при переповненні буфера. `SOCK_SEQPACKET` гарантує надійну послідовну доставку та сигналізує про закриття іншого кінця сокета.
3. **Відмова від спільної пам'яті (Shared Memory):** Спільна пам'ять між процесами створює небезпеку атак подвійної вибірки (Double-Fetch) та стану гонки (Race Condition). Сокетний обмін змушує ядро виконувати повне копіювання даних в ізольований стек отримувача, усуваючи будь-яку можливість підміни байтів під час перевірки.

## Повна реалізація системи ізольованого парсингу

Наведемо завершений, промисловий код пісочниці мовами C та C++.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <sys/syscall.h>

#define MAX_PAYLOAD 512

/* Структура безпечного DTO для повернення розібраних даних */
typedef struct {
    uint32_t magic;
    uint32_t width;
    uint32_t height;
    uint32_t checksum;
} ParsedHeaderDTO;

/* Встановлення фільтра Seccomp-BPF */
static int install_sandbox_filter(void) {
    struct sock_filter filter[] = {
        /* [0] Перевірка архітектури: завантажити seccomp_data.arch */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
#if defined(__x86_64__)
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
#elif defined(__aarch64__)
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_AARCH64, 1, 0),
#else
#error "Непідтримувана архітектура CPU"
#endif
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        /* [3] Завантажити номер системного виклику: seccomp_data.nr */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

        /* Білий список дозволених системних викликів */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_read, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_write, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_exit_group, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_rt_sigreturn, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_brk, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_mmap, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_munmap, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        /* Усі інші системні виклики (open, execve, socket) знищують процес */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS)
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    /* Заборона на підняття привілеїв (обов'язково для непривілейованого seccomp) */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        return -1;
    }

    if (syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog) != 0) {
        return -1;
    }
    return 0;
}

/* Логіка парсера всередині ізольованого воркера */
static void run_parser_worker(int ipc_fd) {
    if (install_sandbox_filter() != 0) {
        _exit(127);
    }

    uint8_t input_buf[MAX_PAYLOAD];
    ssize_t n = read(ipc_fd, input_buf, sizeof(input_buf));
    if (n < 16) {
        _exit(1);
    }

    /* Простий парсинг заголовка формату: Magic(4) | W(4) | H(4) | CRC(4) */
    ParsedHeaderDTO result;
    memcpy(&result.magic, input_buf, 4);
    memcpy(&result.width, input_buf + 4, 4);
    memcpy(&result.height, input_buf + 8, 4);
    memcpy(&result.checksum, input_buf + 12, 4);

    /* Перевірка магічного байта */
    if (result.magic != 0x54494646) { /* "TIFF" */
        _exit(2);
    }

    /* Надсилання безпечного результату майстру */
    if (write(ipc_fd, &result, sizeof(result)) != (ssize_t)sizeof(result)) {
        _exit(3);
    }

    _exit(0);
}

/* Головний привілейований процес (Master) */
int main(void) {
    int sv[2];
    if (socketpair(AF_UNIX, SOCK_SEQPACKET, 0, sv) != 0) {
        perror("socketpair");
        return EXIT_FAILURE;
    }

    pid_t child_pid = fork();
    if (child_pid < 0) {
        perror("fork");
        close(sv[0]);
        close(sv[1]);
        return EXIT_FAILURE;
    }

    if (child_pid == 0) {
        /* Дочірній процес */
        close(sv[0]); /* Закриваємо сторону майстра */
        run_parser_worker(sv[1]);
    }

    /* Батьківський процес */
    close(sv[1]); /* Закриваємо сторону воркера */

    /* Імітація вхідного пакету від зовнішнього клієнта */
    uint8_t untrusted_input[16] = {
        0x46, 0x46, 0x49, 0x54, /* Magic: "TIFF" у little-endian */
        0x00, 0x04, 0x00, 0x00, /* Width: 1024 */
        0x00, 0x03, 0x00, 0x00, /* Height: 768 */
        0xEF, 0xBE, 0xAD, 0xDE  /* Checksum */
    };

    /* Передача сирих даних у пісочницю */
    if (write(sv[0], untrusted_input, sizeof(untrusted_input)) != sizeof(untrusted_input)) {
        perror("master write");
    }

    /* Очікування безпечного результату від воркера */
    ParsedHeaderDTO header;
    ssize_t read_bytes = read(sv[0], &header, sizeof(header));

    int status = 0;
    waitpid(child_pid, &status, 0);

    if (WIFSIGNALED(status)) {
        int sig = WTERMSIG(status);
        if (sig == SIGSYS) {
            printf("[SECURITY ALERT] Воркер знищено ядром через спробу забороненого системного виклику (SIGSYS)!\n");
        } else {
            printf("[ALERT] Воркер загинув від сигналу %d\n", sig);
        }
    } else if (WIFEXITED(status) && WEXITSTATUS(status) == 0 && read_bytes == sizeof(header)) {
        printf("[OK] Заголовок успішно розібрано у пісочниці: Width=%u, Height=%u\n", header.width, header.height);
    } else {
        printf("[ERROR] Воркер завершився з кодом помилки %d\n", WEXITSTATUS(status));
    }

    close(sv[0]);
    return EXIT_SUCCESS;
}
```
```cpp
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <sys/syscall.h>
#include <unistd.h>

#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <expected>
#include <system_error>
#include <cstring>
#include <memory>

namespace sandbox {

inline constexpr size_t kMaxPayload = 512;

struct ParsedHeaderDTO {
    uint32_t magic{0};
    uint32_t width{0};
    uint32_t height{0};
    uint32_t checksum{0};
};

class [[nodiscard]] ScopedDescriptor {
public:
    explicit ScopedDescriptor(int fd = -1) noexcept : fd_(fd) {}
    ~ScopedDescriptor() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    ScopedDescriptor(const ScopedDescriptor&) = delete;
    ScopedDescriptor& operator=(const ScopedDescriptor&) = delete;

    ScopedDescriptor(ScopedDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    ScopedDescriptor& operator=(ScopedDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) {
                ::close(fd_);
            }
            fd_ = other.fd_;
            other.fd_ = -1;
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

private:
    int fd_{-1};
};

class SeccompFilterBuilder {
public:
    static std::expected<void, std::error_code> apply_strict_sandbox() noexcept {
        struct sock_filter filter[] = {
            BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
#if defined(__x86_64__)
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
#elif defined(__aarch64__)
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_AARCH64, 1, 0),
#else
#error "Непідтримувана архітектура процесора"
#endif
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

            BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_read, 0, 1),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_write, 0, 1),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_exit_group, 0, 1),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_rt_sigreturn, 0, 1),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_brk, 0, 1),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_mmap, 0, 1),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_munmap, 0, 1),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS)
        };

        struct sock_fprog prog = {
            .len = static_cast<unsigned short>(sizeof(filter) / sizeof(filter[0])),
            .filter = filter,
        };

        if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog) != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }
};

class IsolatedWorker {
public:
    static void execute(ScopedDescriptor ipc_channel) noexcept {
        auto result = SeccompFilterBuilder::apply_strict_sandbox();
        if (!result) {
            ::_exit(127);
        }

        std::array<uint8_t, kMaxPayload> buffer{};
        ssize_t bytes_read = ::read(ipc_channel.get(), buffer.data(), buffer.size());
        if (bytes_read < 16) {
            ::_exit(1);
        }

        ParsedHeaderDTO header{};
        std::memcpy(&header.magic, buffer.data(), 4);
        std::memcpy(&header.width, buffer.data() + 4, 4);
        std::memcpy(&header.height, buffer.data() + 8, 4);
        std::memcpy(&header.checksum, buffer.data() + 12, 4);

        if (header.magic != 0x54494646) { // "TIFF"
            ::_exit(2);
        }

        if (::write(ipc_channel.get(), &header, sizeof(header)) != sizeof(header)) {
            ::_exit(3);
        }

        ::_exit(0);
    }
};

class MasterHost {
public:
    static std::expected<ParsedHeaderDTO, std::string> process_untrusted_payload(std::span<const uint8_t> payload) {
        int sv[2];
        if (::socketpair(AF_UNIX, SOCK_SEQPACKET, 0, sv) != 0) {
            return std::unexpected("Не вдалося створити socketpair");
        }

        ScopedDescriptor master_sock(sv[0]);
        ScopedDescriptor worker_sock(sv[1]);

        pid_t pid = ::fork();
        if (pid < 0) {
            return std::unexpected("Помилка fork()");
        }

        if (pid == 0) {
            master_sock.~ScopedDescriptor();
            IsolatedWorker::execute(std::move(worker_sock));
        }

        worker_sock.~ScopedDescriptor();

        if (::write(master_sock.get(), payload.data(), payload.size()) != static_cast<ssize_t>(payload.size())) {
            return std::unexpected("Помилка запису в сокет воркера");
        }

        ParsedHeaderDTO header{};
        ssize_t read_bytes = ::read(master_sock.get(), &header, sizeof(header));

        int status = 0;
        ::waitpid(pid, &status, 0);

        if (WIFSIGNALED(status)) {
            if (WTERMSIG(status) == SIGSYS) {
                return std::unexpected("SECURITY VIOLATION: Воркер знищено сигналом SIGSYS за спробу недозволеного системного виклику!");
            }
            return std::unexpected("Воркер завершився аварійно");
        }

        if (WIFEXITED(status) && WEXITSTATUS(status) == 0 && read_bytes == sizeof(header)) {
            return header;
        }

        return std::unexpected("Воркер повернув помилку валідації");
    }
};

} // namespace sandbox

int main() {
    const std::array<uint8_t, 16> sample_packet = {
        0x46, 0x46, 0x49, 0x54, // "TIFF"
        0x00, 0x08, 0x00, 0x00, // Width: 2048
        0x00, 0x06, 0x00, 0x00, // Height: 1536
        0xAA, 0xBB, 0xCC, 0xDD
    };

    auto result = sandbox::MasterHost::process_untrusted_payload(sample_packet);
    if (result) {
        std::cout << "[C++ OK] Розібрано в пісочниці: " << result->width << "x" << result->height << std::endl;
    } else {
        std::cerr << "[C++ ERROR] " << result.error() << std::endl;
    }

    return 0;
}
```
:::

## Простеження та перевірка поведінки пісочниці під атакою

Для перевірки ефективності ізоляції симулюємо атаку: додамо у код воркера спробу виконати `open("/etc/passwd", O_RDONLY)`.

### 1. Перевірка статусу процесу через procfs

Стан фільтрації процесу можна перевірити безпосередньо у віртуальній файловій системі Linux:

```bash
grep Seccomp /proc/<PID_воркера>/status
# Seccomp: 2   (2 означає режим SECCOMP_MODE_FILTER)
```

### 2. Діагностика порушень через системний журнал auditd

Коли воркер здійснює несанкціонований виклик, підсистема аудиту ядра Linux генерує повідомлення в системний журнал `/var/log/audit/audit.log`:

```
type=SECCOMP msg=audit(1724174400.123:456): auid=1000 uid=1000 gid=1000 
ses=1 subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 
pid=12345 comm="parser_worker" exe="/app/parser_worker" 
sig=31 arch=c000003e syscall=2 compat=0 ip=0x7f1234567890 code=0x0
```

У цьому звіті:
- `sig=31`: Сигнал `SIGSYS` (Bad system call).
- `arch=c000003e`: Архітектура `AUDIT_ARCH_X86_64`.
- `syscall=2`: Номер виклику `SYS_open` в архітектурі x86-64.
- `code=0x0`: Дія `SECCOMP_RET_KILL_PROCESS`.

### 3. Діагностика через утиліту strace

Запуск програми під наглядом трасувальника `strace -f ./sandbox_demo` наочно демонструє момент спрацювання бар'єра:

```
[pid 12345] prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) = 0
[pid 12345] seccomp(SECCOMP_SET_MODE_FILTER, 0, {len=13, filter=0x...}) = 0
[pid 12345] read(4, "TIFF\0\4\0\0\0\3\0\0\xef\xbe\xad\xde", 512) = 16
[pid 12345] open("/etc/passwd", O_RDONLY) = ?
[pid 12345] +++ killed by SIGSYS (core dumped) +++
[pid 12344] --- SIGCHLD {si_signo=SIGCHLD, si_code=CLD_KILLED, si_pid=12345, si_status=SIGSYS} ---
```

Ядро не дозволило виклику `open` навіть розпочати пошук дескриптора в таблиці файлів: процес було нейтралізовано до виконання будь-яких дискових операцій.

## Крайові випадки та захист від відмови в обслуговуванні (DoS)

Під час експлуатації пісочниці у високонавантажених сервісах слід враховувати три критичні крайові випадки:

1. **Зависання парсера (Нескінченний цикл):** Якщо пошкоджений файл спричиняє нескінченний цикл у коді воркера, процес не викликатиме системних викликів і не впаде за Seccomp. Майстер-процес зобов'язаний встановлювати жорсткий таймаут на читання з сокета через `poll()` або `select()`. Якщо за 100 мс відповідь не надійшла, майстер посилає сигнал `kill(child_pid, SIGKILL)` і перезапускає пісочницю.
2. **Вичерпання пам'яті (Memory Exhaustion):** Воркер може спробувати виділити гігабайти пам'яті через `malloc()` для виклику відмови в обслуговуванні хоста. Перед запуском Seccomp майстер встановлює ліміт віртуальної пам'яті через `setrlimit(RLIMIT_AS, &limit)` або поміщає воркер у виділену контрольну групу `cgroups v2` з обмеженням `memory.max = 64M`.
3. **Обробка сигналів (Signal Safety):** Якщо воркер отримує сигнал `SIGPIPE` або `SIGTERM`, обробник сигналу повинен мати право викликати `SYS_rt_sigreturn`. Саме тому `SYS_rt_sigreturn` обов'язково включено до білого списку нашого Seccomp-фільтра; без нього будь-який сигнал призвів би до аварійного падіння з `SIGSYS`.

Завдяки поєднанню Seccomp-BPF, сокетного обміну `SOCK_SEQPACKET` та захисту від підвищення прав `PR_SET_NO_NEW_PRIVS` створюється непереборна межа довіри, яка надійно захищає критичну інфраструктуру від найскладніших атак нульового дня в сторонніх бібліотеках.
