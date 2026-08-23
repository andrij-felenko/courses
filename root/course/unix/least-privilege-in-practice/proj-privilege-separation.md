# ⚙️ Реалізація розподілу привілеїв: безпечний мережевий демон із Seccomp та пісочницею

Цей проект демонструє повну практичну реалізацію принципу найменших привілеїв для мережевого сервісу в Linux. Ми створимо повноцінну архітектуру з розділенням привілеїв (*Privilege Separation*), де сервіс розділено на два окремі процеси з чітким розмежуванням повноважень: привілейованого майстра-супервізора (*Master*) та ізольованого непривілейованого обробника (*Worker*), які взаємодіють через локальний Unix Domain сокет.

Усі приклади коду наведено двома мовами: низькорівневою **C** із прямими системними викликами POSIX/Linux та ідіоматичною сучасною **C++** із застосуванням концепції RAII, безпечних типізованих обгорток дескрипторів та обробки помилок через `std::expected`.

---

## 1. Постановка задачі та архітектурна схема

Класичний мережевий сервер, запущений від імені суперкористувача `root`, становить колосальну загрозу для безпеки операційної системи. Якщо в складному коді парсера протоколу (обробка HTTP-заголовків, розбір TLS-пакетів або декодування DNS-запитів) виникає вразливість — переповнення буфера на стеку, пошкодження купи (*heap corruption*), розіменування нульового вказівника або помилка форматування рядка — зловмисник отримує можливість виконати довільний машинний код із максимальними системними привілеями. Маючи `UID 0` та повний набір capabilities, такий процес може змінювати системні файли конфігурації `/etc/shadow`, встановлювати модулі ядра (*rootkits*), змінювати правила брандмауера та читати оперативну пам'ять інших процесів.

Для кардинального усунення цього класу загроз ми застосовуємо фундаментальний архітектурний патерн розділення привілеїв (*Privilege Separation*), вперше запроваджений у проектах OpenSSH та Postfix:

1. **Привілейований процес (Master / Supervisor):**
   * Запускається від імені адміністратора (`root`) або з вузьким набором прав `CAP_NET_BIND_SERVICE`.
   * Створює двосторонній локальний канал зв'язку через `socketpair()`.
   * Відкриває мережевий сокет, встановлює параметри сокета (`SO_REUSEADDR`) та виконує прив'язку (`bind()`) до захищеного порту (наприклад, TCP `8080` або `80`).
   * Породжує дочірній процес воркера за допомогою `fork()`.
   * Переходить у безпечний цикл прийому нових клієнтських підключень (`accept()`).
   * Отримавши новий сокет клієнта, майстер передає його відкритий файловий дескриптор у процес воркера через сокет керування за допомогою допоміжних повідомлень ядра `SCM_RIGHTS`.
   * Сам майстер **ніколи не читає і не парсить** неперевірені байти клієнтського мережевого трафіку. Його кодова база мінімальна і легко піддається аудиту.
   * Майстер обробляє сигнал `SIGCHLD`, контролює стан воркера через `waitpid()` та автоматично перезапускає новий екземпляр воркера у разі його аварійного падіння.

2. **Непривілейований процес (Worker / Sandbox):**
   * Одразу після `fork()` закриває кінець сокета керування, що належить майстру, розриваючи непотрібні зв'язки.
   * Викликає `setgroups(0, NULL)` для очищення додаткових груп суперкористувача.
   * Безповоротно скидає свій GID та UID на виділеного системного користувача (наприклад, `nobody` або `_daemon`) за допомогою `setresgid()` та `setresuid()`.
   * Встановлює прапорець `PR_SET_NO_NEW_PRIVS` через виклик `prctl()`, забороняючи будь-яке підвищення прав через біти `setuid` чи файлові capabilities.
   * Конструює та завантажує жорсткий фільтр системних викликів Seccomp-BPF. Фільтр дозволяє виключно той мінімум системних викликів, який необхідний для обробки переданих сокетів (`read`, `write`, `recvmsg`, `sendmsg`, `close`, `epoll_wait`, `epoll_ctl`, `futex`, `exit_group`).
   * Отримує дескриптори клієнтських сокетів від майстра, читає HTTP-запити, виконує бізнес-логіку та повертає HTTP-відповіді.
   * Навіть якщо зловмисник знайде вразливість у воркері та захопить потік виконання через ROP-ланцюжок (*Return-Oriented Programming*), він опиниться у повній ізоляції: процес не має прав суперкористувача, позбавлений capabilities, а будь-яка спроба викликати `execve()`, `socket()`, `connect()`, `openat()` чи `ptrace()` буде негайно заблокована ядром на рівні Seccomp.

---

## 2. Реалізація передачі дескрипторів через `SCM_RIGHTS`

Оскільки ізольований воркер позбавлений права відкривати нові сокети або файли, передача вже відкритих файлових дескрипторів між процесами є ключовим механізмом взаємодії.

У Linux передача дескриптора здійснюється через системний виклик `sendmsg()` над сокетом сімейства `AF_UNIX`. Разом зі звичайними байтами даних відправник формує блок допоміжних службових даних (*ancillary data* / *control message*), заповнюючи структуру `struct cmsghdr` з рівнем `SOL_SOCKET` та типом `SCM_RIGHTS`.

### 2.1. Анатомія пам'яті керуючого повідомлення

Структура `struct msghdr` вимагає суворого вирівнювання пам'яті для масиву дескрипторів. Макрос `CMSG_SPACE(sizeof(int))` обчислює загальний розмір буфера з урахуванням вирівнювання за межами 64-бітних слів процесора, а макрос `CMSG_LEN(sizeof(int))` визначає фактичну довжину блоку даних для поля `cmsg_len`.

```
Буфер допоміжних даних msg_control:
┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
│ struct cmsghdr          │ int fd                  │ Падінг вирівнювання     │
│ cmsg_len, level, type   │ (переданий дескриптор)  │ (до CMSG_SPACE байтів)  │
└─────────────────────────┴─────────────────────────┴─────────────────────────┘
 ▲                         ▲
 └── CMSG_FIRSTHDR(&msg)   └── CMSG_DATA(cmsg)
```

Коли ядро отримує таке повідомлення через внутрішню функцію `scm_send()`, воно знаходить структуру `struct file` у таблиці відправника та збільшує її лічильник посилань `f_count`. Коли воркер викликає `recvmsg()`, ядро виділяє новий вільний номер у таблиці дескрипторів воркера, прив'язує його до тієї самої структури `struct file` і повертає цей номер у масиві даних `CMSG_DATA()`.

:::tabs
```c
#define _GNU_SOURCE
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>

/* Відправка файлового дескриптора через Unix Domain сокет */
int send_fd(int socket_fd, int fd_to_send) {
    struct msghdr msg = {0};
    struct iovec iov[1];
    char dummy_char = 'F'; /* Обов'язковий 1 байт корисних даних для протоколу */
    
    /* Буфер для збереження заголовка cmsghdr та самого int дескриптора */
    char cmsg_buf[CMSG_SPACE(sizeof(int))];
    memset(cmsg_buf, 0, sizeof(cmsg_buf));

    iov[0].iov_base = &dummy_char;
    iov[0].iov_len = sizeof(dummy_char);
    msg.msg_iov = iov;
    msg.msg_iovlen = 1;

    msg.msg_control = cmsg_buf;
    msg.msg_controllen = sizeof(cmsg_buf);

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));

    /* Копіюємо числовий дескриптор у область даних cmsghdr */
    memcpy(CMSG_DATA(cmsg), &fd_to_send, sizeof(int));

    if (sendmsg(socket_fd, &msg, 0) < 0) {
        perror("sendmsg SCM_RIGHTS");
        return -1;
    }
    return 0;
}

/* Отримання переданого дескриптора з Unix Domain сокета */
int recv_fd(int socket_fd) {
    struct msghdr msg = {0};
    struct iovec iov[1];
    char dummy_char = 0;
    char cmsg_buf[CMSG_SPACE(sizeof(int))];
    memset(cmsg_buf, 0, sizeof(cmsg_buf));

    iov[0].iov_base = &dummy_char;
    iov[0].iov_len = sizeof(dummy_char);
    msg.msg_iov = iov;
    msg.msg_iovlen = 1;

    msg.msg_control = cmsg_buf;
    msg.msg_controllen = sizeof(cmsg_buf);

    ssize_t bytes_read = recvmsg(socket_fd, &msg, 0);
    if (bytes_read <= 0) {
        return -1; /* З'єднання закрито або сталася помилка */
    }

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    if (cmsg == NULL || cmsg->cmsg_level != SOL_SOCKET || cmsg->cmsg_type != SCM_RIGHTS) {
        fprintf(stderr, "Помилка: отримано повідомлення без блоку SCM_RIGHTS\n");
        return -1;
    }

    int received_fd = -1;
    memcpy(&received_fd, CMSG_DATA(cmsg), sizeof(int));
    return received_fd;
}
```
```cpp
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <cstring>
#include <iostream>
#include <expected>
#include <system_error>
#include <array>

// RAII-обгортка для автоматичного управління життєвим циклом дескрипторів
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

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
};

// Відправка файлового дескриптора через сокет Unix
[[nodiscard]] std::expected<void, std::error_code> send_fd(int socket_fd, int fd_to_send) noexcept {
    struct msghdr msg{};
    struct iovec iov{};
    char dummy_char = 'F';

    alignas(struct cmsghdr) std::array<char, CMSG_SPACE(sizeof(int))> cmsg_buf{};

    iov.iov_base = &dummy_char;
    iov.iov_len = sizeof(dummy_char);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cmsg_buf.data();
    msg.msg_controllen = cmsg_buf.size();

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

// Отримання переданого дескриптора з сокета Unix
[[nodiscard]] std::expected<UniqueFd, std::error_code> recv_fd(int socket_fd) noexcept {
    struct msghdr msg{};
    struct iovec iov{};
    char dummy_char = 0;
    alignas(struct cmsghdr) std::array<char, CMSG_SPACE(sizeof(int))> cmsg_buf{};

    iov.iov_base = &dummy_char;
    iov.iov_len = sizeof(dummy_char);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cmsg_buf.data();
    msg.msg_controllen = cmsg_buf.size();

    if (::recvmsg(socket_fd, &msg, 0) <= 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    struct cmsghdr* cmsg = CMSG_FIRSTHDR(&msg);
    if (!cmsg || cmsg->cmsg_level != SOL_SOCKET || cmsg->cmsg_type != SCM_RIGHTS) {
        return std::unexpected(std::make_error_code(std::errc::bad_message));
    }

    int received_fd = -1;
    std::memcpy(&received_fd, CMSG_DATA(cmsg), sizeof(int));
    return UniqueFd(received_fd);
}
```
:::

---

## 3. Складання та завантаження BPF-фільтра для воркера

Фільтр Seccomp-BPF працює як спеціалізована віртуальна машина ядра. Ми програмуємо фільтр у вигляді масиву інструкцій `struct sock_filter`. Кожна інструкція складається з чотирьох полів:
* `code`: код операції віртуальної машини (завантаження, порівняння, безумовний перехід або повернення значення).
* `jt`: зсув переходу за адресою інструкцій у разі істинності умови (*jump true*).
* `jf`: зсув переходу за адресою інструкцій у разі хибності умови (*jump false*).
* `k`: константа або зміщення для адресації пам'яті структури `struct seccomp_data`.

### 3.1. Логіка виконання інструкцій фільтра

Послідовність перевірок нашого BPF-фільтра:
1. Завантажити поле `arch` зі структури `seccomp_data`.
2. Перевірити, що архітектура збігається з `AUDIT_ARCH_X86_64`. Якщо зловмисник намагається використати 32-бітний шлюз емуляції `int 0x80`, фільтр негайно вбиває процес дією `SECCOMP_RET_KILL_PROCESS`.
3. Завантажити номер системного виклику `nr`.
4. Порівняти `nr` із білим списком дозволених системних викликів. Якщо знайдено збіг — перейти до інструкції `SECCOMP_RET_ALLOW`.
5. Якщо номер виклику не знайдено в білому списку — повернути дію `SECCOMP_RET_ERRNO` з кодом помилки `EPERM`. Це блокує виконання виклику в ядрі, повертаючи процесу стандартну помилку `EPERM`.

:::tabs
```c
#define _GNU_SOURCE
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <sys/syscall.h>
#include <sys/prctl.h>
#include <stddef.h>
#include <stdio.h>
#include <errno.h>

int install_worker_seccomp_filter(void) {
    /* 1. Блокуємо підвищення привілеїв (обов'язкова передумова Seccomp) */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        perror("prctl(PR_SET_NO_NEW_PRIVS)");
        return -1;
    }

    /* 2. Масив інструкцій класичного Berkeley Packet Filter (cBPF) */
    struct sock_filter filter[] = {
        /* [0] Завантажуємо номер архітектури процесора з seccomp_data.arch */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
        
        /* [1] Перевіряємо архітектуру x86_64; у разі невідповідності — вбиваємо процес */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        /* [2] Завантажуємо номер системного виклику з seccomp_data.nr */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

        /* [3..12] Перевіряємо номер виклику проти дозволеного білого списку */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_read,            10, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_write,           9, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_recvmsg,         8, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_sendmsg,         7, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_close,           6, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_epoll_wait,      5, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_epoll_ctl,       4, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_futex,           3, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_restart_syscall, 2, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_exit_group,      1, 0),

        /* За замовчуванням блокуємо виклик і повертаємо EPERM */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

        /* Дозвіл для системних викликів із білого списку */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    /* Завантажуємо BPF-фільтр у контекст поточного процесу */
    if (syscall(__NR_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog) != 0) {
        perror("seccomp(SECCOMP_SET_MODE_FILTER)");
        return -1;
    }
    return 0;
}
```
```cpp
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <sys/syscall.h>
#include <sys/prctl.h>
#include <cstddef>
#include <expected>
#include <system_error>
#include <array>

[[nodiscard]] std::expected<void, std::error_code> install_worker_seccomp() noexcept {
    // Встановлення прапорця блокування нових привілеїв
    if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    constexpr std::array filter = {
        // Перевірка архітектури CPU
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        // Завантаження номера виклику
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

        // Білий список системних викликів
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_read,            10, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_write,           9, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_recvmsg,         8, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_sendmsg,         7, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_close,           6, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_epoll_wait,      5, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_epoll_ctl,       4, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_futex,           3, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_restart_syscall, 2, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_exit_group,      1, 0),

        // Блокування всіх інших викликів із кодом помилки EPERM
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

        // Дозвіл для системних викликів із білого списку
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };

    struct sock_fprog prog{
        .len = static_cast<unsigned short>(filter.size()),
        .filter = const_cast<struct sock_filter*>(filter.data()),
    };

    if (::syscall(__NR_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
```
:::

---

## 4. Повний робочий цикл демона з розділенням привілеїв

Нижче наведено повну реалізацію сервера, який відкриває захищений мережевий порт `8080`, скидає привілеї та делегує клієнтські підключення в ізольований процес-воркер.

:::tabs
```c
#define _GNU_SOURCE
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <unistd.h>
#include <grp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#define TARGET_UID 65534 /* nobody */
#define TARGET_GID 65534 /* nogroup */
#define LISTEN_PORT 8080

/* Оголошення допоміжних функцій */
int send_fd(int socket_fd, int fd_to_send);
int recv_fd(int socket_fd);
int install_worker_seccomp_filter(void);

/* Робочий цикл непривілейованого воркера */
void run_worker(int channel_fd) {
    /* 1. Очищуємо додаткові групи суперкористувача */
    if (setgroups(0, NULL) != 0) {
        perror("worker: setgroups");
        exit(EXIT_FAILURE);
    }

    /* 2. Безповоротно скидаємо GID та UID */
    if (setresgid(TARGET_GID, TARGET_GID, TARGET_GID) != 0) {
        perror("worker: setresgid");
        exit(EXIT_FAILURE);
    }
    if (setresuid(TARGET_UID, TARGET_UID, TARGET_UID) != 0) {
        perror("worker: setresuid");
        exit(EXIT_FAILURE);
    }

    /* 3. Вмикаємо пісочницю Seccomp-BPF */
    if (install_worker_seccomp_filter() != 0) {
        fprintf(stderr, "worker: не вдалося активувати seccomp\n");
        exit(EXIT_FAILURE);
    }

    printf("[Worker PID %d] Успішно скинув права до UID %d і увійшов у пісочницю\n",
           getpid(), getuid());

    /* 4. Головний цикл обробки підключень */
    while (1) {
        int client_fd = recv_fd(channel_fd);
        if (client_fd < 0) {
            break; /* Майстер закрив сокет зв'язку або завершив роботу */
        }

        const char response[] = "HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nHello, World!";
        write(client_fd, response, sizeof(response) - 1);
        close(client_fd);
    }
    exit(EXIT_SUCCESS);
}

int main(void) {
    int channel[2];
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, channel) != 0) {
        perror("socketpair");
        return EXIT_FAILURE;
    }

    pid_t worker_pid = fork();
    if (worker_pid < 0) {
        perror("fork");
        return EXIT_FAILURE;
    }

    if (worker_pid == 0) {
        /* Дочірній процес: закриваємо дескриптор сторони майстра */
        close(channel[0]);
        run_worker(channel[1]);
    }

    /* Батьківський процес (Master): закриваємо дескриптор сторони воркера */
    close(channel[1]);
    int master_chan = channel[0];

    /* Відкриваємо мережевий сокет */
    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        perror("master: socket");
        return EXIT_FAILURE;
    }

    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(LISTEN_PORT);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(listen_fd, (struct sockaddr *)&addr, sizeof(addr)) != 0) {
        perror("master: bind");
        return EXIT_FAILURE;
    }

    if (listen(listen_fd, 128) != 0) {
        perror("master: listen");
        return EXIT_FAILURE;
    }

    printf("[Master PID %d] Слухає порт %d, передає клієнтів воркеру PID %d\n",
           getpid(), LISTEN_PORT, worker_pid);

    /* Майстер приймає з'єднання і делегує дескриптор воркеру */
    for (int i = 0; i < 5; ++i) {
        int client_fd = accept(listen_fd, NULL, NULL);
        if (client_fd < 0) {
            perror("master: accept");
            continue;
        }

        if (send_fd(master_chan, client_fd) != 0) {
            fprintf(stderr, "master: помилка передачі дескриптора\n");
        }
        /* Закриваємо власну копію дескриптора в майстрі */
        close(client_fd);
    }

    close(listen_fd);
    close(master_chan);
    waitpid(worker_pid, NULL, 0);
    printf("[Master] Роботу завершено штатно.\n");
    return EXIT_SUCCESS;
}
```
```cpp
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <unistd.h>
#include <grp.h>
#include <iostream>
#include <string_view>
#include <cstdlib>

constexpr uid_t TARGET_UID = 65534; // nobody
constexpr gid_t TARGET_GID = 65534; // nogroup
constexpr uint16_t LISTEN_PORT = 8080;

// Оголошення функцій із розділів 2 та 3
[[nodiscard]] std::expected<void, std::error_code> send_fd(int socket_fd, int fd_to_send) noexcept;
[[nodiscard]] std::expected<UniqueFd, std::error_code> recv_fd(int socket_fd) noexcept;
[[nodiscard]] std::expected<void, std::error_code> install_worker_seccomp() noexcept;

void run_worker(UniqueFd channel) {
    // 1. Очищення додаткових груп
    if (::setgroups(0, nullptr) != 0) {
        std::cerr << "worker: setgroups failed\n";
        std::exit(EXIT_FAILURE);
    }

    // 2. Скидання GID та UID
    if (::setresgid(TARGET_GID, TARGET_GID, TARGET_GID) != 0 ||
        ::setresuid(TARGET_UID, TARGET_UID, TARGET_UID) != 0) {
        std::cerr << "worker: privilege drop failed\n";
        std::exit(EXIT_FAILURE);
    }

    // 3. Увімкнення Seccomp
    if (auto res = install_worker_seccomp(); !res) {
        std::cerr << "worker: seccomp installation failed: " << res.error().message() << "\n";
        std::exit(EXIT_FAILURE);
    }

    std::cout << "[Worker PID " << ::getpid() << "] Права скинуто до UID " << ::getuid() << ", seccomp активний\n";

    // 4. Обробка клієнтських запитів
    while (true) {
        auto client_fd = recv_fd(channel.get());
        if (!client_fd) {
            break; // Майстер закрив керуючий сокет
        }

        constexpr std::string_view response = "HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nHello, World!";
        ::write(client_fd->get(), response.data(), response.size());
    }
    std::exit(EXIT_SUCCESS);
}

int main() {
    int fds[2];
    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) != 0) {
        std::cerr << "socketpair error\n";
        return EXIT_FAILURE;
    }

    UniqueFd master_chan(fds[0]);
    UniqueFd worker_chan(fds[1]);

    pid_t worker_pid = ::fork();
    if (worker_pid < 0) {
        std::cerr << "fork error\n";
        return EXIT_FAILURE;
    }

    if (worker_pid == 0) {
        master_chan.reset(); // Закриваємо сторону майстра
        run_worker(std::move(worker_chan));
    }

    worker_chan.reset(); // Закриваємо сторону воркера

    UniqueFd listen_fd(::socket(AF_INET, SOCK_STREAM, 0));
    if (!listen_fd.valid()) {
        std::cerr << "master: socket error\n";
        return EXIT_FAILURE;
    }

    int opt = 1;
    ::setsockopt(listen_fd.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(LISTEN_PORT);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (::bind(listen_fd.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) != 0 ||
        ::listen(listen_fd.get(), 128) != 0) {
        std::cerr << "master: bind/listen error\n";
        return EXIT_FAILURE;
    }

    std::cout << "[Master PID " << ::getpid() << "] Слухає порт " << LISTEN_PORT << "\n";

    for (int i = 0; i < 5; ++i) {
        UniqueFd client_fd(::accept(listen_fd.get(), nullptr, nullptr));
        if (client_fd.valid()) {
            static_cast<void>(send_fd(master_chan.get(), client_fd.get()));
        }
    }

    master_chan.reset();
    listen_fd.reset();
    ::waitpid(worker_pid, nullptr, 0);
    std::cout << "[Master] Завершення роботи.\n";
    return EXIT_SUCCESS;
}
```
:::

---

## 5. Діагностика, налагодження та аналіз крайових випадків

### 5.1. Трасування фільтрації Seccomp через `strace`

При розробці та тестуванні пісочниць найпоширенішою інженерною проблемою є блокування системних викликів, які неявно здійснюються стандартною бібліотекою мови C (`glibc` або `musl`). Наприклад, виклики `malloc()` або `std::string` при розростанні пам'яті можуть виконувати системні виклики `brk` або `mmap`. Крім того, функції отримання поточного часу або випадкових чисел можуть викликати `clock_gettime` чи `getrandom`.

Для швидкої діагностики заблокованих викликів використовуйте утиліту `strace` зі спеціальним фільтром:

```bash
# Відстеження операцій керування привілеями та системних викликів seccomp
strace -f -e trace=seccomp,prctl,setresuid,setresgid,setgroups ./privilege_demo
```

Якщо воркер спробує виконати системний виклик `openat()`, який відсутній у нашому білому списку, у виводі `strace` з'явиться відповідний запис:

```
[pid  4912] openat(AT_FDCWD, "/etc/passwd", O_RDONLY) = -1 EPERM (Operation not permitted)
```

Завдяки поверненню дії `SECCOMP_RET_ERRNO` замість `SECCOMP_RET_KILL_PROCESS`, процес не падає аварійно від сигналу `SIGSYS`, а отримує зрозумілий код помилки `EPERM`, що значно полегшує локалізацію проблеми під час розробки.

### 5.2. Пастки обробки дескрипторів та витоку ресурсів

1. **Не закрита копія дескриптора в майстрі:**
   Коли майстер передає `client_fd` до воркера через `send_fd()`, ядро збільшує лічильник посилань на відповідну структуру `struct file`. Якщо майстер забуде викликати `close(client_fd)` у своєму циклі після виклику `send_fd()`, сокет залишиться відкритим у майстрі навіть після того, як воркер повністю завершить обробку запиту та викличе `close()`. Клієнтське TCP-з'єднання не отримає пакет `FIN`, зависне у стані очікування, а таблиця файлових дескрипторів майстра поступово вичерпається.

2. **Вразливість `Time-of-Check to Time-of-Use` (TOCTOU) при роботі з файловою системою:**
   Ніколи не передавайте між майстром і воркером строкові імена або шляхи файлової системи для подальшого відкриття привілейованим процесом. Зловмисник, що скомпрометував воркера, може підмінити вказаний файл символьним посиланням (`symlink`) на `/etc/shadow` безпосередньо між моментом перевірки шляху та моментом його відкриття. У моделі розподілу привілеїв майстер зобов'язаний самостійно відкривати всі ресурси за жорстко зафіксованими абсолютними шляхами і передавати у воркер лише готові файлові дескриптори.

3. **Стійкість майстра до збоїв воркера:**
   У промислових серверах майстер налаштовує обробник сигналу `SIGCHLD` за допомогою системного виклику `sigaction()` з прапорцем `SA_NOCLDSTOP`. Якщо воркер аварійно завершується (наприклад, через помилку сегментації пам'яті або спрацьовування забороненого Seccomp-виклику), майстер викликає `waitpid(-1, &status, WNOHANG)`, реєструє подію в системному журналі та негайно відкриває нову пару `socketpair()`, породжуючи свіжий ізольований екземпляр воркера без зупинки слухаючого TCP-порта та без втрати вхідних з'єднань клієнтів.
