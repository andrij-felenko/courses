# Підсистема лічильників ядра Counter subsystem (Hardware Quadrature Encoders)

<preknowlist>
- [Ядро й простір користувача](book:unix-linux/kernel-and-userspace) — поділ привілеїв, перехід контексту та системні виклики.
- [Модель пристроїв у sysfs](book:unix-linux/sysfs-device-model) — kobject, атрибути sysfs та дерево /sys/devices.
- [Переривання, softirq і робочі черги](book:unix-linux/interrupts-bottom-halves) — обробка апаратних сигналів та відкладене виконання.
- [Керівний канал до драйвера: ioctl](book:unix-linux/ioctl-interface) — механіка керування символьними пристроями через ioctl.
</preknowlist>

Промисловий електромотор із кутовим оптичним енкодером на 4096 імпульсів на оберт при швидкості обертання 6000 обертів на хвилину генерує понад 1.6 мільйона електричних фронтів на секунду. Якщо спробувати обробляти кожен фронт сигналу через звичайні апаратні переривання процесора (IRQ) та програмний обробник GPIO, центральний процесор опиниться у стані неперервного шторму переривань. Контекст ядра перемикатиметься сотні тисяч разів на секунду, система пропустить частину фронтів, а точний облік позиції вала буде втрачено.

Щоб уникнути цього навантаження, сучасні мікроконтролери та системи на кристалі (SoC) оснащують спеціалізованими апаратними лічильниками — периферійними блоками QEI (Quadrature Encoder Interface) або розширеними таймерами з апаратним декодуванням фаз. Ці блоки автономно підраховують імпульси у внутрішніх 32-бітних регістрах без залучення ядра CPU.

Головна задача підсистеми **Counter (Counter subsystem)** у ядрі Linux — створити уніфікований шар абстракції над цим різноманітним апаратним забезпеченням, зв'язати фізичні електричні входи з логічними лічильниками та надати простору користувача прозорий інтерфейс через `sysfs` й символьні пристрої `/dev/counterX`.

## Фізика та математика квадратурного енкодера

Квадратурний енкодер перетворює обертовий або лінійний рух у два прямокутні цифрові сигнали, які позначаються як **Канал A** та **Канал B**. Ключова особливість квадратурного кодування полягає у тому, що електричний сигнал Каналу A зсунутий відносно Каналу B по фазі на 90 градусів (одна чверть періоду).

![Сигнали квадратурного енкодера](/reference/unix-linux/devices/counter-subsystem-quadrature/img/quadrature-signals.svg)
*Сигнали квадратурного енкодера (Канали A і B), фазовий зсув 90 градусів та режими декодування X1, X2, X4.*

### Визначення напрямку та декодування станів

Оскільки сигнали A та B зсунуті на 90 градусів, двобітна комбінація їхніх логічних рівнів `(A, B)` під час обертання вала змінюється за чітко визначеною послідовністю Грея.

При обертанні за годинниковою стрілкою (Forward / CW) послідовність станів має вигляд:

```
00 -> 10 -> 11 -> 01 -> 00
```

При обертанні проти годинникової стрілки (Reverse / CCW) послідовність змінюється на зворотну:

```
00 -> 01 -> 11 -> 10 -> 00
```

Апаратний декодер у кожен момент часу аналізує попередній стан `(A_old, B_old)` та новий стан `(A_new, B_new)`. Якщо відбувся перехід `00 -> 10`, лічильник збільшує своє значення на одиницю (+1). Якщо відбувся перехід `00 -> 01`, значення зменшується на одиницю (-1).

Переходи, у яких змінюються обидва біти одночасно (наприклад, `00 -> 11` або `10 -> 01`), є фізично неможливими при нормальному обертанні. Поява таких переходів сигналізує про виникнення помилки: перевищення максимально припустимої швидкості обертання, апаратний брязкіт контакту або наявність сильної електромагнітної перешкоди.

### Режими декодування X1, X2 та X4

Залежно від необхідної роздільної здатності та можливостей апаратури, підсистема лічильників дозволяє налаштовувати один із трьох режимів фіксації фронтів:

1. **Режим X1 (Pulse / Direction)**: апаратний блок фіксує лише передні фронти (rising edges) одного каналу (наприклад, A). На один повний електричний цикл (360 градусів) припадає 1 відлік лічильника.
2. **Режим X2**: апаратний блок фіксує як передній, так і задній фронт (rising & falling edges) каналу A. На один електричний цикл припадає 2 відліки.
3. **Режим X4 (Quadrature X4)**: підсистема підраховує абсолютно всі зміни станів — передні та задні фронти обох каналів A і B. Це дає 4 відліки на один електричний цикл, збільшуючи точність вимірювання позиції у 4 рази без заміни фізичного датчика.

Обчислення підсумкового значення роздільної здатності енкодера в режимі X4 виконується за схемою:

```
N_total = PPR × 4
[де PPR — кількість фізичних рисок/пазлів енкодера на оберт]
```

Для енкодера з `PPR = 1024` у режимі X4 підсумкова кількість відліків на один повний оберт вала складе:

```
N_total
= 1024 × 4           [застосування X4 декодування]
= 4096 відліків/оберт
```

### Індексний канал Z (Index Pulse)

Більшість оптичних та магнітних енкодерів мають третій фізичний вихід — **Канал Z (або Index / Reference)**. Цей сигнал ґенерує один вузький імпульс на один повний механічний оберт диска.

Сигнал Z використовується для апаратного скидання позиції у нуль (Zero Homing) або фіксації точного значення лічильника в момент проходження нульової позначки. Це дозволяє компенсувати накопичену помилку та прив'язати відносні імпульси енкодера до абсолютної системи координат механізму.

Детальніше про передісторію створення уніфікованої підсистеми для таких пристроїв можна прочитати у матеріалі [Історія створення підсистеми Counter](book:unix-linux/counter-subsystem-quadrature/hist-counter-subsystem-birth.md).

## Архітектурні абстракції Linux Counter Subsystem

Підсистема Counter описує будь-яке апаратне забезпечення через набір з п'яти базових логічних об'єктів. Це дозволяє репрезентувати як найпростіший одноканальний лічильник кнопок, так і складний багатоосьовий промисловий контролер руху.

![Архітектура підсистеми Counter](/reference/unix-linux/devices/counter-subsystem-quadrature/img/counter-architecture-abstractions.svg)
*Взаємозв'язок апаратних сигналів, синапсів, лічильників та інтерфейсів користувацького простору у ядрі Linux.*

### 1. Signal (Сигнал)
`Signal` репрезентує фізичну або логічну вхідну лінію пристрою. Це джерело подій. Наприклад, вхідний вихід фази A енкодера — це `Signal 0`, фази B — `Signal 1`, індексного каналу Z — `Signal 2`.

Сигнал може перебувати у двох логічних рівнях (`COUNTER_SIGNAL_LEVEL_LOW` та `COUNTER_SIGNAL_LEVEL_HIGH`).

### 2. Count (Лічильник)
`Count` репрезентує безпосередній логічний акумулятор (регістр лічильника), який зберігає поточне числове значення (`u64`). Пристрій може мати кілька об'єктів `Count` (наприклад, для трьох осей ЧПУ верстата X, Y, Z).

### 3. Synapse (Синапс)
`Synapse` визначає точний зв'язок між конкретним `Signal` та `Count`. Він задає правило, який саме електричний фронт даного сигналу здатний викликати зміну лічильника. Синапс визначає припустимі дії (`Action`):
- `COUNTER_SYNAPSE_ACTION_NONE`: сигнал не впливає на лічильник.
- `COUNTER_SYNAPSE_ACTION_RISING_EDGE`: лічильник реагує на передній фронт.
- `COUNTER_SYNAPSE_ACTION_FALLING_EDGE`: лічильник реагує на задній фронт.
- `COUNTER_SYNAPSE_ACTION_BOTH_EDGES`: лічильник реагує на обидва фронти.

### 4. Function (Функція)
`Function` визначає режим роботи об'єкта `Count`. Вона задає алгоритм, за яким підсистема інтерпретує дії синапсів. Приклади функцій: `COUNTER_FUNCTION_INCREASE`, `COUNTER_FUNCTION_PULSE_DIRECTION`, `COUNTER_FUNCTION_QUADRATURE_X4`.

### 5. Extension (Розширення)
`Extension` експортує специфічні атрибути пристрою, лічильника або сигналу у `sysfs`. Через розширення драйвер реалізує регулювання цифрових фільтрів брязкіту (`glitch_filter_ns`), встановлення верхньої межі підрахунку (`ceiling`), нижньої межі (`floor`) або читання поточного напрямку обертання (`direction`).

Повний перелік параметрів функцій та UAPI-структур наведено у матеріалі [Довідник ядерних структур та інтерфейсу підсистеми Counter](book:unix-linux/counter-subsystem-quadrature/api-counter-kernel-interface.md).

## Ядерні структури даних та програмування драйверів

Драйвер лічильника розробляється шляхом заповнення об'єкта `struct counter_device` та його реєстрації у підсистемі за допомогою devres-функцій.

### Головна структура `struct counter_device`

У заголовочному файлі `<linux/counter.h>` пристрій описується таким чином:

```c
struct counter_device {
    const char *name;
    struct device *parent;
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

Драйвер зв'язує фізичні операції читання та запису апаратних регістрів через структуру колбеків `struct counter_ops`:

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

### Передача подій з контексту переривання у кільцевий буфер

Коли апаратний блок лічильника фіксує переповнення або проходження індексного каналу Z, він генерує переривання. У списку апаратного обробника переривань (IRQ Handler) драйвер викликає ядерну функцію `counter_push_event()`:

```c
void counter_push_event(struct counter_device *counter, u8 event, u8 channel);
```

Ця функція зчитує поточний час з монотонного годинника `ktime_get_ns()`, отримує поточне значення лічильника з колбеку `count_read`, упаковує ці дані у бінарну структуру `struct counter_event` та додає її в кільцевий буфер пристрою (`kfifo`). Після цього функція викликає `wake_up_interruptible()`, сповіщаючи потік простору користувача, заблокований у виклику `poll()`.

### Приклад створення драйвера для апаратного енкодера

Розглянемо повну реалізацію базового драйвера для SoC платформи, який зчитує 32-бітний апаратний регістр лічильника енкодера.

```c
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/counter.h>
#include <linux/io.h>
#include <linux/interrupt.h>

struct my_encoder_priv {
    void __iomem *regs;
    int irq;
};

/* Припустимі режими роботи лічильника */
static const enum counter_function my_encoder_functions[] = {
    COUNTER_FUNCTION_QUADRATURE_X4,
    COUNTER_FUNCTION_PULSE_DIRECTION,
};

/* Припустимі дії для синапсів фаз A і B */
static const enum counter_synapse_action my_encoder_synapse_actions[] = {
    COUNTER_SYNAPSE_ACTION_BOTH_EDGES,
    COUNTER_SYNAPSE_ACTION_NONE,
};

/* Опис вхідних сигналів (Phase A, Phase B) */
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

/* Зв'язок сигналів A та B із лічильником */
static struct counter_synapse my_encoder_synapses[] = {
    {
        .actions_list = my_encoder_synapse_actions,
        .num_actions = ARRAY_SIZE(my_encoder_synapse_actions),
        .signal = &my_encoder_signals[0],
    },
    {
        .actions_list = my_encoder_synapse_actions,
        .num_actions = ARRAY_SIZE(my_encoder_synapse_actions),
        .signal = &my_encoder_signals[1],
    },
};

/* Опис об'єкта Count */
static struct counter_count my_encoder_counts[] = {
    {
        .id = 0,
        .name = "Channel 0 Position",
        .functions_list = my_encoder_functions,
        .num_functions = ARRAY_SIZE(my_encoder_functions),
        .synapses = my_encoder_synapses,
        .num_synapses = ARRAY_SIZE(my_encoder_synapses),
    },
};

/* Реалізація колбеків читання та запису */
static int my_encoder_count_read(struct counter_device *counter,
                                 struct counter_count *count,
                                 u64 *val)
{
    struct my_encoder_priv *priv = counter_priv(counter);
    *val = readl(priv->regs + 0x04); /* Регістр поточного значення */
    return 0;
}

static int my_encoder_count_write(struct counter_device *counter,
                                  struct counter_count *count,
                                  u64 val)
{
    struct my_encoder_priv *priv = counter_priv(counter);
    writel((u32)val, priv->regs + 0x04);
    return 0;
}

static int my_encoder_function_read(struct counter_device *counter,
                                    struct counter_count *count,
                                    enum counter_function *function)
{
    *function = COUNTER_FUNCTION_QUADRATURE_X4;
    return 0;
}

static const struct counter_ops my_encoder_ops = {
    .count_read = my_encoder_count_read,
    .count_write = my_encoder_count_write,
    .function_read = my_encoder_function_read,
};

/* Обробник апаратного переривання (IRQ) */
static irqreturn_t my_encoder_irq_handler(int irq, void *dev_id)
{
    struct counter_device *counter = dev_id;
    struct my_encoder_priv *priv = counter_priv(counter);
    u32 status = readl(priv->regs + 0x08); /* Регістр статусу переривання */

    if (status & 0x01) { /* Переповнення (Overflow) */
        writel(0x01, priv->regs + 0x08); /* Скидання прапорця */
        counter_push_event(counter, COUNTER_EVENT_OVERFLOW, 0);
        return IRQ_HANDLED;
    }

    return IRQ_NONE;
}

static int my_encoder_probe(struct platform_device *pdev)
{
    struct counter_device *counter;
    struct my_encoder_priv *priv;
    void __iomem *regs;
    int irq, ret;

    regs = devm_platform_ioremap_resource(pdev, 0);
    if (IS_ERR(regs))
        return PTR_ERR(regs);

    irq = platform_get_irq(pdev, 0);
    if (irq < 0)
        return irq;

    counter = devm_counter_alloc(&pdev->dev, sizeof(*priv));
    if (!counter)
        return -ENOMEM;

    priv = counter_priv(counter);
    priv->regs = regs;
    priv->irq = irq;

    counter->name = dev_name(&pdev->dev);
    counter->parent = &pdev->dev;
    counter->ops = &my_encoder_ops;
    counter->signals = my_encoder_signals;
    counter->num_signals = ARRAY_SIZE(my_encoder_signals);
    counter->counts = my_encoder_counts;
    counter->num_counts = ARRAY_SIZE(my_encoder_counts);

    ret = devm_request_irq(&pdev->dev, irq, my_encoder_irq_handler,
                           IRQF_SHARED, dev_name(&pdev->dev), counter);
    if (ret)
        return ret;

    return devm_counter_add(&pdev->dev, counter);
}

static const struct of_device_id my_encoder_of_match[] = {
    { .compatible = "vendor,quad-encoder-v1" },
    { /* sentinel */ }
};
MODULE_DEVICE_TABLE(of, my_encoder_of_match);

static struct platform_driver my_encoder_driver = {
    .probe = my_encoder_probe,
    .driver = {
        .name = "my-quad-encoder",
        .of_match_table = my_encoder_of_match,
    },
};
module_platform_driver(my_encoder_driver);

MODULE_AUTHOR("Industrial Embedded Developer");
MODULE_DESCRIPTION("Generic Hardware Quadrature Encoder Driver");
MODULE_LICENSE("GPL");
```

## Інтерфейси простору користувача: Sysfs проти Character Device

Підсистема Counter надає два паралельних інтерфейси доступу для програм користувацького простору.

### 1. Інтерфейс Sysfs (`/sys/bus/counter/devices/counterX/`)

Використовується для первинної конфігурації, налагодження та читання повільних значень. Дерево sysfs має такий вигляд:

```
/sys/bus/counter/devices/counter0/
├── count0/
│   ├── count                  # Поточне значення (64-бітне)
│   ├── ceiling                # Максимальне значення (переповнення)
│   ├── floor                  # Мінімальне значення
│   ├── function               # Режим (quadrature x4, pulse-direction)
│   └── synapse0_action        # Дія на синапсі 0 (both edges)
├── signal0/
│   ├── name                   # Назва ("Channel A")
│   └── signal                 # Логічний рівень (high/low)
├── name                       # Ім'я пристрою
└── num_counts                 # Кількість лічильників
```

Зчитування значення лічильника з командного рядка:

```bash
cat /sys/bus/counter/devices/counter0/count0/count
```

### 2. Події символьного пристрою (`/dev/counterX`)

Для реального часу та обробки високої частоти імпульсів ядро Linux реалізує символьний пристрій `/dev/counterX`. Замість опитування sysfs програма реєструє спостерігачів (Watches) через виклики `ioctl` та зчитує бінарні структури `struct counter_event`:

```c
struct counter_event {
    u64 timestamp; /* Наносекундна мітка часу CLOCK_MONOTONIC */
    u64 value;     /* Значення лічильника на момент події */
    u8 watch_id;   /* ID зареєстрованого спостерігача */
    u8 channel;    /* Номер каналу */
    u8 pad[6];
};
```

Виклики `ioctl` керування подіями:
- `COUNTER_ADD_WATCH_IOCTL`: додає об'єкт `counter_watch` (наприклад, подія `COUNTER_EVENT_OVERFLOW` або `COUNTER_EVENT_INDEX`).
- `COUNTER_ENABLE_EVENTS_IOCTL`: активує генерацію подій у кільцевому буфері ядра.

Програма може викликати `poll()` або `epoll()`, переходячи у стан сну до моменту виникнення апаратного переповнення або проходження індексного позначення Z.

Детальний приклад реалізації читача подій на C та C++ доступний у матеріалі [Практичний приклад читача подій у просторі користувача](book:unix-linux/counter-subsystem-quadrature/proj-counter-event-reader.md).

> 🔧 **Навіщо це.**
> Застосування символьного пристрою `/dev/counterX` дозволяє синхронізувати позиції виконавчих механізмів робота з наносекундними мітками часу `CLOCK_MONOTONIC`. Це необхідно для алгоритмів оцінки швидкості (диференціювання позиції за часом) та побудови зворотного зв'язку в PID-регуляторах без часового джиттеру, притаманного періодичному опитуванню sysfs.

## Порівняння з підсистемами IIO, GPIO та input

Рішення про використання підсистеми Counter замість альтернативних ядерних підсистем спирається на вимоги продуктивності та наявність апаратури:

- **Підсистема IIO (Industrial I/O)**: призначена для потокового знімання даних аналогових датчиків з регулярним періодом квантування. IIO надмірно важка для ізольованого підрахунку позиції й не має поняття синаптичних зв'язків між фазами A/B.
- **Підсистема GPIO (`gpiod`)**: обробка квадратурного енкодера через переривання `gpiod_to_irq()` прийнятна лише для повільного людського введення (наприклад, ручка гучності на панелі приладу). При частоті сигналів понад 1000 Гц програмна обробка через GPIO повністю виснажує процесорний час.
- **Підсистема Input (`evdev`)**: фокусується на генерації подій клавіатур та мишей. Використання `evdev` для енкодерів роботів створює зайвий оверхед на парсинг `input_event` та блокує масштабування.

## Продуктивність, розширення 32-бітних регістрів та крайові випадки

При роботі з апаратними лічильниками квадратурних енкодерів інженер стикається з кількома важливими апаратними обмеженнями.

### 1. Переповнення (Rollover) 32-бітних регістрів

Більшість апаратних таймерів у SoC (наприклад, STM32 або TI eQEP) мають 16-бітні або 32-бітні регістри підрахунку імпульсів. При тривалій роботі мотора у розімкненому напрямку лічильник неминуче досягає верхньої межі `2³² - 1` (4 294 967 295) і переповнюється до 0.

Для збереження непреривної 64-бітної позиції драйвер ядра обробляє переривання апаратного переповнення (Overflow IRQ) й оновлює верхні 32 біти програмного акумулятора:

```
N_64 = (Overflows × 2³²) + N_hw32
```

При обчисленні різниці позицій між двома вибірками `N_old` та `N_new` для 32-бітного регістра використовується беззнакове віднімання з явним приведенням типів, яке коректно враховує циклічний перехід через нуль:

```
ΔN = (int32_t)(N_new - N_old)
```

Якщо `N_old = 4294967290`, а `N_new = 5`, то обчислення дасть:

```
N_new - N_old
= 5 - 4294967290
= 11 (в беззнаковому 32-бітному арифметичному просторі)
```

### 2. Фільтрація брязкіту та перешкод (Glitch Filtering)

В умовах промислового цеху довгі кабелі енкодера піддаються високому рівню електромагнітних перешкод від частотних перетворювачів моторів. Наведені напруги можуть створювати хибні мікроімпульси (glitches) тривалістю в кілька наносекунд.

Апаратні блоки QEI містять цифрові фільтри (Digital Glitch Filters). Вони тактуються від системної частоти й вимагають, щоб новий логічний рівень тримався на вході протягом `N` послідовних тактів перед тим, як зміна буде передана до декодера. Підсистема Counter дозволяє налаштовувати тривалість фільтрації у наносекундах через sysfs-атрибут `glitch_filter_ns`.

### 3. Джиттер на межі фронту (Quadrature Jitter)

Якщо мотор зупинився точно у точці переходу сигналу з 0 в 1, механічна вібрація обладнання може викликати мікроскопічні коливання диска енкодера. Це призводить до постійного перемикання стану `00 <-> 10`.

У режимі X4 апаратний лічильник буде почергово робити `+1` та `-1`, тримаючи підсумкове значення позиції абсолютно стабільним. Однак якщо драйвер налаштовано на генерацію подій переривання при кожному фронті, вібрація на межі створить шторм переривань. Для запобігання цьому у конфігурації подій підсистеми Counter рекомендується підписуватися на розраховані події переповнення або проходження індексу, а не на сирі зміни логічного рівня сигналів.
