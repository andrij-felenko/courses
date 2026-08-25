# 📋 Структури даних та макроси Netlink: nlmsghdr, nlattr, rtattr

Ця довідкова вставка містить детальний двійковий опис базових структур даних, прапорців, системних макросів вирівнювання та специфічних заголовків підсистем ядра Linux для протоколів Netlink (`AF_NETLINK`). Вона слугує низькорівневим орієнтиром для розробників системного програмного забезпечення на мовах C та C++.

## Загальний заголовок повідомлення: struct nlmsghdr

Кожна дейтаграма Netlink (як від простору користувача до ядра, так і у зворотному напрямку) починається зі стандартного заголовка `struct nlmsghdr`, визначеного у файлі `<linux/netlink.h>`. Заголовок має вирівняний розмір 16 байтів і передує корисному навантаженню.

:::tabs
```c
struct nlmsghdr {
    __u32 nlmsg_len;   /* Повна довжина повідомлення у байтах (включаючи цей заголовок) */
    __u16 nlmsg_type;  /* Тип вмісту або коду команди підсистеми */
    __u16 nlmsg_flags; /* Бітові прапорці керування та режимів обробки */
    __u32 nlmsg_seq;   /* Номер послідовності (Sequence number) для квитування */
    __u32 nlmsg_pid;   /* Порт-ідентифікатор відправника (Port ID, зазвичай PID) */
};
```
```cpp
#include <linux/netlink.h>
#include <cstdint>

// Ідіоматична ініціалізація заголовка nlmsghdr у C++20
constexpr uint32_t req_seq = 1001;
nlmsghdr nlh{
    .nlmsg_len = NLMSG_LENGTH(0),
    .nlmsg_type = RTM_GETLINK,
    .nlmsg_flags = NLM_F_REQUEST | NLM_F_DUMP,
    .nlmsg_seq = req_seq,
    .nlmsg_pid = 0
};
```
:::

### Двійкова розкладка пам'яті заголовка `nlmsghdr`

Нижче наведено схему розташування полів у пам'яті з урахуванням вирівнювання:

| Зсув (байтори) | Поле | Тип даних | Призначення та семантика |
| :--- | :--- | :--- | :--- |
| `0x00` | `nlmsg_len` | `__u32` (4 байти) | Загальний розмір пакета з заголовком, навантаженням та атрибутами. |
| `0x04` | `nlmsg_type` | `__u16` (2 байти) | Стандартний тип контролю (`NLMSG_*`) або специфічний тип (`RTM_*`). |
| `0x06` | `nlmsg_flags` | `__u16` (2 байти) | Комбінація прапорців `NLM_F_*`. |
| `0x08` | `nlmsg_seq` | `__u32` (4 байти) | Порядковий номер для зіставлення запитів із відповідями. |
| `0x0C` | `nlmsg_pid` | `__u32` (4 байти) | Порт призначення/джерела (0 — ядро; PID процесу або унікальний ідентифікатор). |

## Базові макроси вирівнювання та обходу NLMSG_*

Оскільки повідомлення Netlink вирівнюються за межою 4 байтів (`NLMSG_ALIGNTO = 4U`), для безпечної роботи з вказівниками та обходу потоку дейтаграм у ядрі та користувацькому просторі застосовуються спеціальні системні макроси.

Математична форматування вирівнювання описується формулою:

```
NLMSG_ALIGN(len) = (((len) + 3) & ~3)
```

Системні макроси файлу `<linux/netlink.h>` визначаються так:

:::tabs
```c
#define NLMSG_ALIGNTO   4U
#define NLMSG_ALIGN(len) (((len)+NLMSG_ALIGNTO-1) & ~(NLMSG_ALIGNTO-1))
#define NLMSG_HDRLEN     ((int) NLMSG_ALIGN(sizeof(struct nlmsghdr)))
#define NLMSG_LENGTH(len) ((len) + NLMSG_HDRLEN)
#define NLMSG_SPACE(len) NLMSG_ALIGN(NLMSG_LENGTH(len))
#define NLMSG_DATA(nlh)  ((void*)(((char*)nlh) + NLMSG_LENGTH(0)))
#define NLMSG_NEXT(nlh,len) ((len) -= NLMSG_ALIGN((nlh)->nlmsg_len), \
                            (struct nlmsghdr*)(((char*)(nlh)) + NLMSG_ALIGN((nlh)->nlmsg_len)))
#define NLMSG_OK(nlh,len) ((len) >= (int)sizeof(struct nlmsghdr) && \
                           (nlh)->nlmsg_len >= sizeof(struct nlmsghdr) && \
                           (nlh)->nlmsg_len <= (len))
#define NLMSG_PAYLOAD(nlh,len) ((nlh)->nlmsg_len - NLMSG_SPACE((len)))
```
```cpp
#include <linux/netlink.h>
#include <span>
#include <cstdint>

// C++20 обгортки та constexpr-функції замість макросів препроцесора
namespace netlink {
    constexpr size_t AlignTo = 4;

    [[nodiscard]] constexpr size_t align(size_t len) noexcept {
        return (len + AlignTo - 1) & ~(AlignTo - 1);
    }

    [[nodiscard]] inline std::span<const uint8_t> payload(const nlmsghdr* nlh) noexcept {
        auto data_ptr = reinterpret_cast<const uint8_t*>(nlh) + NLMSG_HDRLEN;
        size_t data_len = nlh->nlmsg_len > NLMSG_HDRLEN ? nlh->nlmsg_len - NLMSG_HDRLEN : 0;
        return {data_ptr, data_len};
    }
}
```
:::

### Детальна семантика макросів обходу:
* **`NLMSG_ALIGN(len)`**: Округлює довжину `len` до найближчого кратного 4 значення вгору за допомогою побітової операції І з інвертованою маскою.
* **`NLMSG_LENGTH(len)`**: Обчислює повну довжину повідомлення для навантаження розміром `len` байтів, додаючи вирівняний розмір заголовка `NLMSG_HDRLEN`.
* **`NLMSG_SPACE(len)`**: Повертає повний обсяг пам'яті з урахуванням вирівнювання кінця кадру, необхідний для розміщення повідомлення з навантаженням `len`.
* **`NLMSG_DATA(nlh)`**: Повертає вказівник `void*` на початок корисного навантаження, що лежить безпосередньо за заголовком `nlmsghdr`.
* **`NLMSG_NEXT(nlh, len)`**: Зсуває вказівник `nlh` на наступний заголовок `struct nlmsghdr` у тому ж буфері пам'яті та зменшує змінну залишку довжини `len` на вирівняний розмір поточного пакета.
* **`NLMSG_OK(nlh, len)`**: Інваріант перевірки безпеки читання. Повертає істину тільки тоді, коли залишок буфера `len` більший або дорівнює розміру заголовка, довжина пакета `nlmsg_len` не менша за розмір заголовка й не перевищує залишок пам'яті `len`.

## Стандартні типи повідомлень: `nlmsg_type`

Значення `nlmsg_type`, що є меншими за `NLMSG_MIN_TYPE` (`0x10`), зарезервовані під службові керуючі повідомлення ядра:

| Константа | Код | Призначення та семантика |
| :--- | :--- | :--- |
| `NLMSG_NOOP` | `0x1` | Порожнє повідомлення. Використовується для вирівнювання або тестування. Має бути проігнороване при обробці. |
| `NLMSG_ERROR` | `0x2` | Сповіщення про помилку або квитування ACK. Корисне навантаження містить структуру `struct nlmsgerr`. |
| `NLMSG_DONE` | `0x3` | Завершальний пакет потоку повідомлень, що складається з багатьох частин (multipart stream). |
| `NLMSG_OVERRUN` | `0x4` | Сповіщення про втрату даних через переповнення приймального буфера сокета у ядрі. |

### Структура помилки та квитування: `struct nlmsgerr`

При виникненні помилки під час виконання запиту (або при наявності прапорця `NLM_F_ACK`) ядро повертає пакет з типом `NLMSG_ERROR`, навантаження якого містить структуру `struct nlmsgerr`:

:::tabs
```c
struct nlmsgerr {
    int error;                /* Від'ємний код помилки (наприклад, -ENOENT, -EPERM), або 0 для успішного ACK */
    struct nlmsghdr msg;      /* Копія заголовка запиту, що спричинив помилку або підтвердження */
};
```
```cpp
#include <linux/netlink.h>
#include <system_error>
#include <iostream>

// Обробка nlmsgerr у C++ за допомогою std::error_code
void process_ack(const nlmsgerr& err) {
    if (err.error == 0) {
        std::cout << "Запит успішно підтверджено ядром (ACK)\n";
    } else {
        std::error_code ec(-err.error, std::generic_category());
        std::cerr << "Помилка виконання запиту: " << ec.message() << "\n";
    }
}
```
:::

У сучасних ядрах Linux (версії 4.12+) при встановленні прапорця `NLM_F_ACK_TLVS` до структури `struct nlmsgerr` додаються розширені TLV-атрибути помилки (Extended ACK):
* **`NLMSGERR_ATTR_MSG`**: Текстовий рядок у форматі UTF-8 з описом причини відмови ядра (наприклад, `"Invalid MAC address"`).
* **`NLMSGERR_ATTR_OFFS`**: 32-бітне число `__u32`, що вказує на точний зсув байта у вхідному запиті, де сталося порушення схеми або валідації.
* **`NLMSGERR_ATTR_COOKIE`**: Опціональний кукі-ідентифікатор обробника.

## Повна таблиця бітових прапорців: `nlmsg_flags`

Прапорці визначають семантику запиту та поведінку ядра при обробці:

| Прапорець | Значення | Режим | Призначення та семантика |
| :--- | :--- | :--- | :--- |
| `NLM_F_REQUEST` | `0x01` | Загальний | Обов'язковий прапорець для всіх запитів від простору користувача до ядра. |
| `NLM_F_MULTI` | `0x02` | Загальний | Вказує, що відповідь складається з кількох частин і завершується пакетом `NLMSG_DONE`. |
| `NLM_F_ACK` | `0x04` | Загальний | Вимагає від ядра надсилання підтвердження `NLMSG_ERROR` (з `error = 0`) при успіху. |
| `NLM_F_ECHO` | `0x08` | Загальний | Вимагає від ядра трансляції цього запиту іншим слухачам мультикасту. |
| `NLM_F_DUMP_INTR` | `0x10` | Загальний | Вказує, що вивантаження дампа було перервано зміною послідовності таблиці. |
| `NLM_F_DUMP_FILTERED`| `0x20` | Загальний | Вказує, що вивантаження дампа було відфільтровано на боці ядра. |
| `NLM_F_ROOT` | `0x100` | GET-Запит | Повернути всю таблицю об'єктів (використовується для запиту дампа). |
| `NLM_F_MATCH` | `0x200` | GET-Запит | Повернути всі записи, що відповідають заданому критерію фільтрації. |
| `NLM_F_ATOMIC` | `0x400` | GET-Запит | Повернути атомарний зріз таблиці (застаріле). |
| `NLM_F_DUMP` | `0x300` | GET-Запит | Стандартний прапорець вивантаження дампа (`NLM_F_ROOT \| NLM_F_MATCH`). |
| `NLM_F_REPLACE` | `0x100` | NEW-Запит | Замінити наявний об'єкт новим. |
| `NLM_F_EXCL` | `0x200` | NEW-Запит | Не замінювати об'єкт, якщо він уже існує (повернути помилку `-EEXIST`). |
| `NLM_F_CREATE` | `0x400` | NEW-Запит | Створити об'єкт у ядрі, якщо він відсутній у системі. |
| `NLM_F_APPEND` | `0x800` | NEW-Запит | Додати новий об'єкт у кінець існуючого списку. |

## Структури TLV-атрибутів: struct nlattr та struct rtattr

Корисне навантаження повідомлень Netlink після специфічного заголовка підсистеми кодується у вигляді послідовності атрибутів Type-Length-Value (TLV).

### Сучасна структура атрибута: `struct nlattr`

Використовується в Generic Netlink та сучасних підсистемах ядра (`<linux/netlink.h>`):

:::tabs
```c
struct nlattr {
    __u16 nla_len;   /* Довжина атрибута (включаючи заголовок nlattr) */
    __u16 nla_type;  /* Тип атрибута та бітові прапорці NLA_F_* */
};
```
```cpp
#include <linux/netlink.h>
#include <cstdint>

// Створення та обробка структури nlattr у C++20
constexpr uint16_t type_mask = NLA_TYPE_MASK;
nlattr nla{
    .nla_len = NLA_HDRLEN,
    .nla_type = IFLA_IFNAME & type_mask
};
```
:::

Поле `nla_type` містить ідентифікатор типу в молодших 14 бітах. Старші два біти виконують роль службових прапорців:
* **`NLA_F_NESTED`** (`0x8000`): Вказує, що вмістом цього атрибута є вкладений список інших структур `struct nlattr`.
* **`NLA_F_NET_BYTEORDER`** (`0x4000`): Вказує, що двійкові дані атрибута записано у мережевому порядку байтів (Big-Endian).

### Системні макроси NLA_* для `struct nlattr`:

:::tabs
```c
#define NLA_ALIGNTO     4
#define NLA_ALIGN(len)  (((len) + NLA_ALIGNTO - 1) & ~(NLA_ALIGNTO - 1))
#define NLA_HDRLEN      ((int) NLA_ALIGN(sizeof(struct nlattr)))
#define NLA_DATA(nla)   ((void *)((char *)(nla) + NLA_HDRLEN))
#define NLA_PAYLOAD(nla) ((int)((nla)->nla_len - NLA_HDRLEN))
#define NLA_NEXT(nla,len) ((len) -= NLA_ALIGN((nla)->nla_len), \
                          (struct nlattr *)(((char *)(nla) + NLA_ALIGN((nla)->nla_len))))
#define NLA_OK(nla,len) ((len) >= (int)sizeof(struct nlattr) && \
                         (nla)->nla_len >= sizeof(struct nlattr) && \
                         (nla)->nla_len <= (len))
```
```cpp
#include <linux/netlink.h>
#include <string_view>
#include <span>
#include <cstdint>

// Безпечний парсинг NLA-атрибутів у C++20 через std::string_view та std::span
namespace netlink {
    [[nodiscard]] inline std::string_view get_string_attr(const nlattr* nla) noexcept {
        auto data = reinterpret_cast<const char*>(nla) + NLA_HDRLEN;
        auto len = static_cast<size_t>(NLA_PAYLOAD(nla));
        if (len > 0 && data[len - 1] == '\0') --len; // відкидаємо термінатор null
        return {data, len};
    }
}
```
:::

### Типи даних даних атрибутів у полі `nla_type`

Підсистеми ядра використовують декларативну політики `nla_policy` для перевірки типів даних:
* **`NLA_U8`, `NLA_U16`, `NLA_U32`, `NLA_U64`**: Беззнакові цілі числа відповідної розрядності.
* **`NLA_STRING` / `NLA_NUL_STRING`**: Текстові рядки, за якими обов'язково слідує нульовий символ термінації `\0`.
* **`NLA_BINARY`**: Сирий двійковий масив байтів заданого максимального розміру.
* **`NLA_FLAG`**: Логічний атрибут. Присутість атрибута означає `true`, відсутність — `false`.
* **`NLA_NESTED`**: Контейнер вкладених атрибутів.

### Застаріла структура атрибута rtnetlink: `struct rtattr`

Використовується у класичних викликах підсистеми `NETLINK_ROUTE` (`<linux/rtnetlink.h>`):

:::tabs
```c
struct rtattr {
    unsigned short rta_len;  /* Довжина атрибута з заголовком rtattr */
    unsigned short rta_type; /* Тип атрибута (IFLA_*, IFA_*, RTA_*) */
};
```
```cpp
#include <linux/rtnetlink.h>
#include <cstdint>

// Ініціалізація структури rtattr у C++20
constexpr uint16_t attr_type = IFLA_ADDRESS;
rtattr rta{
    .rta_len = RTA_HDRLEN,
    .rta_type = attr_type
};
```
:::

Макроси `RTA_ALIGN`, `RTA_LENGTH`, `RTA_SPACE`, `RTA_DATA`, `RTA_NEXT`, `RTA_OK` працюють ідентично до відповідних макросів `NLA_*`.

## Заголовки підсистем rtnetlink

Для протоколу `NETLINK_ROUTE` корисне навантаження починається зі специфічної структури підсистеми ядра, за якою розташовуються динамічні атрибути `rtattr`.

### 1. Інформація про мережевий інтерфейс: `struct ifinfomsg`

Використовується для команд `RTM_NEWLINK`, `RTM_DELLINK`, `RTM_GETLINK`, `RTM_SETLINK`:

:::tabs
```c
struct ifinfomsg {
    unsigned char  ifi_family; /* Сімейство адреси (AF_UNSPEC) */
    unsigned short ifi_type;   /* Тип обладнання ARPHRD_* (ARPHRD_ETHER, ARPHRD_LOOPBACK, ARPHRD_PPP) */
    int            ifi_index;  /* Унікальний числовий індекс інтерфейсу (ifindex) */
    unsigned int   ifi_flags;  /* Прапорці пристрою (IFF_UP, IFF_BROADCAST, IFF_RUNNING, IFF_PROMISC) */
    unsigned int   ifi_change; /* Маска змін прапорців (зарезервовано для запитів модифікації) */
};
```
```cpp
#include <linux/rtnetlink.h>
#include <net/if.h>

// Створення ifinfomsg для модифікації стану каналу у C++20
ifinfomsg ifi{
    .ifi_family = AF_UNSPEC,
    .ifi_type = ARPHRD_ETHER,
    .ifi_index = 2,
    .ifi_flags = IFF_UP,
    .ifi_change = IFF_UP
};
```
:::

Повний список ключових атрибутів `IFLA_*` після `ifinfomsg`:
* `IFLA_IFNAME`: Рядок `char*` із текстовою назвою мережевого інтерфейсу (наприклад, `"eth0"` чи `"wlan0"`).
* `IFLA_ADDRESS`: Двійковий масив L2-адреси пристрою (наприклад, 6 байтів MAC-адреси Ethernet).
* `IFLA_BROADCAST`: Двійковий масив L2-широкоповіщальної адреси.
* `IFLA_MTU`: 32-бітне число `__u32` з розміром максимального блоку передачі (MTU у байтах).
* `IFLA_OPERSTATE`: 8-бітний стан каналу (`IF_OPER_UP`, `IF_OPER_DOWN`, `IF_OPER_TESTING`, `IF_OPER_UNKNOWN`).
* `IFLA_LINKMODE`: Режим роботи каналу (`0` — стандартний, `1` — dormancy).
* `IFLA_LINKINFO`: Вкладений атрибут (`NLA_F_NESTED`), який описує драйвер віртуального пристрою (`IFLA_INFO_KIND`: `"vlan"`, `"bridge"`, `"veth"`, `"bond"`, `"vxlan"`).

### 2. Інформація про IP-адресу: `struct ifaddrmsg`

Використовується для команд `RTM_NEWADDR`, `RTM_DELADDR`, `RTM_GETADDR`:

:::tabs
```c
struct ifaddrmsg {
    unsigned char ifa_family;    /* Сімейство адреси (AF_INET або AF_INET6) */
    unsigned char ifa_prefixlen; /* Довжина префікса маски мережі у форматі CIDR (наприклад, 24) */
    unsigned char ifa_flags;     /* Прапорці адреси (IFA_F_SECONDARY, IFA_F_PERMANENT, IFA_F_NOPREFIXROUTE) */
    unsigned char ifa_scope;     /* Область видимості адреси (RT_SCOPE_UNIVERSE, RT_SCOPE_LINK, RT_SCOPE_HOST) */
    unsigned int  ifa_index;     /* Числовий індекс мережевого інтерфейсу ifindex */
};
```
```cpp
#include <linux/rtnetlink.h>
#include <sys/socket.h>

// Ініціалізація ifaddrmsg у C++20
ifaddrmsg ifa{
    .ifa_family = AF_INET6,
    .ifa_prefixlen = 64,
    .ifa_flags = IFA_F_PERMANENT,
    .ifa_scope = RT_SCOPE_UNIVERSE,
    .ifa_index = 3
};
```
:::

Основні атрибути `IFA_*` після `ifaddrmsg`:
* `IFA_ADDRESS`: IP-адреса інтерфейсу (`struct in_addr` для IPv4 або `struct in6_addr` для IPv6).
* `IFA_LOCAL`: Локальна IP-адреса (для p2p-з'єднань точка-точка).
* `IFA_LABEL`: Текстова мітка інтерфейсного псевдоніма (наприклад, `"eth0:1"`).
* `IFA_BROADCAST`: Широкоповіщальна IP-адреса мережі.
* `IFA_CACHEINFO`: Структура `struct ifa_cacheinfo`, що містить дані про час життя тимчасової адреси IPv6 (preferred та valid lifetime у секундах).

### 3. Інформація про маршрут: `struct rtmsg`

Використовується для команд `RTM_NEWROUTE`, `RTM_DELROUTE`, `RTM_GETROUTE`:

:::tabs
```c
struct rtmsg {
    unsigned char rtm_family;   /* AF_INET або AF_INET6 */
    unsigned char rtm_dst_len;  /* Довжина маски призначення в бітах (CIDR) */
    unsigned char rtm_src_len;  /* Довжина маски джерела в бітах */
    unsigned char rtm_tos;      /* Тип обслуговування (Type of Service) */
    unsigned char rtm_table;    /* ID таблиці маршрутизації (RT_TABLE_MAIN, RT_TABLE_LOCAL, RT_TABLE_DEFAULT) */
    unsigned char rtm_protocol; /* Джерело маршруту (RTPROT_BOOT, RTPROT_STATIC, RTPROT_BGP, RTPROT_KERNEL) */
    unsigned char rtm_scope;    /* Область видимості маршруту (RT_SCOPE_UNIVERSE, RT_SCOPE_LINK, RT_SCOPE_NOWHERE) */
    unsigned char rtm_type;     /* Тип маршруту (RTN_UNICAST, RTN_LOCAL, RTN_BROADCAST, RTN_BLACKHOLE) */
    unsigned int  rtm_flags;    /* Прапорці маршрутизації RTM_F_* */
};
```
```cpp
#include <linux/rtnetlink.h>
#include <sys/socket.h>

// Створення заповненої структури rtmsg у C++20
rtmsg rtm{
    .rtm_family = AF_INET,
    .rtm_dst_len = 24,
    .rtm_src_len = 0,
    .rtm_tos = 0,
    .rtm_table = RT_TABLE_MAIN,
    .rtm_protocol = RTPROT_STATIC,
    .rtm_scope = RT_SCOPE_LINK,
    .rtm_type = RTN_UNICAST,
    .rtm_flags = 0
};
```
:::

Основні атрибути `RTA_*` після `rtmsg`:
* `RTA_DST`: IP-адреса призначення цільової мережі.
* `RTA_SRC`: IP-адреса джерела.
* `RTA_GATEWAY`: IP-адреса шлюзу за замовчуванням (Next Hop).
* `RTA_OIF`: 32-бітний індекс вихідного мережевого інтерфейсу (`ifindex`).
* `RTA_PRIORITY`: Метрика (вага) маршруту для вибору шляху планувальником.
* `RTA_PREFSRC`: Переважна адреса джерела при відправці пакетів за цим маршрутом.
* `RTA_MULTIPATH`: Вкладена структура для маршрутизації з кількома вихідними шляхами (Equal-Cost Multi-Path, ECMP).

### 4. Інформація про сусідні вузли (ARP / NDP): `struct ndmsg`

Використовується для команд `RTM_NEWNEIGH`, `RTM_DELNEIGH`, `RTM_GETNEIGH`:

:::tabs
```c
struct ndmsg {
    unsigned char ndm_family;   /* AF_INET або AF_INET6 */
    int           ndm_ifindex;  /* Індекс мережевого інтерфейсу */
    __u16         ndm_state;    /* Стан ARP/NDP таблиці (NUD_REACHABLE, NUD_FAILED, NUD_STALE) */
    __u8          ndm_flags;    /* Прапорці (NTF_PROXY, NTF_ROUTER) */
    __u8          ndm_type;     /* Тип сусіда (RTN_UNICAST) */
};
```
```cpp
#include <linux/rtnetlink.h>
#include <sys/socket.h>

// Ініціалізація структури ndmsg для запиту ARP/NDP у C++20
ndmsg ndm{
    .ndm_family = AF_INET,
    .ndm_ifindex = 1,
    .ndm_state = NUD_REACHABLE,
    .ndm_flags = NTF_PROXY,
    .ndm_type = RTN_UNICAST
};
```
:::

Основні атрибути `NDA_*`: `NDA_DST` (IP-адреса сусіда), `NDA_LLADDR` (аппартна MAC-адреса сусіда), `NDA_CACHEINFO` (статистика часу життя запису кешу ARP).

## Заголовок Generic Netlink: struct genlmsghdr

При використанні домену `NETLINK_GENERIC` за заголовком `struct nlmsghdr` іде заголовок розширюваної шини `struct genlmsghdr` (`<linux/genetlink.h>`):

:::tabs
```c
struct genlmsghdr {
    __u8 cmd;      /* Внутрішній код команди сімейства (наприклад, CTRL_CMD_GETFAMILY) */
    __u8 version;  /* Версія API підсистеми */
    __u16 reserved;/* Зарезервовано для вирівнювання */
};
```
```cpp
#include <linux/genetlink.h>
#include <cstdint>

// Ініціалізація заголовка Generic Netlink genlmsghdr у C++20
constexpr uint8_t ctrl_ver = 2;
genlmsghdr gnl{
    .cmd = CTRL_CMD_GETFAMILY,
    .version = ctrl_ver,
    .reserved = 0
};
```
:::

### Атрибути контролера Generic Netlink (`nlctrl`)

Контролер `nlctrl` використовує атрибути `CTRL_ATTR_*` для передачі параметрів реєстрації сімейств:
* `CTRL_ATTR_FAMILY_ID`: 16-бітний динамічний ідентифікатор сімейства.
* `CTRL_ATTR_FAMILY_NAME`: Текстовий рядок з назвою сімейства (наприклад, `"nl80211"`).
* `CTRL_ATTR_VERSION`: Версія реалізації сімейства в ядрі.
* `CTRL_ATTR_MAXATTR`: Максимальна кількість атрибутів, що підтримуються сімейством.
* `CTRL_ATTR_MCAST_GROUPS`: Вкладений список мультикаст-груп, зареєстрованих даним сімейством.
