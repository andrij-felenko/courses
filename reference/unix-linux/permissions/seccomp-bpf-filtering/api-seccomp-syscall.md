# 📋 Інтерфейс системного виклику seccomp та структури даних

Системний виклик `seccomp(2)` є основою низькорівневого інтерфейсу підсистеми Secure Computing Mode у ядрі Linux, починаючи з версії 3.17. Він надає уніфікований контракт для завантаження BPF-фільтрів, перевірки підтримуваних дій ядра, синхронізації правил між потоками та організації перехоплення викликів у просторі користувача.

## 1. Сигнатура та параметри системного виклику `seccomp(2)`

На відміну від застарілого виклику `prctl(PR_SET_SECCOMP, ...)`, системний виклик `seccomp(2)` розроблений із можливістю розширення через прапорці та підтримує повернення результатів специфічних операцій (наприклад, створення дескрипторів сповіщень).

Заголовочний файл ядра `<linux/seccomp.h>` оголошує операції та прапорці, а обгортка системного виклику у `libc` або безпосередній виклик через `syscall(3)` дає доступ до підсистеми з простору користувача.

:::tabs
```c
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/seccomp.h>

// Сигнатура виклику seccomp(2) на рівні ядра
int seccomp(unsigned int operation, unsigned int flags, void *args);

// Приклад виклику через прямий glibc syscall wrapper
int result = syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, flags, &prog);
```
```cpp
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/seccomp.h>
#include <system_error>
#include <expected>

namespace sys {

// Ідіоматична C++23 обгортка для системного виклику seccomp
inline std::expected<void, std::error_code> seccomp_call(
    unsigned int operation, 
    unsigned int flags, 
    void* args) noexcept 
{
    long rc = ::syscall(SYS_seccomp, operation, flags, args);
    if (rc < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

} // namespace sys
```
:::

Перелічимо детальні характеристики кожного з трьох параметрів виклику:

1. `operation` — беззнакове ціле число, яке визначає конкретний режим роботи або запит інспекції. Ядро Linux підтримує чотири основні операції:
   - `SECCOMP_SET_MODE_STRICT` (`0`): Активує початковий суворий режим. Процесу дозволяється виконувати лише системні виклики `read`, `write`, `_exit` та `rt_sigreturn`. Спроба передати будь-які прапорці `flags` або вказівник `args`, відмінний від `NULL`, призводить до негайної відмови з кодом `EINVAL`.
   - `SECCOMP_SET_MODE_FILTER` (`1`): Завантажує програму Classic BPF (cBPF), передану у параметрі `args` як вказівник на структуру `struct sock_fprog`. Програмі передує обов'язкова перевірка `PR_SET_NO_NEW_PRIVS` або наявність `CAP_SYS_ADMIN`.
   - `SECCOMP_GET_ACTION_AVAIL` (`2`): Дозволяє процесу дізнатися, чи підтримує поточне ядро конкретну дію seccomp (наприклад, `SECCOMP_RET_USER_NOTIF` або `SECCOMP_RET_LOG`). Параметр `flags` повинен дорівнювати `0`, а `args` вказує на 32-бітну константу дії `__u32`. Повертає `0` при успіху і `-1` з `EOPNOTSUPP`, якщо ядро не підтримує цю дію.
   - `SECCOMP_GET_NOTIF_SIZES` (`3`): Запитує у ядра розміри внутрішніх структур сповіщень `struct seccomp_notif` та `struct seccomp_notif_resp`. Потрібно, щоб виділити буфери достатнього розміру при роботі з `SECCOMP_RET_USER_NOTIF`: структури ростуть від версії до версії, і зашитий у програму `sizeof` рано чи пізно розійдеться з ядром.

2. `flags` — бітова маска модифікації поведінки завантаженого фільтра:
   - `SECCOMP_FILTER_FLAG_TSYNC` (`1 << 0`): Потоковий синхронізатор. Атомарно застосовує BPF-фільтр до всіх потоків групи (thread group). Якщо хоча б один потік не здатен прийняти фільтр (уже має несумісний ланцюжок фільтрів або не має `PR_SET_NO_NEW_PRIVS`), стан жодного потоку не змінюється, а виклик повертає не `0` і не `-1`, а ідентифікатор одного з таких потоків.
   - `SECCOMP_FILTER_FLAG_LOG` (`1 << 1`): Примусово логує в auditd усі дії даного фільтра, окрім `SECCOMP_RET_ALLOW`.
   - `SECCOMP_FILTER_FLAG_SPEC_ALLOW` (`1 << 2`): Скасовує автоматичне пом'якшення Speculative Store Bypass (Spectre v4), яке ядро інакше вмикає для кожного процесу з seccomp-фільтром: швидше, але без цього захисту.
   - `SECCOMP_FILTER_FLAG_NEW_LISTENER` (`1 << 3`): Повертає новий файловий дескриптор сповіщень `seccomp_unotify` для обробки викликів у просторі користувача.

3. `args` — бестиповий вказівник на буфер даних користувача, структура якого залежить від значення `operation`.

## 2. Формат і розкладка структури `seccomp_data` в пам'яті

При виконанні будь-якого системного виклику ядро формує в пам'яті структуру `seccomp_data` на основі регістрів процесора і передає її як аргумент cBPF-програмі.

:::tabs
```c
#include <linux/seccomp.h>
#include <linux/types.h>

struct seccomp_data {
    int   nr;                   /* Номер системного виклику */
    __u32 arch;                 /* Архітектура процесора (AUDIT_ARCH_*) */
    __u64 instruction_pointer;  /* Вказівник на інструкцію в користувацькому просторі */
    __u64 args[6];              /* Аргументи системного виклику (значення) */
};
```
```cpp
#include <linux/seccomp.h>
#include <cstdint>
#include <span>

namespace sys {

// Структурне представлення аргументів виклику для безпечного обходу у C++
struct SeccompDataView {
    int32_t nr;
    uint32_t arch;
    uint64_t ip;
    std::span<const uint64_t, 6> args;

    explicit SeccompDataView(const ::seccomp_data& raw) noexcept
        : nr(raw.nr), arch(raw.arch), ip(raw.instruction_pointer), args(raw.args) {}
};

} // namespace sys
```
:::

Поле `nr` містить номер системного виклику. Важливо враховувати, що цей номер є відносним для кожної системної архітектури. Поле `arch` зберігає константу архітектури, визначену в `<linux/audit.h>` (наприклад, `AUDIT_ARCH_X86_64` = `0xc000003e`, `AUDIT_ARCH_I386` = `0x40000003`, `AUDIT_ARCH_AARCH64` = `0xc00000b7`). 

Поле `instruction_pointer` зберігає 64-бітну адресу лічильника інструкцій процесора (`rip` на x86_64), з якої було здійснено виклик. Поле `args` являє собою масив із шести 64-бітних цілих чисел, в які копіюються значення з процесорних регістрів передачі параметрів (`rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9`).

## 3. Структури BPF інструкцій `sock_filter` та `sock_fprog`

Фільтрація у seccomp реалізована через інтерфейс інструкцій Classic BPF.

:::tabs
```c
#include <linux/filter.h>

struct sock_filter {
    __u16 code;  /* Код інструкції (наприклад, BPF_LD | BPF_W | BPF_ABS) */
    __u8  jt;    /* Зміщення переходу при істинності умови (Jump True) */
    __u8  jf;    /* Зміщення переходу при хибності умови (Jump False) */
    __u32 k;     /* Багатофункціональне поле операнда / зміщення / константи */
};

struct sock_fprog {
    unsigned short len;         /* Кількість інструкцій BPF у масиві */
    struct sock_filter *filter; /* Вказівник на масив інструкцій */
};
```
```cpp
#include <linux/filter.h>
#include <vector>
#include <span>

namespace sys {

// C++ контейнерний тип для безпечного керування пам'яттю BPF програм
class BpfProgram {
    std::vector<::sock_filter> instructions_;
public:
    explicit BpfProgram(std::vector<::sock_filter> instrs) 
        : instructions_(std::move(instrs)) {}

    [[nodiscard]] ::sock_fprog get_fprog() const noexcept {
        return ::sock_fprog{
            .len = static_cast<unsigned short>(instructions_.size()),
            .filter = const_cast<::sock_filter*>(instructions_.data())
        };
    }
};

} // namespace sys
```
:::

Структура `sock_filter` описує одну 8-байтну інструкцію віртуальної машини. Поле `code` складається з коду операції, класу інструкції та режиму адресації. Поля `jt` та `jf` визначають відносні зміщення в інструкціях для переходів за результатами порівняння. Поле `k` виступає константою операнда або зміщенням у байтах від початку структури `seccomp_data`.

## 4. Контракт інтерфейсу користувацьких сповіщень (`SECCOMP_RET_USER_NOTIF`)

Дія `SECCOMP_RET_USER_NOTIF` дозволяє передавати обробку перехопленого виклику зовнішньому процесу-супервізору. При поверненні цієї дії фільтром ядро створює сповіщення і блокує потік користувача.

:::tabs
```c
#include <linux/seccomp.h>

struct seccomp_notif {
    __u64 id;                   /* Унікальний 64-бітний ідентифікатор запиту */
    __u32 pid;                  /* PID процесу, що зробив системний виклик */
    __u32 flags;                /* Прапорці сповіщення */
    struct seccomp_data data;   /* Повний пакет даних системного виклику */
};

struct seccomp_notif_resp {
    __u64 id;                   /* Ідентифікатор запиту (мусить збігатися з seccomp_notif.id) */
    __s64 val;                  /* Значення, яке поверне системний виклик (при успіху) */
    __s32 error;                /* Код помилки (від'ємне значення errno, наприклад -EPERM) */
    __u32 flags;                /* Прапорці відповіді (SECCOMP_USER_NOTIF_FLAG_CONTINUE) */
};
```
```cpp
#include <linux/seccomp.h>
#include <sys/ioctl.h>
#include <expected>
#include <system_error>

namespace sys {

struct UserNotificationHandler {
    static std::expected<::seccomp_notif, std::error_code> receive_notif(int listener_fd) noexcept {
        ::seccomp_notif req{};
        if (::ioctl(listener_fd, SECCOMP_IOCTL_NOTIF_RECV, &req) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return req;
    }

    static std::expected<void, std::error_code> send_response(
        int listener_fd, 
        const ::seccomp_notif_resp& resp) noexcept 
    {
        if (::ioctl(listener_fd, SECCOMP_IOCTL_NOTIF_SEND, &resp) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }
};

} // namespace sys
```
:::

Для обміну повідомленнями супервізор використовує виклики `ioctl(2)` на дескрипторі `seccomp_unotify`:
- `SECCOMP_IOCTL_NOTIF_RECV`: Читає наступне сповіщення з черги ядра у `struct seccomp_notif`.
- `SECCOMP_IOCTL_NOTIF_SEND`: Відправляє результат `struct seccomp_notif_resp` ядру, що спричиняє розблокування цільового потоку.
- `SECCOMP_IOCTL_NOTIF_ID_VALID`: Перевіряє, чи ідентифікатор `id` іще дійсний, тобто чи не завершився тим часом заблокований потік. Без цієї перевірки супервізор ризикує виконати дію від імені вже мертвого процесу, чий PID міг дістатися іншому.
- `SECCOMP_IOCTL_NOTIF_ADDFD`: Інжектує новий дескриптор файлу у простір цільового процесу.

## 5. Системні коди помилок та procfs-інтерфейс інспекції

Системний виклик `seccomp(2)` повертає значення `0` при успішному виконанні та `-1` при виникненні помилок, встановлюючи `errno`.

| Код помилки | Внутрішня причина у ядрі Linux |
| :--- | :--- |
| `EFAULT` | Переданий вказівник `args` виходить за межі адресованості пам'яті процесу користувача. |
| `EINVAL` | Невідома операція `operation`, некоректні прапорці `flags` або cBPF програма містить недопустимі інструкції чи недосяжні блоки. |
| `EPERM` | Процес не має `CAP_SYS_ADMIN` і прапорець `PR_SET_NO_NEW_PRIVS` не був встановлений перед `SECCOMP_SET_MODE_FILTER`. |
| `EBUSY` | Вказано `SECCOMP_FILTER_FLAG_NEW_LISTENER`, але в процесу вже є фільтр зі встановленим слухачем сповіщень. |
| `ENOMEM` | Недостатньо пам'яті ядра для виділення внутрішніх структур фільтра або виконання JIT-компіляції. |
| `EOPNOTSUPP` | Дія, передана в `SECCOMP_GET_ACTION_AVAIL`, не підтримується цим ядром. |

Конфігурація доступних дій та налаштувань логування перебуває у `procfs`, у гілці `sysctl` за шляхом `/proc/sys/kernel/seccomp/`. Файл `actions_avail` містить список усіх дій, підтримуваних ядром, а `actions_logged` визначає дії, які викликають запис у системний auditd.
