# ⚙️ Запит та моніторинг таблиці маршрутизації через RTNETLINK мовами C та C++

Утиліти управління мережею (`iproute2`), підсистеми моніторингу та демони динамічної маршрутизації (такі як BIRD або FRRouting) взаємодіють із таблицею маршрутизації ядра Linux через сокети `AF_NETLINK` (протокол `NETLINK_ROUTE`). Цей підхід забезпечує атомарне виконання операцій, відсутність накладних витрат парсингу текстових файлів `/proc` чи `/sys` та можливість отримувати асинхронні сповіщення про зміну маршрутів у реальному часі.

Практична побудова такої утиліти мовою C та її ідіоматичного еквівалента мовою C++ вимагає надсилання запиту `RTM_GETROUTE` до ядра для визначення вихідного інтерфейсу й IP-адреси шлюзу для заданої IP-адреси призначення з наступним переходом у режим прослуховування асинхронних подій оновлення маршрутів `RTMGRP_IPV4_ROUTE`. Розбір її реалізації розкриває структуру кастомних розширень Netlink, правила бінарного вирівнювання атрибутів та механізм асинхронного відстеження змін у таблицях FIB.

---

## Архітектура та принцип роботи сокетів RTNETLINK

Взаємодія з мережевим стеком ядра Linux через Netlink спирається на двобоку передачу датаграм. На відміну від звичайних мережевих сокетів TCP/UDP, Netlink діє виключно в межах локальної оперативної пам'яті комп'ютера, передаючи повідомлення між процесами користувача та підсистемами ядра.

Основний цикл обробки повідомлень включає п'ять послідовних етапів:

1. **Створення сокета та виділення дескриптора:** Застосунок створює системний дескриптор сокета за допомогою виклику `socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE)`. Тип `SOCK_RAW` означає, що програма самостійно формує заголовки Netlink-повідомлень та обробляє сирі байтові масиви.
2. **Підписка на групи мультикасту (Multicast Groups):** Для отримання асинхронних сповіщень про події в ядрі (наприклад, додавання чи вилучення маршруту сторонніми процесами) сокет зв'язується з відповідною групою через `bind()`. Вказавши прапорець `RTMGRP_IPV4_ROUTE`, програма реєструється в ядрі як слухач подій IPv4-маршрутизації.
3. **Формування та вирівнювання запиту:** Повідомлення Netlink складається зі стандартного заголовка `struct nlmsghdr`, заголовка маршрутизації `struct rtmsg` та послідовності атрибутів `struct rtattr`. Кожен елемент у буфері повинен бути вирівняний за 4-байтовою межею (`NLMSG_ALIGN` та `RTA_ALIGN`). Нехтування вирівнюванням призводить до відхилення пакета ядром з помилкою `EINVAL`.
4. **Виконання запиту `RTM_GETROUTE`:** Надіслане повідомлення з типом `RTM_GETROUTE` змушує ядро виконати пошук у префіксному дереві LC-Trie (FIB) для вказаної IP-адреси. Ядро знаходить відповідний запис і повертає повідомлення `RTM_NEWROUTE`, яке містить повну інформацію про маршрут: IP-адресу шлюзу (`RTA_GATEWAY`), індекс вихідного інтерфейсу (`RTA_OIF`), переважне джерело (`RTA_PREFSRC`) та метрику (`RTA_PRIORITY`).
5. **Асинхронний моніторинг подій:** Після обробки первинної відповіді програма входить у цикл `recv()`, очікуючи на нові сповіщення від ядра. Коли інший процес виконує додавання (`ip route add`) або видалення (`ip route del`) маршруту, ядро дублює відповідні повідомлення `RTM_NEWROUTE` або `RTM_DELROUTE` всім підписаним сокетам.

---

## Детальний розбір сокетної адресації: struct sockaddr_nl

При ініціалізації сокета Netlink системний виклик `bind()` приймає спеціалізовану структуру адреси `struct sockaddr_nl`:

:::tabs
```c
struct sockaddr_nl {
    sa_family_t nl_family;   /* Обов'язково AF_NETLINK */
    unsigned short nl_pad;   /* Заповнювач (мусить бути 0) */
    __u32        nl_pid;     /* Ідентифікатор сокета (Port ID, 0 для ядра) */
    __u32        nl_groups;  /* Бітова маска груп підписки мультикасту */
};
```
```cpp
// У C++20 адресація Netlink задається через C++-типи та ініціалізатори за замовчуванням
namespace net {
    struct SockAddrNl {
        sa_family_t nl_family{AF_NETLINK}; /* Обов'язково AF_NETLINK */
        std::uint16_t nl_pad{0};           /* Заповнювач (мусить бути 0) */
        std::uint32_t nl_pid{0};           /* Ідентифікатор сокета (Port ID, 0 для ядра) */
        std::uint32_t nl_groups{0};        /* Бітова маска груп підписки мультикасту */
    };
}
```
:::

Поле `nl_pid` виступає унікальною адресою порту в межах даного мережевого простору імен (network namespace). Зазвичай користувацькі програми вказують `nl_pid = 0`. У цьому випадку ядро автоматично присвоює сокету ідентифікатор, що дорівнює PID поточного процесу. Якщо один процес відкриває кілька сокетів Netlink, ядро комбінує PID процесу та унікальний номер потоку.

Поле `nl_groups` визначає бітову маску мультикаст-груп підписки:
* `RTMGRP_LINK`: Підписка на події створення/зміни мережевих інтерфейсів (`RTM_NEWLINK`/`RTM_DELLINK`).
* `RTMGRP_IPV4_IFADDR`: Підписка на зміну IPv4-адрес на інтерфейсах (`RTM_NEWADDR`).
* `RTMGRP_IPV4_ROUTE`: Підписка на зміну IPv4-маршрутів у FIB (`RTM_NEWROUTE`/`RTM_DELROUTE`).
* `RTMGRP_IPV4_RULE`: Підписка на зміну правил PBR (`RTM_NEWRULE`).

---

## Особливості додавання маршрутів через RTM_NEWROUTE

При розширенні програми для додавання нових маршрутів (`ip route add`) утиліта повинна формувати запит з типом `RTM_NEWROUTE` та прапорцями `NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL`.

При додаванні слід враховувати тип топології мережевого інтерфейсу:

1. **Маршрут через Ethernet (Broadcast/Multitap):** Вимагає обов'язкової наявності атрибута `RTA_GATEWAY` з IP-адресою шлюзу. Ядро використовує цю IP-адресу для виконання ARP-запиту в локальній мережі.
2. **Точка-точка (Point-to-Point, PPP, GRE, WireGuard):** Включає лише атрибут `RTA_OIF` з індексом інтерфейсу, оскільки L2-адресація на таких тунелях відсутній і всі пакети відправляються напряму в тунель.

При спробі додати маршрут з недосяжним шлюзом (коли IP-адреса шлюзу з `RTA_GATEWAY` не підпадає під жодну з локальних підмереж `scope link`), ядро повертає помилку `-ENETUNREACH` ("Network is unreachable").

---

## Детальний розбір буферизації та макросів вирівнювання Netlink

Під час роботи з бінарним протоколом Netlink розробник не може спиратися на прості виклики `write()` чи `read()` із текстурированими даними. Буфер пам'яті пакета складається зі зв'язаних блоків TLV.

Для коректної обробки цих блоків ядро Linux надає набір обов'язкових макросів у файлі `<linux/netlink.h>` та `<linux/rtnetlink.h>`:

* **`NLMSG_ALIGN(len)`:** Округлює довжину `len` до найближчого кратного 4 значення. Усі заголовки та дані у Netlink зобов'язані починатися за 4-байтовою межею пам'яті (align boundary).
* **`NLMSG_LENGTH(len)`:** Обчислює загальний розмір заголовка `struct nlmsghdr` плюс корисне навантаження `len`, вирівняне за правилами Netlink.
* **`NLMSG_SPACE(len)`:** Повертає повну кількість байтів у пам'яті, необхідну для розміщення заголовка та навантаження `len` з урахуванням кінцевого вирівнювання.
* **`NLMSG_DATA(nlh)`:** Повертає вказівник на початок корисного навантаження, розташованого одразу за заголовком `struct nlmsghdr` (у нашому випадку — на структуру `struct rtmsg`).
* **`NLMSG_NEXT(nlh, len)`:** Пересуває вказівник `nlh` на наступне повідомлення в одному зведеному буфері, зменшуючи залишок `len` на розмір поточного повідомлення.
* **`NLMSG_OK(nlh, len)`:** Перевіряє, чи не виходить поточний заголовок за межі зчитаного з сокета буфера пам'яті.
* **`RTA_ALIGN(len)`:** Вирівнює розмір атрибута `struct rtattr`.
* **`RTA_LENGTH(len)`:** Обчислює розмір `struct rtattr` плюс корисне навантаження `len`.
* **`RTA_DATA(rta)`:** Повертає вказівник на значення атрибута (наприклад, на `struct in_addr` для `RTA_DST` або `RTA_GATEWAY`).
* **`RTA_NEXT(rta, len)`:** Пересуває вказівник атрибута на наступний TLV-блок.
* **`RTA_OK(rta, len)`:** Перевіряє валідність залишку ланцюжка атрибутів.

Некоректне застосування цих макросів (наприклад, спроба прочитати `RTA_DATA` без перевірки `RTA_OK`) є найпоширенішою причиною аварійного завершення системних утиліт через уразливість segmentation fault або вихід за межі масиву.

---

## Налаштування опцій сокета та обробка сигналів POSIX

При створенні промислових сервісів моніторингу мережі слід враховувати поведінку Netlink-сокета при отриманні POSIX-сигналів та навантаженні на систему:

1. **Обробка переривань системних викликів (`EINTR`):** Виклик `recv()` може бути перерваний при надходженні системного сигналу (наприклад, `SIGINT` або `SIGALRM`). Код обробки мусить перевіряти `errno == EINTR` і продовжувати цикл читання замість аварійного завершення.
2. **Управління розміром системного буфера (`SO_RCVBUF`):** Під час масового оновлення таблиці маршрутизації ядро генерує тисячі повідомлень на секунду. Якщо розмір сокетного буфера за замовчуванням є занадто малим (наприклад 212 Кб), буфер швидко переповнюється, і ядро скидає нові сповіщення. Збільшення розміру буфера через `setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &size, sizeof(size))` до 4-8 Мб запобігає втраті пакетів під час сплесків.
3. **Строга перевірка атрибутів (`NETLINK_GET_STRICT_CHK`):** Починаючи з ядра Linux 4.20, включення цієї опції через `setsockopt(fd, SOL_NETLINK, NETLINK_GET_STRICT_CHK, &one, sizeof(one))` змушує ядро виконувати сувору перевірку всіх атрибутів `RTA_*`, що гарантує відсікання некоректно сформованих запитів на ранній стадії.
4. **Контроль облікових даних (`SO_PASSCRED`):** Дозволяє системним демонам підтверджувати UID та GID процесу, який надіслав повідомлення через Netlink, захищаючи від підробки запитів.

---

## Продуктивність та порівняння з /proc файловими інтерфейсами

Чому сучасні високонавантажені демони маршрутизації (такі як BIRD, FRRouting, Cilium) повністю відмовилися від зчитування інформації з `/proc/net/route` чи `/proc/net/fib_trie` на користь Netlink?

1. **Відсутність накладних витрат формативування та парсингу:** Файли `/proc` генерують текстові рядки у режимі real-time при кожному виклику `read()`. Перетворення двозначних десяткових та шістнадцятирічних рядків у бінарні IP-адреси вимагає мільйонів викликів `sscanf()` або `strtoul()`. Netlink передає сирі бінарні структури прямо з пам'яті ядра без жодної трансформації в текст.
2. **Атомарність та версійність змін:** При зчитуванні великого текстового файла `/proc/net/fib_trie` (який може мати розмір у десятки мегабайтів при наявності BGP Full View) таблиця маршрутизації може змінитися прямо посеред читання. Це створює неузгоджений стан даних у користувацькому просторі. Netlink надсилає атомарні сповіщення про зміну конкретних префіксів із черговістю послідовних номерів `nlmsg_seq`.
3. **Асинхронні події замість пасивного опитання (Polling):** Щоб виявити зміну маршруту через `/proc`, програма мусила б у нескінченному циклі опитувати файл (polling), що спалювало б ресурси CPU. Netlink переводить потік користувача у стан сну `recv()`, виключаючи марні виклики до моменту появи реальної події у ядрі.

---

## Інтеграція з евентовими циклами (epoll та non-blocking I/O)

У промислових демонах мережевого моніторингу (наприклад, у сервісах Kubernetes CNI або демонах BGP) сокет Netlink не може бути блокуючим. Перебування у безкінечному блокуючому виклику `recv()` блокує єдиний потік виконання і робить неможливим паралельне обслуговування інших сокетів.

Щоб інтегрувати сокет Netlink у сучасний асинхронний цикл обробки подій (`epoll` або `io_uring`):
1. Сокет преводиться у неблокуючий режим через системний виклик `fcntl(fd, F_SETFL, O_NONBLOCK)`.
2. Файловий дескриптор сокета реєструється в контексті `epoll` за допомогою `epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev)` з прапорцями `EPOLLIN | EPOLLET` (Edge-Triggered Mode).
3. При настанні події готовності читання цикл `epoll_wait()` сповіщає потік обробки. Застосунок у циклі зчитує всі доступні повідомлення Netlink до тих пір, поки `recv()` не поверне помилку `EAGAIN` або `EWOULDBLOCK`.
4. Збільшення розміру буфера прийому сокета через `setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &bufsize, sizeof(bufsize))` дозволяє уникати втрати сповіщень під час сплесків трафіку.

---

## Крайові випадки та обробка помилок

Під час розробки високопродуктивних мережевих систем на базі Netlink необхідно враховувати ряд критичних крайових випадків:

### 1. Переповнення сокетного буфера (`ENOBUFS`)

Якщо утиліта не встигає зчитувати сповіщення з сокета під час масового оновлення маршрутів (наприклад, при отриманні BGP Full View з 800 000 маршрутів від демона FRRouting), буфер прийому сокета переповнюється. Ядро скидає нові сповіщення і повертає помилку `ENOBUFS` при наступному виклику `recv()`.

У цьому випадку програма зобов'язана очистити буфер і повторно виконати повне сканування таблиць через `RTM_GETROUTE` з прапорцем `NLM_F_DUMP`.

### 2. Багаточастинні повідомлення (`NLM_F_MULTI`)

При запиті повної таблиці маршрутизації ядро розбиває відповідь на послідовність багатьох пакетів. Кожен такий пакет має прапорець `NLM_F_MULTI` у заголовку `struct nlmsghdr`. Послідовність завершується спеціальним повідомленням із типом `NLMSG_DONE`. Програма повинна продовжувати цикл читання до отримання маркера `NLMSG_DONE`.

### 3. Обробка помилок ядра (`NLMSG_ERROR`)

Якщо ядро не може виконати запит (наприклад, маршрут до вказаного IP відсутній у FIB), воно повертає повідомлення з типом `NLMSG_ERROR`. Внутрішня структура `struct nlmsgerr` містить від'ємний код помилки POSIX (наприклад, `-ESRCH` для відсутнього маршруту або `-EPERM` при відсутності прав `CAP_NET_ADMIN`).

:::tabs
```c
struct nlmsgerr {
    int error;             /* Від'ємний код помилки (наприклад -ESRCH) */
    struct nlmsghdr msg;   /* Копія заголовка запиту, який викликав помилку */
};
```
```cpp
// У C++ обробка помилок Netlink інтегрується зі std::error_code або std::system_error
namespace net {
    struct NlMsgErr {
        int error{0};          /* Від'ємний код помилки POSIX (наприклад -ESRCH) */
        ::nlmsghdr msg{};      /* Копія заголовка запиту, який викликав помилку */

        [[nodiscard]] std::error_code code() const noexcept {
            return std::error_code(-error, std::generic_category());
        }
    };
}
```
:::

---

## Покроковий розбір реалізації мовою C

С-версія утиліти демонструє низькорівневе управління пам'яттю та пряму роботу із системними структури ядра Linux.

Основним блоком відправки є функція `add_attr_var()`, яка будує послідовність атрибутів `rtattr` у виділеному буфері:
1. Перевіряє, чи вистачає вільного місця в `route_request` для нового атрибута TLV.
2. Знаходить кінець поточного пакета за допомогою `NLMSG_ALIGN(n->nlmsg_len)`.
3. Заповнює поля `rta_type` та `rta_len`.
4. Копіює значення (наприклад, `struct in_addr`) через `memcpy()` у ділянку `RTA_DATA(rta)`.
5. Збільшує `n->nlmsg_len` на вирівняну довжину нового атрибута.

Після надсилання запиту функція `parse_route_response()` проходить по всіх атрибутах `rtattr` у відповіді ядра, розпізнає тип атрибута за списком `switch (rta->rta_type)` і перетворює бінарну IP-адресу у читабельний текстовий вигляд за допомогою `inet_ntop()`.

Якщо вихідний інтерфейс знайдено (атрибут `RTA_OIF`), функція `if_indextoname()` здійснює додатковий виклик до мережевої підсистеми для перетворення числового індексу інтерфейсу (наприклад, `2`) у текстове ім'я (наприклад, `eth0`).

---

## Покроковий розбір ідіоматичної реалізації мовою C++20

C++20 версія утиліти повністю усуває недоліки прямої роботи з вказівниками та мануального контролю ресурсів.

Ключові архітектурні елементи C++20 коду:

1. **Клас-обгортка `NetlinkSocket` (RAII):** Конструктор відкриває сокет, а деструктор гарантує його закриття через `close(fd)`. Клас забороняє копіювання (`delete copy constructor`), але дозволяє переміщення (`move semantics`), що відповідає семантиці унікального володіння системним дескриптором.
2. **Безпечна робота з буферами через `std::span`:** Метод `send()` приймає `std::span<const uint8_t>`, унеможливлюючи передачу неузгоджених пар «вказівник + довжина». Буфер прийому `rx_buffer` автоматично керується динамічним вектором `std::vector<uint8_t>`.
3. **Ізоляція структури `RouteInfo`:** Замість процедурного виводу інформації у потік `stdout`, функція `parse_rtmsg()` повертає суто безпечну C++ структуру `RouteInfo`, яка містить типові рядки `std::string` та чисельні значення.
4. **Обробка помилок через виключення `std::system_error`:** Будь-який збій системного виклику (`socket()`, `bind()`, `send()`, `recv()`) генерує стандартизоване виключення `std::system_error`, яке інкапсулює значення `errno` та надає зрозуміле текстове пояснення причини аварії.

---

## Інструкція зі збірки та тестування програми

Для збірки та перевірки роботи програми в операційній системі Linux виконайте наступні команди:

### 1. Компіляція C та C++ версій

```bash
# Збірка версії мовою C
gcc -O2 -Wall -Wextra rtnetlink_route_lookup.c -o route_lookup_c

# Збірка версії мовою C++20
g++ -O2 -std=c++20 -Wall -Wextra rtnetlink_route_lookup.cpp -o route_lookup_cpp
```

### 2. Запуск та діагностика

Для створення сокетів Netlink не потрібні привілеї суперкористувача `root`, якщо програма лише виконує читання та моніторинг маршрутів (`RTM_GETROUTE`). Проте привілеї `CAP_NET_ADMIN` потрібні, якщо ви додаєте нові маршрути (`RTM_NEWROUTE`).

```bash
# Запуск запиту маршруту до адреси 8.8.8.8
./route_lookup_cpp 8.8.8.8
```

Приклад очікуваного виводу програми:
```text
Надіслано запит RTM_GETROUTE для IP: 8.8.8.8
[NEW] Призначення: 8.8.8.8/32 | Шлюз: 192.168.1.1 | Джерело: 192.168.1.100 | Інтерфейс: eth0 (2)
```

Якщо під час роботи програми у сусідньому терміналі виконати додавання статичного маршруту:
```bash
sudo ip route add 10.99.0.0/16 via 192.168.1.1 dev eth0
```
Програма миттєво зреагує на асинхронне сповіщення ядра і надрукує у термінал новий рядок:
```text
[NEW] Призначення: 10.99.0.0/16 | Шлюз: 192.168.1.1 | Джерело: 192.168.1.100 | Інтерфейс: eth0 (2)
```

---

## Повний код утиліти мовами C та C++

:::tabs
```c
/*
 * rtnetlink_route_lookup.c
 * Системна програма мовою C для запиту та моніторингу маршрутів через NETLINK_ROUTE.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <linux/rtnetlink.h>

#define BUFFER_SIZE 8192

/* Структура для запиту маршруту до ядра */
struct route_request {
    struct nlmsghdr nl;
    struct rtmsg    rt;
    char            buf[128];
};

/* Допоміжна функція додавання атрибута TLV */
static void add_attr_var(struct nlmsghdr *n, int maxlen, int type, const void *data, int alen) {
    int len = RTA_LENGTH(alen);
    struct rtattr *rta;

    if (NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len) > maxlen) {
        fprintf(stderr, "Помилка: буфер Netlink переповнено\n");
        return;
    }
    rta = (struct rtattr *)(((char *)n) + NLMSG_ALIGN(n->nlmsg_len));
    rta->rta_type = type;
    rta->rta_len = len;
    memcpy(RTA_DATA(rta), data, alen);
    n->nlmsg_len = NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len);
}

/* Парсинг атрибутів RTA у відповіді ядра */
static void parse_route_response(struct nlmsghdr *nlh) {
    struct rtmsg *rt = (struct rtmsg *)NLMSG_DATA(nlh);
    struct rtattr *rta = (struct rtattr *)RTM_RTA(rt);
    int rtl = RTM_PAYLOAD(nlh);

    char dst_str[INET_ADDRSTRLEN] = "default";
    char gw_str[INET_ADDRSTRLEN] = "none";
    char src_str[INET_ADDRSTRLEN] = "none";
    int oif = 0;

    for (; RTA_OK(rta, rtl); rta = RTA_NEXT(rta, rtl)) {
        switch (rta->rta_type) {
            case RTA_DST:
                inet_ntop(AF_INET, RTA_DATA(rta), dst_str, sizeof(dst_str));
                break;
            case RTA_GATEWAY:
                inet_ntop(AF_INET, RTA_DATA(rta), gw_str, sizeof(gw_str));
                break;
            case RTA_PREFSRC:
                inet_ntop(AF_INET, RTA_DATA(rta), src_str, sizeof(src_str));
                break;
            case RTA_OIF:
                oif = *(int *)RTA_DATA(rta);
                break;
        }
    }

    char ifname[IF_NAMESIZE] = "unknown";
    if (oif > 0) {
        if_indextoname(oif, ifname);
    }

    printf("[ROUTE] Призначення: %s/%d | Шлюз: %s | Джерело: %s | Інтерфейс: %s (%d)\n",
           dst_str, rt->rtm_dst_len, gw_str, src_str, ifname, oif);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <Destination IPv4>\n", argv[0]);
        return EXIT_FAILURE;
    }

    struct in_addr dst_addr;
    if (inet_pton(AF_INET, argv[1], &dst_addr) <= 0) {
        fprintf(stderr, "Некоректна IP-адреса: %s\n", argv[1]);
        return EXIT_FAILURE;
    }

    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
    if (fd < 0) {
        perror("Помилка створення socket(AF_NETLINK)");
        return EXIT_FAILURE;
    }

    /* Прив'язка до сокета та підписка на події маршрутизації */
    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;
    sa.nl_groups = RTMGRP_IPV4_ROUTE;

    if (bind(fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("Помилка bind()");
        close(fd);
        return EXIT_FAILURE;
    }

    /* Формування запиту RTM_GETROUTE */
    struct route_request req;
    memset(&req, 0, sizeof(req));
    req.nl.nlmsg_len = NLMSG_LENGTH(sizeof(struct rtmsg));
    req.nl.nlmsg_flags = NLM_F_REQUEST;
    req.nl.nlmsg_type = RTM_GETROUTE;
    req.rt.rtm_family = AF_INET;
    req.rt.rtm_dst_len = 32;

    add_attr_var(&req.nl, sizeof(req), RTA_DST, &dst_addr, sizeof(dst_addr));

    if (send(fd, &req, req.nl.nlmsg_len, 0) < 0) {
        perror("Помилка send()");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Надіслано запит RTM_GETROUTE для IP: %s\n", argv[1]);

    /* Отримання відповіді та слухання асинхронних подій */
    char buffer[BUFFER_SIZE];
    while (1) {
        ssize_t len = recv(fd, buffer, sizeof(buffer), 0);
        if (len < 0) {
            perror("Помилка recv()");
            break;
        }

        struct nlmsghdr *nlh = (struct nlmsghdr *)buffer;
        for (; NLMSG_OK(nlh, len); nlh = NLMSG_NEXT(nlh, len)) {
            if (nlh->nlmsg_type == NLMSG_DONE) {
                break;
            }
            if (nlh->nlmsg_type == NLMSG_ERROR) {
                fprintf(stderr, "Отримано помилку від ядра Netlink\n");
                break;
            }
            if (nlh->nlmsg_type == RTM_NEWROUTE || nlh->nlmsg_type == RTM_DELROUTE) {
                printf("%s ", (nlh->nlmsg_type == RTM_NEWROUTE) ? "[NEW]" : "[DEL]");
                parse_route_response(nlh);
            }
        }
    }

    close(fd);
    return EXIT_SUCCESS;
}
```
```cpp
/*
 * rtnetlink_route_lookup.cpp
 * Ідіоматична реалізація мовою C++20 з використанням RAII, std::span та std::expected.
 */

#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <expected>
#include <system_error>
#include <memory>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <linux/rtnetlink.h>

namespace net {

// RAII обгортка навколо Netlink сокета
class NetlinkSocket {
public:
    explicit NetlinkSocket(int protocol) {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW, protocol);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося створити AF_NETLINK сокет");
        }
    }

    ~NetlinkSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;

    NetlinkSocket(NetlinkSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    NetlinkSocket& operator=(NetlinkSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    void bind(uint32_t groups) {
        sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;
        sa.nl_groups = groups;

        if (::bind(fd_, reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка bind() для Netlink");
        }
    }

    void send(std::span<const uint8_t> data) const {
        if (::send(fd_, data.data(), data.size(), 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка відправки в Netlink");
        }
    }

    ssize_t receive(std::span<uint8_t> buffer) const {
        ssize_t ret = ::recv(fd_, buffer.data(), buffer.size(), 0);
        if (ret < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка читання з Netlink");
        }
        return ret;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }

private:
    int fd_{-1};
};

struct RouteInfo {
    std::string destination;
    uint8_t prefix_len{0};
    std::string gateway;
    std::string preferred_src;
    std::string interface_name;
    uint32_t interface_index{0};
    uint16_t msg_type{0};
};

// Парсинг атрибутів повідомлення RTM_NEWROUTE
inline RouteInfo parse_rtmsg(const nlmsghdr* nlh) {
    RouteInfo info{};
    info.msg_type = nlh->nlmsg_type;

    const auto* rt = reinterpret_cast<const rtmsg*>(NLMSG_DATA(nlh));
    info.prefix_len = rt->rtm_dst_len;

    const auto* rta = reinterpret_cast<const rtattr*>(RTM_RTA(rt));
    int rtl = RTM_PAYLOAD(nlh);

    char addr_buf[INET_ADDRSTRLEN]{0};

    for (; RTA_OK(rta, rtl); rta = RTA_NEXT(rta, rtl)) {
        switch (rta->rta_type) {
            case RTA_DST:
                ::inet_ntop(AF_INET, RTA_DATA(rta), addr_buf, sizeof(addr_buf));
                info.destination = addr_buf;
                break;
            case RTA_GATEWAY:
                ::inet_ntop(AF_INET, RTA_DATA(rta), addr_buf, sizeof(addr_buf));
                info.gateway = addr_buf;
                break;
            case RTA_PREFSRC:
                ::inet_ntop(AF_INET, RTA_DATA(rta), addr_buf, sizeof(addr_buf));
                info.preferred_src = addr_buf;
                break;
            case RTA_OIF:
                info.interface_index = *reinterpret_cast<const uint32_t*>(RTA_DATA(rta));
                break;
        }
    }

    if (info.destination.empty()) info.destination = "default";
    if (info.gateway.empty()) info.gateway = "none";
    if (info.preferred_src.empty()) info.preferred_src = "none";

    if (info.interface_index > 0) {
        char ifbuf[IF_NAMESIZE]{0};
        if (::if_indextoname(info.interface_index, ifbuf)) {
            info.interface_name = ifbuf;
        } else {
            info.interface_name = "unknown";
        }
    }

    return info;
}

} // namespace net

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <Destination IPv4>\n";
        return EXIT_FAILURE;
    }

    in_addr dst_addr{};
    if (::inet_pton(AF_INET, argv[1], &dst_addr) <= 0) {
        std::cerr << "Некоректна IP-адреса: " << argv[1] << "\n";
        return EXIT_FAILURE;
    }

    try {
        net::NetlinkSocket sock(NETLINK_ROUTE);
        sock.bind(RTMGRP_IPV4_ROUTE);

        // Будуємо повідомлення RTM_GETROUTE
        std::vector<uint8_t> request_buf(NLMSG_SPACE(sizeof(rtmsg)) + RTA_SPACE(sizeof(in_addr)));
        
        auto* nlh = reinterpret_cast<nlmsghdr*>(request_buf.data());
        nlh->nlmsg_len = NLMSG_LENGTH(sizeof(rtmsg));
        nlh->nlmsg_flags = NLM_F_REQUEST;
        nlh->nlmsg_type = RTM_GETROUTE;

        auto* rt = reinterpret_cast<rtmsg*>(NLMSG_DATA(nlh));
        rt->rtm_family = AF_INET;
        rt->rtm_dst_len = 32;

        // Додаємо атрибут RTA_DST
        auto* rta = reinterpret_cast<rtattr*>(reinterpret_cast<char*>(nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
        rta->rta_type = RTA_DST;
        rta->rta_len = RTA_LENGTH(sizeof(in_addr));
        std::memcpy(RTA_DATA(rta), &dst_addr, sizeof(in_addr));
        nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(rta->rta_len);

        sock.send(request_buf);
        std::cout << "Надіслано запит RTM_GETROUTE для IP: " << argv[1] << "\n";

        std::vector<uint8_t> rx_buffer(8192);
        while (true) {
            ssize_t len = sock.receive(rx_buffer);
            const auto* rx_nlh = reinterpret_cast<const nlmsghdr*>(rx_buffer.data());

            for (; NLMSG_OK(rx_nlh, len); rx_nlh = NLMSG_NEXT(rx_nlh, len)) {
                if (rx_nlh->nlmsg_type == NLMSG_DONE) break;
                if (rx_nlh->nlmsg_type == NLMSG_ERROR) {
                    std::cerr << "Помилка ядра Netlink\n";
                    break;
                }
                if (rx_nlh->nlmsg_type == RTM_NEWROUTE || rx_nlh->nlmsg_type == RTM_DELROUTE) {
                    auto info = net::parse_rtmsg(rx_nlh);
                    std::cout << (info.msg_type == RTM_NEWROUTE ? "[NEW] " : "[DEL] ")
                              << "Призначення: " << info.destination << "/" << static_cast<int>(info.prefix_len)
                              << " | Шлюз: " << info.gateway
                              << " | Джерело: " << info.preferred_src
                              << " | Інтерфейс: " << info.interface_name << " (" << info.interface_index << ")\n";
                }
            }
        }
    } catch (const std::exception& ex) {
        std::cerr << "Виключна ситуація: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

---

## Порівняльний аналіз C та C++ рішень

Розроблена утиліта демонструє глибокі концептуальні відмінності підходів при створенні системного софту для Linux:

1. **Керування ресурсами та безпека виключень:** У С-реалізації розробник змушений вручну контролювати закриття системного файлового дескриптора `close(fd)` у кожній гілці обробки помилок (після `bind()`, `send()`, `recv()`). Забутий `close()` створює витік дескрипторів у довготривалих демонах. У C++ клас `NetlinkSocket` використовує парадигму **RAII (Resource Acquisition Is Initialization)**. Системний дескриптор гарантовано закривається в деструкторі при виході з області видимості, навіть якщо у внутрішньому циклі було згенеровано виключення.
2. **Безпека роботи з пам'яттю:** У коді на C маніпуляції з бінарними буферами виконуються через неприведені вказівники `char*` та сирі операції `memcpy()`. Помилка у розрахунку довжини вирівнювання `NLMSG_ALIGN` може призвести до виходу за межі виділеної пам'яті (out-of-bounds write). У C++ застосування `std::span<uint8_t>` забезпечує безпечну передачу неперервних ділянок пам'яті без явного передавання окремого аргументу довжини, а `std::vector<uint8_t>` здійснює автоматичне виділення та звільнення пам'яті в купі.
3. **Обробка помилок та ABI:** C-версія повертає від'ємні коди `errno` та друкує повідомлення в `stderr` через `perror()`. C++ версія інтегрує системні коди помилок у загальну ієрархію `std::system_error`, дозволяючи вищому рівню застосунку перехоплювати та коректно обробляти помилки мережевого стека без аварійного завершення процесу.
