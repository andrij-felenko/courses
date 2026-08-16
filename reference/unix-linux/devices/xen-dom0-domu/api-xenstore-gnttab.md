# 📋 Структура даних Xenstore, Xenbus та Grant Table entries

Ця вставка містить детальні довідкові структури даних, розмітку пам'яті, інтерфейси системних викликів ioctl та схему каталогу Xenstore. Опис призначено для глибокого аналізу механізмів міждоменного обміну даними та розробки розділених драйверів (split drivers) під гіпервізором Xen.

## 1. Схема ієрархічного дерева Xenstore та права доступу

Xenstore являє собою централізовану базу даних типу "ключ-значення" з файловоподібною ієрархічною структурою шляхів. Доступ до ключів керується списком контролю доступу (ACL). Кожен вузол має власника (домен) та набір прав для інших доменів: `r` (read), `w` (write), `b` (both / read-write) або `n` (none). Dom0 володіє коренем дерева за замовчуванням і має необмежений доступ до всіх гілок.

Дерево Xenstore розділене на три основні функціональні зони:
- `/local/domain/<domid>/`: персональна гілка домену, де зберігаються глобальні параметри віртуальної машини, конфігурація VCPU, ліміти ОЗП та точки підключення фронтенд-драйверів.
- `/backend/<type>/<domid>/<devid>/`: гілка в просторі Dom0, у якій зберігається прив'язка бекендів до реальних пристроїв хоста (файли дисків, блокові пристрої, мережеві мости).
- `/tool/`: службові параметри утиліт управління toolstack.

```
/
├── local/
│   └── domain/
│       ├── 0/                      # Простір привілейованого Dom0
│       │   ├── name = "Domain-0"
│       │   └── domid = 0
│       └── <domid>/                # Простір непривілейованого гостя (DomU)
│           ├── name = "guest-vm1"
│           ├── domid = "<domid>"
│           ├── cpu/                # Конфігурація віртуальних ядер VCPU
│           ├── memory/
│           │   └── target = "4194304" # Цільовий обсяг ОЗП у кілобайтах (= 4 ГіБ)
│           ├── store/
│           │   ├── port = "1"      # Номер порту Event Channel для зв'язку з xenstored
│           │   └── ring-ref = "8"  # Номер Grant Reference сторінки спільної пам'яті Xenstore
│           ├── device/             # Дерево конфігурації фронтенд-драйверів
│           │   ├── vbd/            # Virtual Block Device (дискова підсистема)
│           │   │   └── 768/
│           │   │       ├── backend = "/local/domain/0/backend/vbd/<domid>/768"
│           │   │       ├── backend-id = "0"
│           │   │       ├── state = "4" # Поточний стан (XenbusStateConnected)
│           │   │       ├── ring-ref = "128" # Grant Ref спільної сторінки I/O кільця
│           │   │       └── event-channel = "14" # Порт сповіщень про I/O
│           │   └── vif/            # Virtual Network Interface ( мережева підсистема)
│           │       └── 0/
│           │           ├── backend = "/local/domain/0/backend/vif/<domid>/0"
│           │           └── state = "4"
│           └── control/
│               └── shutdown = ""   # Прапор примусового вимкнення або перезавантаження
└── backend/                        # Дерево конфігурації бекенд-драйверів у Dom0
    ├── vbd/
    │   └── <domid>/
    │       └── 768/
    │           ├── frontend = "/local/domain/<domid>/device/vbd/768"
    │           ├── frontend-id = "<domid>"
    │           ├── state = "4"
    │           ├── dev = "xvda"
    │           └── params = "/var/lib/xen/images/disk.raw"
    └── vif/
        └── <domid>/
            └── 0/
                ├── frontend = "/local/domain/<domid>/device/vif/0"
                └── bridge = "xenbr0"
```

Зміна параметрів у деревоподібній структурі Xenstore виконується за допомогою атомарних транзакцій (`xenbus_transaction_start` та `xenbus_transaction_end`). У разі виникнення конфлікту паралельних записів транзакція повертає помилку `EAGAIN` і має бути повторена.

## 2. Перелічення станів Xenbus та автомат узгодження

Взаємодія та синхронізація станів між фронтендом у DomU та бекендом у Dom0 виконується за допомогою автомата станів Xenbus. Стан кожного пристрою кодується цілочисельним значенням `enum xenbus_state`, яке записується десятковим числом у текстовому вигляді у відповідний ключ `state` в ієрархії Xenstore.

Обидві сторони підписуються на зміни ключів `state` за допомогою механізму спостерігачів (Watches). При зміні стану `xenstored` надсилає підписникам сповіщення, а гіпервізор доставляє його як подію в Event Channel, змушуючи відповідне ядро перевірити новий стан.

:::tabs
```c
enum xenbus_state {
    XenbusStateUnknown      = 0,  /* Невідомий стан або пристрій відсутній */
    XenbusStateInitialising = 1,  /* Драйвер виявлено, ініціалізація локальних ресурсів */
    XenbusStateInitWait     = 2,  /* Ресурси виділено, очікування відповіді від протилежної сторони */
    XenbusStateInitialised  = 3,  /* Налаштування завершено, готовність до підключення */
    XenbusStateConnected    = 4,  /* Кільце I/O та Event Channel активні, йде обмін даними */
    XenbusStateClosing      = 5,  /* Запит на відключення пристрою (підготовка до видалення) */
    XenbusStateClosed       = 6,  /* Пристрій повністю відключено та розмаплено */
    XenbusStateReconfiguring= 7,  /* Зміна конфігурації пристрою на льоту (наприклад, зміна розміру) */
    XenbusStateReconfigured = 8   /* Завершення підтвердження зміни конфігурації */
};
```
```cpp
enum class XenbusState : std::uint32_t {
    Unknown      = 0,  // Невідомий стан або пристрій відсутній
    Initialising = 1,  // Драйвер виявлено, ініціалізація локальних ресурсів
    InitWait     = 2,  // Ресурси виділено, очікування відповіді від протилежної сторони
    Initialised  = 3,  // Налаштування завершено, готовність до підключення
    Connected    = 4,  // Кільце I/O та Event Channel активні, йде обмін даними
    Closing      = 5,  // Запит на відключення пристрою
    Closed       = 6,  // Пристрій повністю відключено та розмаплено
    Reconfiguring= 7,  // Зміна конфігурації пристрою на льоту
    Reconfigured = 8   // Завершення підтвердження зміни конфігурації
};
```
:::

Якщо під час ініціалізації виникає збій (наприклад, неможливість виділити gref чи порт подій), пристрій переходить у стан `XenbusStateClosing` або `Closed`, а в ключ `error` записується текстовий опис помилки.

## 3. Структура записів Grant Table: версії 1 і 2

Таблиця грантів (Grant Table) містить інформацію про правила доступу до сторінок пам'яті, наданих іншим доменам. Залежно від конфігурації ядра та версії Xen використовуються записи версії 1 (`grant_entry_v1_t`) або версії 2 (`grant_entry_v2_t`).

### Версія 1 (`grant_entry_v1_t`)
Структура V1 є компактною і займає рівно 8 байтів на один запис. Вона містить 16-бітний ідентифікатор цільового домену, 16-бітну маску прапорців та 32-бітний номер кадру машинної сторінки (Machine Frame Number, MFN).

:::tabs
```c
struct grant_entry_v1 {
    uint16_t flags;    /* Прапорці доступу (GTF_permit_access, GTF_reading, GTF_writing) */
    domid_t  domid;    /* ID домену, якому надається доступ (наприклад, 0 для Dom0) */
    uint32_t frame;    /* Machine Frame Number (MFN) фізичної сторінки ОЗП */
};
typedef struct grant_entry_v1 grant_entry_v1_t;

/* Основні бітові прапорці flags */
#define GTF_invalid       (0U<<0) /* Запис недійсний / вільний для використання */
#define GTF_permit_access (1U<<0) /* Надано дозвіл на відображення сторінки іншим доменом */
#define GTF_accept_transfer (2U<<0) /* Надано дозвіл на повну передачу власності сторінки */
#define GTF_readonly      (1U<<2) /* Дозвіл тільки для читання (якщо не встановлено — читання/запис) */
#define GTF_reading       (1U<<3) /* Встановлюється гіпервізором: домен наразі мапить для читання */
#define GTF_writing       (1U<<4) /* Встановлюється гіпервізором: домен наразі мапить для запису */
```
```cpp
struct GrantEntryV1 {
    std::uint16_t flags; /* Прапорці доступу (GTF_permit_access, GTF_reading, GTF_writing) */
    std::uint16_t domid; /* ID домену, якому надається доступ (domid_t) */
    std::uint32_t frame; /* Machine Frame Number (MFN) фізичної сторінки ОЗП */
};

// Прапорці у вигляді константних виразів C++20
namespace GrantFlags {
    constexpr std::uint16_t Invalid        = 0U << 0; // Запис недійсний / вільний
    constexpr std::uint16_t PermitAccess   = 1U << 0; // Надано дозвіл на відображення сторінки
    constexpr std::uint16_t AcceptTransfer = 2U << 0; // Надано дозвіл на передачу власності сторінки
    constexpr std::uint16_t ReadOnly       = 1U << 2; // Дозвіл тільки для читання
    constexpr std::uint16_t Reading        = 1U << 3; // Встановив гіпервізор: домен мапить для читання
    constexpr std::uint16_t Writing        = 1U << 4; // Встановив гіпервізор: домен мапить для запису
}
```
:::

### Версія 2 (`grant_entry_v2_t`)
Структура V2 розширена до 16 байтів. Вона розроблена для підтримки 64-бітних MFN в архітектурах із обсягом ОЗП понад 16 терабайтів, а також дозволяє надавати доступ до окремих суб-сторінкових фрагментів (суб-гранти із зазначенням зміщення `page_off` та довжини `length`).

:::tabs
```c
union grant_entry_v2 {
    struct {
        uint16_t flags;
        domid_t  domid;
        uint32_t pad0;
        uint64_t frame;     /* 64-бітний MFN для систем з ОЗП понад 16 ТіБ */
    } full_page;
    struct {
        uint16_t flags;
        domid_t  domid;
        uint16_t page_off;  /* Зміщення всередині сторінки в байтах від початку кадру */
        uint16_t length;    /* Довжина дозволеного фрагмента в байтах */
        uint64_t frame;     /* MFN сторінки, фрагмент якої відкрито */
    } sub_page;
};
typedef union grant_entry_v2 grant_entry_v2_t;
```
```cpp
union GrantEntryV2 {
    struct FullPage {
        std::uint16_t flags;
        std::uint16_t domid;
        std::uint32_t pad0;
        std::uint64_t frame;     // 64-бітний MFN для ОЗП понад 16 ТіБ
    } full_page;

    struct SubPage {
        std::uint16_t flags;
        std::uint16_t domid;
        std::uint16_t page_off;  // Зміщення всередині сторінки в байтах
        std::uint16_t length;    // Довжина дозволеного фрагмента
        std::uint64_t frame;     // MFN сторінки, фрагмент якої відкрито
    } sub_page;
};
```
:::

При зміні прапорців гіпервізор виконує атомарні бітові операції (наприклад, `lock bts` на x86), що унеможливлює стан перегонів при одночасному зверненні кількох CPU.

## 4. Інтерфейс ioctl пристрою `/dev/xen/gntdev`

Символьний пристрій `/dev/xen/gntdev` надає інтерфейс для простору користувача у Dom0, дозволяючи відображати міждоменні гранти у віртуальний адресний простір процесів бекенда за допомогою виклику `mmap()`.

Основними командами керування `ioctl` є:
- `IOCTL_GNTDEV_MAP_GRANT_REF`: надсилає запит гіпервізору на перевірку прав та мапування грантів. Повертає псевдо-зміщення (`index`), яке передається аргументом `offset` у виклик `mmap()`.
- `IOCTL_GNTDEV_UNMAP_GRANT_REF`: звільняє мапування за вказаним зміщенням `index`, викликаючи вилучення сторінок із таблиць сторінок процесу та інвалідацію кешу TLB.

:::tabs
```c
/* Структура запиту на відображення грантів */
struct ioctl_gntdev_map_grant_ref {
    uint32_t count; /* Кількість грантів у масиві refs */
    uint32_t pad;
    struct ioctl_gntdev_grant_ref {
        uint32_t domid; /* ID домену-власника сторінки (DomU) */
        uint32_t ref;   /* Індекс grant reference (gref) */
    } refs[1];          /* Динамічний масив елементів для пакетного мапування */

    uint64_t index;     /* Вихідне псевдо-зміщення для подальшого виклику mmap() */
};

/* Структура запиту на зняття відображення */
struct ioctl_gntdev_unmap_grant_ref {
    uint64_t index;     /* Зміщення, отримане під час виклику MAP ioctl */
    uint32_t count;     /* Кількість сторінок для unmap */
    uint32_t pad;
};

#define IOCTL_GNTDEV_MAP_GRANT_REF   _IOC(_IOC_NONE, 'G', 0, sizeof(struct ioctl_gntdev_map_grant_ref))
#define IOCTL_GNTDEV_UNMAP_GRANT_REF _IOC(_IOC_NONE, 'G', 1, sizeof(struct ioctl_gntdev_unmap_grant_ref))
```
```cpp
// C++ структура запиту відображення грантів
struct GntdevMapGrantRef {
    std::uint32_t count; // Кількість грантів у масиві
    std::uint32_t pad;
    struct GrantRef {
        std::uint32_t domid; // ID домену-власника
        std::uint32_t ref;   // Індекс grant reference (gref)
    } refs[1];

    std::uint64_t index; // Віртуальне зміщення для виклику mmap()
};

struct GntdevUnmapGrantRef {
    std::uint64_t index; // Зміщення, отримане під час map
    std::uint32_t count; // Кількість сторінок для unmap
    std::uint32_t pad;
};
```
:::

## 5. Інтерфейс ioctl пристрою `/dev/xen/evtchn`

Символьний пристрій `/dev/xen/evtchn` надає процесам у просторі користувача можливість прив'язуватися до віртуальних каналів подій Event Channels та генерувати переривання.

Пристрій підтримує неблокуючий доступ (`O_NONBLOCK`) та стандартні виклики `poll()` / `select()`. Коли на прив'язаному порту відбувається виклик upcall, системний виклик `read()` повертає номер порту, на якому виникло переривання.

:::tabs
```c
/* Прив'язка до незв'язаного порту Event Channel.
   Номер виділеного локального порту повертає сам ioctl своїм значенням —
   окремого вихідного поля в структурі немає. */
struct ioctl_evtchn_bind_unbound_port {
    unsigned int remote_domain; /* ID домену, якому дозволено з'єднатися */
};

/* Надсилання сповіщення у порт (генерація upcall) */
struct ioctl_evtchn_notify {
    unsigned int port;          /* Локальний порт для генерації upcall */
};

#define IOCTL_EVTCHN_BIND_UNBOUND_PORT \
    _IOC(_IOC_NONE, 'E', 2, sizeof(struct ioctl_evtchn_bind_unbound_port))
#define IOCTL_EVTCHN_NOTIFY            \
    _IOC(_IOC_NONE, 'E', 4, sizeof(struct ioctl_evtchn_notify))
```
```cpp
// C++ підсистема обгортки Event Channel ioctl
struct EvtchnBindUnboundPort {
    std::uint32_t remote_domain; // ID віддаленого домену; порт повертає сам ioctl
};

struct EvtchnNotify {
    std::uint32_t port;          // Локальний порт для генерації upcall
};
```
:::
