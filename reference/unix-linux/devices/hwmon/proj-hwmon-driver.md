# ⚙️ Мінімальний драйвер hwmon для датчика на I²C

Ось повний текст робочого драйвера — трохи більше за сотню рядків, які перетворюють мікросхему на двох дротах у каталог `/sys/class/hwmon/hwmonN` з файлами `temp1_input`, `temp1_max` і `temp1_max_hyst`. Контракт hwmon іззовні виглядає простим, і саме тому три його гострі кути — знак у зсуві, спільний на всіх покажчик регістра в мікросхемі й реєстрація теплової зони — знаходять кожного, хто пише такий драйвер уперше.

## Що на платі й що має вийти

Беремо мікросхему, сумісну з LM75. У неї чотири шістнадцятибітні регістри, до яких ходять командою «прочитати слово»: `0x00` — виміряна температура, лише читання; `0x03` — межа, за якою мікросхема сама здіймає тривогу на своїй ніжці; `0x02` — гістерезис, поріг повернення. Дев'ять значущих бітів вирівняні вліво в слові, крок — пів градуса, старший біт — знак. Розмова йде по [шині I²C](book:electronics/i2c): дві лінії, адреса пристрою, номер регістра, дані.

Слово на дротах їде старшим байтом уперед, а процесор у нас найімовірніше молодшим — тому в ядрі є окрема `i2c_smbus_read_word_swapped()`, яка переставляє байти сама. Це не косметика: звичайна `i2c_smbus_read_word_data()` віддасть те саме слово задом наперед, і температура вийде вигаданою.

Драйверу треба зробити рівно три речі: оголосити, які канали в нього є; вміти віддати й прийняти значення в мілі-градусах; прив'язатися до пристрою, коли той з'явиться на шині.

## Оголошення: канали, дії, чип

Оголошення — це два масиви й одна структура, і всі три статичні: нічого рахувати в них не треба.

```c
static const struct hwmon_channel_info * const ms_info[] = {
        HWMON_CHANNEL_INFO(chip, HWMON_C_REGISTER_TZ),
        HWMON_CHANNEL_INFO(temp,
                           HWMON_T_INPUT | HWMON_T_MAX | HWMON_T_MAX_HYST),
        NULL
};

static const struct hwmon_ops ms_ops = {
        .is_visible = ms_is_visible,
        .read       = ms_read,
        .write      = ms_write,
};

static const struct hwmon_chip_info ms_chip_info = {
        .ops  = &ms_ops,
        .info = ms_info,
};
```

`HWMON_CHANNEL_INFO(temp, …)` — макрос, що збирає на місці анонімну структуру з полем `.type = hwmon_temp` і масивом конфігурацій, по одному слову на канал. Каналів тут один, тому слово одне; було б два датчики — два слова через кому, і ядро створило б `temp1_*` та `temp2_*`. Перший рядок описує не канал вимірювання, а сам чип: тип `hwmon_chip` — це місце для властивостей, які стосуються всієї мікросхеми.

## Три зворотні виклики

`is_visible` вирішує долю кожного оголошеного атрибута: `0` — файла не буде взагалі, `0444` — тільки читання, `0644` — ще й запис для власника. Її кличуть один раз, при реєстрації, і не питають більше ніколи; змінити права на ходу через неї не вийде.

```c
static umode_t ms_is_visible(const void *drvdata, enum hwmon_sensor_types type,
                             u32 attr, int channel)
{
        if (type != hwmon_temp)
                return 0;

        switch (attr) {
        case hwmon_temp_input:
                return 0444;
        case hwmon_temp_max:
        case hwmon_temp_max_hyst:
                return 0644;
        default:
                return 0;
        }
}
```

`read` і `write` отримують ту саму трійку «тип, ознака, канал» — і перше, що варто помітити: `dev` у них **не** ваш `i2c_client`. Це пристрій hwmon, дитина вашого; його приватні дані ядро поставило само з того вказівника, який ви передали при реєстрації. Тому `dev_get_drvdata(dev)` тут повертає саме вашу структуру, а `to_i2c_client(dev)` поверне сміття.

```c
static int ms_read(struct device *dev, enum hwmon_sensor_types type,
                   u32 attr, int channel, long *val)
{
        struct minisens *data = dev_get_drvdata(dev);
        s16 raw;
        int ret;

        if (type != hwmon_temp)
                return -EOPNOTSUPP;

        switch (attr) {
        case hwmon_temp_input:
                ret = ms_read_temp(data, &raw);
                break;
        case hwmon_temp_max:
                ret = ms_read_reg(data, MS_REG_MAX, &raw);
                break;
        case hwmon_temp_max_hyst:
                ret = ms_read_reg(data, MS_REG_HYST, &raw);
                break;
        default:
                return -EOPNOTSUPP;
        }
        if (ret)
                return ret;

        *val = ms_reg_to_mc(raw);       /* мілі°C — одиниця задана типом каналу */
        return 0;
}

static int ms_write(struct device *dev, enum hwmon_sensor_types type,
                    u32 attr, int channel, long val)
{
        struct minisens *data = dev_get_drvdata(dev);
        int ret;
        u8 reg;

        if (type != hwmon_temp)
                return -EOPNOTSUPP;

        switch (attr) {
        case hwmon_temp_max:
                reg = MS_REG_MAX;
                break;
        case hwmon_temp_max_hyst:
                reg = MS_REG_HYST;
                break;
        default:
                return -EOPNOTSUPP;
        }

        mutex_lock(&data->lock);
        ret = i2c_smbus_write_word_swapped(data->client, reg, ms_mc_to_reg(val));
        mutex_unlock(&data->lock);
        return ret;
}
```

Гілки `default` тут мали б ніколи не спрацювати: ядро питає лише про те, що драйвер сам оголосив. Але оголошення й обробник — два різні місця, і розходяться вони на диво легко: додали в маску `HWMON_T_CRIT`, а гілку в `switch` дописати забули. `-EOPNOTSUPP` («операція не підтримується») — усталена в підсистемі відповідь на таку комбінацію; читання файла впаде з виразною помилкою замість того, щоб віддати випадкове число з неініціалізованої змінної.

## Кеш і замок

Тепер найважче — і найкоротше на вигляд. Кожне читання `temp1_input` — це справжня транзакція на шині, і на дротах вона з двох кроків: спершу в мікросхему їде номер регістра, потім звідти читається слово. Покажчик регістра в мікросхемі **один на всіх**, тому розривати ці кроки не можна. Коли драйвер робить їх однією командою SMBus, цілість забезпечує ядро: `i2c_smbus_read_word_swapped()` — це один обмін, і адаптер на його час замкнено. А щойно драйвер розкладає читання на два окремі виклики або вичитує підряд кілька регістрів, які мають бути узгоджені між собою, кроки двох процесів перемішуються — і другий перезаписує покажчик між кроками першого.

![Два читачі на одній шині без замка й із замком](/reference/unix-linux/devices/hwmon/img/bus-race.svg)

*Помилка тут особливо підступна тим, що обидва читання успішні: жодного коду помилки, просто в `temp1_input` час від часу з'являється значення межі.*

Той самий м'ютекс закриває й кеш — інакше один потік міг би побачити оновлений час поруч зі старим значенням. Що таке [м'ютекс у ядрі й де ним не можна користуватися](book:unix-linux/kernel-locking), варто знати окремо: тут ми в контексті процесу, який має право спати, тож звичайний `mutex` доречний; в обробнику переривання довелося б брати спінлок.

```c
#define MS_CACHE_TTL (HZ / 2)           /* пів секунди */

struct minisens {
        struct i2c_client *client;
        struct mutex lock;              /* закриває і шину, і кеш */
        unsigned long stamp;            /* jiffies останнього успішного читання */
        bool valid;
        s16 raw;                        /* сире слово регістра температури */
};

static int ms_read_reg(struct minisens *data, u8 reg, s16 *out)
{
        int ret;

        mutex_lock(&data->lock);
        ret = i2c_smbus_read_word_swapped(data->client, reg);
        mutex_unlock(&data->lock);
        if (ret < 0)
                return ret;
        *out = (s16)ret;                /* функція вертає int: 0xE480 приїде як 58496 */
        return 0;
}

static int ms_read_temp(struct minisens *data, s16 *out)
{
        int ret = 0;

        mutex_lock(&data->lock);
        if (!data->valid || time_after(jiffies, data->stamp + MS_CACHE_TTL)) {
                ret = i2c_smbus_read_word_swapped(data->client, MS_REG_TEMP);
                if (ret < 0)
                        goto out;
                data->raw = (s16)ret;
                data->stamp = jiffies;
                data->valid = true;
                ret = 0;
        }
        *out = data->raw;
out:
        mutex_unlock(&data->lock);
        return ret;
}
```

`jiffies` — лічильник тиків ядра, `HZ` — скільки їх на секунду; порівнювати їх треба саме через `time_after()`, а не знаком «більше», бо лічильник переповнюється й на 32-бітній системі робить це за лічені тижні (детальніше — [час у ядрі](book:unix-linux/kernel-timekeeping)). Позначку часу оновлюємо **лише після успіху**: інакше невдале читання поставило б свіжий штамп, і півсекунди драйвер віддавав би старе значення, вважаючи його новим.

> 🔧 **Навіщо це.** Панель у стільниці, служба нагляду й збирач метрик легко опитують той самий датчик одночасно й із різною частотою. Без кешу вони втроє довше тримають шину, на якій, буває, висить не тільки термометр; без замка — час від часу читають чуже. Обидві біди мовчазні: у логах порожньо, у графіку — зубець.

## Знак, який легко загубити

`i2c_smbus_read_word_swapped()` повертає `int`, бо мусить лишити місце під від'ємні коди помилок. Значення слова приїжджає в ньому як додатне число від 0 до 65535 — і саме тут ламається перетворення, якщо взяти для нього беззнаковий тип.

![Одне слово, два типи змінної, два різні результати](/reference/unix-linux/devices/hwmon/img/sign-extension.svg)

*Над беззнаковим типом зсув вправо затягує згори нулі, над знаковим — копії старшого біта; компілятор не бачить у першому варіанті нічого підозрілого.*

```c
/* Дев'ять значущих бітів вирівняні вліво, крок — пів градуса.
   Тип ОБОВ'ЯЗКОВО знаковий: інакше зсув затягне нулі замість знака. */
static long ms_reg_to_mc(s16 reg)
{
        return (reg >> 7) * 500;
}

static u16 ms_mc_to_reg(long mc)
{
        mc = clamp_val(mc, -55000, 125000);
        return (u16)(s16)(DIV_ROUND_CLOSEST(mc, 500) * 128);
}
```

У зворотному перетворенні замість зсуву вліво стоїть множення на 128 — те саме число, але без зсуву від'ємного значення, поведінка якого в C описана не для всіх випадків. `clamp_val()` тут не перестраховка: у `temp1_max` записує людина, і `echo 100000 > temp1_max` без затиску перетворився б на сміття в регістрі мікросхеми, яка мовчки почала б здіймати тривогу на випадковому порозі.

## Прив'язка: таблиця збігу й probe

Драйвер сам себе ні до чого не чіпляє. Він реєструється на шині з таблицею імен, а далі ядро зіставляє ці імена з описом заліза й кличе `probe` (як саме — [прив'язка драйвера до пристрою](book:unix-linux/driver-probe-and-binding)). Для I²C таблиць дві: `of_match_table` зіставляє рядок `compatible` із [дерева пристроїв](book:unix-linux/device-tree), `id_table` — старе ім'я, яким користуються платформи без дерева.

```c
static int ms_probe(struct i2c_client *client)
{
        struct device *dev = &client->dev;
        struct minisens *data;
        struct device *hwmon;

        if (!i2c_check_functionality(client->adapter, I2C_FUNC_SMBUS_WORD_DATA))
                return -EOPNOTSUPP;

        data = devm_kzalloc(dev, sizeof(*data), GFP_KERNEL);
        if (!data)
                return -ENOMEM;

        data->client = client;
        mutex_init(&data->lock);

        hwmon = devm_hwmon_device_register_with_info(dev, "minisens", data,
                                                     &ms_chip_info, NULL);
        return PTR_ERR_OR_ZERO(hwmon);
}

static const struct i2c_device_id ms_ids[] = { { "minisens" }, { } };
MODULE_DEVICE_TABLE(i2c, ms_ids);

static const struct of_device_id ms_of_match[] = {
        { .compatible = "example,minisens" },
        { }
};
MODULE_DEVICE_TABLE(of, ms_of_match);

static struct i2c_driver ms_driver = {
        .driver = {
                .name           = "minisens",
                .of_match_table = ms_of_match,
        },
        .probe    = ms_probe,
        .id_table = ms_ids,
};
module_i2c_driver(ms_driver);
```

Префікс `devm_` означає «прив'язано до життя пристрою»: і пам'ять, і пристрій hwmon ядро звільнить само при відв'язуванні драйвера, у зворотному до виділення порядку. Тому в цьому драйвері немає ані `remove`, ані жодного `kfree` — і немає цілого класу помилок, у яких пам'ять звільнили раніше, ніж зник файл, з якого її читають. Перевірка `i2c_check_functionality()` теж не формальна: не кожен контролер уміє команду «слово», і краще відмовитися в `probe`, ніж отримувати `-EOPNOTSUPP` на кожному читанні.

## `HWMON_C_REGISTER_TZ`: віддати температуру тепловому каркасу

Один прапорець у першому рядку оголошення робить те, чого драйвер не робить сам: ядро реєструє наші канали температури як джерела для теплового каркаса. Умови жорсткі й мовчазні. Перший елемент масиву `info` мусить бути саме типу `hwmon_chip` і нести `HWMON_C_REGISTER_TZ` у першому слові конфігурації; пристрій має походити з дерева пристроїв; драйвер має зворотний виклик `read`. Далі ядро обходить усі канали типу `hwmon_temp`, бере ті, що оголосили `HWMON_T_INPUT` і яким `is_visible` не повернула нуль, і реєструє кожен як сенсор теплової зони.

Користь з'являється тоді, коли в дереві пристроїв є зона, яка на нас посилається:

```
minisens: temperature-sensor@4c {
        compatible = "example,minisens";
        reg = <0x4c>;
        #thermal-sensor-cells = <1>;
};

thermal-zones {
        board-thermal {
                thermal-sensors = <&minisens 0>;
                trips { … };
                cooling-maps { … };
        };
};
```

З цієї миті політикою опікується вже [тепловий каркас ядра](book:unix-linux/thermal-framework): точки спрацювання, прив'язані вентилятори, обмеження частоти. Драйвер про це нічого не знає — він і далі просто віддає число. Якщо ж зони в дереві немає, ядро проковтне це мовчки: жодної помилки не буде, і прапорець просто ні на що не вплине. Це головна пастка — «увімкнув, а нічого не сталося» тут означає не зламаний драйвер, а незаповнене дерево.

## Читач із простору користувача

Каталог `hwmonN` — не адреса: номер відображає лише порядок реєстрації цього разу. Шукати треба за вмістом файла `name`.

:::tabs
```python
#!/usr/bin/env python3
"""Знайти пристрій hwmon за вмістом name і прочитати temp1_input."""
import sys
from pathlib import Path

want = sys.argv[1] if len(sys.argv) > 1 else "minisens"

for node in sorted(Path("/sys/class/hwmon").glob("hwmon*")):
    try:
        if (node / "name").read_text().strip() != want:
            continue
        milli = int((node / "temp1_input").read_text())
    except OSError:
        continue          # пристрій міг зникнути між переліком і читанням
    print(f"{node.name}: {milli / 1000:.3f} °C")
    sys.exit(0)

sys.exit(f"пристрій «{want}» не знайдено")
```
```c
/* hwmon-find.c — знайти пристрій hwmon за вмістом name і прочитати temp1_input.
   Складання: cc -O2 -Wall -Wextra -o hwmon-find hwmon-find.c
   Запуск:    ./hwmon-find minisens */
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int slurp(const char *path, char *buf, size_t n)
{
        FILE *f = fopen(path, "r");
        int ok;

        if (!f)
                return -1;
        ok = fgets(buf, (int)n, f) ? 0 : -1;
        fclose(f);
        if (ok == 0)
                buf[strcspn(buf, "\n")] = '\0';
        return ok;
}

int main(int argc, char **argv)
{
        const char *want = argc > 1 ? argv[1] : "minisens";
        char path[512], buf[64];
        struct dirent *e;
        DIR *d = opendir("/sys/class/hwmon");

        if (!d)
                return 1;

        while ((e = readdir(d))) {
                if (strncmp(e->d_name, "hwmon", 5))
                        continue;
                snprintf(path, sizeof(path), "/sys/class/hwmon/%s/name", e->d_name);
                if (slurp(path, buf, sizeof(buf)) || strcmp(buf, want))
                        continue;
                snprintf(path, sizeof(path), "/sys/class/hwmon/%s/temp1_input",
                         e->d_name);
                if (slurp(path, buf, sizeof(buf)))
                        continue;
                printf("%s: %.3f °C\n", e->d_name, atoi(buf) / 1000.0);
                closedir(d);
                return 0;
        }
        closedir(d);
        fprintf(stderr, "пристрій «%s» не знайдено\n", want);
        return 1;
}
```
:::

Обидва варіанти читають каталог заново при кожному запуску — і це навмисно. Довготривала служба має або перечитувати `name` при старті кожної сесії, або тримати відкритим дескриптор `temp1_input`: він переживе перенумерування, але не переживе від'єднання пристрою й почне повертати помилку.

## Що зміниться на справжньому чипі

Тут один канал, і аргумент `channel` у зворотних викликах ні на що не впливає. На мікросхемі з шістьма входами він стає головним: `switch` розростається на два рівні, а кеш перестає бути одним значенням. У більшості наглядачів плати всі величини вичитуються однією серією транзакцій, тому вигідно тримати в структурі цілий знімок регістрів із однією позначкою часу — тоді шість файлів, прочитаних поспіль, покажуть узгоджену між собою картину, а не шість моментів із різницею в мілісекунди.

А ось `is_visible` на справжньому чипі зазвичай перестає бути таблицею констант. Одна й та сама мікросхема часто випускається в кількох варіантах — із термістором і без, із чотирма входами й із двома, — і драйвер, розпізнавши варіант у `probe`, ховає зайві атрибути, повернувши для них нуль. Саме тому `drvdata` передають у `is_visible` першим аргументом: на момент її виклику пристрою hwmon ще не існує, а знати, з чим маємо справу, вже треба.
