# 📋 Довідник `setsockopt`: рівні, типи, замовчування, переносність

Тут зібрано те, що доводиться згадувати щоразу, коли пишеш рядок із `setsockopt`: на якому рівні живе опція, якого типу її аргумент, що стоїть за замовчуванням, до якого виклику її ще має сенс ставити, що поверне `getsockopt` — і чим усе це відрізняється в Linux, BSD, Windows та lwIP. Таблиці нижче варто читати вибірково: знайшов рядок — подивився примітку під таблицею, де пояснено, чому саме так.

## Підпис і контракт виклику

```c
#include <sys/socket.h>

int setsockopt(int fd, int level, int optname,
               const void *optval, socklen_t optlen);

int getsockopt(int fd, int level, int optname,
                     void *optval, socklen_t *optlen);

/* обидва: 0 — успіх; -1 — помилка, причина в errno */
```

| Частина виклику | Що про неї треба знати |
| --- | --- |
| `level` | Адреса шару, а не категорія: `SOL_SOCKET` — сам об'єкт сокета, `IPPROTO_TCP` — машина TCP, `IPPROTO_IP` / `IPPROTO_IPV6` — заголовок пакета. Числові значення імен унікальні лише в межах рівня, тож `IP_TTL` із рівнем `SOL_SOCKET` дасть `ENOPROTOOPT` або зовсім іншу опцію. |
| `optval` | Нетипізований покажчик: компілятор нічого не перевірить. Булеві опції беруть **`int`**, не `char` і не `bool`. |
| `optlen` у `setsockopt` | Вхідний. Ядро читає рівно стільки байтів, скільки ти сказав. |
| `optlen` у `getsockopt` | «Вхід-вихід»: перед викликом — розмір твого буфера, після — скільки байтів ядро записало. Неініціалізований `optlen` — типова причина `EINVAL` чи `EFAULT`. |
| результат | `0` не означає «стало як просив»: ядро вільне округлити, подвоїти або обрізати значення стелею. |

Звідси мінімальний робочий шаблон: поставити й **прочитати назад**.

```c
#include <sys/socket.h>
#include <netinet/tcp.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>

/* поставити цілочислену опцію й показати, що ядро справді взяло */
static int set_int_opt(int fd, int level, int name, int want, const char *label)
{
    if (setsockopt(fd, level, name, &want, sizeof want) < 0) {
        fprintf(stderr, "%s: setsockopt: %s\n", label, strerror(errno));
        return -1;
    }
    int got = 0;
    socklen_t len = sizeof got;
    if (getsockopt(fd, level, name, &got, &len) == 0 && got != want)
        fprintf(stderr, "%s: просив %d, ядро дало %d\n", label, want, got);
    return 0;
}

/* виклик */
set_int_opt(fd, IPPROTO_TCP, TCP_NODELAY, 1,      "TCP_NODELAY");
set_int_opt(fd, SOL_SOCKET,  SO_RCVBUF,   262144, "SO_RCVBUF");
```

Другий рядок надрукує розбіжність завжди: Linux подвоює прохане під службовий облік. Це не збій, а документована поведінка — саме подвоєне число потім і повертає `getsockopt`.

## Коли ставити: вікна життєвого циклу

Крайній момент — це не стиль, а мить, коли рішення вже ухвалене: після `bind` нема з ким сперечатися за адресу, після рукостискання — за коефіцієнт масштабування вікна.

| Група опцій | Крайній момент | Що станеться пізніше |
| --- | --- | --- |
| `SO_REUSEADDR`, `SO_REUSEPORT`, `SO_EXCLUSIVEADDRUSE` | до `bind` | `bind` уже перевірив зайнятість адреси — опція просто нічого не змінить |
| `SO_RCVBUF`, `SO_SNDBUF` на TCP | до `connect` або `listen` | коефіцієнт масштабування вікна сторони узгоджують у SYN; число зміниться, стеля вікна — ні |
| усе, що має успадкувати `accept` | до `listen` (на слухаючому сокеті) | нові сокети народжуються з поточних налаштувань слухача; успадковується не все, тож перевіряй на своїй системі |
| `IP_ADD_MEMBERSHIP` | **після** `bind` | групу приєднують до вже відомої локальної адреси й порту |
| `IP_MULTICAST_IF`, `IP_MULTICAST_TTL`, `IP_MULTICAST_LOOP` | до першого `sendto` | діють на пакети, які підуть далі; вже надіслані не переписуються |
| `SO_LINGER` | до `close` | його читає саме `close` |
| `TCP_NODELAY`, `SO_RCVTIMEO`/`SO_SNDTIMEO`, `IP_TTL`, `TCP_KEEP*`, `TCP_USER_TIMEOUT` | будь-коли | діють з наступної операції |

Порядок викликів, у який ці вікна вкладаються — `socket` → опції → `bind` → `listen`/`connect` → `accept` — розібрано в [API сокетів](topic:programming/sockets-tcp-udp): там же видно, який виклик що фіксує остаточно.

## Рівень `SOL_SOCKET`

| Опція | Тип `optval` | Замовчування в Linux | Ставити до | `getsockopt` повертає |
| --- | --- | --- | --- | --- |
| `SO_RCVBUF` | `int`, байти | для TCP — середнє з `net.ipv4.tcp_rmem` (4 КіБ / 128 КіБ / до 32 МіБ); для решти — `net.core.rmem_default` | `connect`/`listen` | **подвоєне** значення |
| `SO_SNDBUF` | `int`, байти | для TCP — середнє з `net.ipv4.tcp_wmem` (4 КіБ / 16 КіБ / до 4 МіБ); для решти — `net.core.wmem_default` | `connect`/`listen` | **подвоєне** значення |
| `SO_RCVBUFFORCE`, `SO_SNDBUFFORCE` | `int`, байти | — | там само | подвоєне |
| `SO_RCVTIMEO`, `SO_SNDTIMEO` | `struct timeval` | `{0, 0}` — без обмеження | будь-коли | поточний таймаут |
| `SO_REUSEADDR` | `int` (0/1) | 0 | **`bind`** | 0/1 |
| `SO_REUSEPORT` | `int` (0/1) | 0 | **`bind`** | 0/1 |
| `SO_KEEPALIVE` | `int` (0/1) | 0 | будь-коли (на слухачі — до `listen`) | 0/1 |
| `SO_LINGER` | `struct linger` | `{0, 0}` — вимкнено | `close` | структуру |
| `SO_BROADCAST` | `int` (0/1) | 0 | до першого `sendto` на широкомовну адресу | 0/1 |
| `SO_ERROR` | `int` | — | лише читання | код помилки **і очищає його** |
| `SO_RCVLOWAT` | `int`, байти | 1 | будь-коли | значення |
| `SO_TYPE`, `SO_ACCEPTCONN` | `int` | — | лише читання | `SOCK_STREAM`/`SOCK_DGRAM`; 0/1 |

**Мінімуми й стелі.** Ядро не дасть поставити скільки завгодно мало: найменше подвоєне значення — 256 байтів для `SO_RCVBUF` і 2048 для `SO_SNDBUF`. Зверху обмежують `net.core.rmem_max` і `net.core.wmem_max`, і при перевищенні `setsockopt` **не** повертає помилки — просто дає менше. `SO_RCVBUFFORCE`/`SO_SNDBUFFORCE` (з Linux 2.6.14) ці стелі обходять, але вимагають повноваження `CAP_NET_ADMIN`. Окремий наслідок явного `SO_RCVBUF` на TCP: він вимикає автоналаштування приймального буфера (`net.ipv4.tcp_moderate_rcvbuf`, типово ввімкнене), тобто замінює вимір ядра твоїм здогадом. Приймальний буфер тут не просто пам'ять: вільне місце в ньому стек оголошує другій стороні як вікно — [керування потоком](topic:communications/flow-control) саме так і працює, і тому розмір буфера ставить стелю швидкості на довгому шляху.

**Таймаути обмежують виклик, а не операцію.** `SO_RCVTIMEO` вичерпався — `recv` повертає `-1` з `EAGAIN` (він же `EWOULDBLOCK`), тобто поводиться як [неблокуючий сокет](topic:programming/blocking-vs-nonblocking-io), який не має чого віддати. Але якщо частину даних уже забрано, повернеться **кількість байтів**, а не помилка, і наступна ітерація циклу дістане свіжий повний таймаут. Обмежити операцію цілком можна лише власним дедлайном.

**`SO_LINGER` — три різні поведінки `close`.**

| `l_onoff` | `l_linger` | Що робить `close` |
| --- | --- | --- |
| 0 | ігнорується | Повертається одразу; недіслане ядро дошле у фоні, з'єднання закриється нормально (`FIN`). |
| 1 | 0 | Недіслане викидається, друга сторона дістає `RST`, стану `TIME_WAIT` не буде. Спосіб грубо обірвати з'єднання. |
| 1 | N > 0 | Блокується до N секунд, доки все не підтвердять. Не встигло — з'єднання скидають `RST`-ом, а `close` може повернути `-1` з `EWOULDBLOCK`. |

**`SO_ERROR` — єдиний спосіб дізнатися результат неблокуючого `connect`.** Помилка з'єднання приходить асинхронно: сокет просто стає готовим на запис, а причину доводиться питати окремо.

```c
/* poll/epoll повідомив, що fd готовий на запис — чому саме? */
int err = 0;
socklen_t len = sizeof err;
if (getsockopt(fd, SOL_SOCKET, SO_ERROR, &err, &len) < 0)
    err = errno;                     /* сам getsockopt не вдався */

if (err == 0) { /* з'єднання встановлене */ }
else          { /* ECONNREFUSED, ETIMEDOUT, EHOSTUNREACH, ENETUNREACH… */ }
```

Читання **очищає** поле, тож другий виклик поспіль дасть `0`. Частина цих кодів приходить не від самого TCP, а зі службових повідомлень мережі — як вони потрапляють у програму, розібрано в [помилках ICMP у коді](topic:programming/icmp-errors-in-code).

## Рівень `IPPROTO_TCP`

| Опція | Тип `optval` | Замовчування | Одиниці | Примітка |
| --- | --- | --- | --- | --- |
| `TCP_NODELAY` | `int` (0/1) | 0 — притримування ввімкнене | — | Linux 2.2; кожен `send` виходить негайно |
| `TCP_CORK` | `int` (0/1) | 0 | — | Linux 2.2; неповні сегменти не виходять узагалі, але не довше ніж 200 мс; перекриває `TCP_NODELAY` |
| `TCP_QUICKACK` | `int` (0/1) | 0 | — | Linux 2.4.4; **не постійна** — ядро саме повертає звичайний режим |
| `TCP_USER_TIMEOUT` | `unsigned int` | 0 — брати системну політику повторів | мілісекунди | Linux 2.6.37; скільки даних можуть лишатися непідтвердженими, перш ніж з'єднання оголосять мертвим; діє лише в синхронізованих станах (`ESTABLISHED`, `FIN-WAIT`, `CLOSE-WAIT`…) |
| `TCP_KEEPIDLE` | `int` | `net.ipv4.tcp_keepalive_time` = 7200 | секунди | Linux 2.4; тиша до першої проби |
| `TCP_KEEPINTVL` | `int` | `net.ipv4.tcp_keepalive_intvl` = 75 | секунди | пауза між пробами |
| `TCP_KEEPCNT` | `int` | `net.ipv4.tcp_keepalive_probes` = 9 | штуки | скільки проб без відповіді до розриву |
| `TCP_MAXSEG` | `int` | від MTU шляху | байти | впливає на SYN, лише якщо поставлено до `connect`/`listen`; більше за MTU не діє |
| `TCP_DEFER_ACCEPT` | `int` | 0 | секунди | Linux 2.4; `accept` прокидається, лише коли прийшли дані, а не на голе рукостискання |
| `TCP_INFO` | `struct tcp_info` | — | — | лише читання: стан, виміряний час обігу, вікно перевантаження, лічильники повторів |

Три опції keepalive працюють як одне ціле, і час до розриву мертвого з'єднання рахується просто:

```text
час = KEEPIDLE + KEEPINTVL · KEEPCNT

Замовчування Linux:   7200 + 75 · 9 = 7875 с ≈ 2 год 11 хв
Виявити обрив за 40 с: KEEPIDLE = 20, KEEPINTVL = 5, KEEPCNT = 4
                       20 + 5 · 4 = 40 с
```

Дві години — це не помилка, а свідома настанова RFC 1122: часті проби на тисячах простоюючих з'єднань коштують дорого. Для прикладних протоколів, де обрив треба помітити за секунди, цю трійку ставлять явно, а сам механізм і його межі — у [керуванні з'єднаннями](topic:programming/connection-management). Важлива різниця: keepalive перевіряє **простій**, а `TCP_USER_TIMEOUT` — **непідтверджені дані**. Перший мовчить, поки ти щось шлеш; другий спрацьовує саме тоді, коли ти шлеш, а відповіді немає.

## Рівні `IPPROTO_IP` і `IPPROTO_IPV6`

| Опція | Тип `optval` | Замовчування | Примітка |
| --- | --- | --- | --- |
| `IP_TTL` | `int` | 64 (`net.ipv4.ip_default_ttl`) | бюджет переходів для звичайних пакетів |
| `IP_TOS` | `int`, молодший байт | 0 | верхні 6 бітів — DSCP, нижні 2 — ECN; мережа має право це ігнорувати |
| `IP_MULTICAST_TTL` | Linux — `int`; BSD і macOS — `u_char` | **1** | одиниця = пакет не виходить за свою підмережу |
| `IP_MULTICAST_LOOP` | Linux — `int`; BSD і macOS — `u_char` | 1 (увімкнено) | чи бачить відправник власні пакети на цій же машині |
| `IP_MULTICAST_IF` | `struct in_addr` або `struct ip_mreqn` | інтерфейс за таблицею маршрутів | на машині з кількома інтерфейсами вибір за тобою |
| `IP_ADD_MEMBERSHIP`, `IP_DROP_MEMBERSHIP` | `struct ip_mreq` / `ip_mreqn` | — | лише встановлення; після `bind` |
| `IP_MTU_DISCOVER` | `int` (`IP_PMTUDISC_*`) | `IP_PMTUDISC_WANT` | керує бітом «не фрагментувати» |
| `IP_MTU` | `int` | — | лише читання, лише на з'єднаному сокеті |
| `IP_RECVERR` | `int` (0/1) | 0 | вмикає чергу розширених помилок — інакше ICMP до UDP-програми не доходить |
| `IPV6_UNICAST_HOPS` | `int`; `-1` = системне | системне | те саме, що `IP_TTL`, з чеснішою назвою |
| `IPV6_MULTICAST_HOPS` | `int` | 1 | як `IP_MULTICAST_TTL` |
| `IPV6_MULTICAST_LOOP` | `unsigned int` за RFC 3493 | 1 | значення поза 0…1 → `EINVAL` |
| `IPV6_V6ONLY` | `int` (0/1) | Linux — за `net.ipv6.bindv6only`, типово 0 (подвійний стек) | **до `bind`**; на Windows типово **ввімкнено** |

Головна пастка рівня — не значення, а **тип**. Багатоадресні опції прийшли з 4.4BSD однобайтовими, і у FreeBSD та macOS заголовки досі оголошують `u_char ttl;`. Linux приймає обидві довжини, тому помилку виявляють уже після переносу коду — чужим `EINVAL`.

```c
/* один намір — два типи аргументу */
#if defined(__linux__) || defined(_WIN32)
    int mttl = 8;                    /* Linux: int; Windows: DWORD */
#else
    unsigned char mttl = 8;          /* FreeBSD, macOS та решта BSD */
#endif
setsockopt(fd, IPPROTO_IP, IP_MULTICAST_TTL, &mttl, sizeof mttl);
```

Для IPv6 цієї біди немає свідомо: RFC 3493 оголосив аргументи `int` (для `IPV6_MULTICAST_LOOP` — `unsigned int`) на всіх системах. `IP_MULTICAST_IF` натомість вимагає уваги до порядку байтів: адреса інтерфейсу передається в мережевому порядку, і `htonl` тут не декорація — [порядок байтів](topic:programming/endianness) на x86 та ARM протилежний мережевому, тож забуте перетворення дає тихо неправильний інтерфейс. Решта тонкощів вступу в групу — у [багатоадресній розсилці й виявленні вузлів](topic:programming/multicast-and-discovery).

## Коди помилок

| `errno` | Що означає | Типова причина |
| --- | --- | --- |
| `EBADF` | `fd` — не дескриптор | сокет уже закритий; гонитва в багатопотоковому коді |
| `ENOTSOCK` | дескриптор є, але це не сокет | переплутано з файлом або каналом |
| `ENOPROTOOPT` | опції на цьому рівні немає | не той `level`; стек її не реалізує (типово lwIP або стара система) |
| `EINVAL` | не той `optlen`; іноді — недопустиме значення | передано `int` там, де чекають `struct timeval`; неініціалізований `optlen` у `getsockopt` |
| `EFAULT` | `optval` вказує не в свою пам'ять | покажчик на звільнену змінну; забутий `&` |
| `EPERM` | бракує повноважень | `SO_RCVBUFFORCE`/`SO_SNDBUFFORCE` без `CAP_NET_ADMIN` |

`ENOPROTOOPT` варто обробляти окремо від решти: він означає «цей стек так не вміє», а не «в коді помилка». Програма, яку переносять між Linux, macOS і мікроконтролером, від нього не повинна падати.

```c
/* «спробувати поставити»: відсутність опції — не привід зупинятися */
static int try_setopt(int fd, int level, int name,
                      const void *val, socklen_t len, const char *label)
{
    if (setsockopt(fd, level, name, val, len) == 0)
        return 0;
    if (errno == ENOPROTOOPT) {
        fprintf(stderr, "%s: стек не підтримує — пропущено\n", label);
        return 0;
    }
    fprintf(stderr, "%s: setsockopt: %s\n", label, strerror(errno));
    return -1;
}
```

На Windows контракт інший: обидві функції повертають `SOCKET_ERROR`, `errno` не чіпають, а код беруть із `WSAGetLastError()` — `WSAENOPROTOOPT`, `WSAEINVAL`, `WSAENOTSOCK`, `WSAEFAULT`. Крім того, `optval` там оголошено як `const char *`, тож приведення типу обов'язкове, а дескриптор має тип `SOCKET`, а не `int`.

## Переносність одним поглядом

| Опція | Linux | FreeBSD / macOS | Windows | lwIP (ESP-IDF) |
| --- | --- | --- | --- | --- |
| `SO_RCVTIMEO`, `SO_SNDTIMEO` | `struct timeval` | `struct timeval` | **`DWORD`, мілісекунди** | `struct timeval`, якщо ввімкнено `LWIP_SO_RCVTIMEO`/`LWIP_SO_SNDTIMEO` (в ESP-IDF ввімкнено) |
| `SO_RCVBUF` | є, значення подвоюється | є | `DWORD` | лише при `LWIP_SO_RCVBUF`; в ESP-IDF типово **вимкнено** |
| `SO_SNDBUF` | є | є | `DWORD` | **немає взагалі** — розмір задає `TCP_SND_BUF` при збірці |
| `SO_REUSEADDR` | звільняє адресу в `TIME_WAIT` | так само | **інша семантика**: дозволяє перехопити чужий порт; захист — `SO_EXCLUSIVEADDRUSE` | лише при `SO_REUSE` (в ESP-IDF типово ввімкнено) |
| `SO_REUSEPORT` | з 3.9, з розкладанням навантаження | є (давня BSD-семантика) | немає | немає |
| `SO_LINGER` | є | є | є | лише при `LWIP_SO_LINGER`; в ESP-IDF типово вимкнено |
| `SO_BROADCAST` | є; без неї `sendto` дає `EACCES` | є | є | приймається, але фільтр працює лише при `IP_SOF_BROADCAST = 1` (типово 0) |
| `TCP_NODELAY` | є | є | `DWORD` | є |
| `TCP_CORK` | є, стеля 200 мс | `TCP_NOPUSH` — тримає до закриття сокета або повного буфера | немає | немає |
| `TCP_QUICKACK` | є | немає | немає | немає |
| `TCP_USER_TIMEOUT` | є, мілісекунди | немає | `TCP_MAXRT`, **секунди** | немає |
| `TCP_KEEPIDLE` / `INTVL` / `CNT` | є, секунди | FreeBSD: `u_int`, секунди. macOS: `TCP_KEEPALIVE` замість `TCP_KEEPIDLE` | `TCP_KEEPIDLE`/`TCP_KEEPINTVL` з Windows 10 1709; `TCP_KEEPCNT` з 1703 | лише при `LWIP_TCP_KEEPALIVE` |
| `IP_MULTICAST_TTL`, `IP_MULTICAST_LOOP` | `int` | **`u_char`** | `DWORD`; `IP_MULTICAST_LOOP` ставлять на **приймальному** сокеті, а не на відправному | є; довжину аргументу стек звіряє й на розбіжність дає `EINVAL` — тип уточнюй у `sockets.c` своєї версії |
| `IP_TOS` | є | є | документація радить **не використовувати** — лише через QoS API | є |
| `IP_TTL` | є, типово 64 | є | `DWORD`, типово 128 | є |

Розбіжність у типі таймауту між Linux і Windows — найтихіша з усіх: `struct timeval` на 64-бітній системі має 16 байтів, `DWORD` — чотири, тож переносний код передає їх під `#ifdef`, а не «майже однаково».

## lwIP та ESP-IDF: що задають при збірці

На мікроконтролері половина ручок переїхала з часу виконання в час компіляції. Просити буфер через `setsockopt` там нема в кого: пам'ять розподілено наперед.

| Що | Символ lwIP | Типово в lwIP | ESP-IDF |
| --- | --- | --- | --- |
| максимальний сегмент | `TCP_MSS` | 536 | `CONFIG_LWIP_TCP_MSS` = 1440 |
| приймальне вікно | `TCP_WND` | 4 · `TCP_MSS` | `CONFIG_LWIP_TCP_WND_DEFAULT` = 5760 (4 сегменти) |
| передавальний буфер | `TCP_SND_BUF` | 2 · `TCP_MSS` | `CONFIG_LWIP_TCP_SND_BUF_DEFAULT` = 5760 |
| черга прийнятих датаграм | `DEFAULT_UDP_RECVMBOX_SIZE` | — | `CONFIG_LWIP_UDP_RECVMBOX_SIZE` = 6 **повідомлень** |
| `SO_RCVBUF` | `LWIP_SO_RCVBUF` | 0 (вимкнено) | `CONFIG_LWIP_SO_RCVBUF`, типово вимкнено |
| `SO_LINGER` | `LWIP_SO_LINGER` | 0 | типово вимкнено |
| `SO_REUSEADDR` | `SO_REUSE` | 0 | типово ввімкнено |
| `TCP_KEEP*` | `LWIP_TCP_KEEPALIVE` | 0 | ввімкнено |
| межа повторів | `TCP_MAXRTX` / `TCP_SYNMAXRTX` | 12 / 6 | ті самі 12 / 6 |

Два наслідки варто тримати в голові окремо. По-перше, вікно 5760 байтів прямо обмежує швидкість на далекому шляху — 5760 / 0.1 с ≈ 57.6 КБ/с при часі обігу 100 мс, хоч би який широкий був канал; підняти це можна лише перезбіркою. По-друге, черга UDP лічиться **повідомленнями**, а не байтами: шість датаграм по сорок байтів переповнять її так само, як шість по півтори тисячі, і зайві зникнуть тихо — рівно так, як описано в [семантиці датаграми UDP](topic:programming/udp-datagram-semantics). Чому саме ці числа й де вони живуть у стеку — в [архітектурі lwIP](topic:programming/lwip-internals).
