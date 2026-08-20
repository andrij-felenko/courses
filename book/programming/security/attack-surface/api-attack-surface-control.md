# 📋 Довідник системних інтерфейсів звуження поверхні атаки в Linux

Мінімізація поверхні атаки програмного комплексу на рівні операційної системи вимагає використання низькорівневих інтерфейсів обмеження привілеїв, фільтрації системних викликів та ізоляції просторів імен. Звуження системних інтерфейсів перетворює процес на ізольовану пісочницю, яка навіть у разі повної компрометації пам'яті не здатна завдати шкоди операційній системі або сусіднім службам.

Коли процес звертається до ядра через програмне переривання або спеціальну процесорну інструкцію (`syscall` на x86_64 або `svc` на ARM64), процесор перемикається у привілейований режим Ring 0. Ядро Linux надає користувацькому простору кілька взаємодоповнюючих підсистем для затискання цієї межі: фільтрацію системних викликів Seccomp-BPF, обмеження файлових операцій Landlock LSM, поділ просторів імен та керування бітовими масками можливостей POSIX capabilities.

Нижче наведено структуровану довідку системних викликів, структур даних, констант та псевдофайлових інтерфейсів ядра Linux (з порівнянням із BSD), призначених для затискання процесу у мінімальний безпечний контекст.

## 1. Системний виклик `seccomp(2)` та керування фільтрами

Системний виклик `seccomp` (англ. *Secure Computing Mode*) дозволяє процесу встановити односторонній бар'єр, що обмежує доступ до системних викликів ядра. Фільтр перевіряє кожен виклик до того, як ядро виділить для нього ресурси або виконає перевірку прав доступу.

:::tabs
```c
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <sys/syscall.h>
#include <unistd.h>

int syscall(SYS_seccomp, unsigned int operation, unsigned int flags, void *args);
```
```cpp
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <system_error>
#include <expected>
#include <span>

namespace seccomp_api {

enum class Operation : unsigned int {
    SetModeStrict = SECCOMP_SET_MODE_STRICT,
    SetModeFilter = SECCOMP_SET_MODE_FILTER,
    GetActionAvail = SECCOMP_GET_ACTION_AVAIL,
    GetNotifSizes = SECCOMP_GET_NOTIF_SIZES
};

[[nodiscard]] inline std::expected<int, std::error_code> invoke_seccomp(
    Operation op, unsigned int flags, void* args) noexcept {
    int res = ::syscall(SYS_seccomp, static_cast<unsigned int>(op), flags, args);
    if (res < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return res;
}

} // namespace seccomp_api
```
:::

### 1.1. Операції (`operation`)

| Операція | Опис та семантика |
| :--- | :--- |
| `SECCOMP_SET_MODE_STRICT` | Суворий режим за замовчуванням. Дозволяє виключно `read(2)`, `write(2)`, `_exit(2)` та `sigreturn(2)`. Будь-який інший виклик миттєво вбиває процес сигналом `SIGKILL`. Аргумент `args` має бути `NULL`. |
| `SECCOMP_SET_MODE_FILTER` | Режим програмованого BPF-фільтра. Завантажує класичну програму BPF (`struct sock_fprog`), яка перевіряє номер виклику, архітектуру та аргументи. |
| `SECCOMP_GET_ACTION_AVAIL` | Перевірка підтримки ядром конкретної дії повернення фільтра (`SECCOMP_RET_*`). Дозволяє переконатися у наявності підтримки `SECCOMP_RET_USER_NOTIF` або `SECCOMP_RET_KILL_PROCESS` перед накладанням фільтра. |
| `SECCOMP_GET_NOTIF_SIZES` | Отримання розмірів структур для механізму сповіщень у простір користувача (User Notification). |

### 1.2. Прапорці операції (`flags`)

| Прапорець | Призначення |
| :--- | :--- |
| `SECCOMP_FILTER_FLAG_TSYNC` | Синхронізувати встановлений фільтр для **всіх потоків** поточного процесу. Якщо хоча б один потік не може застосувати фільтр — виклик завершується з помилкою. Запобігає обходу фільтра через фонові нитки. |
| `SECCOMP_FILTER_FLAG_LOG` | Примусово протоколювати всі дії фільтра, крім `SECCOMP_RET_ALLOW`, у системний журнал аудиту `auditd`. |
| `SECCOMP_FILTER_FLAG_SPEC_ALLOW` | Вимкнути захист від спекулятивних атак (Speculative Store Bypass) для оптимізації продуктивності. Заборонено використовувати у захищених середовищах. |

### 1.3. Значення повернення фільтра (`SECCOMP_RET_*`)

Фільтр BPF повертає 32-бітне число, де старші 16 біт визначають дію ядра, а молодші 16 біт — користувацькі дані (наприклад, код помилки `errno`):

| Дія | Пріоритет | Поведінка ядра |
| :--- | :--- | :--- |
| `SECCOMP_RET_KILL_PROCESS` | Найвищий | Негайне аварійне знищення всього процесу разом з усіма нитками (`SIGSYS`). Запобігає подальшому виконанню коду експлойту. |
| `SECCOMP_RET_KILL_THREAD` | Високий | Знищення лише поточної нитки, що виконала заборонений виклик. |
| `SECCOMP_RET_TRAP` | Середній | Відправка сигналу `SIGSYS` процесу з заповненням структури `siginfo_t` для програмної обробки. |
| `SECCOMP_RET_ERRNO` | Середній | Системний виклик не виконується; потік отримує значення `-1`, а `errno` встановлюється у молодші 16 біт значення повернення фільтра. |
| `SECCOMP_RET_USER_NOTIF` | Середній | Передача перехопленого виклику процесу-наглядачу (Supervisor) через спеціальний дескриптор для емуляції або перевірки. |
| `SECCOMP_RET_TRACE` | Нижчий | Сповіщення налагоджувача `ptrace` (якщо приєднаний); якщо налагоджувача немає — повертає помилку `ENOSYS`. |
| `SECCOMP_RET_LOG` | Низький | Виклик дозволяється до виконання, але запис про нього обов'язково потрапляє в системний журнал аудиту. |
| `SECCOMP_RET_ALLOW` | Найнижчий | Системний виклик виконується без жодних перешкод. |

## 2. Структури BPF-фільтрації

Фільтрація виконується за допомогою псевдокоду класичного Berkeley Packet Filter (cBPF). Інструкції BPF представляють послідовність операцій завантаження, порівняння та умовних переходів над структурою `seccomp_data`.

:::tabs
```c
#include <linux/filter.h>
#include <linux/seccomp.h>

struct sock_filter {
    __u16 code;   /* Код операції BPF (інструкція завантаження, переходу або повернення) */
    __u8  jt;     /* Зсув переходу при True (кількість інструкцій для пропуску) */
    __u8  jf;     /* Зсув переходу при False */
    __u32 k;      /* Багатоцільове поле (константа, номер виклику, зміщення в пам'яті) */
};

struct sock_fprog {
    unsigned short      len;     /* Кількість інструкцій у масиві filter */
    struct sock_filter *filter;  /* Вказівник на масив інструкцій */
};

struct seccomp_data {
    int   nr;                    /* Номер системного виклику (__NR_*) */
    __u32 arch;                  /* Ідентифікатор архітектури (AUDIT_ARCH_X86_64 тощо) */
    __u64 instruction_pointer;   /* Адреса інструкції CPU, що ініціювала виклик */
    __u64 args[6];               /* 6 аргументів системного виклику */
};
```
```cpp
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <cstdint>
#include <span>

namespace seccomp_api {

struct SockFilter {
    uint16_t code{0};
    uint8_t  jt{0};
    uint8_t  jf{0};
    uint32_t k{0};
};

struct SockFilterProgram {
    uint16_t len{0};
    const SockFilter* filter{nullptr};

    explicit SockFilterProgram(std::span<const SockFilter> instructions) noexcept
        : len{static_cast<uint16_t>(instructions.size())},
          filter{instructions.data()} {}
};

struct SeccompData {
    int32_t  nr{0};
    uint32_t arch{0};
    uint64_t instruction_pointer{0};
    uint64_t args[6]{0, 0, 0, 0, 0, 0};
};

} // namespace seccomp_api
```
:::

Кожна інструкція `sock_filter` виконує елементарну дію віртуальної машини BPF. Регістр акумулятора завантажує номер виклику (`BPF_LD | BPF_W | BPF_ABS`), після чого інструкції порівняння (`BPF_JMP | BPF_JEQ | BPF_K`) зіставляють значення з дозволеними константами. У разі збігу лічильник команд переходить на фінальну інструкцію дозволу `SECCOMP_RET_ALLOW`.

## 3. Запобігання ескалації привілеїв: `prctl(PR_SET_NO_NEW_PRIVS)`

Перед завантаженням Seccomp-фільтра непривілейованим процесом ядро Linux вимагає обов'язкової активації прапорця `no_new_privs`. Це запобігає атаці, коли процес накладає фільтр на виклики автентифікації і запускає бінарний файл із бітом SUID (наприклад, `/bin/su` або `/usr/bin/sudo`), сподіваючись змусити його пропустити перевірку пароля через повернення штучної помилки.

:::tabs
```c
#include <sys/prctl.h>

int prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);
```
```cpp
#include <sys/prctl.h>
#include <system_error>
#include <expected>

namespace seccomp_api {

[[nodiscard]] inline std::expected<void, std::error_code> set_no_new_privs() noexcept {
    if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

} // namespace seccomp_api
```
:::

**Семантика:** Після встановлення значення `1` процес та всі його дочірні процеси ніколи не зможуть отримати додаткові привілеї через біти `setuid`/`setgid` на виконуваних файлах або файлові можливості (file capabilities). Ця дія є строго односторонньою та незворотною: жоден наступний системний виклик не може повернути значення `0`.

## 4. Ізоляція просторів імен (`unshare(2)`)

Системний виклик `unshare` дозволяє процесу відокремити свій контекст виконання від решти системи, створюючи приватні копії системних ресурсів.

:::tabs
```c
#include <sched.h>

int unshare(int flags);
```
```cpp
#include <sched.h>
#include <system_error>
#include <expected>

namespace seccomp_api {

[[nodiscard]] inline std::expected<void, std::error_code> unshare_namespaces(int flags) noexcept {
    if (::unshare(flags) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

} // namespace seccomp_api
```
:::

### Деталізація прапорців просторів імен

| Прапорець | Звуження поверхні атаки та наслідки |
| :--- | :--- |
| `CLONE_NEWNS` | Створює приватний простір монтування. Дозволяє демонтувати чутливі каталоги (`/home`, `/root`, `/sys`) або перевести кореневий каталог у режим `MS_RDONLY`. |
| `CLONE_NEWNET` | Створює ізольований мережевий стек. Процес бачить лише власний інтерфейс `lo`, повністю втрачаючи доступ до зовнішніх мережевих адаптерів та локальної мережі. |
| `CLONE_NEWPID` | Ізолює дерево процесів. Дочірній процес стає `PID 1` у власному просторі й не може бачити, трасувати чи відправляти сигнали іншим процесам ОС. |
| `CLONE_NEWUSER` | Дозволяє процесу отримати віртуальний `UID 0` всередині пісочника без надання жодних прав у батьківській системі. |
| `CLONE_NEWIPC` | Ізолює черги повідомлень System V / POSIX, семафори та сегменти спільної пам'яті. |
| `CLONE_NEWUTS` | Ізолює ім'я хоста та доменне ім'я від глобальної системи. |

## 5. Обмеження файлової системи через Landlock LSM

Починаючи з версії ядра Linux 5.13, з'явився модуль безпеки Landlock (LSM). Він дозволяє непривілейованому процесу створювати набори правил обмеження доступу до ієрархії файлової системи без необхідності прав адміністратора `root`.

:::tabs
```c
#include <linux/landlock.h>
#include <sys/syscall.h>
#include <unistd.h>

/* Створення набору правил Landlock */
int landlock_create_ruleset(const struct landlock_ruleset_attr *attr, size_t size, __u32 flags);

/* Додавання правила для конкретного файлового дескриптора */
int landlock_add_rule(int ruleset_fd, enum landlock_rule_type rule_type, const void *rule_attr, __u32 flags);

/* Застосування обмежень до поточного процесу */
int landlock_restrict_self(int ruleset_fd, __u32 flags);
```
```cpp
#include <linux/landlock.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <system_error>
#include <expected>

namespace landlock_api {

[[nodiscard]] inline std::expected<int, std::error_code> create_ruleset(
    const landlock_ruleset_attr* attr, size_t size, uint32_t flags) noexcept {
    int fd = ::syscall(SYS_landlock_create_ruleset, attr, size, flags);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return fd;
}

[[nodiscard]] inline std::expected<void, std::error_code> restrict_self(
    int ruleset_fd, uint32_t flags) noexcept {
    if (::syscall(SYS_landlock_restrict_self, ruleset_fd, flags) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

} // namespace landlock_api
```
:::

Landlock дозволяє процесу дозволити читання або запис виключно для вказаних каталогів (наприклад, конфігураційного каталогу `/etc/app` або тимчасового буфера `/tmp/sandbox`), повністю забороняючи звернення до решти файлової системи навіть при наявності системних викликів `openat` та `read`. На відміну від `chroot`, Landlock не вимагає прав `root` і захищає від атак виходу з ізоляції через відносні шляхи `..` та відкриті файлові дескриптори.

## 6. Порівняння: механізми обмеження в OpenBSD та FreeBSD

В інших Unix-подібних операційних системах звуження інтерфейсів ядра реалізовано за допомогою альтернативних архітектурних концепцій.

### 6.1. OpenBSD Pledge та Unveil
В операційній системі OpenBSD звуження інтерфейсів ядра реалізовано через два високорівневі декларативні виклики `pledge` та `unveil`. На відміну від Seccomp у Linux, розробнику не потрібно вручну писати асемблерний код BPF: процес просто декларує категорії операцій.

:::tabs
```c
#include <unistd.h>

/* Обмеження доступних підсистем ядра через список обіцянок */
int pledge(const char *promises, const char *execpromises);

/* Обмеження доступу до файлової системи за конкретними шляхами */
int unveil(const char *path, const char *permissions);
```
```cpp
#include <unistd.h>
#include <string_view>
#include <system_error>
#include <expected>

namespace openbsd_api {

[[nodiscard]] inline std::expected<void, std::error_code> apply_pledge(
    std::string_view promises, const char* execpromises = nullptr) noexcept {
    if (::pledge(promises.data(), execpromises) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

[[nodiscard]] inline std::expected<void, std::error_code> apply_unveil(
    std::string_view path, std::string_view permissions) noexcept {
    if (::unveil(path.data(), permissions.data()) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

} // namespace openbsd_api
```
:::

### Таблиця еквівалентів категорій OpenBSD `pledge` та Linux Seccomp

| Категорія OpenBSD | Дозволені операції | Еквівалентний набір системних викликів у Linux Seccomp |
| :--- | :--- | :--- |
| `"stdio"` | Базове введення/виведення, робота з виділенням пам'яті | `read`, `write`, `close`, `mmap`, `brk`, `futex`, `exit_group` |
| `"rpath"` | Читання існуючих файлів | `openat(O_RDONLY)`, `read`, `stat`, `getdents64`, `lseek` |
| `"wpath"` | Запис у файли та зміна атрибутів | `openat(O_WRONLY)`, `write`, `truncate`, `fchmod` |
| `"cpath"` | Створення або видалення файлів і каталогів | `creat`, `mkdir`, `unlink`, `rename`, `rmdir` |
| `"inet"` | Мережева взаємодія протоколами IPv4/IPv6 | `socket(AF_INET)`, `connect`, `bind`, `sendto`, `recvfrom` |
| `"unix"` | Локальні сокети IPC домену Unix | `socket(AF_UNIX)`, `connect`, `bind`, `listen` |
| `NULL` | Повне блокування подальших змін | Незворотне накладання BPF-фільтра |

### 6.2. FreeBSD Capsicum
В операційній системі FreeBSD реалізовано модель об'єктних повноважень Capsicum. Після виклику `cap_enter(2)` процес втрачає доступ до глобальних просторів назв (файлова система, таблиця мережевих адрес). Усі операції можуть виконуватися виключно над уже відкритими файловими дескрипторами з явно обмеженими бітовими масками прав (`cap_rights_limit`).

## 7. Обмеження пристроїв через контрольні групи Cgroups v2

Для ізоляції апаратної поверхні та запобігання несанкціонованому доступу до драйверів пристроїв (`/dev/mem`, `/dev/kmem`, прямий доступ до дисків `/dev/sda`) ядро Linux використовує контролер пристроїв у Cgroups v2.

Контролер пристроїв керується через інтерфейс `cgroup.procs` та програмовані фільтри eBPF типу `BPF_PROG_TYPE_CGROUP_DEVICE`. На відміну від застарілих списків `devices.allow`/`devices.deny` у Cgroups v1, версія v2 перевіряє права відкриття символьних та блокових пристроїв за мажорними та мінорними номерами через швидкий JIT-компільований фільтр.

## 8. Інтроспекція та аудит поверхні атаки через `procfs`

Стан обмеження активного процесу можна діагностувати через віртуальну файлову систему `/proc` без зупинки процесу:

### 8.1. Перевірка статусу процесу (`/proc/[pid]/status`)

```text
Seccomp:        2         # 0 = вимкнено, 1 = strict, 2 = filter
NoNewPrivs:     1         # 1 = підвищення привілеїв заборонено
CapInh: 0000000000000000  # Спадковані можливості (Inherited)
CapPrm: 0000000000000000  # Дозволені можливості (Permitted)
CapEff: 0000000000000000  # Ефективні активні можливості (Effective)
CapBnd: 0000000000000000  # Межа можливостей (Bounding Set)
CapAmb: 0000000000000000  # Фонова множина (Ambient)
```

Значення `Seccomp: 2` свідчить про активний фільтр BPF, а нульові бітові маски `Cap*` підтверджують повну відсутність привілеїв Linux capabilities.

### 8.2. Доступні дії Seccomp у ядрі (`/proc/sys/kernel/seccomp/actions_avail`)

```text
kill_process kill_thread trap errno user_notif trace log allow
```

Цей псевдофайл відображає повний перелік дій Seccomp, які підтримуються поточною збіркою ядра Linux. Утиліти моніторингу використовують його для перевірки готовності платформи до суворого сандбоксингу.
