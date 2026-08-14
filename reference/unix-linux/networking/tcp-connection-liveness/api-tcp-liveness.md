# 📋 Довідник опцій сокета та параметрів ядра для виявлення TCP-liveness

У цьому довіднику зведено конфігураційні параметри ядра Linux, опції системного виклику `setsockopt()`, коди помилок та структури даних, які застосовуються для керування таймерами життєздатності (liveness) TCP-з'єднань. Усі налаштування розділено за рівнем впливу: від глобальних системних параметрів `sysctl` до специфічних прапорців сокета на рівні стека `IPPROTO_TCP`.

Довідник призначений для використання під час проектування високонавантажених мережевих демонів, розробки системних сервісів, діагностики мережевих збоїв та налаштування операційної системи Linux для роботи у складі високонавантажених розподілених кластерів.

---

## 1. Системні параметри ядра Linux (`sysctl`)

Глобальні налаштування керують поведінкою за замовчуванням для всіх TCP-сокетів у системному просторі або у відповідному мережевому неймспейсі (`netns`). Значення розміщуються у віртуальній файловій системі `/proc/sys/net/ipv4/` і відповідають за базові інтервали зондування, обмеження повторних спроб та системні таймаути.

### Таблиця глобальних параметрів sysctl

| Параметр sysctl | Значення за замовчуванням | Описовий тип | Призначення та механіка |
| :--- | :--- | :--- | :--- |
| `net.ipv4.tcp_keepalive_time` | `7200` (секунди) | Ціле число | Час суцільного простою з'єднання у стані `ESTABLISHED` (без передачі та прийому даних) перед надсиланням першого keepalive-зонда. |
| `net.ipv4.tcp_keepalive_intvl` | `75` (секунди) | Ціле число | Інтервал між повторними keepalive-зондами, якщо на попередній зонд не було отримано підтвердження (ACK). |
| `net.ipv4.tcp_keepalive_probes` | `9` (кількість) | Ціле число | Максимальна кількість непідтверджених keepalive-зондів перед тим, як ядро вважатиме з'єднання мертвим і знищить сокет з помилкою `ETIMEDOUT`. |
| `net.ipv4.tcp_retries2` | `15` (кількість) | Ціле число | Максимальна кількість повторних спроб відправки звичайних непідтверджених даних у стані RTO backoff перед розривом з'єднання (за замовчуванням займає від 13 до 30 хвилин). |
| `net.ipv4.tcp_retries1` | `3` (кількість) | Ціле число | Поріг спроб повторної передачі, після якого ядро розпочинає перевірку мережевого маршруту (IP route lookup / ARP refresh) для виявлення змін у топології. |
| `net.ipv4.tcp_orphan_retries` | `0` (кількість) | Ціле число | Кількість спроб повторної передачі для "сирітських" сокетів (відкритих ядерних сокетів, закріплених за закритими файловими дескрипторами у Userspace). Значення `0` відповідає 8 спробам. |
| `net.ipv4.tcp_syn_retries` | `6` (кількість) | Ціле число | Кількість спроб повторної відправки пакетів SYN при встановленні вихідного з'єднання через виклик `connect()`. |
| `net.ipv4.tcp_synack_retries` | `5` (кількість) | Ціле число | Кількість спроб повторної відправки пакетів SYN-ACK пасивним сервером під час трикрокового рукопожимання TCP. |
| `net.ipv4.tcp_fin_timeout` | `60` (секунди) | Ціле число | Час утримання сокета у стані `FIN_WAIT_2` після закриття локальною стороною перед примусовим знищенням, якщо віддалений вузол не припиняє передачу. |
| `net.ipv4.tcp_slow_start_after_idle` | `1` (прапорець) | Логічне | Якщо прапорець активовано (1), ядро скидає вікно перевантаження (Congestion Window, `cwnd`) до початкового значення у разі тривалого простою сокета. |

### Детальний опис механіки sysctl

Кожен з указаних параметрів ядра відіграє роль у глобальному циклі обслуговування TCP-з'єднань. Параметр `net.ipv4.tcp_keepalive_time` визначає "вік мовчання", після якого ядро ініціює фонову перевірку. Якщо системний адміністратор встановлює це значення рівним `300`, це означає, що будь-яке неактивне TCP-з'єднання в системі почне надсилати перший зонд через 5 хвилин простою.

Параметр `net.ipv4.tcp_retries2` контролює алгоритм повторних спроб передачі для пакетів, що містять дані. При кожній невдалій спробі ядро підвоює час очікування RTO (наприклад, 200мс, 400мс, 800мс, 1600мс... до максимального значення `TCP_RTO_MAX`, яке за замовчуванням становить 120 секунд). Значення 15 означає, що ядро зробить 15 спроб, сумарна тривалість яких становить близько 20–30 хвилин залежно від початкового значення RTT.

### Читання та зміна глобальних параметрів

Динамічне читання та зміна параметрів виконується через утиліту `sysctl` або безпосередньо через інтерфейс `/proc`. Зміни, внесені через `sysctl -w`, застосовуються негайно до всіх нових та існуючих сокетів, які не мають індивідуальних перевизначень через `setsockopt()`.

```bash
# Перегляд поточних параметрів Keepalive у системі
sysctl net.ipv4.tcp_keepalive_time net.ipv4.tcp_keepalive_intvl net.ipv4.tcp_keepalive_probes

# Динамічна зміна параметрів у запущеній системі для прискореного виявлення (наприклад, для серверів баз даних)
sudo sysctl -w net.ipv4.tcp_keepalive_time=300
sudo sysctl -w net.ipv4.tcp_keepalive_intvl=15
sudo sysctl -w net.ipv4.tcp_keepalive_probes=5
```

Персистентне збереження здійснюється шляхом додавання відповідних конфігураційних рядків до файлу `/etc/sysctl.conf` або окремого файлу в каталозі `/etc/sysctl.d/99-tcp-liveness.conf`.

---

## 2. Опції сокетів (`setsockopt` / `getsockopt`)

Конфігурація на рівні окремого файлового дескриптора сокета має абсолютний пріоритет над системними налаштуваннями `sysctl`. Зміна здійснюється за допомогою системних викликів `setsockopt()` та `getsockopt()`, що дозволяє налаштовувати різну мережеву політику для різних сокетів у межах одного й того самого процесу (наприклад, тримати короткі таймаути для сервісних RPC-викликів та довгі для завантаження великих файлів).

### Сигнатура системних викликів

:::tabs
```c
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

int setsockopt(int sockfd, int level, int optname, const void *optval, socklen_t optlen);
int getsockopt(int sockfd, int level, int optname, void *optval, socklen_t *optlen);
```
```cpp
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

// У системній бібліотеці C++ використовуються ті самі POSIX-сигнатури C-API:
extern "C" {
    int setsockopt(int sockfd, int level, int optname, const void *optval, socklen_t optlen);
    int getsockopt(int sockfd, int level, int optname, void *optval, socklen_t *optlen);
}
```
:::

### Специфікація прапорців та опцій

#### `SO_KEEPALIVE`
- **Рівень (`level`)**: `SOL_SOCKET`
- **Тип аргументу (`optval`)**: `int` (0 — вимкнено, 1 — увімкнено)
- **Опис**: Вмикає або вимикає генерацію періодичних зондувальних пакетів для сокета у стані `TCP_ESTABLISHED`. Якщо опція вимкнена, ядро Linux не надсилатиме жодних зондів у період простою з'єднання.

#### `TCP_KEEPIDLE` (у POSIX/BSD еквівалент `TCP_KEEPALIVE`)
- **Рівень (`level`)**: `IPPROTO_TCP`
- **Тип аргументу (`optval`)**: `int` (секунди)
- **Опис**: Індивідуальний таймаут простою перед надсиланням першого зонда для даного сокета. Перекриває глобальне системне значення `net.ipv4.tcp_keepalive_time`.

#### `TCP_KEEPINTVL`
- **Рівень (`level`)**: `IPPROTO_TCP`
- **Тип аргументу (`optval`)**: `int` (секунди)
- **Опис**: Індивідуальний інтервал між зондами для даного сокета при відсутності відповіді. Перекриває глобальне системне значення `net.ipv4.tcp_keepalive_intvl`.

#### `TCP_KEEPCNT`
- **Рівень (`level`)**: `IPPROTO_TCP`
- **Тип аргументу (`optval`)**: `int` (кількість спроб)
- **Опис**: Індивідуальна лімітована кількість непідтверджених зондів для даного сокета. Перекриває глобальне системне значення `net.ipv4.tcp_keepalive_probes`.

#### `TCP_USER_TIMEOUT` (стандарт RFC 5482)
- **Рівень (`level`)**: `IPPROTO_TCP`
- **Тип аргументу (`optval`)**: `unsigned int` (мілісекунди!)
- **Опис**: Встановлює максимальний інтервал часу, протягом якого надіслані дані або зонди можуть залишатися без підтвердження ACK. Якщо час перевищує вказаний таймаут, сокет примусово закривається з помилкою `ETIMEDOUT`. Значення `0` повертає використання стандартного експоненційного алгоритму `tcp_retries2`.

#### `SO_LINGER`
- **Рівень (`level`)**: `SOL_SOCKET`
- **Тип аргументу (`optval`)**: `struct linger { int l_onoff; int l_linger; }`
- **Опис**: Керує поведінкою системного виклику `close()`. Якщо `l_onoff = 1` та `l_linger = 0`, при закритті сокета ядро негайно примусово надсилає пакет TCP RST (Reset), анулюючи непідтверджені дані у буферах та обминаючи стадію `TIME_WAIT`.

#### `SO_RCVTIMEO` та `SO_SNDTIMEO`
- **Рівень (`level`)**: `SOL_SOCKET`
- **Тип аргументу (`optval`)**: `struct timeval { time_t tv_sec; suseconds_t tv_usec; }`
- **Опис**: Встановлюють максимальний час очікування для блокуючих системних викликів `read()`/`recv()` та `write()`/`send()`. Якщо операція введення-виведення блокується довше за вказаний інтервал, виклик переривається з помилкою `EAGAIN` або `EWOULDBLOCK`.

---

## 3. Приклади конфігурації сокета в C та C++

У цьому розділі наведено ідіоматичні приклади встановлення параметрів TCP Keepalive та `TCP_USER_TIMEOUT` для мережевого сокета. У прикладі мовою C++ застосовано механізм RAII, `std::chrono` та обробку помилок через системні винятки `std::system_error`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

int configure_tcp_liveness(int fd, int idle_sec, int intvl_sec, int cnt, unsigned int user_timeout_ms) {
    int enable = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &enable, sizeof(enable)) < 0) {
        perror("setsockopt(SO_KEEPALIVE)");
        return -1;
    }

    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &idle_sec, sizeof(idle_sec)) < 0) {
        perror("setsockopt(TCP_KEEPIDLE)");
        return -1;
    }

    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPINTVL, &intvl_sec, sizeof(intvl_sec)) < 0) {
        perror("setsockopt(TCP_KEEPINTVL)");
        return -1;
    }

    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPCNT, &cnt, sizeof(cnt)) < 0) {
        perror("setsockopt(TCP_KEEPCNT)");
        return -1;
    }

    if (user_timeout_ms > 0) {
        if (setsockopt(fd, IPPROTO_TCP, TCP_USER_TIMEOUT, &user_timeout_ms, sizeof(user_timeout_ms)) < 0) {
            perror("setsockopt(TCP_USER_TIMEOUT)");
            return -1;
        }
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <system_error>
#include <chrono>
#include <cerrno>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

class SocketLivenessConfigurator {
public:
    struct Options {
        std::chrono::seconds idle_time{60};
        std::chrono::seconds probe_interval{10};
        int probe_count{5};
        std::chrono::milliseconds user_timeout{15000};
    };

    static void apply(int fd, const Options& opts) {
        const int enable = 1;
        if (::setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &enable, sizeof(enable)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to set SO_KEEPALIVE");
        }

        const int idle_sec = static_cast<int>(opts.idle_time.count());
        if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &idle_sec, sizeof(idle_sec)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to set TCP_KEEPIDLE");
        }

        const int intvl_sec = static_cast<int>(opts.probe_interval.count());
        if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPINTVL, &intvl_sec, sizeof(intvl_sec)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to set TCP_KEEPINTVL");
        }

        if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPCNT, &opts.probe_count, sizeof(opts.probe_count)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to set TCP_KEEPCNT");
        }

        if (opts.user_timeout.count() > 0) {
            const auto timeout_ms = static_cast<unsigned int>(opts.user_timeout.count());
            if (::setsockopt(fd, IPPROTO_TCP, TCP_USER_TIMEOUT, &timeout_ms, sizeof(timeout_ms)) < 0) {
                throw std::system_error(errno, std::generic_category(), "Failed to set TCP_USER_TIMEOUT");
            }
        }
    }
};
```
:::

---

## 4. Коди помилок системних викликів при втраті liveness

Коли ядро Linux ухвалює рішення про закриття TCP-з'єднання внаслідок вичерпання спроб Keepalive або перевищення `TCP_USER_TIMEOUT`, будь-які подальші спроби читання чи запису повертають помилку через системну змінну `errno`. Програма має правильно інтерпретувати ці коди для своєчасного закриття файлового дескриптора та очищення контексту сесії.

### Деталізація системних кодів помилок

| Код помилки (`errno`) | Назва текстової константи | Сценарій виникнення | Рекомендована дія застосунку |
| :--- | :--- | :--- | :--- |
| `110` | `ETIMEDOUT` | Вичерпано всі keepalive-зонди або перевищено `TCP_USER_TIMEOUT` під час очікування ACK. | Закрити сокет (`close()`), звільнити ресурси та ініціювати reconnect. |
| `104` | `ECONNRESET` | Віддалена сторона (або проміжний фаєрвол/NAT) надіслала пакет з прапорцем TCP RST у відповідь на зонд чи дані. | Закрити сокет, зкинути стан сесії. |
| `32` | `EPIPE` | Застосунок намагається виконати `write()` у сокет, для якого вже було отримано FIN або RST (генерує сигнал `SIGPIPE`). | Перехоплювати `SIGPIPE` або використовувати `MSG_NOSIGNAL`, закрити сокет. |
| `113` | `EHOSTUNREACH` | Проміжний маршрутизатор повернув ICMP Destination Unreachable під час передачі зонду або даних. | Закрити сокет, перевірити мережевий маршрут та DNS. |
| `101` | `ENETUNREACH` | Локальна система не має дійсного маршруту до мережі призначення (наприклад, вимкнено інтерфейс). | Записати помилку у журнал, чекати відновлення мережевого інтерфейсу. |
| `107` | `ENOTCONN` | Спроба виконання операції читання/запису на сокеті, який ще не з'єднано або вже закрито в ядрі. | Закрити дескриптор. |
| `11` / `85` | `EAGAIN` / `EWOULDBLOCK` | Неблокуючий сокет не має даних для читання або буфер запису заповнений. | Чекати події від `epoll`/`select`. |

---

## 5. Діагностичні параметри та структури ядра

При налагодженні мережевих проблем розробнику необхідно перевіряти стан внутрішніх таймерів ядра для конкретного сокета. В операційній системі Linux для цього доступні два інструменти: структури системних викликів та текстовий консольний інструментарій.

### Структура `struct tcp_info`

Отримати точний стан внутрішніх таймерів TCP для конкретного сокета можна за допомогою `getsockopt` з опцією `TCP_INFO`. Ця структура повертає внутрішні лічильники та метрики ядра:

:::tabs
```c
#include <sys/socket.h>
#include <netinet/tcp.h>

struct tcp_info info;
socklen_t len = sizeof(info);
if (getsockopt(sockfd, IPPROTO_TCP, TCP_INFO, &info, &len) == 0) {
    /* info.tcpi_state — поточний стан TCP (напр. TCP_ESTABLISHED) */
    /* info.tcpi_rto — поточний очікуваний таймаут повтору (RTO) у мікросекундах */
    /* info.tcpi_unacked — кількість непідтверджених пакетів у мережі */
    /* info.tcpi_probes — кількість вже надісланих зондувальних пакетів */
    /* info.tcpi_backoff — поточний ступінь експоненційного відступу RTO */
    /* info.tcpi_retransmits — кількість виконаних повторних передач */
}
```
```cpp
#include <sys/socket.h>
#include <netinet/tcp.h>
#include <optional>

std::optional<::tcp_info> fetch_tcp_info(int sockfd) {
    ::tcp_info info{};
    ::socklen_t len = sizeof(info);
    if (::getsockopt(sockfd, IPPROTO_TCP, TCP_INFO, &info, &len) == 0) {
        return info;
    }
    return std::nullopt;
}
```
:::

### Поля структури `struct tcp_info`, пов'язані з liveness

- `tcpi_state`: внутрішній стан TCP-автомата (1 = `TCP_ESTABLISHED`, 7 = `TCP_CLOSE`).
- `tcpi_probes`: кількість надісланих keepalive-зондів або zero-window зондів, на які ще не отримано відповіді.
- `tcpi_backoff`: поточна експонента RTO (кількість подвоєнь інтервалу повторної передачі).
- `tcpi_rto`: поточний розрахований час повторної передачі (Retransmission Timeout) у мікросекундах.
- `tcpi_unacked`: кількість пакетів, надісланих у мережу, але ще не підтверджених пакетами ACK.
- `tcpi_sacked`: кількість пакетів, підтверджених через механізм Selective ACK (SACK).
- `tcpi_lost`: кількість пакетів, які ядро вважає втраченими у мережі.
- `tcpi_retrans`: кількість пакетів, які зараз перебувають у процесі повторного надсилання.

### Формат таймерів у консольній утиліти `ss`

При виклику утиліти `ss -t -i` або `ss -t -o` ядро повертає текстове представлення таймерів сокета:

```text
State       Recv-Q Send-Q Local Address:Port  Peer Address:Port  Process
ESTAB       0      0      192.168.1.10:45234 192.168.1.20:8080   users:(("app",pid=1234,fd=4))
	 timer:(keepalive,48min,0) rto:200 rtt:0.15/0.04 ato:40 mss:1460 rcvspace:14600 ssthresh:10
```

- **`timer:(keepalive,48min,0)`**: означає, що для сокета активовано таймер keepalive, і наступний зонд буде надіслано через 48 хвилин.
- **`timer:(persist,...)`**: активовано таймер зондування вікна (Zero Window Probe), коли віддалена сторона повідомила про нульовий розмір вікна прийому.
- **`timer:(retrans,...)`**: активовано таймер повторного надсилання непідтверджених даних (RTO retransmit).

### Інспектування через `/proc/net/tcp`

Віртуальний файл `/proc/net/tcp` містить низькорівневу таблицю всіх існуючих IPv4 TCP-сокетів системи. Кожен рядок представляє один сокет і містить стовпчик `tr:tm->when`:

```text
  sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode
   0: 0100007F:0050 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 12345
   1: 0A0110C0:B032 140110C0:0050 01 00000000:00000000 02:00005B30 00000000  1000        0 67890
```

У стовпчику `tr` (Timer State) число вказує на тип активного таймера:
- `00` — таймер не запущено.
- `01` — активовано таймер повторної передачі (Retransmit Timer).
- `02` — активовано таймер Keepalive.
- `03` — активовано таймер TIME_WAIT.

Таблиця станів TCP у `/proc/net/tcp` кодується шістнадцятковими числами: `01` = `TCP_ESTABLISHED`, `02` = `TCP_SYN_SENT`, `03` = `TCP_SYN_RECV`, `04` = `TCP_FIN_WAIT1`, `05` = `TCP_FIN_WAIT2`, `06` = `TCP_TIME_WAIT`, `07` = `TCP_CLOSE`, `08` = `TCP_CLOSE_WAIT`, `09` = `TCP_LAST_ACK`, `0A` = `TCP_LISTEN`, `0B` = `TCP_CLOSING`.

Знання цих числових кодів дозволяє системним інженерам писати швидкі скріпти діагностики стану мережевих сокетів без використання сторонніх утиліт.
