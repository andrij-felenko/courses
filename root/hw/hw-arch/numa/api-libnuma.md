# 📋 Довідник libnuma, системних викликів та утиліт ядра Linux

Керування пам'яттю та плануванням процесів у неоднорідних системах (NUMA) в операційній системі Linux реалізовано на трьох рівнях:
1. **Системні виклики ядра (Linux Syscalls)**: базовий низькорівневий інтерфейс ядра (`mbind`, `set_mempolicy`, `move_pages` тощо).
2. **Користувацька бібліотека `libnuma` (`<numa.h>`, `<numaif.h>`)**: зручна C/C++ обгортка для динамічного виділення пам'яті, маніпулювання бітовими масками вузлів та прив'язки потоків.
3. **Утиліти командного рядка та файлова система `sysfs`**: інструменти діагностики, моніторингу та конфігурації оточення (`numactl`, `numastat`, `/sys/devices/system/node/`).

---

### 1. Системні виклики ядра Linux для керування NUMA

Системні виклики ядра є первинним інтерфейсом, через який простір користувача взаємодіє з підсистемою керування пам'яттю (англ. *Virtual Memory Subsystem*). Усі високорівневі бібліотеки (зокрема `libnuma`, алокатори `jemalloc` чи `TCMalloc`) є лише тонкими обгортками над цими викликами.

Усі системні виклики оголошено в заголовному файлі `<numaif.h>`. Їхнє виконання супроводжується переходом у простір ядра через інструкцію `syscall`, перевіркою прав доступу процесу та оновленням дескрипторів віртуальних областей пам'яті `struct vm_area_struct` (VMA).

#### `mbind()` — прив'язка діапазону віртуальних адрес до вузлів

Системний виклик `mbind()` модифікує політику розміщення пам'яті для конкретного, уже виділеного діапазону віртуальних адрес процесу.

:::tabs
```c
long mbind(void *addr, unsigned long len, int mode,
           const unsigned long *nodemask, unsigned long maxnode,
           unsigned flags);
```
```cpp
#include <sys/mman.h>
#include <numaif.h>
#include <span>
#include <expected>
#include <system_error>

std::expected<void, std::error_code> bind_memory_range(
    std::span<std::byte> range, int mode, unsigned long nodemask, unsigned flags = 0) noexcept;
```
:::

**Внутрішній механізм виконання в ядрі:**
1. Ядро перевіряє вирівнювання: початкова адреса `addr` мусить бути кратною базовому розміру сторінки архітектури (`PAGE_SIZE = 4096` байтів). Довжина `len` автоматично округлюється вгору до найближчої межі сторінки.
2. Підсистема VMA знаходить усі структури `vm_area_struct`, що перетинаються з інтервалом `[addr, addr + len)`.
3. Якщо діапазон частково накладається на наявну VMA, ядро розрізає її (англ. *VMA split*) на кілька незалежних областей і призначає цільовому відрізку нову структуру політики `struct mempolicy`.
4. Якщо встановлено прапорці міграції (`MPOL_MF_MOVE`), ядро ініціює асинхронне або синхронне перенесення фізичних сторінок: сторінки тимчасово блокуються (виставляється біт `PG_locked`), видаляються з таблиць сторінок процесу, копіюються контролером пам'яті на новий вузол і повертаються в таблицю сторінок з новими фізичними адресами.

**Параметри виклику:**
- **`addr`**: початкова адреса віртуального діапазону пам'яті.
- **`len`**: довжина діапазону в байтах.
- **`mode`**: числове значення політики (`MPOL_DEFAULT`, `MPOL_BIND`, `MPOL_INTERLEAVE`, `MPOL_PREFERRED`, `MPOL_LOCAL`, `MPOL_PREFERRED_MANY`). Також може містити допоміжні прапорці режиму (наприклад, `MPOL_F_STATIC_NODES` або `MPOL_F_RELATIVE_NODES`).
- **`nodemask`**: покажчик на бітовий масив, де кожен біт відповідає номеру NUMA-вузла (біт 0 = Вузол 0, біт 1 = Вузол 1 тощо).
- **`maxnode`**: кількість бітів у переданому масиві `nodemask` плюс один.
- **`flags`**: керування міграцією та строгістю перевірки:
  - `0`: відкладена дія (англ. *lazy allocation*). Політика застосовується лише до тих сторінок у діапазоні, які ще не мають фізичного відображення (будуть виділені під час майбутніх Page Fault).
  - `MPOL_MF_STRICT`: ядро сканує вже виділені сторінки діапазону. Якщо хоча б одна сторінка розташована на вузлі, не включеному в `nodemask`, виклик негайно завершується з помилкою `-EIO`.
  - `MPOL_MF_MOVE`: ядро намагається перемістити всі фізичні сторінки діапазону, що порушують нову політику, на вказані вузли. Переміщуються лише ті сторінки, які монопольно належать поточному процесу (анонімна пам'ять із лічильником посилань `mapcount == 1`).
  - `MPOL_MF_MOVE_ALL`: примусово переміщує навіть спільні сторінки (англ. *shared pages*), що використовуються іншими процесами. Ця операція є потенційно деструктивною для сторонніх потоків, тому вимагає системних привілеїв суперкористувача `CAP_SYS_NICE`.

**Детальний аналіз кодів помилок `errno` для `mbind()`:**

| Код помилки | Внутрішня причина виникнення |
| :--- | :--- |
| **`EINVAL`** | Неприпустимий режим `mode` або невідомі прапорці `flags`. Також виникає, якщо адреса `addr` не вирівняна за межею 4 КБ, або якщо параметр `len + addr` призводить до переповнення адресного простору. |
| **`EFAULT`** | Вказаний діапазон адрес або покажчик `nodemask` вказує на неприпустиму пам'ять поза адресним простором процесу. |
| **`ENOMEM`** | Недостатньо пам'яті ядра під час виділення дескрипторів VMA, або цільовий NUMA-вузол не має вільної фізичної пам'яті для завершення міграції при прапорці `MPOL_MF_STRICT`. |
| **`EIO`** | Передано прапорець `MPOL_MF_STRICT`, і ядро виявило, що частина сторінок розташована на заборонених вузлах і не може бути переміщена. |
| **`EPERM`** | Процес спробував використати прапорець `MPOL_MF_MOVE_ALL` без наявності привілею `CAP_SYS_NICE`. |
| **`EBUSY`** | Сторінки заблоковані операціями прямого доступу до пам'яті (DMA) або вводу-виводу і не можуть бути тимчасово переміщені. |

#### `set_mempolicy()` — глобальна політика поточного потоку

Встановлює політику за замовчуванням для поточного потоку виконання. Усі наступні операції виділення динамічної пам'яті (через `brk()`, `sbrk()` або анонімний `mmap()`) будуть автоматично наслідувати цю політику.

:::tabs
```c
long set_mempolicy(int mode, const unsigned long *nodemask,
                   unsigned long maxnode);
```
```cpp
#include <numaif.h>
#include <expected>
#include <system_error>

std::expected<void, std::error_code> apply_thread_mempolicy(
    int mode, unsigned long nodemask) noexcept;
```
:::

Якщо для окремого діапазону пам'яті пізніше буде викликано `mbind()`, локальна політика діапазону матиме пріоритет над глобальною політикою `set_mempolicy()`.

**Коди помилок:**
- `EINVAL`: невідомий режим або некоректна маска `nodemask`.
- `EFAULT`: покажчик `nodemask` вказує на недоступну адресу.
- `ENODEV`: жоден із вузлів у `nodemask` не містить фізичної пам'яті чи не доступний онлайн.

#### `get_mempolicy()` — інтроспекція стану пам'яті

Дозволяє визначити діючу політику процесу або дізнатися номер фізичного NUMA-вузла, на якому розміщена конкретна віртуальна адреса.

:::tabs
```c
long get_mempolicy(int *mode, unsigned long *nodemask,
                   unsigned long maxnode, void *addr,
                   unsigned long flags);
```
```cpp
#include <numaif.h>
#include <expected>
#include <system_error>

struct MemoryPolicyInfo {
    int mode{0};
    unsigned long nodemask{0};
};

std::expected<MemoryPolicyInfo, std::error_code> query_address_policy(
    const void* addr, unsigned long flags = 0) noexcept;
```
:::

**Прапорці інтроспекції:**
- `0`: повертає глобальну числову політику `mode` та маску `nodemask` для поточного потоку.
- `MPOL_F_ADDR`: досліджує конкретну адресу `addr`. Якщо передано `MPOL_F_NODE`, змінна `mode` отримує числовий номер фізичного NUMA-вузла, на якому виділена відповідна сторінка.
- `MPOL_F_MEMS_ALLOWED`: записує в `nodemask` бітову маску всіх вузлів, виділення на яких дозволено поточному контексту процесу (з урахуванням обмежень cgroups cpuset).

#### `move_pages()` — адресне переміщення сторінок

Системний виклик для точкового перенесення довільного переліку сторінок на різні вузли за один виклик ядра.

:::tabs
```c
long move_pages(int pid, unsigned long count, void **pages,
                const int *nodes, int *status, int flags);
```
```cpp
#include <numaif.h>
#include <span>
#include <vector>
#include <expected>
#include <system_error>

std::expected<std::vector<int>, std::error_code> migrate_page_span(
    int pid, std::span<void*> pages, std::span<const int> target_nodes, int flags);
```
:::

- **`pid`**: ідентифікатор цільового процесу (`0` — поточний процес). Для перенесення сторінок іншого процесу потрібні права `CAP_SYS_NICE` та збіг реального UID.
- **`count`**: розмір масиву сторінок.
- **`pages`**: масив покажчиків на віртуальні адреси сторінок (кожна адреса повинна вказувати на початок сторінки).
- **`nodes`**: масив цільових вузлів для кожної відповідної сторінки. Якщо передано `NULL`, ядро не переміщує сторінки, а лише записує їхній поточний фізичний стан у масив `status`.
- **`status`**: вихідний масив результатів розміром `count`. Для кожної сторінки ядро записує або номер вузла, де вона опинилася, або від'ємний код помилки:
  - `-EACCES`: сторінка відображена лише для читання або належить ядру.
  - `-EBUSY`: сторінка заблокована іншим процесом чи контролером введення-виведення.
  - `-EFAULT`: адреса не відображена у віртуальному просторі процесу.
  - `-ENOENT`: сторінки фізично не існує (ще не відбувся перший дотик).
  - `-ENOMEM`: на цільовому вузлі вичерпано вільну фізичну пам'ять.

#### `migrate_pages()` — масове перенесення процесу

Здійснює масове переміщення всієї пам'яті процесу з однієї групи вузлів на іншу.

:::tabs
```c
long migrate_pages(int pid, unsigned long maxnode,
                  const unsigned long *old_nodes,
                  const unsigned long *new_nodes);
```
```cpp
#include <numaif.h>
#include <expected>
#include <system_error>

std::expected<void, std::error_code> migrate_process_nodes(
    int pid, unsigned long old_nodes_mask, unsigned long new_nodes_mask) noexcept;
```
:::

Цей виклик є основою для роботи системних демонів міграції контейнерів та оркестраторів ресурсів при перерозподілі пам'яті між NUMA-доменами без перезапуску застосунку.

### 2. Апаратні таблиці ACPI: SRAT та SLIT

Під час завантаження комп'ютера прошивка материнської плати (UEFI/BIOS) опитує контролери процесорів і формує системні таблиці ACPI, які передаються ядру Linux:

#### SRAT (System Resource Affinity Table)
Таблиця описує прив'язку апаратних компонентів до просторових доменів (англ. *Proximity Domains*), які в ОС стають NUMA-вузлами. Вона складається зі структур трьох типів:
1. **Processor Local APIC/x2APIC Affinity Structure**: пов'язує апаратний ідентифікатор процесора (APIC ID) із номером NUMA-домену (`Proximity Domain`).
2. **Memory Affinity Structure**: задає діапазони фізичних базових адрес пам'яті (`Base Address`), їхню довжину (`Length`) та прапорці придатності (`Hot-Pluggable`, `Non-Volatile`).
3. **Generic Initiator Affinity Structure**: реєструє прискорювачі без власних ядер (GPU, FPGA, CXL-пристрої) та вказує їхній найближчий вузол пам'яті.

#### Режими конфігурації BIOS: Sub-NUMA Clustering (SNC) та NPS
Сучасні серверні процесори (AMD EPYC, Intel Xeon Scalable) дозволяють у BIOS штучно розділяти один фізичний сокет на кілька віртуальних NUMA-вузлів:
- **AMD NPS (NUMA Nodes Per Socket)**:
  - `NPS1`: один вузол на весь сокет (усі 8 каналів пам'яті чергуються разом, затримка усереднена).
  - `NPS2`: сокет ділиться на 2 вузли по 4 канали пам'яті.
  - `NPS4`: кожен кристал CCD або пара чиплетів прив'язується до власних 2 каналів пам'яті, створюючи 4 NUMA-вузли на сокет (мінімальна затримка до найближчого контролера).
- **Intel SNC (Sub-NUMA Clustering)**:
  - `SNC2` / `SNC4`: поділ сокета на 2 або 4 кластери з локалізацією L3-кешу та найближчих каналів пам'яті.

Коли ввімкнено режим NPS4 на 2-сокетному сервері, операційна система Linux бачить не 2, а **8 незалежних NUMA-вузлів** (`numactl -H`), що вимагає ретельного планування потоків.

#### SLIT (System Locality Distance Information Table)
Таблиця містить двовимірну матрицю відносних затримок доступу розміром `N × N` (де `N` — кількість вузлів). Значення є безрозмірними коефіцієнтами:
- Діагональні елементи завжди дорівнюють `10` (базова відносна затримка локальної пам'яті).
- Прямий лінк між двома сусідніми сокетами зазвичай кодується числом `21` (означає, що затримка приблизно в 2.1 раза вища за локальну).
- Транзитний перехід через проміжний сокет кодується числом `31` (~3.1×).

Ядро Linux читає таблицю SLIT під час ініціалізації (`drivers/acpi/numa/srat.c`) і зберігає значення у внутрішньому масиві ядра `node_distance(from, to)`.

---

### 3. Структури даних простору ядра: анатомія `pg_data_t`

У вихідному коді ядра Linux кожен NUMA-вузол описується структурою `typedef struct pglist_data pg_data_t` (визначеною в `<linux/mmzone.h>`). Доступ до дескриптора конкретного вузла здійснюється через макрос `NODE_DATA(node_id)`.

Ключові поля структури `pg_data_t`:

:::tabs
```c
typedef struct pglist_data {
    struct zone node_zones[MAX_NR_ZONES];       // масив зон пам'яті (DMA, DMA32, Normal, Movable)
    struct zonelist node_zonelists[MAX_ZONELISTS]; // списки зон для пошуку вільної пам'яті при дефіциті
    int nr_zones;                               // кількість активних зон на цьому вузлі
    
    struct page *node_mem_map;                  // масив дескрипторів фізичних сторінок (struct page)
    unsigned long node_start_pfn;               // перший номер фізичного фрейму сторінки (Page Frame Number)
    unsigned long node_present_pages;           // реальна кількість присутніх сторінок
    unsigned long node_spanned_pages;           // загальний діапазон сторінок включно з дірками
    int node_id;                                // числовий номер NUMA-вузла (0, 1, ...)
    
    wait_queue_head_t kswapd_wait;              // черга очікування для фонового демона вивільнення kswapd
    struct task_struct *kswapd;                 // покажчик на потік ядра kswapd для даного вузла
    
    unsigned long min_unmapped_pages;           // поріг невідображених сторінок для zone_reclaim
    unsigned long min_slab_pages;               // поріг кешів SLAB для zone_reclaim
    
    CACHELINE_PADDING(_pad1_);
    spinlock_t lru_lock;                        // спінлок списків активних/неактивних сторінок (LRU)
    struct lruvec __lruvec;                     // списки сторінок LRU для алгоритмів заміщення
} pg_data_t;
```
```cpp
// Концептуальне відображення стану зон вузла в C++
#include <vector>
#include <string>
#include <cstdint>

struct NumaZoneDescriptor {
    std::string zone_name;
    std::uint64_t free_pages{0};
    std::uint64_t watermark_min{0};
    std::uint64_t watermark_low{0};
    std::uint64_t watermark_high{0};
};
```
:::

Кожен вузол має **повністю незалежні екземпляри зон та списків бадді-алокатора**. Це означає, що коли ядро виділяє сторінку на Вузлі 0, воно захоплює локальний спінлок `free_area` Вузла 0 і взагалі не контактує з пам'яттю Вузла 1, усуваючи будь-який міжпроцесорний контеншн на рівні системного алокатора сторінок.

| Політика | Числовий код | Опис механізму | Типове застосування |
| :--- | :--- | :--- | :--- |
| **`MPOL_DEFAULT`** | `0` | Виділення пам'яті на локальному вузлі ядра, що викликало Page Fault. Якщо пам'ять вичерпано — плавний перехід (fallback) на найближчі вузли. | За замовчуванням для всіх процесів Linux. |
| **`MPOL_BIND`** | `1` | Жорстке виділення пам'яті **виключно** на вузлах із переданої бітової маски. Якщо на них немає вільної пам'яті, процес отримує помилку OOM (або зависає в реклеймі). | Високопродуктивні сервіси, бази даних із жорсткою ізоляцією ресурсів. |
| **`MPOL_INTERLEAVE`**| `2` | Посторінкове чергування (Round-Robin) сторінок розміром 4 КБ між вузлами з маски: сторінка 0 → Node 0, сторінка 1 → Node 1 тощо. | Спільні буфери для багатьох потоків (shared memory PostgreSQL, великі масиви MPI). |
| **`MPOL_PREFERRED`** | `3` | Пам'ять намагається виділитися на одному вказаному вузлі. Якщо на ньому виникає дефіцит — ядро прозоро виділяє пам'ять на сусідніх вузлах без помилок. | Однопотокові сервіси, яким бажано жити на одному сокеті. |
| **`MPOL_LOCAL`** | `4` | Явна вимога локальності: пам'ять виділяється на вузлі того ядра, де виконується потік під час алокації (навіть якщо політика батьківського процесу була іншою). | Потоки в пулах задач із жорсткою процесорною прив'язкою. |
| **`MPOL_PREFERRED_MANY`**| `5` | Розширення `MPOL_PREFERRED` для множини вузлів (з'явилося в ядрі Linux 5.15). Дозволяє вказати список пріоритетних сокетів. | Багаточиплетні системи з кількома внутрішніми доменами. |

---

### 3. Бібліотека `libnuma`: високорівневий C/C++ API

Бібліотека `libnuma` надає зручні функції для повсякденної роботи з неоднорідною пам'яттю без ручного формування бітових масок через двійкові зсуви.

#### Перевірка середовища та топології

:::tabs
```c
// Перевірка підтримки NUMA (повертає -1, якщо вимкнено або не підтримується)
int numa_available(void);

// Максимальний номер NUMA-вузла в системі (наприклад, 1 для двосокетного сервера)
int numa_max_node(void);

// Кількість налаштованих та доступних вузлів
int numa_num_configured_nodes(void);

// Кількість наявних процесорних ядер у системі
int numa_num_configured_cpus(void);

// Отримання розміру пам'яті вузла та обсягу вільної пам'яті
long long numa_node_size64(int node, long long *freep);

// Відносна дистанція між двома вузлами за таблицею SLIT (10 = локально, 21 = сусід)
int numa_distance(int node1, int node2);
```
```cpp
#include <numa.h>
#include <stdexcept>
#include <format>
#include <utility>

class NumaTopologyInspector {
public:
    static bool is_supported() noexcept { return numa_available() >= 0; }
    static int get_max_node() noexcept { return numa_max_node(); }
    static int get_configured_nodes() noexcept { return numa_num_configured_nodes(); }
    static int get_configured_cpus() noexcept { return numa_num_configured_cpus(); }
    static int get_node_distance(int from, int to) noexcept { return numa_distance(from, to); }
};
```
:::

#### Виділення та звільнення пам'яті

:::tabs
```c
// Виділити пам'ять на конкретному вузлі
void* numa_alloc_onnode(size_t size, int node);

// Виділити пам'ять на локальному вузлі поточного потоку
void* numa_alloc_local(size_t size);

// Виділити пам'ять із посторінковим чергуванням між усіма вузлами
void* numa_alloc_interleaved(size_t size);

// Виділити пам'ять із чергуванням за заданою маскою вузлів
void* numa_alloc_interleaved_subset(size_t size, struct bitmask *nodemask);

// Звільнити пам'ять, виділену функціями numa_alloc_*
void numa_free(void *start, size_t size);
```
```cpp
#include <numa.h>
#include <span>
#include <memory>
#include <stdexcept>

template <typename T>
class NumaScopedBlock {
public:
    NumaScopedBlock(std::size_t count, int node) : count_(count), bytes_(count * sizeof(T)) {
        ptr_ = static_cast<T*>(numa_alloc_onnode(bytes_, node));
        if (!ptr_) throw std::bad_alloc();
    }
    ~NumaScopedBlock() noexcept {
        if (ptr_) numa_free(ptr_, bytes_);
    }
    [[nodiscard]] std::span<T> span() noexcept { return {ptr_, count_}; }
private:
    T* ptr_{nullptr};
    std::size_t count_{0};
    std::size_t bytes_{0};
};
```
:::

#### Керування прив'язкою потоків і процесів

:::tabs
```c
// Прив'язати виконання поточного процесу/потоку до ядер вказаного вузла
int numa_run_on_node(int node);

// Прив'язати виконання до маски ядер
int numa_run_on_node_mask(struct bitmask *nodemask);

// Встановити жорстку прив'язку виконання і пам'яті (CPU + Memory Bind)
void numa_bind(struct bitmask *nodemask);

// Встановити бажаний вузол для виділення пам'яті
void numa_set_preferred(int node);

// Встановити маску для чергування сторінок у поточному потоці
void numa_set_interleave_mask(struct bitmask *nodemask);
```
```cpp
#include <numa.h>
#include <stdexcept>
#include <format>

class NumaThreadAffinityManager {
public:
    static void bind_current_thread_to_node(int node) {
        if (numa_run_on_node(node) != 0) {
            throw std::runtime_error(std::format("Не вдалося прив'язати потік до вузла {}", node));
        }
    }
    static void set_preferred_memory_node(int node) noexcept {
        numa_set_preferred(node);
    }
};
```
:::

#### Робота зі структурою `struct bitmask`

Бібліотека `libnuma` використовує динамічну структуру `bitmask` для представлення множин процесорів і вузлів будь-якого розміру:

:::tabs
```c
#include <numa.h>
#include <stdio.h>

void configure_nodes(void) {
    // Виділення бітової маски під усі можливі вузли системи
    struct bitmask *nodes = numa_allocate_nodemask();

    // Очищення маски
    numa_bitmask_clearall(nodes);

    // Встановлення бітів для Вузла 0 та Вузла 2
    numa_bitmask_setbit(nodes, 0);
    numa_bitmask_setbit(nodes, 2);

    if (numa_bitmask_isbitset(nodes, 0)) {
        printf("Node 0 обрано для виділення пам'яті\n");
    }

    // Звільнення пам'яті дескриптора маски
    numa_bitmask_free(nodes);
}
```
```cpp
#include <numa.h>
#include <iostream>
#include <memory>
#include <stdexcept>

// Безпечна RAII-обгортка для struct bitmask
struct BitmaskDeleter {
    void operator()(bitmask* bm) const noexcept {
        if (bm) numa_bitmask_free(bm);
    }
};
using ScopedBitmask = std::unique_ptr<bitmask, BitmaskDeleter>;

ScopedBitmask make_scoped_nodemask() {
    bitmask* bm = numa_allocate_nodemask();
    if (!bm) throw std::bad_alloc();
    return ScopedBitmask(bm);
}

void configure_nodes_cpp() {
    auto nodes = make_scoped_nodemask();
    numa_bitmask_clearall(nodes.get());
    numa_bitmask_setbit(nodes.get(), 0);
    numa_bitmask_setbit(nodes.get(), 2);

    if (numa_bitmask_isbitset(nodes.get(), 0)) {
        std::cout << "Node 0 обрано для виділення пам'яті\n";
    }
}
```
:::

---

### 4. Утиліти командного рядка для адміністрування NUMA

#### Утиліта `numactl`

Головний системний інструмент запуску процесів із попередньо налаштованими політиками прив'язки.

```bash
# 1. Виведення апаратної топології системи: кількість вузлів, ядер, обсяг пам'яті та таблиця SLIT
numactl --hardware
# або скорочено:
numactl -H

# 2. Виведення поточної політики NUMA для активного сеансу shell
numactl --show

# 3. Запуск процесу з прив'язкою до ядер та пам'яті Вузла 0 (повна локалізація)
numactl --cpunodebind=0 --membind=0 ./my_server_node0

# 4. Запуск процесу з прив'язкою до конкретних фізичних ядер (наприклад, ядра 0-15)
numactl --physcpubind=0-15 --membind=0 ./compute_task

# 5. Запуск процесу з посторінковим чергуванням між усіма доступними вузлами
numactl --interleave=all ./postgres -D /data/pg_db

# 6. Запуск процесу з бажаним виділенням на Вузлі 1 (з можливістю fallback)
numactl --preferred=1 ./worker_app
```

#### Прапорці утиліти `numactl`:

- `--hardware`, `-H`: показати топологію NUMA-вузлів.
- `--show`, `-s`: показати діючі політики пам'яті.
- `--interleave=nodes`, `-i nodes`: посторінкове чергування пам'яті.
- `--membind=nodes`, `-m nodes`: жорстке виділення пам'яті лише на вказаних вузлах.
- `--cpunodebind=nodes`, `-N nodes`: виконання лише на процесорах вказаних вузлів.
- `--physcpubind=cpus`, `-C cpus`: виконання лише на конкретних процесорних ядрах (CPU IDs).
- `--preferred=node`, `-p node`: бажаний вузол для виділення пам'яті.
- `--localalloc`, `-l`: завжди виділяти пам'ять на поточному вузлі.

#### Утиліта `numastat`

Виводить статистику звернень до пам'яті для кожного вузла системи.

```bash
# Перегляд загальної системної статистики
numastat

# Перегляд статистики пам'яті у зручному форматі (МБ) за вузлами
numastat -m

# Перегляд розподілу пам'яті конкретного процесу за його PID
numastat -p 12345

# Неперервний моніторинг із періодом оновлення 1 секунда
watch -n 1 numastat -c
```

---

### 5. Семантика системних лічильників пам'яті (`numastat`)

Коли ви запускаєте `numastat`, утиліта зчитує лічильники з файлу `/sys/devices/system/node/node*/numastat`:

| Метрика | Значення та діагностичний сенс |
| :--- | :--- |
| **`numa_hit`** | Кількість сторінок, які процес успішно виділив на тому вузлі, де виконувався потік під час виникнення Page Fault. Що вище значення відносно інших, то краща локальність. |
| **`numa_miss`** | Кількість сторінок, які потік хотів виділити на певному вузлі (наприклад, через політику preferred), але через дефіцит вільної пам'яті ядро виділило їх на іншому вузлі. Ознака вичерпання локальної пам'яті. |
| **`numa_foreign`** | Дзеркало для `numa_miss`. Показує кількість сторінок, виділених на цьому вузлі для потоків, які спочатку хотіли виділити пам'ять на іншому вузлі. |
| **`interleave_hit`** | Кількість сторінок, які успішно виділено за черговою схемою політики `MPOL_INTERLEAVE`. |
| **`local_node`** | Кількість сторінок, успішно виділених процесом, що фізично виконувався на процесорному ядрі цього вузла. |
| **`other_node`** | Кількість сторінок, виділених на цьому вузлі для процесу, що в цей момент виконувався на ядрі **іншого** сокета. Високе значення — прямий індикатор NUMA-неоднорідності та міжвузлового трафіку. |

---

### 6. Налаштування параметрів ядра через `sysctl`

Поведінка ядра щодо управління сторінками в неоднорідних системах налаштовується через псевдофайлову систему `/proc/sys/`:

#### `vm.zone_reclaim_mode` — режим агресивного локального вивільнення

Визначає, як поводиться ядро, коли на локальному вузлі закінчується вільна пам'ять:

- `0` (**Рекомендовано для серверів баз даних**): вимкнено. Якщо на локальному вузлі бракує пам'яті, ядро виділяє сторінку на сусідньому віддаленому вузлі, де є вільне місце.
- `1`: ядро намагається агресивно вивільнити локальний кеш сторінок (Page Cache) та брудні сторінки, перш ніж звертатися до віддаленої пам'яті. Спричиняє гігантські затримки та NUMA Thrashing у базах даних!
- `2`: записувати брудні сторінки на диск під час реклейму.
- `4`: скидати сторінки swap під час локального реклейму.

```bash
# Перевірка поточного значення
sysctl vm.zone_reclaim_mode

# Вимкнення небезпечного локального реклейму
sudo sysctl -w vm.zone_reclaim_mode=0
```

#### `kernel.numa_balancing` — автоматичне балансування сторінок ядра (AutoNUMA)

- `0`: вимкнено. Сторінки залишаються на тих вузлах, де їх вперше виділили.
- `1`: увімкнено. Ядро сканує адресні простори процесів, помічає сторінки як `PROT_NONE` і за перехопленням NUMA-hint faults переміщує сторінки ближче до активних потоків.

```bash
# Увімкнення / вимкнення AutoNUMA
sudo sysctl -w kernel.numa_balancing=1

# Періодичність сканування адресного простору процесу (мс)
sudo sysctl -w kernel.numa_balancing_scan_period_min_ms=1000
sudo sysctl -w kernel.numa_balancing_scan_period_max_ms=60000

# Розмір блоку сканування сторінок за один прохід (МБ)
sudo sysctl -w kernel.numa_balancing_scan_size_mb=256
```

---

### 7. Структура файлової системи `sysfs` для дослідження NUMA

Ядро експортує детальний фізичний стан кожного вузла в каталог `/sys/devices/system/node/`:

```
/sys/devices/system/node/
├── node0/
│   ├── cpulist             # Список процесорів вузла (наприклад, "0-31,64-95")
│   ├── cpumap              # Бітова маска процесорів у шістнадцятковому форматі
│   ├── distance            # Дистанції до інших вузлів ("10 21")
│   ├── meminfo             # Детальна статистика пам'яті (MemTotal, MemFree, Active, Inactive)
│   ├── numastat            # Лічильники NUMA-подій вузла
│   ├── hugepages/          # Стан HugePages для даного вузла (2048kB, 1048576kB)
│   └── compact             # Запис '1' у файл ініціює ручну дефрагментацію пам'яті вузла
├── node1/
│   └── ...
├── has_cpu                 # Маска вузлів, що мають фізичні процесорні ядра
├── has_memory              # Маска вузлів, що мають власну фізичну DRAM
├── online                  # Список активних вузлів системи
└── possible                # Максимально можлива кількість вузлів за конфігурацією ядра
```

### 8. Пакет `hwloc` (Hardware Locality): візуалізація та тонке керування

Хоча `libnuma` та `numactl` є стандартними утилітами Linux, бібліотека **Portable Hardware Locality (hwloc)** надає значно багатший та кросплатформний рівень абстракції, що охоплює не лише сокети та пам'ять, а й кеші L1/L2/L3, ядра, апаратні потоки (SMT/Hyper-Threading), адаптери PCIe (GPU, NVMe, мережеві карти) та топологію NUMA.

#### Утиліта `lstopo` — побудова графічної карти заліза

```bash
# 1. Текстовий вивід повної топології процесорів, кешів та NUMA-вузлів
lstopo --no-io

# 2. Графічний експорт структури сервера у векторний формат SVG або PDF
lstopo server_topology.svg
lstopo server_topology.pdf

# 3. Виведення зв'язку між мережевими інтерфейсами та найближчими NUMA-вузлами (PCIe Locality)
lstopo --pci
```

Вивід `lstopo --pci` показує, до якого саме сокета під'єднано контролер PCIe:

```
Machine (512GB Total)
  Package L#0 (256GB NUMANode L#0)
    L3 (36MB)
      Core L#0 ... Core L#31
    HostBridge
      PCI 0000:3b:00.0 (Network: eth0, 100GbE)  <-- Під'єднано напряму до Сокета 0!
  Package L#1 (256GB NUMANode L#1)
    L3 (36MB)
      Core L#32 ... Core L#63
```

Якщо мережева карта `eth0` під'єднана до PCIe-ліній Сокета 0, потік обробки мережевих пакетів повинен виконуватися на ядрах Сокета 0. Якщо обробник працюватиме на Сокеті 1, кожен пакет через DMA записуватиметься у вузол 0, а читатиметься ядрами вузла 1, створюючи подвійний міжвузловий штраф.

#### Утиліти фільтрації та прив'язки `hwloc`

```bash
# Запуск процесу на NUMA-вузлі 0 за допомогою hwloc-bind
hwloc-bind numa:0 -- ./high_load_server

# Розрахунок процесорних масок для розподілу завдань
hwloc-calc --intersect numa:1 package:all

# Моніторинг розміщення активних процесів за топологією заліза
hwloc-ps -a
```

#### Програмний інтерфейс C/C++ бібліотеки `hwloc`

:::tabs
```c
#include <hwloc.h>
#include <stdio.h>

void print_hwloc_topology(void) {
    hwloc_topology_t topo;
    hwloc_topology_init(&topo);
    hwloc_topology_load(topo);

    // Отримання кількості NUMA-вузлів через тип HWLOC_OBJ_NUMANODE
    int num_nodes = hwloc_get_nbobjs_by_type(topo, HWLOC_OBJ_NUMANODE);
    printf("Виявлено NUMA-вузлів через hwloc: %d\n", num_nodes);

    for (int i = 0; i < num_nodes; ++i) {
        hwloc_obj_t node = hwloc_get_obj_by_type(topo, HWLOC_OBJ_NUMANODE, i);
        printf("  NUMANode #%d: обсяг пам'яті = %.2f ГБ\n",
               node->os_index,
               (double)node->attr->numanode.memory_overhead / (1024 * 1024 * 1024));
    }

    hwloc_topology_destroy(topo);
}
```
```cpp
#include <hwloc.h>
#include <iostream>
#include <memory>
#include <format>
#include <stdexcept>

struct HwlocTopologyDeleter {
    void operator()(hwloc_topology_t topo) const noexcept {
        if (topo) hwloc_topology_destroy(topo);
    }
};
using UniqueTopology = std::unique_ptr<hwloc_topology, HwlocTopologyDeleter>;

void print_hwloc_topology_cpp() {
    hwloc_topology_t raw_topo;
    if (hwloc_topology_init(&raw_topo) != 0) {
        throw std::runtime_error("hwloc_topology_init failed");
    }
    UniqueTopology topo(raw_topo);
    hwloc_topology_load(topo.get());

    const int num_nodes = hwloc_get_nbobjs_by_type(topo.get(), HWLOC_OBJ_NUMANODE);
    std::cout << std::format("Виявлено NUMA-вузлів через hwloc: {}\n", num_nodes);

    for (int i = 0; i < num_nodes; ++i) {
        const hwloc_obj_t node = hwloc_get_obj_by_type(topo.get(), HWLOC_OBJ_NUMANODE, i);
        std::cout << std::format("  NUMANode #{}: індекс ОС = {}\n", i, node->os_index);
    }
}
```
:::

---

### 9. Керування NUMA в контейнерах і контрольних групах (cgroups v2)

У сучасних контейнеризованих середовищах (Docker, Podman, Kubernetes) обмеження процесорів і пам'яті задаються через контрольні групи підсистеми `cpuset`.

У файловій системі `cgroup v2` (каталог `/sys/fs/cgroup/`) для кожного контейнера створюються спеціальні файли конфігурації:

#### `cpuset.cpus` — список дозволених процесорів
```bash
# Дозволити контейнеру виконуватися лише на ядрах 0–31 (Вузол 0)
echo "0-31" | sudo tee /sys/fs/cgroup/my_container/cpuset.cpus
```

#### `cpuset.mems` — список дозволених NUMA-вузлів для виділення пам'яті
```bash
# Жорстко обмежити виділення пам'яті контейнера лише Вузлом 0
echo "0" | sudo tee /sys/fs/cgroup/my_container/cpuset.mems
```

Якщо процес усередині контейнера намагається виділити пам'ять на вузлі, не включеному в `cpuset.mems`, ядро автоматично блокує це виділення або перенаправляє його на дозволені вузли, запобігаючи несанкціонованому споживанню ресурсів сусідніх сокетів.

#### `memory.numa_stat` — детальна статистика контейнера за вузлами
```bash
cat /sys/fs/cgroup/my_container/memory.numa_stat
```
Вивід файлу містить повний зріз споживання анонімної пам'яті, файлового кешу та сторінок пам'яті ядра окремо для кожного вузла (`anon N0=... N1=...`, `file N0=... N1=...`, `kernel N0=... N1=...`).

---

### 10. Повний перелік функцій бібліотеки `libnuma`

Нижче наведено повну довідкову таблицю найважливіших функцій бібліотеки `libnuma` із зазначенням їхньої ролі та поведінки:

| Функція `libnuma` | Призначення та поведінка |
| :--- | :--- |
| **`numa_available()`** | Перевіряє, чи підтримує поточне ядро системні виклики NUMA. Повертає `0` при готовності та `-1` при помилці. Мусить викликатися першою перед будь-якими іншими викликами `numa_*`. |
| **`numa_max_node()`** | Повертає максимальний доступний ідентифікатор вузла в системі. |
| **`numa_num_configured_nodes()`** | Повертає загальну кількість сконфігурованих вузлів. |
| **`numa_node_to_cpus(node, mask)`** | Заповнює структуру `bitmask` переліком усіх фізичних ядер, що апаратно належать вказаному вузлу `node`. |
| **`numa_node_to_cpu_update()`** | Оновлює кешовану таблицю відповідності ядер і вузлів (актуально при гарячому підключенні процесорів CPU Hotplug). |
| **`numa_alloc_onnode(size, node)`** | Виділяє пам'ять обсягом `size` строго на вузлі `node` через системний виклик `mmap` та `mbind(..., MPOL_BIND)`. |
| **`numa_alloc_local(size)`** | Виділяє пам'ять на локальному вузлі ядра, на якому виконується потік під час виклику. |
| **`numa_alloc_interleaved(size)`** | Виділяє пам'ять, сторінки якої по черзі розподіляються між усіма активними вузлами системи (`MPOL_INTERLEAVE`). |
| **`numa_alloc(size)`** | Виділяє пам'ять відповідно до діючої політики за замовчуванням поточного процесу. |
| **`numa_free(ptr, size)`** | Звільняє пам'ять, виділену функціями `numa_alloc_*`. Вимагає точного передавання початкового розміру `size` для коректного виклику `munmap`. |
| **`numa_tonode_memory(ptr, size, node)`** | Примусово мігрує вже виділений блок пам'яті за адресою `ptr` на вузол `node` через `mbind(..., MPOL_MF_MOVE)`. |
| **`numa_tonodemask_memory(ptr, size, mask)`** | Мігрує діапазон пам'яті на множину вузлів, задану маскою `mask`. |
| **`numa_set_bind_policy(strict)`** | Встановлює строгість політики прив'язки: якщо `strict = 1`, неможливість виділити пам'ять на цільовому вузлі генерує помилку; якщо `0`, дозволяється виділення на інших вузлах. |
| **`numa_set_strict(strict)`** | Глобальний перемикач генерації помилок при відмові виділення пам'яті на бажаному вузлі. |
| **`numa_warn(number, description)`** | Внутрішній обробник попереджень бібліотеки `libnuma`. |
| **`numa_exit_on_error`** | Глобальна змінна-прапорець: якщо встановлена в `1`, бібліотека завершує процес із викликом `exit()` при будь-якій внутрішній помилці виділення чи прив'язки. |

Цей довідник охоплює повний набір інтерфейсів для створення надійного системного програмного забезпечення, оптимізованого під архітектуру сучасних багатопроцесорних серверів.

