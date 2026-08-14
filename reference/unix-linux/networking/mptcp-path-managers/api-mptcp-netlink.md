# 📋 Довідник Netlink API та інструментів управління MPTCP

Цей довідник містить вичерпну специфікацію бінарного програмного інтерфейсу MPTCP Generic Netlink (`GENL_NAME_MPTCP`), списки команд ядра, мультикаст-подій, атрибутів структури NLA (Netlink Attributes), а також розширений синтаксис та приклади використання адміністративного інструменту `ip mptcp` та налаштувань ядра через підсистему `sysctl`.

## 1. Специфікація Generic Netlink Сімейства MPTCP

Керування підсистемою MPTCP у ядрі Linux виконується через механізм Generic Netlink, який надає динамічну адресацію сімейств та мультикаст-груп поверх класичного сокета `AF_NETLINK` із типом `NETLINK_GENERIC`.

Основні константи, визначені в заголовочному файлі ядра `<linux/mptcp.h>`:

- **Ім'я Generic Netlink сімейства**: `mptcp` (визначено константою `MPTCP_PM_NAME` або `GENL_NAME_MPTCP`).
- **Версія протоколу**: `1` (`MPTCP_PM_VER`).
- **Мультикаст-група подій**: `subflow` (`MPTCP_PM_EV_GRP_NAME`).

Структура кожного Netlink-повідомлення складається з базового заголовка Netlink (`struct nlmsghdr`), за яким іде заголовок Generic Netlink (`struct genlmsghdr`), а далі — послідовність вирівняних по 4 байтах атрибутів NLA (`struct nlattr`).

### Структура заголовків Netlink

Заголовок `struct nlmsghdr` містить наступні поля:
- `nlmsg_len`: повна довжина повідомлення в байтах, включаючи всі заголовки та корисне навантаження.
- `nlmsg_type`: ідентифікатор сімейства Generic Netlink (отриманий динамічно під час запиту `CTRL_CMD_GETFAMILY`).
- `nlmsg_flags`: прапорці запиту (наприклад, `NLM_F_REQUEST`, `NLM_F_ACK`, `NLM_F_DUMP`).
- `nlmsg_seq`: порядковий номер повідомлення для синхронізації запитів та відповідей.
- `nlmsg_pid`: порт (PID) відправника повідомлення.

Заголовок `struct genlmsghdr` іде одразу за базовим заголовком і містить:
- `cmd`: ідентифікатор команди або події (`MPTCP_PM_CMD_*` або `MPTCP_EVENT_*`).
- `version`: версія протоколу MPTCP Netlink (дорівнює `1`).
- `reserved`: зарезервоване поле вирівнювання (2 байти).

### Правила серіалізації та вирівнювання NLA-атрибутів

Кожен атрибут NLA додається до пакета за допомогою макросів `nla_put()` у ядрі або `mnl_attr_put()` у просторі користувача. Базовий тип `struct nlattr` складається з двох полів:
- `nla_len`: 16-бітна загальна довжина атрибута (заголовок 4 байти плюс довжина корисних даних).
- `nla_type`: 16-бітний тип атрибута (`MPTCP_ATTR_*`).

Ядро Linux вимагає, щоб кожен атрибут був вирівняний по 4-байтній межі. Якщо розмір корисного навантаження атрибута не є кратним 4 байтам (наприклад, 1-байтне поле `MPTCP_ATTR_LOC_ID` або 2-байтний порт `MPTCP_ATTR_SPORT`), функція серіалізації автоматично додає від 1 до 3 байтів нульового заповнення (padding). Загальний розмір вирівняного атрибута обчислюється макросом `NLA_ALIGN(nla_len)`.

---

## 2. Мультикаст-події ядра (Kernel Events)

Коли системний параметр `sysctl net.mptcp.pm_type` встановлено у значення `1` (Userspace Path Manager) або коли утиліта `ip mptcp monitor` підключена до мультикаст-групи `subflow`, ядро надсилає сповіщення про зміну стану MPTCP-з'єднань.

Події передаються в заголовку Generic Netlink (`struct genlmsghdr`), де поле `cmd` містить один із ідентифікаторів з переліку `enum mptcp_event_type`:

| Ідентифікатор події | Значення | Опис та тригер у ядрі |
| :--- | :--- | :--- |
| `MPTCP_EVENT_UNSPEC` | `0` | Невизначена подія (використовується як резервне значення). |
| `MPTCP_EVENT_CREATED` | `1` | Створено нове MPTCP-з'єднання. Подія тригерується, коли сокет переходить у стан `TCP_SYN_SENT` або `TCP_SYN_RECV` і бере участь у обміні опціями `MP_CAPABLE`. |
| `MPTCP_EVENT_ESTABLISHED` | `2` | Успішно завершено рукостискання (3-way handshake) основного підпотоку з опцією `MP_CAPABLE`. Сокет готовий до передачі даних. |
| `MPTCP_EVENT_CLOSED` | `3` | MPTCP-з'єднання повністю закрите. Всі підпотоки знищено, сокет очищено з пам'яті. |
| `MPTCP_EVENT_ANNOUNCED` | `4` | Віддалений вузол (Peer) надіслав TCP-опцію `ADD_ADDR` із новою IP-адресою, портом та ідентифікатором `Address ID`. |
| `MPTCP_EVENT_REMOVED` | `5` | Віддалений вузол надіслав TCP-опцію `REMOVE_ADDR` з ідентифікатором адреси (`address_id`). |
| `MPTCP_EVENT_SUB_ESTABLISHED` | `6` | Успішно створено та підключено новий додатковий підпотік (`MP_JOIN`). |
| `MPTCP_EVENT_SUB_CLOSED` | `7` | Додатковий TCP-підпотік закрито або обірвано внаслідок мережевого збою. |
| `MPTCP_EVENT_SUB_PRIO` | `8` | Змінено пріоритет підпотоку (отримано або відправлено опцію `MP_PRIO` чи прапорець `BACKUP`). |
| `MPTCP_EVENT_LISTENER_CREATED`| `9` | Створено слухаючий сокет (bound socket), що очікує нові MPTCP-з'єднання. |
| `MPTCP_EVENT_LISTENER_CLOSED` | `10` | Слухаючий сокет закритий процесом простору користувача. |

### Детальний механізм генерування подій у ядрі

Кожна мультикаст-подія генерується всередині підсистеми MPTCP ядра за допомогою функції `mptcp_nl_mcast_send()`.

Наприклад, при отриманні пакета з TCP-опцією `ADD_ADDR` ядро виконує наступну послідовність дій:
1. Перевіряє валидність HMAC-підпису повідомлення за допомогою ключа з'єднання `struct mptcp_sock`.
2. Якщо HMAC збігається, ядро виділяє новий буфер `sk_buff` для Netlink-повідомлення.
3. Заповнює заголовок Generic Netlink з `cmd = MPTCP_EVENT_ANNOUNCED`.
4. Вкладає атрибути `MPTCP_ATTR_TOKEN`, `MPTCP_ATTR_REM_ID`, `MPTCP_ATTR_FAMILY`, `MPTCP_ATTR_DADDR4`/`DADDR6` та `MPTCP_ATTR_DPORT`.
5. Викликає `genlmsg_multicast()`, транслюючи сповіщення у підписані сокети простору користувача.

---

## 3. Команди Userspace Path Manager (Kernel Commands)

Демон у просторі користувача (наприклад, `mptcpd`) або власна утиліта надсилає командні пакетні запити до ядра через unicast-з'єднання Netlink. Ідентифікатори команд визначаються у `enum mptcp_pm_cmd`:

| Ідентифікатор команди | Значення | Напрямок | Докладний опис дії |
| :--- | :--- | :--- | :--- |
| `MPTCP_PM_CMD_UNSPEC` | `0` | — | Невизначена команда (резерв). |
| `MPTCP_PM_CMD_ADD_ADDR` | `1` | US → Kernel | Наказати ядру згенерувати та відправити TCP-опцію `ADD_ADDR` для вказаного MPTCP-з'єднання (ідентифікується за `MPTCP_ATTR_TOKEN`). |
| `MPTCP_PM_CMD_DEL_ADDR` | `2` | US → Kernel | Наказати ядру відправити TCP-опцію `REMOVE_ADDR` для видалення IP-адреси за її ідентифікатором `MPTCP_ATTR_LOC_ID`. |
| `MPTCP_PM_CMD_GET_ADDR` | `3` | US ↔ Kernel | Отримати детальні метадані про конкретну кінцеву точку (Endpoint). |
| `MPTCP_PM_CMD_FLUSH_ADDRS` | `4` | US → Kernel | Очистити всі локальні кінцеві точки з бази даних ядра. |
| `MPTCP_PM_CMD_SET_LIMITS` | `5` | US → Kernel | Встановити глобальні ліміти `subflows` та `add_addr_accepted` для даної `netns`. |
| `MPTCP_PM_CMD_GET_LIMITS` | `6` | US ↔ Kernel | Запитати поточні значення глобальних лімітів ядра. |
| `MPTCP_PM_CMD_SUBFLOW_CREATE` | `7` | US → Kernel | Наказати ядру відкрити новий TCP-підпотік (`MP_JOIN`) з вказаної локальної IP-адреси/порту на віддалену IP-адресу/порт для конкретного токена. |
| `MPTCP_PM_CMD_SUBFLOW_DESTROY` | `8` | US → Kernel | Примусово закрити конкретний підпотік за його сокетним кортежем 4-tuple. |
| `MPTCP_PM_CMD_SET_FLAGS` | `9` | US → Kernel | Змінити прапорці (наприклад, встановити прапорець `backup` або `fullmesh`) для існуючого підпотоку. |

### Внутрішній шлях виконання команди `MPTCP_PM_CMD_SUBFLOW_CREATE`

Коли простір користувача надсилає команду `MPTCP_PM_CMD_SUBFLOW_CREATE`, ядро виконує обробку у функції `mptcp_pm_nl_subflow_create_doit()`:
1. За атрибутом `MPTCP_ATTR_TOKEN` ядро знаходить відповідний сокет `struct mptcp_sock` у внутрішній хеш-таблиці з'єднань. Якщо токен не знайдено, ядро повертає помилку Netlink `-ENOENT`.
2. Перевіряє наявність локальної та віддаленої адрес у атрибутах `MPTCP_ATTR_SADDR4/6` та `MPTCP_ATTR_DADDR4/6`.
3. Викликає внутрішню функцію ядра `mptcp_subflow_connect()`, яка створює новий сокет `struct socket` із типом `SOCK_STREAM` та протоколом `IPPROTO_TCP`.
4. Прив'язує новий сокет до локального мережевого інтерфейсу `MPTCP_ATTR_IF_INDEX` і виконує системний виклик `kernel_connect()`, генеруючи пакет TCP SYN з опцією `MP_JOIN`.

---

## 4. Атрибути Netlink (Netlink Attributes `MPTCP_ATTR_*`)

Кожне Netlink-повідомлення містить послідовність вкладених атрибутів NLA (`enum mptcp_attr`). Структура `struct nlattr` складається з 16-бітного поля `nla_len` та 16-бітного поля `nla_type`.

Нижче наведено вичерпний опис атрибутів MPTCP:

| Атрибут | Тип NLA | Розмірність | Опис та порядок байтів |
| :--- | :--- | :--- | :--- |
| `MPTCP_ATTR_UNSPEC` | NLA_UNSPEC | — | Невизначений атрибут. |
| `MPTCP_ATTR_TOKEN` | NLA_U32 | 4 байти | Унікальний 32-бітний токен з'єднання (Key HMAC Hash). Порядок байтів — Host Byte Order. |
| `MPTCP_ATTR_FAMILY` | NLA_U16 | 2 байти | Сімейство адрес: `AF_INET` (`2`) або `AF_INET6` (`10`). |
| `MPTCP_ATTR_LOC_ID` | NLA_U8 | 1 байт | Локальний ідентифікатор адреси (`Address ID`, від 0 до 255). |
| `MPTCP_ATTR_REM_ID` | NLA_U8 | 1 байт | Віддалений ідентифікатор адреси, призначений протилежною стороною. |
| `MPTCP_ATTR_SADDR4` | NLA_U32 | 4 байти | Джерельна IPv4-адреса. Порядок байтів — Network Byte Order (Big-Endian). |
| `MPTCP_ATTR_SADDR6` | NLA_BINARY | 16 байтів | Джерельна IPv6-адреса у формі бінарного масиву `struct in6_addr`. |
| `MPTCP_ATTR_DADDR4` | NLA_U32 | 4 байти | Призначена (віддалена) IPv4-адреса (Network Byte Order). |
| `MPTCP_ATTR_DADDR6` | NLA_BINARY | 16 байтів | Призначена IPv6-адреса у формі `struct in6_addr`. |
| `MPTCP_ATTR_SPORT` | NLA_U16 | 2 байти | Джерельний TCP-порт (Network Byte Order). |
| `MPTCP_ATTR_DPORT` | NLA_U16 | 2 байти | Призначений TCP-порт (Network Byte Order). |
| `MPTCP_ATTR_FLAGS` | NLA_U32 | 4 байти | Бітова маска прапорців кінцевої точки (`MPTCP_PM_ADDR_FLAG_*`). |
| `MPTCP_ATTR_SUBFLOW_LIMIT` | NLA_U32 | 4 байти | Глобальний ліміт на кількість додаткових підпотоків. |
| `MPTCP_ATTR_ADD_ADDR_ACCEPTED`| NLA_U32 | 4 байти | Глобальний ліміт прийнятих `ADD_ADDR` від віддаленого вузла. |
| `MPTCP_ATTR_IF_INDEX` | NLA_S32 | 4 байти | Системний індекс мережевого інтерфейсу ядра (`ifindex`). |

### Прапорці адрес (`MPTCP_PM_ADDR_FLAG_*`)

Поле `MPTCP_ATTR_FLAGS` задається маскою бітових прапорців:

:::tabs
```c
/* C UAPI Headers */
#define MPTCP_PM_ADDR_FLAG_SIGNAL        (1 << 0)
#define MPTCP_PM_ADDR_FLAG_SUBFLOW       (1 << 1)
#define MPTCP_PM_ADDR_FLAG_BACKUP        (1 << 2)
#define MPTCP_PM_ADDR_FLAG_FULLMESH      (1 << 3)
#define MPTCP_PM_ADDR_FLAG_IMPLICIT      (1 << 4)
```
```cpp
// C++23 Strongly Typed Enum Bitflags
#include <cstdint>

namespace mptcp::flags {
    enum class AddressFlag : std::uint32_t {
        Signal   = 1 << 0,
        Subflow  = 1 << 1,
        Backup   = 1 << 2,
        Fullmesh = 1 << 3,
        Implicit = 1 << 4
    };

    constexpr AddressFlag operator|(AddressFlag a, AddressFlag b) noexcept {
        return static_cast<AddressFlag>(static_cast<std::uint32_t>(a) | static_cast<std::uint32_t>(b));
    }
}
```
:::

- `MPTCP_PM_ADDR_FLAG_SIGNAL`: вимагає оголошення адреси через `ADD_ADDR`.
- `MPTCP_PM_ADDR_FLAG_SUBFLOW`: вимагає активного створення підпотоків через `MP_JOIN`.
- `MPTCP_PM_ADDR_FLAG_BACKUP`: встановлює біт `B` (Backup) у заголовках.
- `MPTCP_PM_ADDR_FLAG_FULLMESH`: вимагає створення підпотоків до всіх відомих адрес протилежної сторони.
- `MPTCP_PM_ADDR_FLAG_IMPLICIT`: позначає адреси, додані автоматично ядром при отриманні `MP_JOIN` від клієнта.

---

## 5. Довідник CLI: утиліта `ip mptcp`

Команда `ip mptcp` із пакета `iproute2` надає адміністративний інтерфейс для взаємодії з In-Kernel Path Manager.

### 1. Додавання кінцевої точки (`ip mptcp endpoint add`)

Повна форма синтаксису:

```bash
ip mptcp endpoint add <IP-адреса> [ dev <інтерфейс> ] [ id <1-255> ] [ port <порт> ] [ signal | subflow | backup | fullmesh ]
```

#### Параметри:
- `<IP-адреса>`: IPv4 або IPv6 адреса локального мережевого адаптера.
- `dev <інтерфейс>`: назва мережевого пристрою (наприклад, `eth0`, `wlan0`, `wwan0`).
- `id <1-255>`: унікальний числовий ідентифікатор кінцевої точки (`Address ID`). Якщо не вказано, ядро призначає вільний ID автоматично.
- `port <порт>`: спеціальний номер порту для NAT-проходження (якщо оголошувана адреса знаходиться за фаєрволом NAT).
- `signal | subflow | backup | fullmesh`: прапорці поведінки кінцевої точки.

#### Приклади команд:

- Оголосити адресу `192.168.1.100` через `ADD_ADDR`:
  ```bash
  ip mptcp endpoint add 192.168.1.100 dev eth0 id 1 signal
  ```

- Ініціювати створення підпотоку з мобільного інтерфейсу `wwan0`:
  ```bash
  ip mptcp endpoint add 10.80.4.12 dev wwan0 id 2 subflow
  ```

- Створити резервний підпотік з Wi-Fi інтерфейсу:
  ```bash
  ip mptcp endpoint add 192.168.2.50 dev wlan0 id 3 subflow backup
  ```

- Створити повнозв'язну сітку підпотоків:
  ```bash
  ip mptcp endpoint add 10.0.0.15 dev eth1 id 4 subflow fullmesh
  ```

---

### 2. Видалення та перегляд кінцевих точок

- **Відобразити всі зареєстровані кінцеві точки**:
  ```bash
  ip mptcp endpoint show
  ```

- **Видалити кінцеву точку за її `Address ID`**:
  ```bash
  ip mptcp endpoint delete id 1
  ```

- **Видалити кінцеву точку за її IP-адресою**:
  ```bash
  ip mptcp endpoint delete 192.168.1.100
  ```

- **Повністю очистити всі кінцеві точки**:
  ```bash
  ip mptcp endpoint flush
  ```

---

### 3. Управління глобальними лімітами (`ip mptcp limits`)

- **Встановити ліміт на підпотоки та оголошення**:
  ```bash
  ip mptcp limits set subflows 4 add_addr_accepted 3
  ```

- **Переглянути поточні обмеження**:
  ```bash
  ip mptcp limits show
  ```

---

### 4. Монітор подій у реальному часі (`ip mptcp monitor`)

Утиліта `ip mptcp monitor` слухає мультикаст-групу `subflow` і декодує Netlink-повідомлення у зручний текстовий вивід:

```bash
ip mptcp monitor
```

#### Приклад виводу у консолі:

```text
[        CREATED] token=a1b2c3d4 family=2 saddr4=192.168.1.50 daddr4=203.0.113.10 sport=45210 dport=443
[    ESTABLISHED] token=a1b2c3d4 family=2 saddr4=192.168.1.50 daddr4=203.0.113.10 sport=45210 dport=443
[      ANNOUNCED] token=a1b2c3d4 rem_id=2 family=2 daddr4=203.0.113.11 dport=443
[SUB_ESTABLISHED] token=a1b2c3d4 loc_id=2 rem_id=2 saddr4=10.0.0.2 daddr4=203.0.113.11 sport=51204 dport=443
[     SUB_CLOSED] token=a1b2c3d4 loc_id=2 rem_id=2 saddr4=10.0.0.2 daddr4=203.0.113.11 sport=51204 dport=443
[         CLOSED] token=a1b2c3d4
```

---

## 6. Конфігурація параметрів ядра через `sysctl`

Підсистема MPTCP керується наступними ключовими параметрами ядра:

- **`net.mptcp.enabled`**: глобальний перемикач MPTCP (1 — увімкнено, 0 — вимкнено).
- **`net.mptcp.pm_type`**: вибір типу менеджера шляхів (0 — In-Kernel PM, 1 — Userspace PM / `mptcpd`).
- **`net.mptcp.add_addr_timeout`**: тайм-аут у секундах для повторної відправки `ADD_ADDR` при відсутності відповіді (за замовчуванням 120 секунд).
- **`net.mptcp.stale_loss_cnt`**: кількість послідовних втрат пакетів, після яких підпотік вважається «застряглим» (stale) і тимчасово виключається з планувальника.
- **`net.mptcp.checksum_enabled`**: увімкнення додаткової контрольної суми MPTCP DSS Checksum для захисту від спотворення даних Middlebox-пристроями.

Приклад налаштування через `/etc/sysctl.d/99-mptcp.conf`:

```ini
net.mptcp.enabled = 1
net.mptcp.pm_type = 0
net.mptcp.add_addr_timeout = 60
net.mptcp.stale_loss_cnt = 4
net.mptcp.checksum_enabled = 1
```

Кожен із цих параметрів змінює стан внутрішнього контролера MPTCP у ядрі. Зміна `net.mptcp.pm_type` у реальному часі впливає лише на нові MPTCP-з'єднання, тоді як існуючі з'єднання зберігають той режим керування шляхами, з яким вони були ініціалізовані під час рукостискання `MP_CAPABLE`.
