# 📋 Довідник ядерних структур та інтерфейсу підсистеми Counter

Цей довідник містить систематизований перелік структур даних ядра з `<linux/counter.h>`, системних констант та викликів `ioctl` з UAPI-заголовка `<uapi/linux/counter.h>`, а також детальний розклад атрибутів файлової системи `sysfs`.

## 1. Архітектура контракту та управління пам’яттю ядра

Підсистема Counter відокремлює логіку керування пристроєм від конкретної шинної архітектури (PCI, platform_device, I2C, SPI). Драйвер описує свій стан через об'єкт `struct counter_device`, який реєструється у ядрі за допомогою ресурсно-керованих функцій devres (`devm_counter_alloc` та `devm_counter_add`).

При виклику `devm_counter_alloc(dev, sizeof_priv)` ядро виділяє суцільний блок пам'яті в замовленій системній купі, який включає як саму структуру `counter_device`, так і приватно зарезервовану пам'ять драйвера. Доступ до приватних даних здійснюється через вбудований інлайн-хелпер `counter_priv(counter)`. Такий підхід гарантує цілісність даних при відключенні пристрою та запобігає витокам пам'яті (memory leaks) при вивантаженні модуля.

### Поля структури `struct counter_device`

Структура `struct counter_device` слугує головною точкою монтування пристрою лічильника в ієрархію kobject ядра Linux.

- `name`: вказівник на постійний ASCII-рядок із назвою пристрою (експортується у sysfs як атрибут `/sys/bus/counter/devices/counterX/name`).
- `parent`: вказівник на батьківський об'єкт `struct device` (зазвичай `&pdev->dev`), який визначає положення пристрою у загальному дереві пристроїв ядра `/sys/devices/`.
- `ops`: вказівник на статичну таблицю функцій-колбеків `struct counter_ops`, які викликаються підсистемою при зверненні користувача через sysfs або ioctl.
- `signals`: масив апаратних вхідних сигналів `struct counter_signal`, кожен із яких репрезентує окрему фізичну ніжку чи канал (наприклад, Phase A, Phase B, Index Z).
- `num_signals`: кількість елементів у масиві `signals`.
- `counts`: масив логічних лічильників `struct counter_count`, які репрезентують апаратні акумулятори (регістри позиції).
- `num_counts`: кількість елементів у масиві `counts`.
- `ext`: масив глобальних розширень пристрою `struct counter_ext`, що експортують додаткові системні налаштування.
- `num_ext`: кількість глобальних розширень пристрою.
- `priv`: приватний вказівник на внутрішній стан драйвера.

### Таблиця операцій `struct counter_ops`

Таблиця `struct counter_ops` об'єднує колбеки, які ядерна підсистема викликає у контексті процесу для виконання читання чи запису апаратних регістрів.

```c
struct counter_ops {
    int (*signal_read)(struct counter_device *counter,
                       struct counter_signal *signal,
                       enum counter_signal_level *level);
    int (*count_read)(struct counter_device *counter,
                      struct counter_count *count,
                      u64 *val);
    int (*count_write)(struct counter_device *counter,
                       struct counter_count *count,
                       u64 val);
    int (*function_read)(struct counter_device *counter,
                         struct counter_count *count,
                         enum counter_function *function);
    int (*function_write)(struct counter_device *counter,
                          struct counter_count *count,
                          enum counter_function function);
    int (*action_read)(struct counter_device *counter,
                       struct counter_count *count,
                       struct counter_synapse *synapse,
                       enum counter_synapse_action *action);
    int (*action_write)(struct counter_device *counter,
                        struct counter_count *count,
                        struct counter_synapse *synapse,
                        enum counter_synapse_action action);
};
```

Колбек `count_read` обов'язково повертає 64-бітне беззнакове значення `u64`. Якщо апаратний лічильник є 16-бітним або 32-бітним, драйвер відповідає за правильне розширення знаку або додавання програмного оверфлоу-лічильника перед поверненням значення.

## 2. Переліки (Enums) режимів та синаптичних дій

### Режими роботи лічильника `enum counter_function`

Енумерація `enum counter_function` описує логічний режим, у якому працює конкретний об'єкт `Count`.

- `COUNTER_FUNCTION_INCREASE`: значення лічильника інкрементується при кожному імпульсі на активному синапсі.
- `COUNTER_FUNCTION_DECREASE`: значення лічильника декрементується при кожному імпульсі.
- `COUNTER_FUNCTION_PULSE_DIRECTION`: перший сигнал генерує імпульси підрахунку, а другий сигнал визначає напрямок (високий рівень — додавання, низький — віднімання).
- `COUNTER_FUNCTION_QUADRATURE_X1_A`: квадратурний режим, при якому рахується лише передній фронт сигналу A, а стан сигналу B визначає знак (+1 чи -1).
- `COUNTER_FUNCTION_QUADRATURE_X2_A`: квадратурний режим, при якому рахуються передній та задній фронти сигналу A, а стан сигналу B визначає знак.
- `COUNTER_FUNCTION_QUADRATURE_X4`: повнофункціональний квадратурний режим, у якому рахуються абсолютно всі 4 фронти сигналів A і B на кожному електричному циклі.

### Синаптичні реакції `enum counter_synapse_action`

Енумерація `enum counter_synapse_action` задає правило реагування лічильника на зміни конкретного вхідного сигналу `Signal`.

- `COUNTER_SYNAPSE_ACTION_NONE`: події даного сигналу повністю ігноруються лічильником.
- `COUNTER_SYNAPSE_ACTION_RISING_EDGE`: фіксується лише перехід сигналу з логічного 0 у 1 (передній фронт).
- `COUNTER_SYNAPSE_ACTION_FALLING_EDGE`: фіксується лише перехід сигналу з логічної 1 у 0 (задній фронт).
- `COUNTER_SYNAPSE_ACTION_BOTH_EDGES`: фіксуються обидва переходи (і передній, і задній фронти).

### Логічні рівні сигналів `enum counter_signal_level`

Описує миттєвий стан вхідної лінії пристрою.

- `COUNTER_SIGNAL_LEVEL_LOW`: електричний рівень логічного нуля (0 V / GND).
- `COUNTER_SIGNAL_LEVEL_HIGH`: електричний рівень логічної одиниці (3.3 V / 5 V).

## 3. ABI подій символьного пристрою (`<uapi/linux/counter.h>`)

Інтерфейс подій символьного пристрою `/dev/counterX` дозволяє отримувати апаратні сповіщення з низькою затримкою. Користувацький простір налаштовує маску подій через системний виклик `ioctl` й читає фіксовані бінарні структури `counter_event`.

### Команди керування `ioctl`

У заголовочному файлі `<uapi/linux/counter.h>` визначено такі коди команд:

- `COUNTER_ADD_WATCH_IOCTL` (`_IOW('c', 0x00, struct counter_watch)`): додає новий об'єкт спостереження у список подій ядра.
- `COUNTER_ENABLE_EVENTS_IOCTL` (`_IO('c', 0x01)`): активує кільцевий буфер подій та дозволяє генерацію переривань у бік юзерспейсу.
- `COUNTER_DISABLE_EVENTS_IOCTL` (`_IO('c', 0x02)`): вимикає кільцевий буфер та зупиняє сповіщення.

### Структури бінарного ABI подій

Для уникнення розбіжностей ABI між 32-бітними та 64-бітними системами (наприклад, 32-бітний юзерспейс на 64-бітному ядрі ARM64/x86_64) структура `struct counter_event` має суворо вирівняний розмір 24 байти з явними падінг-полями (`pad[6]`).

```c
struct counter_watch {
    struct counter_component component;
    __u32 event;
    __u8 channel;
};

struct counter_event {
    __u64 timestamp;  /* Час виникнення події u64 (CLOCK_MONOTONIC, нс) */
    __u64 value;      /* 64-бітне значення лічильника на момент події */
    __u8 watch_id;    /* Унікальний ID спостерігача, призначений ядром */
    __u8 channel;     /* Номер апаратного каналу */
    __u8 pad[6];      /* Явне вирівнювання структури до 24 байтів */
};
```

Прийоми системного виклику `read()` повертають один або кілька цілісних екземплярів `struct counter_event`. Якщо буфер ядра переповнився до того, як програма прочитала дані, ядро повертає помилку `-EOVERFLOW`.

## 4. Ієрархія атрибутів у файловій системі sysfs

Підсистема Counter автоматично реєструє дерево атрибутів у файловій системі `sysfs` за шляхом `/sys/bus/counter/devices/counterX/` (або через символьне посилання у `/sys/class/counter/counterX/`).

### Стандартні файли пристрою

- `name`: [read-only, S_IRUGO] ASCII-рядок із назвою пристрою.
- `num_counts`: [read-only, S_IRUGO] десятичне число, що показує кількість логічних лічильників.
- `num_signals`: [read-only, S_IRUGO] кількість вхідних електричних сигналів.

### Атрибути каталогу `countY/`

Кожен логічний лічильник створює власну піддиректорію `countY/`, де `Y` — числовий індекс лічильника.

- `countY/count`: [read-write, S_IRUGO | S_IWUSR] поточне значення лічильника. Читання повертає ASCII-рядок із 64-бітним числом. Запис дозволяє скинути або встановити довільну позицію.
- `countY/function`: [read-write, S_IRUGO | S_IWUSR] поточна функція декодування (наприклад, `quadrature x4`, `pulse-direction`). Читання підтягує вибране значення, а читання списку припустимих функцій доступне через `countY/function_available`.
- `countY/ceiling`: [read-write, optional] верхня межа апаратного лічильника. При досягненні цього значення лічильник скидається в 0 або ґенерує подію `COUNTER_EVENT_OVERFLOW`.
- `countY/floor`: [read-write, optional] нижня межа підрахунку.
- `countY/synapseZ_action`: [read-write] дія синапсу `Z` відносно даного лічильника `Y` (наприклад, `both edges`, `rising edge`, `none`).

### Атрибути каталогу `signalX/`

Кожен вхідний сигнал утворює піддиректорію `signalX/`.

- `signalX/name`: [read-only] ім'я каналу (наприклад, `Index Z`, `Phase A`).
- `signalX/signal`: [read-only] миттєвий логічний рівень на фізичній ніжці пристрою (`high` або `low`).
