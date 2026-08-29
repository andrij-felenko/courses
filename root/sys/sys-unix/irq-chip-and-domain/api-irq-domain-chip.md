# 📋 Інтерфейс контролера та домену переривань: структури, методи й операції ядра

Підсистема керування перериваннями ядра Linux (*Generic IRQ Framework*) надає типізований та модульний програмний інтерфейс, який розділяє апаратне керування лініями контролера, трансляцію просторів номерів, підтримку векторних повідомлень MSI/MSI-X, каскадне демультиплексування та реєстрацію обробників периферійних пристроїв. Архітектура спирається на такі ключові компоненти:

1. **`struct irq_chip`** — таблиця низькорівневих операцій для безпосередньої взаємодії з регістрами фізичного контролера переривань (маскування, квитування, надсилання EOI, маршрутизація на ядра CPU, конструювання повідомлень MSI, керування живленням).
2. **`struct irq_domain`** — абстракція простору номерів, яка інкапсулює логіку взаємно однозначного відображення локальних апаратних номерів (`hwirq`) у єдиний простір віртуальних дескрипторів ядра Linux (`virq`).
3. **Підсистема MSI/MSI-X доменів (`struct msi_domain_info`, `struct msi_msg`)** — багаторівнева ієрархія для виділення, трансляції та програмування переривань на основі запису повідомлень у системну пам'ять на шинах PCI Express, Platform MSI та I2C.
4. **Каскадні демультиплексори (*Chained IRQ Handlers*) та вкладені обробники (*Nested Threaded IRQ*)** — механізми вторинної диспетчеризації переривань для блоків GPIO, розширювачів портів та FPGA.
5. **Диспетчери потоку (*Generic Flow Handlers*)** — уніфіковані алгоритми ядра, що реалізують протокол обробки сигналів залежно від їхньої електричної природи (рівень напруги, фронт, повідомлення MSI, каскадні або вкладені шини).
6. **Життєвий цикл переривання та поділ половин** — наскрізний шлях виконання від апаратного вектора процесора, виклику `generic_handle_domain_irq()` та обробників дій `struct irqaction` до диспетчеризації `softirq` (`__do_softirq()`) та ниток реального часу `kthread` (`irq/NN-name`).
7. **Керування процесорною спорідненістю (IRQ Affinity)** — C-інтерфейс ядра (`irq_set_affinity()`, `irq_create_affinity_masks()`), апаратні моделі маршрутизації (APIC logical/physical mode, GICv3 IROUTER) та системний демон балансування навантаження `irqbalance`.
8. **Інтеграція з Device Tree (`of_irq`) та платформою (`platform_irq`)** — декларативний опис топології переривань у дереві пристроїв та ядровий C-інтерфейс зв'язування вузлів із драйверами.
9. **Драйверний інтерфейс реєстрації** — методи `request_threaded_irq()`, `devm_request_threaded_irq()`, правила синхронізації та відкладеного керування.
10. **Віртуалізація переривань та пряма ін'єкція векторів** — протокол зв'язування `VFIO_DEVICE_SET_IRQS`, механізми `irqfd` та `resamplefd` у KVM, підсистема `irqbypass`, а також пряма апаратна ін'єкція повідомлень у віртуальні процесори без виходу в гіпервізор (Intel VT-d Posted Interrupts, ARM GICv4 Virtual LPI).
11. **Діагностика та метрики** — структури `/proc/interrupts`, sysfs, DebugFS (`irq/domains/summary`) та трасувальні точки `tracepoint`.

Нижче наведено вичерпну специфікацію внутрішнього API ядра Linux, сигнатур функцій, структур даних, контекстів виконання, вимог до блокувань та системних діагностичних інтерфейсів.

---

## 1. Низькорівнева абстракція контролера: struct irq_chip

Структура `struct irq_chip` (визначена в `<linux/irq.h>`) містить набір функціональних покажчиків, які ядро викликає для маніпуляції станом фізичних ліній та регістрів контролера переривань. Усі методи приймають покажчик на `struct irq_data`, через який драйвер отримує локальний апаратний номер `data->hwirq`, прив'язаний чіп `data->chip`, приватні дані екземпляра `data->chip_data` та маску спорідненості `irq_data_get_affinity_mask(data)`.

```c
#include <linux/irq.h>

struct irq_chip {
    struct device       *parent_device;
    const char          *name;
    unsigned int        (*irq_startup)(struct irq_data *data);
    void                (*irq_shutdown)(struct irq_data *data);
    void                (*irq_enable)(struct irq_data *data);
    void                (*irq_disable)(struct irq_data *data);

    void                (*irq_ack)(struct irq_data *data);
    void                (*irq_mask)(struct irq_data *data);
    void                (*irq_mask_ack)(struct irq_data *data);
    void                (*irq_unmask)(struct irq_data *data);
    void                (*irq_eoi)(struct irq_data *data);

    int                 (*irq_set_affinity)(struct irq_data *data,
                                            const struct cpumask *dest,
                                            bool force);
    int                 (*irq_retrigger)(struct irq_data *data);
    int                 (*irq_set_type)(struct irq_data *data,
                                        unsigned int flow_type);
    int                 (*irq_set_wake)(struct irq_data *data,
                                        unsigned int on);

    void                (*irq_bus_lock)(struct irq_data *data);
    void                (*irq_bus_sync_unlock)(struct irq_data *data);

    void                (*irq_compose_msi_msg)(struct irq_data *data,
                                               struct msi_msg *msg);
    void                (*irq_write_msi_msg)(struct irq_data *data,
                                             struct msi_msg *msg);

    int                 (*irq_set_vcpu_affinity)(struct irq_data *data,
                                                 void *vcpu_info);

    unsigned long       flags;
};
```

### Специфікація полів та функціональних покажчиків

| Поле / Метод | Контекст виклику | Блокування | Опис та контракт поведінки |
| :--- | :--- | :--- | :--- |
| `name` | — | — | Рядковий ідентифікатор контролера (наприклад, `"GICv3"`, `"gpio-irq"`). Відображається у `/proc/interrupts` та DebugFS. |
| `parent_device` | — | — | Покажчик на базовий `struct device`, який володіє контролером переривань. Використовується підсистемою керування живленням. |
| `irq_startup(data)` | Процес / ініціалізація | `desc->lock` | Первинний запуск лінії переривання. Якщо метод не визначено (NULL), ядро за замовчуванням викликає `irq_enable()` або `irq_unmask()`. Повертає 0 у разі успіху або від'ємний код помилки. |
| `irq_shutdown(data)` | Процес (`free_irq`) | `desc->lock` | Повне апаратне відключення лінії після звільнення останнього драйвера. Якщо NULL, викликається `irq_disable()` або `irq_mask()`. |
| `irq_enable(data)` | hardirq / процес | `desc->lock` | Дозволяє генерацію переривань на фізичній лінії. Якщо NULL, викликається `irq_unmask()`. |
| `irq_disable(data)` | hardirq / процес | `desc->lock` | Забороняє генерацію переривань. Якщо NULL, ядро викликає `irq_mask()`. Реалізує механізм відкладеного (lazy) відключення. |
| `irq_ack(data)` | hardirq (атомарний) | `desc->lock` | Квитує отримання імпульсу переривання в контролері (скидання засувки статусу, зазвичай записом одиниці — *Write-1-to-Clear*). Обов'язковий для переривань за фронтом (`handle_edge_irq`). |
| `irq_mask(data)` | hardirq (атомарний) | `desc->lock` | Записує бітову маску блокування в регістр контролера. Забороняє передачу сигналу на CPU. Заборонено засинати або виділяти пам'ять. |
| `irq_mask_ack(data)` | hardirq (атомарний) | `desc->lock` | Оптимізація для контролерів, де маскування та квитування виконуються однією операцією запису в спільний регістр MMIO. |
| `irq_unmask(data)` | hardirq / процес | `desc->lock` | Знімає маску блокування, дозволяючи фізичній лінії знову сигналізувати центральному процесору про нові події. |
| `irq_eoi(data)` | hardirq (атомарний) | `desc->lock` | Надсилає сигнал завершення обробки (*End of Interrupt*) у контролер з апаратною чергою пріоритетів (ARM GIC, Intel APIC, RISC-V PLIC). |
| `irq_set_affinity(data, dest, force)` | Процес / переривання | `desc->lock` | Перенаправляє лінію переривання на вказану маску ядер процесора `dest`. Повертає `IRQ_SET_MASK_OK` (ядро оновить маску в дескрипторі), `IRQ_SET_MASK_OK_DONE` (драйвер сам оновив маску), або `-EINVAL` / `-ENOSYS`. |
| `irq_retrigger(data)` | hardirq (атомарний) | `desc->lock` | Програмно повторно ініціює переривання в контролері. Повертає 1, якщо retrigger виконано апаратно, або 0, якщо ядро має застосувати програмний fallback через softirq (`resend_irqs`). |
| `irq_set_type(data, flow_type)` | Процес / ініціалізація | `desc->lock` | Програмує електричну чутливість вхідного каскаду контролера. Параметр `flow_type` містить комбінацію бітових прапорців `IRQ_TYPE_*`. Повертає 0 у разі успіху або `-EINVAL`. |
| `irq_set_wake(data, on)` | Процес (`suspend`) | `desc->lock` | Вмикає (`on=1`) або вимикає (`on=0`) здатність переривання пробуджувати процесор зі стану сну (*System Suspend*). Повертає 0 або `-EINVAL` / `-ENXIO`. |
| `irq_bus_lock(data)` | Процес | Власний м'ютекс | Захоплює сплячий м'ютекс (`mutex_lock`) для контролерів на повільних шинах I2C/SPI/SPMI перед модифікацією тіньових регістрів. |
| `irq_bus_sync_unlock(data)` | Процес | Власний м'ютекс | Виконує реальні транзакції запису накопичених змін по шині I2C/SPI в контексті потоку і відпускає сплячий м'ютекс (`mutex_unlock`). |
| `irq_compose_msi_msg(data, msg)` | Процес | `desc->lock` | Формує 64-бітну адресу запису в пам'ять `msg->address_hi/lo` та 32-бітне значення даних `msg->data` для повідомлень PCI MSI/MSI-X. |
| `irq_write_msi_msg(data, msg)` | Процес | `desc->lock` | Записує структуру `struct msi_msg` у конфігураційні регістри кінцевого пристрою або контролера. |
| `irq_set_vcpu_affinity(data, vcpu_info)` | Процес (KVM) | `desc->lock` | Налаштовує пряму апаратну доставку переривання у віртуальний процесор гостьової ОС (наприклад, ARM GICv4 virtual interrupts / vPE). |

### Детальний контракт зворотних викликів irq_chip

#### `irq_startup(data)` та `irq_shutdown(data)`
- **`irq_startup`**: Викликається під час активації першого обробника лінії (`__setup_irq()`). Повертає `0` або `IRQ_STARTUP_NORMAL` при успішній ініціалізації апаратного блоку. Якщо повертається від'ємне число (`-EBUSY`, `-EINVAL`), реєстрація переривання завершується аварійно.
- **`irq_shutdown`**: Викликається під час звільнення останнього `struct irqaction` у функції `free_irq()`. Драйвер зобов'язаний повністю перевести лінію в пасивний стан, вимкнути тактування аналогового входу та зняти всі виставлені тригери.

#### `irq_ack(data)`, `irq_mask(data)`, `irq_unmask(data)` та `irq_eoi(data)`
- **`irq_ack`**: Виконує скидання біта фіксації переривання (*Latch*) у контролері. Викликається на початку `handle_edge_irq` до виклику дій пристрою, щоб апаратура не пропустила новий імпульс під час роботи ISR.
- **`irq_mask`**: Записує одиницю у бітову маску блокування (*Interrupt Mask Register*). Виклик здійснюється під `raw_spin_lock(&desc->lock)` з вимкненими локальними перериваннями процесора. Будь-які блокуючі виклики (`msleep()`, `mutex_lock()`, `kmalloc(..., GFP_KERNEL)`) у цьому методі заборонені.
- **`irq_unmask`**: Записує одиницю у регістр очищення маски (*Interrupt Unmask / Clear Mask Register*), відкриваючи проходження сигналу на процесорне ядро.
- **`irq_eoi`**: Сигнал завершення транзакції переривання для контролерів із чергою пріоритетів. На контролерах ARM GICv3 запис у регістр `ICC_EOIR1_EL1` знижує пріоритет запущеної задачі та дозволяє арбітраж наступних сигналів тієї ж або вищої пріоритетної групи.

#### `irq_set_affinity(data, dest, force)`
- **Призначення:** Зміна маски ядер центрального процесора, на які контролер спрямовує сигнал переривання.
- **Параметри:**
  - `dest`: константний покажчик на `struct cpumask` із цільовими процесорами.
  - `force`: логічний прапорець. Якщо `force == false`, драйвер зобов'язаний обмежити вибір лише тими ядрами з `dest`, які перебувають у стані онлайн (`cpu_online_mask`). Якщо `force == true`, драйвер змушений налаштувати контролер на вказану маску навіть під час гарячого відключення поточного ядра (*CPU Hotplug offline path*).
- **Коди повернення:**
  - `IRQ_SET_MASK_OK`: налаштування успішне; загальне ядро переривань автоматично записує нову маску в `irq_data->common->affinity`.
  - `IRQ_SET_MASK_OK_DONE`: налаштування успішне, і драйвер самостійно оновив маску спорідненості.
  - `-EINVAL`: жоден із вказаних CPU не підтримується контролером.
  - `-ENOSYS`: апаратна маршрутизація спорідненості не підтримується цією мікросхемою.

#### `irq_bus_lock(data)` та `irq_bus_sync_unlock(data)`
- **Проблема:** Контролери переривань, розміщені на повільних послідовних шинах (I2C/SPI розширювачі портів типу MCP23017 або PMIC), не можуть виконувати операції вводу-виводу всередині `irq_mask()` чи `irq_unmask()`, оскільки ці методи викликаються під час утримання `raw_spinlock_t` дескриптора з вимкненими перериваннями.
- **Механізм роботи:**
  1. Коли високорівневий код (наприклад, `enable_irq()` або `irq_set_type()`) хоче змінити стан лінії, ядро викликає `chip->irq_bus_lock(data)`, де драйвер захоплює власний `mutex_lock(&chip_priv->bus_mutex)`.
  2. Методи `irq_mask()`, `irq_unmask()`, `irq_set_type()` викликаються під spinlock дескриптора, але **не виконують фізичних транзакцій шини**, а лише оновлюють поля тіньового стану драйвера (`shadow_mask`, `shadow_type`).
  3. Ядро відпускає спінлок дескриптора і викликає `chip->irq_bus_sync_unlock(data)`.
  4. У методі `irq_bus_sync_unlock()` драйвер виконує повільні блокуючі транзакції запису накопичених змін по шині I2C/SPI через `i2c_transfer()` / `spi_sync()` і відпускає сплячий м'ютекс `mutex_unlock(&chip_priv->bus_mutex)`.

### Прапорці конфігурації чіпа (`flags`)

Поле `flags` структури `struct irq_chip` керує оптимізаціями та апаратними обмеженнями контролера:

```c
#define IRQCHIP_SET_TYPE_MASKED         (1 << 0)
#define IRQCHIP_EOI_IF_HANDLED          (1 << 1)
#define IRQCHIP_MASK_ON_SUSPEND         (1 << 2)
#define IRQCHIP_ONESHOT_SAFE            (1 << 3)
#define IRQCHIP_SKIP_SET_WAKE           (1 << 4)
#define IRQCHIP_AUTOMASKS_FLOW          (1 << 5)
#define IRQCHIP_AFFINITY_PRE_STARTUP    (1 << 6)
#define IRQCHIP_SUPPORTS_LEVEL_MSI      (1 << 7)
#define IRQCHIP_IMMUTABLE               (1 << 8)
```

- **`IRQCHIP_SET_TYPE_MASKED`**: Вимагає від ядра обов'язково замаскувати лінію переривання перед викликом методу `irq_set_type()`. Застосовується для контролерів, які генерують помилковий паразитний імпульс під час перемикання тригера чутливості з фронту на рівень.
- **`IRQCHIP_EOI_IF_HANDLED`**: Вказує диспетчеру `handle_fasteoi_irq` надсилати сигнал `irq_eoi()` лише тоді, коли хоча б один зареєстрований обробник `struct irqaction` повернув `IRQ_HANDLED` або лінія не була заблокована.
- **`IRQCHIP_MASK_ON_SUSPEND`**: Ядро автоматично викликає `irq_mask()` для цієї лінії перед переходом системи в режим сну, якщо для неї не було активовано джерело пробудження через `enable_irq_wake()`.
- **`IRQCHIP_ONESHOT_SAFE`**: Повідомляє ядро, що контролер здатний самостійно утримувати лінію замаскованою на апаратному рівні під час роботи потокового обробника, усуваючи необхідність додаткового програмного маскування в режимі `IRQF_ONESHOT`.
- **`IRQCHIP_SKIP_SET_WAKE`**: Вказує ядру ігнорувати відсутність реалізації методу `irq_set_wake()` і не повертати помилку `-ENXIO` під час налаштування джерел пробудження.
- **`IRQCHIP_AUTOMASKS_FLOW`**: Контролер апаратно маскує лінію під час прийому сигналу (потрібне явне демаскування в кінці циклу обробки).
- **`IRQCHIP_AFFINITY_PRE_STARTUP`**: Вимагає від ядра налаштувати процесорну спорідненість (`irq_set_affinity`) до виклику `irq_startup()`.
- **`IRQCHIP_SUPPORTS_LEVEL_MSI`**: Позначає, що даний MSI-контролер коректно емулює семантику переривань за рівнем напруги.
- **`IRQCHIP_IMMUTABLE`**: Позначає структуру чіпа як незмінну константу (`const struct irq_chip`), що захищає таблицю функціональних покажчиків від динамічної модифікації під час виконання.

---

## 2. Простори номерів та типи доменів: struct irq_domain

Структура `struct irq_domain` (визначена в `<linux/irqdomain.h>`) інкапсулює простір локальних номерів `hwirq` одного фізичного або логічного контролера переривань.

```c
#include <linux/irqdomain.h>

struct irq_domain {
    struct list_head        link;
    const char              *name;
    const struct irq_domain_ops *ops;
    void                    *host_data;
    unsigned int            flags;
    unsigned int            mapcount;

    struct fwnode_handle    *fwnode;
    enum irq_domain_bus_token bus_token;

    struct irq_domain       *parent;

    irq_hw_number_t         hwirq_max;
    unsigned int            revmap_size;
    struct radix_tree_root  revmap_tree;
    struct xarray           revmap_xarray;
    unsigned int            linear_revmap[];
};
```

### Типи шинних маркерів доменів (`enum irq_domain_bus_token`)

Поле `bus_token` розрізняє домени за типом апаратної шини, які обслуговують однаковий вузол пристрою (наприклад, одночасна наявність дротових ліній та MSI на одному контролері):

```c
enum irq_domain_bus_token {
    DOMAIN_BUS_ANY          = 0,
    DOMAIN_BUS_WIRED        = 1,
    DOMAIN_BUS_GENERIC_MSI  = 2,
    DOMAIN_BUS_PCI_MSI      = 3,
    DOMAIN_BUS_PLATFORM_MSI = 4,
    DOMAIN_BUS_NEXUS        = 5,
    DOMAIN_BUS_I2C_MSI      = 6,
    DOMAIN_BUS_VMD_MSI      = 7,
    DOMAIN_BUS_PCI_DEVICE_MSI  = 8,
    DOMAIN_BUS_PCI_DEVICE_MSIX = 9,
};
```

### Моделі зворотного відображення (*Reverse Mapping*)

Домен переривань підтримує декілька моделей збереження та швидкого пошуку відображення `hwirq -> virq`:

```
+-------------------------------------------------------------------------------+
|                        Типи доменів переривань Linux                          |
+---------------------+-------------------+-------------------+-----------------+
|   Linear Domain     |   Radix / Tree    |    Hierarchical   |     Legacy      |
|  irq_domain_add_    |  irq_domain_add_  |  irq_domain_      |  irq_domain_    |
|       linear()      |       tree()      | create_hierarchy()|   add_legacy()  |
+---------------------+-------------------+-------------------+-----------------+
| Швидкий масив O(1): | Розріджене дерево | Багаторівневий    | Фіксований зсув |
| hwirq < revmap_size | Великі / розрід-  | зв'язок domain->  | virq = base +   |
| (GPIO, SoC чіпи)    | жені номери (MSI) | parent (MSI->GIC) | hwirq (ISA PIC) |
+---------------------+-------------------+-------------------+-----------------+
```

#### 1. Лінійний домен (*Linear Domain*)
- **Функція створення:** `irq_domain_add_linear()` або `irq_domain_create_linear()`.
- **Внутрішня організація:** Виділяє структуру `struct irq_domain` разом із гнучким масивом `linear_revmap[size]` в єдиному неперервному блоці динамічної пам'яті через `kzalloc(sizeof(*domain) + size * sizeof(unsigned int), GFP_KERNEL)`.
- **Пошук відображення (`irq_find_mapping`):** Прямий індексний доступ `domain->linear_revmap[hwirq]`. Виконується за `O(1)` без використання блокувань, виділення пам'яті чи атомарних бар'єрів.
- **Обмеження:** Номер `hwirq` повинен суворо задовольняти умову `hwirq < domain->revmap_size`. Якщо запитується `hwirq >= size`, пошук повертає 0.
- **Застосування:** Контролери GPIO (16..256 ліній), первинні контролери переривань SoC із фіксованим невеликим числом входів (ARM GIC SPI/PPI до 1024 ліній).

#### 2. Деревоподібний домен (*Tree / Radix Domain*)
- **Функція створення:** `irq_domain_add_tree()` або `irq_domain_create_tree()`.
- **Внутрішня організація:** Зберігає асоціації `hwirq -> virq` у розрідженій деревоподібній структурі `XArray` (`revmap_xarray`) або Radix Tree (`revmap_tree`). Поле `revmap_size` встановлюється в `0`.
- **Пошук відображення (`irq_find_mapping`):** Виконує пошук за ключем у структурі `XArray` під захистом RCU (`rcu_read_lock()`). Складність пошуку складає `O(log N)`, де `N` — кількість зареєстрованих векторів.
- **Переваги:** Підтримка довільно великих або розріджених апаратних номерів у діапазоні від `0` до `2^32 - 1` (або `2^64 - 1`) без надлишкових витрат пам'яті на порожні проміжки.
- **Застосування:** Контролери повідомлень PCI MSI/MSI-X, блоки ARM GIC-ITS із 32-бітними ідентифікаторами подій (*Event ID*).

#### 3. Ієрархічний домен (*Hierarchical Domain*)
- **Функція створення:** `irq_domain_create_hierarchy()`.
- **Внутрішня організація:** Зв'язує ланцюжок контролерів через покажчик `domain->parent`. Для одного номера `virq` ядро створює пов'язаний список структур `struct irq_data`, де кожний елемент представляє свій рівень апаратури (`data->parent_data`).
- **Трансляція та виділення:** Метод `ops->alloc()` виділяє локальний апаратний ресурс і каскадно викликає `irq_domain_alloc_irqs_parent(d, virq, nr_irqs, &parent_arg)`.
- **Застосування:** Багаторівневі шляхи проходження сигналів: `PCIe MSI Endpoint -> IOMMU Interrupt Remapping (IRTE) -> ARM GIC ITS -> ARM GIC Distributor`.

#### 4. Застарілий домен (*Legacy Domain*)
- **Функція створення:** `irq_domain_add_legacy()` або `irq_domain_create_legacy()`.
- **Внутрішня організація:** Жорстко пов'язує неперервний діапазон `hwirq` з попередньо виділеним фіксованим базовим номером `first_irq` за формулою: `virq = first_irq + (hwirq - first_hwirq)`.
- **Особливість:** Під час створення домену ядро автоматично створює всі дескриптори та викликає метод `ops->map()` для кожного елемента діапазону.
- **Застосування:** Контролери x86 8259A PIC (номери 0..15), старі платформи ARM без підтримки розріджених дескрипторів `CONFIG_SPARSE_IRQ`.

#### 5. Прямий домен (*No-Map Domain*)
- **Функція створення:** `irq_domain_add_nomap()`.
- **Контракт:** Припускає повну тотожність номерів: `virq == hwirq`.
- **Статус у ядрі:** Заборонений для використання в нових драйверах. Зберігся виключно для зворотної сумісності зі старими вбудованими платами PowerPC.

---

## 3. Таблиця операцій домену: struct irq_domain_ops

Структура `struct irq_domain_ops` визначає методи трансляції специфікаторів, створення відображень та керування багаторівневими дескрипторами:

```c
#include <linux/irqdomain.h>

struct irq_domain_ops {
    int (*match)(struct irq_domain *d, struct device_node *node,
                 enum irq_domain_bus_token bus_token);
    int (*select)(struct irq_domain *d, struct irq_fwspec *fwspec,
                  enum irq_domain_bus_token bus_token);
    int (*map)(struct irq_domain *d, unsigned int virq, irq_hw_number_t hw);
    void (*unmap)(struct irq_domain *d, unsigned int virq);
    int (*xlate)(struct irq_domain *d, struct device_node *node,
                 const u32 *intspec, unsigned int intsize,
                 unsigned long *out_hwirq, unsigned int *out_type);
    int (*translate)(struct irq_domain *d, struct irq_fwspec *fwspec,
                     unsigned long *out_hwirq, unsigned int *out_type);
    int (*alloc)(struct irq_domain *d, unsigned int virq,
                 unsigned int nr_irqs, void *arg);
    void (*free)(struct irq_domain *d, unsigned int virq,
                 unsigned int nr_irqs);
    int (*activate)(struct irq_domain *d, struct irq_data *irqd, bool reserve);
    void (*deactivate)(struct irq_domain *d, struct irq_data *irqd);
};
```

### Контракти методів

#### `match(d, node, bus_token)`
- **Призначення:** Визначає, чи відповідає даний домен вузлу Device Tree `node` та типу шини `bus_token`.
- **Повертає:** `1` у разі повної відповідності, `0` якщо домен не підходить.
- **Поведінка ядра за замовчуванням (якщо NULL):** Ядро перевіряє `to_of_node(d->fwnode) == node` та рівність шинного токена (`d->bus_token == bus_token || d->bus_token == DOMAIN_BUS_ANY`).

#### `select(d, fwspec, bus_token)`
- **Призначення:** Універсальний механізм ідентифікації домену на основі структури `struct irq_fwspec` (підтримує як вузли Device Tree, так і об'єкти ACPI fwnode).
- **Повертає:** `1` при збігу, `0` при невідповідності. Викликається ядром перед методом `match()`.

#### `map(d, virq, hw)`
- **Призначення:** Ініціалізація дескриптора переривання під час первинного зв'язування `hwirq` та `virq` у функції `irq_create_mapping()`.
- **Параметри:** `d` — покажчик на домен, `virq` — виділений віртуальний номер ядра, `hw` — локальний апаратний номер `hwirq`.
- **Обов'язки драйвера:**
  1. Призначити структуру операцій `struct irq_chip` та диспетчер потоку через `irq_set_chip_and_handler()` або `irq_set_chip_and_handler_name()`.
  2. Зберегти приватний покажчик на контекст драйвера через `irq_set_chip_data(virq, priv)`.
  3. Встановити початкові біти стану лінії через `irq_set_status_flags()`.
- **Коди повернення:** `0` при успіху, від'ємний код помилки (`-EINVAL`, `-ENOMEM`, `-EPERM`).
- **Контекст блокування:** Викликається з процесного контексту під час утримання глобального м'ютексу `irq_domain_mutex`.

#### `unmap(d, virq)`
- **Призначення:** Звільнення прив'язаних до лінії ресурсів перед видаленням відображення у функції `irq_dispose_mapping()`.
- **Обов'язки драйвера:** Скинути налаштування чіпа через `irq_set_chip_and_handler(virq, NULL, NULL)`, очистити приватні дані `irq_set_chip_data(virq, NULL)` та повернути виділені апаратні ресурси контролера.

#### `xlate(d, node, intspec, intsize, out_hwirq, out_type)`
- **Призначення:** Декодує сирі 32-бітні цілі числа з властивості `interrupts = <...>` вузла Device Tree.
- **Параметри:**
  - `intspec`: масив числових комірок специфікатора переривання.
  - `intsize`: кількість переданих комірок (визначається властивістю `#interrupt-cells` батьківського контролера).
  - `out_hwirq`: вихідний покажчик, куди записується обчислений апаратний номер `hwirq`.
  - `out_type`: вихідний покажчик, куди записується маска типу тригера (`IRQ_TYPE_*`).
- **Повертає:** `0` при успіху або `-EINVAL`, якщо кількість комірок `intsize` не відповідає формату контролера.
- **Стандартні допоміжні функції ядра:**
  - `irq_domain_xlate_onecell`: 1 комірка (`intspec[0] = hwirq`, тип встановлюється в `IRQ_TYPE_NONE`).
  - `irq_domain_xlate_twocell`: 2 комірки (`intspec[0] = hwirq`, `intspec[1] = trigger_flags`).
  - `irq_domain_xlate_onetwocell`: підтримує як 1, так і 2 комірки.

#### `translate(d, fwspec, out_hwirq, out_type)`
- **Призначення:** Універсальний аналог `xlate()`, що працює зі структурою `struct irq_fwspec`. Використовується для трансляції дескрипторів ACPI Extended Interrupt Resource Descriptors, PCI MSI та платформних пристроїв.
- **Повертає:** `0` при успіху або `-EINVAL`.

#### `alloc(d, virq, nr_irqs, arg)`
- **Призначення:** Виділяє ресурси в ієрархічному домені для діапазону з `nr_irqs` неперервних номерів, починаючи з `virq`.
- **Параметр `arg`:** Покажчик на специфікатор запиту (зазвичай `struct irq_fwspec *` або специфічна для шини структура, наприклад `msi_alloc_info_t`).
- **Послідовність виконання в драйвері:**
  1. Декодувати локальний `hwirq` та тип тригера з `arg`.
  2. Сформувати аргументи для батьківського домену `struct irq_fwspec parent_fwspec`.
  3. Каскадно викликати `irq_domain_alloc_irqs_parent(d, virq, nr_irqs, &parent_fwspec)`.
  4. Прив'язати кожен номер у циклі: `irq_domain_set_hwirq_and_chip(d, virq + i, hwirq + i, chip, chip_data)`.
- **Повертає:** `0` у разі успіху або `-ENOMEM` / `-EINVAL` при помилці.

#### `free(d, virq, nr_irqs)`
- **Призначення:** Звільняє ресурси ієрархічного дескриптора. Драйвер очищає власні структури та обов'язково каскадно викликає `irq_domain_free_irqs_parent(d, virq, nr_irqs)`.

#### `activate(d, irqd, reserve)` та `deactivate(d, irqd)`
- **Призначення:** Реалізують механізм лінивої активації (*Lazy Activation*).
- **Параметр `reserve`:** Якщо `reserve == true`, ядро резервує апаратний вектор у таблицях маршрутизації без фактичного дозволу фізичної генерації сигналу. Якщо `reserve == false`, драйвер виконує повне апаратне програмування маршруту в регістрах контролера (викликається безпосередньо всередині `request_threaded_irq()`).
- **`deactivate`**: Вимикає апаратну маршрутизацію вектора після виклику `free_irq()`.

---

## 4. Функції реєстрації, управління та життєвого циклу доменів

### Створення та знищення доменів

```c
#include <linux/irqdomain.h>

/* Створення лінійного домену на основі Device Tree node */
struct irq_domain *irq_domain_add_linear(struct device_node *of_node,
                                         unsigned int size,
                                         const struct irq_domain_ops *ops,
                                         void *host_data);

/* Створення лінійного домену на основі універсального fwnode */
struct irq_domain *irq_domain_create_linear(struct fwnode_handle *fwnode,
                                            unsigned int size,
                                            const struct irq_domain_ops *ops,
                                            void *host_data);

/* Створення деревоподібного домену (Radix tree / XArray) */
struct irq_domain *irq_domain_add_tree(struct device_node *of_node,
                                       const struct irq_domain_ops *ops,
                                       void *host_data);

struct irq_domain *irq_domain_create_tree(struct fwnode_handle *fwnode,
                                          const struct irq_domain_ops *ops,
                                          void *host_data);

/* Створення ієрархічного домену */
struct irq_domain *irq_domain_create_hierarchy(struct irq_domain *parent,
                                               unsigned int flags,
                                               unsigned int size,
                                               struct fwnode_handle *fwnode,
                                               const struct irq_domain_ops *ops,
                                               void *host_data);

/* Створення legacy-домену з фіксованою прив'язкою virq */
struct irq_domain *irq_domain_add_legacy(struct device_node *of_node,
                                         unsigned int size,
                                         unsigned int first_irq,
                                         irq_hw_number_t first_hwirq,
                                         const struct irq_domain_ops *ops,
                                         void *host_data);

struct irq_domain *irq_domain_create_legacy(struct fwnode_handle *fwnode,
                                            unsigned int size,
                                            unsigned int first_irq,
                                            irq_hw_number_t first_hwirq,
                                            const struct irq_domain_ops *ops,
                                            void *host_data);

/* Зміна шинного маркера домену */
void irq_domain_update_bus_token(struct irq_domain *d,
                                 enum irq_domain_bus_token bus_token);

/* Видалення домену з глобального реєстру ядра */
void irq_domain_remove(struct irq_domain *d);
```

### Створення та трансляція номерів (`hwirq <-> virq`)

```c
/* Створення або повернення існуючого відображення (виділяє virq та викликає ops->map) */
unsigned int irq_create_mapping(struct irq_domain *host,
                                irq_hw_number_t hwirq);

/* Швидкий безблокувальний пошук virq у гарячому тракті обробника (не виділяє пам'ять) */
unsigned int irq_find_mapping(struct irq_domain *host,
                              irq_hw_number_t hwirq);

/* Створення відображення на основі структури irq_fwspec */
unsigned int irq_create_fwspec_mapping(struct irq_fwspec *fwspec);

/* Звільнення віртуального номера та видалення зв'язку з таблиці revmap */
void irq_dispose_mapping(unsigned int virq);
```

- **`irq_create_mapping(host, hwirq)`**:
  - **Контракт:** Перевіряє, чи існує вже відображення для даного `hwirq`. Якщо знайдено — повертає існуючий `virq`. Якщо ні — виділяє новий дескриптор `struct irq_desc`, асоціює з ним номер `virq`, викликає метод `host->ops->map(host, virq, hwirq)`, зберігає зв'язок у таблиці зворотного пошуку та інкрементує `host->mapcount`.
  - **Контекст:** Процесний контекст. Заборонено викликати з hardirq / softirq.
  - **Повертає:** Призначений віртуальний номер `virq` або `0` у разі нестачі пам'яті чи помилки методу `map()`.
- **`irq_find_mapping(host, hwirq)`**:
  - **Контракт:** Здійснює пряме читання з масиву `linear_revmap` або безблокувальний пошук під `rcu_read_lock()` у структурі `revmap_xarray`.
  - **Контекст:** Атомарний жорсткий контекст переривання (*hardirq context*). Метод не захоплює сплячих блокувань і не виділяє пам'ять.
  - **Повертає:** Знайдений віртуальний номер `virq` або `0`, якщо для даного `hwirq` відображення не створено.
- **`irq_dispose_mapping(virq)`**:
  - **Контракт:** Викликає `ops->unmap()`, видаляє асоціацію з таблиць `linear_revmap` / `revmap_tree`, звільняє віртуальний дескриптор і повертає `virq` у пул вільних номерів ядра.

### Допоміжні функції налаштування дескрипторів та ієрархій

```c
/* Призначення chip та обробника потоку */
void irq_set_chip_and_handler(unsigned int irq,
                              const struct irq_chip *chip,
                              irq_flow_handler_t handle);

/* Призначення chip, обробника потоку та текстової назви */
void irq_set_chip_and_handler_name(unsigned int irq,
                                   const struct irq_chip *chip,
                                   irq_flow_handler_t handle,
                                   const char *name);

/* Збереження приватного покажчика драйвера в irq_data */
int irq_set_chip_data(unsigned int irq, void *data);

/* Отримання приватного покажчика */
void *irq_get_chip_data(unsigned int irq);

/* Встановлення приватних даних для flow-handler */
int irq_set_handler_data(unsigned int irq, void *data);

/* Отримання приватних даних flow-handler */
void *irq_get_handler_data(unsigned int irq);

/* Комплексна ініціалізація дескриптора в ієрархічному домені */
int irq_domain_set_info(struct irq_domain *domain, unsigned int virq,
                        irq_hw_number_t hwirq, const struct irq_chip *chip,
                        void *chip_data, irq_flow_handler_t handler,
                        void *handler_data, const char *handler_name);

/* Встановлення апаратного номера та чіпа для конкретного рівня ієрархії */
int irq_domain_set_hwirq_and_chip(struct irq_domain *domain, unsigned int virq,
                                  irq_hw_number_t hwirq,
                                  const struct irq_chip *chip,
                                  void *chip_data);

/* Каскадні виклики виділення та звільнення до батьківського домену */
int irq_domain_alloc_irqs_parent(struct irq_domain *domain,
                                 unsigned int irq_base,
                                 unsigned int nr_irqs, void *arg);
void irq_domain_free_irqs_parent(struct irq_domain *domain,
                                 unsigned int irq_base,
                                 unsigned int nr_irqs);

/* Делегування стандартних операцій батьківському irq_chip в ієрархіях */
void irq_chip_ack_parent(struct irq_data *data);
void irq_chip_mask_parent(struct irq_data *data);
void irq_chip_unmask_parent(struct irq_data *data);
void irq_chip_eoi_parent(struct irq_data *data);
int irq_chip_set_affinity_parent(struct irq_data *data,
                                 const struct cpumask *dest, bool force);
int irq_chip_set_type_parent(struct irq_data *data, unsigned int type);
int irq_chip_set_wake_parent(struct irq_data *data, unsigned int on);
```

---

## 5. Домени переривань на основі повідомлень (MSI та MSI-X)

Переривання на основі повідомлень (*Message Signaled Interrupts*) передаються периферійними пристроями шляхом виконання транзакції прямого запису в пам'ять (*DMA / PCIe Memory Write Transaction*) за фіксованою фізичною адресою із заданим корисним навантаженням. Підсистема MSI доменів ядра Linux інкапсулює створення ієрархій доменів, формування адресних пакетів та програмування апаратних дескрипторів векторів.

```
+-------------------------------------------------------------------------------+
|             Ієрархія MSI-доменів для шини PCI Express (ARM / x86)             |
+-------------------------------------------------------------------------------+
| [Кінцевий пристрій PCIe] (наприклад, NVMe Controller, bus_token: PCI_MSI)     |
|   |  - Виділяє nvec векторів: pci_alloc_irq_vectors()                         |
|   v                                                                           |
| [PCI-MSI Domain] (irq_chip: pci_msi_irq_chip, ops: pci_msi_domain_ops)        |
|   |  - Транслює запит у формат MSI-дескрипторів                               |
|   v                                                                           |
| [Interrupt Remapping / ITS Domain] (GIC-ITS / Intel DMAR IRTE)                |
|   |  - Виділяє DeviceID / EventID / ITT та формує фізичну адресу MMIO         |
|   v                                                                           |
| [Батьківський контролер переривань] (ARM GICv3 Distributor / Local APIC)      |
+-------------------------------------------------------------------------------+
```

### Структура повідомлення MSI: struct msi_msg

Структура `struct msi_msg` (визначена в `<linux/msi.h>`) описує пакет транзакції запису, що фізично програмується в регістри кінцевого периферійного пристрою:

```c
#include <linux/msi.h>

struct msi_msg {
    u32 address_lo; /* Нижні 32 біти цільової фізичної адреси запису */
    u32 address_hi; /* Верхні 32 біти цільової фізичної адреси запису */
    u32 data;       /* 32-бітний корисний вантаж (Payload / Вектор) */
};
```

#### Специфікація полів та архітектурне кодування `struct msi_msg`

1. **`address_lo` та `address_hi` (Цільова адреса повідомлення — Message Address):**
   - **Архітектура x86 / x86-64 (Local APIC / IO-APIC):**
     - `address_hi = 0;`
     - `address_lo = 0xFEE00000 | (dest_id << 12) | (redirection_hint << 3) | (destination_mode << 2);`
     - Базова адреса `0xFEE00000` перехоплюється системним агентом процесора як внутрішній цикл переривання APIC. Поле `dest_id` вказує APIC ID цільового логічного процесора.
   - **Архітектура ARM / ARM64 (GICv3 / GICv4 ITS — Interrupt Translation Service):**
     - `address_hi = upper_32_bits(its_translater_phys_addr);`
     - `address_lo = lower_32_bits(its_translater_phys_addr);`
     - Адреса вказує на регістр запису трансляції `GITS_TRANSLATER` (фізична MMIO адреса блоку ITS).
   - **Архітектура RISC-V (AIA — Advanced Interrupt Architecture / IMSIC):**
     - `address_hi / address_lo` вказують на фізичну адресу регістра `setipnum` відповідного HART interrupt file.

2. **`data` (Корисне навантаження повідомлення — Message Data Payload):**
   - **Архітектура x86:**
     - `data = (trigger_mode << 15) | (level << 14) | (delivery_mode << 8) | (vector & 0xFF);`
     - Містить номер вектора процесора (0..255), режим доставки (Fixed, Lowest Priority, NMI) та тип тригера.
   - **Архітектура ARM GIC-ITS:**
     - `data = event_id;`
     - 32-бітний унікальний ідентифікатор події пристрою (*Event ID*). Блок ITS використовує кортеж `(DeviceID, EventID)` для пошуку у внутрішніх таблицях трансляції (*ITT — Interrupt Translation Table*) та визначення кінцевого номера LPI (*Locality-specific Peripheral Interrupt*).

### Дескриптор повідомлення переривання: struct msi_desc

Кожен виділений вектор MSI/MSI-X представляється в ядрі дескриптором `struct msi_desc`, зв'язаним зі списком пристрою `dev->msi.data`:

```c
#include <linux/msi.h>

struct msi_desc {
    /* Навігація у списку дескрипторів пристрою */
    struct list_head        list;
    unsigned int            irq;        /* Призначений віртуальний virq */
    unsigned int            nvec_used;  /* Кількість виділених векторів */
    struct device           *dev;       /* Покажчик на периферійний пристрій */
    struct msi_msg          msg;        /* Кешований пакет повідомлення */
    struct irq_affinity_desc *affinity; /* Бажана процесорна спорідненість */

    /* Прапорці атрибутів дескриптора */
    struct {
        u8 is_msix      : 1; /* 1 = MSI-X, 0 = стандартний MSI */
        u8 is_64        : 1; /* Підтримка 64-бітної адреси повідомлення */
        u8 can_mask     : 1; /* Підтримка апаратного маскування вектором */
        u8 is_virtual   : 1; /* Віртуальний MSI (емульований гіпервізором) */
        u16 entry_nr;        /* Індекс запису в таблиці MSI-X BAR */
        unsigned int default_irq; /* Базовий IRQ пристрою */
    } msi_attrib;
};
```

### Конфігурація та операції MSI-домену: struct msi_domain_info

Драйвер контролера (наприклад, ITS, DMAR або платформний блок MSI) налаштовує параметри домену за допомогою структури `struct msi_domain_info` та таблиці операцій `struct msi_domain_ops`:

```c
#include <linux/msi.h>

struct msi_domain_info {
    unsigned int            flags;
    const struct msi_domain_ops *ops;
    struct irq_chip         *chip;
    irq_flow_handler_t      handler;
    const char              *handler_name;
    void                    *data;
};

struct msi_domain_ops {
    int  (*msi_init)(struct irq_domain *domain, struct msi_domain_info *info,
                     unsigned int virq, irq_hw_number_t hwirq,
                     msi_alloc_info_t *arg);
    void (*msi_free)(struct irq_domain *domain, struct msi_domain_info *info,
                     unsigned int virq);
    int  (*msi_check)(struct irq_domain *domain, struct msi_domain_info *info,
                      struct device *dev);
    int  (*msi_prepare)(struct irq_domain *domain, struct device *dev,
                        int nvec, msi_alloc_info_t *arg);
    void (*set_desc)(msi_alloc_info_t *arg, struct msi_desc *desc);
    int  (*domain_alloc_irqs)(struct irq_domain *domain, struct device *dev,
                              int nvec);
    void (*domain_free_irqs)(struct irq_domain *domain, struct device *dev);
};
```

#### Бітові прапорці конфігурації MSI-домену (`flags`)

```c
#define MSI_FLAG_USE_DEF_DOM_OPS    (1 << 0)
#define MSI_FLAG_USE_DEF_CHIP_OPS   (1 << 1)
#define MSI_FLAG_PCI_MSIX           (1 << 2)
#define MSI_FLAG_MULTI_PCI_MSI      (1 << 3)
#define MSI_FLAG_ACTIVATE_EARLY     (1 << 4)
#define MSI_FLAG_MUST_REACTIVATE    (1 << 5)
#define MSI_FLAG_DEV_SYSFS          (1 << 6)
#define MSI_FLAG_LEVEL_CAPABLE      (1 << 7)
```

- **`MSI_FLAG_USE_DEF_DOM_OPS`**: Вимагає від ядра підставити стандартну таблицю операцій за замовчуванням `msi_domain_ops_default` для незаповнених функціональних покажчиків.
- **`MSI_FLAG_USE_DEF_CHIP_OPS`**: Автоматично призначає стандартні методи маскування/демаскування `pci_msi_mask_irq` та `pci_msi_unmask_irq` у структурі `struct irq_chip`.
- **`MSI_FLAG_PCI_MSIX`**: Дозволяє домену обслуговувати таблиці векторів PCI MSI-X.
- **`MSI_FLAG_MULTI_PCI_MSI`**: Дозволяє виділення кількох суміжних векторів для класичного PCI MSI (ступені двійки: 1, 2, 4, 8, 16, 32).
- **`MSI_FLAG_ACTIVATE_EARLY`**: Програмує апаратні маршрути MSI на ранньому етапі виділення дескрипторів до фактичного виклику `request_irq()`.

### Функції створення доменів та виділення MSI векторів

```c
#include <linux/msi.h>
#include <linux/pci.h>

/* Створення PCI-MSI домену поверх батьківського ієрархічного домену */
struct irq_domain *pci_msi_create_irq_domain(struct fwnode_handle *fwnode,
                                             struct msi_domain_info *info,
                                             struct irq_domain *parent);

/* Створення універсального платформного MSI домену */
struct irq_domain *platform_msi_create_irq_domain(struct fwnode_handle *fwnode,
                                                  struct msi_domain_info *info,
                                                  struct irq_domain *parent);

/* Виділення діапазону векторів MSI для кінцевого пристрою */
int msi_domain_alloc_irqs(struct irq_domain *domain,
                          struct device *dev,
                          int nvec);

/* Звільнення всіх векторів MSI даного пристрою */
void msi_domain_free_irqs(struct irq_domain *domain,
                          struct device *dev);

/* Отримання кешованої копії msi_msg для заданого virq */
void get_cached_msi_msg(unsigned int irq, struct msi_msg *msg);

/* Безпосередній запис повідомлення в конфігураційні регістри пристрою */
void pci_write_msi_msg(unsigned int irq, struct msi_msg *msg);
```

#### Покроковий контракт виклику `pci_msi_create_irq_domain()`
1. Створює новий ієрархічний домен переривань із шинним токеном `DOMAIN_BUS_PCI_MSI`.
2. Прив'язує переданий `parent` (наприклад, ITS domain) як джерело апаратних векторів.
3. Встановлює внутрішні операції трансляції `pci_msi_domain_ops`, які транслюють структуру `pci_dev` у виклики виділення батьківського домену.

#### Драйверний інтерфейс виділення MSI/MSI-X у периферійних пристроях
Драйвери PCI-пристроїв (наприклад, мережеві адаптери або контролери NVMe) не викликають `msi_domain_alloc_irqs()` напряму, а використовують високорівневий інтерфейс ядра:

```c
/* Виділення від min_vecs до max_vecs векторів MSI або MSI-X */
int pci_alloc_irq_vectors(struct pci_dev *dev,
                          unsigned int min_vecs,
                          unsigned int max_vecs,
                          unsigned int flags);

/* Отримання віртуального номера ядра virq для вектора з індексом msi_index */
int pci_irq_vector(struct pci_dev *dev, unsigned int msi_index);

/* Звільнення виділених векторів під час від'єднання драйвера */
void pci_free_irq_vectors(struct pci_dev *dev);
```

Параметр `flags` у `pci_alloc_irq_vectors()` комбінує біти `PCI_IRQ_MSIX`, `PCI_IRQ_MSI`, `PCI_IRQ_LEGACY`, `PCI_IRQ_AFFINITY`. Ядро автоматично намагається виділити MSI-X; у разі відмови — класичний MSI; у разі повної відсутності підтримки повідомлень — повертається до спільної лінії INTx.

---

## 6. Каскадні переривання та демультиплексування (Chained Handlers vs Nested IRQ)

Коли вторинний контролер (розширювач ліній GPIO, FPGA, контролер переривань периферійного моста) підключений до процесора через одну спільну батьківську лінію переривання, ядро повинно перехопити сигнал батьківського дескриптора, з'ясувати стан вторинних входів і диспетчеризувати виклики кінцевих драйверів.

```
+-------------------------------------------------------------------------------+
|                      Моделі вторинної диспетчеризації                         |
+---------------------------------------+---------------------------------------+
|  Chained IRQ Handler (MMIO / FPGA)    |  Nested Threaded IRQ (I2C / SPI)      |
+---------------------------------------+---------------------------------------+
| - Регістри в адресному просторі MMIO   | - Регістри за повільною шиною I2C/SPI |
| - Контекст: HardIRQ (атомарний)       | - Контекст: Потік ядра (Threaded)     |
| - Точка входу:                        | - Точка входу:                        |
|   irq_set_chained_handler_and_data()  |   request_threaded_irq()              |
| - Диспетчеризація:                    | - Диспетчеризація:                    |
|   generic_handle_domain_irq()         |   handle_nested_irq()                 |
| - Заборонено засинати або блокуватись | - Дозволено засинати й виконувати I/O |
+---------------------------------------+---------------------------------------+
```

### Специфікація ланцюгового обробника: irq_set_chained_handler_and_data

Функція `irq_set_chained_handler_and_data()` налаштовує батьківський дескриптор переривання на виконання функції демультиплексора:

```c
#include <linux/irq.h>

void irq_set_chained_handler_and_data(unsigned int irq,
                                      irq_flow_handler_t handle,
                                      void *data);
```

- **Параметри:**
  - `irq`: віртуальний номер батьківського переривання `parent_virq` (отриманий з Device Tree або шини).
  - `handle`: функція демультиплексора з сигнатурою `void (*irq_flow_handler_t)(struct irq_desc *desc)`.
  - `data`: приватний покажчик на контекст драйвера вторинного контролера.
- **Внутрішній контракт ядра:**
  1. Захоплює `raw_spin_lock_irqsave(&desc->lock, flags)`.
  2. Замінює диспетчер потоку `desc->handle_irq = handle`.
  3. Зберігає покажчик у `desc->irq_common_data.handler_data = data`.
  4. Встановлює прапорці дескриптора `IRQ_NOTHREAD | IRQ_NOPROBE | IRQ_NOAUTOEN`, що унеможливлює випадкову реєстрацію драйверів через `request_irq()` на цій батьківській лінії.
  5. Автоматично викликає `irq_startup()` / `irq_unmask()` для відкриття фізичного проходження сигналу.

### Бар'єри батьківського контролера: chained_irq_enter() та chained_irq_exit()

Функція демультиплексора зобов'язана огортати цикл опитування статусних регістрів викликами макросів захисту батьківської лінії:

```c
#include <linux/irqchip/chained_irq.h>

void chained_irq_enter(struct irq_chip *chip, struct irq_desc *desc);
void chained_irq_exit(struct irq_chip *chip, struct irq_desc *desc);
```

- **`chained_irq_enter(chip, desc)`**: Якщо батьківський чіп не підтримує автоматичне апаратне маскування або чергу пріоритетів EOI, метод викликає `chip->irq_mask_ack()` для запобігання паразитному рекурсивному збудженню hardirq під час читання повільних регістрів MMIO.
- **`chained_irq_exit(chip, desc)`**: Надсилає сигнал завершення `chip->irq_eoi()` або відновлює маску `chip->irq_unmask()`.

### Точки диспетчеризації: generic_handle_domain_irq() проти generic_handle_irq()

```c
#include <linux/irqdesc.h>

/* Диспетчеризація за апаратним номером hwirq всередині домену (O(1) lookup + ISR) */
int generic_handle_domain_irq(struct irq_domain *domain, unsigned int hwirq);

/* Диспетчеризація за готовим віртуальним номером virq */
int generic_handle_irq(unsigned int irq);
```

- **`generic_handle_domain_irq(domain, hwirq)`**:
  - **Контракт:**
    1. Виконує швидкий безблокувальний пошук дескриптора `virq = irq_find_mapping(domain, hwirq)`.
    2. Якщо `virq == 0` (немає зареєстрованого обробника), повертає `-EINVAL`.
    3. Знаходить `struct irq_desc` та передає керування призначеному диспетчеру потоку лінії (`desc->handle_irq(desc)`).
    4. Повертає `0` при успішному виклику.
  - **Контекст:** HardIRQ (атомарний). Заборонено засинати.
  - **Перевага:** Усуває потребу у проміжному збереженні масивів `virq` у драйвері контролера, повністю спираючись на `linear_revmap` домену.

- **`handle_nested_irq(virq)` (Для контролерів I2C/SPI):**
  - **Сигнатура:** `void handle_nested_irq(unsigned int irq);`
  - **Контракт:** Викликається виключно всередині потоку ядра (*Thread Context*). Знаходить зареєстровані дії `action` дескриптора і синхронно викликає потокову дію `action->thread_fn(action->irq, action->dev_id)` без захоплення hardirq-спінлоків.

### Канонічний патерн демультиплексора MMIO/FPGA

```c
static void my_gpio_irq_handler(struct irq_desc *desc)
{
    struct my_gpio_chip *chip = irq_desc_get_handler_data(desc);
    struct irq_chip *parent_chip = irq_desc_get_chip(desc);
    unsigned long pending;
    int hwirq;

    chained_irq_enter(parent_chip, desc);

    /* Читання регістра активних немаскованих переривань */
    pending = readl_relaxed(chip->base + GPIO_INT_STATUS) &
              readl_relaxed(chip->base + GPIO_INT_ENABLE);

    /* Ітерація по всіх виставлених бітах у 32-бітному слові */
    for_each_set_bit(hwirq, &pending, chip->num_lines) {
        generic_handle_domain_irq(chip->domain, hwirq);
    }

    chained_irq_exit(parent_chip, desc);
}
```

---

## 7. Стандартні диспетчери потоку обробки (Generic IRQ Flow Handlers)

Коли центральний процесор отримує сигнал переривання і викликає точку входу `generic_handle_irq()` або `generic_handle_domain_irq()`, ядро знаходить дескриптор `struct irq_desc` та передає керування призначеному диспетчеру потоку (`desc->handle_irq`).

Сигнатура диспетчера потоку:
```c
typedef void (*irq_flow_handler_t)(struct irq_desc *desc);
```

```
                  +-----------------------------------+
                  |  Апаратний сигнал переривання     |
                  +-----------------+-----------------+
                                    |
            +-----------------------+-----------------------+
            |                       |                       |
            v                       v                       v
   [handle_level_irq]      [handle_edge_irq]      [handle_fasteoi_irq]
   1. mask_ack_irq()       1. chip->irq_ack()     1. handle_irq_event()
   2. handle_irq_event()   2. handle_irq_event()  2. chip->irq_eoi()
   3. chip->irq_unmask()      (цикл по PENDING)   
```

### 1. `handle_level_irq` (Переривання за рівнем напруги)
- **Призначення:** Лінії, де сигнал активний доти, доки периферійний пристрій не скине прапорець статусу (активний нуль або логічна одиниця).
- **Послідовність виконання:**
  1. Захоплює спінлок дескриптора: `raw_spin_lock(&desc->lock)`.
  2. Маскує та квитує лінію: `mask_ack_irq(desc)` (викликає `chip->irq_mask()` та `chip->irq_ack()`).
  3. Якщо лінія заблокована (`irqd_irq_disabled(&desc->irq_data)`), завершує обробку.
  4. Виставляє біт `IRQD_IRQ_INPROGRESS`.
  5. Відпускає `raw_spin_unlock(&desc->lock)`.
  6. Запускає зареєстровані дії драйверів через `handle_irq_event(desc)`.
  7. Захоплює `raw_spin_lock(&desc->lock)`.
  8. Скидає біт `IRQD_IRQ_INPROGRESS`.
  9. Якщо лінію не було вимкнено під час обробки і не активний режим oneshot, демаскує її: `chip->irq_unmask(&desc->irq_data)`.
  10. Відпускає `raw_spin_unlock(&desc->lock)`.
- **Інваріант:** Обов'язкове маскування перед запуском дій усуває «шторм переривань» (*Interrupt Storm*), оскільки активний рівень напруги миттєво знову збудив би CPU.

### 2. `handle_edge_irq` (Переривання за фронтом сигналу)
- **Призначення:** Лінії, що фіксують перепад напруги (короткий імпульс).
- **Послідовність виконання:**
  1. Захоплює спінлок `raw_spin_lock(&desc->lock)`.
  2. Негайно квитує контролер: `chip->irq_ack(&desc->irq_data)`.
  3. Якщо обробка вже триває на іншому CPU (`IRQD_IRQ_INPROGRESS`), виставляє прапорець `desc->istate |= IRQS_PENDING` і виходить.
  4. Виставляє `IRQD_IRQ_INPROGRESS`.
  5. Виконує цикл:
     ```c
     do {
         if (unlikely(irqd_irq_disabled(&desc->irq_data))) {
             mask_ack_irq(desc);
             break;
         }
         desc->istate &= ~IRQS_PENDING;
         raw_spin_unlock(&desc->lock);
         handle_irq_event(desc);
         raw_spin_lock(&desc->lock);
     } while ((desc->istate & IRQS_PENDING) && !irqd_irq_disabled(&desc->irq_data));
     ```
  6. Скидає `IRQD_IRQ_INPROGRESS` та відпускає `raw_spin_unlock(&desc->lock)`.
- **Інваріант:** Лінія не маскується на час роботи ISR, щоб не пропустити повторні імпульси під час виконання обробника.

### 3. `handle_fasteoi_irq` (Контролери з апаратною чергою EOI)
- **Призначення:** Сучасні контролери (ARM GIC, Intel APIC, PCIe MSI).
- **Послідовність виконання:**
  1. Захоплює `raw_spin_lock(&desc->lock)`.
  2. Виставляє `IRQD_IRQ_INPROGRESS`.
  3. Відпускає спінлок `raw_spin_unlock(&desc->lock)`.
  4. Запускає `handle_irq_event(desc)`.
  5. Захоплює `raw_spin_lock(&desc->lock)`.
  6. Скидає `IRQD_IRQ_INPROGRESS`.
  7. Надсилає сигнал завершення: `chip->irq_eoi(&desc->irq_data)`.
  8. Відпускає `raw_spin_unlock(&desc->lock)`.
- **Перевага:** Найшвидший тракт обробки без додаткових записів у регістри маскування.

### 4. `handle_simple_irq` (Прості некеровані переривання)
- **Призначення:** Мультиплексори та віртуальні лінії без апаратних регістрів маскування.
- **Послідовність:** Захоплює `desc->lock`, викликає `handle_irq_event(desc)` і відпускає блокування.

### 5. `handle_nested_irq` (Вкладені потокові переривання)
- **Призначення:** Контролери на повільних шинах I2C/SPI (розширювачі портів GPIO).
- **Контекст виконання:** Викликається виключно з контексту потоку ядра (*Thread Context*) первинного обробника батьківського контролера.
- **Послідовність:** Знаходить дескриптор `struct irq_desc` за номером `virq` і синхронно викликає потокову дію `action->thread_fn(action->irq, action->dev_id)` у поточному потоці ядра без створення або пробудження додаткових ниток.

### 6. `handle_percpu_irq` та `handle_percpu_devid_irq`
- **Призначення:** Локальні процесорні переривання (таймери CPU, PMU, IPI).
- **Особливість:** Працюють без захоплення глобального `desc->lock`, оскільки лінія апаратно ізольована для кожного конкретного CPU. У версії `devid` як параметр обробника передається вказівник на per-CPU структуру `__percpu *dev_id`.

### 7. `handle_bad_irq` (Обробка паразитних сигналів)
- **Призначення:** Резервний обробник для незареєстрованих, помилкових або паразитних (*Spurious*) переривань. Інкрементує лічильник `/proc/interrupts` `spurious` та квитує контролер через `ack_bad_irq()`.

---

## 8. Повний життєвий цикл переривання: від апаратного імпульсу до softirq та threaded handler

Життєвий цикл обробки сигналу переривання в ядрі Linux проходить крізь вісім чітко розмежованих стадій: від генерації електричного сигналу на фізичній шині до виконання фонових потоків ядра та захисту від штормів переривань.

```
+-----------------------------------------------------------------------------------+
|               Повний тракт виконання переривання в ядрі Linux                     |
+-----------------------------------------------------------------------------------+
|  [Апаратний рівень] Фізична лінія (Edge/Level) або PCIe TLP MSI Write            |
|       |                                                                           |
|       v                                                                           |
|  [Контролер IRQ] Арбітраж пріоритетів (GIC Distributor / APIC) -> Сигнал на CPU   |
|       |                                                                           |
|       v                                                                           |
|  [Вектор архітектури] el1_irq / common_interrupt -> Збереження pt_regs            |
|       |                                             Перемикання на IRQ Stack      |
|       v                                             irq_enter() (HARDIRQ_OFFSET)  |
|  [Generic IRQ] handle_domain_irq() -> irq_find_mapping(hwirq) -> irq_desc         |
|       |                                                                           |
|       v                                                                           |
|  [Flow Handler] handle_fasteoi_irq / handle_level_irq / handle_edge_irq           |
|       |         - Синхронізація desc->lock, маскування / EOI                      |
|       v                                                                           |
|  [Top-Half ISR] handle_irq_event() -> action->handler(irq, dev_id)                |
|       |                                                                           |
|       +-----------------------------------+-----------------------------------+   |
|       |                                   |                                   |   |
|       v (raise_softirq / napi)            v (IRQ_WAKE_THREAD)                 v   |
|  [irq_exit()]                             [Потік kthread]               IRQ_HANDLED
|  - Скидання HARDIRQ_OFFSET                - wake_up_process(action->thread)   (кінець)
|  - invoke_softirq() -> __do_softirq()     - irq/NN-name (SCHED_FIFO, prio 50)     |
|  - Виконання NET_RX / TIMER / RCU         - action->thread_fn()                   |
|  - Ліміт budget: перехід у ksoftirqd/N    - irq_finalize_oneshot() (unmask)       |
+-----------------------------------------------------------------------------------+
```

### Покроковий механізм обробки переривання

#### 1. Апаратна сигналізація та арбітраж контролера
- Фізичний периферійний пристрій змінює рівень напруги на виділеній лінії або ініціює прямий запис у системну пам'ять (*PCIe TLP Memory Write*).
- Контролер переривань (ARM GIC Distributor/ITS, Intel IO-APIC, RISC-V PLIC/APLIC) фіксує подію, перевіряє поточну маску пріоритетів та надсилає апаратний сигнал на відповідне ядро CPU через шину між'ядерного сполучення.

#### 2. Архітектурний вектор винятку та перемикання стеків
- Процесорне ядро призупиняє виконання поточного потоку інструкцій і переходить на фіксовану адресу вектора переривань (наприклад, `el1_irq` на ARM64 або вектор таблиці IDT `common_interrupt` на x86).
- **Збереження регістрів:** Ядро зберігає регістровий файл процесора у структурі `struct pt_regs` на стеку поточного контексту.
- **Перемикання на стек переривань (*IRQ Stack*):** Для уникнення переповнення стека користувацького процесу або потоку ядра (який за замовчуванням обмежений розміром 8 КБ або 16 КБ), обробник апаратно перемикає покажчик стека `SP` на спеціальний виділений per-CPU стек переривань (`irq_stack_union` на x86_64 або масив `irq_stack` на ARM64).
- **Вхід у контекст переривання (`irq_enter` / `irq_enter_rcu`):**
  - Атомарно збільшує поле `preempt_count` процесора зсувом `HARDIRQ_OFFSET`. Це інформує планувальник про перебування в атомарному контексті й забороняє виклик `schedule()`.
  - Викликає `rcu_irq_enter()`, що пробуджує підсистему RCU, якщо ядро перебувало у стані глибокого сну (*nohz / idle*).
  - Зупиняє облік часу виконання активного користувацького завдання та перемикає лічильники на облік часу переривань (*system / irq time*).
- **Апаратне квитування:** На архітектурах ARM64 ядро зчитує системний регістр `ICC_IAR1_EL1` (Interrupt Acknowledge Register), отримуючи апаратний ідентифікатор `hwirq` та переводячи стан переривання в контролері з *Pending* у *Active*.

#### 3. Вхід у Generic IRQ Framework та трансляція номера
- Архітектурний код викликає ядрову точку входу `generic_handle_domain_irq(domain, hwirq)` або `handle_domain_irq()`.
- За допомогою функції `irq_find_mapping(domain, hwirq)` ядро за `O(1)` виконує пошук глобального віртуального номера `virq` у масиві `linear_revmap` домену або RCU-пошук у дереві `XArray`.
- Отримує покажчик на дескриптор лінії: `struct irq_desc *desc = irq_to_desc(virq)`. Якщо дескриптор не знайдено або відображення відсутнє, викликається резервний обробник `handle_bad_irq()`.

#### 4. Виконання диспетчера потоку (Flow Handler)
- Залежно від типу лінії викликається призначений диспетчер `desc->handle_irq(desc)`:
  - **`handle_fasteoi_irq`** (MSI, APIC, GIC): захоплює `raw_spin_lock(&desc->lock)`, виставляє прапорець `IRQD_IRQ_INPROGRESS`, відпускає блокування, викликає `handle_irq_event(desc)`, повторно захоплює блокування, скидає `IRQD_IRQ_INPROGRESS`, надсилає `chip->irq_eoi()` у контролер і відпускає спінлок.
  - **`handle_edge_irq`** (GPIO, ISA): негайно квитує імпульс `chip->irq_ack()`. Якщо попередня обробка на іншому ядрі ще не завершена (`IRQD_IRQ_INPROGRESS`), виставляє біт `desc->istate |= IRQS_PENDING` і виходить. Інакше виконує цикл обробки всіх накопичених подій `IRQS_PENDING`.
  - **`handle_level_irq`** (дротові лінії INTx): викликає `mask_ack_irq(desc)` для негайного маскування активного рівня напруги на вході, виконує `handle_irq_event(desc)` і демаскує лінію `chip->irq_unmask()` на виході (якщо не активовано `IRQF_ONESHOT`).

#### 5. Виконання обробників верхньої половини (Top-Half Processing)
- Функція `handle_irq_event(desc)` викликає внутрішній обробник `__handle_irq_event_percpu(desc)`:
  - Інкрементує локальний лічильник per-CPU статистики `*this_cpu_ptr(desc->kstat_irqs)`.
  - Ітерує по зв'язаному списку дій `struct irqaction *action`:
    - Викликає функцію первинного обробника: `ret = action->handler(action->irq, action->dev_id)`.
    - Якщо `ret == IRQ_HANDLED`: переривання вважається успішно опрацьованим.
    - Якщо `ret == IRQ_NONE`: сигнал не належав цьому обробнику (для спільних ліній `IRQF_SHARED`). Якщо лічильник невирішених подій досягає 100 000 поспіль, спрацьовує евристика захисту від шторму переривань `note_interrupt()`: ядро блокує дефектну лінію через `disable_irq_nosync()` і виводить попередження `nobody cared (irq N)` у системний журнал `dmesg`.
    - Якщо `ret == IRQ_WAKE_THREAD`: ядро викликає `__irq_wake_thread(desc, action)`. Метод встановлює атомарний прапорець `IRQTF_RUNTHREAD` у структурі дії та пробуджує асоційований потік ядра через `wake_up_process(action->thread)`.
  - Якщо всередині ISR драйвер викликав `raise_softirq()` або `napi_schedule()`, ядро атомарно встановлює відповідний біт у per-CPU бітовій масці `local_softirq_pending()`.

#### 6. Вихід із контексту hardirq та ініціалізація softirq
- Після завершення роботи ISR та відновлення попереднього стану контролера викликається функція `irq_exit()` (або `irq_exit_rcu()`):
  - Зменшує значення лічильника `preempt_count` на константу `HARDIRQ_OFFSET`.
  - Виконує перевірку запуску відкладених нижніх половин:
    ```c
    if (!in_interrupt() && local_softirq_pending())
        invoke_softirq();
    ```
  - Макрос `!in_interrupt()` гарантує, що процесор не перебуває всередині вкладеного переривання та що на поточному ядрі зараз не виконується інший екземпляр softirq.
  - Якщо умова виконується, функція `invoke_softirq()` запускає прямий обробник `__do_softirq()`.

#### 7. Виконання нижніх половин: цикл __do_softirq() та делегування ksoftirqd
- Функція `__do_softirq()` виконує накопичену важку роботу (мережевий стек NAPI, таймери, tasklet-и, RCU):
  - Збільшує `preempt_count` на `SOFTIRQ_OFFSET`, блокуючи повторний вхід у softirq на поточному ядрі.
  - **Дозвіл локальних переривань:** Викликає `local_irq_enable()`. Це ключове архітектурне рішення: апаратні переривання (*hardirq*) дозволено виконувати поверх `softirq`, що гарантує низьку латентність прийому наступних сигналів обладнання.
  - Зчитує бітову маску незавершених дій `pending = local_softirq_pending()` та скидає її в пам'яті через `set_softirq_pending(0)`.
  - Почергово викликає обробники векторів `softirq_vec[nr].action(softirq_vec)`:
    - `HI_SOFTIRQ` (пріоритетні тасклети).
    - `TIMER_SOFTIRQ` (класичні таймери ядра `timer_list`).
    - `NET_TX_SOFTIRQ` / `NET_RX_SOFTIRQ` (пакетний стек підсистеми NAPI).
    - `BLOCK_SOFTIRQ` (завершення операцій вводу-виводу блочних пристроїв).
    - `IRQ_POLL_SOFTIRQ` (полінг високонавантажених контролерів NVMe).
    - `TASKLET_SOFTIRQ` (стандартні тасклети драйверів).
    - `SCHED_SOFTIRQ` (балансування планувальника CFS / EEVDF).
    - `HRTIMER_SOFTIRQ` (високоточні таймери).
    - `RCU_SOFTIRQ` (обробка RCU-колбеків).
  - **Захист від монополізації CPU (Latency & Starvation Protection):**
    - Після проходження всіх бітів ядро знову перевіряє `local_softirq_pending()`. Якщо під час роботи обробників нові hardirq виставили додаткові прапорці, ядро повторює цикл.
    - Для запобігання повному зависанню системи та голодуванню користувацьких процесів ядро обмежує час прямої обробки двома константами:
      1. Загальний час перебування в `__do_softirq()` не повинен перевищувати 2 мс (`MAX_SOFTIRQ_TIME = 2 * HZ / 1000`).
      2. Кількість повторних ітерацій циклу не повинна перевищувати 10 (`MAX_SOFTIRQ_RESTART = 10`).
    - Якщо будь-який ліміт вичерпано, ядро зупиняє виконання `__do_softirq()`, викликає `wakeup_softirqd()` для пробудження системного потоку ядра `ksoftirqd/N` (де `N` — номер поточного CPU) і повертає керування. Решта роботи softirq буде виконана у стандартному процесному контексті з плануванням за політикою CFS.
  - Вимикає локальні переривання `local_irq_disable()`, зменшує `preempt_count` на `SOFTIRQ_OFFSET` та повертає покажчик стека з IRQ-стека на стек процесу.

#### 8. Виконання потокових обробників (Threaded IRQ Handler)
- Якщо первинний ISR повернув `IRQ_WAKE_THREAD`, диспетчер планувальника активує потік ядра `irq/NN-devname` (функція `irq_thread()`):
  - Потік має пріоритет реального часу `SCHED_FIFO` зі значенням 50, що забезпечує його запуск раніше будь-яких звичайних користувацьких програм.
  - Потік виконує функцію `action->thread_fn(action->irq, action->dev_id)`. Оскільки це повноцінний процесний контекст, тут дозволено виконувати операції з очікуванням: захоплювати м'ютекси `mutex_lock()`, засинати через `msleep()`, виділяти динамічну пам'ять із прапорцем `GFP_KERNEL` та виконувати повільні I/O транзакції по шинах I2C/SPI.
  - **Фіналізація oneshot-режиму:** Після завершення `thread_fn` потік викликає внутрішню функцію `irq_finalize_oneshot(desc, action)`. Якщо для лінії було активне маскування `IRQF_ONESHOT`, ядро викликає метод `chip->irq_unmask(&desc->irq_data)`, дозволяючи контролеру сигналізувати про нові події.

---

## 9. Керування процесорною спорідненістю (IRQ Affinity) та балансування SMP

У багатопроцесорних системах (*SMP*) продуктивність підсистеми вводу-виводу безпосередньо залежить від коректного розподілу обробки переривань між ядрами CPU. Нерівномірний розподіл призводить до перевантаження окремих процесорів (*CPU 0 Bottleneck*), вимивання процесорного кешу L1/L2 та деградації пропускної здатності на шинах зв'язку NUMA-вузлів.

### C-інтерфейс ядра для керування спорідненістю

```c
#include <linux/interrupt.h>

/* Встановлення маски дозволених ядер (фільтрується за cpu_online_mask) */
int irq_set_affinity(unsigned int irq, const struct cpumask *cpumask);

/* Примусове встановлення маски (використовується ядром під час hotplug) */
int irq_force_affinity(unsigned int irq, const struct cpumask *cpumask);

/* Встановлення підказки спорідненості для простору користувача (affinity_hint) */
int irq_set_affinity_hint(unsigned int irq, const struct cpumask *m);

/* Оновлення підказки спорідненості */
int irq_update_affinity_hint(unsigned int irq, const struct cpumask *m);

/* Одночасне встановлення маски та підказки */
int irq_set_affinity_and_hint(unsigned int irq, const struct cpumask *m);

/* Реєстрація нотифікатора сповіщення про зміну спорідненості */
int irq_set_affinity_notifier(unsigned int irq,
                              struct irq_affinity_notify *notify);

/* Автоматичне конструювання масок для векторів багаточергового пристрою */
struct cpumask *irq_create_affinity_masks(unsigned int nvecs,
                                          struct irq_affinity *affd);
```

#### Контракти функцій та правила синхронізації

- **`irq_set_affinity(irq, cpumask)`**:
  - **Контракт:** Перевіряє перетин переданої маски `cpumask` із маскою активних ядер `cpu_online_mask`. Захоплює `raw_spin_lock_irqsave(&desc->lock, flags)` і викликає низькорівневий метод `chip->irq_set_affinity()`.
  - **Повертає:** `0` при успіху, `-EINVAL` якщо в масці немає жодного активного ядра, або `-ENOSYS`, якщо контролер не підтримує маршрутизацію.
  - **Контекст:** Процесний або атомарний контекст.

- **`irq_set_affinity_hint(irq, cpumask)`**:
  - **Контракт:** Зберігає вказівник на `cpumask` у полі `desc->affinity_hint`. Ця маска транслюється у файл `/proc/irq/[N]/affinity_hint` і слугує рекомендацією для демона `irqbalance`, але **не змінює апаратні регістри контролера автоматично**.
  - **Використання в драйверах:** Драйвери високошвидкісних мережевих карт (наприклад, `mlx5`, `ixgbe`) передають сюди маску ядер, локальних для NUMA-вузла PCIe-слота.

- **`irq_create_affinity_masks(nvecs, affd)`**:
  - **Контракт:** Виділяє масив структур `struct cpumask`, автоматично рівномірно розподіляючи `nvecs` векторів пристрою (наприклад, черг NVMe або RX/TX кілець NIC) між усіма доступними онлайн-ядрами з урахуванням топології сокетів та спільних кешів L3.

### Архітектурні моделі та апаратні обмеження

#### 1. Архітектура x86 (Local APIC / IO-APIC / MSI)
- **Режими адресації:**
  - *Physical Destination Mode:* Вектор програмується на конкретний APIC ID фізичного процесорного потоку.
  - *Logical Destination Mode (Flat / Cluster):* Дозволяє адресувати групу ядер. У режимі *x2APIC* застосовується кластерна схема: верхні 16 бітів визначають номер кластера (*Cluster ID*), а нижні 16 бітів — бітову маску ядер у межах кластера.
- **Інваріант `IRQD_SINGLE_TARGET`:**
  - На архітектурі x86 кожен апаратний вектор переривання фізично доставляється лише на **одне процесорне ядро за раз**.
  - Навіть якщо адміністратор записує маску `0xff` у `/proc/irq/[N]/smp_affinity`, ядро призначає переривання одному ядру з цієї маски. Фактичне активне ядро відображається у файлі `/proc/irq/[N]/effective_affinity`.
- **Відкладена міграція вектору (*Vector Migration in Interrupt Context*):**
  - При перенаправленні лінії на інше ядро процесор не може миттєво перемкнути маршрут, якщо переривання активне. Ядро x86 виділяє новий вектор на цільовому CPU, зберігаючи старий вектор у стані очікування (*Pending Migration*), і завершує видалення старого відображення лише після отримання сигналу EOI від попереднього спрацьовування.

#### 2. Архітектура ARM (GICv2 / GICv3 / GICv4)
- **GICv2:** Регістри `GICD_ITARGETSR<n>` використовують 8-бітне бітове поле для кожного SPI-переривання (кожен біт відповідає процесорному інтерфейсу CPU0..CPU7).
- **GICv3 / GICv4 (Affinity Routing):** Регістри `GICD_IROUTER<n>` кодують повну ієрархічну адресу ядра у форматі `Aff3.Aff2.Aff1.Aff0` (64 біти):
  - Поле `Interrupt_Routing_Mode = 0`: переривання маршрутизується строго на вказане ядро (*Specific Target PE*).
  - Поле `Interrupt_Routing_Mode = 1`: режим 1-of-N (переривання надсилається будь-якому доступному процесорному елементу кластера, який не зайнятий виконанням високопріоритетного коду).

#### 3. Міграція під час відключення процесора (CPU Hotplug)
- Коли ядро CPU виводиться з експлуатації (`echo 0 > /sys/devices/system/cpu/cpuX/online`), підсистема hotplug викликає внутрішню функцію `migrate_one_irq(desc)`:
  1. Перевіряє, чи входить відключене ядро в поточну маску спорідненості `irq_data->common->affinity`.
  2. Якщо це ядро було єдиним у масці, ядро знаходить перше доступне ядро з `cpu_online_mask`.
  3. Викликає `chip->irq_set_affinity(data, new_mask, true)` із прапорцем `force = true`.
  4. Оновлює системні дескриптори та перепрограмує апаратні маршрути контролера.

### Демон балансування переривань простору користувача (irqbalance)

Утиліта `irqbalance` працює у просторі користувача як системний сервіс, періодично (кожні 10 секунд за замовчуванням) аналізуючи завантаження системи та модифікуючи маски `/proc/irq/[N]/smp_affinity`.

```
+-------------------------------------------------------------------------------+
|                    Ієрархія топології в дереві irqbalance                     |
+-------------------------------------------------------------------------------+
|  [NUMA Node 0]                                 [NUMA Node 1]                  |
|     |                                             |                           |
|     +--> [Socket / Package 0]                     +--> [Socket / Package 1]   |
|             |                                             |                   |
|             +--> [Cache Domain (L3 / LLC)]                +--> [Cache Domain] |
|                     |                                             |           |
|                     +--> [Core 0]    [Core 1]                     +--> [Core] |
|                             |            |                                    |
|                             +-> SMT 0    +-> SMT 2                            |
|                             +-> SMT 1    +-> SMT 3                            |
+-------------------------------------------------------------------------------+
```

#### Класифікація класів переривань у irqbalance

| Клас переривання | Типові джерела | Стратегія розміщення |
| :--- | :--- | :--- |
| **`IRQ_TYPE_LEGACY`** | Таймер 8254, клавіатура i8042, RTC (IRQ 0..15) | Жорстко закріплюються за CPU 0 для мінімізації накладних витрат. |
| **`IRQ_TYPE_STORAGE`** | AHCI SATA, SAS HBA, NVMe контролери | Розподіляються між різними кеш-доменами для уникнення конкуренції за шину пам'яті. |
| **`IRQ_TYPE_NETWORKING`** | Черги RX/TX мережевих карт Ethernet / Wi-Fi | Балансуються по ядрах одного кеш-домену з прив'язкою до NUMA-вузла мережевого адаптера. |
| **`IRQ_TYPE_OTHER`** | USB-хости, аудіокодеки, сенсори I2C/SPI | Спрямовуються на найменш завантажені ядра процесора. |

#### Конфігурація та виключення ядер

Керування поведінкою демона здійснюється через конфігураційний файл `/etc/default/irqbalance` (або `/etc/sysconfig/irqbalance`):

- **`IRQBALANCE_BANNED_CPUS`**: 64-бітна або шістнадцяткова бітова маска ядер, які `irqbalance` **заборонено використовувати** для призначення переривань.
  ```bash
  # Виключити ядра CPU 2 та CPU 3 з балансування (біти 2 і 3 = 0x0C)
  IRQBALANCE_BANNED_CPUS=0000000c
  ```
- **`IRQBALANCE_ARGS="--banirq=<irq>"`**: Повна заборона автоматичного балансування для конкретного віртуального номера переривання.
- **Взаємодія з ізольованими ядрами ядра Linux:** Якщо ядро завантажено з параметрами `isolcpus=2,3` або `nohz_full=2,3`, демон `irqbalance` автоматично зчитує маску `/sys/devices/system/cpu/isolated` та виключає вказані процесори з пулу балансування, захищаючи real-time задачі від затримок обробки hardirq.

#### Інженерні правила тюнінгу у високонавантажених системах

1. **Мережеві адаптери 100GbE+ та сховища NVMe:** Автоматичний демон `irqbalance` рекомендується вимикати (`systemctl stop irqbalance`), оскільки постійна міграція векторів між ядрами призводить до руйнування локальності кешу L1/L2 та втрати пакетів.
2. **Ручне прив'язування векторів черг (Manual Queue Pinning):** Кожну окрему чергу переривання `nvme0qN` або `eth0-TxRx-N` слід статично прив'язувати до одного виділеного фізичного ядра на тому ж NUMA-вузлі:
   ```bash
   # Прив'язати чергу 0 мережевого адаптера до CPU 4
   echo 4 > /proc/irq/42/smp_affinity_list
   ```
3. **Узгодження з RPS/XPS:** Маска `smp_affinity` апаратного переривання черги має збігатися з маскою передачі пакетів `xps_cpus` відповідного мережевого кільця для забезпечення локальності структур сокетів у пам'яті процесора.

---

## 10. Опис переривань у Device Tree та підсистема of_irq / platform_irq

Дерево пристроїв (*Device Tree*) описує апаратну топологію джерел та споживачів сигналів переривань через стандартизовані властивості специфікації Open Firmware.

### Властивості вузлів Device Tree для переривань

| Властивість | Вузол | Тип значення | Опис та семантика |
| :--- | :--- | :--- | :--- |
| `interrupt-controller` | Контролер | Булевий прапорець (порожній) | Оголошує вузол як апаратний контролер або домен переривань. |
| `#interrupt-cells` | Контролер | `u32` (ціле число) | Визначає кількість 32-бітних комірок у специфікаторі переривання (1, 2 або 3). |
| `interrupt-parent` | Споживач / Шина | `phandle` (посилання) | Вказує контролер переривань за замовчуванням для даного вузла або всієї дочірньої гілки. |
| `interrupts` | Споживач | Список комірок `u32` | Масив специфікаторів переривань відповідно до `#interrupt-cells` батьківського контролера. |
| `interrupts-extended` | Споживач | Список пар `<phandle intspec>` | Розширений формат, де кожне переривання має власний `phandle` контролера (дозволяє підключення до різних чіпів). |
| `interrupt-names` | Споживач | Список рядків | Текстові ідентифікатори ліній переривання (наприклад, `"rx"`, `"tx"`, `"wakeup"`). |
| `interrupt-map` | Міст / Nexus | Таблиця кортежів | Матриця маршрутизації та перетворення специфікаторів шини на специфікатори цільового контролера. |
| `interrupt-map-mask` | Міст / Nexus | Бітова маска `u32` | Бітова маска для фільтрації адрес та ліній перед пошуком у таблиці `interrupt-map`. |

### Константи тригерів переривань (`<dt-bindings/interrupt-controller/irq.h>`)

```c
#define IRQ_TYPE_NONE           0
#define IRQ_TYPE_EDGE_RISING    1
#define IRQ_TYPE_EDGE_FALLING   2
#define IRQ_TYPE_EDGE_BOTH      (IRQ_TYPE_EDGE_FALLING | IRQ_TYPE_EDGE_RISING)
#define IRQ_TYPE_LEVEL_HIGH     4
#define IRQ_TYPE_LEVEL_LOW      8
#define IRQ_TYPE_LEVEL_MASK     (IRQ_TYPE_LEVEL_LOW | IRQ_TYPE_LEVEL_HIGH)
#define IRQ_TYPE_SENSE_MASK     0x0000000f
```

### Константи ARM GIC (`<dt-bindings/interrupt-controller/arm-gic.h>`)

Для контролерів ARM GIC специфікатор `#interrupt-cells = <3>` кодує:
1. Тип переривання: `GIC_SPI = 0` (Shared Peripheral Interrupt, базовий зсув hwirq = 32), `GIC_PPI = 1` (Private Peripheral Interrupt, hwirq = 16).
2. Апаратний номер лінії відносно базового типу.
3. Прапорці тригера (`IRQ_TYPE_EDGE_RISING`, `IRQ_TYPE_LEVEL_HIGH` тощо).

### Приклад опису зв'язку контролера та периферії в DTS

```dts
/ {
    /* Первинний контролер ARM GIC */
    gic: interrupt-controller@2c001000 {
        compatible = "arm,gic-400";
        interrupt-controller;
        #interrupt-cells = <3>;
        reg = <0x2c001000 0x1000>, <0x2c002000 0x2000>;
    };

    /* Вторинний контролер GPIO з прямим підключенням до GIC */
    gpio0: gpio@40020000 {
        compatible = "vendor,custom-gpio";
        reg = <0x40020000 0x1000>;
        interrupt-parent = <&gic>;
        interrupts = <GIC_SPI 45 IRQ_TYPE_LEVEL_HIGH>; /* SPI 45 у GIC */

        gpio-controller;
        #gpio-cells = <2>;

        interrupt-controller;
        #interrupt-cells = <2>; /* [0] = пін GPIO (0..31), [1] = прапорці тригера */
    };

    /* Кінцевий периферійний пристрій із двома лініями від різних контролерів */
    sensor@0 {
        compatible = "vendor,sensor-device";
        interrupts-extended = <&gpio0 5 IRQ_TYPE_EDGE_FALLING>,
                              <&gic GIC_SPI 80 IRQ_TYPE_LEVEL_HIGH>;
        interrupt-names = "data_ready", "error_alert";
    };
};
```

### C-інтерфейс ядра для отримання та трансляції переривань з DT

```c
#include <linux/of_irq.h>
#include <linux/platform_device.h>

/* Отримання virq за числовим індексом з вузла Device Tree */
int of_irq_get(struct device_node *np, int index);

/* Отримання virq за текстовим ім'ям з властивості interrupt-names */
int of_irq_get_byname(struct device_node *np, const char *name);

/* Трансляція переривання у структуру struct resource (тип IORESOURCE_IRQ) */
int of_irq_to_resource(struct device_node *np, int index, struct resource *res);

/* Низькорівневий розбір сирого специфікатора переривання */
int of_irq_parse_one(struct device_node *np, int index,
                     struct of_phandle_args *out_irq);

/* Високорівневий інтерфейс для драйверів платформних пристроїв */
int platform_get_irq(struct platform_device *pdev, unsigned int num);
int platform_get_irq_byname(struct platform_device *pdev, const char *name);
int platform_get_irq_optional(struct platform_device *pdev, unsigned int num);
```

- **`platform_get_irq(pdev, num)`**:
  - **Контракт:** Зчитує переривання під індексом `num`, автоматично створює дескриптор та відображення в домені через `irq_create_of_mapping()` і повертає глобальний `virq`.
  - **Коди повернення:** Додатнє число `virq > 0` при успіху, або від'ємний код помилки (`-ENXIO`, `-EINVAL`, `-EPROBE_DEFER`).
  - **`platform_get_irq_optional()`**: Не виводить повідомлення про помилку в лог ядра `dmesg`, якщо переривання відсутнє (використовується для опціональних ліній).

---

## 11. Драйверний інтерфейс реєстрації та керування перериваннями

Периферійні драйвери ядра використовують високорівневий інтерфейс керування лініями (визначений у `<linux/interrupt.h>`):

```c
#include <linux/interrupt.h>

/* Базовий макрос реєстрації (без окремого потоку) */
int request_irq(unsigned int irq,
                irq_handler_t handler,
                unsigned long flags,
                const char *name,
                void *dev);

/* Повний інтерфейс реєстрації з підтримкою потокової обробки (Threaded IRQ) */
int request_threaded_irq(unsigned int irq,
                         irq_handler_t handler,
                         irq_handler_t thread_fn,
                         unsigned long irqflags,
                         const char *devname,
                         void *dev_id);

/* Керована ядром реєстрація з автоматичним звільненням ресурсу */
int devm_request_threaded_irq(struct device *dev,
                              unsigned int irq,
                              irq_handler_t handler,
                              irq_handler_t thread_fn,
                              unsigned long irqflags,
                              const char *devname,
                              void *dev_id);

/* Звільнення обробника переривання */
const void *free_irq(unsigned int irq, void *dev_id);
void devm_free_irq(struct device *dev, unsigned int irq, void *dev_id);

/* Синхронне відключення лінії (чекає завершення активних обробників) */
void disable_irq(unsigned int irq);

/* Асинхронне відключення лінії (безпечно викликати в атомарному контексті) */
void disable_irq_nosync(unsigned int irq);

/* Дозвіл лінії переривання (зменшує лічильник глибини depth) */
void enable_irq(unsigned int irq);

/* Очікування завершення виконання активних hardirq та потоків на всіх CPU */
void synchronize_irq(unsigned int irq);

/* Керування здатністю лінії пробуджувати систему зі стану сну */
int irq_set_irq_wake(unsigned int irq, unsigned int on);
int enable_irq_wake(unsigned int irq);
int disable_irq_wake(unsigned int irq);
```

### Контракт функцій реєстрації

- **`request_threaded_irq()`**:
  - **Параметри:**
    - `irq`: віртуальний номер ядра `virq`.
    - `handler`: первинний обробник верхньої половини (*top-half*), виконується у жорсткому `hardirq`-контексті з вимкненими локальними перериваннями. Повертає:
      - `IRQ_HANDLED`: переривання успішно оброблено, нижня половина не потрібна.
      - `IRQ_NONE`: переривання не належало цьому пристрою (для спільних ліній `IRQF_SHARED`).
      - `IRQ_WAKE_THREAD`: передати керування потоковому обробнику `thread_fn`.
      - Якщо передано `NULL`, ядро підставляє стандартний stub `irq_default_primary_handler()`, який завжди повертає `IRQ_WAKE_THREAD` (вимагає обов'язкового встановлення прапорця `IRQF_ONESHOT`).
    - `thread_fn`: обробник нижньої половини (*bottom-half*), виконується в окремому потоці ядра `irq/NN-devname` із пріоритетом реального часу `SCHED_FIFO` (50). Тут дозволено засинати, захоплювати м'ютекси, викликати транзакції шин I2C/SPI та виділяти пам'ять через `GFP_KERNEL`.
    - `irqflags`: бітова комбінація прапорців `IRQF_*`.
    - `devname`: текстовий рядок назви пристрою для відображення у `/proc/interrupts`.
    - `dev_id`: унікальний cookie-покажчик на екземпляр структури пристрою (обов'язковий для спільних ліній `IRQF_SHARED` та для подальшого звільнення через `free_irq`).
  - **Повертані значення:** `0` при успіху, `-EINVAL` (некоректні параметри або відсутній `dev_id` при `IRQF_SHARED`), `-EBUSY` (конфлікт прапорців конфігурації або зайнята лінія), `-ENOMEM` (нестача пам'яті для виділення `struct irqaction` або створення потоку ядра).
  - **Контекст виконання:** Процесний контекст (може засинати).

- **`devm_request_threaded_irq()`**:
  - **Семантика:** Повністю повторює контракт `request_threaded_irq()`, але прив'язує життєвий цикл ресурсу переривання до структури `struct device *dev`.
  - **Перевага:** Ядро автоматично викликає `free_irq()` у разі відмови функції `probe()` драйвера або під час від'єднання пристрою (`driver unbind`), що виключає витоки пам'яті та помилки подвійного звільнення (*Use-After-Free*).

- **`disable_irq(irq)` vs `disable_irq_nosync(irq)`**:
  - Обидві функції збільшують лічильник глибини `desc->depth`. Реальне апаратне маскування `chip->irq_mask()` виконується лише тоді, коли `depth` збільшується з `0` до `1`.
  - `disable_irq()` є синхронною операцією: він чекає завершення виконання поточного hardirq на всіх процесорних ядрах та завершення роботи потоку `thread_fn`.
  - **Попередження:** Виклик `disable_irq()` зсередини власного обробника переривання призводить до миттєвого взаємного блокування (*Deadlock*). Для відключення лінії всередині ISR слід викликати виключно `disable_irq_nosync()`.
  - `disable_irq_nosync()` лише модифікує лічильник та маскує лінію без очікування завершення поточних обробників. Безпечний для виклику в контексті `hardirq`.

- **`enable_irq(irq)`**:
  - Зменшує лічильник `desc->depth`. Коли значення досягає `0`, ядро викликає демаскування `chip->irq_unmask()`.
  - Якщо викликати `enable_irq()` при вже активному перериванні (`depth == 0`), ядро зафіксує розбалансування і видасть попередження `Unbalanced enable for IRQ` у системний лог `dmesg`.

### Прапорці конфігурації реєстрації (`irqflags`)

| Прапорець | Значення та правила використання |
| :--- | :--- |
| **`IRQF_SHARED`** | Дозволяє декільком периферійним драйверам реєструвати свої обробники на одній фізичній лінії переривання (шина PCI, спільні шини SoC). Усі драйвери на цій лінії зобов'язані передавати цей прапорець, однаковий тип тригера та унікальний вказівник `dev_id`. |
| **`IRQF_ONESHOT`** | Утримує лінію переривання замаскованою на апаратному рівні доти, доки потоковий обробник `thread_fn` повністю не завершить виконання. Є обов'язковим для ліній за рівнем напруги з потоковою обробкою, якщо первинний обробник `handler == NULL`. |
| **`IRQF_NO_SUSPEND`** | Забороняє підсистемі керування живленням вимикати дане переривання під час переходу системи в стан сну (*System Suspend*). Використовується для системних таймерів та ліній міжпроцесорних сповіщень. |
| **`IRQF_NO_AUTOEN`** | Запобігає автоматичному включенню лінії всередині `request_threaded_irq()`. Драйвер має явно викликати `enable_irq()` пізніше, коли завершиться повна апаратна ініціалізація пристрою. |
| **`IRQF_PERCPU`** | Позначає переривання як локальне для кожного процесорного ядра (наприклад, ARM Generic Timer PPI). |
| **`IRQF_EARLY_RESUME`** | Дозволяє відновити обробку цього переривання на ранньому етапі виходу зі стану сну до відновлення роботи основних шин і пристроїв. |
| **`IRQF_COND_ONESHOT`** | Вмикає режим oneshot лише для тих обробників спільної лінії `IRQF_SHARED`, які використовують потокову обробку. |
| **`IRQF_NO_THREAD`** | Забороняє автоматичне переведення даного переривання в потоковий режим при запуску ядра з параметром `threadirqs` (використовується для ліній системного таймера). |
| **`IRQF_TRIGGER_RISING`** | Налаштувати тригер чутливості на наростаючий фронт сигналу (перехід 0 → 1). |
| **`IRQF_TRIGGER_FALLING`** | Налаштувати тригер чутливості на спадний фронт сигналу (перехід 1 → 0). |
| **`IRQF_TRIGGER_HIGH`** | Налаштувати чутливість на високий логічний рівень напруги. |
| **`IRQF_TRIGGER_LOW`** | Налаштувати чутливість на низький логічний рівень напруги. |
| **`IRQF_TRIGGER_PROBE`** | Повідомляє ядро, що драйвер виконує автовизначення типу апаратного тригера. |

---

## 12. Віртуалізація переривань: VFIO, KVM та пряма ін'єкція векторів (Direct Vector Injection)

Під час прямого прокидання фізичних пристроїв PCI Express у віртуальні машини (*PCI Device Passthrough* через VFIO та KVM) традиційна схема емуляції через вихід у користувацький простір гіпервізора QEMU створює неприйнятні накладні витрати (тисячі тактів процесора на кожен VM-Exit). Для досягнення продуктивності, близької до «голого заліза» (*Bare-metal Performance*), ядро Linux надає три рівні оптимізації доставки сигналів у гостьові ОС:

```
+-----------------------------------------------------------------------------------+
|               Еволюція шляхів доставки переривань у віртуальні машини             |
+-----------------------------------------------------------------------------------+
| 1. Класична емуляція (Legacy QEMU):                                               |
|    Фізичний IRQ -> Хостовий ISR -> QEMU Userspace (read/poll) -> ioctl(KVM_IRQ)    |
|    [Накладні витрати: 2 перемикання контексту + 1 VM-Exit]                        |
|                                                                                   |
| 2. Механізм irqfd + resamplefd (Kernel Bypass):                                   |
|    Фізичний IRQ -> VFIO ISR -> eventfd_signal() -> KVM irqfd -> Guest vAPIC/vGIC   |
|    [Накладні витрати: 0 виходів у Userspace, 1 VM-Exit для ін'єкції]              |
|                                                                                   |
| 3. Пряма апаратна ін'єкція (Intel Posted Interrupts / ARM GICv4 Virtual LPI):     |
|    Фізичний PCIe MSI -> IOMMU (IRTE) -> Posted Interrupt -> Direct to vCPU Core   |
|    [Накладні витрати: 0 виходів у Userspace, 0 VM-Exits (повністю апаратно)]      |
+-----------------------------------------------------------------------------------+
```

### 1. Механізм irqfd у KVM

Механізм `irqfd` пов'язує дескриптор міжпроцесної сигналізації `eventfd` ядра з вектором глобального системного переривання гостьової ОС (*GSI — Global System Interrupt*).

```c
#include <linux/kvm.h>

struct kvm_irqfd {
    __u32 fd;         /* Файловий дескриптор eventfd */
    __u32 gsi;        /* Номер вектора GSI у віртуальній машині */
    __u32 flags;      /* Бітові прапорці керування (KVM_IRQFD_FLAG_*) */
    __u32 resamplefd; /* Дескриптор eventfd для відновлення переривань за рівнем */
    __u8  pad[16];
};

#define KVM_IRQFD_FLAG_DEASSIGN  (1 << 0)
#define KVM_IRQFD_FLAG_RESAMPLE  (1 << 1)
```

#### Протокол роботи irqfd

1. Гіпервізор QEMU відкриває дескриптор `eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC)`.
2. QEMU реєструє цей `eventfd` у підсистемі VFIO за допомогою команди `ioctl(vfio_dev_fd, VFIO_DEVICE_SET_IRQS, &irq_set)`.
3. QEMU передає той самий дескриптор у модуль KVM через системний виклик `ioctl(kvm_vm_fd, KVM_IRQFD, &struct kvm_irqfd)`.
4. Ядро KVM реєструє функцію зворотного виклику опитування (*Poll Callback* `irqfd_wakeup()`) на цей `eventfd`.
5. Коли фізичний периферійний пристрій генерує MSI-повідомлення, хостовий драйвер `vfio-pci` викликає функцію `eventfd_signal()`.
6. Підсистема подій ядра миттєво активує функцію `irqfd_wakeup()`. KVM перехоплює сигнал і програмно виставляє біт переривання у віртуальному контролері переривань гостя (vAPIC або vGIC), повністю оминаючи процесний контекст QEMU.

### 2. Емуляція переривань за рівнем (INTx) та механізм resamplefd

Переривання за рівнем напруги (класичні лінії PCI INTx) не можуть бути оброблені простим одноразовим імпульсом `irqfd`, оскільки фізична лінія залишається активною доти, доки гостьовий драйвер не виконає I/O-операцію скидання прапорця статусу в регістрах кінцевого пристрою.

#### Проблема шторму переривань у віртуалізації
Якщо просто передати сигнал INTx у гостьову ОС без маскування, хостове ядро отримає безперервний шторм переривань (*Interrupt Storm*), оскільки фізична лінія залишається активною на материнській платі, блокуючи виконання будь-якого іншого коду на хості.

#### Протокол взаємодії з resamplefd

```
[Фізичний пристрій] ----(INTx Active)----> [Хостовий VFIO ISR]
                                                |
                   1. Маскує хостову лінію (disable_irq_nosync)
                   2. Сигналізує eventfd (irqfd)
                                                |
                                                v
[Гостьовий vCPU] <----(Inject INTx)------- [KVM irqfd]
       |
3. Гостьовий ISR скидає регістр пристрою
4. Гість надсилає EOI у віртуальний APIC
       |
       v
[KVM vAPIC/vIOAPIC] ----(Перехоплює EOI)----> Сигналізує resamplefd
                                                    |
                                                    v
[Хостовий VFIO] <----(resamplefd event)-------------+
       |
5. Демаскує хостову фізичну лінію (chip->irq_unmask)
```

1. Фізичний пристрій піднімає рівень напруги на лінії переривання.
2. Первинний обробник `vfio-pci` у контексті hardirq маскує хостову лінію (`disable_irq_nosync()`) і надсилає сигнал в `eventfd`.
3. KVM отримує подію через `irqfd` та інжектує віртуальне переривання в гостьовий контролер vIOAPIC.
4. Гостьовий драйвер виконує читання регістрів пристрою, усуваючи причину переривання, та надсилає сигнал завершення обробки (*End of Interrupt*) у віртуальний контролер.
5. KVM перехоплює запис EOI у віртуальний APIC/IOAPIC і генерує сигнал у вторинний дескриптор `resamplefd` (прапорець `KVM_IRQFD_FLAG_RESAMPLE`).
6. Драйвер `vfio-pci` отримує сповіщення з `resamplefd` і викликає демаскування фізичної лінії контролера хоста `enable_irq()` / `chip->irq_unmask()`.

### 3. Підсистема прямого зв'язування: IRQ Bypass Manager

Підсистема ядра `IRQ Bypass Manager` (визначена в `<linux/irqbypass.h>`) надає модульний механізм прямого сполучення постачальників переривань (*Producers*, драйвер `vfio-pci`) та споживачів (*Consumers*, підсистема `kvm`), оминаючи проміжну програмну чергу `eventfd`.

```c
#include <linux/irqbypass.h>

struct irq_bypass_producer {
    struct list_head node;
    void *token;                  /* Унікальний ідентифікатор (покажчик на eventfd_ctx) */
    unsigned int irq;             /* Фізичний віртуальний номер virq хоста */
    void (*add_consumer)(struct irq_bypass_producer *,
                         struct irq_bypass_consumer *);
    void (*del_consumer)(struct irq_bypass_producer *,
                         struct irq_bypass_consumer *);
};

struct irq_bypass_consumer {
    struct list_head node;
    void *token;                  /* Той самий покажчик на eventfd_ctx */
    struct kvm *kvm;              /* Покажчик на екземпляр віртуальної машини KVM */
    int (*add_producer)(struct irq_bypass_consumer *,
                        struct irq_bypass_producer *);
    void (*del_producer)(struct irq_bypass_consumer *,
                         struct irq_bypass_producer *);
    void (*start)(struct irq_bypass_consumer *);
    void (*stop)(struct irq_bypass_consumer *);
};

/* Реєстрація постачальника переривань (VFIO) */
int irq_bypass_register_producer(struct irq_bypass_producer *producer);
void irq_bypass_unregister_producer(struct irq_bypass_producer *producer);

/* Реєстрація споживача переривань (KVM) */
int irq_bypass_register_consumer(struct irq_bypass_consumer *consumer);
void irq_bypass_unregister_consumer(struct irq_bypass_consumer *consumer);
```

#### Контракт роботи IRQ Bypass Manager

1. Коли драйвер `vfio-pci` виділяє MSI-вектор для пристрою, він реєструє структуру `struct irq_bypass_producer`, передаючи вказівник на контекст `eventfd_ctx` як токен.
2. Коли KVM конфігурує `irqfd` для цього ж `eventfd`, він реєструє `struct irq_bypass_consumer` з ідентичним токеном.
3. Менеджер зіставляє токени `producer->token == consumer->token` і синхронно викликає метод `consumer->add_producer(consumer, producer)`.
4. Усередині методу `add_producer` модуль KVM отримує прямий доступ до хостового дескриптора `producer->irq` і конфігурує апаратні механізми прямої доставки процесора (*Posted Interrupts*).

### 4. Апаратна пряма ін'єкція векторів (Direct Vector Injection)

Пряма апаратна ін'єкція повністю виключає процесор хоста та гіпервізор із тракту обробки переривань: периферійний пристрій записує повідомлення MSI безпосередньо у внутрішні структури віртуального процесора гостьової ОС.

#### Intel VT-d Posted Interrupts (APIC-v)

На процесорах Intel x86 із підтримкою технологій віртуалізації VT-d та APIC-v процес доставки реалізується на рівні контролера пам'яті IOMMU та апаратної сторінки vAPIC:

```
[PCIe Endpoint (MSI-X Write)]
       |
       v (DMA Transaction)
[Intel IOMMU (Interrupt Remapping Unit)]
       |
       +--> 1. Зчитує IRTE (Posted Mode: Target PID Address + Vector)
       +--> 2. Атомарно встановлює біт вектора у PIR структури Posted-Interrupt Descriptor
       +--> 3. Генерує Posted-Interrupt Notification Event (NV = 0xF2) на шині процесора
       |
       v
[Intel CPU Core (Виконує гостьовий vCPU у Non-Root Mode)]
       |
       +--> Апаратний блок APIC-v перехоплює вектор NV
       +--> Апаратно копіює біти з PIR у Virtual-APIC IRR (Interrupt Request Register)
       +--> Інжектує вектор безпосередньо в гостьове ядро (0 VM-Exits!)
```

- **Posted-Interrupt Descriptor (PID):** 64-байтна вирівняна структура в пам'яті хоста, яка містить 256-бітне поле `PIR` (*Posted Interrupt Requests*), прапорець `ON` (*Outstanding Notification*) та фізичний APIC ID цільового ядра CPU.
- **Нульовий оверхед гіпервізора:** Якщо віртуальний процесор гостя вже виконується на ядрі CPU (*Guest Non-Root Mode*), процесор апаратно оновлює регістри vAPIC і передає керування в гостьовий ISR без жодного виходу у стан гіпервізора (*0 VM-Exits*). Якщо vCPU був у стані очікування (`HLT`), вектор сповіщення NV пробуджує фізичне ядро для запуску планувальника KVM.

#### ARM GICv4 / GICv4.1 Virtual LPI Direct Injection

На 64-бітних платформах ARM із контролерами GICv4 пряма ін'єкція реалізується через розширення блоку ITS (*Interrupt Translation Service*) та віртуальні редистриб'ютори:

- Метод `irq_chip->irq_set_vcpu_affinity(data, &vcpu_info)` зв'язує фізичний дескриптор переривання зі структурою `struct its_vpe` (*Virtual Processing Element*).
- Драйвер ITS надсилає апаратні команди керування в чергу команд ITS:
  - `VMAPP`: реєструє віртуальний процесор vPE у таблицях ITS та пов'язує його з фізичним редистриб'ютором.
  - `VMAPI` / `VMAPTI`: створює трансляцію кортежу `(DeviceID, EventID)` безпосередньо у віртуальний ідентифікатор `vLPI`, прив'язаний до даного vPE.
  - `VMOVI`: виконує прозору апаратну міграцію віртуального переривання під час переміщення гостьового vCPU на інше фізичне ядро CPU.
- Під час отримання транзакції MSI блок GICv4 ITS самостійно записує прапорець переривання у віртуальний регістр очікування `GICR_VPENDBASER` цільового vPE, доставляючи сигнал у гостьову ОС на швидкості кремнію.

---

## 13. Метрики, налагодження та системні інтерфейси (/proc та /sys)

### Формат та структура файлу `/proc/interrupts`

Файл `/proc/interrupts` надає статистику спрацьовувань переривань у розрізі кожного процесорного ядра системи:

```
           CPU0       CPU1       CPU2       CPU3       
 16:       1420          0          0          0  GICv3  33 Level     arm-pmu
 24:          0      38421          0          0  GICv3  57 Edge      serial
 42:       8129       7614      12049      11980  GIC-ITS 8192 Edge   nvme0q0
 89:        102          0          0          0  my-gpio-irq   5 Edge user_button
NMI:          0          0          0          0  Non-maskable interrupts
LOC:     184920     152301     178120     169400  Local timer interrupts
SPU:          0          0          0          0  Spurious interrupts
```

**Розшифрування колонок:**
1. **Колонка 1 (`16:`, `42:`):** Віртуальний системний номер ядра Linux (`virq`).
2. **Колонки `CPU0..CPUn`:** Кількість оброблених сигналів кожним процесорним ядром (значення читаються з per-CPU змінної `desc->kstat_irqs`).
3. **Колонка назви чіпа (`GICv3`, `GIC-ITS`, `my-gpio-irq`):** Рядок `irq_chip->name`.
4. **Колонка апаратного номера та типу (`33 Level`, `8192 Edge`):** Апаратний номер `hwirq` та поточний тип електричного тригера.
5. **Остання колонка (`arm-pmu`, `nvme0q0`):** Список зареєстрованих імен драйверів з `action->name`.

### Керування процесорною спорідненістю через `/proc/irq/[N]/`

Для кожного віртуального номера `[N]` ядро експортує каталог `/proc/irq/[N]/` із параметрами керування маршрутизацією:

- **`/proc/irq/[N]/smp_affinity`**: Шістнадцяткова бітова маска дозволених ядер CPU (наприклад, `0f` — ядра CPU0..CPU3, `02` — тільки CPU1). Запис нового значення викликає `chip->irq_set_affinity()`.
- **`/proc/irq/[N]/smp_affinity_list`**: Десятковий список ядер у зрозумілому форматі (наприклад, `0,2-4`).
- **`/proc/irq/[N]/effective_affinity`**: Реальна маска ядра, на яке контролер фізично доставляє сигнал у поточний момент (критично для архітектур, де одне переривання апаратно маршрутизується лише на один процесорний потік).
- **`/proc/irq/[N]/effective_affinity_list`**: Десятковий список реально задіяних процесорів.
- **`/proc/irq/[N]/node`**: Ідентифікатор NUMA-вузла, до якого прив'язаний дескриптор.
- **`/proc/irq/[N]/spurious`**: Статистика паразитних спрацьовувань (`count` — загальна кількість, `unhandled` — кількість невирішених подій).
- **`/proc/irq/[N]/wake_depth`**: Поточне значення лічильника глибини пробудження зі стану сну.

### Діагностика через DebugFS

Якщо ядро зібрано з підтримкою `CONFIG_GENERIC_IRQ_DEBUGFS`, у файловій системі `debugfs` доступна повна картина доменів та дескрипторів:

```bash
# Перегляд дерева всіх зареєстрованих доменів переривань у системі
cat /sys/kernel/debug/irq/domains/summary

# Повний дамп стану конкретного віртуального переривання 42
cat /sys/kernel/debug/irq/irqs/42
```

Приклад виводу стану дескриптора через DebugFS:
```
handler:  handle_fasteoi_irq
device:   0000:01:00.0
status:   0x00000200
istate:   0x00000000
ddepth:   0
wdepth:   0
dstate:   0x03013200
            IRQD_ACTIVATED
            IRQD_IRQ_STARTED
            IRQD_SINGLE_TARGET
node:     0
affinity: 0-7
effectiv: 2
domain:   :pci-msi-0
 hwirq:   0x2000
 chip:    PCI-MSI
  flags:  0x10
 parent:
    domain:   :its-0
     hwirq:   0x2000
     chip:    GICv3-ITS
      flags:  0x0
     parent:
        domain:   :gic-0
         hwirq:   0x2040
         chip:    GICv3
```

Дамп демонструє ланцюжок ієрархічних доменів (`PCI-MSI -> GICv3-ITS -> GICv3`), прив'язку до фізичного пристрою PCI, активну процесорну маску та призначений диспетчер `handle_fasteoi_irq`.

### Точки трасування ядра (*Kernel Tracepoints*)

Підсистема переривань інтегрована з `ftrace` та `perf` через стандартні tracepoints підсистеми `irq`:

- **`irq:irq_handler_entry`**: Фіксує момент передачі керування у функцію `action->handler(irq, dev_id)` (поля: `irq`, `name`).
- **`irq:irq_handler_exit`**: Фіксує завершення виконання `handler` та код повернення `ret` (`IRQ_HANDLED`, `IRQ_NONE`, `IRQ_WAKE_THREAD`).
- **`irq:softirq_entry`** / **`irq:softirq_exit`**: Трасування початку та завершення обробки нижніх половин softirq (`TIMER_SOFTIRQ`, `NET_RX_SOFTIRQ`, `TASKLET_SOFTIRQ`).
- **`irq:softirq_raise`**: Фіксує програмне виставлення прапорця виконання softirq через `raise_softirq()`.
