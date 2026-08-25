# 📋 Інтерфейс Netlink CTNETLINK та бібліотека libnetfilter_conntrack

Користувацькі утиліти, демони системного моніторингу та балансувальники навантаження взаємодіють із підсистемою відстеження з'єднань ядра Linux через спеціалізований бінарний протокол Netfilter Netlink — **CTNETLINK** (ідентифікатор підсистеми `NFNL_SUBSYS_CTNETLINK`). Замість повільного парсингу текстового файлу `/proc/net/nf_conntrack` (який вимагає виділення великих буферів пам'яті для всього списку з'єднань і викликає тривалі затримки в обробці), ядерний API CTNETLINK надає асинхронний сокетний інтерфейс реального часу для зчитування, створення, модифікації та видалення записів conntrack, а також підписки на події створення й закриття сесій.

Офіційною C-бібліотекою низького рівня для зручної роботи з цим API є **`libnetfilter_conntrack`**.

## Заголовочні файли та лінкування

Для використання API у власних програмах необхідно підключити основний заголовочний файл і злінкувати проєкт із бібліотеками `-lnetfilter_conntrack` та `-lmnl` (або `-lnfnetlink` у старіших версіях):

```c
#include <libnetfilter_conntrack/libnetfilter_conntrack.h>
```

Для спеціалізованої роботи з розширеннями TCP, NAT або таблицями очікуваних з'єднань (expectations) використовують додаткові заголовки:
- `<libnetfilter_conntrack/libnetfilter_conntrack_tcp.h>`
- `<libnetfilter_conntrack/libnetfilter_conntrack_ftp.h>`

## Будова повідомлень Netlink та підсистема CTNETLINK

Протокол CTNETLINK функціонує поверх сімейства сокетів `AF_NETLINK` із типом `NETLINK_NETFILTER`. Кожне повідомлення між ядром і користувацьким простором має стандартне розмежування вкладених заголовочних блоків:

1. **`struct nlmsghdr`**: Стандартний заголовок Netlink-повідомлення, що містить загальну довжину, тип повідомлення (`NFNL_SUBSYS_CTNETLINK << 8 | IPCTNL_MSG_CT_NEW`), прапорці (`NLM_F_REQUEST`, `NLM_F_DUMP`, `NLM_F_ACK`) та порядковий номер (sequence number).
2. **`struct nfgenmsg`**: Заголовок підсистеми Netfilter, що вказує на сімейство мережевих адрес (`AF_INET`, `AF_INET6` або `AF_UNSPEC`), версію протоколу (`NFNETLINK_V0`) та ідентифікатор ресурсу.
3. **TLV-атрибути (`struct nlattr`)**: Набір послідовних пар «Тип-Довжина-Значення» (Type-Length-Value), що кодують окремі атрибути з'єднання (IP-адреси, порти, статуси, таймери, лічильники байтів).

Бібліотека `libnetfilter_conntrack` повністю приховує ручне низькорівневе формування та парсинг цих TLV-структур за зручним об'єктно-орієнтованим C-інтерфейсом.

## Основні типи даних та структури

- **`struct nfct_handle`**: Непрозорий дескриптор сокета Netfilter Netlink. Управляє відкритим файловим дескриптором, буферами прийому/передачі, порядковими номерами повідомлень та підписками на групові події ядра.
- **`struct nf_conntrack`**: Структура в пам'яті користувацького простору, що представляє один зліпок з'єднання conntrack (аналог ядерної `struct nf_conn`).
- **`enum nf_conntrack_attr`**: Перелічуваний тип ключів для читання та запису атрибутів з'єднання.
- **`enum nfct_q_type`**: Тип синхронного запиту до ядра (`NFCT_Q_DUMP`, `NFCT_Q_CREATE`, `NFCT_Q_UPDATE`, `NFCT_Q_DESTROY`, `NFCT_Q_GET`).
- **`enum nfct_msg_type`**: Тип асинхронного повідомлення від ядра (`NFCT_T_NEW`, `NFCT_T_UPDATE`, `NFCT_T_DESTROY`).

## Повний довідник атрибутів з'єднання (`enum nf_conntrack_attr`)

Нижче наведено розширений перелік атрибутів, які використовуються для аналізу та конфігурування об'єктів `struct nf_conntrack`:

| Атрибут | Тип даних | Опис та специфікація |
| :--- | :--- | :--- |
| `ATTR_ORIG_IPV4_SRC` | `uint32_t` | IPv4-адреса джерела в напрямку ORIGINAL (network byte order) |
| `ATTR_ORIG_IPV4_DST` | `uint32_t` | IPv4-адреса призначення в напрямку ORIGINAL (network byte order) |
| `ATTR_REPLY_IPV4_SRC` | `uint32_t` | IPv4-адреса джерела в напрямку REPLY |
| `ATTR_REPLY_IPV4_DST` | `uint32_t` | IPv4-адреса призначення в напрямку REPLY |
| `ATTR_ORIG_IPV6_SRC` | `struct in6_addr` | 128-бітна IPv6-адреса джерела в напрямку ORIGINAL |
| `ATTR_ORIG_IPV6_DST` | `struct in6_addr` | 128-бітна IPv6-адреса призначення в напрямку ORIGINAL |
| `ATTR_REPLY_IPV6_SRC` | `struct in6_addr` | IPv6-адреса джерела у напрямку REPLY |
| `ATTR_REPLY_IPV6_DST` | `struct in6_addr` | IPv6-адреса призначення у напрямку REPLY |
| `ATTR_ORIG_PORT_SRC` | `uint16_t` | L4-порт джерела в напрямку ORIGINAL (network byte order) |
| `ATTR_ORIG_PORT_DST` | `uint16_t` | L4-порт призначення в напрямку ORIGINAL (network byte order) |
| `ATTR_REPLY_PORT_SRC` | `uint16_t` | L4-порт джерела в напрямку REPLY |
| `ATTR_REPLY_PORT_DST` | `uint16_t` | L4-порт призначення в напрямку REPLY |
| `ATTR_L3PROTO` | `uint8_t` | Сімейство мережевого протоколу (`AF_INET`, `AF_INET6`) |
| `ATTR_L4PROTO` | `uint8_t` | Номер транспортного протоколу (`IPPROTO_TCP`, `IPPROTO_UDP`, `IPPROTO_ICMP`) |
| `ATTR_TCP_STATE` | `uint8_t` | Стан TCP-автомата (`TCP_CONNTRACK_ESTABLISHED`, `TCP_CONNTRACK_SYN_SENT` тощо) |
| `ATTR_STATUS` | `uint32_t` | Бітова маска статусів з'єднання (`IPS_ASSURED`, `IPS_SEEN_REPLY`, `IPS_SRC_NAT`) |
| `ATTR_TIMEOUT` | `uint32_t` | Залишковий час життя з'єднання в секундах до його видалення з ядра |
| `ATTR_MARK` | `uint32_t` | 32-бітний маркер з'єднання (connmark), збережений у пам'яті ядра |
| `ATTR_ZONE` | `uint16_t` | Ідентифікатор conntrack zone (для ізоляції VRF та контейнерних мереж) |
| `ATTR_ORIG_COUNTER_PACKETS`| `uint64_t` | Кількість пропущених пакетів у напрямку ORIGINAL (потрібен acct) |
| `ATTR_ORIG_COUNTER_BYTES`  | `uint64_t` | Кількість пропущених байтів у напрямку ORIGINAL |
| `ATTR_REPLY_COUNTER_PACKETS`| `uint64_t` | Кількість пропущених пакетів у напрямку REPLY |
| `ATTR_REPLY_COUNTER_BYTES`  | `uint64_t` | Кількість пропущених байтів у напрямку REPLY |
| `ATTR_ID` | `uint32_t` | Унікальний системний ідентифікатор з'єднання у ядрі |

## Специфікація функцій API

### 1. Ініціалізація та закриття сокета

```c
struct nfct_handle *nfct_open(uint8_t subsys_id, unsigned subscriptions);
int nfct_close(struct nfct_handle *h);
```

Функція `nfct_open()` створює сокет Netlink, зв'язує його з локальною адресою порту Netlink і підписується на вказані мультикаст-групи подій.
- **`subsys_id`**: Вказує на підсистему Netlink. Для conntrack передається константа `NFNL_SUBSYS_CTNETLINK`.
- **`subscriptions`**: Бітова маска подій ядра, на які підписується дескриптор:
  - `NFCT_ALL_SYS_GROUP`: Отримувати всі повідомлення про створення, оновлення та вилучення з'єднань у всіх мережевих namespaces.
  - `NFCT_GROUP_NEW`: Підписка лише на нові з'єднання (`NFCT_T_NEW`).
  - `NFCT_GROUP_UPDATE`: Підписка лише на оновлення станів (`NFCT_T_UPDATE`).
  - `NFCT_GROUP_DESTROY`: Підписка лише на видалені з'єднання (`NFCT_T_DESTROY`).
  - `0`: Сокет відкривається виключно для виконання синхронних точкових запитів (дамп, створення, видалення записів).
- **Повертане значення**: Дійсний вказівник `struct nfct_handle *` у разі успіху або `NULL` при виникненні помилки (із встановленням відповідного значення `errno`).

Функція `nfct_close()` закриває системний сокет `AF_NETLINK` та звільняє виділені під нього ресурси пам'яті.

### 2. Створення та знищення userspace-структур

```c
struct nf_conntrack *nfct_new(void);
void nfct_destroy(struct nf_conntrack *ct);
struct nf_conntrack *nfct_clone(const struct nf_conntrack *ct);
```

- **`nfct_new()`**: Виділяє з купи користувацького простору пам'ять під новий об'єкт `struct nf_conntrack` та ініціалізує його порожніми значеннями.
- **`nfct_destroy()`**: Звільняє пам'ять, виділену під об'єкт `struct nf_conntrack`. Слід обов'язково викликати після завершення обробки кожного клонованого або локально створеного об'єкта.
- **`nfct_clone()`**: Створює точну глибоку копію існуючого об'єкта `ct`.

### 3. Модифікація та читання атрибутів

Для запису атрибутів використовується сімейство функцій `nfct_set_attr_*`:

```c
void nfct_set_attr_u8(struct nf_conntrack *ct, const enum nf_conntrack_attr attr, uint8_t value);
void nfct_set_attr_u16(struct nf_conntrack *ct, const enum nf_conntrack_attr attr, uint16_t value);
void nfct_set_attr_u32(struct nf_conntrack *ct, const enum nf_conntrack_attr attr, uint32_t value);
void nfct_set_attr_u64(struct nf_conntrack *ct, const enum nf_conntrack_attr attr, uint64_t value);
void nfct_set_attr(struct nf_conntrack *ct, const enum nf_conntrack_attr attr, const void *data);
```

Для читання атрибутів призначено відповідне сімейство `nfct_get_attr_*`:

```c
uint8_t  nfct_get_attr_u8(const struct nf_conntrack *ct, const enum nf_conntrack_attr attr);
uint16_t nfct_get_attr_u16(const struct nf_conntrack *ct, const enum nf_conntrack_attr attr);
uint32_t nfct_get_attr_u32(const struct nf_conntrack *ct, const enum nf_conntrack_attr attr);
uint64_t nfct_get_attr_u64(const struct nf_conntrack *ct, const enum nf_conntrack_attr attr);
const void *nfct_get_attr(const struct nf_conntrack *ct, const enum nf_conntrack_attr attr);
```

Якщо запитаний атрибут відсутній у з'єднанні (наприклад, спроба зчитати `ATTR_TCP_STATE` для UDP-з'єднання), функція повертає `0` або `NULL`. Перевірити наявність атрибута можна за допомогою `nfct_attr_is_set(ct, attr)`.

### 4. Виконання синхронних запитів до ядра

```c
int nfct_query(struct nfct_handle *h, const enum nfct_q_type qt, const void *data);
```

Перелічуваний тип `qt` визначає команду, яка упаковується у Netlink-повідомлення і надсилається ядру:

- `NFCT_Q_DUMP`: Запитати повний дамп усіх активних з'єднань із ядра. Вказівник `data` задає сімейство адрес (наприклад, `int family = AF_INET`).
- `NFCT_Q_CREATE`: Примусово створити новий запис з'єднання у ядрі. Вказівник `data` має посилатися на підготовлений `struct nf_conntrack` з обов'язково заповненими кортежами `ORIGINAL` та `REPLY`.
- `NFCT_Q_DESTROY`: Знищити запис у ядрі, що відповідає кортежу у `data`.
- `NFCT_Q_GET`: Запитати у ядра точну інформацію про одне конкретне з'єднання за його кортежем.

### 5. Реєстрація зворотних викликів та асинхронний цикл

```c
typedef int (*nfct_callback)(enum nfct_msg_type type, struct nf_conntrack *ct, void *data);

int nfct_callback_register(struct nfct_handle *h, enum nfct_type type, nfct_callback cb, void *data);
int nfct_catch(struct nfct_handle *h);
```

- **`nfct_callback_register()`**: Реєструє користувацьку функцію `cb` для сокета `h`.
  - `type`: Фільтр типів повідомлень (`NFCT_T_ALL`, `NFCT_T_NEW`, `NFCT_T_UPDATE`, `NFCT_T_DESTROY`).
  - `data`: Довільний контекстний вказівник користувача, який незмінним передаватиметься третім аргументом у функцію `cb`.
- **`nfct_catch()`**: Запускає блокуючий цикл зчитування Netlink-повідомлень із сокета ядра. Для кожного отриманого повідомлення функція декодує `struct nf_conntrack` і викликає зареєстрований `cb`.
  - Повертане значення `cb`: Якщо `cb` повертає `NFCT_CB_CONTINUE` (або `0`), `nfct_catch()` продовжує цикл. Якщо `cb` повертає `NFCT_CB_STOP` (або від'ємне значення), `nfct_catch()` перериває цикл і повертає керування викликачу.

## Робота з таблицею очікуваних з'єднань (Expectations API)

Для протоколів із динамічними портами (наприклад, FTP або SIP) у бібліотеці передбачено окремий набір типів і функцій для керування таблицею очікувань:

- **`struct nf_expect`**: Представляє очікуване майбутнє з'єднання у ядрі.
- **`nfexp_new()` / `nfexp_destroy()`**: Виділення та звільнення пам'яті під об'єкт очікування.
- **`nfexp_set_attr_*()` / `nfexp_get_attr_*()`**: Налаштування маски очікуваних адрес та портів (`ATTR_EXP_MASTER`, `ATTR_EXP_TUPLE`, `ATTR_EXP_MASK`).
- **`exp_query(h, NFCT_Q_CREATE, exp)`**: Вставка очікування в ядро.

## Обробка буферних переповнень та помилок

Під час взаємодії через сокет Netlink можуть виникати наступні виняткові ситуації:

1. **`ENOBUFS` (No buffer space available):** Загальний буфер прийому сокета в ядрі переповнився, оскільки швидкість генерації подій conntrack перевищила швидкість їх обробки у користувацькому процесі.
   - **Виправлення:** Збільшити розмір системного буфера сокета через `setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &size)` до кількох мегабайтів та налаштувати неблокираючий режим читання `O_NONBLOCK`.
2. **`EEXIST`:** Спроба створити з'єднання через `NFCT_Q_CREATE`, яке вже присутнє в глобальній хеш-таблиці ядра.
3. **`PERM` / `EACCES`:** Спроба відкрити сокет CTNETLINK без привілеїв `CAP_NET_ADMIN` або без прав root.
