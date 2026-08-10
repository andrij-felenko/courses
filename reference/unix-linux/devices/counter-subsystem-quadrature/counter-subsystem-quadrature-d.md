# Підсистема лічильників ядра Counter subsystem (Hardware Quadrature Encoders)

<preknowlist>
- [Концепції ядра Linux](book:unix-linux/kernel-and-userspace) — базові поняття системних викликів та VFS.
</preknowlist>

## Вступ

Підсистема лічильників (Counter subsystem) у ядрі Linux — це спеціалізований фреймворк, розроблений для підтримки та керування апаратними лічильниками, енкодерами, таймерами та подібними пристроями. Зі стрімким розвитком робототехніки, промислової автоматизації та вбудованих систем виникла гостра потреба у стандартизації доступу до апаратних лічильників, зокрема квадратурних енкодерів (Quadrature Encoders). 

До появи Counter subsystem драйвери лічильників були розпорошені по різних підсистемах (IIO, input, misc), що призводило до дублювання коду та нестандартних користувацьких інтерфейсів (API). Підсистема Counter пропонує уніфіковану абстракцію для апаратних лічильників, забезпечуючи зручний інтерфейс через sysfs та character device вузли.

Ця стаття детально розглядає архітектуру підсистеми Counter, ключові структури даних (такі як `struct counter_device`), принципи роботи квадратурних енкодерів, інтерфейс `/sys/bus/counter/` та методи розробки драйверів для лічильників.

## Що таке квадратурний енкодер?

Квадратурний енкодер (Quadrature Encoder) — це електромеханічний пристрій, який перетворює кутове або лінійне положення, швидкість та напрямок обертання у цифрові сигнали. Принцип дії заснований на генерації двох імпульсних сигналів (зазвичай позначаються як Канал A та Канал B), які зсунуті по фазі на 90 градусів один відносно одного (у квадратурі).

### Принцип роботи

1. **Фазовий зсув**: Сигнали A і B зсунуті на 90 електричних градусів.
2. **Визначення напрямку**: Якщо сигнал A випереджає B (тобто A змінює стан раніше за B), енкодер обертається в одному напрямку (наприклад, за годинниковою стрілкою). Якщо B випереджає A — в протилежному.
3. **Визначення положення**: Підрахунок кількості імпульсів або фронтів (rising/falling edges) дозволяє точно визначити зміну положення.
4. **Індексний канал (Z)**: Багато енкодерів мають додатковий канал Z, який генерує один імпульс на оберт. Він використовується для скидання лічильника або визначення абсолютної нульової позиції.

### Типи декодування

Залежно від того, як обробляються фронти сигналів A і B, розрізняють три режими декодування:
- **X1 декодування**: Рахується лише один тип фронту (наприклад, передній) одного каналу (наприклад, A).
- **X2 декодування**: Рахуються обидва фронти (передній і задній) одного каналу (наприклад, A).
- **X4 декодування**: Рахуються всі фронти (і передні, і задні) обох каналів (A і B). Це забезпечує максимальну роздільну здатність.

## Архітектура підсистеми Counter

Підсистема Counter базується на кількох основних абстракціях, які дозволяють гнучко описувати будь-яку конфігурацію лічильників.

1. **Signal (Сигнал)**: Представляє фізичне джерело вхідних даних, таке як канал A або канал B енкодера. Сигнал має певні рівні та стани.
2. **Count (Підрахунок / Лічильник)**: Представляє логічний акумулятор, який підраховує події. Це значення, яке безпосередньо змінюється апаратним забезпеченням.
3. **Synapse (Синапс)**: Представляє зв'язок між Сигналом і Лічильником. Визначає, як зміни в Сигналі впливають на Лічильник (наприклад, фронт сигналу A збільшує лічильник).
4. **Extension (Розширення)**: Використовується для експорту специфічних для пристрою або лічильника властивостей (наприклад, конфігурація фільтрів, максимальне значення, напрямок).
5. **Function (Функція)**: Визначає режим роботи Лічильника на основі вхідних Сигналів через Синапси (наприклад, режим квадратурного енкодера X4).
6. **Action (Дія)**: Визначає, як конкретний стан або зміна Сигналу (через Синапс) впливає на підрахунок (наприклад, збільшення на передньому фронті).

## Основні структури даних

Для розробки драйвера Counter subsystem необхідно працювати з набором структур, визначених у `<linux/counter.h>`.

### struct counter_device

Це головна структура, яка описує пристрій лічильника.

```c
struct counter_device {
    struct device dev;
    const char *name;
    struct counter_device_parent *parent;
    const struct counter_ops *ops;
    struct counter_signal *signals;
    size_t num_signals;
    struct counter_count *counts;
    size_t num_counts;
    struct counter_ext *ext;
    size_t num_ext;
    void *priv;
};
```

- `name`: Назва пристрою.
- `parent`: Вказівник на батьківський пристрій (для sysfs).
- `ops`: Вказівник на структуру `counter_ops`, яка містить колбеки для читання/запису.
- `signals`, `num_signals`: Масив доступних сигналів та їх кількість.
- `counts`, `num_counts`: Масив логічних лічильників та їх кількість.
- `ext`, `num_ext`: Масив розширень пристрою.
- `priv`: Приватні дані драйвера.

### struct counter_count

Описує логічний лічильник.

```c
struct counter_count {
    int id;
    const char *name;
    const enum counter_function *functions_list;
    size_t num_functions;
    struct counter_synapse *synapses;
    size_t num_synapses;
    struct counter_ext *ext;
    size_t num_ext;
};
```

- `id`: Унікальний ідентифікатор лічильника в межах пристрою.
- `functions_list`: Масив підтримуваних функцій (наприклад, `COUNTER_FUNCTION_QUADRATURE_X4`).
- `synapses`: Масив синапсів, що підключають сигнали до цього лічильника.

### struct counter_signal

Описує вхідний сигнал.

```c
struct counter_signal {
    int id;
    const char *name;
    struct counter_ext *ext;
    size_t num_ext;
};
```

### struct counter_synapse

Описує зв'язок "Сигнал -> Лічильник".

```c
struct counter_synapse {
    const enum counter_synapse_action *actions_list;
    size_t num_actions;
    struct counter_signal *signal;
};
```

- `actions_list`: Які дії може виконувати цей сигнал на лічильнику (наприклад, `COUNTER_SYNAPSE_ACTION_RISING_EDGE`).
- `signal`: Вказівник на пов'язаний сигнал.

### struct counter_ops

Колбеки для взаємодії ядра з апаратним забезпеченням.

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

## Інтерфейс користувача: /sys/bus/counter/ та Character Devices

Підсистема Counter надає два основних способи взаємодії з користувацьким простором: через `sysfs` для конфігурації та повільного читання, та через файли символьних пристроїв (`/dev/counterX`) для швидкого читання та обробки подій.

### Sysfs інтерфейс

Після реєстрації `counter_device`, у `/sys/bus/counter/devices/counterX/` (або просто `/sys/class/counter/counterX/`) з'являється ієрархія файлів.

Основні атрибути:
- `name`: Назва пристрою.
- `countY/count`: Значення лічильника Y. Може бути прочитане або записане (якщо підтримується).
- `countY/function`: Поточна функція лічильника Y (наприклад, `quadrature x4`).
- `countY/synapseZ_action`: Дія, яку виконує синапс Z (який пов'язаний з певним сигналом) на лічильнику Y.
- `signalX/signal`: Поточний логічний рівень сигналу X (high/low).

Розширення (`extensions`) створюють додаткові файли, наприклад, `countY/ceiling` для встановлення максимального значення, або `countY/direction` для читання напрямку.

### Події та Character Device

Для випадків використання, що вимагають низької затримки або відстеження моментів зміни значень (наприклад, досягнення лімиту, скидання за індексом), sysfs інтерфейс недостатньо швидкий. Для цього Counter subsystem підтримує генерацію подій (Counter Events).

Кожен пристрій має відповідний файл `/dev/counterX`. Програма користувача може використовувати виклики `ioctl` для налаштування маски подій, які потрібно відстежувати (наприклад, `COUNTER_EVENT_OVERFLOW`, `COUNTER_EVENT_INDEX`). Після налаштування програма використовує системні виклики `read()` (з підтримкою `poll()` / `select()`) для читання структур `counter_event`, які містять мітку часу (timestamp), тип події та значення лічильника на момент події.

## Розробка драйвера лічильника

Розглянемо базовий процес написання драйвера для апаратного квадратурного енкодера.

### Крок 1. Ініціалізація структур

```c
#include <linux/counter.h>
#include <linux/module.h>
#include <linux/platform_device.h>

struct my_encoder_priv {
    void __iomem *base;
};

/* Оголошення підтримуваних функцій */
static const enum counter_function my_encoder_functions[] = {
    COUNTER_FUNCTION_QUADRATURE_X4,
};

/* Оголошення підтримуваних дій для сигналів */
static const enum counter_synapse_action my_encoder_actions[] = {
    COUNTER_SYNAPSE_ACTION_BOTH_EDGES,
};

/* Сигнали */
static struct counter_signal my_encoder_signals[] = {
    {
        .id = 0,
        .name = "Channel A",
    },
    {
        .id = 1,
        .name = "Channel B",
    },
};

/* Синапси: прив'язка сигналів до лічильника */
static struct counter_synapse my_encoder_synapses[] = {
    {
        .actions_list = my_encoder_actions,
        .num_actions = ARRAY_SIZE(my_encoder_actions),
        .signal = &my_encoder_signals[0],
    },
    {
        .actions_list = my_encoder_actions,
        .num_actions = ARRAY_SIZE(my_encoder_actions),
        .signal = &my_encoder_signals[1],
    },
};

/* Логічний лічильник */
static struct counter_count my_encoder_counts[] = {
    {
        .id = 0,
        .name = "Position Counter",
        .functions_list = my_encoder_functions,
        .num_functions = ARRAY_SIZE(my_encoder_functions),
        .synapses = my_encoder_synapses,
        .num_synapses = ARRAY_SIZE(my_encoder_synapses),
    },
};
```

### Крок 2. Реалізація колбеків `counter_ops`

```c
static int my_encoder_count_read(struct counter_device *counter,
                                 struct counter_count *count,
                                 u64 *val)
{
    struct my_encoder_priv *priv = counter_priv(counter);
    
    /* Читання значення з регістрів пристрою */
    *val = readl(priv->base + 0x00);
    return 0;
}

static int my_encoder_function_read(struct counter_device *counter,
                                    struct counter_count *count,
                                    enum counter_function *function)
{
    /* Завжди X4 для цього драйвера */
    *function = COUNTER_FUNCTION_QUADRATURE_X4;
    return 0;
}

static int my_encoder_action_read(struct counter_device *counter,
                                  struct counter_count *count,
                                  struct counter_synapse *synapse,
                                  enum counter_synapse_action *action)
{
    *action = COUNTER_SYNAPSE_ACTION_BOTH_EDGES;
    return 0;
}

static const struct counter_ops my_encoder_ops = {
    .count_read = my_encoder_count_read,
    .function_read = my_encoder_function_read,
    .action_read = my_encoder_action_read,
};
```

### Крок 3. Реєстрація пристрою в probe

Замість прямого створення `struct counter_device`, слід використовувати API для виділення пристрою, що забезпечує правильне управління пам'яттю за допомогою devres.

```c
static int my_encoder_probe(struct platform_device *pdev)
{
    struct counter_device *counter;
    struct my_encoder_priv *priv;
    int ret;

    /* Виділення counter_device разом з приватною пам'яттю */
    counter = devm_counter_alloc(&pdev->dev, sizeof(*priv));
    if (!counter)
        return -ENOMEM;

    priv = counter_priv(counter);
    /* Ініціалізація priv->base, запит ресурсів тощо */

    counter->name = dev_name(&pdev->dev);
    counter->parent = &pdev->dev;
    counter->ops = &my_encoder_ops;
    counter->counts = my_encoder_counts;
    counter->num_counts = ARRAY_SIZE(my_encoder_counts);
    counter->signals = my_encoder_signals;
    counter->num_signals = ARRAY_SIZE(my_encoder_signals);

    /* Реєстрація counter device у системі */
    ret = devm_counter_add(&pdev->dev, counter);
    if (ret)
        dev_err(&pdev->dev, "Failed to add counter device\n");

    return ret;
}
```

## Висновки

Підсистема лічильників Linux забезпечує міцний та універсальний фундамент для інтеграції апаратних квадратурних енкодерів, таймерів і спеціалізованих лічильників. Абстрагування від фізичних сигналів, логічних синапсів та операцій підрахунку дозволяє розробникам описувати навіть найскладніші конфігурації апаратного забезпечення без створення кастомних sysfs інтерфейсів. Завдяки наявності швидких подій через `/dev/counterX`, ця підсистема відмінно підходить для задач жорсткого реального часу в робототехніці та промисловості.

---

> Цей документ підготовлено як частина довідника «Unix і Linux». Зміни та доповнення вносяться відповідно до процесу розробки ядра Linux.
