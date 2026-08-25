# 📋 Специфікація повідомлень та опкодів протоколу vhost-user

Протокол vhost-user визначає двійковий формат обміну керуючими повідомленнями між процесом гіпервізора (Master / Frontend) та зовнішнім сервером простору користувача (Slave / Backend) через локальний потоковий сокет домену Unix (`AF_UNIX`).

## Загальна структура повідомлення

Кожен пакет протоколу передається як цілісний кадр, що складається з фіксованого 12-байтового заголовка та змінного тіла (payload), розмір якого вказано в полі заголовка `size`. Опціонально разом із заголовком через допоміжні керуючі повідомлення сокета (`ancillary data`, `SCM_RIGHTS`) операційна система Linux може передавати масив відкритих файлових дескрипторів ядра.

Порядок байтів у всіх числових полях заголовка та корисного навантаження — виключно Little-Endian. Якщо хост і гість мають різну архітектурну розрядність чи порядок байтів, сторони зобов'язані узгодити прапорець `VHOST_USER_PROTOCOL_F_CROSS_ENDIAN` до передачі будь-яких структур даних.

:::tabs
```c
/* Двійковий заголовок та універсальний конверт повідомлення vhost-user */
struct vhost_user_msg {
    uint32_t request;          /* Код запиту або відповіді (опкод) */
    uint32_t flags;            /* Бітові прапорці версії, напрямку та підтвердження */
    uint32_t size;             /* Розмір корисного навантаження (payload) у байтах */
    union {
        uint64_t u64;
        struct vhost_user_vring_state state;
        struct vhost_user_vring_addr addr;
        struct vhost_user_memory memory;
        struct vhost_user_log log;
        struct vhost_user_config config;
        struct vhost_user_inflight inflight;
        uint8_t raw[1024];
    } payload;
} __attribute__((packed));
```
```cpp
#include <cstdint>
#include <cstddef>

/* Двійковий заголовок та типізований конверт повідомлення vhost-user у C++ */
struct alignas(4) VhostUserHeader {
    uint32_t request{0};       // Код запиту або відповіді (опкод)
    uint32_t flags{0};         // Бітові прапорці версії, напрямку та підтвердження
    uint32_t size{0};          // Розмір корисного навантаження (payload) у байтах
};

struct VhostUserMsgRaw {
    VhostUserHeader header;
    uint8_t payload[1024];
};
```
:::

### Бітові прапорці заголовка (`flags`)

Поле `flags` містить метадані, необхідні для демультиплексування запитів, перевірки сумісності версій та синхронізації відповідей:

| Біт | Назва | Опис |
| :--- | :--- | :--- |
| `0..1` | `VHOST_USER_VERSION_MASK` | Маска версії протоколу. Поточна версія стандарту дорівнює `0x1`. Повідомлення з іншими значеннями відкидаються. |
| `2` | `VHOST_USER_FLAG_REPLY` | Ознака відповіді. Встановлюється в `1`, якщо пакет є відповіддю на раніше надісланий запит, і `0`, якщо це первинний запит. |
| `3` | `VHOST_USER_FLAG_NEED_REPLY` | Вимога підтвердження. Якщо встановлено, сервер зобов'язаний надіслати у відповідь пакет з результатом виконання (потребує `VHOST_USER_PROTOCOL_F_REPLY_ACK`). |

Синхронний режим `VHOST_USER_FLAG_NEED_REPLY` має вирішальне значення під час зміни конфігурації в реальному часі. Наприклад, перед тим як демонтувати застарілу область пам'яті VM, гіпервізор зобов'язаний переконатися, що сервер завершив усі операції читання й скинув внутрішні кеші.

## Модель синхронізації та стани з'єднання

Протокол vhost-user реалізує детерміновану скінченну автоматно-орієнтовану модель станів (state machine). Перехід між станами відбувається строго за послідовністю команд від Master до Slave:

1. **Стан ініціалізації (Uninitialized)**: сокет відкрито, але обробка запитів заблокована. На цій фазі виконується виключно обмін `GET_FEATURES` та `SET_FEATURES`. Будь-які спроби надіслати команди роботи з чергами ігноруються або призводять до закриття з'єднання.
2. **Стан відображення пам'яті (Memory Configured)**: після успішного виконання `VHOST_USER_SET_MEM_TABLE` сервер отримує дескриптори та монтує таблиці пам'яті. З цього моменту сервер готовий до трансляції адрес, але черги залишаються неактивними.
3. **Стан налаштування віртчерг (Rings Configured)**: сторони передають розміри кілець (`SET_VRING_NUM`), базові адреси структур (`SET_VRING_ADDR`) та дескриптори сигналізації (`SET_VRING_KICK`, `SET_VRING_CALL`). Сервер валідує адреси та перевіряє, що всі кільця потрапляють у межі зареєстрованих регіонів спільної пам'яті.
4. **Активний дата-плейн (Active Data Plane)**: команда `VHOST_USER_SET_VRING_ENABLE` з ненульовим значенням переводить чергу в робочий режим. Сервер запускає потік опитування або реєструє `kick_fd` у своєму циклі подій (event loop).
5. **Призупинення та заморожування (Quiesced / Migrating)**: команда `VHOST_USER_GET_VRING_BASE` зупиняє роботу черги, змушуючи сервер скинути незавершені операції та повернути останній збережений індекс обробки для збереження цілісності перед міграцією.

## Узгодження можливостей протоколу (Protocol Features)

Протокол vhost-user розділяє можливості на два незалежні простори:
1. **Virtio Features (64-бітне значення)**: стандартні можливості конкретного віртуального пристрою virtio (наприклад, підтримка контрольних сум `VIRTIO_NET_F_CSUM`, розріджених буферів `VIRTIO_NET_F_MRG_RXBUF` чи розміру сектора `VIRTIO_BLK_F_BLK_SIZE`).
2. **Protocol Features (64-бітне значення)**: можливості самого транспортного протоколу vhost-user, що узгоджуються між процесами за допомогою опкодів `VHOST_USER_GET_PROTOCOL_FEATURES` та `VHOST_USER_SET_PROTOCOL_FEATURES`.

Узгодження протокольних можливостей відбувається лише в тому випадку, якщо в загальних virtio features встановлено біт `VHOST_USER_F_PROTOCOL_FEATURES` (біт 30).

| Біт | Назва макросу | Значення та функціональне призначення |
| :--- | :--- | :--- |
| `0` | `VHOST_USER_PROTOCOL_F_MQ` | Підтримка багаточерговості (Multiqueue). Дозволяє створювати кілька пар віртчерг для паралельної обробки на різних процесорних ядрах. |
| `1` | `VHOST_USER_PROTOCOL_F_LOG_SHMFD` | Передача дескриптора розділюваної пам'яті для бітової карти змінених сторінок при живій міграції. |
| `2` | `VHOST_USER_PROTOCOL_F_RARP` | Генерація RARP-пакетів сервером після завершення міграції для негайного оновлення таблиць комутації хоста. |
| `3` | `VHOST_USER_PROTOCOL_F_REPLY_ACK` | Синхронне підтвердження виконання команд: сервер надсилає числовий статус `0` (успіх) на кожен запит із прапорцем `NEED_REPLY`. |
| `4` | `VHOST_USER_PROTOCOL_F_NET_MTU` | Можливість отримання максимального розміру корисного навантаження кадру (MTU) від сервера. |
| `5` | `VHOST_USER_PROTOCOL_F_SLAVE_REQ` | Створення зворотного каналу зв'язку від Slave/Backend до Master/Frontend для асинхронних запитів. |
| `6` | `VHOST_USER_PROTOCOL_F_CROSS_ENDIAN` | Підтримка систем із різним порядком розташування байтів у пам'яті. |
| `7` | `VHOST_USER_PROTOCOL_F_CRYPTO_SESSION` | Керування сесіями симетричного та асиметричного шифрування для virtio-crypto. |
| `8` | `VHOST_USER_PROTOCOL_F_PAGEFAULT` | Підтримка перехоплення сторінкових промахів через інтерфейс ядра `userfaultfd` під час post-copy міграції. |
| `9` | `VHOST_USER_PROTOCOL_F_CONFIG` | Читання та динамічна зміна простору конфігурації пристрою (`get_config` / `set_config`). |
| `10` | `VHOST_USER_PROTOCOL_F_SLAVE_SEND_FD` | Дозвіл бекенду надсилати дескриптори файлів у зворотному напрямку до гіпервізора. |
| `11` | `VHOST_USER_PROTOCOL_F_HOST_NOTIFIER` | Пряме відображення апаратних регістрів сповіщення (doorbells) контролерів у простір гостя. |
| `12` | `VHOST_USER_PROTOCOL_F_INFLIGHT_SHMFD` | Збереження стану активних незавершених дескрипторів у розділюваній пам'яті для відновлення після краху. |
| `13` | `VHOST_USER_PROTOCOL_F_RESET_DEVICE` | Окреме програмне скидання стану черг пристрою без розриву сокетного IPC-з'єднання. |

## Повний перелік опкодів протоколу

Усі запити передаються від Master до Slave, за винятком команд зворотного каналу, активованого прапорцем `VHOST_USER_PROTOCOL_F_SLAVE_REQ`:

| Код | Символьна назва опкоду | Напрямок | Тіло повідомлення (Payload) | Наявність FD (`SCM_RIGHTS`) |
| :---: | :--- | :---: | :--- | :---: |
| `1` | `VHOST_USER_GET_FEATURES` | M → S | Порожнє (розмір 0) | Ні (відповідь повертає `uint64_t`) |
| `2` | `VHOST_USER_SET_FEATURES` | M → S | `uint64_t` (біти virtio features) | Ні |
| `3` | `VHOST_USER_SET_OWNER` | M → S | Порожнє (розмір 0) | Ні |
| `4` | `VHOST_USER_RESET_OWNER` | M → S | Порожнє (розмір 0) | Ні |
| `5` | `VHOST_USER_SET_MEM_TABLE` | M → S | `struct vhost_user_memory` | **Так** (масив дескрипторів пам'яті) |
| `6` | `VHOST_USER_SET_LOG_BASE` | M → S | `struct vhost_user_log` | **Так** (якщо активний `LOG_SHMFD`) |
| `7` | `VHOST_USER_SET_LOG_FD` | M → S | `uint64_t` (службовий параметр) | **Так** (1 fd лог-файлу) |
| `8` | `VHOST_USER_SET_VRING_NUM` | M → S | `struct vhost_user_vring_state` | Ні |
| `9` | `VHOST_USER_SET_VRING_ADDR` | M → S | `struct vhost_user_vring_addr` | Ні |
| `10` | `VHOST_USER_SET_VRING_BASE` | M → S | `struct vhost_user_vring_state` | Ні |
| `11` | `VHOST_USER_GET_VRING_BASE` | M → S | `struct vhost_user_vring_state` | Ні (відповідь містить збережений індекс) |
| `12` | `VHOST_USER_SET_VRING_KICK` | M → S | `struct vhost_user_vring_state` | **Так** (1 fd: `kick_fd` / `ioeventfd`) |
| `13` | `VHOST_USER_SET_VRING_CALL` | M → S | `struct vhost_user_vring_state` | **Так** (1 fd: `call_fd` / `irqfd`) |
| `14` | `VHOST_USER_SET_VRING_ERR` | M → S | `struct vhost_user_vring_state` | **Так** (1 fd для сигналізації помилок) |
| `15` | `VHOST_USER_GET_PROTOCOL_FEATURES` | M → S | Порожнє (розмір 0) | Ні (відповідь повертає `uint64_t`) |
| `16` | `VHOST_USER_SET_PROTOCOL_FEATURES` | M → S | `uint64_t` (біти protocol features) | Ні |
| `18` | `VHOST_USER_SET_VRING_ENABLE` | M → S | `struct vhost_user_vring_state` | Ні |
| `24` | `VHOST_USER_GET_CONFIG` | M → S | `struct vhost_user_config` | Ні (відповідь містить байти конфігурації) |
| `25` | `VHOST_USER_SET_CONFIG` | M → S | `struct vhost_user_config` | Ні |
| `28` | `VHOST_USER_POSTCOPY_ADVISE` | M → S | Порожнє (розмір 0) | **Так** (дескриптор `userfaultfd`) |
| `29` | `VHOST_USER_POSTCOPY_LISTEN` | M → S | Порожнє (розмір 0) | Ні |
| `30` | `VHOST_USER_POSTCOPY_END` | M → S | `uint64_t` (результат завершення) | Ні |
| `31` | `VHOST_USER_GET_INFLIGHT_FD` | M → S | `struct vhost_user_inflight` | **Так** (відповідь повертає спільний fd) |
| `32` | `VHOST_USER_SET_INFLIGHT_FD` | M → S | `struct vhost_user_inflight` | **Так** (передається дескриптор буфера) |

## Детальний розбір структур корисного навантаження

### 1. Таблиця пам'яті: `struct vhost_user_memory`

Використовується в запиті `VHOST_USER_SET_MEM_TABLE`. Повідомлення містить список регіонів оперативної пам'яті віртуальної машини, які сервер зобов'язаний відобразити у власний адресний простір за допомогою системного виклику `mmap()`.

:::tabs
```c
struct vhost_user_memory_region {
    uint64_t guest_phys_addr;   /* Базова адреса регіону в фізичній пам'яті гостя (GPA) */
    uint64_t memory_size;       /* Розмір регіону в байтах */
    uint64_t userspace_addr;    /* Віртуальна адреса регіону в просторі процесу QEMU (QEMU HVA) */
    uint64_t mmap_offset;       /* Зміщення всередині файлу розділюваної пам'яті */
};

struct vhost_user_memory {
    uint32_t nregions;          /* Кількість переданих регіонів */
    uint32_t padding;           /* Вирівнювання структури до 8 байтів */
    struct vhost_user_memory_region regions[8];
};
```
```cpp
#include <cstdint>
#include <array>

struct VhostUserMemoryRegion {
    uint64_t guest_phys_addr{0};  // Базова адреса в пам'яті гостя (GPA)
    uint64_t memory_size{0};      // Розмір регіону в байтах
    uint64_t userspace_addr{0};   // Віртуальна адреса в QEMU (QEMU HVA)
    uint64_t mmap_offset{0};      // Зміщення від початку файлу
};

struct VhostUserMemory {
    uint32_t nregions{0};         // Кількість регіонів
    uint32_t padding{0};
    std::array<VhostUserMemoryRegion, 8> regions{};
};
```
:::

Кількість файлових дескрипторів, переданих через `SCM_RIGHTS` у масиві допоміжних даних сокета, має точно дорівнювати полю `nregions`. `i`-й дескриптор відповідає `i`-му регіону в масиві `regions`. Якщо кількість дескрипторів менша або перевищує `nregions`, повідомлення вважається недійсним і з'єднання негайно розривається.

### 2. Стан віртчерги: `struct vhost_user_vring_state`

Застосовується в командах `VHOST_USER_SET_VRING_NUM`, `SET_VRING_BASE`, `GET_VRING_BASE`, `SET_VRING_ENABLE`:

:::tabs
```c
struct vhost_user_vring_state {
    uint32_t index;             /* Індекс черги virtqueue (наприклад, 0 для RX, 1 для TX) */
    uint32_t num;               /* Розмір кільця (кількість дескрипторів) або прапорець enable (0/1) */
};
```
```cpp
#include <cstdint>

struct VhostUserVringState {
    uint32_t index{0};          // Індекс черги virtqueue
    uint32_t num{0};            // Розмір кільця або статус активації
};
```
:::

### 3. Адреси структур кільця: `struct vhost_user_vring_addr`

Використовується в запиті `VHOST_USER_SET_VRING_ADDR`. Передає віртуальні адреси трьох частин класичної virtqueue у просторі процесу QEMU (HVA):

:::tabs
```c
struct vhost_user_vring_addr {
    uint32_t index;             /* Індекс черги */
    uint32_t flags;             /* Прапорці конфігурації (наприклад, VHOST_VRING_F_LOG) */
    uint64_t desc_user_addr;    /* Адреса таблиці дескрипторів у QEMU HVA */
    uint64_t used_user_addr;    /* Адреса кільця використаних буферів у QEMU HVA */
    uint64_t avail_user_addr;   /* Адреса кільця доступних буферів у QEMU HVA */
    uint64_t log_guest_addr;    /* Адреса для логування змін під час живої міграції */
};
```
```cpp
#include <cstdint>

struct VhostUserVringAddr {
    uint32_t index{0};           // Індекс черги
    uint32_t flags{0};           // Прапорці конфігурації
    uint64_t desc_user_addr{0};  // Адреса Descriptor Table у QEMU HVA
    uint64_t used_user_addr{0};  // Адреса Used Ring у QEMU HVA
    uint64_t avail_user_addr{0}; // Адреса Avail Ring у QEMU HVA
    uint64_t log_guest_addr{0};  // Адреса для логування під час міграції
};
```
:::

Отримавши ці адреси, сервер знаходить відповідний регіон у своїй таблиці пам'яті за адресою `userspace_addr` і перераховує покажчики `desc_user_addr`, `used_user_addr` та `avail_user_addr` у власний віртуальний простір адресації.

### 4. Відстеження незавершених операцій: `struct vhost_user_inflight`

Забезпечує відновлення стану пристрою після аварійного перезапуску сервера (`VHOST_USER_PROTOCOL_F_INFLIGHT_SHMFD`):

:::tabs
```c
struct vhost_user_inflight {
    uint64_t mmap_size;         /* Розмір буфера спільної пам'яті відстеження */
    uint64_t mmap_offset;       /* Зміщення у переданому файловому дескрипторі */
    uint16_t num_queues;        /* Загальна кількість черг пристрою */
    uint16_t queue_size;        /* Місткість однієї черги (кількість елементів) */
    uint32_t inflight_split;    /* Версія структури журналу для split virtqueue */
};
```
```cpp
#include <cstdint>

struct VhostUserInflight {
    uint64_t mmap_size{0};      // Розмір буфера спільної пам'яті
    uint64_t mmap_offset{0};    // Зміщення у файлі
    uint16_t num_queues{0};     // Загальна кількість черг
    uint16_t queue_size{0};     // Місткість однієї черги
    uint32_t inflight_split{0}; // Версія формату журналу
};
```
:::

Цей буфер містить дві таблиці: таблицю опису дескрипторів та кільцевий журнал обробки. Коли бекенд бере дескриптор із черги, він встановлює прапорець `inflight = 1`. Після успішного запису даних на фізичний носій або в мережу прапорець скидається в `0`. Якщо сервер аварійно завершується, новий процес зчитує ці записи, завершує завислі операції і повертає гостю коректний статус без пошкодження файлових систем.

## Специфікація Post-Copy міграції

Процес post-copy міграції через vhost-user вимагає спеціальної трифазної процедури передачі сторінкових помилок:

1. **`VHOST_USER_POSTCOPY_ADVISE`**: QEMU відкриває дескриптор `userfaultfd` у ядрі хоста і передає його серверу через `SCM_RIGHTS`. Сервер дублює цей дескриптор і готується до перехоплення звернень до неініціалізованої пам'яті.
2. **`VHOST_USER_POSTCOPY_LISTEN`**: повідомляє серверу, що віртуальна машина перейшла в режим post-copy і починає виконання на цільовому вузлі. Сервер активує реєстрацію регіонів пам'яті через `ioctl(uffd, UFFDIO_REGISTER, ...)`. Якщо робочий потік PMD звернеться до сторінки, яка ще знаходиться в дорозі по мережі, ядро хоста автоматично призупинить потік.
3. **`VHOST_USER_POSTCOPY_END`**: після того, як гіпервізор переніс останню відсутню сторінку пам'яті через мережу і розблокував усі завислі сторінкові промахи через `UFFDIO_COPY`, надсилається команда завершення post-copy. Сервер закриває дескриптор `userfaultfd` і повертається до звичайного високошвидкісного режиму роботи.
