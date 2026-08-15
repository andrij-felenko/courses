# 📋 Системні виклики та API для програмування реального часу

Створення користувацького процесу реального часу у Linux вимагає виходу за межі стандартної моделі POSIX і явного керування планувальними класами, блокуванням пам'яті та таймерами через спеціалізовані системні виклики ядра. Потрібних інтерфейсів небагато: `sched_setscheduler()` і `sched_setattr()` задають клас та пріоритет, `pthread_setschedparam()` разом із `pthread_setaffinity_np()` роблять те саме для окремого потоку й закріплюють його за ядром CPU, `mlockall()` замикає пам'ять у RAM, а `clock_nanosleep()` тримає період циклу без дрейфу. Уся RT-програма під `PREEMPT_RT` будується довкола цих шести викликів, тож важать їхні точні контракти — параметри, діапазони й коди помилок.

## 1. Системний виклик sched_setscheduler та sched_setattr

Для призначення процесів до класів реального часу `SCHED_FIFO` або `SCHED_RR` використовується системний виклик `sched_setscheduler()` або його сучасне розширення `sched_setattr()`.

Звичайний процес у Linux за замовчуванням належить до класу `SCHED_OTHER` (або `SCHED_NORMAL`), в якому розподіл процесорного часу здійснюється за допомогою вирівнювання віртуального часу виконання — до ядра 6.6 це робив CFS, від 6.6 його місце посів EEVDF; для RT-класів заміна нічого не змінила, бо вони обслуговуються раніше й окремо. Для гарантованого витіснення фонових задач процеси реального часу переводяться у класи `SCHED_FIFO` або `SCHED_RR`.

### Сигнатура POSIX виклику sched_setscheduler

:::tabs
```c
#include <sched.h>

int sched_setscheduler(pid_t pid, int policy, const struct sched_param *param);
```
```cpp
#include <sched.h>

int sched_setscheduler(pid_t pid, int policy, const struct sched_param *param) noexcept;
```
:::

Поле `sched_priority` визначає пріоритет процесу в діапазоні від 1 (найнижчий RT-пріоритет) до 99 (найвищий RT-пріоритет). Планувальник реального часу завжди обирає для виконання потік із найвищим числовим значенням пріоритету серед усіх готових до виконання потоків на цьому CPU.

| Параметр | Тип | Опис |
| :--- | :--- | :--- |
| `pid` | `pid_t` | Ідентифікатор процесу або потоку (`0` означає сам потік, що робить виклик). |
| `policy` | `int` | Клас планування: `SCHED_FIFO` (першим прийшов — першим виконався), `SCHED_RR` (Round-Robin із квантом часу), `SCHED_OTHER` (стандартний). |
| `param` | `const struct sched_param*` | Структура, що містить поле `sched_priority` (діапазон від 1 до 99 для RT-класів). |

### Сучасний виклик sched_setattr для SCHED_DEADLINE

Для роботи з алгоритмом Earliest Deadline First (EDF) у класі `SCHED_DEADLINE` використовується розширений системний виклик `sched_setattr()`, що приймає структуру `struct sched_attr`. Цей клас планування гарантує процесу отримання `Q` наносекунд процесорного часу (`sched_runtime`) протягом кожного періоду `P` (`sched_period`) з інтервалом дедлайну `D` (`sched_deadline`).

:::tabs
```c
#include <sched.h>
#include <sys/syscall.h>
#include <unistd.h>

struct sched_attr {
    uint32_t size;              // Розмір структури (sizeof(struct sched_attr))
    uint32_t sched_policy;      // SCHED_DEADLINE (6)
    uint64_t sched_flags;       // Додаткові прапорці (SCHED_FLAG_RESET_ON_FORK)
    int32_t  sched_nice;        // Використовується для SCHED_OTHER (-20..19)
    uint32_t sched_priority;    // Використовується для SCHED_FIFO/RR (1..99)
    
    /* Параметри реального часу для SCHED_DEADLINE (у наносекундах) */
    uint64_t sched_runtime;     // Гарантований час виконання на період
    uint64_t sched_deadline;    // Відносний дедлайн
    uint64_t sched_period;      // Період повторення завдання
};
```
```cpp
#include <sched.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <cstdint>

struct sched_attr {
    std::uint32_t size;           // Розмір структури (sizeof(struct sched_attr))
    std::uint32_t sched_policy;   // SCHED_DEADLINE (6)
    std::uint64_t sched_flags;    // Додаткові прапорці (SCHED_FLAG_RESET_ON_FORK)
    std::int32_t  sched_nice;     // Використовується для SCHED_OTHER (-20..19)
    std::uint32_t sched_priority; // Використовується для SCHED_FIFO/RR (1..99)
    
    /* Параметри реального часу для SCHED_DEADLINE (у наносекундах) */
    std::uint64_t sched_runtime;  // Гарантований час виконання на період
    std::uint64_t sched_deadline; // Відносний дедлайн
    std::uint64_t sched_period;   // Період повторення завдання
};
```
:::

Поле `size` робить структуру розширюваною: програма передає `sizeof(struct sched_attr)` свого заголовка, а ядро визначає за цим числом, скільки полів воно розуміє. Тому склад структури залежить від версії — приміром, у ядрах від 5.3 у її хвості з'явилися ще `sched_util_min` і `sched_util_max` (підказки утилізації для регулятора частоти), і код, зібраний зі старішим заголовком, працює далі без змін.

При використанні `SCHED_DEADLINE` ядро перевіряє через сервер сталої пропускної здатності (Constant Bandwidth Server, CBS), чи не призведе долучення нового завдання до перевантаження процесора. Поріг допуску — не 100%: для кореневого домену з `M` процесорів сума часток `∑ (Q[i] / P[i])` усіх deadline-завдань мусить лишатися нижчою за `M × (sched_rt_runtime_us / sched_rt_period_us)`, тобто за замовчуванням — нижчою за 95% від `M`. Завдання, яке не проходить цю перевірку, дістає `EBUSY`, а не мовчазне погіршення часу реакції.

| Поле `sched_attr` | Одиниці виміру | Обмеження / Опис |
| :--- | :--- | :--- |
| `sched_runtime` | наносекунди | `sched_runtime <= sched_deadline`. Бюджет часу виконання. |
| `sched_deadline` | наносекунди | `sched_deadline <= sched_period`. Максимальний дозволений час до завершення. |
| `sched_period` | наносекунди | Інтервал генерації завдань (наприклад, 1 000 000 нс = 1 мс). |

## 2. POSIX Threads API: pthread_setschedparam та прив'язка до ядер

У багатопотокових програмах налаштування пріоритетів реального часу для окремих потоків (POSIX Threads) виконується за допомогою `pthread_setschedparam()`. Крім встановлення пріоритету, критично важливим для RT-потоку є ізоляція від інших процесів шляхом жорсткого закріплення за конкретним ядром процесора за допомогою `pthread_setaffinity_np()`.

:::tabs
```c
#include <pthread.h>
#include <sched.h>

int pthread_setschedparam(pthread_t thread, int policy, const struct sched_param *param);
int pthread_setaffinity_np(pthread_t thread, size_t cpusetsize, const cpu_set_t *cpuset);
```
```cpp
#include <pthread.h>
#include <sched.h>

int pthread_setschedparam(pthread_t thread, int policy, const struct sched_param *param) noexcept;
int pthread_setaffinity_np(pthread_t thread, std::size_t cpusetsize, const cpu_set_t *cpuset) noexcept;
```
:::

Прив'язка потоку до виділеного ядра процесора (котре вилучено із загального планування за допомогою `isolcpus` або `nohz_full`) повністю усуває між'ядерну міграцію потоку та міжпроцесорні переривання IPI (Inter-Processor Interrupts), зменшуючи варіацію затримок (jitter).

### Приклад встановлення RT-пріоритету та прив'язки потоку C / C++

:::tabs
```c
#define _GNU_SOURCE
#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include <string.h>

int configure_thread_rt_and_affinity(pthread_t thread, int priority, int cpu_id) {
    struct sched_param param;
    cpu_set_t cpuset;

    /* 1. Встановлення RT-пріоритету SCHED_FIFO.
       Функції pthread_* повертають код помилки й НЕ встановлюють errno,
       тому тут strerror(ret), а не perror(). */
    param.sched_priority = priority;
    int ret = pthread_setschedparam(thread, SCHED_FIFO, &param);
    if (ret != 0) {
        fprintf(stderr, "pthread_setschedparam failed: %s\n", strerror(ret));
        return ret;
    }

    /* 2. Прив'язка до конкретного ядра CPU */
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    ret = pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset);
    if (ret != 0) {
        fprintf(stderr, "pthread_setaffinity_np failed: %s\n", strerror(ret));
        return ret;
    }

    return 0;
}
```
```cpp
#include <pthread.h>
#include <sched.h>
#include <system_error>
#include <expected>

std::expected<void, std::error_code> configure_thread_rt_and_affinity(pthread_t thread, int priority, int cpu_id) noexcept {
    // 1. Встановлення RT-пріоритету SCHED_FIFO
    struct sched_param param{};
    param.sched_priority = priority;
    if (int res = pthread_setschedparam(thread, SCHED_FIFO, &param); res != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(res)));
    }

    // 2. Прив'язка до конкретного ядра CPU
    cpu_set_t cpuset{};
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    if (int res = pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset); res != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(res)));
    }

    return {};
}
```
:::

## 3. Блокування віртуальної пам'яті: mlockall та mlock

Виклики `mlockall()` та `munlockall()` запобігають вивантаженню сторінок віртуальної пам'яті у swap та усувають затримки, спричинені підкачуванням сторінок за запитом (Page Faults).

:::tabs
```c
#include <sys/mman.h>

int mlockall(int flags);
int munlockall(void);
```
```cpp
#include <sys/mman.h>

int mlockall(int flags) noexcept;
int munlockall() noexcept;
```
:::

Виклик `mlockall(MCL_CURRENT | MCL_FUTURE)` примусово відображає і блокує всі поточні та майбутні сторінки у фізичній оперативній пам'яті, знімаючи Page Faults із критичного циклу (звідки саме беруться ці затримки й скільки коштують — розібрано у практичному керівництві).

Контракт виклику має три межі, про які легко забути. По-перше, `mlockall()` потребує або права `CAP_IPC_LOCK`, або запасу в ліміті `RLIMIT_MEMLOCK` — інакше повертається `ENOMEM` (ліміт вичерпано) чи `EPERM` (ліміт нульовий і привілею немає), і програма мовчки лишається без гарантії, якщо не перевіряти код повернення. По-друге, `MCL_FUTURE` діє на нові відображення процесу, але не на сторінки, які може додати ядро в обхід (наприклад, при `fork()` замкненість не успадковується — дочірній процес починає з незамкненою пам'яттю). По-третє, замкнення не знімає копіювання при записі: сторінка, спільна після `fork()`, усе одно спричинить Page Fault на першому ж записі, тож RT-потоки не породжують нащадків із критичного циклу.

| Прапор `mlockall` | Значення | Опис |
| :--- | :--- | :--- |
| `MCL_CURRENT` | `1` | Заблокувати всі сторінки, вже відображені в адресний простір процесу. |
| `MCL_FUTURE` | `2` | Автоматично блокувати всі нові сторінки, які будуть виділені у майбутньому (`malloc`, `mmap`, стек). |
| `MCL_ONFAULT` | `4` | Блокувати сторінку лише після першого звернення до неї (пришвидшує старт, але вимагає prefaulting). Вживається тільки разом із `MCL_CURRENT` чи `MCL_FUTURE`, самотою — `EINVAL`. |

## 4. Високоточні таймери: clock_nanosleep

Проблема `usleep()`, `nanosleep()` чи таймауту `select()` не в роздільності — після появи hrtimers усі вони лягають на високоточні таймери, — а в тому, що всі вони задають затримку **відносно моменту виклику**. Для періодичного циклу це означає накопичення дрейфу. Тому у `PREEMPT_RT` обов'язковим є `clock_nanosleep()` з монотонним годинником `CLOCK_MONOTONIC` та абсолютним прапорцем `TIMER_ABSTIME`.

:::tabs
```c
#include <time.h>

int clock_nanosleep(clockid_t clock_id, int flags,
                    const struct timespec *request,
                    struct timespec *remain);
```
```cpp
#include <time.h>

int clock_nanosleep(clockid_t clock_id, int flags,
                    const struct timespec *request,
                    struct timespec *remain) noexcept;
```
:::

При використанні відносного сну (`flags = 0`, як у `nanosleep()`), якщо обчислення в критичному циклі зайняли 80 мікросекунд, а затримка сну була вказана як 1000 мікросекунд, наступне пробудження настане не через 1000, а через `80 + 1000 = 1080` мікросекунд від попереднього. Похибка накопичуватиметься з кожною ітерацією (jitter drift). При використанні абсолютного часу (`TIMER_ABSTIME`) потік вказує точну позначку часу майбутньої події (`T₀ + N · T_period`), і ядро розбудить потік строго в розрахований момент, незалежно від тривалості обчислень усередині циклу.

| Параметр | Опис |
| :--- | :--- |
| `clock_id` | `CLOCK_MONOTONIC` — незалежний від стрибків системного часу (NTP, `date`). Виклик приймає ще `CLOCK_REALTIME`, `CLOCK_BOOTTIME`, `CLOCK_TAI` і `CLOCK_PROCESS_CPUTIME_ID`, але **не** `CLOCK_MONOTONIC_RAW` (той годинник читається лише через `clock_gettime()`). |
| `flags` | `TIMER_ABSTIME` — заснути до строго визначеного моменту часу (`T₀ + N · T_period`, а не «ще стільки-то від зараз»). Запобігає дрейфу часу (jitter drift). `0` — звичайний відносний сон. |
| `request` | Вказівник на структуру `struct timespec` із цільовим часом пробудження. |
| `remain` | Вказівник на структуру, куди записується залишок часу у разі переривання сигналом (при `TIMER_ABSTIME` не використовується, передають `NULL`). |

## 5. Обмеження ресурсів та системні налаштування sysctl

Ядро Linux містить запобіжні механізми для відвернення повного зависання системи у разі помилки у RT-процесі (наприклад, якщо потік з пріоритетом `SCHED_FIFO` 99 увійшов у нескінченний цикл без викликів сну).

Конфігураційні параметри `sysctl`:
- `kernel.sched_rt_period_us`: Загальний період оновлення квоти реального часу (за замовчуванням 1 000 000 мкс = 1 с).
- `kernel.sched_rt_runtime_us`: Максимальний процесорний час, який дозволено сумарно витрачати всім RT-процесам протягом періоду (за замовчуванням 950 000 мкс = 95%). 5% процесорного часу резервується для виконання системної оболонки та потоків ядра, що дозволяє адміністраторові зупинити зациклений RT-процес.
- Значення `-1` для `kernel.sched_rt_runtime_us` вимикає обмежувач реального часу, віддаючи 100% CPU під RT-задачі (використовується на повністю ізольованих ядрах).

## 6. Таблиця кодів помилок системних викликів RT

| Код помилки | Константа | Причина виникнення у RT-контексті |
| :--- | :--- | :--- |
| `1` | `EPERM` | Бракує потрібного привілею: `CAP_SYS_NICE` для переведення в RT-клас (або вичерпано `RLIMIT_RTPRIO`), `CAP_IPC_LOCK` — для `mlockall()` при нульовому `RLIMIT_MEMLOCK`. |
| `12` | `ENOMEM` | Спроба `mlockall()` перевищила фізичний обсяг RAM або ліміт `RLIMIT_MEMLOCK`. |
| `16` | `EBUSY` | `SCHED_DEADLINE`: завдання не проходить контроль допуску CBS — вільної пропускної здатності на кореневому домені бракує. |
| `22` | `EINVAL` | Некоректний пріоритет (наприклад, `sched_priority > 99` для `SCHED_FIFO`) або порушення умови `sched_runtime ≤ sched_deadline ≤ sched_period`. |
| `38` | `ENOSYS` | Ядро не знає виклику `sched_setattr()`: він з'явився у Linux 3.14, тож на старіших ядрах доступні лише `sched_setscheduler()` і `SCHED_FIFO`/`SCHED_RR`. |
