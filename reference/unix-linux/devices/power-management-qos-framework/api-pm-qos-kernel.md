# 📋 Ядерний API фреймворку PM QoS

Ця вставка містить довідник внутрішніх структур даних, функцій та прототипів підсистеми PM QoS у заголовочному файлі `<linux/pm_qos.h>`, які використовуються розробниками драйверів ядерних пристроїв та підсистем живлення Linux.

### 1. Головні структури даних

Вся логіка PM QoS спирається на три базові набори структур: для системних затримок сну CPU (CPU Latency QoS), затримок та прапорців окремих пристроїв (Per-Device PM QoS) та меж тактових частот (Frequency QoS).

#### Структури агрегації та запитів (`pm_qos_constraints` та `pm_qos_request`)

Центральною структурою агрегації є `struct pm_qos_constraints`. Вона тримає сортований список усіх висунутих вимог клієнтів та керує ланцюжком сповіщень:

```c
enum pm_qos_type {
    PM_QOS_UNION,
    PM_QOS_MIN,
    PM_QOS_MAX,
    PM_QOS_SUM,
};

struct pm_qos_constraints {
    struct plist_head list;
    s32 target_value;
    s32 default_value;
    s32 no_constraint_value;
    enum pm_qos_type type;
    struct blocking_notifier_head *notifiers;
};

struct pm_qos_request {
    struct plist_node node;
    int pm_qos_class;
    struct pm_qos_constraints *qos;
};
```

Поля структури `struct pm_qos_constraints` мають такі значення та призначення:
* `list`: пріоритетний список `struct plist_head`, у якому запити клієнтів автоматично впорядковані за зростанням або спаданням їх пріоритетного значення.
* `target_value`: поточне розраховане агреговане значення для всього списку клієнтів (значення типу `s32`).
* `default_value`: стандартне значення, яке повертається тоді, коли список запитів є порожнім (наприклад, `PM_QOS_CPU_LAT_DEFAULT_VALUE` дорівнює `2000000000` нс для затримок процесора).
* `no_constraint_value`: спеціальне значення, що позначає відсутність будь-яких обмежень з боку клієнтів.
* `type`: тип математичної агрегації: `PM_QOS_MIN` (вибирається найменше значення серед усіх запитів) або `PM_QOS_MAX` (вибирається найбільше значення).
* `notifiers`: вказувальник на ланцюжок сповіщень `struct blocking_notifier_head`, підписники якого отримують виклик при кожній зміні `target_value`.

Клієнтський запит представлений структурою `struct pm_qos_request`. Вона містить убудований вузол пріоритетного списку `node` типу `struct plist_node` та вказувальник на батьківський об'єкт `qos`.

#### Структури PM QoS для конкретних пристроїв (`dev_pm_qos`)

Кожен екземпляр пристрою `struct device` містить вказувальник `power.qos` на об'єкт `struct dev_pm_qos`, який керує локальними вимогами відновлення та відновлення живлення:

```c
enum dev_pm_qos_req_type {
    DEV_PM_QOS_RESUME_LATENCY = 1,
    DEV_PM_QOS_LATENCY_TOLERANCE,
    DEV_PM_QOS_FLAGS,
};

struct dev_pm_qos_request {
    enum dev_pm_qos_req_type type;
    union {
        struct plist_node pnode;
        struct pm_qos_flags_request flr;
    } data;
    struct device *dev;
};

struct dev_pm_qos {
    struct dev_pm_qos_constraints resume_latency;
    struct dev_pm_qos_constraints latency_tolerance;
    struct pm_qos_flags flags;
    struct blocked_notifier_head resume_latency_notifiers;
    struct blocked_notifier_head latency_tolerance_notifiers;
    struct mutex mtx;
};
```

Поля структури `struct dev_pm_qos`:
* `resume_latency`: об'єкт обмежень затримки відновлення робочого стану пристрою D0 (у мкс).
* `latency_tolerance`: об'єкт обмежень допуску затримки для апаратних повідомлень шини PCIe LTR (у мкс).
* `flags`: бітові прапорці управління доденами живлення (`PM_QOS_FLAG_NO_POWER_OFF` та `PM_QOS_FLAG_REMOTE_WAKEUP`).
* `mtx`: локальний м'ютекс `struct mutex`, який захищає структури даних QoS конкретного пристрою від паралельних модифікацій з різних ядер.

#### Структури гарантій частоти (`freq_constraints` та `freq_qos_request`)

Для керування робочими частотами процесорів у `cpufreq` та шин у `devfreq` використовується об'єкт `struct freq_constraints`:

```c
enum freq_qos_req_type {
    FREQ_QOS_MIN = 1,
    FREQ_QOS_MAX,
};

struct freq_constraints {
    struct pm_qos_constraints min_freq;
    struct pm_qos_constraints max_freq;
};

struct freq_qos_request {
    enum freq_qos_req_type type;
    struct plist_node pnode;
    struct freq_constraints *qos;
};
```

Структура `freq_constraints` містить два паралельні об'єкти агрегації:
* `min_freq`: список запитів мінімальної частоти (тип агрегації `PM_QOS_MAX`, щоб обрати найвищу із запитаних мінімальних частот).
* `max_freq`: список запитів максимальної частоти (тип агрегації `PM_QOS_MIN`, щоб обрати найнижчу із запитаних максимальних частот).

---

### 2. API CPU Latency QoS

Функції даного розділу керують системним обмеженням затримки пробудження процесорів від станів сну `cpuidle`.

```c
void cpu_latency_qos_add_request(struct pm_qos_request *req, s32 value);
```
Додає новий запит затримки `value` (у мікросекундах) у глобальний список обмежень. 
* **Параметри:** `req` — вказувальник на виділену клієнтом структуру `struct pm_qos_request`; `value` — бажана максимальна затримка в мкс (значення `0` блокує всі C-states вище C0).
* **Контекст:** Процесний контекст з можливістю сну (Sleepable Process Context). Не можна викликати з переривань.

```c
void cpu_latency_qos_update_request(struct pm_qos_request *req, s32 new_value);
```
Оновлює значення існуючого та вже доданого запиту `req`.
* **Параметри:** `req` — вказувальник на активний запит; `new_value` — нове значення затримки в мкс.
* **Поведінка:** Зміщує вузол у сортованому `plist`, виконує перерахунок агрегованої межі та викликає сповіщення підписників, якщо значення змінилося.

```c
void cpu_latency_qos_remove_request(struct pm_qos_request *req);
```
Видаляє запит `req` із глобального списку обмежень.
* **Поведінка:** Вилучає вузол зі списку `plist`, перераховує підсумкове агреговане значення та сповіщає підписників.

```c
s32 cpu_latency_qos_limit(void);
```
Повертає поточне агреговане значення допустимої затримки пробудження CPU у мікросекундах.
* **Контекст:** Атомарний (Atomic Context). Безпечно для виклику всередині обробників переривань (ISR), гарячих шляхів регуляторів `cpuidle` та під час вимкнених переривань.

```c
bool cpu_latency_qos_request_active(struct pm_qos_request *req);
```
Перевіряє, чи є вказаний запит `req` наразі підключеним та активним у глобальному списку PM QoS. Повертає `true`, якщо запит активний, і `false` у протилежному випадку.

---

### 3. API Per-Device PM QoS

Функції для роботи з обмеженнями відновлення та допусків затримок конкретного периферійного пристрою.

```c
int dev_pm_qos_add_request(struct device *dev, struct dev_pm_qos_request *req,
                           enum dev_pm_qos_req_type type, s32 value);
```
Додає запит QoS для конкретного пристрою `dev`.
* **Параметри:** `dev` — вказувальник на пристрій; `req` — клієнтський дескриптор запиту; `type` — тип обмеження (`DEV_PM_QOS_RESUME_LATENCY`, `DEV_PM_QOS_LATENCY_TOLERANCE` або `DEV_PM_QOS_FLAGS`); `value` — значення затримки чи прапорців.
* **Повертане значення:** `0` при успішному додаванні без зміни загального агрегованого значення пристрою; `1` якщо внаслідок додавання агреговане значення пристрою змінилося; негативний код помилки (`-EINVAL`, `-ENOMEM`) у разі збою.

```c
int dev_pm_qos_update_request(struct dev_pm_qos_request *req, s32 new_value);
```
Змінює значення існуючого пристроєвого запиту `req` на `new_value`.
* **Повертане значення:** `0` якщо агрегат пристрою не змінився; `1` якщо агрегат змінився; негативний код помилки при збої.

```c
int dev_pm_qos_remove_request(struct dev_pm_qos_request *req);
```
Видаляє пристроєвий запит `req` та перераховує обмеження живлення пристрою.

```c
s32 dev_pm_qos_read_value(struct device *dev, enum dev_pm_qos_req_type type);
```
Зчитує поточне агреговане значення обмеження типу `type` для пристрою `dev`. Виконується атомарно без блокувань.

```c
int dev_pm_qos_add_notifier(struct device *dev, struct notifier_block *notifier,
                            enum dev_pm_qos_req_type type);

int dev_pm_qos_remove_notifier(struct device *dev, struct notifier_block *notifier,
                               enum dev_pm_qos_req_type type);
```
Реєструє або видаляє сповіщувач `notifier`, який викликатиметься при кожній зміні агрегованого обмеження типу `type` для вказаного пристрою `dev`.

---

### 4. API Frequency QoS

Забезпечує встановлення нижньої та верхньої межі частоти для регуляторів `cpufreq` та підсистеми `devfreq`.

```c
int freq_qos_add_request(struct freq_constraints *qos, struct freq_qos_request *req,
                         enum freq_qos_req_type type, s32 value);
```
Додає запит обмеження частоти `value` (у килогерцах, кГц) до об'єкта `qos`.
* **Параметри:** `qos` — вказувальник на об'єкт обмежень (наприклад, `&policy->constraints`); `req` — дескриптор запиту; `type` — `FREQ_QOS_MIN` (нижня межа) або `FREQ_QOS_MAX` (верхня межа); `value` — частота у кГц.
* **Повертане значення:** `0` або `1` при успіху, негативний код помилки при помилці.

```c
int freq_qos_update_request(struct freq_qos_request *req, s32 new_value);
```
Оновлює значення частоти для запиту `req` на нове значення `new_value` (у кГц).

```c
int freq_qos_remove_request(struct freq_qos_request *req);
```
Видаляє запит частоти `req` з об'єкта обмежень.

```c
s32 freq_qos_read_value(struct freq_constraints *qos, enum freq_qos_req_type type);
```
Повертає чинне агреговане значення частоти у кГц для типу `FREQ_QOS_MIN` або `FREQ_QOS_MAX`.

```c
int freq_qos_add_notifier(struct freq_constraints *qos, enum freq_qos_req_type type,
                          struct notifier_block *notifier);

int freq_qos_remove_notifier(struct freq_constraints *qos, enum freq_qos_req_type type,
                             struct notifier_block *notifier);
```
Підключає або відключає сповіщувач `notifier` для відстеження змін агрегованих меж частоти.

---

### 5. Правила синхронізації та контексти виконання

Розробники драйверів повинні суворо дотримуватися правил виконання залежно від контексту ядерного коду:

1. **Модифікуючі операції (`add`, `update`, `remove`):**
   * Захоплюють внутрішні спін-локи PM QoS та м'ютекси ланцюжків сповіщень.
   * Викликають `blocking_notifier_call_chain()`, який може переводити потоки у стан очікування (сон).
   * **Правило:** Викликаються виключно у контексті процесів (Process Context) з увімкненими перериваннями. Заборонено викликати всередині обробників переривань (ISR), спін-локів чи атомарних секцій.

2. **Операції зчитування (`limit`, `read_value`):**
   * Здійснюють атомарне зчитування розрахованого поля `target_value` без захоплення блокувальних м'ютексів.
   * **Правило:** Дозволено викликати у будь-якому контексті, включаючи переривання (ISR), нижні половини (softirq, tasklets) та гарячі шляхи регуляторів сну й частоти.
