# 📋 Довідник системних викликів, опцій сокета та прапорців OOB

Системний довідник структур даних, прапорців системних викликів `send`/`recv`, опцій сокета `SO_OOBINLINE`, команд `ioctl` та прапорців асинхронного сповіщення для роботи з позасмуговими даними в ядрі Linux.

Цей довідник описує повний програмний контракт (API) підсистеми термінових даних TCP у ядрі Linux. Тут зведено сигнатури системних викликів, структуру ядерних типізованих об'єктів, коди помилок `errno`, параметри конфігурації sysctl та специфіку поведінки системних функцій у неблокуючому режимі.

---

## 1. Системний виклик send() та прапорець MSG_OOB

Виклик `send()` (а також його розширені аналоги `sendto()` та `sendmsg()`) з прапорцем `MSG_OOB` використовується відправником для позначення даних як термінових.

### 1.1. Сигнатура та параметри

```c
#include <sys/types.h>
#include <sys/socket.h>

ssize_t send(int sockfd, const void *buf, size_t len, int flags);
```

- `sockfd`: Файловий дескриптор відкритого та підключеного потокового сокета (`SOCK_STREAM`).
- `buf`: Вказівник на буфер у пам'яті простору користувача, що містить дані для відправки.
- `len`: Кількість байтів для передачі.
- `flags`: Більтове поле прапорців. Для відправки термінових даних включає біт `MSG_OOB`.

### 1.2. Семантика обробки в ядрі Linux

При виклику `send(sockfd, buf, len, MSG_OOB)` ядро Linux виконує наступні дії:

1. Перевіряє, що сокет належить до типу `SOCK_STREAM` і використовує протокол TCP. Якщо сокет є сокетом датаграм (`SOCK_DGRAM`) або UNIX-сокетом без підтримки OOB, ядро повертає помилку `-1` і встановлює `errno = EOPNOTSUPP`.
2. Останній байт у переданому буфері `buf[len - 1]` розглядається як терміновий байт. Усі попередні байти від `buf[0]` до `buf[len - 2]` передаються як звичайний потік даних.
3. Формує TCP-сегмент, у заголовку якого встановлює біт `URG = 1`.
4. Обчислює 16-бітне значення `Urgent Pointer` відносно `Sequence Number` цього сегмента і записує його в заголовок TCP.
5. У внутрішній структурі сокета `struct tcp_sock` оновлюється нове значення порядкового номера термінового байта `urg_seq`.

### 1.3. Можливі коди помилок (errno)

- `EOPNOTSUPP`: Сокет не підтримує передачу термінових даних (наприклад, UDP-сокет або raw-сокет).
- `ENOTCONN`: Сокет перебуває у нез'єднаному стані (не викликано `connect()` або `accept()`).
- `EWOULDBLOCK` / `EAGAIN`: Сокет переведено в неблокуючий режим (`O_NONBLOCK`), а вихідний буфер сокета (`sk_write_queue`) повністю заповнений.
- `EMSGSIZE`: Розмір повідомлення перевищує максимальний дозволений розмір буфера.
- `ECONNRESET`: З'єднання було насильно скинуто віддаленим вузлом (надіслано TCP RST).

---

## 2. Системний виклик recv() та прапорець MSG_OOB

Виклик `recv()` (а також `recvfrom()` та `recvmsg()`) з прапорцем `MSG_OOB` використовується приймачем для вилучення позасмугового байта з окремого буфера ядра.

### 2.1. Сигнатура та параметри

```c
#include <sys/types.h>
#include <sys/socket.h>

ssize_t recv(int sockfd, void *buf, size_t len, int flags);
```

- `sockfd`: Дескриптор підключеного сокета.
- `buf`: Вказівник на буфер у просторі користувача для запису прочитаного байта.
- `len`: Розмір буфера (для читання OOB зазвичай передають значення `1`).
- `flags`: Повинні містити біт `MSG_OOB`.

### 2.2. Правила поведінки та крайові випадки

- **Звичайний режим (`SO_OOBINLINE = 0`):** Виклик `recv(..., MSG_OOB)` вичитає терміновий байт із внутрішнього поля `urg_data` структури `struct tcp_sock`. Цей байт вилучається із загального вхідного потоку і не буде прочитаний звичайним викликом `read()`.
- **Режим вбудованих даних (`SO_OOBINLINE = 1`):** Виклик `recv(..., MSG_OOB)` завершується помилкою `-1`, а `errno` встановлюється в `EINVAL`, оскільки терміновий байт збережено безпосередньо у загальному вхідному потоці.
- **Повторний виклик:** Після того як терміновий байт прочитано додатком, повторний виклик `recv(..., MSG_OOB)` поверне помилку `EINVAL`, оскільки маркер терміновості вважається вичерпаним (якщо віддалена сторона не надіслала новий сегмент з `URG=1`).
- **Спроба прочитати OOB до його прибуття:** Якщо віддалена сторона надіслала сегмент з `URG=1`, але сам пакет ще перебуває у мережі або затримується переупорядкуванням байтів, виклик у блокуючому режимі чекатиме прибуття пакета. У неблокуючому режимі повертається `-1` з `errno = EWOULDBLOCK`.

---

## 3. Опція сокета SO_OOBINLINE

Опція рівню сокета `SOL_SOCKET` регулює розташування термінового байта у вхідній черзі ядра.

### 3.1. Управління через setsockopt / getsockopt

```c
#include <sys/socket.h>

int setsockopt(int sockfd, int level, int optname, const void *optval, socklen_t optlen);
int getsockopt(int sockfd, int level, int optname, void *optval, socklen_t *optlen);
```

- `level`: `SOL_SOCKET`
- `optname`: `SO_OOBINLINE`
- `optval`: Вказівник на ціле число `int` (значення `0` або `1`).
- `optlen`: Розмір змінної `sizeof(int)`.

### 3.2. Вплив на роботу VFS read() та recv()

:::tabs
```c
#include <sys/socket.h>
#include <stdio.h>
#include <errno.h>

int set_oob_inline(int sockfd, int enable) {
    int optval = enable ? 1 : 0;
    if (setsockopt(sockfd, SOL_SOCKET, SO_OOBINLINE, &optval, sizeof(optval)) < 0) {
        perror("setsockopt SO_OOBINLINE");
        return -1;
    }
    return 0;
}
```
```cpp
#include <sys/socket.h>
#include <system_error>
#include <iostream>

void set_oob_inline(int sockfd, bool enable) {
    int optval = enable ? 1 : 0;
    if (::setsockopt(sockfd, SOL_SOCKET, SO_OOBINLINE, &optval, sizeof(optval)) < 0) {
        throw std::system_error(errno, std::generic_category(), "setsockopt SO_OOBINLINE failed");
    }
}
```
:::

- При `SO_OOBINLINE = 0` терміновий байт пропускається звичайними викликами `read()` або `recv(..., 0)`. Потік даних подається додатку так, ніби цього байта в ньому взагалі не було.
- При `SO_OOBINLINE = 1` терміновий байт залишається на своїй природній позиції в потоці sequence numbers. Виклик `read()` прочитає його як звичайний байт. Для виявлення його позиції процес повинен викликати `ioctl(SIOCATMARK)`.

---

## 4. Команда ioctl: SIOCATMARK

Команда `SIOCATMARK` системного виклику `ioctl()` призначена для визначення того, чи вказує поточний покажчик вхідного буфера безпосередньо на терміновий байт.

### 4.1. Сигнатура та параметри

```c
#include <sys/ioctl.h>

int ioctl(int fd, unsigned long request, int *atmark);
```

- `fd`: Дескриптор сокета.
- `request`: `SIOCATMARK`
- `atmark`: Вказівник на змінну типу `int`, куди ядро записує результат (значення `1` або `0`).

### 4.2. Алгоритм роботи в ядрі

Усередині ядра виклик `SIOCATMARK` виконує перевірку полів `struct tcp_sock`:

```c
/* Спрощена логіка ядра Linux для SIOCATMARK */
int tcp_atmark(const struct tcp_sock *tp)
{
    return tp->urg_data && tp->copied_seq == tp->urg_seq;
}
```

:::tabs
```c
#include <sys/ioctl.h>
#include <stdio.h>

int is_socket_at_mark(int sockfd) {
    int mark = 0;
    if (ioctl(sockfd, SIOCATMARK, &mark) < 0) {
        perror("ioctl SIOCATMARK");
        return -1;
    }
    return mark; // 1 — на маркері, 0 — ні
}
```
```cpp
#include <sys/ioctl.h>
#include <system_error>

bool is_socket_at_mark(int sockfd) {
    int mark = 0;
    if (::ioctl(sockfd, SIOCATMARK, &mark) < 0) {
        throw std::system_error(errno, std::generic_category(), "ioctl SIOCATMARK failed");
    }
    return mark != 0;
}
```
:::

---

## 5. Налаштування власника сокета: fcntl F_SETOWN та F_SETOWN_EX

Щоб ядро надсилало сигнал `SIGURG` при виникненні термінових даних, необхідно призначити процес чи групу процесів власником сокета.

### 5.1. Використання F_SETOWN та F_GETOWN

```c
#include <fcntl.h>

int fcntl(int fd, int cmd, int arg);
```

- `cmd`: `F_SETOWN` — призначає власника; `F_GETOWN` — повертає поточний PID власника.
- `arg`: PID процесу (позитивне значення) або PGID групи процесів (від'ємне значення).

:::tabs
```c
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

int register_socket_owner(int sockfd) {
    if (fcntl(sockfd, F_SETOWN, getpid()) < 0) {
        perror("fcntl F_SETOWN");
        return -1;
    }
    return 0;
}
```
```cpp
#include <fcntl.h>
#include <unistd.h>
#include <system_error>

void register_socket_owner(int sockfd) {
    if (::fcntl(sockfd, F_SETOWN, ::getpid()) < 0) {
        throw std::system_error(errno, std::generic_category(), "fcntl F_SETOWN failed");
    }
}
```
:::

### 5.2. Використання розширеного виклику F_SETOWN_EX

У багатопотокових програмах Linux дозволяє вказувати власником не просто процес, а конкретний LWP (Lightweight Process / Thread ID) за допомогою `F_SETOWN_EX`:

```c
#include <fcntl.h>

struct f_owner_ex {
    int type; // F_OWNER_TID, F_OWNER_PID, F_OWNER_PGRP
    pid_t pid;
};
```

---

## 6. Прапорці мультиплексування I/O: select, poll, epoll

В опитувальних циклах подій термінові дані відстежуються за допомогою спеціальних прапорців високого пріоритету.

| Механізм | Прапорець / Маска | Поведінка ядра |
| :--- | :--- | :--- |
| `select()` | `exceptfds` | Дескриптор помічається як готовий у третьому масиві `exceptfds`. |
| `poll()` | `POLLPRI` | Вказує на наявність термінових даних (`Urgent data available`). |
| `epoll()` | `EPOLLPRI` | Генерує подію високого пріоритету в `epoll_wait()`. |
| `epoll()` | `EPOLLRDBAND` | Вказує на наявність пріоритетної смуги читання (Out-of-band data). |

---

## 7. Конфігурація ядра через procfs та sysctl

Глобальна поведінка інтерпретації покажчика терміновості контролюється параметром ядра `net.ipv4.tcp_stdurg`.

```
Файл у системі procfs: /proc/sys/net/ipv4/tcp_stdurg
Синтаксис sysctl: net.ipv4.tcp_stdurg = 0 | 1
```

### 7.1. Порівняльна таблиця режимів tcp_stdurg

| Значення `tcp_stdurg` | Специфікація | Математична формула Urg Pointer | Практичне застосування |
| :--- | :--- | :--- | :--- |
| `0` (за замовчуванням) | **BSD-Style** | `Urg_Seq = Seg_Seq + Urg_Ptr` | Забезпечує сумісність із BSD UNIX, Windows Winsock та більшістю застарілих мережевих утиліт. |
| `1` | **RFC 1122 Strict** | `Urg_Seq = Seg_Seq + Urg_Ptr - 1` | Строга відповідність офіційним стандартам IETF RFC 793 та RFC 1122. |

---

## 8. Структура tcp_sock у коді ядра Linux

Для повноти розуміння нижче наведено витяг із заголовного файла ядра `include/net/tcp.h`, який описує поля сокета, відповідальні за термінові дані:

```c
struct tcp_sock {
    /* ... */
    u32    urg_seq;     /* Sequence number of urgent data byte */
    u32    copied_seq;  /* Head of sequence space to be read by user */
    u16    urg_data;    /* High byte: flags (TCP_URG_VALID), Low byte: data */
    u8     urg_mode;    /* Urgent mode flag: 1 if urgent pointer active */
    /* ... */
};
```

Ці поля підтримуються внутрішньою становою машиною ядра і гарантують атомарне оновлення термінових даних при проходженні мережевих пакетів через підсистему TCP.
