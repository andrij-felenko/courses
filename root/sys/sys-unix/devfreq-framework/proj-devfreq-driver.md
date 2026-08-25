# ⚙️ Реалізація devfreq-драйвера для апаратного блоку пам'яті

Інтеграція периферійного пристрою або контролера системної шини в підсистему devfreq вимагає від драйвера виконання двох базових завдань: періодичного збору апаратних метрик завантаження та безпечного виконання переходу між робочими точками через підсистему OPP (Operating Performance Points). Розгляньмо повноцінну реалізацію драйвера для контролера шини оперативної пам'яті `sample-bus-devfreq`.

### 1. Опис апаратної топології в Device Tree

Драйвер ядра не повинен містити «зашитих» у бінарний код таблиць напруг чи частот. Усі фізичні обмеження кристала виносяться у вузли дерева пристроїв (Device Tree). Джерелом даних для devfreq слугує стандартний вузол `operating-points-v2`.

Вузол пристрою визначає необхідні ресурси: базову адресу регістрів MMIO, генератор тактового сигналу шини, посилання на регулятор напруги живлення PMIC та посилання на таблицю доступних робочих точок:

```dts
/ {
    soc {
        #address-cells = <1>;
        #size-cells = <1>;

        bus_opp_table: opp-table-bus {
            compatible = "operating-points-v2";
            opp-shared;

            opp-100000000 {
                opp-hz = /bits/ 64 <100000000>;
                opp-microvolt = <800000>;
            };
            opp-200000000 {
                opp-hz = /bits/ 64 <200000000>;
                opp-microvolt = <850000>;
            };
            opp-400000000 {
                opp-hz = /bits/ 64 <400000000>;
                opp-microvolt = <950000>;
            };
            opp-800000000 {
                opp-hz = /bits/ 64 <800000000>;
                opp-microvolt = <1100000>;
            };
        };

        memory_bus: bus-controller@10040000 {
            compatible = "vendor,sample-bus-controller";
            reg = <0x10040000 0x1000>;
            clocks = <&cru CLK_BUS_SRC>;
            clock-names = "bus_clk";
            operating-points-v2 = <&bus_opp_table>;
            bus-supply = <&vdd_bus_regulator>;
        };
    };
};
```

Властивість `opp-shared` сигналізує ядру, що якщо інші периферійні вузли посилаються на цю саму таблицю (наприклад, внутрішні мости комутатора NoC), їхні робочі стани мають змінюватися синхронно.

---

### 2. Реалізація драйвера ядра Linux

Драйвер реєструє профіль пристрою `struct devfreq_dev_profile`. У ньому визначаються дві головні функції зворотного виклику:
1. `get_dev_status()` — опитує апаратні регістри лічильників і повертає час зайнятості пристрою (`busy_time`) та загальну тривалість вимірювання (`total_time`).
2. `target()` — приймає від активного регулятора бажану частоту, знаходить найближчу відповідну точку в таблиці OPP та ініціює перемикання частоти й напруги.

```c
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/devfreq.h>
#include <linux/pm_opp.h>
#include <linux/clk.h>
#include <linux/io.h>
#include <linux/slab.h>

#define REG_BUS_TOTAL_CYCLES   0x00
#define REG_BUS_BUSY_CYCLES    0x04
#define REG_BUS_CTRL           0x08
#define BUS_CTRL_RESET_COUNTERS BIT(0)

struct sample_bus_devfreq {
    struct device *dev;
    void __iomem *regs;
    struct clk *clk;
    struct devfreq *df;
    struct devfreq_dev_profile profile;
    struct mutex lock;
};

/* Зчитування апаратних метрик навантаження */
static int sample_bus_get_dev_status(struct device *dev,
                                     struct devfreq_dev_status *stat)
{
    struct sample_bus_devfreq *priv = dev_get_drvdata(dev);
    u32 total_cycles, busy_cycles;

    mutex_lock(&priv->lock);

    /* Зчитуємо 32-бітні лічильники апаратних циклів */
    total_cycles = readl_relaxed(priv->regs + REG_BUS_TOTAL_CYCLES);
    busy_cycles  = readl_relaxed(priv->regs + REG_BUS_BUSY_CYCLES);

    /* Скидаємо апаратні лічильники для наступного інтервалу вимірювання */
    writel_relaxed(BUS_CTRL_RESET_COUNTERS, priv->regs + REG_BUS_CTRL);

    stat->current_frequency = clk_get_rate(priv->clk);
    stat->total_time = total_cycles;
    stat->busy_time  = busy_cycles;
    stat->private_data = NULL;

    mutex_unlock(&priv->lock);
    return 0;
}

/* Встановлення цільової частоти, запрошеної регулятором */
static int sample_bus_target(struct device *dev, unsigned long *freq, u32 flags)
{
    struct dev_pm_opp *opp;
    int ret;

    /* Шукаємо найближчу доступну точку OPP, що задовольняє запит */
    opp = devfreq_recommended_opp(dev, freq, flags);
    if (IS_ERR(opp)) {
        dev_err(dev, "Не знайдено валідної точки OPP для частоти %lu Гц\n", *freq);
        return PTR_ERR(opp);
    }
    dev_pm_opp_put(opp);

    /* Застосовуємо зміну частоти та напруги через OPP API */
    ret = dev_pm_opp_set_rate(dev, *freq);
    if (ret) {
        dev_err(dev, "Помилка встановлення частоти %lu Гц: %d\n", *freq, ret);
        return ret;
    }

    return 0;
}

static int sample_bus_probe(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    struct sample_bus_devfreq *priv;
    int ret;

    priv = devm_kzalloc(dev, sizeof(*priv), GFP_KERNEL);
    if (!priv)
        return -ENOMEM;

    priv->dev = dev;
    mutex_init(&priv->lock);

    priv->regs = devm_platform_ioremap_resource(pdev, 0);
    if (IS_ERR(priv->regs))
        return PTR_ERR(priv->regs);

    priv->clk = devm_clk_get(dev, "bus_clk");
    if (IS_ERR(priv->clk))
        return dev_err_probe(dev, PTR_ERR(priv->clk), "Не вдалося отримати тактовий сигнал\n");

    /* Ініціалізація таблиці OPP з Device Tree */
    ret = devm_pm_opp_of_add_table(dev);
    if (ret)
        return dev_err_probe(dev, ret, "Помилка парсингу OPP таблиці з DT\n");

    /* Конфігурація регулятора напруги через OPP Framework */
    ret = devm_pm_opp_set_regulators(dev, (const char *[]){ "bus" }, 1);
    if (ret)
        return dev_err_probe(dev, ret, "Помилка реєстрації регулятора живлення\n");

    /* Заповнення структури профілю devfreq */
    priv->profile.polling_ms = 50; /* Інтервал опитування за замовчуванням: 50 мс */
    priv->profile.target = sample_bus_target;
    priv->profile.get_dev_status = sample_bus_get_dev_status;
    priv->profile.initial_freq = clk_get_rate(priv->clk);

    platform_set_drvdata(pdev, priv);

    /* Реєстрація керованого devfreq-пристрою з регулятором simple_ondemand */
    priv->df = devm_devfreq_add_device(dev, &priv->profile,
                                       DEVFREQ_GOV_SIMPLE_ONDEMAND, NULL);
    if (IS_ERR(priv->df))
        return dev_err_probe(dev, PTR_ERR(priv->df), "Помилка реєстрації devfreq\n");

    dev_info(dev, "Драйвер devfreq шини успішно зареєстровано, початкова частота: %lu Гц\n",
             priv->profile.initial_freq);
    return 0;
}

static const struct of_device_id sample_bus_of_match[] = {
    { .compatible = "vendor,sample-bus-controller" },
    { /* кінець списку */ }
};
MODULE_DEVICE_TABLE(of, sample_bus_of_match);

static struct platform_driver sample_bus_driver = {
    .probe = sample_bus_probe,
    .driver = {
        .name = "sample-bus-devfreq",
        .of_match_table = sample_bus_of_match,
    },
};
module_platform_driver(sample_bus_driver);

MODULE_AUTHOR("Antigravity Devfreq Team");
MODULE_DESCRIPTION("Devfreq драйвер для контролера системної шини пам'яті");
MODULE_LICENSE("GPL");
```

---

### 3. Детальний аналіз механізмів та архітектурних нюансів

Розгляньмо крок за кроком, що відбувається під час життєвого циклу драйвера та які приховані пастки можуть виникнути у виробничому коді:

#### Ініціалізація та керування керованими ресурсами (devres)
Використання префікса `devm_` (наприклад, `devm_kzalloc`, `devm_clk_get`, `devm_pm_opp_of_add_table`, `devm_devfreq_add_device`) забезпечує автоматичне звільнення всієї пам'яті, дескрипторів та OPP-структур у зворотному порядку, якщо функція `probe()` поверне помилку або якщо модуль буде вивантажено з ядра. Це усуває ризик витоку ресурсів та спрощує обробку помилок через макрос `dev_err_probe()`.

#### Робота з апаратними лічильниками завантаження
У функції `sample_bus_get_dev_status()` драйвер звертається до двох апаратних 32-бітних регістрів:
* `REG_BUS_TOTAL_CYCLES` — лічильник, який безупинно інкрементується на кожному такті системної шини.
* `REG_BUS_BUSY_CYCLES` — лічильник, який інкрементується лише тоді, коли шина здійснює активну передачу даних (сигнали AXI `VALID` та `READY` перебувають у високому стані).

Після зчитування значень драйвер надсилає команду скидання лічильників у регістр керування `REG_BUS_CTRL`. Це гарантує, що наступний виклик `get_dev_status()` через 50 мс виміряє чистий інтервал активності без накопичення попередньої історії.

#### Модель синхронізації та запобігання стану перегонів
Під час виконання коду драйвера різні підсистеми ядра можуть одночасно взаємодіяти з екземпляром devfreq:
1. Таймер робочої черги devfreq періодично викликає `get_dev_status()` у контексті системного потоку `kworker`.
2. Користувач або демон енергозбереження може в цей самий момент змінити частоту через запис у `/sys/class/devfreq/.../userspace/set_freq`, що спричиняє виклик `target()`.
3. Підсистема керування живленням може надіслати запит на призупинення роботи пристрою під час входу в стан сну (System Suspend).

Для захисту внутрішнього стану та доступу до регістрів MMIO структура драйвера містить м'ютекс `priv->lock`. Це запобігає стану перегонів (*race conditions*), коли скидання апаратних лічильників збігається в часі зі зміною дільників частоти в PLL.

#### Захист від переповнення та часові обмеження
Якщо тактова частота шини становить 800 МГц, 32-бітний регістр переповнюється за формулою:

```
T_overflow = 2³² / f_max
= 4294967296 / 800000000
≈ 5.368 секунд
```

Оскільки період опитування становить 50 мс, переповнення в штатному режимі неможливе. Проте, якщо система переходить у стан сну (Suspend) або якщо центральний процесор затримується на виконанні тривалого критичного обробника переривань (ISR), лічильник може переповнитися. У реальних промислових драйверах рекомендується або використовувати 64-бітні регістри, або зберігати попереднє значення лічильника та обчислювати беззнакову модульну різницю:

```
delta_cycles = current_cycles - previous_cycles
```

Завдяки властивостям беззнакової арифметики C (переповнення 32-бітного `u32` через нуль) різниця `current_cycles - previous_cycles` дає математично точну кількість минулих тактів за умови, що за інтервал сталося не більше одного циклічного переповнення.

#### Атомарність та безпека перемикання станів
У функції `sample_bus_target()` вкрай важливо уникати прямих викликів низькорівневих функцій `clk_set_rate()`. Перемикання частоти без узгодження з напругою живлення призводить до порушення часових затримок і зависання контролера пам'яті. Функція `dev_pm_opp_set_rate()` гарантує правильний порядок:
* При підвищенні частоти: спочатку підвищується напруга регулятора `bus-supply`, витримується апаратна пауза на стабілізацію лінії живлення, після чого змінюється дільник тактового генератора.
* При зниженні частоти: спочатку знижується частота шини, і лише після завершення перехідного процесу PLL знижується напруга живлення.

---

### 4. Налагодження та трасування devfreq-драйвера

Ядро Linux надає вбудовані точки трасування (tracepoints) для моніторингу роботи підсистеми devfreq. Розробник може відстежувати кожне рішення регулятора та кожен перехід частоти в реальному часі через інтерфейс `ftrace`:

```bash
# Увімкнення трасування подій devfreq
echo 1 > /sys/kernel/debug/tracing/events/devfreq/enable

# Перегляд журналу трасування
cat /sys/kernel/debug/tracing/trace_pipe
```

Вивід трасування містить точні часові мітки, назву пристрою, поточну та цільову частоти, а також розраховане завантаження:

```
<idle>-0  [002] d..1  124.582910: devfreq_monitor: devfreq_dev=10040000.bus-controller freq=200000000 busy_time=9500000 total_time=10000000
kworker-45 [001] ...1  124.583120: devfreq_frequency: devfreq_dev=10040000.bus-controller prev=200000000 target=400000000
```

Ці діагностичні інструменти дозволяють точно оцінити плавність перемикання робочих точок, перевірити відсутність паразитних стрибків частоти та оптимізувати параметри гістерезису для конкретної апаратної платформи.
