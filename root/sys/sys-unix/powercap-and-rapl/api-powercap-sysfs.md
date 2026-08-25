# 📋 Інтерфейс підсистеми powercap: файлова структура sysfs, параметри обмежень та структури ядра

Цей довідник містить вичерпну специфікацію програмних інтерфейсів ядра Linux для керування лімітами енергоспоживання через віртуальну файлову систему `sysfs` та внутрішній API підсистеми `powercap` (`include/linux/powercap.h`). Довідник необхідний системним адміністраторам, розробникам низькорівневих сервісів моніторингу та авторам драйверів керування живленням для коректної навігації по дереву зон, зчитування лічильників мікроджоулів, обробки помилок та налаштування часових вікон обмеження потужності.

## 1. Файлова ієрархія sysfs (`/sys/class/powercap/`)

Підсистема powercap експортує ієрархію пристроїв у каталозі `/sys/class/powercap/`. Для платформ Intel та AMD з підтримкою RAPL кореневими контролерами є каталоги з префіксом `intel-rapl`.

Кожен рівень ієрархії відображає топологічну вкладеність фізичних або логічних доменів живлення. Символ двокрапки `:` у назві каталогу використовується як роздільник рівнів: ім'я `intel-rapl:0` відповідає сокету 0, `intel-rapl:0:0` — першій підзоні сокета 0 (обчислювальні ядра), а `intel-rapl:1:1` — другій підзоні сокета 1 (оперативна пам'ять у двосокетній системі).

```text
/sys/class/powercap/
├── intel-rapl/                      # Символьне посилання на активний клас пристроїв
├── intel-rapl:0/                    # Зона рівня сокета / Package 0
│   ├── name                         # Рядок "package-0"
│   ├── enabled                      # 1 (зона увімкнена) / 0 (вимкнена)
│   ├── energy_uj                    # Накопичена енергія у мікроджоулях (uJ)
│   ├── max_energy_range_uj          # Значення переповнення лічильника (uJ)
│   ├── max_power_range_uw           # Теоретична пікова потужність домену (uW)
│   ├── constraint_0_name            # "long_term" (PL1 / TDP)
│   ├── constraint_0_power_limit_uw  # Ліміт довготривалої потужності (uW)
│   ├── constraint_0_time_window_us  # Часове вікно інтегрування PL1 (us)
│   ├── constraint_0_max_power_uw    # Максимально допустиме значення ліміту PL1
│   ├── constraint_0_min_power_uw    # Мінімально допустиме значення ліміту PL1
│   ├── constraint_0_max_time_window_us # Максимальне підтримуване часове вікно
│   ├── constraint_0_min_time_window_us # Мінімальне підтримуване часове вікно
│   ├── constraint_1_name            # "short_term" (PL2 / Turbo Burst)
│   ├── constraint_1_power_limit_uw  # Ліміт короткочасної потужності (uW)
│   ├── constraint_1_time_window_us  # Часове вікно інтегрування PL2 (us)
│   ├── constraint_1_max_power_uw    # Максимально допустимий ліміт PL2
│   ├── constraint_1_min_power_uw    # Мінімально допустимий ліміт PL2
│   │
│   ├── intel-rapl:0:0/              # Підзона ядер процесора (Core / PP0)
│   │   ├── name                     # "core"
│   │   ├── enabled                  # 1 / 0
│   │   ├── energy_uj                # Енергія, спожита лише обчислювальними ядрами
│   │   ├── max_energy_range_uj
│   │   ├── constraint_0_name        # "long_term"
│   │   ├── constraint_0_power_limit_uw
│   │   └── constraint_0_time_window_us
│   │
│   ├── intel-rapl:0:1/              # Підзона оперативної пам'яті (DRAM)
│   │   ├── name                     # "dram"
│   │   ├── enabled
│   │   ├── energy_uj
│   │   ├── max_energy_range_uj
│   │   ├── constraint_0_name
│   │   ├── constraint_0_power_limit_uw
│   │   └── constraint_0_time_window_us
│   │
│   ├── intel-rapl:0:2/              # Підзона Uncore / вбудованої графіки (PP1)
│   │   ├── name                     # "uncore"
│   │   └── energy_uj
│   │
│   └── intel-rapl:0:3/              # Підзона всієї платформи (Psys)
│       ├── name                     # "psys"
│       ├── energy_uj
│       ├── constraint_0_power_limit_uw
│       └── constraint_0_time_window_us
│
└── intel-rapl:1/                    # Зона сокета / Package 1 (у двосокетних серверах)
    └── ...
```

## 2. Специфікація атрибутів зони керування (`powercap_zone`)

Кожен каталог зони містить системні файли, що описують поточний енергетичний стан компонента:

* **`name`** (тип `string`, доступ `0444 / RO`):
  Текстовий ідентифікатор зони. Для сокетів повертає `package-N`, для обчислювальних ядер — `core`, для оперативної пам'яті — `dram`, для позаядерної графіки — `uncore`, для повної материнської плати — `psys`. Застосунки повинні використовувати цей файл для динамічної ідентифікації доменів замість жорсткого кодування числових індексів, оскільки порядок ініціалізації підзон у sysfs може варіюватися між версіями ядра та різними поколіннями процесорів.
* **`enabled`** (тип `integer`, доступ `0644 / RW`):
  Прапорець глобальної активації лімітування для поточної зони. Запис символу `1` переводить зону в активний стан, дозволяючи апаратному контролеру застосовувати встановлені обмеження потужності. Запис символу `0` відключає всі обмеження зони, дозволяючи компоненту споживати максимум потужності в межах стандартного заводського профілю.
* **`energy_uj`** (тип `u64`, доступ `0400 / RO`):
  Накопичений лічильник спожитої енергії у **мікроджоулях** (`1 Дж = 1 000 000 мкДж`). Значення монотонно зростає до досягнення величини, зазначеної в `max_energy_range_uj`, після чого скидається в нуль і продовжує рахунок. Зчитування здійснюється як перетворення цілочисельного MSR-значення з урахуванням одиниці `Energy Status Unit`.
* **`max_energy_range_uj`** (тип `u64`, доступ `0444 / RO`):
  Апаратна межа переповнення 32-бітного лічильника MSR, переведена у мікроджоулі. Дозволяє користувацьким програмам коректно обчислювати різницю енергії `ΔE` при переході через нуль.
* **`max_power_range_uw`** (тип `u64`, доступ `0444 / RO`):
  Максимально можлива пікова потужність для даного домену у **мікроваттах** (`1 Вт = 1 000 000 мкВт`), обумовлена електричними характеристиками силіконового кристала та силових ліній живлення.

> ⚠️ **Політика безпеки прав доступу:** Внаслідок впровадження патчів проти вразливості Platypus (CVE-2020-8694) права на читання файлу `energy_uj` обмежені виключно суперкористувачем `root` (режим `0400`). Спроба відкриття файлу непривілейованим процесом повертає системну помилку `EACCES` (*Permission denied*).

## 3. Специфікація атрибутів обмежень (`powercap_constraint`)

Зона керування містить одну або дві групи атрибутів обмежень із префіксами `constraint_0_` (зазвичай довготривалий ліміт PL1) та `constraint_1_` (короткочасний турбо-ліміт PL2):

* **`constraint_X_name`** (тип `string`, доступ `0444 / RO`):
  Семантична назва правила. Значення `long_term` вказує на ліміт середнього теплопакета (TDP), `short_term` — на ліміт короткочасного пікового прискорення, `peak_power` — на миттєвий електричний ліміт захисту VRM (PL4).
* **`constraint_X_power_limit_uw`** (тип `u64`, доступ `0600 / RW`):
  Цільовий поріг потужності у **мікроваттах** (`uW`). Запис додатного значення встановлює новий поріг. Запис `0` знімає дане обмеження. При спробі встановити значення за межами дозволеного діапазону драйвер повертає помилку `-EINVAL`.
* **`constraint_X_time_window_us`** (тип `u64`, доступ `0600 / RW`):
  Часове вікно інтегрування середньої потужності у **мікросекундах** (`us`). Апаратура x86 використовує експоненційне кодування `(1 + X/4) · 2^Y · Time_Unit`. Якщо користувач записує довільне числове значення, драйвер ядра автоматично округлює його до найближчого дискретного апаратного кроку, тому після запису рекомендується виконати повторне читання для отримання точного встановленого часу.
* **`constraint_X_max_power_uw`** та **`constraint_X_min_power_uw`** (тип `u64`, доступ `0444 / RO`):
  Апаратні межі, в межах яких контролер здатний підтримувати стабільне регулювання. Встановлення ліміту нижче `min_power_uw` є небезпечним, оскільки може призвести до нестабільності напруги живлення ядра під час різкого скидання частоти.
* **`constraint_X_max_time_window_us`** та **`constraint_X_min_time_window_us`** (тип `u64`, доступ `0444 / RO`):
  Граничні значення тривалості ковзного вікна, підтримувані апаратними таймерами процесора.

## 4. Синхронізація, блокування та події uevent у ядрі

Всередині ядра Linux підсистема powercap захищає доступ до спільних структур даних за допомогою м'ютексів `powercap_zone.lock` та глобального блокування класу `powercap_control_type.lock`.

Під час зміни ліміту потужності або активації зони ядра послідовно виконує такі кроки:
1. Захоплює локальний м'ютекс відповідної зони `mutex_lock(&zone->lock)`;
2. Перевіряє діапазони через виклики таблиці `const_ops->get_min_power_uw` та `const_ops->get_max_power_uw`;
3. Викликає низькорівневий зворотний виклик драйвера `const_ops->set_power_limit_uw`, який здійснює безпосередній запис у MSR або MMIO;
4. Генерує подію ядра **uevent** (`KOBJ_CHANGE`) через підсистему kobject, сповіщаючи підписників у просторі користувача (демони udev, systemd) про зміну енергетичного профілю пристрою;
5. Звільняє м'ютекс `mutex_unlock(&zone->lock)`.

Така архітектура запобігає виникненню станів гонитви (race conditions) при одночасному записі параметрів декількома процесами моніторингу.

## 5. Коди помилок та крайові ситуації

Під час взаємодії з файлами підсистеми powercap системні виклики можуть повертати такі коди помилок:

* `-EACCES`: Спроба читання `energy_uj` або запису в `constraint_X_power_limit_uw` без привілеїв суперкористувача (`CAP_SYS_RAWIO` або `uid == 0`).
* `-EINVAL`: Передано некоректне значення потужності (від'ємне число, рядок із нечисловими символами або поріг, що перевищує `max_power_uw`).
* `-ENODEV` / `-ENOENT`: Запитуваний домен живлення не підтримується процесором або відповідний модуль драйвера (`intel_rapl_msr` чи `intel_rapl_tpmi`) не завантажено.
* `-EBUSY`: Конфлікт доступу до MSR або блокування апаратного інтерфейсу внутрішнім мікрокодом PCU/SMU.

## 6. Програмний API ядра Linux (`include/linux/powercap.h`)

Драйвери периферійних пристроїв та апаратні бекенди керування живленням використовують структури ядра для реєстрації нових зон та передачі зворотних викликів:

:::tabs
```c
#include <linux/powercap.h>

/* Таблиця операцій зони керування */
struct powercap_zone_ops {
    int (*get_energy_uj)(struct powercap_zone *zone, u64 *energy_uj);
    int (*reset_energy_uj)(struct powercap_zone *zone);
    int (*get_max_energy_range_uj)(struct powercap_zone *zone, u64 *max_uj);
    int (*get_power_uw)(struct powercap_zone *zone, u64 *power_uw);
    int (*set_enable)(struct powercap_zone *zone, bool mode);
    int (*get_enable)(struct powercap_zone *zone, bool *mode);
    int (*release)(struct powercap_zone *zone);
};

/* Таблиця операцій конкретного обмеження */
struct powercap_zone_constraint_ops {
    int (*set_power_limit_uw)(struct powercap_zone *zone, int cid, u64 power_uw);
    int (*get_power_limit_uw)(struct powercap_zone *zone, int cid, u64 *power_uw);
    int (*set_time_window_us)(struct powercap_zone *zone, int cid, u64 time_us);
    int (*get_time_window_us)(struct powercap_zone *zone, int cid, u64 *time_us);
    int (*get_max_power_uw)(struct powercap_zone *zone, int cid, u64 *power_uw);
    int (*get_min_power_uw)(struct powercap_zone *zone, int cid, u64 *power_uw);
    int (*get_max_time_window_us)(struct powercap_zone *zone, int cid, u64 *time_us);
    int (*get_min_time_window_us)(struct powercap_zone *zone, int cid, u64 *time_us);
    const char *(*get_name)(struct powercap_zone *zone, int cid);
};

/* Реєстрація зони контролю в підсистемі powercap */
struct powercap_zone *powercap_register_zone(
    struct powercap_zone *parent,
    struct powercap_control_type *control_type,
    const char *name,
    const struct powercap_zone_ops *ops,
    int nr_constraints,
    const struct powercap_zone_constraint_ops *const_ops
);

/* Скасування реєстрації та видалення зони */
int powercap_unregister_zone(
    struct powercap_control_type *control_type,
    struct powercap_zone *zone
);
```
```cpp
#include <linux/powercap.h>

// Концептуальні C++ сигнатури для розробки обгорток ядра та тестових модулів

extern "C" {

struct powercap_zone_ops {
    int (*get_energy_uj)(struct powercap_zone *zone, u64 *energy_uj);
    int (*reset_energy_uj)(struct powercap_zone *zone);
    int (*get_max_energy_range_uj)(struct powercap_zone *zone, u64 *max_uj);
    int (*get_power_uw)(struct powercap_zone *zone, u64 *power_uw);
    int (*set_enable)(struct powercap_zone *zone, bool mode);
    int (*get_enable)(struct powercap_zone *zone, bool *mode);
    int (*release)(struct powercap_zone *zone);
};

struct powercap_zone_constraint_ops {
    int (*set_power_limit_uw)(struct powercap_zone *zone, int cid, u64 power_uw);
    int (*get_power_limit_uw)(struct powercap_zone *zone, int cid, u64 *power_uw);
    int (*set_time_window_us)(struct powercap_zone *zone, int cid, u64 time_us);
    int (*get_time_window_us)(struct powercap_zone *zone, int cid, u64 *time_us);
    int (*get_max_power_uw)(struct powercap_zone *zone, int cid, u64 *power_uw);
    int (*get_min_power_uw)(struct powercap_zone *zone, int cid, u64 *power_uw);
    int (*get_max_time_window_us)(struct powercap_zone *zone, int cid, u64 *time_us);
    int (*get_min_time_window_us)(struct powercap_zone *zone, int cid, u64 *time_us);
    const char *(*get_name)(struct powercap_zone *zone, int cid);
};

struct powercap_zone *powercap_register_zone(
    struct powercap_zone *parent,
    struct powercap_control_type *control_type,
    const char *name,
    const struct powercap_zone_ops *ops,
    int nr_constraints,
    const struct powercap_zone_constraint_ops *const_ops
);

int powercap_unregister_zone(
    struct powercap_control_type *control_type,
    struct powercap_zone *zone
);

}
```
:::

## 7. Приклад налаштування лімітів через командний рядок

Для обмеження максимального енергоспоживання сокета до 65 Вт (`65 000 000 uW`) із тривалістю часового вікна 15 секунд (`15 000 000 us`):

```bash
# 1. Перевірка ідентифікатора зони сокета
cat /sys/class/powercap/intel-rapl/intel-rapl:0/name
# Очікуване значення: package-0

# 2. Встановлення ліміту довготривалої потужності PL1
echo 65000000 | sudo tee /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw

# 3. Встановлення часового вікна для ліміту PL1
echo 15000000 | sudo tee /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_time_window_us

# 4. Активація контролю зони
echo 1 | sudo tee /sys/class/powercap/intel-rapl/intel-rapl:0/enabled

# 5. Перевірка фактично встановлених параметрів
cat /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw
cat /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_time_window_us
```
