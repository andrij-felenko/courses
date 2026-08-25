# 📋 Інтерфейс підсистеми маршрутизації: rtnetlink, структури ядра fib_info та /proc/net/fib_trie

Мережева підсистема ядра Linux надає чітко розмежований набір програмних інтерфейсів для взаємодії з підсистемою маршрутизації. Усі операції з додавання, вилучення, модифікації та моніторингу маршрутів і правил маршрутизації здійснюються користувацькими утилітами (такими як `iproute2`, `FRRouting`, `BIRD`) через сокети розширеної взаємодії **RTNETLINK**. Усередині ядра рішення про маршрутизацію спирається на взаємопов'язану систему C-структур (`fib_table`, `key_vector`, `fib_alias`, `fib_info`), а поточний стан префіксного дерева експортується в простір користувача через файли віртуальної файлової системи `/proc/net/fib_trie` та `/proc/net/fib_triestat`. Ця вставка містить вичерпний довідник структур даних, бітових прапорів, типів повідомлень Netlink та дрібниць їхньої інтерпретації.

---

## 1. Протокол RTNETLINK: Повідомлення та структури маршрутизації

Протокол Netlink розробено як заміну застарілим системним викликам `ioctl()` та файлам `/proc`. На відміну від `ioctl()`, який вимагав лінійного опису фіксованих структур, Netlink побудований на асинхронній передачі повідомлень, вирівняних за 4-байтовою межею, з підтримкою розширюваних атрибутів TLV (Type-Length-Value).

Для управління маршрутами та правилами PBR у користувацькому просторі створюється сокет Netlink сімейства `AF_NETLINK` з типом `NETLINK_ROUTE`.

:::tabs
```c
int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
```
```cpp
// Ідіоматична C++ RAII-обгортка із генерацією виключення std::system_error
namespace net {
    class NetlinkSocket {
    public:
        NetlinkSocket() {
            fd_ = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
            if (fd_ < 0) {
                throw std::system_error(errno, std::generic_category(), "Не вдалося створити сокет Netlink");
            }
        }
        ~NetlinkSocket() { if (fd_ >= 0) ::close(fd_); }
        [[nodiscard]] int native_handle() const noexcept { return fd_; }
    private:
        int fd_{-1};
    };
}
```
:::

Кожен пакет, який надсилається або отримується через цей сокет, починається зі стандартного заголовка `struct nlmsghdr`. За цим заголовком слідує специфічний для маршрутизації заголовок `struct rtmsg`, після якого розміщується довільна кількість вкладених атрибутів `struct rtattr`.

### Розшифровка прапорців заголовка Netlink (`nlmsg_flags`)

Поле `nlmsg_flags` у заголовку `struct nlmsghdr` визначає семантику виконання запиту та поведінку ядра:

* `NLM_F_REQUEST`: Обов'язковий прапорець для всіх повідомлень, що надсилаються з користувацького простору в ядро.
* `NLM_F_MULTI`: Вказує, що відповідь ядра складається з багатьох послідовних пакетів, які завершуються повідомленням `NLMSG_DONE`.
* `NLM_F_ACK`: Вимагає від ядра надсилання підтвердження виконання операції (повідомлення `NLMSG_ERROR` із кодом помилки `0` при успіху або кодом POSIX при помилці).
* `NLM_F_ECHO`: Вимагає від ядра віддзеркалити згенероване сповіщення про зміну об'єкта назад на сокет-відправник.
* `NLM_F_ROOT` та `NLM_F_MATCH`: Використовуються разом із `RTM_GETROUTE` для вивантаження всієї таблиці маршрутизації (дамп FIB).
* `NLM_F_REPLACE`: Дозволяє замінити існуючий маршрут із тим самим префіксом.
* `NLM_F_EXCL`: Повертає помилку `EEXIST`, якщо створюваний маршрут вже присутній у таблиці.
* `NLM_F_CREATE`: Створює новий маршрут, якщо він відсутній у таблиці.
* `NLM_F_APPEND`: Додає новий маршрут у кінець списку варіантів префіксу.

### Основні типи повідомлень (Header Types)

При роботі з маршрутизацією використовуються наступні основні коди повідомлень у полі `nlmsg_type`:

* `RTM_NEWROUTE`: Надсилається з простору користувача в ядро для створення нового маршруту. Якщо маршрут з такими самими параметрами вже існує і прапорець `NLM_F_EXCL` не встановлено, ядро оновлює існуючий маршрут. Також це повідомлення розсилається ядром через сокет мультикасту всім демонам моніторингу при зміні таблиць.
* `RTM_DELROUTE`: Виклики для вилучення маршруту з FIB. Ядро знаходить відповідний запис за префіксом і маскою та вилучає його з префіксного дерева LC-Trie.
* `RTM_GETROUTE`: Використовується для двох цілей: зчитування всієї таблиці маршрутизації (при встановленні прапорця `NLM_F_DUMP`) або для виконання тестового опитування FIB для однієї конкретної IP-адреси призначення.
* `RTM_NEWRULE`: Додавання нового правила політики маршрутизації в базу RPDB (`ip rule add`).
* `RTM_DELRULE`: Вилучення правила з бази RPDB (`ip rule del`).
* `RTM_GETRULE`: Отримання повного переліку правил RPDB.

### Заголовок повідомлення маршруту: `struct rtmsg`

Кожне повідомлення типу `RTM_*ROUTE` містить заголовок `struct rtmsg` одразу після стандартного заголовка Netlink `struct nlmsghdr`:

:::tabs
```c
#include <linux/rtnetlink.h>

struct rtmsg {
    unsigned char rtm_family;   /* Сімейство адрес: AF_INET (IPv4) або AF_INET6 (IPv6) */
    unsigned char rtm_dst_len;  /* Довжина маски префіксу призначення (0..32 для IPv4) */
    unsigned char rtm_src_len;  /* Довжина маски префіксу джерела (зазвичай 0) */
    unsigned char rtm_tos;      /* Type of Service (ToS) / DSCP */
    unsigned char rtm_table;    /* ID таблиці маршрутизації (RT_TABLE_MAIN, RT_TABLE_LOCAL тощо) */
    unsigned char rtm_protocol; /* Протокол, що створив маршрут (RTPROT_STATIC, BGP тощо) */
    unsigned char rtm_scope;    /* Область видимості маршруту (RT_SCOPE_UNIVERSE тощо) */
    unsigned char rtm_type;     /* Тип маршруту (RTN_UNICAST, RTN_LOCAL тощо) */
    unsigned unsigned rtm_flags;/* Допоміжні прапорці (RTM_F_CLONED, RTM_F_FIB_MATCH) */
};
```
```cpp
#include <linux/rtnetlink.h>
#include <cstdint>

// Обгортка заголовка rtmsg з ініціалізацією полів у C++20
namespace net {
    struct RtMsg {
        std::uint8_t family{AF_INET};    /* Сімейство адрес (AF_INET або AF_INET6) */
        std::uint8_t dst_len{0};         /* Довжина маски префіксу призначення */
        std::uint8_t src_len{0};         /* Довжина маски префіксу джерела */
        std::uint8_t tos{0};             /* Type of Service (ToS) / DSCP */
        std::uint8_t table{RT_TABLE_MAIN};/* ID таблиці маршрутизації */
        std::uint8_t protocol{RTPROT_STATIC};/* Протокол джерела (BGP, Static) */
        std::uint8_t scope{RT_SCOPE_UNIVERSE};/* Область видимості */
        std::uint8_t type{RTN_UNICAST};  /* Тип маршруту (RTN_UNICAST тощо) */
        std::uint32_t flags{0};          /* Допоміжні прапорці */
    };
}
```
:::

Поле `rtm_family` визначає мережевий протокол. Для IPv4 це значення дорівнює `AF_INET` (2), для IPv6 — `AF_INET6` (10).

Поле `rtm_dst_len` вказує кількість маскованих біт у префіксі призначення. Для безадресного маршруту за замовчуванням (`default route`) це значення дорівнює `0`. Для конкретного хоста (`/32` в IPv4 або `/128` в IPv6) це значення дорівнює `32` або `128`.

Поле `rtm_table` містить числовий ідентифікатор таблиці. Оскільки це поле має розмір 1 байт, воно може кодувати лише значення від 0 до 255. Якщо ідентифікатор таблиці перевищує 255 (наприклад, користувацька таблиця 1000), у полі `rtm_table` записується `RT_TABLE_COMPAT` (252), а справжній 32-бітний ID додається через атрибут `RTA_TABLE`.

#### Повний перелік типів маршрутів (`rtm_type`)

Тип маршруту визначає семантику обробки пакета після того, як його адреса призначення збіглася з даним записом у FIB:

* `RTN_UNICAST` (1): Стандартний транзитний або шлюзовий маршрут. Пакет повинен бути перенаправлений через вихідний мережевий інтерфейс на вказаний next-hop.
* `RTN_LOCAL` (2): IP-адреса належить одному з локальних інтерфейсів самого хоста. Пакет передається вхідному стеку протоколів L4 (TCP/UDP/ICMP).
* `RTN_BROADCAST` (3): широкомовна адреса підмережі. Пакет приймається локально та надсилається як L2-широкомовний кадр.
* `RTN_ANYCAST` (4): Адреса будь-якого мовлення, що належить даній машині.
* `RTN_MULTICAST` (5): Багатоадресна група (адреси діапазону 224.0.0.0/4).
* `RTN_BLACKHOLE` (6): Пакет підлягає мовчазному знищенню (Drop). Жодні ICMP-повідомлення про помилку відправнику не надсилаються.
* `RTN_UNREACHABLE` (7): Пакет скидається, а відправнику надсилається ICMP-повідомлення `Destination Unreachable` (Type 3, Code 1).
* `RTN_PROHIBITED` (8): Пакет скидається, а відправнику надсилається ICMP-повідомлення `Communication Administratively Prohibited` (Type 3, Code 13).
* `RTN_THROW` (9): Спеціальний внутрішній тип для PBR. Якщо пошук у поточній таблиці дає збіг з маршрутом `THROW`, ядро припиняє пошук у цій таблиці, ігнорує подальші маршрути і повертається в базу RPDB для переходу до наступного правила `ip rule`.

#### Область видимості маршруту (`rtm_scope`)

Область видимості (Scope) вказує відстань до призначення і відіграє критичну роль при виборі локальної IP-адреси джерела (`src IP`) для вихідних пакетів:

* `RT_SCOPE_UNIVERSE` (0): Глобальний маршрут. Призначення знаходиться за межами локальної L2-мережі, доступ до нього здійснюється через один або кілька шлюзів (маршрутизаторів).
* `RT_SCOPE_SITE` (200): Маршрут обмежений локальною автоновною системою чи сайтом (зараз практично не використовується).
* `RT_SCOPE_LINK` (253): Маршрут прямого зв'язку. Призначення знаходиться в безпосередньо підключеній L2-мережі (наприклад, адреса в мережі `192.168.1.0/24`, підключеній до `eth0`). Шлюз для таких маршрутів відсутній (`gateway = 0.0.0.0`).
* `RT_SCOPE_HOST` (254): Маршрут обмежений даним хостом. Використовується для loopback-інтерфейсу (`lo`) та власної IP-адреси хоста.
* `RT_SCOPE_NOWHERE` (255): Маршрут нікуди не веде.

#### Джерело створення маршруту (`rtm_protocol`)

Поле `rtm_protocol` дозволяє розділити маршрути за їхнім походженням, що унеможливлює випадкове перезаписування маршрутів одного демона іншим:

* `RTPROT_UNSPEC` (0): Джерело не вказано.
* `RTPROT_KERNEL` (2): Маршрут створено автоматично ядром Linux під час присвоєння IP-адреси інтерфейсу та його переведення в стан UP.
* `RTPROT_BOOT` (3): Маршрут створено під час завантаження системи.
* `RTPROT_STATIC` (4): Статичний маршрут, доданий адміністратором через команду `ip route add`.
* `RTPROT_GATED` (8): Маршрут створено демоном GateD.
* `RTPROT_RA` (9): Маршрут отримано через IPv6 Router Advertisement.
* `RTPROT_BGP` (186): Маршрут отримано від протоколу BGP демонами FRRouting, BIRD або GoBGP.
* `RTPROT_OSPF` (188): Маршрут отримано від протоколу OSPF.
* `RTPROT_BABEL` (42): Маршрут протоколу Babel.

---

### Атрибути Netlink для маршрутів (Routing Attributes: `rtattr`)

Після структури `struct rtmsg` у повідомленні Netlink розташовується послідовність атрибутів `struct rtattr` типу TLV (Type-Length-Value). Кожен атрибут повинен вирівнюватися за 4-байтовою межею за допомогою макроса `RTA_ALIGN()`.

:::tabs
```c
struct rtattr {
    unsigned short rta_len;  /* Довжина атрибута з урахуванням заголовка */
    unsigned short rta_type; /* Тип атрибута (RTA_*) */
};
```
```cpp
#include <cstdint>

// Атрибут Netlink (TLV) у форматі C++20 з типовою безпекою
namespace net {
    struct RtAttr {
        std::uint16_t len{0};  /* Довжина атрибута з урахуванням заголовка */
        std::uint16_t type{0}; /* Тип атрибута (RTA_*) */
    };
}
```
:::

#### Повний перелік типів атрибутів (`rta_type`)

* `RTA_DST`: IP-адреса призначення префіксу. Для IPv4 містить 4 байти (`struct in_addr`), для IPv6 — 16 байт (`struct in6_addr`).
* `RTA_SRC`: IP-адреса джерела префіксу.
* `RTA_GATEWAY`: IP-адреса шлюзу (Next-Hop).
* `RTA_OIF`: 32-бітний індекс вихідного мережевого інтерфейсу (`int ifindex`).
* `RTA_IIF`: 32-бітний індекс вхідного мережевого інтерфейсу.
* `RTA_PRIORITY`: Метрика/пріоритет маршруту (`u32`). Якщо для одного префіксу існує кілька маршрутів з однаковою довжиною маски, ядро вибирає маршрут з найменшим значенням `RTA_PRIORITY`.
* `RTA_PREFSRC`: Переважна адреса джерела (Preferred Source IP). Коли локальний застосунок викликає `connect()` без попереднього `bind()`, ядро бере IP-адресу з цього атрибута для підстави у заголовок пакета.
* `RTA_METRICS`: Вкладені атрибути метрик TCP/IP. Містить внутрішній TLV масив типу `RTAX_*`:
  * `RTAX_MTU`: Фіксоване значення Path MTU для маршруту.
  * `RTAX_WINDOW`: Розмір вікна TCP за замовчуванням.
  * `RTAX_RTT` / `RTAX_RTTVAR`: Початкова оцінка RTT (Round Trip Time) для прискорення старту TCP.
  * `RTAX_SSTHRESH`: Початковий поріг повільного старту TCP (Slow Start Threshold).
  * `RTAX_ADVMSS`: Переважне значення Maximum Segment Size (MSS).
  * `RTAX_INITCWND`: Початкове вікно конгестії TCP (Initial Congestion Window).
* `RTA_TABLE`: 32-бітний ідентифікатор таблиці маршрутизації.
* `RTA_MULTIPATH`: Вкладений масив структур `struct rtnexthop` для опису багатошляхової маршрутизації (ECMP — Equal-Cost Multi-Path).
* `RTA_PREF`: Перевага маршруту IPv6 (ICMPv6 Router Preference: Low, Medium, High).
* `RTA_ENCAP_TYPE` та `RTA_ENCAP`: Опис тунелювання для інкапсуляції пакетів (MPLS, VXLAN, SEG6, LWTUNNEL).

#### Структура багатошляхового next-hop: `struct rtnexthop`

При використанні ECMP (багатошляхової маршрутизації з однаковою вартістю) атрибут `RTA_MULTIPATH` містить один або декілька блоків `struct rtnexthop`:

:::tabs
```c
struct rtnexthop {
    unsigned short rtnh_len;     /* Довжина структури разом з її під-атрибутами */
    unsigned char  rtnh_flags;   /* Прапорці (RTNH_F_DEAD, RTNH_F_LINKDOWN) */
    unsigned char  rtnh_hops;    /* Вага маршруту для балансування трафіку */
    int            rtnh_ifindex; /* Індекс вихідного інтерфейсу */
};
```
```cpp
#include <cstdint>

// Елемент ECMP next-hop у C++ з ініціалізацією членів
namespace net {
    struct RtNextHop {
        std::uint16_t len{0};     /* Довжина структури разом із під-атрибутами */
        std::uint8_t  flags{0};   /* Прапорці (RTNH_F_DEAD, RTNH_F_LINKDOWN) */
        std::uint8_t  hops{0};    /* Вага маршруту для балансування трафіку */
        std::int32_t  ifindex{0}; /* Індекс вихідного інтерфейсу */
    };
}
```
:::

Одразу після структури `struct rtnexthop` у пам'яті можуть іти вкладені атрибути `struct rtattr`, такі як `RTA_GATEWAY` саме для цього конкретного шлюзу.

---

## 2. Внутрішні структури даних ядра Linux (`include/net/ip_fib.h`)

Усередині ядра Linux підсистема FIB (Forwarding Information Base) оперує взаємопов'язаним графом C-структур. Головна мета цієї організації — виділення незмінних даних у спільні об'єкти для економії оперативної пам'яті та мінімізації промахів CPU-кешу.

```
struct fib_table
   └── struct trie (trie_node / key_vector)
         └── struct fib_alias
               └── struct fib_info
                     └── struct fib_nh_common (Next-Hop details)
```

### 1. `struct fib_table`
Представляє одну екземплярну таблицю маршрутизації (наприклад, `local` ID 255, `main` ID 254 або користувацьку таблицю VRF):

:::tabs
```c
struct fib_table {
    struct hlist_node tb_hlist;
    u32               tb_id;           /* Numeric Table ID (254 = MAIN, 255 = LOCAL) */
    int               tb_num_default;  /* Кількість дефолтних маршрутів у таблиці */
    struct rcu_head   rcu;
    unsigned long     tb_data[0];      /* Вказівник на дерево LC-Trie (struct trie) */
};
```
```cpp
#include <cstdint>

// Моделювання таблиці FIB у C++ з використанням C++17/20 типів
namespace net::kernel_sim {
    struct FibTable {
        std::uint32_t id{254};         /* Numeric Table ID (254 = MAIN, 255 = LOCAL) */
        std::int32_t  num_default{0};  /* Кількість дефолтних маршрутів у таблиці */
        uintptr_t     trie_ptr{0};     /* Вказівник на корінь дерева LC-Trie */
    };
}
```
:::

Таблиця реалізує інтерфейс віртуальних функцій через методи `tb_lookup()`, `tb_insert()`, `tb_delete()`, які в сучасних ядрах вказують безпосередньо на реалізацію LC-Trie у файлі `net/ipv4/fib_trie.c`.

### 2. `struct key_vector` (Вузол дерева LC-Trie)
У реалізації LC-Trie ядра Linux вузли розгалуження (Branch) та листки (Leaf) об'єднані у єдину компактну структуру `struct key_vector`:

:::tabs
```c
struct key_vector {
    t_key          key;        /* 32-бітне значення префіксу адреси */
    unsigned char  pos;        /* Позиція аналізованого біта (0..31 від старшого біта) */
    unsigned char  bits;       /* Кількість біт у даному рівні (stride size, k = 1..8) */
    unsigned char  slen;       /* Максимальна довжина суфіксу в піддереві */
    union {
        struct key_vector *tnode[0]; /* Масив з 2^bits вказівників на дочірні вузли (Branch) */
        struct hlist_head leaf;      /* Зв'язаний список об'єктів fib_alias (Leaf) */
    };
};
```
```cpp
#include <cstdint>
#include <variant>
#include <vector>

// Представлення вузла LC-Trie у C++ з використанням std::variant та std::vector
namespace net::kernel_sim {
    struct KeyVector {
        std::uint32_t key{0};     /* 32-бітне значення префіксу адреси */
        std::uint8_t  pos{0};     /* Позиція аналізованого біта (0..31) */
        std::uint8_t  bits{0};    /* Кількість біт у рівні (stride size, k = 1..8) */
        std::uint8_t  slen{0};    /* Максимальна довжина суфіксу піддерева */
        
        // Вузол розгалуження містить вектор дочірніх вузлів, а листок — списки маршрутів
        std::variant<std::vector<KeyVector*>, void*> node_data;
    };
}
```
:::

Поле `bits` виступає маркером типу вузла. Якщо `bits > 0`, це внутрішній вузол розгалуження (Internal Branch Node), який містить масив `tnode` розміром `2^bits` вказівників. Якщо `bits == 0`, це листок (Leaf Node), а поле `leaf` містить головний вузол зв'язаного списку `struct fib_alias`.

### 3. `struct fib_alias`
Листок префіксного дерева кодує лише мережевий префікс. Проте для одного й того самого префіксу (наприклад, `10.0.0.0/24`) можуть існувати кілька маршрутів із різною Type of Service (ToS) або різним пріоритетом. Опис кожного такого варіанта зберігається у структурі `struct fib_alias`:

:::tabs
```c
struct fib_alias {
    struct hlist_node fa_list;
    struct fib_info  *fa_info;      /* Вказівник на незмінні дані про next-hop */
    u8                fa_tos;       /* Type of Service */
    u8                fa_type;      /* Тип маршруту (RTN_UNICAST, RTN_LOCAL тощо) */
    u8                fa_state;     /* Внутрішній стан (FIB_ALIAS_SCHEDULED тощо) */
    u8                fa_slen;      /* Довжина маски префіксу (32 - prefix_length) */
    struct rcu_head   rcu;
};
```
```cpp
#include <cstdint>

// Запис fib_alias у C++ з підтримкою зв'язку з FibInfo
namespace net::kernel_sim {
    struct FibInfo; // Випереджувальне оголошення

    struct FibAlias {
        const FibInfo* info{nullptr}; /* Незмінні дані про next-hop */
        std::uint8_t   tos{0};        /* Type of Service */
        std::uint8_t   type{0};       /* Тип маршруту (RTN_UNICAST тощо) */
        std::uint8_t   state{0};      /* Внутрішній стан */
        std::uint8_t   slen{0};       /* Довжина маски префіксу (32 - prefix_length) */
    };
}
```
:::

Список `fa_list` відсортовано за спаданням довжини маски та пріоритету, що дозволяє ядру миттєво знаходити наиболее специфічний збіг під час обходу листка.

### 4. `struct fib_info`
Структура `struct fib_info` містить важку інформацію про шлюзи, вихідний інтерфейс, переважні IP-адреси джерела та метрики. 

Деталізація структури:

:::tabs
```c
struct fib_info {
    struct hlist_node   fib_hash;
    struct hlist_node   fib_lhash;
    atomic_t            fib_treeref;  /* Лічильник посилань від дерев маршрутизації */
    atomic_t            fib_clntref;  /* Лічильник посилань від сокетів/клієнтів */
    u32                 fib_metrics;  /* Метрики (MTU, rtt, window) */
    u32                 fib_priority; /* Метрика/пріоритет (RTA_PRIORITY) */
    u32                 fib_prefsrc;  /* Preferred Source IP */
    u32                 fib_flags;    /* Прапорці (RTNH_F_DEAD тощо) */
    unsigned char       fib_protocol; /* Протокол джерела (RTPROT_BGP тощо) */
    unsigned char       fib_nhs;      /* Кількість nexthops (для ECMP) */
    struct fib_nh_common fib_nh[0];   /* Масив структур наступного хопу */
};
```
```cpp
#include <cstdint>
#include <atomic>
#include <vector>

// Запис fib_info у C++ з використанням std::atomic та std::vector для next-hop структур
namespace net::kernel_sim {
    struct FibInfo {
        std::atomic<std::int32_t> treeref{0};  /* Атомарний лічильник посилань від дерев */
        std::atomic<std::int32_t> clntref{0};  /* Атомарний лічильник посилань від сокетів */
        std::uint32_t             metrics{0};  /* Метрики (MTU, rtt, window) */
        std::uint32_t             priority{0}; /* Метрика/пріоритет (RTA_PRIORITY) */
        std::uint32_t             prefsrc{0};  /* Preferred Source IP */
        std::uint32_t             flags{0};    /* Прапорці */
        std::uint8_t              protocol{0}; /* Протокол джерела */
        std::vector<std::uint32_t> nexthops;   /* Масив індексів nexthop */
    };
}
```
:::

Ядро Linux застосовує дедуплікацію `struct fib_info`. Якщо 50 000 різних префіксів BGP мають один і той самий next-hop шлюз (`192.168.1.1 dev eth0`), ядро створює **лише один екземпляр `struct fib_info`** у пам'яті. Усі 50 000 об'єктів `struct fib_alias` містять вказівник на цю єдину структуру, а лічильник `fib_treeref` дорівнює 50 000. Це економить десятки мегабайтів оперативної пам'яті на магістральних маршрутизаторах.

### 5. `struct fib_result`
Результат виконання функції `fib_lookup()` повертається у структурі `struct fib_result`. Вона виступає легковаговим контекстом рішення про маршрутизацію:

:::tabs
```c
struct fib_result {
    __be32          prefix;       /* Префікс адреси */
    unsigned char   prefixlen;    /* Довжина маски префіксу */
    unsigned char   nh_sel;       /* Обраний індекс next-hop у масиві ECMP */
    unsigned char   type;         /* Тип маршруту (RTN_UNICAST тощо) */
    unsigned char   scope;        /* Область видимості */
    u32             tclassid;     /* Клас трафіку для QOS */
    struct fib_info *fi;          /* Знайдена структура fib_info */
    struct fib_table *table;      /* Знайдена таблиця маршрутизації */
};
```
```cpp
#include <cstdint>

// Результат fib_lookup у C++ з явними типами та nullptr за замовчуванням
namespace net::kernel_sim {
    struct FibInfo;
    struct FibTable;

    struct FibResult {
        std::uint32_t   prefix{0};      /* Префікс адреси */
        std::uint8_t    prefixlen{0};   /* Довжина маски префіксу */
        std::uint8_t    nh_sel{0};      /* Обраний індекс next-hop у масиві ECMP */
        std::uint8_t    type{0};        /* Тип маршруту (RTN_UNICAST тощо) */
        std::uint8_t    scope{0};       /* Область видимості */
        std::uint32_t   tclassid{0};    /* Клас трафіку для QoS */
        const FibInfo*  fi{nullptr};    /* Знайдена структура FibInfo */
        const FibTable* table{nullptr}; /* Знайдена таблиця маршрутизації */
    };
}
```
:::

Макроси ядра для витягування параметрів з `struct fib_result`:
* `FIB_RES_DEV(res)`: Отримати вказівник на вихідний `struct net_device`.
* `FIB_RES_GW(res)`: Отримати IP-адресу шлюзу (`__be32`).
* `FIB_RES_PREFSRC(net, res)`: Отримати переважну адресу джерела.

---

## 3. Синхронізація RCU у підсистемі FIB

Усі маніпуляції з деревами LC-Trie та структурою `fib_table` спираються на механізм **RCU (Read-Copy Update)**. 

Це забезпечує визначну характеристику продуктивності ядра Linux: **читачі маршрутів (функція `fib_lookup`), які обробляють вхідний трафік, взагалі НЕ беруть жодних спинлоків або м'ютексів**.

1. **Lock-Free пошук (Read Path):** Функції `ip_route_input_noref()` та `fib_lookup()` викликаються всередині секції `rcu_read_lock()`. Вони читають вказівники `key_vector` та `fib_info` через `rcu_dereference()`. Жодної атомарної інструкції з блокуванням шини CPU (`LOCK` prefix) під час пошуку маршруту не виконується.
2. **Copy-On-Write оновлення (Write Path):** Коли демон BGP додає або вилучає маршрути (`ip route add/del`), процес оновлення модифікує дерево через `rcu_assign_pointer()`. Нові вузли створюються у пам'яті паралельно, після чого ядро атомарно перемикає вказівник у базі `tnode`. Старі вузли звільняються з затримкою через `call_rcu()` лише після того, як усі процесорні ядра завершать поточні обходи читання.

Завдяки RCU підсистема маршрутизації Linux бездоганно масштабується на багатьох'ядерних системах (64+ ядер CPU), усуваючи будь-які паузи при паралельному зчитуванні та швидкому оновленні BGP-таблиць.

---

## 4. Файловий інтерфейс діагностики: `/proc/net/fib_trie`

Ядро Linux експортує поточний внутрішній стан дерева LC-Trie для IPv4 через віртуальний файл `/proc/net/fib_trie`. Оскільки читання цього файлу може вимагати ітерацій по сотнях тисяч вузлів, воно виконується через механізм `seq_file` з підтримкою RCU-синхронізації без блокування обробки трафіку.

### Приклад текстового зліпку `/proc/net/fib_trie`

```text
Main:
  +-- 0.0.0.0/0 3 0 5
     |-- 0.0.0.0
        =/0 tn internal 0 1 2
        +-- 10.0.0.0/8 2 0 2
           |-- 10.1.1.0
              =/24 unicast src 10.1.1.100 val protocol kernel scope link
           |-- 10.1.2.0
              =/24 unicast via 192.168.1.1 dev eth0 val protocol static scope universe
Local:
  +-- 0.0.0.0/0 3 0 2
     |-- 127.0.0.0
        =/8 host dev lo val protocol kernel scope host
        =/32 host dev lo val protocol kernel scope host
     |-- 192.168.1.100
        =/32 host dev eth0 val protocol kernel scope host
```

### Розшифровка елементів виводу

1. **Ідентифікатор таблиці (`Main:`, `Local:`):** Окреме префіксне дерево роздруковується для кожної активної FIB-таблиці.
2. **Внутрішній вузол розгалуження (`+-- 0.0.0.0/0 3 0 5`):**
   * `+--`: Позначення внутрішнього вузла (Branch Node, `key_vector` з `bits > 0`).
   * `0.0.0.0/0`: Ключ-префікс даного вузла.
   * `3`: Кількість біт у цьому рівні розгалуження (`bits = 3`). Це означає, що вузол містить масив із `2^3 = 8` дочірніх вказівників.
   * `0`: Позиція біта розгалуження (`pos = 0`, тобто аналізуються старші біти IPv4-адреси).
   * `5`: Максимальна довжина суфіксу (`slen = 5`).
3. **Листок дерева (`|-- 10.1.1.0`):**
   * `--`: Позначення листка (Leaf Node, `key_vector` з `bits == 0`).
4. **Опис запису маршруту (`=/24 unicast via 192.168.1.1 ...`):**
   * `=/24`: Довжина маски префіксу.
   * `unicast` / `host`: Тип маршруту (`fa_type`).
   * `via 192.168.1.1`: Адреса шлюзу (`RTA_GATEWAY`).
   * `dev eth0`: Вихідний мережевий інтерфейс.
   * `protocol static`: Джерело додавання маршруту.
   * `scope universe`: Область видимості маршруту.

### Статистика LC-Trie: `/proc/net/fib_triestat`

Файл `/proc/net/fib_triestat` надає загальну статистику ефективності стиснення дерев LC-Trie для оцінки споживання пам'яті та глибини пошуку:

```text
Basic Trie Statistics:
  Main:
    Leaves: 15420
    Internal nodes: 4120
    Pointers: 32800
    Total memory used: 412 Kb
    Max depth: 4
```

Інтерпретація метрик статистики:
* **`Leaves`:** Загальна кількість листків у дереві (дорівнює кількості унікальних IP-префіксів у даній таблиці).
* **`Internal nodes`:** Кількість внутрішніх вузлів розгалуження (Branch Nodes). Чим менше це число відносно `Leaves`, тим ефективніше алгоритм Level Compression згортає дерево.
* **`Pointers`:** Загальна кількість елементів у масивах `tnode`.
* **`Total memory used`:** Сумарний обсяг оперативної пам'яті в кілобайтах, виділений під структуру дерева.
* **`Max depth`:** Максимальна глибина дерева від кореня до найвіддаленішого листка. Значення `Max depth` у межах 3–5 означає, що пошук найдовшого префіксу (LPM) для будь-якої адреси в таблиці з 800 000 BGP-маршрутів гарантовано виконується всього за 3–5 кроків індексації масиву.
