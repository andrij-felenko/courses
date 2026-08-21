# ⚙️ Драйвер контролера переривань для GPIO: розробка власного irqchip та домену

Периферійні контролери введення-виведення загального призначення (*GPIO — General Purpose Input/Output*) є найпоширенішим класом вторинних контролерів переривань у вбудованих системах та сучасних комп'ютерах. Майже будь-яка система на кристалі (*SoC*) містить один або кілька блоків GPIO, фізичні контакти яких можуть працювати не лише як цифрові входи чи виходи, але й як джерела асинхронних подій: фіксувати натискання кнопок користувача, зміну стану ліній готовності периферійних мікросхем або сигнали тривоги від зовнішніх датчиків.

Розробка драйвера такого контролера вимагає створення повноцінного моста між апаратурою та ядром Linux: реалізації низькорівневих методів `struct irq_chip`, реєстрації лінійного домену `struct irq_domain` та організації демультиплексування вхідного апаратного сигналу.

## Архітектурний вибір: ланцюговий обробник проти вкладеного потоку

Перш ніж писати код драйвера, інженер повинен визначити апаратний спосіб підключення контролера до центрального процесора. Від цього залежить вибір базової моделі обробки переривань у ядрі Linux:

1. **Контролери з відображенням у пам'ять (MMIO — *Memory-Mapped I/O*):** Регістри контролера розташовані безпосередньо в адресному просторі процесора (внутрішній блок SoC або PCI-пристрій). Читання та запис регістрів займають кілька тактів шини і виконуються атомарно. Для таких пристроїв застосовується **ланцюговий обробник переривань** (*Chained IRQ Handler*). Батьківське переривання викликає демультиплексор у жорсткому hardirq-контексті, який вичитує регістр статусу й послідовно запускає обробники активних пінів через `generic_handle_domain_irq()`.
2. **Контролери на повільних послідовних шинах (I2C, SPI):** Мікросхема розширювача (наприклад, MCP23017 або PCA9535) підключена через зовнішню шину. Щоб прочитати регістр статусу, драйвер повинен надіслати пакет по шині, що вимагає очікування відповіді та засинання потоку. Оскільки в hardirq-контексті спати суворо заборонено, для таких контролерів застосовується **вкладений потоковий обробник** (*Nested Threaded IRQ*). Батьківське переривання запускає потік ядра, всередині якого викликається `handle_nested_irq()`.

Нижче наведено повну реалізацію драйвера для 32-бітного контролера GPIO з прямим відображенням у пам'ять (MMIO).

## Реалізація драйвера ядра Linux

Драйвер реалізує структуру операцій `struct irq_chip` для керування апаратними регістрами маскування та квитування, а також використовує вбудовану в підсистему `gpiochip` підтримку доменів переривань:

```c
// SPDX-License-Identifier: GPL-2.0
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/gpio/driver.h>
#include <linux/interrupt.h>
#include <linux/io.h>
#include <linux/of.h>
#include <linux/spinlock.h>

#define GPIO_DATA_IN   0x00  /* Читання поточного стану пінів */
#define GPIO_DIR       0x04  /* Напрямок: 0 — вхід, 1 — вихід */
#define GPIO_INT_MASK  0x08  /* Дозвіл переривань: 1 — дозволено */
#define GPIO_INT_STAT  0x0C  /* Статус: Write-1-to-Clear */
#define GPIO_INT_TYPE  0x10  /* Чутливість: 0 — рівень, 1 — фронт */

#define MY_GPIO_NR_PINS 32

struct my_gpio_chip {
    struct gpio_chip  gc;
    void __iomem     *base;
    raw_spinlock_t    lock;       /* Захист MMIO регістрів у hardirq */
    int               parent_irq; /* Системний номер батьківського GIC */
};

/* Заборона генерації переривання на контакті */
static void my_gpio_irq_mask(struct irq_data *d)
{
    struct gpio_chip *gc = irq_data_get_irq_chip_data(d);
    struct my_gpio_chip *chip = gpiochip_get_data(gc);
    irq_hw_number_t hwirq = irqd_to_hwirq(d);
    unsigned long flags;
    u32 mask;

    raw_spin_lock_irqsave(&chip->lock, flags);
    mask = readl_relaxed(chip->base + GPIO_INT_MASK);
    mask &= ~BIT(hwirq);
    writel_relaxed(mask, chip->base + GPIO_INT_MASK);
    raw_spin_unlock_irqrestore(&chip->lock, flags);
}

/* Дозвіл генерації переривання на контакті */
static void my_gpio_irq_unmask(struct irq_data *d)
{
    struct gpio_chip *gc = irq_data_get_irq_chip_data(d);
    struct my_gpio_chip *chip = gpiochip_get_data(gc);
    irq_hw_number_t hwirq = irqd_to_hwirq(d);
    unsigned long flags;
    u32 mask;

    raw_spin_lock_irqsave(&chip->lock, flags);
    mask = readl_relaxed(chip->base + GPIO_INT_MASK);
    mask |= BIT(hwirq);
    writel_relaxed(mask, chip->base + GPIO_INT_MASK);
    raw_spin_unlock_irqrestore(&chip->lock, flags);
}

/* Квитування спрацьовування: скидання прапорця в регістрі статусу */
static void my_gpio_irq_ack(struct irq_data *d)
{
    struct gpio_chip *gc = irq_data_get_irq_chip_data(d);
    struct my_gpio_chip *chip = gpiochip_get_data(gc);
    irq_hw_number_t hwirq = irqd_to_hwirq(d);

    /* Апаратне скидання біта записом 1 (Write-1-to-Clear) без блокування */
    writel_relaxed(BIT(hwirq), chip->base + GPIO_INT_STAT);
}

/* Програмування електричної чутливості лінії */
static int my_gpio_irq_set_type(struct irq_data *d, unsigned int type)
{
    struct gpio_chip *gc = irq_data_get_irq_chip_data(d);
    struct my_gpio_chip *chip = gpiochip_get_data(gc);
    irq_hw_number_t hwirq = irqd_to_hwirq(d);
    unsigned long flags;
    u32 reg_val;

    raw_spin_lock_irqsave(&chip->lock, flags);
    reg_val = readl_relaxed(chip->base + GPIO_INT_TYPE);

    if (type & IRQ_TYPE_EDGE_BOTH) {
        reg_val |= BIT(hwirq);  /* Режим фронту */
        irq_set_handler_locked(d, handle_edge_irq);
    } else if (type & IRQ_TYPE_LEVEL_MASK) {
        reg_val &= ~BIT(hwirq); /* Режим рівня */
        irq_set_handler_locked(d, handle_level_irq);
    } else {
        raw_spin_unlock_irqrestore(&chip->lock, flags);
        return -EINVAL;
    }

    writel_relaxed(reg_val, chip->base + GPIO_INT_TYPE);
    raw_spin_unlock_irqrestore(&chip->lock, flags);
    return 0;
}

/* Налаштування пробудження системи з режиму сну */
static int my_gpio_irq_set_wake(struct irq_data *d, unsigned int on)
{
    struct gpio_chip *gc = irq_data_get_irq_chip_data(d);
    struct my_gpio_chip *chip = gpiochip_get_data(gc);

    /* Передаємо запит батьківському контролеру переривань */
    return irq_set_irq_wake(chip->parent_irq, on);
}

static const struct irq_chip my_gpio_irqchip = {
    .name         = "my-gpio-irq",
    .irq_mask     = my_gpio_irq_mask,
    .irq_unmask   = my_gpio_irq_unmask,
    .irq_ack      = my_gpio_irq_ack,
    .irq_set_type = my_gpio_irq_set_type,
    .irq_set_wake = my_gpio_irq_set_wake,
    .flags        = IRQCHIP_IMMUTABLE,
};

/* Батьківський каскадний демультиплексор */
static void my_gpio_irq_handler(struct irq_desc *desc)
{
    struct gpio_chip *gc = irq_desc_get_handler_data(desc);
    struct my_gpio_chip *chip = gpiochip_get_data(gc);
    struct irq_chip *parent_chip = irq_desc_get_chip(desc);
    unsigned long pending;
    int hwirq;

    chained_irq_enter(parent_chip, desc);

    /* Зчитуємо активні події, які не замасковані */
    pending = readl_relaxed(chip->base + GPIO_INT_STAT);
    pending &= readl_relaxed(chip->base + GPIO_INT_MASK);

    /* Викликаємо диспетчер для кожного активного піна */
    for_each_set_bit(hwirq, &pending, MY_GPIO_NR_PINS) {
        generic_handle_domain_irq(gc->irq.domain, hwirq);
    }

    chained_irq_exit(parent_chip, desc);
}

/* Зондування та ініціалізація периферійного пристрою */
static int my_gpio_probe(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    struct my_gpio_chip *chip;
    struct gpio_irq_chip *girq;
    int ret;

    chip = devm_kzalloc(dev, sizeof(*chip), GFP_KERNEL);
    if (!chip)
        return -ENOMEM;

    chip->base = devm_platform_ioremap_resource(pdev, 0);
    if (IS_ERR(chip->base))
        return PTR_ERR(chip->base);

    chip->parent_irq = platform_get_irq(pdev, 0);
    if (chip->parent_irq < 0)
        return chip->parent_irq;

    raw_spin_lock_init(&chip->lock);

    /* Забороняємо всі переривання на старті та очищуємо старі прапорці */
    writel_relaxed(0x00000000, chip->base + GPIO_INT_MASK);
    writel_relaxed(0xFFFFFFFF, chip->base + GPIO_INT_STAT);

    /* Налаштування базових параметрів GPIO */
    chip->gc.label = dev_name(dev);
    chip->gc.base = -1;
    chip->gc.ngpio = MY_GPIO_NR_PINS;
    chip->gc.parent = dev;
    chip->gc.owner = THIS_MODULE;

    /* Інтеграція підсистеми переривань у gpiochip */
    girq = &chip->gc.irq;
    gpio_irq_chip_set_chip(girq, &my_gpio_irqchip);
    girq->parent_handler = my_gpio_irq_handler;
    girq->num_parents = 1;
    girq->parents = devm_kcalloc(dev, 1, sizeof(*girq->parents), GFP_KERNEL);
    if (!girq->parents)
        return -ENOMEM;

    girq->parents[0] = chip->parent_irq;
    girq->default_type = IRQ_TYPE_NONE;
    girq->handler = handle_bad_irq;

    ret = devm_gpiochip_add_data(dev, &chip->gc, chip);
    if (ret)
        return dev_err_probe(dev, ret, "Не вдалося зареєструвати gpiochip\n");

    return 0;
}

static const struct of_device_id my_gpio_of_match[] = {
    { .compatible = "custom,my-gpio-controller" },
    { /* кінець таблиці */ }
};
MODULE_DEVICE_TABLE(of, my_gpio_of_match);

static struct platform_driver my_gpio_driver = {
    .probe = my_gpio_probe,
    .driver = {
        .name = "my-gpio-controller",
        .of_match_table = my_gpio_of_match,
    },
};
module_platform_driver(my_gpio_driver);

MODULE_AUTHOR("Linux Kernel Developer");
MODULE_DESCRIPTION("Драйвер контролера GPIO з підтримкою переривань irqchip");
MODULE_LICENSE("GPL");
```

## Покроковий розбір реалізації та підводні камені

Розробка надійного вторинного контролера переривань вимагає врахування тонких деталей синхронізації та взаємодії з апаратурою:

### 1. Суворе використання raw_spinlock_t

Усі операції з регістрами маскування та конфігурації виконуються під захистом `raw_spinlock_t`. У стандартному ядрі Linux звичайний `spinlock_t` та `raw_spinlock_t` еквівалентні. Проте в ядрі реального часу з патчами `PREEMPT_RT` звичайні спінлоки перетворюються на сплячі м'ютекси для зменшення затримок планування. Оскільки методи `irq_mask`, `irq_unmask` та `irq_set_type` викликаються підсистемою ядра з відключеними перериваннями процесора, спроба заснути призведе до негайної паніки ядра (*Kernel Panic: scheduling while atomic*). Використання `raw_spinlock_t` гарантує збереження атомарності за будь-якої конфігурації ядра.

### 2. Безблокувальне квитування за принципом Write-1-to-Clear

Метод `my_gpio_irq_ack` реалізований за допомогою одного виклику `writel_relaxed(BIT(hwirq), chip->base + GPIO_INT_STAT)` без використання спінлока. Більшість контролерів переривань реалізують семантику скидання бітів записом одиниці: запис 1 скидає відповідний тригер, тоді як запис 0 у сусідні розряди ніяк не змінює їхнього стану. Завдяки цьому драйверу не потрібно виконувати цикл читання-модифікації-запису (*Read-Modify-Write*), що виключає стан гонитви між різними процесорними ядрами та мінімізує затримку обробки.

Крім того, апаратне квитування за принципом Write-1-to-Clear захищає систему від втрати нових подій: якщо під час читання регістру статусу на сусідньому піні виникає новий перепад напруги, запис маски з одиницею лише для обробленого біта скине лише старий прапорець і не зачепить щойно встановлений новий біт.

### 3. Динамічне перемикання диспетчерів потоку

У методі `my_gpio_irq_set_type` драйвер аналізує прапорці запитаного типу переривання. Залежно від того, як налаштована лінія, функція `irq_set_handler_locked()` призначає або `handle_edge_irq`, або `handle_level_irq`. Це критично важливо:
- Якщо призначити `handle_edge_irq` для переривання за рівнем, виникне шторм переривань, оскільки лінія не маскуватиметься під час виконання драйвера пристрою.
- Якщо призначити `handle_level_irq` для переривання за фронтом, ядро замаскує лінію і пропустить повторні короткі імпульси, що надійдуть до завершення роботи першого обробника.

### 4. Каскадний демультиплексор та chained_irq_enter

Метод `my_gpio_irq_handler` є точкою входу, яку викликає батьківський контролер переривань (ARM GIC). Функції `chained_irq_enter()` та `chained_irq_exit()` виконують правильне квитування та маскування батьківської лінії GIC. Цикл `for_each_set_bit` сканує бітову маску тільки тих ліній, які одночасно активні в регістрі `GPIO_INT_STAT` та дозволені в регістрі `GPIO_INT_MASK`. Кожен знайдений біт передається у функцію `generic_handle_domain_irq()`, яка знаходить зареєстрований `struct irq_desc` у домені та запускає призначений flow-handler.

## Інтеграція з Device Tree

Для того щоб ядро Linux змогло автоматично зіставити вузол контролера у дереві пристроїв із нашим драйвером та дозволити іншим вузлам посилатися на його піни як на джерела переривань, у дереві пристроїв описується відповідний вузол:

```dts
my_gpio: gpio-controller@10000000 {
    compatible = "custom,my-gpio-controller";
    reg = <0x10000000 0x1000>;
    gpio-controller;
    #gpio-cells = <2>;
    interrupt-controller;
    #interrupt-cells = <2>;
    interrupt-parent = <&gic>;
    interrupts = <GIC_SPI 42 IRQ_TYPE_LEVEL_HIGH>;
};

user_button {
    compatible = "gpio-keys";
    button_0 {
        label = "User Button 0";
        gpios = <&my_gpio 5 GPIO_ACTIVE_LOW>;
        interrupt-parent = <&my_gpio>;
        interrupts = <5 IRQ_TYPE_EDGE_FALLING>;
    };
};
```

Властивість `#interrupt-cells = <2>` повідомляє підсистему ядра, що для адресації переривання потрібні два параметри: апаратний номер піна (0–31) та прапорець типу електричної чутливості (`IRQ_TYPE_EDGE_FALLING` або `IRQ_TYPE_LEVEL_HIGH`).

Коли драйвер клавіатури `gpio-keys` ініціалізується, ядро автоматично парсить посилання `interrupt-parent = <&my_gpio>`, звертається до зареєстрованого домену нашого контролера, викликає метод `map` і повертає готовий номер `virq`. Драйвер кнопки викликає `request_threaded_irq()`, не знаючи жодних деталей про MMIO-регістри контролера GPIO.

## Перевірка та діагностика в системі

Після завантаження драйвера перевірити реєстрацію нового контролера переривань можна за допомогою стандартних системних інтерфейсів:

```bash
# Перевірка реєстрації нового контролера та лічильників
cat /proc/interrupts | grep my-gpio

# Перевірка зв'язків у домені переривань через DebugFS
cat /sys/kernel/debug/irq/domains/summary

# Перевірка налаштування типу переривання через sysfs
cat /sys/kernel/debug/irq/irqs/$(cat /sys/class/gpio/gpio5/edge)
```

У виводі `/proc/interrupts` з'явиться новий рядок із назвою чіпа `my-gpio-irq`, а кожен пін, використаний периферійним драйвером (наприклад, кнопкою `gpio-keys`), отримає власний унікальний номер `virq` та коректно відображатиме кількість зафіксованих подій.
