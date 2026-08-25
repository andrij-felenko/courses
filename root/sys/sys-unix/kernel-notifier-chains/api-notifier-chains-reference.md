# 📋 Довідник API ланцюжків сповіщень: типи, структури, функції та коди повернення

Підсистема ланцюжків сповіщень ядра Linux оголошена в заголовковому файлі `<linux/notifier.h>`. Вона надає уніфікований інтерфейс для реалізації патерну «Видавець–Передплатник» (Publish-Subscribe) між слабкозв'язаними підсистемами ядра. Цей довідник містить детальний опис структур даних, правил їхнього наповнення, функцій життєвого циклу, кодів повернення та вичерпний каталог глобальних ланцюжків ядра з описом контекстів їхнього виклику.

### Фундаментальні структури даних

Підсистема базується на зв'язці вузла передплатника (`struct notifier_block`) та заголовної структури ланцюжка (`*_notifier_head`).

#### 1. Вузол передплатника: struct notifier_block

Кожен модуль ядра, що бажає отримувати повідомлення про системні події, зобов'язаний виділити та ініціалізувати екземпляр `struct notifier_block`:

```c
struct notifier_block {
    int (*notifier_call)(struct notifier_block *nb,
                         unsigned long action,
                         void *data);
    struct notifier_block __rcu *next;
    int priority;
};
```

Детальний опис полів та інваріантів структури:

- **`notifier_call`** — вказівник на функцію зворотного виклику. Функція викликається синхронно під час генерації події в ланцюжку. Вона приймає три аргументи:
  - `struct notifier_block *nb` — вказівник на сам зареєстрований вузол. Якщо блок сповіщення вбудовано у власну структуру драйвера (наприклад, `struct my_device_state`), обробник відновлює адресу батьківського об'єкта через виклик `container_of(nb, struct my_device_state, nb)`.
  - `unsigned long action` — числовий код події, специфічний для конкретного ланцюжка. Значення передається без змін від джерела генерації.
  - `void *data` — вказівник на контекстні дані події. Тип об'єкта, на який вказує цей параметр, суворо зафіксований протоколом конкретного ланцюжка (наприклад, `struct net_device*` або `struct netdev_notifier_info*` для мережі).
- **`next`** — вказівник на наступний вузол у списку. Поле позначене як `__rcu`, що забороняє пряме розіменування без використання допоміжних макросів RCU (`rcu_dereference`, `rcu_assign_pointer`) і захищає читачів від збоїв пам'яті при паралельній зміні списку.
- **`priority`** — знакове ціле число (`int`), що задає пріоритет обробника. Вузол із більшим числовим значенням розміщується ближче до початку списку і викликається раніше. Стандартне значення за замовчуванням дорівнює `0`. Від'ємні значення використовуються для фонових спостерігачів низького пріоритету (логування, збір статистики), а додатні — для критично важливих фільтрів і драйверів, які повинні підготувати апаратуру до реакції інших підсистем.

---

#### 2. Заголовні структури чотирьох типів ланцюжків

Заголовна структура визначає модель синхронізації та контекст, у якому дозволено викликати й обробляти сповіщення.

```c
/* 1. Атомарний ланцюжок (захист через spinlock) */
struct atomic_notifier_head {
    spinlock_t lock;
    struct notifier_block *head;
};

/* 2. Блокуючий ланцюжок (захист через семафор читачів/письменників) */
struct blocking_notifier_head {
    struct rw_semaphore rwsem;
    struct notifier_block *head;
};

/* 3. Сирий ланцюжок (без внутрішніх блокувань) */
struct raw_notifier_head {
    struct notifier_block *head;
};

/* 4. SRCU-ланцюжок (Sleepable RCU) */
struct srcu_notifier_head {
    struct mutex mutex;
    struct srcu_struct srcu;
    struct notifier_block *head;
};
```

Особливості внутрішнього устрою заголовків:

- **`atomic_notifier_head`** містить спінлок `lock`, який захоплюється з вимкненням переривань як під час модифікації списку, так і під час обходу обробників. Це гарантує цілісність списку в умовах виклику з HardIRQ та SoftIRQ, але виключає можливість сну для обробників.
- **`blocking_notifier_head`** містить семафор `rwsem`. Реєстрація використовує режим запису (`down_write`), унеможливлюючи паралельні модифікації, а виклик сповіщень — режим читання (`down_read`), дозволяючи багатьом процесорам паралельно виконувати блокуючі обробники.
- **`raw_notifier_head`** містить виключно вказівник `head`. Будь-які блокування відсутні, що дозволяє підсистемі-власнику застосовувати власні спеціалізовані замки.
- **`srcu_notifier_head`** комбінує звичайний м'ютекс `mutex` (для захисту операцій вставки/видалення) та структуру Sleepable RCU `srcu`. Читачі виконують паралельний обхід списку без блокувань і водночас мають повне право спати всередині своїх обробників.

---

### Макроси ініціалізації та очищення

Ланцюжки сповіщень можуть бути оголошені статично під час компіляції ядра або ініціалізовані динамічно під час завантаження модуля.

```c
/* Статичне оголошення та ініціалізація глобальних ланцюжків */
#define ATOMIC_NOTIFIER_HEAD(name)
#define BLOCKING_NOTIFIER_HEAD(name)
#define RAW_NOTIFIER_HEAD(name)

/* Динамічна ініціалізація структур у купі або всередині об'єктів пристроїв */
void atomic_notifier_chain_init(struct atomic_notifier_head *nh);
void blocking_notifier_chain_init(struct blocking_notifier_head *nh);
void raw_notifier_chain_init(struct raw_notifier_head *nh);
int  srcu_init_notifier_head(struct srcu_notifier_head *nh);
void srcu_cleanup_notifier_head(struct srcu_notifier_head *nh);
```

Важливе зауваження щодо SRCU: функція `srcu_init_notifier_head()` динамічно виділяє пам'ять під системні структури відстеження RCU-поколінь, тому вона може повернути помилку `-ENOMEM`. Якщо динамічний SRCU-ланцюжок більше не потрібен, обов'язково слід викликати `srcu_cleanup_notifier_head()` для звільнення внутрішніх таблиць SRCU.

---

### Функції реєстрації та дереєстрації

Ядро надає суворо типізований набір функцій для підключення та відключення обробників.

| Тип ланцюжка | Реєстрація | Дереєстрація |
| :--- | :--- | :--- |
| **Atomic** | `int atomic_notifier_chain_register(struct atomic_notifier_head *nh, struct notifier_block *nb)` | `int atomic_notifier_chain_unregister(struct atomic_notifier_head *nh, struct notifier_block *nb)` |
| **Blocking** | `int blocking_notifier_chain_register(struct blocking_notifier_head *nh, struct notifier_block *nb)` | `int blocking_notifier_chain_unregister(struct blocking_notifier_head *nh, struct notifier_block *nb)` |
| **Raw** | `int raw_notifier_chain_register(struct raw_notifier_head *nh, struct notifier_block *nb)` | `int raw_notifier_chain_unregister(struct raw_notifier_head *nh, struct notifier_block *nb)` |
| **SRCU** | `int srcu_notifier_chain_register(struct srcu_notifier_head *nh, struct notifier_block *nb)` | `int srcu_notifier_chain_unregister(struct srcu_notifier_head *nh, struct notifier_block *nb)` |

Поведінка та правила використання:

- Усі функції реєстрації повертають `0` при успішному додаванні вузла або від'ємний код помилки `-EEXIST`, якщо цей самий об'єкт `nb` уже присутній у списку.
- Вузол вставляється у позицію, що відповідає його полю `priority` (за спаданням).
- Функції дереєстрації вилучають вузол зі списку. Для SRCU-ланцюжка функція `srcu_notifier_chain_unregister()` автоматично викликає `synchronize_srcu()`, гарантуючи, що після повернення з функції жоден процесор у системі більше не виконує старий обробник.

---

### Функції генерації подій (Call Chain)

Джерело події сповіщає зареєстрованих отримувачів за допомогою відповідної функції виклику:

```c
int atomic_notifier_call_chain(struct atomic_notifier_head *nh,
                               unsigned long val, void *v);

int blocking_notifier_call_chain(struct blocking_notifier_head *nh,
                                 unsigned long val, void *v);

int raw_notifier_call_chain(struct raw_notifier_head *nh,
                            unsigned long val, void *v);

int srcu_notifier_call_chain(struct srcu_notifier_head *nh,
                             unsigned long val, void *v);
```

Кожна з цих обгорток захоплює відповідний примітив синхронізації та передає керування внутрішньому універсальному диспетчеру:

```c
int notifier_call_chain(struct notifier_block **nl,
                        unsigned long val, void *v,
                        int nr_to_call, int *nr_calls);
```

Параметр `nr_to_call` дозволяє обмежити максимальну кількість викликаних обробників (значення `-1` означає виклик усіх елементів списку без обмеження), а `nr_calls` повертає фактичну кількість обробників, які встигли виконатися до повернення або переривання ланцюжка.

---

### Коди повернення та бітові прапорці

Функція `notifier_call` повертає 32-бітне ціле число, сформоване з констант `<linux/notifier.h>`:

```c
#define NOTIFY_DONE         0x0000
#define NOTIFY_OK           0x0001
#define NOTIFY_STOP_MASK    0x8000
#define NOTIFY_STOP         (NOTIFY_OK | NOTIFY_STOP_MASK)
#define NOTIFY_BAD          (NOTIFY_STOP_MASK | 0x0002)
```

Семантика кодів повернення:

- **`NOTIFY_DONE` (0x0000):** повідомлення свідчить, що обробник проігнорував подію (вона не стосується його пристрою) або виконав пасивне спостереження без формування власного результату. Диспетчер переходить до наступного обробника.
- **`NOTIFY_OK` (0x0001):** обробник успішно виконав необхідні дії у відповідь на подію. Диспетчер продовжує обхід ланцюжка.
- **`NOTIFY_STOP` (0x8001):** обробник успішно виконав дію і вимагає **зупинити подальшу розсилку**. Наступні обробники в ланцюжку викликані не будуть. Застосовується для ексклюзивного перехоплення подій.
- **`NOTIFY_BAD` (0x8002):** під час виконання сталася помилка або підсистема накладає вето на дію під час підготовчої фази. Диспетчер негайно перериває обхід і повертає цей статус викликачу.

#### Допоміжний макрос конвертації кодів помилок

Для зручного повернення системних помилок стандарту POSIX використовується інлайн-функція:

```c
static inline int notifier_from_errno(int err)
{
    if (err)
        return NOTIFY_BAD | (err & 0xffff);
    return NOTIFY_OK;
}
```

Якщо `err` дорівнює `0`, макрос повертає `NOTIFY_OK`; якщо `err` містить від'ємний код (наприклад, `-EINVAL` або `-ENOMEM`), він пакує його в комбінований статус із встановленим бітом `NOTIFY_BAD`.

---

### Каталог ключових глобальних ланцюжків ядра Linux

Нижче наведено структуровану таблицю найважливіших ланцюжків ядра, експортованих для використання драйверами та модулями:

| Назва ланцюжка / Обгортка | Тип | Допустимий контекст | Опис переданих подій та параметрів `data` |
| :--- | :--- | :--- | :--- |
| `netdev_chain`<br>`register_netdevice_notifier()` | **SRCU** | Процес (дозволено сон) | Зміна стану мережевих інтерфейсів (`NETDEV_UP`, `NETDEV_DOWN`, `NETDEV_CHANGEMTU`, `NETDEV_REGISTER`). `data` вказує на `struct netdev_notifier_info*`. |
| `inetaddr_chain`<br>`register_inetaddr_notifier()` | **Blocking** | Процес | Призначення або видалення IPv4-адрес на інтерфейсах. `data` вказує на `struct in_ifaddr*`. |
| `inet6addr_chain`<br>`register_inet6addr_notifier()` | **Blocking** | Процес | Зміни конфігурації IPv6-адрес та префіксів. `data` вказує на `struct inet6_ifaddr*`. |
| `reboot_notifier_list`<br>`register_reboot_notifier()` | **Blocking** | Процес | Завершення роботи системи (`SYS_RESTART`, `SYS_HALT`, `SYS_POWER_OFF`). `data` передає рядок команди перезапуску `char *cmd`. |
| `panic_notifier_list`<br>`atomic_notifier_chain_register()` | **Atomic** | Атомарний (фатальний збій) | Аварійна паніка ядра (`panic()`). Викликається перед зупинкою або перезавантаженням. `data` передає текст повідомлення про паніку. |
| `die_chain`<br>`register_die_notifier()` | **Atomic** | Атомарний (CPU exception) | Перехоплення апаратних збоїв та винятків процесора (Oops, Page Fault у ядрі). `data` вказує на `struct die_args*`. |
| `pm_chain_head`<br>`register_pm_notifier()` | **Blocking** | Процес | Події керування живленням (`PM_SUSPEND_PREPARE`, `PM_POST_SUSPEND`). Дозволяє підсистемам зберегти стан перед сном. |
| `cpu_chain` (через cpuhp framework) | **SRCU / Raw** | Процес / Атомарний | Гаряче підключення та вимкнення ядер CPU (`CPU_ONLINE`, `CPU_DEAD`, `CPU_UP_PREPARE`). |

---

### Інструменти спостереження та налагодження

Для діагностики ланцюжків сповіщень у запущеній системі використовуються стандартні інтерфейси ядра:

1. **Пошук адрес обробників:** зареєстровані статичні обробники можна знайти в таблиці символів `/proc/kallsyms` за суфіксами `_notifier` або `_nb`.
2. **Динамічне трасування через ftrace:** виклики функцій генерації подій легко простежуються через фільтр функцій ядра:
   ```bash
   echo '*notifier_call_chain*' > /sys/kernel/tracing/set_ftrace_filter
   echo function > /sys/kernel/tracing/current_tracer
   cat /sys/kernel/tracing/trace_pipe
   ```
3. **Аналіз викликів kprobe:** можна встановити динамічний зонд на `atomic_notifier_call_chain` або `blocking_notifier_call_chain`, щоб перевірити, які підсистеми генерують надмірну кількість повідомлень під навантаженням.
