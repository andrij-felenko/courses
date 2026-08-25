# Довідник API системних викликів та структур Landlock ABI v4/v5

Підсистема Landlock надає трійку системних викликів для створення, наповнення та застосування наборів правил безпеки (rulesets). Нижче наведено вичерпну специфікацію API, структур даних, констант, розмітки пам'яті та кодів помилок для версій ABI v4 (Linux 6.7) та ABI v5 (Linux 6.8).

## 1. Системні виклики та їхні сигнатури

Оскільки функціональні обгортки для системних викликів Landlock можуть бути відсутні у застарілих версіях C-бібліотек (glibc/musl), виклики виконуються безпосередньо через універсальний інтерфейс `syscall()` з оголошенням відповідних номерів викликів із `<sys/syscall.h>`.

:::tabs
@tab C
```c
#include <linux/landlock.h>
#include <sys/syscall.h>

int landlock_create_ruleset(
    const struct landlock_ruleset_attr *attr,
    size_t size,
    __u32 flags
);

int landlock_add_rule(
    int ruleset_fd,
    enum landlock_rule_type rule_type,
    const void *rule_attr,
    __u32 flags
);

int landlock_restrict_self(
    int ruleset_fd,
    __u32 flags
);
```
@tab C++
```cpp
#include <linux/landlock.h>
#include <sys/syscall.h>
#include <unistd.h>

extern "C" {
    int landlock_create_ruleset(
        const struct landlock_ruleset_attr *attr,
        std::size_t size,
        std::uint32_t flags
    );

    int landlock_add_rule(
        int ruleset_fd,
        enum landlock_rule_type rule_type,
        const void *rule_attr,
        std::uint32_t flags
    );

    int landlock_restrict_self(
        int ruleset_fd,
        std::uint32_t flags
    );
}
```
:::

### 1.1. `landlock_create_ruleset`
- **Опис**: Створює анонімний файловий дескриптор, що представляє новий набір правил Landlock у ядрі.
- **Аргументи**:
  - `attr`: Вказівник на структуру `landlock_ruleset_attr`, яка визначає домени доступу (VFS, Network).
  - `size`: Розмір структури `sizeof(struct landlock_ruleset_attr)`. Використовується ядром для забезпечення розширюваності та зворотної сумісності ABI через внутрішню функцію ядра `copy_struct_from_user()`.
  - `flags`: Прапорці створення. Головний прапорець: `LANDLOCK_CREATE_RULESET_VERSION` — запитує поточну версію ABI, підтримувану ядром (при цьому `attr` має бути `NULL`, а `size` — `0`).
- **Повертане значення**: При успіху повертає новий файловий дескриптор ruleset (`>= 0`) або цілочисельну версію ABI при виклику з `LANDLOCK_CREATE_RULESET_VERSION`. При помилці повертає `-1` і виставляє `errno`.

### 1.2. `landlock_add_rule`
- **Опис**: Додає конкретне правило дозволу до існуючого та ще не застосованого набору правил.
- **Аргументи**:
  - `ruleset_fd`: Файловий дескриптор, отриманий від `landlock_create_ruleset`.
  - `rule_type`: Енумерований тип правила:
    - `LANDLOCK_RULE_PATH_BENEATH` (1): Правило доступу до файлової ієрархії VFS.
    - `LANDLOCK_RULE_NET_PORT` (2): Правило доступу до мережевого порту (введено у v4).
  - `rule_attr`: Вказівник на відповідну структуру атрибутів правила (`landlock_path_beneath_attr` або `landlock_net_port_attr`).
  - `flags`: Зарезервовані прапорці (повинні дорівнювати `0`).
- **Повертане значення**: `0` при успішному додаванні правила або `-1` при помилці.

### 1.3. `landlock_restrict_self`
- **Опис**: Переводить набір правил у стан активного обмеження для поточного процесу та всіх його майбутніх нащадків.
- **Вимоги**: Процес повинен попередньо виставити прапорець `PR_SET_NO_NEW_PRIVS` через `prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)` або володіти можливості `CAP_SYS_ADMIN` у власному користувацькому просторі імен (user namespace).
- **Аргументи**: `ruleset_fd` (файловий дескриптор правил), `flags` (зарезервовано, `0`).
- **Повертане значення**: `0` при успіху або `-1` при помилці.

## 2. Структури даних та бітові маски

### 2.1. `struct landlock_ruleset_attr`

Основоположна структура ініціалізації domain-контексту пісочниці:

:::tabs
@tab C
```c
struct landlock_ruleset_attr {
    __u64 handled_access_fs;   /* Бітова маска VFS-операцій */
    __u64 handled_access_net;  /* Бітова маска мережевих операцій (ABI v4+) */
    __u64 scoped;              /* Маска міжпроцесних обмежень (ABI v6+) */
};
```
@tab C++
```cpp
struct landlock_ruleset_attr {
    std::uint64_t handled_access_fs;   // Бітова маска VFS-операцій
    std::uint64_t handled_access_net;  // Бітова маска мережевих операцій (ABI v4+)
    std::uint64_t scoped;              // Маска міжпроцесних обмежень (ABI v6+)
};
```
:::

#### Прапорці `handled_access_net` (ABI v4+)
- `LANDLOCK_ACCESS_NET_BIND_TCP` (1ULL << 0): Контролює прив'язку TCP-сокетів до порту через `bind()`.
- `LANDLOCK_ACCESS_NET_CONNECT_TCP` (1ULL << 1): Контролює ініціалізацію вихідних TCP-з'єднань через `connect()`.

#### Прапорці `handled_access_fs` (усі версії ABI, включаючи ABI v5)
- `LANDLOCK_ACCESS_FS_EXECUTE` (1ULL << 0): Виконання бінарних файлів.
- `LANDLOCK_ACCESS_FS_WRITE_FILE` (1ULL << 1): Запис у вміст файлів.
- `LANDLOCK_ACCESS_FS_READ_FILE` (1ULL << 2): Читання вмісту файлів.
- `LANDLOCK_ACCESS_FS_READ_DIR` (1ULL << 3): Читання списку елементів каталогу.
- `LANDLOCK_ACCESS_FS_REMOVE_DIR` (1ULL << 4): Видалення порожніх каталогів.
- `LANDLOCK_ACCESS_FS_REMOVE_FILE` (1ULL << 5): Видалення файлів та вузлів VFS.
- `LANDLOCK_ACCESS_FS_MAKE_CHAR` (1ULL << 6): Створення символьних пристроїв.
- `LANDLOCK_ACCESS_FS_MAKE_DIR` (1ULL << 7): Створення каталогів.
- `LANDLOCK_ACCESS_FS_MAKE_REG` (1ULL << 8): Створення звичайних файлів.
- `LANDLOCK_ACCESS_FS_MAKE_SOCK` (1ULL << 9): Створення UNIX-сокетів VFS.
- `LANDLOCK_ACCESS_FS_MAKE_FIFO` (1ULL << 10): Створення FIFO (named pipes).
- `LANDLOCK_ACCESS_FS_MAKE_BLOCK` (1ULL << 11): Створення блочних пристроїв.
- `LANDLOCK_ACCESS_FS_MAKE_SYM` (1ULL << 12): Створення символьних посилань.
- `LANDLOCK_ACCESS_FS_REFER` (1ULL << 13): **ABI v3+**. Перейменування та лінкування файлів між каталогами.
- `LANDLOCK_ACCESS_FS_TRUNCATE` (1ULL << 14): **ABI v2+**. Зміна розміру файлів через `truncate` / `ftruncate`.
- `LANDLOCK_ACCESS_FS_IOCTL_DEV` (1ULL << 15): **ABI v5+**. Виконання `ioctl()` на символьних та блочних пристроях.

### 2.2. `struct landlock_net_port_attr` (ABI v4+)

Структура опису мережевого правила для TCP-порту:

:::tabs
@tab C
```c
struct landlock_net_port_attr {
    __u64 allowed_access; /* Бітова маска дозволених мережевих дій */
    __u64 port;           /* Номер TCP-порту в звичайному порядку байтів (host byte order) */
};
```
@tab C++
```cpp
struct landlock_net_port_attr {
    std::uint64_t allowed_access; // Бітова маска дозволених мережевих дій
    std::uint64_t port;           // Номер TCP-порту в звичайному порядку байтів (host byte order)
};
```
:::

### 2.3. `struct landlock_path_beneath_attr`

Структура опису VFS-правила для файлової ієрархії:

:::tabs
@tab C
```c
struct landlock_path_beneath_attr {
    __u64 allowed_access; /* Бітова маска дозволених VFS-дій */
    __s32 parent_fd;      /* Файловий дескриптор батьківського каталогу або файла (O_PATH) */
};
```
@tab C++
```cpp
struct landlock_path_beneath_attr {
    std::uint64_t allowed_access; // Бітова маска дозволених VFS-дій
    std::int32_t parent_fd;       // Файловий дескриптор батьківського каталогу або файла (O_PATH)
};
```
:::

## 3. Сумісність ABI та вирівнювання у пам'яті

Для гарантування зворотної та прямої сумісності між різними випусками ядра Linux системні виклики Landlock застосовують паттерн вирівнювання розширюваних структур даних.

Усі поля структур (`landlock_ruleset_attr`, `landlock_net_port_attr`, `landlock_path_beneath_attr`) є явними 64-бітними цілими числами (`__u64`, `__s64`) або мають чітке вирівнювання за межею 8 байтів. Це усуває проблеми розбіжностей ABI між 32-бітними та 64-бітними архітектурами (наприклад, виконання 32-бітного бінарника у 64-бітному середовищі `x86_64` / `arm64`).

Під час виконання `landlock_create_ruleset()` ядро перевіряє передане значення `size`:
- Якщо програма передає структуру меншого розміру, ніж знає ядро, ядро заповнює відсутні нові поля нулями (fallback до старішої поведінки).
- Якщо програма передає новішу структуру більшого розміру, ніж знає старе ядро, ядро перевіряє, чи всі невідомі йому нові поля заповнені нулями. Якщо в нових полях є біти, ядро повертає помилку `-E2BIG`.

## 4. Деталізація кодів помилок `errno`

Під час виконання системних викликів Landlock ядро може повертати наступні коди помилок у змінній `errno`:

| Код помилки | Системний виклик | Визначення та причина виникнення |
| :--- | :--- | :--- |
| `EACCES` | `bind`, `connect`, `ioctl`, `openat` | Спроба виконання операції, заблокованої активним набором правил Landlock. |
| `EINVAL` | `landlock_create_ruleset`, `landlock_add_rule` | Передано невідомий прапорець, невідомий `rule_type`, або номер порту перевищує значення `65535`. |
| `EOPNOTSUPP` | `landlock_create_ruleset` | Передано атрибут доступу (наприклад, мережевий прапорець у `handled_access_net`), який не підтримується поточним ABI ядра. |
| `E2BIG` | `landlock_create_ruleset` | Параметр `size` перевищує розмір структури, відомий поточній версії ядра. |
| `EPERM` | `landlock_restrict_self` | Спроба застосувати пісочницю без попереднього встановлення прапорця `PR_SET_NO_NEW_PRIVS`. |
| `EBADF` | `landlock_add_rule`, `landlock_restrict_self` | Передано некоректний або закритий файловий дескриптор `ruleset_fd` або `parent_fd`. |
| `EFAULT` | Усі виклики | Передано недійсний вказівник у пам'яті користувацького простору. |
| `ENOMSG` | `landlock_add_rule` | Передана маска `allowed_access` порожня або містить біти, які не були задекларовані під час створення ruleset. |
