# 📋 Системні виклики прив'язки потоків, NUMA-політик та io_uring

Довідник містить специфікацію низькорівневих системних інтерфейсів Linux (POSIX API, `libnuma`, `io_uring` та сокетні прапорці), які використовуються під час проектування та реалізації високопродуктивних серверних систем архітектури Thread-per-core.

### 1. Системні виклики CPU Affinity (Прив'язка до ядер)

Інтерфейси призначені для жорсткої фіксації потоків виконання за конкретними фізичними ядрами процесора для усунення перемикання контексту та збереження локальності кеш-пам'яті L1/L2. Коли потік прив'язаний до одного ядра, планувальник ядра Linux вилучає його з глобальних черг балансування навантаження і гарантує, що потік виконуватиметься виключно на призначеному апаратному процесорі.

Функції `sched_setaffinity` та `pthread_setaffinity_np` приймають маску бітів процесорів, розмір якої передається параметром `cpusetsize`. Після успішного виклику планувальник негайно переносить потік на одне з дозволених ядер, якщо поточне ядро не входить до зазначеного набору.

Внутрішньо планувальник ядра Linux (модуль `kernel/sched/core.c`) оновлює поле `cpus_ptr` у дескрипторі процесу `task_struct`. Якщо потік у цей момент уже виконувався на іншому процесорі, ядро активує службовий потік міграції ядра `migration/N`, який примусово зупиняє виконання на старому ядрі та переносить стан регістрів на цільовий процесор.

:::tabs
```c
#define _GNU_SOURCE
#include <sched.h>
#include <pthread.h>

/* Встановлення маски дозволених ядер для процесу за його PID */
int sched_setaffinity(pid_t pid, size_t cpusetsize, const cpu_set_t *mask);

/* Отримання поточної маски дозволених ядер для процесу */
int sched_getaffinity(pid_t pid, size_t cpusetsize, cpu_set_t *mask);

/* Прив'язка конкретного POSIX-потоку до маски ядер */
int pthread_setaffinity_np(pthread_t thread, size_t cpusetsize, const cpu_set_t *cpuset);

/* Отримання маски ядер для конкретного POSIX-потоку */
int pthread_getaffinity_np(pthread_t thread, size_t cpusetsize, cpu_set_t *cpuset);
```
```cpp
#include <thread>
#include <stdexcept>
#include <system_error>
#include <pthread.h>
#include <sched.h>

namespace tpc {

/* Безпечна C++ обгортка над прив'язкою потоку std::jthread або native handle */
inline void set_current_thread_affinity(int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);

    const int rc = pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
    if (rc != 0) {
        throw std::system_error(rc, std::generic_category(), "Помилка встановлення CPU affinity");
    }
}

} // namespace tpc
```
:::

#### Макроси маніпуляції бітовими масками ядер
Маска ядер типу `cpu_set_t` являє собою бітовий масив, де кожен біт відповідає номеру логічного ядра процесора в системі (від `0` до `CPU_SETSIZE - 1`, за замовчуванням 1024 ядра):

| Макрос | Опис функціоналу |
|---|---|
| `void CPU_ZERO(cpu_set_t *set)` | Очищає маску, скидаючи всі біти ядер у нуль |
| `void CPU_SET(int cpu, cpu_set_t *set)` | Додає ядро з індексом `cpu` (0..`N-1`) до маски дозволених ядер |
| `void CPU_CLR(int cpu, cpu_set_t *set)` | Вилучає вказане ядро з маски виконання |
| `int CPU_ISSET(int cpu, const cpu_set_t *set)` | Повертає ненульове значення, якщо ядро присутнє у масці |
| `int CPU_COUNT(const cpu_set_t *set)` | Повертає загальну кількість активних ядер у масці |

#### Коди помилок системних викликів
- `EFAULT` — передано некоректну адресу покажчика маски в пам'яті.
- `EINVAL` — параметр `cpusetsize` менший за мінімальний розмір маски ядра або маска не містить жодного фізично доступного процесора.
- `ESRCH` — потік або процес із зазначеним ідентифікатором `pid` чи дескриптором `thread` не знайдено в системі.

Для забезпечення максимальної продуктивності прив'язаних потоків рекомендується виділяти ядра через параметр завантаження ядра Linux `isolcpus=2-63` та вмикати безтиковий режим `nohz_full=2-63`. Це вилучає зазначені ядра з загального планування ОС і вимикає обробку періодичних системних таймерів. Крім того, на рівні підсистеми `cgroups v2` можна задати суворі обмеження процесорних ресурсів через контролер `cpuset.cpus`.

---

### 2. Інтерфейси керування пам'яттю NUMA (`libnuma` та системні виклики)

Інтерфейси дозволяють локалізувати структури даних шарду строго на тому сокеті або вузлі, де виконується закріплений потік. Це запобігає трансляції звернень до пам'яті через повільні міжпроцесорні шини зв'язку.

Виклик `numa_alloc_onnode()` безпосередньо звертається до ядра через системний виклик `mbind()` з політикою `MPOL_BIND`. Пам'ять виділяється сторінками фіксованого розміру (4 КБ або величезними сторінками HugePages 2 МБ / 1 ГБ).

На рівні ядра Linux сторінковий алокатор (*Buddy Allocator*) підтримує окремі списки вільних зон (*zonelists*) для кожного NUMA-вузла (`ZONE_NORMAL`, `ZONE_DMA32`). Використання політики `MPOL_BIND` гарантує, що сторінки фізичної оперативної пам'яті будуть виділені контролером пам'яті локального сокета, усуваючи затримки доступу через міжсокетну шину зв'язку.

:::tabs
```c
#include <numa.h>
#include <numaif.h>

/* Виділення блоку пам'яті строго на вказаному NUMA-вузлі */
void *numa_alloc_onnode(size_t size, int node);

/* Звільнення пам'яті, виділеної через numa_alloc_* */
void numa_free(void *start, size_t size);

/* Отримання індексу NUMA-вузла для вказаного ядра CPU */
int numa_node_of_cpu(int cpu);

/* Встановлення бажаного вузла виділення пам'яті для поточного потоку */
void numa_set_preferred(int node);

/* Системний виклик mbind для прив'язки діапазону віртуальних адрес */
long mbind(void *addr, unsigned long len, int mode,
           const unsigned long *nodemask, unsigned long maxnode, unsigned flags);
```
```cpp
#include <memory>
#include <new>
#include <numa.h>
#include <numaif.h>

namespace tpc {

/* Шаблонний C++ алокатор пам'яті для конкретного NUMA-вузла */
template <typename T>
struct NumaAllocator {
    using value_type = T;
    int target_node{0};

    explicit NumaAllocator(int node) noexcept : target_node(node) {}

    template <typename U>
    NumaAllocator(const NumaAllocator<U>& other) noexcept : target_node(other.target_node) {}

    T* allocate(std::size_t n) {
        void* ptr = numa_alloc_onnode(n * sizeof(T), target_node);
        if (!ptr) {
            throw std::bad_alloc();
        }
        return static_cast<T*>(ptr);
    }

    void deallocate(T* p, std::size_t n) noexcept {
        numa_free(p, n * sizeof(T));
    }
};

} // namespace tpc
```
:::

#### Політики виділення пам'яті (`mode`)
| Політика | Значення | Опис поведінки алокатора |
|---|---|---|
| `MPOL_BIND` | `1` | Суворе виділення пам'яті виключно на вузлах із `nodemask`. Якщо пам'ять вузла вичерпано — повертає `ENOMEM` без виходу на сусідні сокети |
| `MPOL_PREFERRED` | `2` | Пріоритетне виділення на зазначеному вузлі з автоматичним виділенням на сусідніх сокетах при переповненні |
| `MPOL_INTERLEAVE` | `3` | Посторінкове чергування виділення пам'яті (round-robin) між усіма доступними NUMA-вузлами |

При вичерпанні пам'яті на локальному вузлі поведінка системи залежить від обраної політики: `MPOL_BIND` гарантує ізоляцію затримки, відмовляючи у виділенні, тоді як `MPOL_PREFERRED` дозволяє уникнути аварійного завершення ціною тимчасового збільшення затримок доступу до даних. Для великорозмірних таблиць рекомендується підключати сторінки HugePages через `madvise()` із прапорцем `MADV_HUGEPAGE`.

---

### 3. Сокетні параметри маршрутизації вхідного трафіку

Прапорці налаштування файлових дескрипторів TCP-сокетів для паралельного розподілу вхідних мережевих сесій між ядрами без конкуренції за глобальний слухаючий сокет.

Коли кілька потоків викликають `bind()` на однаковий порт із прапорцем `SO_REUSEPORT`, ядро створює масив слухаючих сокетів. Під час надходження нового клієнтського TCP-пакета `SYN`, ядро обчислює хеш і передає з'єднання у чергу конкретного сокета, усуваючи проблему «пробудження стада» (*thundering herd problem*).

Прапорець `SO_INCOMING_CPU` дозволяє явно вказати ядру операційної системи номер бажаного процесора для обробки мережевого потоку, оптимізуючи шлях пакета від драйвера мережевої карти до буфера сокета в просторі користувача.

:::tabs
```c
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

/* Налаштування сокета для Thread-per-core */
int configure_tpc_socket(int fd, int cpu_id) {
    int opt = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt)) < 0) {
        return -1;
    }
    if (setsockopt(fd, SOL_SOCKET, SO_INCOMING_CPU, &cpu_id, sizeof(cpu_id)) < 0) {
        return -1;
    }
    int nodelay = 1;
    if (setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &nodelay, sizeof(nodelay)) < 0) {
        return -1;
    }
    return 0;
}
```
```cpp
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <system_error>

namespace tpc {

/* C++ функція налаштування сокета шарду */
inline void configure_tpc_socket(int fd, int cpu_id) {
    int opt = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt)) < 0) {
        throw std::system_error(errno, std::generic_category(), "SO_REUSEPORT failed");
    }
    if (setsockopt(fd, SOL_SOCKET, SO_INCOMING_CPU, &cpu_id, sizeof(cpu_id)) < 0) {
        throw std::system_error(errno, std::generic_category(), "SO_INCOMING_CPU failed");
    }
    int nodelay = 1;
    if (setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &nodelay, sizeof(nodelay)) < 0) {
        throw std::system_error(errno, std::generic_category(), "TCP_NODELAY failed");
    }
}

} // namespace tpc
```
:::

#### Прапорці виклику `setsockopt(fd, SOL_SOCKET, optname, ...)`

| Назва опції | Тип аргументу | Опис функціоналу |
|---|---|---|
| `SO_REUSEPORT` | `int (0/1)` | Дозволяє кільком сокетам (на різних ядрах) відкривати однаковий порт `IP:Port`. Ядро розподіляє з'єднання |
| `SO_INCOMING_CPU` | `int (cpu_id)` | Підказує ядру приймати з'єднання лише на сокеті, закріпленому за ядром `cpu_id` |
| `SO_ATTACH_REUSEPORT_EBPF` | `int (bpf_fd)` | Підключає скомпільовану програму eBPF для вибору цільового сокета за власним хешем бізнес-даних |
| `TCP_NODELAY` | `int (0/1)` | Вимикає алгоритм Нейгла, відправляючи TCP-пакети негайно без буферизації |

Для систем із гранично високими вимогами до затримок додатково налаштовують параметри опитування сокетів у ядрі через `/proc/sys/net/core/busy_read` та `busy_poll`, що змушує ядро опитувати мережеву карту в активному циклі, усуваючи затримки апаратних переривань.

---

### 4. Конфігураційні прапорці підсистеми `io_uring` для Thread-per-core

Структури та параметри ініціалізації неблокувального введення-виведення без системних викликів.

Підсистема `io_uring` проектувалася з урахуванням багатоядерної архітектури. Прапорець `IORING_SETUP_SQPOLL` активує режим, у якому ядро виділяє окремий потік ядра для опитування черги SQ. Поєднуючи цей прапорець із `IORING_SETUP_SQ_AFFINITY`, застосунок гарантує, що потік ядра виконуватиметься на тому самому фізичному ядрі або NUMA-вузлі, що й потік користувача, максимізуючи локальність кешу L1/L2.

Додатково застосунок може попередньо зареєструвати файлові дескриптори та буфери пам'яті через функцію `io_uring_register()`. Це усуває атомарні операції підрахунку посилань на файли в ядрі та операції прив'язки віртуальних сторінок під час кожного читання та запису.

:::tabs
```c
#include <liburing.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Ініціалізація екземпляра io_uring для потоку ядра */
int init_tpc_ring(struct io_uring *ring, unsigned entries, int cpu_id) {
    struct io_uring_params params;
    memset(&params, 0, sizeof(params));
    params.flags = IORING_SETUP_SQPOLL | IORING_SETUP_SQ_AFFINITY;
    params.sq_thread_cpu = cpu_id;
    params.sq_thread_idle = 2000; /* Час очікування ядра в мілісекундах */

    return io_uring_queue_init_params(entries, ring, &params);
}
```
```cpp
#include <liburing.h>
#include <system_error>
#include <cstring>

namespace tpc {

/* RAII обгортка над екземпляром io_uring для потоку ядра */
class ScopedIoUring {
public:
    ScopedIoUring(unsigned entries, int cpu_affinity) {
        io_uring_params params{};
        params.flags = IORING_SETUP_SQPOLL | IORING_SETUP_SQ_AFFINITY;
        params.sq_thread_cpu = static_cast<uint32_t>(cpu_affinity);
        params.sq_thread_idle = 2000; // 2 секунди очікування ядра

        const int rc = io_uring_queue_init_params(entries, &ring_, &params);
        if (rc < 0) {
            throw std::system_error(-rc, std::generic_category(), "Помилка ініціалізації io_uring");
        }
    }

    ~ScopedIoUring() noexcept {
        io_uring_queue_exit(&ring_);
    }

    ScopedIoUring(const ScopedIoUring&) = delete;
    ScopedIoUring& operator=(const ScopedIoUring&) = delete;

    struct io_uring* get() noexcept { return &ring_; }

private:
    struct io_uring ring_{};
};

} // namespace tpc
```
:::

#### Ключові прапорці режиму Thread-per-core (`flags`)
- `IORING_SETUP_SQPOLL` — створює потік опитування черги подання в ядрі. Застосунок додає завдання в SQ-кільце без виклику системної функції `io_uring_enter()`.
- `IORING_SETUP_SQ_AFFINITY` — жорстко прив'язує потік опитування ядра до конкретного фізичного ядра CPU, вказаного в полі `sq_thread_cpu`.
- `IORING_SETUP_COOP_TASKRUN` — оптимізує виконання завдань ядра, мінімізуючи міжпроцесорні переривання (IPI).

Завдяки правильній конфігурації цих параметрів підсистема `io_uring` перетворюється на швидкий неблокувальний конвеєр, що дозволяє одному ядру виконувати сотні тисяч дискових та мережевих операцій за секунду з мінімальною затримкою.
