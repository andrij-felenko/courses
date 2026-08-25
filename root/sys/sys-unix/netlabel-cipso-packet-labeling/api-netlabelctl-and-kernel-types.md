# 📋 Довідник інтерфейсу: утиліта netlabelctl, Generic Netlink та структури ядра

<preknowlist>
- [Фреймворк модулів безпеки ядра Linux (LSM)](topic:sys-unix/lsm-framework) — структури ядра для збереження контекстів безпеки.
- [SELinux: Type Enforcement та контексти безпеки](topic:sys-unix/selinux-type-enforcement) — представлення числових рівнів і категорій MLS.
</preknowlist>

Підсистема NetLabel надає два взаємопов'язані рівні інтерфейсу:
1. **Інтерфейс простору користувача (Userspace API):** реалізований на базі сімейства сокетів Generic Netlink (`NETLINK_GENERIC`), з яким взаємодіє командна утиліта `netlabelctl` та MLS-демони.
2. **Внутрішній інтерфейс ядра (Kernel Internal API):** набір експортованих структур даних C та функцій зв'язку (`netlbl_*`), які інтегруються з модулями безпеки LSM (SELinux, Smack) та мережевим стеком ядра Linux.

---

## 1. Командний інтерфейс утиліти `netlabelctl`

Утиліта `netlabelctl` є офіційним інструментом адміністрування підсистеми NetLabel. Вона формує Netlink-повідомлення, передає їх ядру для оновлення таблиць доменів інтерпретації (DOI), налаштовує статичні правила для немаркованих вузлів та скидає внутрішні кеші.

### Загальний синтаксис виклику

```
netlabelctl [-p] [-t <секунди>] [-v] <підсистема> <дія> [параметри...]
```

Прапорці глобального виклику:
- `-p` (parsable): виводить результат у структурованому машинному форматі, придатному для автоматизованого розбору скриптами;
- `-t <секунди>` (timeout): встановлює максимальний час очікування відповіді від ядра на Netlink-запит (за замовчуванням 3 секунди);
- `-v` (verbose): вмикає детальний діагностичний вивід параметрів запитів та заголовків відповідей.

---

### 1.1. Підсистема `mgmt` (Загальне адміністрування та керування кешем)

Підсистема `mgmt` відповідає за діагностику стану підсистеми NetLabel у ядрі, отримання підтримуваних версій протоколів та інвалідацію швидкого кешу записів.

| Команда | Призначення | Очікувані параметри | Коди помилок ядра |
| :--- | :--- | :--- | :--- |
| `mgmt show` | Показати поточний стан підсистеми | Немає | `0` (успіх), `ENOMEM` |
| `mgmt version` | Вивести версію протоколу NetLabel | Немає | `0` |
| `mgmt protver` | Вивести підтримувані версії розширень | Немає | `0` |
| `mgmt chear` | Повністю очистити внутрішній кеш міток | Немає | `0`, `EPERM` |

Приклад скидання швидкого кешу міток NetLabel у ядрі:
```bash
netlabelctl mgmt chear
```

---

### 1.2. Підсистема `cipsov4` (Налаштування протоколу CIPSO для IPv4)

Підсистема `cipsov4` конфігурує домени інтерпретації (Domain of Interpretation, DOI) відповідно до стандарту FIPS PUB 188. Кожен домен визначає, як локальні числові рівні та категорії транслюються в опцію IP 134 (`0x86`).

| Команда | Опис | Параметри | Коди помилок ядра |
| :--- | :--- | :--- | :--- |
| `cipsov4 add pass` | Додати домен pass-through (пряме прозоре відображення) | `doi:<DOI> tags:<список_тегів>` | `EEXIST`, `EINVAL`, `ENOMEM` |
| `cipsov4 add std` | Додати домен зі стандартним зіставленням рівнів і категорій | `doi:<DOI> tags:<теги> levels:<рівні> cats:<категорії>` | `EEXIST`, `EINVAL`, `ENOMEM` |
| `cipsov4 add local` | Додати локальний DOI (без виходу в зовнішню мережу) | `doi:<DOI>` | `EEXIST`, `EINVAL` |
| `cipsov4 del` | Видалити сконфігурований домен інтерпретації | `doi:<DOI>` | `ENOENT`, `EBUSY` |
| `cipsov4 list` | Вивести конфігурацію конкретного або всіх доменів DOI | `[doi:<DOI>]` | `ENOENT` (якщо DOI не знайдено) |

Параметри команд `cipsov4`:
- `doi:<DOI>`: ціле 32-бітне беззнакове число (`1`..`4294967295`), що ідентифікує спільний простір інтерпретації міток;
- `tags:<список_тегів>`: перелік допустимих типів тегів FIPS 188 через кому (`1` — бітова маска, `2` — перелік, `5` — діапазони);
- `levels:<локальний>=<віддалений>,...`: правила зіставлення рівнів чутливості;
- `cats:<локальна>=<віддалена>,...`: правила зіставлення окремих категорій або діапазонів.

Приклад конфігурації прозорого домену pass-through DOI 1 з тегом 1:
```bash
netlabelctl cipsov4 add pass doi:1 tags:1
```

Приклад конфігурації зіставлення рівнів для взаємодії з віддаленим вузлом:
```bash
netlabelctl cipsov4 add std doi:2 tags:1,2 levels:0=0,1=10,2=20 cats:0=100,1=101,2=102
```

---

### 1.3. Підсистема `calipso` (Налаштування протоколу CALIPSO для IPv6)

Підсистема `calipso` керує доменами інтерпретації для протоколу IPv6 відповідно до специфікації RFC 5570 (опція `0x07` у заголовках `Hop-by-Hop` або `Destination Options`).

| Команда | Опис | Параметри | Коди помилок ядра |
| :--- | :--- | :--- | :--- |
| `calipso add pass` | Додати pass-through домен CALIPSO для IPv6 | `doi:<DOI>` | `EEXIST`, `EINVAL`, `ENOMEM` |
| `calipso del` | Видалити сконфігурований домен CALIPSO | `doi:<DOI>` | `ENOENT`, `EBUSY` |
| `calipso list` | Переглянути всі активні домени CALIPSO | `[doi:<DOI>]` | `0`, `ENOENT` |

Приклад додавання домену CALIPSO DOI 100 для IPv6-мережі:
```bash
netlabelctl calipso add pass doi:100
```

---

### 1.4. Підсистема `unlbl` (Немаркований трафік / Fallback)

Підсистема `unlbl` призначена для взаємодії зі звичайними мережевими вузлами, операційні системи яких не підтримують CIPSO або CALIPSO. Вона дозволяє призначити фіксований статичний контекст безпеки SELinux/Smack трафіку від конкретних IP-адрес чи цілих підмереж.

| Команда | Опис | Параметри | Коди помилок ядра |
| :--- | :--- | :--- | :--- |
| `unlbl accept on/off` | Дозволити або заборонити прийом немаркованих пакетів | `on` або `off` | `0`, `EINVAL` |
| `unlbl add default` | Призначити статичний контекст безпеки за замовчуванням | `secattr:<контекст>` | `EINVAL`, `ENOMEM` |
| `unlbl add address` | Призначити статичний контекст безпеки конкретній IP-адресі чи підмережі | `address:<IP/маска> secattr:<контекст>` | `EINVAL`, `EEXIST` |
| `unlbl del address` | Видалити статичне правило для підмережі | `address:<IP/маска>` | `ENOENT` |
| `unlbl list` | Вивести перелік усіх правил немаркованого зіставлення | Немає | `0` |

Приклад конфігурації статичного контексту для внутрішньої адміністративної підмережі:
```bash
netlabelctl unlbl accept on
netlabelctl unlbl add address:192.168.50.0/24 secattr:system_u:object_r:unlabeled_t:s0
```

---

### 1.5. Підсистема `map` (Зіставлення LSM-доменів із мережевими протоколами)

Підсистема `map` зв'язує локальні домени модулів безпеки (назви типів SELinux або міток Smack) з конкретними DOI або механізмами маркування.

| Команда | Опис | Параметри | Коди помилок ядра |
| :--- | :--- | :--- | :--- |
| `map add default` | Зіставити домен за замовчуванням із протоколом маркування | `protocol:cipsov4,<DOI>` або `protocol:unlbl` | `EINVAL`, `ENOMEM` |
| `map add domain` | Прив'язати конкретний домен до протоколу та селектора адрес | `domain:<назва> protocol:<тип,DOI> [address:<IP/маска>]` | `EINVAL`, `EEXIST` |
| `map del domain` | Видалити прив'язку для домену | `domain:<назва>` | `ENOENT` |
| `map list` | Вивести повну таблицю зіставлення доменів | Немає | `0` |

Приклад призначення домену `mls_trusted_t` протоколу CIPSO v4 DOI 1 для підмережі `10.20.0.0/16`:
```bash
netlabelctl map add domain:mls_trusted_t protocol:cipsov4,1 address:10.20.0.0/16
```

---

## 2. Протокол Generic Netlink та константи повідомлень

Усі операції `netlabelctl` виконуються через інтерфейс Generic Netlink. NetLabel реєструє в ядрі чотири окремі сім'ї (Generic Netlink Families):
1. `NETLBL_NLTYPE_MGMT` (`"NETLBL_MGMT"`): команди загального управління;
2. `NETLBL_NLTYPE_CIPSOV4` (`"NETLBL_CIPSOv4"`): конфігурація IPv4 CIPSO;
3. `NETLBL_NLTYPE_CALIPSO` (`"NETLBL_CALIPSO"`): конфігурація IPv6 CALIPSO;
4. `NETLBL_NLTYPE_UNLABELED` (`"NETLBL_UNLBL"`): правила немаркованого трафіку.

### Основні атрибути Generic Netlink (NLA) для CIPSO:
- `NLBL_CIPSOV4_A_DOI` (тип `NLA_U32`): 32-бітне число DOI;
- `NLBL_CIPSOV4_A_MTYPE` (тип `NLA_U32`): тип відображення (`CIPSO_V4_MAP_PASS`, `CIPSO_V4_MAP_TRANS`, `CIPSO_V4_MAP_LOCAL`);
- `NLBL_CIPSOV4_A_TAG` (тип `NLA_U8`): окремий числовий тег;
- `NLBL_CIPSOV4_A_TAGLST` (тип `NLA_NESTED`): вкладений список підтримуваних тегів;
- `NLBL_CIPSOV4_A_MLSLVLLOC` (тип `NLA_U32`): локальний рівень MLS;
- `NLBL_CIPSOV4_A_MLSLVLREM` (тип `NLA_U32`): віддалений рівень CIPSO;
- `NLBL_CIPSOV4_A_MLSCATLOC` (тип `NLA_U32`): локальний номер категорії;
- `NLBL_CIPSOV4_A_MLSCATREM` (тип `NLA_U32`): віддалений номер категорії.

---

## 3. Структури даних ядра Linux (`include/net/netlabel.h`)

Внутрішній інтерфейс NetLabel побудований на оптимізованих C-структурах, що взаємодіють з LSM без блокування за допомогою механізму Read-Copy-Update (RCU).

### 3.1. Універсальна структура атрибутів безпеки: `struct netlbl_lsm_secattr`

Структура `struct netlbl_lsm_secattr` виступає уніфікованим проміжним представленням мітки безпеки між драйверами пакетів, підсистемою NetLabel та модулями безпеки ядра:

```c
struct netlbl_lsm_secattr_mls {
    u32 lvl;                       /* числовий рівень чутливості (sensitivity) */
    struct netlbl_lsm_catmap *cat; /* динамічний бітмап категорій (categories) */
};

struct netlbl_lsm_secattr {
    u32 flags;                     /* бітова маска валідності полів */
    u32 type;                      /* джерело мітки: CIPSO, CALIPSO, UNLBL */
    char *domain;                  /* назва LSM-домену (якщо задана) */
    u32 secid;                     /* числовий Security ID ядра */
    struct netlbl_lsm_secattr_mls mls; /* параметри MLS */
    struct netlbl_lsm_cache *cache;    /* вказівник на кеш швидкого шляху */
};
```

Прапорці бітової маски `flags`:
- `NETLBL_SECATTR_NONE` (`0x00000000`): структура не містить ініціалізованих даних;
- `NETLBL_SECATTR_DOMAIN` (`0x00000001`): поле `domain` містить валідний статичний рядок;
- `NETLBL_SECATTR_DOMAIN_CPY` (`0x00000002`): пам'ять рядка `domain` виділена динамічно через `kstrdup()` і вимагає звільнення через `kfree()`;
- `NETLBL_SECATTR_MLS_LVL` (`0x00000004`): поле `mls.lvl` містить валідний числовий рівень;
- `NETLBL_SECATTR_MLS_CAT` (`0x00000008`): поле `mls.cat` містить валідний бітмап категорій;
- `NETLBL_SECATTR_SECID` (`0x00000010`): поле `secid` містить готовий ідентифікатор безпеки LSM;
- `NETLBL_SECATTR_CACHE` (`0x00000020`): присутній дійсний кешований запис швидкого шляху.

---

### 3.2. Динамічний бітмап категорій: `struct netlbl_lsm_catmap`

Оскільки кількість категорій у SELinux та інших MLS-системах може досягати кількох тисяч, ядро не використовує статичні фіксовані масиви великого розміру. Категорії зберігаються у вигляді однозв'язного списку 256-бітних вузлів:

```c
#define NETLBL_CATMAP_MAPTYPE      unsigned long
#define NETLBL_CATMAP_MAPBITS      (sizeof(NETLBL_CATMAP_MAPTYPE) * 8)
#define NETLBL_CATMAP_MAPCNT       4
#define NETLBL_CATMAP_SIZE         (NETLBL_CATMAP_MAPBITS * NETLBL_CATMAP_MAPCNT)

struct netlbl_lsm_catmap {
    u32 startbit;                  /* початковий бітовий індекс вузла (кратний 256) */
    NETLBL_CATMAP_MAPTYPE bitmap[NETLBL_CATMAP_MAPCNT]; /* бітова маска 256 бітів */
    struct netlbl_lsm_catmap *next;/* вказівник на наступний вузол категорій */
};
```

---

### 3.3. Швидкий кеш міток: `struct netlbl_lsm_cache`

Для зменшення затримок на гігабітних мережевих інтерфейсах NetLabel кешує результат трансляції сирих байтів опції IP безпосередньо у відповідний SECID:

```c
struct netlbl_lsm_cache {
    refcount_t refcount;           /* атомарний лічильник посилань */
    u32 type;                      /* тип протоколу маркування */
    u8 *opt;                       /* копія сирого байтового буфера опції IP */
    u32 opt_len;                   /* довжина буфера опції */
    u32 secid;                     /* кешований Security ID модуля безпеки */
    struct list_head list;         /* вузол геш-таблиці кешу ядра */
    struct rcu_head rcu;           /* структура для асинхронного RCU-звільнення */
};
```

---

## 4. Основні функції API ядра (`include/net/netlabel.h`)

| Функція ядра | Сигнатура та опис |
| :--- | :--- |
| `netlbl_sock_setattr` | `int netlbl_sock_setattr(struct sock *sk, u16 family, const struct netlbl_lsm_secattr *secattr);`<br>Генерує та прикріплює опції CIPSO/CALIPSO до сокета ядра. |
| `netlbl_sock_getattr` | `int netlbl_sock_getattr(struct sock *sk, struct netlbl_lsm_secattr *secattr);`<br>Видобуває атрибути безпеки зі збережених опцій сокета. |
| `netlbl_skbuff_getattr` | `int netlbl_skbuff_getattr(const struct sk_buff *skb, u16 family, struct netlbl_lsm_secattr *secattr);`<br>Розбирає заголовки пакета `sk_buff` і видобуває мітку безпеки. |
| `netlbl_skbuff_err` | `int netlbl_skbuff_err(struct sk_buff *skb, u16 family, int error, int gateway);`<br>Генерує ICMP-відповідь про помилку розбору або заборону доступу за міткою. |
| `netlbl_secattr_init` | `void netlbl_secattr_init(struct netlbl_lsm_secattr *secattr);`<br>Ініціалізує поля структури нульовими значеннями. |
| `netlbl_secattr_destroy` | `void netlbl_secattr_destroy(struct netlbl_lsm_secattr *secattr);`<br>Звільняє динамічно виділену пам'ять (рядок домену та бітмапи категорій). |

---

## 5. Аудит та події підсистеми NetLabel у журналі аудиту ядра

Будь-які зміни конфігурації доменів інтерпретації, прив'язок та немаркованих правил генерують спеціалізовані повідомлення аудиту в підсистемі `auditd`. Це забезпечує відповідність вимогам стандартів оцінки захищеності інформаційних технологій (Common Criteria / EAL4+):

- `AUDIT_MAC_CIPSOV4_ADD` (код `1401`): успішне або неуспішне додавання нового домену інтерпретації CIPSO для IPv4;
- `AUDIT_MAC_CIPSOV4_DEL` (код `1402`): видалення існуючого домену CIPSO;
- `AUDIT_MAC_CALIPSO_ADD` (код `1416`): реєстрація домену CALIPSO для IPv6;
- `AUDIT_MAC_CALIPSO_DEL` (код `1417`): видалення домену CALIPSO;
- `AUDIT_MAC_UNLBL_STCADD` (код `1405`): додавання статичного правила прив'язки для немаркованого хоста чи підмережі;
- `AUDIT_MAC_UNLBL_STCDEL` (код `1406`): видалення статичного правила немаркованого трафіку;
- `AUDIT_MAC_MAP_ADD` (код `1403`): створення запису в таблиці зіставлення доменів безпеки;
- `AUDIT_MAC_MAP_DEL` (код `1404`): видалення запису з таблиці зіставлення доменів.

Кожен запис аудиту фіксує ідентифікатор сесії (`auid`), UID користувача, що ініціював зміну, передане значення DOI та результуючий статус операції (`res=1` або `res=0`).
