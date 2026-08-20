# 📋 Опції сокета та системні параметри TCP Keep-Alive

Механізм підтримки активності на рівні TCP (англ. *TCP Keep-Alive*) реалізований безпосередньо в мережевому стеку ядра операційної системи. Його завдання — періодично надсилати спеціальні зондувальні пакети через відкритий сокет за відсутності корисного трафіку, щоб своєчасно виявляти аварійно зупинені вузли, розірвані фізичні лінії зв'язку або скинуті записи в динамічних таблицях трансляції адрес (NAT) і мережевих екранах.

Конфігурація механізму складається з двох взаємопов'язаних шарів: глобальних системних замовчувань ядра операційної системи та індивідуальних опцій для конкретного файлового дескриптора сокета.

## Протокольний механізм зондування TCP

Зонд Keep-Alive — це стандартний TCP-сегмент без корисного навантаження (або з одним фіктивним нульовим байтом-заповнювачем для сумісності зі старими реалізаціями), який навмисно порушує поточний стан нумерації байтів.

Стек ядра формує зонд із номером послідовності на одиницю меншим за поточний очікуваний номер непідтвердженого байта:

```
seq = SND.UNA - 1
```

Оскільки віддалений вузол уже успішно прийняв і підтвердив цей байт раніше, надходження такого сегмента класифікується специфікацією RFC 1122 як дублікат. Стек TCP протилежної сторони зобов'язаний негайно згенерувати у відповідь порожній сегмент `ACK` із зазначенням актуального очікуваного номера:

```
ack = SND.UNA
```

Отримавши такий `ACK`, локальне ядро переконується, що протилежний стек живий, скидає внутрішній таймер простою та повертає з'єднання у стан очікування наступного періоду бездіяльності. Якщо ж віддалений вузол знеструмлено або маршрут обірвано, відповідь не надходить, і локальний стек ініціює серію повторних зондів.

## Системні параметри ядра (sysctl у Linux)

На рівні операційної системи Linux поведінка за замовчуванням контролюється трьома глобальними параметрами віртуальної файлової системи `/proc/sys/net/ipv4/`. Вони визначають таймінги для будь-якого сокета, на якому увімкнено базовий прапорець `SO_KEEPALIVE`:

| Змінна sysctl | Замовчування Linux | Призначення та одиниці виміру |
|:---|:---:|:---|
| `net.ipv4.tcp_keepalive_time` | `7200` с (2 години) | Час повної бездіяльності в секундах до надсилання першого зонда |
| `net.ipv4.tcp_keepalive_intvl` | `75` с | Інтервал між повторними зондами за відсутності підтвердження |
| `net.ipv4.tcp_keepalive_probes` | `9` спроб | Кількість поспіль втрачених зондів до примусового закриття сокета |

За стандартних значень ядро виявить зникнення віддаленого вузла лише через:

```
7200 + (75 · 9) = 7875 секунд ≈ 2 години 11 хвилин 15 секунд
```

Для більшості прикладних систем (мікросервіси, бази даних, клієнти черг повідомлень) дві години очікування мертвого сокета є неприпустимими: за цей час вичерпуються пули потоків і блокуються ресурси. Зміна глобальних параметрів через `sysctl -w` небажана, оскільки вона впливає на всі процеси в системі (включно з фоновими демонами). Тому прикладний код конфігурує ці значення індивідуально для кожного сокета через виклик `setsockopt`.

## Опції сокета рівня SOL_SOCKET та IPPROTO_TCP

Керування підтримкою активності окремого сокета виконується через такі опції:

| Константа опції | Рівень (level) | Тип значення | Опис та семантика |
|:---|:---:|:---:|:---|
| `SO_KEEPALIVE` | `SOL_SOCKET` | `int` (0 або 1) | Вмикає або вимикає генерацію зондів на рівні транспортного протоколу |
| `TCP_KEEPIDLE` | `IPPROTO_TCP` | `int` (секунди) | Час спокою з'єднання до надсилання першого зонда (Linux-специфічна назва) |
| `TCP_KEEPALIVE` | `IPPROTO_TCP` | `int` (секунди) | Аналог `TCP_KEEPIDLE` у стеках BSD та macOS |
| `TCP_KEEPINTVL` | `IPPROTO_TCP` | `int` (секунди) | Інтервал між повторними зондами Keep-Alive |
| `TCP_KEEPCNT` | `IPPROTO_TCP` | `int` (кількість) | Максимальна кількість спроб до визнання з'єднання мертвим |
| `TCP_USER_TIMEOUT` | `IPPROTO_TCP` | `unsigned int` (мс) | Максимальний час, протягом якого передані дані або зонди можуть залишатися непідтвердженими |

### Взаємодія TCP_USER_TIMEOUT та лічильників зондів

Опція `TCP_USER_TIMEOUT` (RFC 5482, впроваджена в Linux 2.6.37) задає абсолютний ліміт очікування підтвердження у мілісекундах. Вона уніфікує поведінку таймера ретрансмісії даних (RTO) та таймера зондів Keep-Alive:

- Якщо `TCP_USER_TIMEOUT` встановлено в ненульове значення, воно має абсолютний пріоритет над формулою `TCP_KEEPINTVL · TCP_KEEPCNT`.
- Якщо надісланий зонд Keep-Alive або повторно переданий пакет даних не отримує підтвердження протягом заданого ліміту мілісекунд, ядро негайно переводить сокет у стан помилки `ETIMEDOUT`, навіть якщо лічильник спроб `TCP_KEEPCNT` ще не вичерпано.
- Це усуває проблему розбіжності експоненційного відкату RTO (англ. *Exponential Backoff*) під час передачі реальних даних і лінійних інтервалів зондування у стані простою.

## Кросплатформний програмний інтерфейс

Налаштування параметрів слід виконувати одразу після створення дескриптора сокета або отримання його з виклику `accept()`.

:::tabs
```c
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

int configure_tcp_keepalive(int fd, int idle_sec, int interval_sec, int count, unsigned int user_timeout_ms) {
    int enable = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &enable, sizeof(enable)) < 0) {
        perror("setsockopt(SO_KEEPALIVE)");
        return -1;
    }

#ifdef __linux__
    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &idle_sec, sizeof(idle_sec)) < 0) {
        perror("setsockopt(TCP_KEEPIDLE)");
        return -1;
    }
#elif defined(__APPLE__) || defined(__FreeBSD__) || defined(__NetBSD__) || defined(__OpenBSD__)
    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPALIVE, &idle_sec, sizeof(idle_sec)) < 0) {
        perror("setsockopt(TCP_KEEPALIVE)");
        return -1;
    }
#endif

    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPINTVL, &interval_sec, sizeof(interval_sec)) < 0) {
        perror("setsockopt(TCP_KEEPINTVL)");
        return -1;
    }

    if (setsockopt(fd, IPPROTO_TCP, TCP_KEEPCNT, &count, sizeof(count)) < 0) {
        perror("setsockopt(TCP_KEEPCNT)");
        return -1;
    }

#ifdef TCP_USER_TIMEOUT
    if (user_timeout_ms > 0) {
        if (setsockopt(fd, IPPROTO_TCP, TCP_USER_TIMEOUT, &user_timeout_ms, sizeof(user_timeout_ms)) < 0) {
            perror("setsockopt(TCP_USER_TIMEOUT)");
            return -1;
        }
    }
#endif

    return 0;
}
```
```cpp
#include <system_error>
#include <chrono>
#include <cstring>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

struct KeepAliveOptions {
    std::chrono::seconds idleTime{30};
    std::chrono::seconds probeInterval{5};
    int probeCount{3};
    std::chrono::milliseconds userTimeout{18000};
};

class SocketOptionTuner {
public:
    static std::error_code applyKeepAlive(int fd, const KeepAliveOptions& opts) noexcept {
        int enable = 1;
        if (::setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &enable, sizeof(enable)) < 0) {
            return std::error_code(errno, std::generic_category());
        }

        int idle = static_cast<int>(opts.idleTime.count());
#ifdef __linux__
        if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &idle, sizeof(idle)) < 0) {
            return std::error_code(errno, std::generic_category());
        }
#elif defined(__APPLE__) || defined(__FreeBSD__) || defined(__NetBSD__) || defined(__OpenBSD__)
        if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPALIVE, &idle, sizeof(idle)) < 0) {
            return std::error_code(errno, std::generic_category());
        }
#endif

        int intvl = static_cast<int>(opts.probeInterval.count());
        if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPINTVL, &intvl, sizeof(intvl)) < 0) {
            return std::error_code(errno, std::generic_category());
        }

        int cnt = opts.probeCount;
        if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPCNT, &cnt, sizeof(cnt)) < 0) {
            return std::error_code(errno, std::generic_category());
        }

#ifdef TCP_USER_TIMEOUT
        auto utMs = static_cast<unsigned int>(opts.userTimeout.count());
        if (utMs > 0) {
            if (::setsockopt(fd, IPPROTO_TCP, TCP_USER_TIMEOUT, &utMs, sizeof(utMs)) < 0) {
                return std::error_code(errno, std::generic_category());
            }
        }
#endif

        return {};
    }
};
```
:::

## Особливості реалізації у Windows Sockets (Winsock)

В операційних системах сімейства Windows механізм TCP Keep-Alive налаштовується інакше, ніж у POSIX-системах. Замість окремих констант `IPPROTO_TCP` використовується керівний код введення-виведення `WSAIoctl` із кодом операції `SIO_KEEPALIVE_VALS` та спеціальною структурою `tcp_keepalive`:

:::tabs
```c
struct tcp_keepalive {
    u_long onoff;             // 1 = увімкнено, 0 = вимкнено
    u_long keepalivetime;     // Час бездіяльності в мілісекундах (аналог TCP_KEEPIDLE)
    u_long keepaliveinterval; // Інтервал між повторними зондами в мілісекундах
};
```
```cpp
struct tcp_keepalive {
    u_long onoff;             // 1 = увімкнено, 0 = вимкнено
    u_long keepalivetime;     // Час бездіяльності в мілісекундах (аналог TCP_KEEPIDLE)
    u_long keepaliveinterval; // Інтервал між повторними зондами в мілісекундах
};
```
:::

Головна відмінність Windows полягає в тому, що кількість спроб (`TCP_KEEPCNT`) жорстко зафіксована на рівні 10 у системному драйвері `tcpip.sys` і до Windows 10 версії 1709 не підлягала модифікації з простору користувача. Починаючи з нових версій Windows, Microsoft додала підтримку `TCP_KEEPIDLE`, `TCP_KEEPINTVL` та `TCP_KEEPCNT` через стандартний `setsockopt`.

## Діагностика та спостереження за станом таймерів сокета

Перевірити активність і залишок часу таймерів Keep-Alive для конкретного сокета можна без зупинки процесу за допомогою системної утиліти `ss` (Socket Statistics) у Linux:

```text
$ ss -tioen '( dport = :5432 )'
ESTAB  0  0  10.0.0.2:48122  10.0.0.5:5432
     timer:(keepalive,28sec,0) ino:184920 sk:5c <->
     skmem:(r0,rb131072,t0,tb16384,f0,w0,o0,bl0,d0)
```

Поле `timer:(keepalive,28sec,0)` містить ключову діагностичну інформацію:
- `keepalive` — тип активного таймера ядра (на відміну від `on` для таймера повторної передачі даних RTO або `timewait`).
- `28sec` — час у секундах, що залишився до відправлення наступного зонда.
- `0` — кількість уже надісланих непідтверджених зондів (лічильник невдалих спроб). Коли це число досягає `TCP_KEEPCNT`, сокет закривається.

У віртуальній файловій системі ядра інформація про таймери сокетів доступна у файлі `/proc/net/tcp`. Колонка `tr` (timer active) позначає тип активного таймера:
- `00` — таймер не активний;
- `01` — таймер повторної передачі (RTO / on);
- `02` — таймер підтримки активності (Keep-Alive);
- `03` — таймер стану `TIME_WAIT`.

Для низькорівневого перехоплення та перегляду самих зондів утилітою `tcpdump` використовують фільтр за нульовим розміром корисного навантаження та наявністю прапорця ACK:

```text
$ tcpdump -nnvv -i eth0 'tcp[tcpflags] & tcp-ack != 0 and ip[2:2] <= 41'
```

У виводі дампа зонд відображається як пакет із довжиною корисного навантаження 0 або 1 байт і номером послідовності, що повторює попередній сегмент:

```text
14:20:01.104210 IP 10.0.0.2.48122 > 10.0.0.5.5432: Flags [.], seq 214981:214981, ack 48192, win 502, length 0
14:20:01.104520 IP 10.0.0.5.5432 > 10.0.0.2.48122: Flags [.], ack 214982, win 501, length 0
```

## Динамічне налаштування через eBPF (sockops)

У сучасних хмарних інфраструктурах на базі ядра Linux версій 4.18+ конфігурацію Keep-Alive дедалі частіше виконують без внесення змін у вихідний код прикладних програм. За допомогою технології eBPF (Extended Berkeley Packet Filter) програма типу `BPF_PROG_TYPE_SOCK_OPS` прикріплюється до cgroup контейнера й автоматично перехоплює події життєвого циклу сокетів `BPF_SOCK_OPS_PASSIVE_ESTABLISHED_CB` та `BPF_SOCK_OPS_ACTIVE_ESTABLISHED_CB`.

У момент переходу сокета в стан `ESTABLISHED` програма eBPF викликає функцію помічника `bpf_setsockopt()`, самостійно виставляючи прапорець `SO_KEEPALIVE` та оптимізовані значення `TCP_KEEPIDLE` відповідно до топології поточної мережі.

## Помилки та крайові випадки

1. **Спадкування налаштувань у виклику `accept()`:** сокети, що повертаються з `accept()`, автоматично успадковують значення прапорця `SO_KEEPALIVE` та пов'язані опції від слухаючого сокета (`listen socket`). Проте на деяких версіях Unix (зокрема Solaris та старих BSD) опції `TCP_KEEPIDLE` потребували повторного явного виставлення на прийнятому клієнтському сокеті.
2. **Асиметрія таймаутів із балансувальниками:** якщо таймаут `TCP_KEEPIDLE` на клієнті перевищує таймаут видалення сесії на проміжному хмарному балансувальнику (наприклад, AWS NLB/ALB із замовчуванням 350 секунд або Azure Load Balancer із 240 секундами), перший зонд прийде на вже видалений запит і викличе неминучий `RST`. Безпечний діапазон для хмарних середовищ становить `TCP_KEEPIDLE = 15..30` секунд.
3. **Надмірне споживання енергії на мобільних пристроях:** надто часті інтервали зондування (менше 5 секунд) не дозволяють радіомодулю смартфона (LTE/5G) перейти в енергоощадний режим сну (DRX), що призводить до швидкого розряджання акумулятора.
