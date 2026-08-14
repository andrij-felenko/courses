# 📋 Інтерфейс RTNETLINK: структура повідомлень, прапорці та моніторинг стану лінка

Цей довідник описує бінарний контракт та структуру даних підсистеми RTNETLINK (сокетна родина `AF_NETLINK`, протокольний модуль `NETLINK_ROUTE`), яка слугує основним програмним інтерфейсом (API) ядра Linux для запитів, налаштування та асинхронного моніторингу стану мережевих інтерфейсів, IP-адрес і таблиць маршрутизації з простору користувача.

## Загальна архітектура повідомлень Netlink

Мережеві повідомлення Netlink передаються через спеціальні сокети у формі пакетів (Datagrams). На відміну від стандартних сокетів `AF_INET`, де корисне навантаження передається у вигляді байтового потоку без форматування, повідомлення Netlink мають сувору бінарну структуру з вирівнюванням по межі 4 байтів (`NLMSG_ALIGNTO = 4`).

Кожен кадр Netlink складається із заголовка `struct nlmsghdr`, після якого слідує специфічна для операції структура даних (наприклад, `struct ifinfomsg` для мережевих пристроїв L2 або `struct ifaddrmsg` для IP-адрес L3). За цією структурою розміщується потік атрибутів змінної довжини у форматі TLV (Type-Length-Value), укладених у обгортки `struct nlattr` (або `struct rtattr`).

```
┌────────────────────────────────────────────────────────────────────────┐
│                        struct nlmsghdr (16 bytes)                      │
├────────────────────────────────────────────────────────────────────────┤
│ struct ifinfomsg (16 bytes)  АБО  struct ifaddrmsg (8 bytes)           │
├────────────────────────────────────────────────────────────────────────┤
│ struct nlattr [1] (Type, Length, Data...)                              │
├────────────────────────────────────────────────────────────────────────┤
│ struct nlattr [2] (Type, Length, Data...)                              │
└────────────────────────────────────────────────────────────────────────┘
```

Якщо буфер містить декілька повідомлень Netlink підряд (наприклад, при отриманні повного списку інтерфейсів системи), кожне нове повідомлення вирівнюється на межу `NLMSG_ALIGN(len)`. Кінцевим кадром у потоці завжди є порожнє повідомлення з типом `NLMSG_DONE`.

## Створення сокета та сокетна адресація Netlink

Взаємодія з підсистемою Netlink починається зі створення сокета за допомогою системного виклику `socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE)`. Тип сокета `SOCK_RAW` або `SOCK_DGRAM` вказує ядрашній підсистемі, що повідомлення будуть передаватися у формі дискретних бінарних кадрів із збереженням меж повідомлень.

Для адресації вузлів у мережі Netlink використовується спеціальна структура `struct sockaddr_nl`, визначена у заголовочному файлі `<linux/netlink.h>`:

```c
struct sockaddr_nl {
    sa_family_t nl_family; /* Завжди AF_NETLINK */
    unsigned short nl_pad;  /* Нульове вирівнювання (Reserved) */
    __u32 nl_pid;          /* Порт / PID процесу (0 для ядра) */
    __u32 nl_groups;       /* Бітова маска мультикаст-груп подій */
};
```

Поле `nl_pid` слугує унікальним ідентифікатором сокета у просторі адресації Netlink. Якщо додаток передає `nl_pid = 0`, ядро самостійно призначає сокету PID поточного процесу (або ідентифікатор потоку). Поле `nl_groups` є 32-бітною маскою, яка визначає, які самі підсистеми сповіщень ядра повинен слухати даний сокет.

## Права доступу та безпека (`CAP_NET_ADMIN`)

Прочитати поточний стан мережевих інтерфейсів та адрес (операції `RTM_GETLINK` та `RTM_GETADDR`) може будь-який непривілейований процес у системі. Проте для виконання будь-яких мутаційних операцій — підйому чи зупинки лінка (`RTM_NEWLINK`), додавання чи видалення IP-адрес (`RTM_NEWADDR` / `RTM_DELADDR`), створення віртуальних `veth` пар або зміни MTU — ядро Linux вимагає наявності привілею **`CAP_NET_ADMIN`** у контексті безпеки викликаючого процесу. При відсутності необхідних привілеїв ядро миттєво відхиляє спробу зміни кадру Netlink, повертаючи помилку `EPERM` (Operation not permitted) у полі `error` структури `nlmsgerr`.

У середовищах із мережевими просторами назв (Network Namespaces) володіння привілеєм `CAP_NET_ADMIN` перевіряється в контексті конкретного `struct net`. Це дозволяє безкорінним (rootless) контейнерам мати повний доступ до керування своїми віртуальними інтерфейсами у власному просторі назв, не маючи при цьому можливості змінити конфігурацію мережі фізичного хоста.

## Налаштування опцій сокета `SOL_NETLINK`

Підсистема Netlink підтримує широкий набір специфічних опцій сокета, що налаштовуються через системний виклик `setsockopt(fd, SOL_NETLINK, option, &val, sizeof(val))`:

1. `NETLINK_ADD_MEMBERSHIP` / `NETLINK_DROP_MEMBERSHIP`:
   Дозволяє динамічно підписуватися на нові мультикаст-групи подій або відписуватися від них без перестворення сокета. Це корисно для демонів, які динамічно змінюють свій контекст моніторингу.

2. `NETLINK_PKTINFO`:
   Вмикає повернення допоміжних метаданих `struct nl_pktinfo` через розширений виклик `recvmsg()`. Це дає змогу додатку точно визначати PID відправника та мультикаст-групу кожного отриманого пакета.

3. `NETLINK_GET_STRICT_CHK`:
   Вмикає строгу перевірку атрибутів запитів ядра. При увімкненні цієї опції ядро жорстко відхиляє запити, які містять невідомі прапорці чи сміття в резервних полях заголовка `ifinfomsg` чи `ifaddrmsg`.

4. `NETLINK_EXT_ACK`:
   Вмикає повернення розширених текстових діагностичних повідомлень про помилки від ядра.

## Налаштування розміру сокетного буфера та обробка ENOBUFS

Коли системний демон підписується на мультикаст-групи подій Netlink, інтенсивний потік повідомлень (наприклад, при переключенні тисяч інтерфейсів або маршрутів) може швидко заповнити приймальний буфер сокета.

За замовчуванням ядро обмежує розмір сокетного буфера параметром `sysctl net.core.rmem_default`. Якщо буфер переповнюється, ядро скидає нові повідомлення і встановлює прапорець помилки. Наступний виклик `recv()` або `recvmsg()` повертає помилку `ENOBUFS` (No buffer space available).

Щоб запобігти втраті сповіщень, високонавантажені системні демони збільшують розмір приймального буфера через системний виклик `setsockopt()`:

```c
int rcvbuf = 1024 * 1024; /* 1 Мегабайт */
setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));
```

При отриманні помилки `ENOBUFS` демон повинен розуміти, що його локальний кеш стану мережі синхронізацію втратив. У цьому випадку програма повинна очистити свої внутрішні таблиці та виконати повторний дамп-запит `RTM_GETLINK` / `RTM_GETADDR` із прапорцем `NLM_F_DUMP` для повного відновлення конфігураційного стану.

## Структури заголовків та полів

### 1. Заголовок повідомлення: struct nlmsghdr (`<linux/netlink.h>`)

Заголовок `struct nlmsghdr` є обов'язковим для всіх кадриків, що передаються через будь-яке сімейство Netlink:

```c
struct nlmsghdr {
    __u32 nlmsg_len;   /* Повний розмір повідомлення у байтах, включно із заголовком */
    __u16 nlmsg_type;  /* Тип повідомлення (наприклад, RTM_NEWLINK, RTM_GETLINK) */
    __u16 nlmsg_flags; /* Бітові прапорці запиту та режиму обробки */
    __u32 nlmsg_seq;   /* Послідовний номер (Sequence Number) для трекінгу */
    __u32 nlmsg_pid;   /* Порт Netlink / PID процесу відправника (0 для ядра) */
};
```

#### Типи повідомлень (`nlmsg_type`)
* `RTM_NEWLINK`: Створення віртуального інтерфейсу або сповіщення про зміну стану наявного інтерфейсу (L2).
* `RTM_DELLINK`: Видалення віртуального інтерфейсу з системи.
* `RTM_GETLINK`: Запит інформації про один або всі мережеві інтерфейси.
* `RTM_NEWADDR`: Додавання нової IP-адреси на інтерфейс або сповіщення про появу нової адреси.
* `RTM_DELADDR`: Видалення IP-адреси з інтерфейсу.
* `RTM_GETADDR`: Запит списку IP-адрес.
* `RTM_NEWROUTE` / `RTM_DELROUTE` / `RTM_GETROUTE`: Створення, видалення або запит таблиць маршрутизації L3.
* `RTM_NEWNEIGH` / `RTM_DELNEIGH` / `RTM_GETNEIGH`: Керування таблицею сусідів ARP/NDP.
* `NLMSG_ERROR`: Повідомлення про помилку від ядра (містить код помилки `errno` та копію вихідного заголовка).
* `NLMSG_DONE`: Позначка завершення багатокадрової відповіді (Dump Done).

#### Прапорці повідомлень (`nlmsg_flags`)
* `NLM_F_REQUEST`: Обов'язковий прапорець для всіх запитів від користувацького простору до ядра.
* `NLM_F_MULTI`: Повідомлення є частиною послідовності з декількох кадрів (вимагає читання буфера до `NLMSG_DONE`).
* `NLM_F_ACK`: Запит до ядра надіслати підтвердження успішного виконання операції кадром `NLMSG_ERROR` із кодом `0`.
* `NLM_F_ECHO`: Прохання до ядра надіслати копію запитуваної зміни у мультикаст-групу подій.
* `NLM_F_DUMP`: Запит на отримання повного списку всіх об'єктів (еквівалент `NLM_F_ROOT | NLM_F_MATCH`).
* `NLM_F_REPLACE`: Оновити наявний об'єкт замість створення нового.
* `NLM_F_EXCL`: Повернути помилку `EEXIST`, якщо об'єкт вже існує при спробі створення.
* `NLM_F_CREATE`: Створити об'єкт, якщо він ще не існує в ядрі.
* `NLM_F_APPEND`: Додати новий елемент у кінець списку адрес або маршрутів.
* `NLM_F_DUMP_INTR`: Повідомлення про те, що дамп списку був перерваний через зміну стану ядра під час ітерації.

### 2. Контекст мережевого пристрою: struct ifinfomsg (`<linux/if_link.h>`)

Заголовок `struct ifinfomsg` розміщується безпосередньо після `struct nlmsghdr` у всіх повідомленнях типу `RTM_*LINK`:

```c
struct ifinfomsg {
    unsigned char  ifi_family; /* Сімейство адрес (зазвичай AF_UNSPEC) */
    unsigned short ifi_type;   /* Апаратний тип пристрою (ARPHRD_ETHER, ARPHRD_LOOPBACK) */
    int            ifi_index;  /* Унікальний системний індекс пристрою (ifindex) */
    unsigned int   ifi_flags;  /* Бітові прапорці пристрою (IFF_UP, IFF_RUNNING тощо) */
    unsigned int   ifi_change; /* Маска змінюваних прапорців (зазвичай 0xFFFFFFFF) */
};
```

Поле `ifi_flags` містить комбінацію класичних прапорців `IFF_*` (наприклад, `IFF_UP`, `IFF_RUNNING`, `IFF_PROMISC`, `IFF_BROADCAST`, `IFF_MULTICAST`, `IFF_LOOPBACK`).

### 3. Контекст IP-адреси: struct ifaddrmsg (`<linux/if_addr.h>`)

Заголовок `struct ifaddrmsg` розміщується після `struct nlmsghdr` у всіх повідомленнях типу `RTM_*ADDR`:

```c
struct ifaddrmsg {
    unsigned char ifa_family;    /* Сімейство адрес: AF_INET (IPv4) або AF_INET6 (IPv6) */
    unsigned char ifa_prefixlen; /* Довжина CIDR-префікса маски (наприклад, 24 для /24) */
    unsigned char ifa_flags;     /* Прапорці IP-адреси (IFA_F_SECONDARY, IFA_F_PERMANENT) */
    unsigned char ifa_scope;     /* Область видимості адреси (RT_SCOPE_UNIVERSE, RT_SCOPE_LINK) */
    unsigned int  ifa_index;     /* Системний індекс пристрою (ifindex), якому належить адреса */
};
```

#### Прапорці IP-адреси (`ifa_flags`)
* `IFA_F_SECONDARY`: Другорядна (вторинна) адреса у цій підмережі.
* `IFA_F_NODAD`: Вимкнути процес виявлення дубльованих адрес (DAD) для IPv6.
* `IFA_F_OPTIMISTIC`: Оптимістична IPv6-адреса (може використовуватися до завершення DAD).
* `IFA_F_DADFAILED`: Спроба активації IPv6-адреси провалилася через виявлений конфлікт у мережі.
* `IFA_F_HOMEADDRESS`: Адреса є Mobile IPv6 Home Address.
* `IFA_F_DEPRECATED`: Застаріла IPv6-адреса (віддається перевага іншим адресам для нових з'єднань).
* `IFA_F_PERMANENT`: Постійна адреса, налаштована адміністративно (не через SLAAC/DHCPv6).
* `IFA_F_MANAGETEMPADDR`: Ядро повинно автоматично генерувати тимчасові адреси (Privacy Extensions).
* `IFA_F_NOPREFIXROUTE`: Ядро не повинно автоматично створювати маршрут підмережі при додаванні цієї адреси.

#### Область видимості адреси (`ifa_scope`)
* `RT_SCOPE_UNIVERSE` (0): Глобальна адреса, що маршрутизується у глобальній мережі.
* `RT_SCOPE_SITE` (200): Адреса, обмежена межами організації/сайту.
* `RT_SCOPE_LINK` (253): Адреса, дійсна лише в межах локального кабельного сегмента (Link-Local).
* `RT_SCOPE_HOST` (254): Адреса, обмежена локальним хостом (Loopback `127.0.0.1` або `::1`).
* `RT_SCOPE_NOWHERE` (255): Адреса незастосовна для маршрутизації.

### 4. Контекст маршрутизації: struct rtmsg (`<linux/rtnetlink.h>`)

Заголовок `struct rtmsg` описує елементи таблиць маршрутизації L3 при обміні кадрами `RTM_*ROUTE`:

```c
struct rtmsg {
    unsigned char rtm_family;   /* AF_INET або AF_INET6 */
    unsigned char rtm_dst_len;  /* Довжина маски призначення (CIDR, наприклад 24) */
    unsigned char rtm_src_len;  /* Довжина маски джерела (для Source-Based Routing) */
    unsigned char rtm_tos;      /* Тип обслуговування (Type of Service) */
    unsigned char rtm_table;    /* Ідентифікатор таблиці (RT_TABLE_MAIN, RT_TABLE_LOCAL) */
    unsigned char rtm_protocol; /* Походження маршруту (RTPROT_BOOT, RTPROT_STATIC, RTPROT_BGP) */
    unsigned char rtm_scope;    /* Область видимості (RT_SCOPE_UNIVERSE, RT_SCOPE_LINK) */
    unsigned char rtm_type;     /* Тип маршруту (RTN_UNICAST, RTN_LOCAL, RTN_BLACKHOLE) */
    unsigned int  rtm_flags;    /* Прапорці маршруту (RTM_F_CLONED, RTM_F_PREFIX) */
};
```

Пов'язані атрибути маршруту (`RTA_*`): `RTA_DST` (адреса призначення), `RTA_SRC` (адреса джерела), `RTA_GATEWAY` (IP шлюзу Next-Hop), `RTA_OIF` (індекс вихідного мережевого пристрою), `RTA_PREFSRC` (надана перевага локальній джерельній адресі).

### 5. Контекст таблиці сусідів ARP/NDP: struct ndmsg (`<linux/neighbour.h>`)

Заголовок `struct ndmsg` описує мапування L2/L3 у кеші ARP/NDP при обміні кадрами `RTM_*NEIGH`:

```c
struct ndmsg {
    unsigned char ndm_family; /* AF_INET або AF_INET6 */
    int           ndm_ifindex;/* Індекс мережевого інтерфейсу */
    __u16         ndm_state;  /* Стан запису сусідів (NUD_REACHABLE, NUD_STALE, NUD_FAILED) */
    unsigned char ndm_flags;  /* Прапорці (NTF_PROXY, NTF_ROUTER) */
    unsigned char ndm_type;   /* Тип сусіда (RTN_UNICAST) */
};
```

Значення стану `ndm_state`:
* `NUD_INCOMPLETE`: Триває процес розпізнавання адреси (надсилаються ARP/NDP запити).
* `NUD_REACHABLE`: Адреса підтверджена і працездатна.
* `NUD_STALE`: Таймер активності вичерпано, запис потребує перевірки при наступній передачі.
* `NUD_FAILED`: Розпізнавання адреси провалилося (немає відповіді на ARP/NDP).
* `NUD_PERMANENT`: Статичний запис, внесений адміністратором (не вилучається таймером).

## Таблиці атрибутів TLV (Attributes)

Після фіксованого заголовка `ifinfomsg` або `ifaddrmsg` у кадрі Netlink розміщується послідовність атрибутів у форматі `struct rtattr` (`struct nlattr`). Кожен атрибут складається з заголовка та даних:

```c
struct rtattr {
    unsigned short rta_len;  /* Розмір атрибута у байтах, включно із заголовком */
    unsigned short rta_type; /* Тип атрибута (константи IFLA_* або IFA_*) */
};
```

### Основні атрибути мережевого пристрою (`IFLA_*`)

Атрибути `IFLA_*` використовуються при запитах та сповіщеннях стану L2:

| Константа | Тип даних | Докладна семантика та призначення |
| :--- | :--- | :--- |
| `IFLA_IFNAME` | Рядок (`char[]`) | Назва мережевого інтерфейсу (наприклад, `"eth0"`, `"wlan0"`, `"docker0"`). |
| `IFLA_ADDRESS` | Масив байтів | Апаратна L2 адреса інтерфейсу (MAC-адреса для Ethernet). |
| `IFLA_BROADCAST` | Масив байтів | Апаратна широкомовна L2 адреса (наприклад, `FF:FF:FF:FF:FF:FF`). |
| `IFLA_MTU` | `__u32` | Поточний розмір максимального блоку передачі MTU в байтах. |
| `IFLA_LINK` | `__u32` | Індекс фізичного пристрою-підкладки (для VLAN, macvlan, veth). |
| `IFLA_QDISC` | Рядок (`char[]`) | Назва активної дисципліни черги (наприклад, `"fq_codel"`, `"noqueue"`). |
| `IFLA_OPERSTATE` | `__u8` | Операційний стан за RFC 2863 (коди `IF_OPER_*`). |
| `IFLA_CARRIER` | `__u8` | Наявність фізичного носія (1 — є лінк, 0 — лінк відсутній). |
| `IFLA_PROMISCUOUS` | `__u32` | Лічильник увімкнення нерозбірливого режиму Promiscuous Mode. |
| `IFLA_NUM_TX_QUEUES` | `__u32` | Кількість апаратних черг передачі Tx у пристрої. |
| `IFLA_NUM_RX_QUEUES` | `__u32` | Кількість апаратних черг прийому Rx у пристрої. |
| `IFLA_LINKINFO` | Вкладений TLV | Метадані віртуального драйвера (`IFLA_INFO_KIND`, `IFLA_INFO_DATA`). |
| `IFLA_NET_NS_FD` | `int` | Файл-дескриптор цільового мережевого простору назв для переміщення пристрою. |
| `IFLA_STATS64` | `struct rtnl_link_stats64` | Розширена 64-бітна лічильникова статистика (пакети, байти, помилки). |

### Основні атрибути IP-адреси (`IFA_*`)

Атрибути `IFA_*` описують параметри призначених IP-адрес L3:

| Константа | Тип даних | Докладна семантика та призначення |
| :--- | :--- | :--- |
| `IFA_ADDRESS` | `struct in_addr` / `in6_addr` | IP-адреса призначення для P2P з'єднань або сама IP-адреса хоста. |
| `IFA_LOCAL` | `struct in_addr` / `in6_addr` | Локальна IP-адреса хоста на інтерфейсі. |
| `IFA_LABEL` | Рядок (`char[]`) | Текстова мітка адреси або назва застарілого псевдоніма (`"eth0:1"`). |
| `IFA_BROADCAST` | `struct in_addr` | Широкомовна IPv4-адреса підмережі (наприклад, `192.168.1.255`). |
| `IFA_ANYCAST` | `struct in6_addr` | Anycast-адреса для протоколу IPv6. |
| `IFA_CACHEINFO` | `struct ifa_cacheinfo` | Таймери життя адреси (Preferred lifetime, Valid lifetime). |
| `IFA_FLAGS` | `__u32` | Розширені 32-бітні прапорці адреси (розширення `ifa_flags`). |

### Вкладені атрибути `IFLA_LINKINFO` для віртуальних пристроїв

Коли простір користувача створює віртуальний пристрій (наприклад, VLAN або парні veth-інтерфейси), конфігураційні параметри передаються у вкладеному атрибуті `IFLA_LINKINFO`. Усередині цього атрибута розміщуються додаткові под-атрибути:
* `IFLA_INFO_KIND`: Рядок, що вказує драйвер віртуального пристрою високої якості (наприклад, `"veth"`, `"vlan"`, `"bridge"`, `"macvlan"`, `"dummy"`, `"bond"`).
* `IFLA_INFO_DATA`: Вкладений контейнер атрибутів, специфічних для обраного драйвера. Наприклад, для `vlan` тут передається `IFLA_VLAN_ID` (`__u16`), а для `veth` — заголовок `struct ifinfomsg` та атрибути парного інтерфейсу.

### Програмне створення віртуальної veth-пари через RTNETLINK

Для створення віртуальної парної мережевої структури `veth` додаток формує кадр `RTM_NEWLINK` із прапорцями `NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL`.

У буфер додаються атрибут `IFLA_IFNAME` (назва першого інтерфейсу, наприклад `"veth0"`) та вкладений атрибут `IFLA_LINKINFO`. Усередині `IFLA_LINKINFO` атрибут `IFLA_INFO_KIND` встановлюється в рядок `"veth"`. Додатково додається атрибут `VETH_INFO_PEER`, усередині якого передається повний заголовок `struct ifinfomsg` та атрибут `IFLA_IFNAME` другого парного інтерфейсу (наприклад, `"veth1"`).

Після відправлення каду у сокет RTNETLINK ядро атомарно виділяє пам'ять під обидва пристрої `struct net_device`, пов'язує їхні операційні вектори `.ndo_start_xmit` і повертає підтвердження `NLMSG_ERROR` із кодом `0`.

### Використання вищих бібліотечних абстракцій (libnl / libmnl)

Хоча низькорівнева обробка бінарних кадрів Netlink дає максимальну продуктивність і нульові додаткові залежності, великі системні проєкти (наприклад, NetworkManager, FRRouting або WPA Supplicant) часто використовують високорівневі бібліотеки абстракції — **`libnl`** (Library for Netlink Protocol) або **`libmnl`** (Minimalistic Netlink Library).

Бібліотека `libnl` надає зручний об'єктно-орієнтований C-інтерфейс, який позбавляє розробника необхідності вручну обчислювати вирівнювання `NLMSG_ALIGN` та обходити атрибути макросами `RTA_NEXT`:

* `nl_socket_alloc()`: Виділяє та ініціалізує сокет Netlink.
* `nl_connect(sk, NETLINK_ROUTE)`: Відкриває сокет та виконує прив'язку `bind()`.
* `rtnl_link_alloc()`: Виділяє об'єкт абстрактного мережевого пристрою.
* `rtnl_link_set_name(link, "veth0")`: Встановлює назву інтерфейсу через безпечні методи.
* `rtnl_link_add(sk, link, NLM_F_CREATE)`: Серіалізує об'єкт у потік TLV-атрибутів і надсилає запит ядра.

Використання `libmnl` забезпечує більш тонкий шар абстракції без виділення динамічної пам'яті heap, що дозволяє поєднати безпеку викликів із високою швидкістю серіалізації.

### Коди операційного стану RFC 2863 (`IF_OPER_*`)

Значення атрибута `IFLA_OPERSTATE`:

* `IF_OPER_UNKNOWN` (0): Операційний стан невідомий драйверу пристрою.
* `IF_OPER_NOTPRESENT` (1): Апаратне забезпечення відсутнє у слоті (наприклад, витягнуто USB/SFP карту).
* `IF_OPER_DOWN` (2): Інтерфейс вимкнено адміністративно (прапорець `IFF_UP = 0`).
* `IF_OPER_LOWERLAYERDOWN` (3): Відсутній нижній фізичний шар (наприклад, підкладковий порт для VLAN вимкнено).
* `IF_OPER_TESTING` (4): Пристрій знаходиться в режимі апаратного діагностичного тестування.
* `IF_OPER_DORMANT` (5): Пристрій очікує на зовнішню підтверджувальну подію (наприклад, завершення сесії шифрування EAPOL/802.1X). Пакети даних не проходять.
* `IF_OPER_UP` (6): Інтерфейс повністю функціональний, кабель підключено, обмін даними дозволено.

## Валідація політик атрибутів у ядрі (`struct nla_policy`)

Для забезпечення надійності підсистема Netlink у ядрі перевіряє кожен отриманий атрибут за допомогою політик валідації `struct nla_policy`. При виконанні запиту `RTM_NEWLINK` ядро звіряє розібраний атрибут із таблицею очікуваних типів:

```c
/* Концептуальна схема валідації атрибутів у ядрі */
static const struct nla_policy ifla_policy[IFLA_MAX+1] = {
    [IFLA_IFNAME]     = { .type = NLA_STRING, .len = IFNAMSIZ - 1 },
    [IFLA_MTU]        = { .type = NLA_U32 },
    [IFLA_ADDRESS]    = { .type = NLA_BINARY, .len = MAX_ADDR_LEN },
    [IFLA_OPERSTATE]  = { .type = NLA_U8 },
};
```

Якщо користувацький додаток надсилає атрибут із розбіжністю типів або некоректним розміром, ядро припиняє обробку пакета і повертає помилку `EINVAL` або `ERANGE` кадром `NLMSG_ERROR`.

## Макроси парсингу та навігації Netlink

Для забезпечення безпечного розбору бінарних буферів та уникнення помилок вирівнювання пам'яті ядро Linux надає набір фундаментальних макросів у заголовках `<linux/netlink.h>` та `<linux/rtnetlink.h>`.

Використання цих макросів є обов'язковим, оскільки прямий доступ до полів через розв'язання вказівників без урахування вирівнювання `NLMSG_ALIGN` призводить до фатальних помилок непогодженого доступу (Bus Error) на архітектурах ARM, MIPS та SPARC.

```c
/* Вирівнювання розміру len на межу NLMSG_ALIGNTO (4 байти) */
NLMSG_ALIGN(len)

/* Мінімальний розмір заголовка з урахуванням вирівнювання */
NLMSG_HDRLEN

/* Обчислення повного розміру кадру для корисного навантаження len */
NLMSG_LENGTH(len)

/* Обчислення зайнятого місця в буфері з урахуванням вирівнювання tails */
NLMSG_SPACE(len)

/* Отримання вказівника на корисне навантаження після nlmsghdr */
NLMSG_DATA(nlh)

/* Перехід до наступного заголовка повідомлення у буфері */
NLMSG_NEXT(nlh, len)

/* Перевірка, чи не вийшов заголовок nlh за межі буферу len */
NLMSG_OK(nlh, len)

/* Отримання розміру корисного навантаження повідомлення */
NLMSG_PAYLOAD(nlh, len)

/* Отримання вказівника на перший атрибут rtattr після ifinfomsg */
IFLA_RTA(ifi)

/* Отримання вказівника на перший атрибут rtattr після ifaddrmsg */
IFA_RTA(ifa)

/* Перевірка валідності атрибута rta у буфері len */
RTA_OK(rta, len)

/* Перехід до наступного атрибута в потоці TLV */
RTA_NEXT(rta, len)

/* Отримання вказівника на бінарні дані атрибута */
RTA_DATA(rta)

/* Отримання розміру даних атрибута без урахування заголовка */
RTA_PAYLOAD(rta)
```

## Асинхронний моніторинг подій через Multicast Groups

Однією з найпотужніших можливостей RTNETLINK є можливість асинхронного стеження за змінами мережевого стану без опитання (Polling).

Щоб отримувати події від ядра в реальному часі, користувацький процес відкриває сокет `AF_NETLINK` і прив'язує його викликом `bind()` до однієї чи кількох мультикаст-групи:

```c
struct sockaddr_nl sa;
memset(&sa, 0, sizeof(sa));
sa.nl_family = AF_NETLINK;
sa.nl_groups = RTMGRP_LINK | RTMGRP_IPV4_IFADDR | RTMGRP_IPV6_IFADDR;

bind(fd, (struct sockaddr *)&sa, sizeof(sa));
```

Після виконання `bind()` сокет стає приймачем асинхронних сповіщень. Коли кабель Ethernet витягується з порту, ядро негайно надсилає в сокет кадр `RTM_NEWLINK` із прапорцем `IFF_RUNNING = 0` та атрибутом `IFLA_OPERSTATE = IF_OPER_LOWERLAYERDOWN`. Демони керування мережею (systemd-networkd, NetworkManager) інтегрують файл-дескриптор цього сокета у свій асинхронний цикл обробки подій `epoll()`, досягаючи нульових накладних витрат у стані спокою.

### Розширені підтвердження помилок (Extended ACK / NETLINK_EXT_ACK)

У сучасних ядрах Linux (починаючи з ядра 4.12) додано опцію сокета `NETLINK_EXT_ACK`. При її активації через `setsockopt(fd, SOL_NETLINK, NETLINK_EXT_ACK, &val, sizeof(val))` ядро у відповідь на помилковий запит повертає не просто код `errno`, а розширене повідомлення `NLMSG_ERROR` із доданим текстовим атрибутом `NLMSGERR_ATTR_MSG`.

Це дає змогу розробникам отримувати зрозумілі людині текстові описи причини відмови ядра (наприклад, `"VLAN ID already assigned to another interface"` або `"Interface index does not exist"`), що істотно спрощує діагностику та налагодження системного коду.

## Робочі приклади коду: Дамп стану інтерфейсів та моніторинг

:::tabs
```c
/* C11 implementation: querying interface state via RTNETLINK */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <net/if.h>
#include <arpa/inet.h>

#define BUF_SIZE 8192

static void parse_rtattr(struct rtattr *tb[], int max, struct rtattr *rta, int len) {
    memset(tb, 0, sizeof(struct rtattr *) * (max + 1));
    while (RTA_OK(rta, len)) {
        if (rta->rta_type <= max) {
            tb[rta->rta_type] = rta;
        }
        rta = RTA_NEXT(rta, len);
    }
}

int main(void) {
    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
    if (fd < 0) {
        perror("socket AF_NETLINK");
        return 1;
    }

    struct {
        struct nlmsghdr nlh;
        struct ifinfomsg ifm;
    } req;

    memset(&req, 0, sizeof(req));
    req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
    req.nlh.nlmsg_type = RTM_GETLINK;
    req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_DUMP;
    req.nlh.nlmsg_seq = 1;
    req.ifm.ifi_family = AF_UNSPEC;

    if (send(fd, &req, req.nlh.nlmsg_len, 0) < 0) {
        perror("send");
        close(fd);
        return 1;
    }

    char buffer[BUF_SIZE];
    ssize_t status = recv(fd, buffer, sizeof(buffer), 0);
    if (status < 0) {
        perror("recv");
        close(fd);
        return 1;
    }

    for (struct nlmsghdr *nlh = (struct nlmsghdr *)buffer;
         NLMSG_OK(nlh, (size_t)status);
         nlh = NLMSG_NEXT(nlh, status)) {

        if (nlh->nlmsg_type == NLMSG_DONE) break;
        if (nlh->nlmsg_type == NLMSG_ERROR) {
            fprintf(stderr, "Error message received from Netlink\n");
            close(fd);
            return 1;
        }

        if (nlh->nlmsg_type == RTM_NEWLINK) {
            struct ifinfomsg *ifi = (struct ifinfomsg *)NLMSG_DATA(nlh);
            struct rtattr *tb[IFLA_MAX + 1];
            int rta_len = nlh->nlmsg_len - NLMSG_SPACE(sizeof(*ifi));

            parse_rtattr(tb, IFLA_MAX, IFLA_RTA(ifi), rta_len);

            const char *ifname = tb[IFLA_IFNAME] ? (const char *)RTA_DATA(tb[IFLA_IFNAME]) : "unknown";
            unsigned int mtu = tb[IFLA_MTU] ? *(unsigned int *)RTA_DATA(tb[IFLA_MTU]) : 0;
            unsigned char operstate = tb[IFLA_OPERSTATE] ? *(unsigned char *)RTA_DATA(tb[IFLA_OPERSTATE]) : 0;

            printf("Interface index %d: name=%s, MTU=%u, IFF_UP=%s, IFF_RUNNING=%s, operstate=%u\n",
                   ifi->ifi_index, ifname, mtu,
                   (ifi->ifi_flags & IFF_UP) ? "YES" : "NO",
                   (ifi->ifi_flags & IFF_RUNNING) ? "YES" : "NO",
                   operstate);
        }
    }

    close(fd);
    return 0;
}
```
```cpp
// C++20 implementation: querying interface state using RAII and std::span
#include <iostream>
#include <vector>
#include <string_view>
#include <span>
#include <memory>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <net/if.h>

class NetlinkSocket {
    int fd_{-1};
public:
    NetlinkSocket() {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to open AF_NETLINK socket");
        }
    }
    ~NetlinkSocket() {
        if (fd_ >= 0) ::close(fd_);
    }
    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;
    NetlinkSocket(NetlinkSocket&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    NetlinkSocket& operator=(NetlinkSocket&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
};

struct InterfaceInfo {
    int index{0};
    std::string name;
    uint32_t mtu{0};
    bool is_up{false};
    bool is_running{false};
    uint8_t operstate{0};
};

std::vector<InterfaceInfo> fetch_interfaces() {
    NetlinkSocket sock;

    struct alignas(NLMSG_ALIGNTO) DumpRequest {
        nlmsghdr nlh;
        ifinfomsg ifm;
    } req{};

    req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(ifinfomsg));
    req.nlh.nlmsg_type = RTM_GETLINK;
    req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_DUMP;
    req.nlh.nlmsg_seq = 1;
    req.ifm.ifi_family = AF_UNSPEC;

    if (::send(sock.get(), &req, req.nlh.nlmsg_len, 0) < 0) {
        throw std::system_error(errno, std::generic_category(), "Failed to send RTNETLINK dump request");
    }

    std::vector<uint8_t> buffer(16384);
    ssize_t bytes_read = ::recv(sock.get(), buffer.data(), buffer.size(), 0);
    if (bytes_read < 0) {
        throw std::system_error(errno, std::generic_category(), "Failed to receive RTNETLINK response");
    }

    std::vector<InterfaceInfo> result;
    auto msg_len = static_cast<size_t>(bytes_read);
    auto* nlh = reinterpret_cast<nlmsghdr*>(buffer.data());

    for (; NLMSG_OK(nlh, msg_len); nlh = NLMSG_NEXT(nlh, msg_len)) {
        if (nlh->nlmsg_type == NLMSG_DONE) break;
        if (nlh->nlmsg_type == NLMSG_ERROR) {
            throw std::runtime_error("Netlink returned error header");
        }

        if (nlh->nlmsg_type == RTM_NEWLINK) {
            auto* ifi = static_cast<ifinfomsg*>(NLMSG_DATA(nlh));
            InterfaceInfo info{};
            info.index = ifi->ifi_index;
            info.is_up = (ifi->ifi_flags & IFF_UP) != 0;
            info.is_running = (ifi->ifi_flags & IFF_RUNNING) != 0;

            auto rta_len = static_cast<int>(nlh->nlmsg_len - NLMSG_SPACE(sizeof(*ifi)));
            auto* rta = IFLA_RTA(ifi);

            std::vector<rtattr*> tb(IFLA_MAX + 1, nullptr);
            while (RTA_OK(rta, rta_len)) {
                if (rta->rta_type <= IFLA_MAX) {
                    tb[rta->rta_type] = rta;
                }
                rta = RTA_NEXT(rta, rta_len);
            }

            if (tb[IFLA_IFNAME]) {
                info.name = static_cast<const char*>(RTA_DATA(tb[IFLA_IFNAME]));
            }
            if (tb[IFLA_MTU]) {
                info.mtu = *static_cast<uint32_t*>(RTA_DATA(tb[IFLA_MTU]));
            }
            if (tb[IFLA_OPERSTATE]) {
                info.operstate = *static_cast<uint8_t*>(RTA_DATA(tb[IFLA_OPERSTATE]));
            }

            result.push_back(std::move(info));
        }
    }

    return result;
}

int main() {
    try {
        auto interfaces = fetch_interfaces();
        for (const auto& dev : interfaces) {
            std::cout << "Dev [" << dev.index << "]: " << dev.name
                      << " MTU=" << dev.mtu
                      << " UP=" << (dev.is_up ? "1" : "0")
                      << " RUNNING=" << (dev.is_running ? "1" : "0")
                      << " OperState=" << static_cast<int>(dev.operstate) << "\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Fatal error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::
