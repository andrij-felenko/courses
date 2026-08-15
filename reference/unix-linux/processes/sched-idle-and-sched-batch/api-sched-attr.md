# 📋 Системний виклик sched_setattr та структура sched_attr

Системний виклик `sched_setattr` та супутній `sched_getattr` упроваджені в ядрі Linux 3.14 як уніфікований розширюваний ABI для керування атрибутами планування процесів і потоків. Вони перекривають можливості старішої групи POSIX-викликів (`sched_setscheduler`, `sched_setparam`, `nice`), не скасовуючи їх, і дають єдиний точний інтерфейс для класів `SCHED_OTHER`, `SCHED_BATCH`, `SCHED_IDLE`, `SCHED_FIFO`, `SCHED_RR` та `SCHED_DEADLINE`.

## 1. Сигнатура та номери системних викликів

Оскільки стандартна бібліотека C (glibc / musl) тривалий час не надавала прямих обгорток C для `sched_setattr` у заголовку `<sched.h>`, виконання здійснюється через прямий виклик `syscall(2)`, а `struct sched_attr` беруть із UAPI-заголовка `<linux/sched/types.h>` або оголошують у програмі самотужки.

```c
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/sched.h>

int sched_setattr(pid_t pid, struct sched_attr *attr, unsigned int flags);
int sched_getattr(pid_t pid, struct sched_attr *attr, unsigned int size, unsigned int flags);
```

Номери системного виклику у таблиці Linux ABI залежать від архітектури CPU:

| Архітектура CPU | `SYS_sched_setattr` | `SYS_sched_getattr` |
| :--- | :--- | :--- |
| `x86_64` | `314` | `315` |
| `x86` (32-bit) | `351` | `352` |
| `arm64` (aarch64) | `274` | `275` |
| `riscv64` | `274` | `275` |
| `powerpc` (64-bit) | `355` | `356` |

При передачі `pid = 0` ядро застосовує зміни до викликаючого потоку (calling thread). Для зміни атрибутів іншого потоку вимагається вказати його дійсний TID (Thread ID) або PID процесу, при цьому викликаючий процес повинен мати тотожний ефективний UID або привілей `CAP_SYS_NICE`.

Аргумент `flags` у виклику `sched_setattr` наразі зарезервований ядром і повинен дорівнювати `0`. Використання ненульових значень у цьому аргументі викликає повернення помилки `EINVAL`.

## 2. Структура struct sched_attr та модель сумісності ABI

Структура `sched_attr` розроблена з урахуванням прямої та зворотної сумісності за допомогою внутрішньої функції ядра `copy_struct_from_user`. Поле `size` визначає розмір структури у байтах, переданої з простору користувача.

```c
struct sched_attr {
    uint32_t size;              /* Розмір цієї структури в байтах (для розширюваності) */
    uint32_t sched_policy;      /* Політика планування (SCHED_OTHER, SCHED_BATCH, SCHED_IDLE, тощо) */
    uint64_t sched_flags;       /* Прапорці розширення (SCHED_FLAG_RESET_ON_FORK тощо) */
    int32_t  sched_nice;        /* Значення nice (-20..+19) для SCHED_OTHER та SCHED_BATCH */
    uint32_t sched_priority;    /* Статичний пріоритет (1..99 для RT; 0 для BATCH/IDLE/OTHER) */
    
    /* Поля для політики SCHED_DEADLINE (в наносекундах) */
    uint64_t sched_runtime;     /* Гарантований час виконання за період */
    uint64_t sched_deadline;    /* Відносний дедлайн */
    uint64_t sched_period;      /* Період виконання */
    
    /* Поля розширення ядра (Linux 5.3+) */
    uint32_t sched_util_min;    /* uclamp.min: мінімальна утилізація CPU */
    uint32_t sched_util_max;    /* uclamp.max: максимальна утилізація CPU */
};
```

### Схема вирівнювання пам'яті структури в 64-бітних системах

Для запобігання невидимому падінню продуктивності при зчитуванні з невирівняних адрес пам'яті структура `sched_attr` вирівняна по 8-байтовій межі:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                     size (uint32_t = 48..)                    |  0x00
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                 sched_policy (uint32_t = 0..6)                |  0x04
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |  0x08
+                       sched_flags (uint64_t)                  +
|                                                               |  0x0C
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                 sched_nice (int32_t = -20..19)                |  0x10
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|               sched_priority (uint32_t = 0..99)               |  0x14
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |  0x18
+                       sched_runtime (uint64_t)                +
|                                                               |  0x1C
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |  0x20
+                      sched_deadline (uint64_t)                +
|                                                               |  0x24
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |  0x28
+                       sched_period (uint64_t)                 +
|                                                               |  0x2C
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                 sched_util_min (uint32_t = 0..1024)           |  0x30 (Linux 5.3+)
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                 sched_util_max (uint32_t = 0..1024)           |  0x34 (Linux 5.3+)
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Двостороння сумісність розміру структури

Ядро Linux обробляє значення `attr->size` за наступними правилами:
1. **Старе ядро / новий додаток (`attr->size > kernel_size`):** Якщо програма передає структуру більшого розміру, ніж підтримує поточна версія ядра, ядро перевіряє додаткові поля на наявність ненульових значень. Якщо нові поля заповнені нулями (`0`), ядро виконує виклик, ігноруючи надлишкові поля. Якщо ж у додаткових полях є ненульові дані (якими програма вимагає непідтримувані ядром опції), виклик повертає помилку `E2BIG`.
2. **Нове ядро / старий додаток (`attr->size < kernel_size`):** Якщо програма скомпільована зі старою версією заголовків і передає менший розмір, ядро заповнює відсутні поля значеннями за замовчуванням (нулями).
3. **Недопустимий розмір (`attr->size < SCHED_ATTR_SIZE_VER0`):** Якщо значення `size` менше за базову версію структури (48 байтів для Linux 3.14), ядро повертає помилку `EINVAL`.

При виклику `sched_getattr` аргумент `size` вказує розмір буфера у просторі користувача. Якщо розмір буфера менший за структуру ядра, виклик завершується помилкою `E2BIG`; актуальний розмір програма дізнається не звідси, а з поля `size`, яке ядро заповнює при успішному `sched_getattr`.

## 3. Детальний аналіз полів структури

Кожне поле структури `sched_attr` має жорстко регламентований діапазон допустимих значень:

* **`size`:** Вхідне значення типу `uint32_t`. Мусить бути ініціалізовано значенням `sizeof(struct sched_attr)`.
* **`sched_policy`:** Визначає алгоритм планування. Приймає значення:
  * `0`: `SCHED_OTHER` (або `SCHED_NORMAL`) — стандартний справедливий інтерактивний режим CFS.
  * `1`: `SCHED_FIFO` — реальночасовий клас з фіксованим пріоритетом без квантування.
  * `2`: `SCHED_RR` — реальночасовий клас з круговим квантуванням (Round-Robin).
  * `3`: `SCHED_BATCH` — пакетний режим CFS із пригніченим витисканням та збільшеними квантами.
  * `5`: `SCHED_IDLE` — фоновий режим з мінімальною вагою `WEIGHT_IDLEPRIO = 3`.
  * `6`: `SCHED_DEADLINE` — реальночасовий режим на основі алгоритму Earliest Deadline First (EDF).
* **`sched_flags`:** Бітова маска додаткових атрибутів (докладно описана в §4).
* **`sched_nice`:** Значення рівня `nice` у діапазоні від `-20` (найвищий пріоритет) до `+19` (найнижчий пріоритет). Застосовується лише для класів `SCHED_OTHER` та `SCHED_BATCH`. Для класів `SCHED_IDLE`, `SCHED_FIFO`, `SCHED_RR` та `SCHED_DEADLINE` це поле ігнорується або мусить дорівнювати `0`.
* **`sched_priority`:** Статичний реальночасовий пріоритет у діапазоні від `1` до `99` для класів `SCHED_FIFO` та `SCHED_RR`. Для класів `SCHED_OTHER`, `SCHED_BATCH`, `SCHED_IDLE` та `SCHED_DEADLINE` цей параметр обов'язково повинен дорівнювати `0`.
* **`sched_runtime`, `sched_deadline`, `sched_period`:** 64-бітні цілі числа в наносекундах. Використовуються виключно для політики `SCHED_DEADLINE`. Для інших класів мають бути занулені.
* **`sched_util_min` та `sched_util_max`:** Поля механізму Utilization Clamping (uclamp), впроваджені в Linux 5.3. Задають мінімальну та максимальну межу ефективної утилізації CPU в діапазоні `0..1024`.

### 3.1. Взаємодія uclamp із підсистемою Energy-Aware Scheduling (EAS)

Поля `sched_util_min` та `sched_util_max` відіграють критичну роль у гетерогенних архітектурах ARM big.LITTLE / DynamIQ (з високопродуктивними Cortex-X ядрами та енергоефективними Cortex-A ядрами):

* Встановлення `sched_util_min` (наприклад, значення `512` = 50% потужності): змушує планувальник розміщувати потік на продуктивних ядрах і підвищувати частоту CPU (cpufreq governor), навіть якщо потік виконує мало обчислень.
* Встановлення `sched_util_max` (наприклад, значення `256` = 25% потужності): обмежує частоту CPU зверху, примусово утримуючи фоновий процес (наприклад, `SCHED_BATCH` фонову конвертацію) на малих енергоефективних ядрах для збереження заряду батареї.

## 4. Прапорці sched_flags

Поле `sched_flags` підтримує бітові маски, що змінюють стандартну поведінку процесів при плануванні та успадкуванні:

*   `SCHED_FLAG_RESET_ON_FORK` (`0x01`): При розгалуженні процесу через системний виклик `fork()` дочірній процес не успадковує привілейовану політику або від'ємне значення `nice`. Якщо батьківський процес мав политику `SCHED_BATCH`, `SCHED_FIFO` або від'ємний `nice`, дочірній процес автоматично скидається до стандартної політики `SCHED_OTHER` із `nice = 0`. Це гарантує, що фоновий або привілейований потік не породить неконтрольовану деревоподібну ієрархію з підвищеними правами.
*   `SCHED_FLAG_RECLAIM` (`0x02`): Використовується політикою `SCHED_DEADLINE` для регенерації та перерозподілу невикористаного CPU-часу між іншими задачами дедлайну.
*   `SCHED_FLAG_DL_OVERRUN` (`0x04`): Дозволяє отримувати сповіщення та сигналізування про перевищення ліміту `sched_runtime` у політиці `SCHED_DEADLINE`.
*   `SCHED_FLAG_KEEP_POLICY` (`0x08`): Дозволяє змінити окремі параметри (наприклад, значення `nice` або `uclamp`), зберігаючи поточну політику планування процесу без її повторного вказування.
*   `SCHED_FLAG_KEEP_PARAMS` (`0x10`): Зберігає існуючі параметри пріоритету при зміні прапорців розширення.
*   `SCHED_FLAG_UTIL_CLAMP_MIN` (`0x20`): Активує встановку мінімальної межі частоти процесора (uclamp.min) для потоку (потрібна конфігурація ядра `CONFIG_UCLAMP_TASK`).
*   `SCHED_FLAG_UTIL_CLAMP_MAX` (`0x40`): Активує встановку максимальної межі частоти процесора (uclamp.max) для обмеження енергоспоживання.

## 5. Коди помилок та обробка виняткових ситуацій

У разі невдалого виконання `sched_setattr` повертає `-1` та встановлює значення `errno`:

*   `EPERM`: Викликаючий процес не має привілеїв `CAP_SYS_NICE` для підвищення пріоритету (наприклад, спроба встановити `nice` нижче за дозволений `RLIMIT_NICE` або зайти в реальночасовий клас понад `RLIMIT_RTPRIO`), або спроба змінити атрибути потоку іншого користувача без належних UID.
*   `EINVAL`: Вказано невідому політику `sched_policy`, недопустиме значення `sched_nice` (виходить за межі `-20..19`), ненульовий `sched_priority` для `SCHED_BATCH`/`SCHED_IDLE`/`SCHED_OTHER`, або суперечливі часові параметри `SCHED_DEADLINE` (`runtime > deadline` або `deadline > period`).
*   `E2BIG`: Переданий у `attr->size` розмір більший за відомий ядру, і в надлишкових полях є ненульові дані. Розмір, менший за `SCHED_ATTR_SIZE_VER0`, дає не `E2BIG`, а `EINVAL`.
*   `ESRCH`: Процес або потік із вказаним `pid` не існує в даному просторі імен PID (PID namespace).
*   `EBUSY`: Для політики `SCHED_DEADLINE` означає недопустимість прийняття нової реальної задачі через перевищення загальної ємності системи (admission control test failed).

## 6. Крайові випадки у контейнерах та ізольованих середовищах

При виконанні `sched_setattr` у середовищах ізоляції (Docker, LXC, systemd-nspawn) діють додаткові обмеження:

1. **User Namespaces та CAP_SYS_NICE:** Привілей `CAP_SYS_NICE` всередині контейнера дозволяє змінювати параметри лише тих процесів, які належать цьому ж простору імен користувача. Зміна класів планування процесів хостової системи з контейнера заборонена.
2. **Обмеження cgroups v2:** Якщо cgroup обмежує групу процесів за допомогою `cpu.max` або `cpu.weight`, системний виклик `sched_setattr(SCHED_BATCH)` або `sched_setattr(SCHED_IDLE)` продовжує функціонувати успішно, але підсумковий розподіл часу між cgroups визначається контролером верхнього рівня.
3. **LSM та Seccomp:** Профілі Seccomp за замовчуванням (наприклад, стандартний профіль Docker) можуть блокувати виклик `sched_setattr` з поверненням `EPERM` або сигналом `SIGSYS`, якщо в профілі не дозволено syscall 314 (x86_64).

## 7. Низькорівневий виклик на рівнях ABI та Асемблера

При безпосередньому використанні асемблерних вставок або створенні системних бібліотек виклик `sched_setattr` здійснюється через передачу аргументів у регістрах CPU згідно з відповідним ABI:

* **x86_64 ABI:** Номер системного виклику `314` поміщається в регістр `%rax`. Аргумент `pid` у `%rdi`, вказівник `attr` у `%rsi`, аргумент `flags` у `%rdx`. Виклик виконується інструкцією `syscall`.
* **ARM64 ABI:** Номер системного виклику `274` поміщається у `x8`. Аргументи `pid`, `attr`, `flags` — у регістри `x0`, `x1`, `x2`. Виклик виконується інструкцією `svc #0`.

Ця специфіка робить виклик `sched_setattr` незалежним від версії C-бібліотеки glibc, що критично для розробників автономних бінарних файлів та статично скомпільованих утиліт на мовах C++, Rust або Go.

## 8. Порівняння sched_setattr із застарілими викликами

Для розуміння еволюції API планування в Linux у таблиці зведено ключові відмінності між новими та старими системними викликами:

| Властивість | `nice(2)` / `setpriority(2)` | `sched_setscheduler(2)` | `sched_setattr(2)` |
| :--- | :--- | :--- | :--- |
| **Стандарт** | POSIX.1-2001 | POSIX.1-2001 | Специфічний для Linux (3.14+) |
| **Підтримка SCHED_BATCH** | Ні | Так | **Так** |
| **Підтримка SCHED_IDLE** | Ні | Так | **Так** |
| **Підтримка SCHED_DEADLINE**| Ні | Ні | **Так** |
| **Атомарна зміна policy + nice** | Ні | Ні | **Так** |
| **Розширюваність структури** | Ні (фіксовані int) | Ні (`struct sched_param`) | **Так** (через `attr.size`) |
| **Прапорці (RESET_ON_FORK)** | Ні | Окремий `sched_setparam` | **Так** (`sched_flags`) |

## 9. Еталонна реалізація встановлення політики SCHED_BATCH та SCHED_IDLE

Нижче наведено крос-архітектурні приклади встановлення політики `SCHED_BATCH` із заданням `nice` та скиданням політики при `fork()`.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/syscall.h>
#include <linux/sched.h>

#ifndef SYS_sched_setattr
#if defined(__x86_64__)
#define SYS_sched_setattr 314
#elif defined(__aarch64__)
#define SYS_sched_setattr 274
#elif defined(__riscv)
#define SYS_sched_setattr 274
#endif
#endif

#ifndef SCHED_FLAG_RESET_ON_FORK
#define SCHED_FLAG_RESET_ON_FORK 0x01
#endif

struct local_sched_attr {
    uint32_t size;
    uint32_t sched_policy;
    uint64_t sched_flags;
    int32_t  sched_nice;
    uint32_t sched_priority;
    uint64_t sched_runtime;
    uint64_t sched_deadline;
    uint64_t sched_period;
};

static int sys_sched_setattr(pid_t pid, const struct local_sched_attr *attr, unsigned int flags) {
    return (int)syscall(SYS_sched_setattr, pid, attr, flags);
}

int set_process_batch_policy(pid_t pid, int nice_val, int reset_on_fork) {
    struct local_sched_attr attr;
    memset(&attr, 0, sizeof(attr));
    
    attr.size = sizeof(attr);
    attr.sched_policy = SCHED_BATCH;
    attr.sched_nice = nice_val;
    attr.sched_priority = 0; // Для SCHED_BATCH пріоритет завжди 0
    
    if (reset_on_fork) {
        attr.sched_flags |= SCHED_FLAG_RESET_ON_FORK;
    }
    
    if (sys_sched_setattr(pid, &attr, 0) < 0) {
        perror("sched_setattr SCHED_BATCH failed");
        return -1;
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <system_error>
#include <cstdint>
#include <cerrno>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/sched.h>

#ifndef SYS_sched_setattr
#if defined(__x86_64__)
#define SYS_sched_setattr 314
#elif defined(__aarch64__)
#define SYS_sched_setattr 274
#elif defined(__riscv)
#define SYS_sched_setattr 274
#endif
#endif

#ifndef SCHED_FLAG_RESET_ON_FORK
#define SCHED_FLAG_RESET_ON_FORK 0x01
#endif

struct local_sched_attr {
    std::uint32_t size;
    std::uint32_t sched_policy;
    std::uint64_t sched_flags;
    std::int32_t  sched_nice;
    std::uint32_t sched_priority;
    std::uint64_t sched_runtime;
    std::uint64_t sched_deadline;
    std::uint64_t sched_period;
};

class TaskScheduler {
public:
    static void set_batch(pid_t pid, int nice_val, bool reset_on_fork) {
        local_sched_attr attr{};
        attr.size = sizeof(attr);
        attr.sched_policy = SCHED_BATCH;
        attr.sched_nice = nice_val;
        attr.sched_priority = 0;
        
        if (reset_on_fork) {
            attr.sched_flags |= SCHED_FLAG_RESET_ON_FORK;
        }
        
        if (::syscall(SYS_sched_setattr, pid, &attr, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                    "Не вдалося встановити SCHED_BATCH через sched_setattr");
        }
    }

    static void set_idle(pid_t pid) {
        local_sched_attr attr{};
        attr.size = sizeof(attr);
        attr.sched_policy = SCHED_IDLE;
        attr.sched_nice = 0;
        attr.sched_priority = 0;

        if (::syscall(SYS_sched_setattr, pid, &attr, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                    "Не вдалося встановити SCHED_IDLE через sched_setattr");
        }
    }
};
```
:::
