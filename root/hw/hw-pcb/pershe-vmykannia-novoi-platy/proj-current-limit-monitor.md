# ⚙️ Монітор споживання струму з апаратним вимкненням навантаження

При першому підключенні щойно зібраної друкованої плати до джерела живлення головною небезпекою є не сам факт наявності короткого замикання, а затримка реакції захисної апаратури. Стандартні лабораторні блоки живлення, попри наявність штатного режиму обмеження струму (Constant Current, CC), мають дві суттєві фізичні вади: значну внутрішню вихідну ємність (від 220 до 1000 мкФ електролітичних конденсаторів, встановлених виробником паралельно вихідним клемам для забезпечення стабільності контуру напруги) та повільну аналогово-цифрову петлю зворотного зв'язку (час реакції внутрішнього підсилювача помилки струму становить від 50 до 300 мікросекунд).

У момент фізичного замикання тумблера або підключення роз'єму вся накопичена у вихідному конденсаторі джерела енергія миттєво розряджається в точку дефекту на друкованій платі. Швидкість наростання струму `di/dt` при цьому обмежена лише мікроскопічною індуктивністю з'єднувальних проводів і сягає сотень ампер на мікросекунду. Для локального випалювання кремнієвих кристалів мікросхем, пробивання підзатворного діелектрика польових транзисторів або розпилення тонких мідних доріжок завширшки 0.1–0.2 мм достатньо імпульсу тривалістю менше 10 мікросекунд.

Створення автономного швидкодіючого монітора струму з напівпровідниковим комутатором дозволяє винести точку захисту безпосередньо до вхідних клем досліджуваної плати (Device Under Test, DUT). Такий прилад поєднує швидкісний апаратний розмикач живлення на базі силових польових транзисторів із надмалим опором відкритого каналу, високоточний вимірювальний шунт із чотирипровідним підключенням за схемою Кельвіна, спеціалізований цифровий вимірювач живлення INA226, резервний аналоговий компаратор миттєвого відсікання та мікроконтролерний блок адаптивного аналізу пускових процесів.

## Топологія силового тракту: вибір схеми комутації та вимірювання струму

Головне схемотехнічне рішення під час проектування стендового монітора полягає у виборі між верхнім (High-Side) та нижнім (Low-Side) розташуванням вимірювального шунта й комутаційного ключа.

```txt
High-Side комутація (Правильно):
Лабораторний БЖ (+) ───[ Back-to-Back MOSFETs ]───[ R_shunt ]───(+) DUT (Плата)
                                                                 │
Лабораторний БЖ (-) ─────────────────────────────────────────────┴─(-) DUT (Спільна земля GND)

Low-Side комутація (Неприпустимо для стенду):
Лабораторний БЖ (+) ───────────────────────────────────────────────(+) DUT (Плата)
                                                                   │
Лабораторний БЖ (-) ───[ R_shunt ]───[ Low-Side MOSFET ]───────────(-) DUT (Розірвана земля!)
```

У стендовому обладнанні для першого вмикання варіант Low-Side вимірювання та комутації є категорично неприпустимим. Розміщення шунта або розмикального транзистора в мінусовій шині розриває опорну лінію заземлення між джерелом живлення та тестованою платою. Якщо до плати під час тестування підключено зовнішній осцилограф, програматор ST-Link чи інтерфейсний кабель UART, земляний провідник цих приладів зашунтує вимірювальний резистор і силовий ключ через спільну мережеву землю розетки 230 В. У результаті струм короткого замикання піде через екран USB-кабелю або виводи програматора, випалюючи порт комп'ютера.

Тому реалізується виключно схема High-Side комутації, яка зберігає нерозривну шину заземлення GND між усіма приладами.

### Архітектура силового комутатора живлення

Силовий комутатор монітора виконує функцію електронного запобіжника (eFuse). Одиничний польовий транзистор містить паразитно увімкнений внутрішній діод (Body Diode) між стоком і витоком. Якщо на тестованій платі присутні заряджені конденсатори великої ємності або стороннє джерело живлення, при закриванні одиночного транзистора зворотний струм безперешкодно протікатиме крізь його діод.

Щоб гарантувати повне двонаправлене розмикання кола, силовий ключ будується за топологією зустрічно увімкнених транзисторів (Back-to-Back MOSFETs):

1. **Конфігурація на P-канальних транзисторах:** Два P-MOSFET з'єднуються однаковими виводами (витік до витоку, Source-to-Source). Спільні затвори підтягуються до позитивної шини живлення через резистор 100 кОм (стан за замовчуванням — надійно закрито). Для відкривання ключа допоміжний біполярний транзистор NPN або малий N-MOSFET притягує лінію затворів до землі, обмежуючи напругу `V_gs` на рівні 10–12 В за допомогою стабілітрона. Для запобігання паразитному дзвіну в момент перемикання послідовно з кожним затвором встановлюється антипаразитний демпферний резистор `R_gate = 10–22 Ом`.
2. **Конфігурація на N-канальних транзисторах:** N-MOSFET мають у 2.5–3 рази менший питомий опір каналу `R_ds(on)` при тій самій площі кристала, порівняно з P-канальними аналогами. Проте для їх відкривання у верхньому плечі напруга на затворі повинна перевищувати напругу шини живлення на 10 В (`V_gate = V_bus + 10 В`). Для цього застосовується спеціалізований контролер захисту з вбудованим генератором накачування заряду (Charge Pump), здатний утримувати затвор відкритим постійно та примусово скидати заряд затвора за час менше 1 мкс струмом до 2–3 А при фіксації аварії.

### Прецизійний струмовий шунт і підключення за схемою Кельвіна

Для вимірювання струмів від 1 мА до 10 А використовується низькоомний шунт опором `R_shunt = 10 мОм` (0.010 Ом). При протіканні струму 100 мА падіння напруги на шунті становить лише 1 мВ. Якщо вимірювальні провідники підключити до звичайних контактних площадок, опір припою та мідних доріжок друкованої плати (який зазвичай становить 1–3 мОм) додасться до опору шунта, спричинивши похибку вимірювання до 30%.

Для усунення цієї похибки застосовується виключно чотирипровідне підключення Кельвіна (Kelvin 4-Wire Sensing):

```txt
                 Силовий струм I_load ──►
        ┌────────────────────────────────────────┐
        │        Прецизійний шунт R_shunt        │
  ──────┴─┐                                    ┌─┴──────
  Силовий │   ┌───┐                    ┌───┐   │ Силовий
   вхід   └───┤ K1│                    │ K2├───┘  вихід
              └───┘                    └───┘
                │                        │
                ▼                        ▼
           IN+ (INA226)             IN- (INA226)
           (Диференційна пара з імпедансом 100 Ом)
```

Силовий струм підводиться до зовнішніх широких контактів резистора, а вимірювальні лінії `K1` та `K2` виводяться з внутрішніх зон струмопровідного шару безпосередньо під тілом компонента. Оскільки вхідний імпеданс вимірювача INA226 становить понад 100 кОм, струм через лінії Кельвіна практично дорівнює нулю, і падіння напруги на вимірювальних трасах не виникає. Диференційні лінії `IN+` та `IN-` прокладаються на платі паралельною парою з мінімальним зазором і екрануються полігоном заземлення для придушення наведених імпульсних завад від комутації DC-DC перетворювачів.

## Робота з мікросхемою INA226: конфігурація та калібрування

Мікросхема INA226 являє собою спеціалізований 16-бітний цифровий монітор струму, напруги та потужності з інтерфейсом I2C. Внутрішній сигма-дельта АЦП вимірює два параметри: диференційну напругу на шунті `V_shunt` (діапазон ±81.92 мВ з роздільною здатністю 2.5 мкВ/digit) та абсолютну напругу на шині живлення `V_bus` (діапазон від 0 до 36 В з фіксованою роздільною здатністю 1.25 мВ/digit).

### Регістрова карта мікросхеми

| Адреса | Назва регістра | Тип | Призначення та бітовий склад |
|---|---|---|---|
| `0x00` | `Configuration` | R/W | Налаштування часу конверсії АЦП, коефіцієнта усереднення вибірок та режиму роботи |
| `0x01` | `Shunt Voltage` | R | Сире 16-бітне знакове значення напруги на шунті (крок 2.5 мкВ) |
| `0x02` | `Bus Voltage` | R | 16-бітне значення напруги шини живлення (крок 1.25 мВ) |
| `0x03` | `Power` | R | 16-бітне розраховане значення потужності навантаження |
| `0x04` | `Current` | R | 16-бітне розраховане значення струму через шунт |
| `0x05` | `Calibration` | R/W | Коефіцієнт масштабування внутрішнього обчислювача струму |
| `0x06` | `Mask/Enable` | R/W | Конфігурація аварійних переривань виводу ALERT |
| `0x07` | `Alert Limit` | R/W | Порогове значення для спрацьовування апаратного компаратора |

### Розрахунок коефіцієнта калібрування

Внутрішній помножувач мікросхеми розраховує значення регістра струму `Current` за формулою:

```txt
Current = (Shunt_Voltage · Calibration_Register) / 2048
```

Для того, щоб кожен молодший розряд регістра струму відповідав зручній фізичній величині (наприклад, `Current_LSB = 200 мкА/digit`), константа калібрування розраховується з фізичних параметрів вимірювального кола:

```txt
CAL = 0.00512 / (Current_LSB · R_shunt)
    = 0.00512 / (0.0002 А · 0.010 Ом)
    = 0.00512 / 0.000002
    = 2560 = 0x0A00       [значення для запису в регістр 0x05]
```

При такому калібруванні максимальний вимірюваний струм стенду становить:

```txt
I_max = Current_LSB · 32767
      = 0.0002 · 32767
      ≈ 6.5534 А          [максимальний струм повної шкали]
```

Цього діапазону з надлишком вистачає для діагностики будь-яких вбудованих контролерів, цифрових плат та інтерфейсних модулів при першому включенні.

### Налаштування апаратного переривання ALERT

Вивід `ALERT` мікросхеми INA226 має відкритий стік (Open-Drain) і підтягується до напруги 3.3 В через резистор 4.7 кОм. У регістрі `Mask/Enable` (адреса `0x06`) конфігуруються такі режими:
- Біт `SOL` (Shunt Over-Limit, біт 15) — генерувати сигнал тривоги, якщо напруга на шунті перевищує значення, записане в регістрі `Alert Limit` (регістр `0x07`).
- Біт `APOL` (Alert Polarity, біт 1) — задає активний високий або активний низький рівень сигналу.
- Біт `LEN` (Latch Enable, біт 0) — фіксує активний стан виводу `ALERT` доти, доки мікроконтролер явно не прочитає регістр `Mask/Enable`. Це унеможливлює ситуацію, коли короткочасний сплеск струму зникає до того, як процесор встиг зреагувати на переривання.

## Аналоговий швидкісний компаратор миттєвого захисту (Hardware Fast Trip)

Хоча мікросхема INA226 забезпечує високу точність вимірювання, її найшвидший цикл перетворення сигма-дельта модулятора становить 140 мікросекунд. У разі прямого металевого замикання силової шини 12 В на землю цей інтервал є занадто довгим.

Тому паралельно з INA226 до вимірювальних виводів шунта підключається ультрашвидкісний аналоговий компаратор із затримкою розповсюдження сигналу `t_prop < 10 нс` (наприклад, TLV3501 або ADCMP601):

```txt
               R_shunt (10 мОм)
         IN+ ────────┬──────── IN-
                     │          │
    ┌────────────────┴─┐        │
    │ Дільник опори    │        │
    │ V_ref_trip = 80мВ│        │
    └────────┬─────────┘        │
             │                  │
             ▼                  ▼
          ┌────────────────────────┐
          │   Швидкий компаратор   │
          │   (TLV3501, t < 10 нс) │
          └───────────┬────────────┘
                      │ Вихід FAULT
                      ▼
          ┌────────────────────────┐
          │   Апаратний RS-тригер  │──────► Розмикання затворів MOSFET
          │    (74LVC1G279 / SCR)  │        (Час спрацьовування < 800 нс)
          └───────────▲────────────┘
                      │ Сигнал Reset від MCU
```

Дільник напруги задає жорстку опорну напругу спрацьовування (наприклад, 80 мВ, що відповідає абсолютному граничному струму 8.0 А). Для усунення брязкоту на межі спрацьовування компаратор охоплений ланцюгом додатної зворотного зв'язку (гістерезис 5 мВ через резистор 100 кОм). Якщо струм перевищує цей поріг, вихід компаратора перемикається в одиницю і зводить апаратний RS-тригер. Вихід тригера безпосередньо вимикає драйвер силових транзисторів, розряджаючи затвори на землю за 500–800 нс без жодної участі процесорного ядра або шини I2C. Мікроконтролер дізнається про факт спрацьовування постфактум через переривання від лінії стану тригера.

## Алгоритм захисту: диференціація пускового струму та короткого замикання

Критичною проблемою програмного забезпечення монітора є запобігання хибним спрацьовуванням захисту в момент подачі напруги на справну плату. Будь-яка сучасна електронна плата містить на вході масив керамічних та електролітичних конденсаторів ємністю від 10 до 500 мкФ.

У момент замикання силового ключа незаряджений конденсатор еквівалентний короткому замиканню. Струм заряджання описується рівнянням:

```txt
i_inrush(t) = (V_bus / R_loop) · exp(-t / (R_loop · C_in))
```

де `R_loop` — сумарний опір силового кола (опір транзисторів, шунта, роз'ємів і кабелів, типово 50–150 мОм). Піковий пусковий струм може досягати 5–10 А навіть на абсолютно справній платі, експоненційно спадаючи до струму спокою (20–100 мА) за час від 500 мікросекунд до 5 мілісекунд.

```txt
Струм I (А)
 ▲
10├──┐ (Пік заряду ємностей Inrush)
  │  │\
 5├──┤ \
  │  │  \  Штатний експоненційний спад
 1├──┼───\──────────────────────────── Поріг тривалого струму I_limit (500 мА)
  │  │    \___________________________ Струм спокою схеми I_quiescent (80 мА)
 0└──┴─────┴─────────────────────────► Час t (мс)
     0    500 мкс          25 мс (Grace Period)
```

Для коректної обробки цього процесу алгоритм реалізує трирівневу модель прийняття рішень:

1. **Рівень 0: Апаратний захист від миттєвого руйнування (Instant Trip):** Працює постійно. Якщо струм перевищує 8 А незалежно від стану системи, аналоговий компаратор миттєво розмикає затвори транзисторів за час менше 800 нс.
2. **Рівень 1: Вікно маскування пускового заряду (Soft Start Grace Period):** Протягом перших 20–30 мс після подачі напруги програмний поріг перевантаження за струмом тимчасово блокується, але одночасно відстежується динаміка наростання напруги на шині `V_bus`. Якщо через 5 мс після відкриття ключа напруга `V_bus` залишається нижчою за 1.0 В при протіканні струму, це свідчить про глухе коротке замикання (Hard Short), і живлення вимикається достроково.
3. **Рівень 2: Стаціонарний моніторинг (Armed Monitor):** Після завершення фази плавного пуску вмикається жорсткий контроль встановленого користувачем ліміту струму (наприклад, 200 мА) із розрахунком цифрового ковзного середнього (EMA) для фільтрації шуму та фіксацією параметрів у кільцевому буфері чорної скриньки (Blackbox Trace).

Цифровий фільтр децимації АЦП INA226 додатково налаштовується на 16 усереднень при часі конверсії 1.1 мс, що створює смугу пропускання близько 50 Гц. Це повністю відсікає високочастотний шум комутації імпульсних стабілізаторів плати (100 кГц — 2 МГц), забезпечуючи гладку картину середньоквадратичного споживання струму без хибних сплесків.

## Повний вихідний код монітора захисту

Нижче наведено повністю працездатну, завершену реалізацію модуля моніторингу двома мовами: на чистому стандарті C99 з явною структурою абстракції апаратного рівня (HAL) та на сучасному стандарті C++20 із застосуванням сильної типізації, концептів, гарантій RAII та семантики обробки помилок через `std::expected`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define INA226_I2C_ADDR         0x40
#define INA226_REG_CONFIG       0x00
#define INA226_REG_SHUNTVOLT    0x01
#define INA226_REG_BUSVOLT      0x02
#define INA226_REG_POWER        0x03
#define INA226_REG_CURRENT      0x04
#define INA226_REG_CALIBRATION  0x05
#define INA226_REG_MASKENABLE   0x06
#define INA226_REG_ALERTLIMIT   0x07

#define INA226_CFG_RESET        0x8000
#define INA226_CFG_AVG_16       (0x02 << 9)
#define INA226_CFG_VBUS_1100US  (0x04 << 6)
#define INA226_CFG_VSH_1100US   (0x04 << 3)
#define INA226_CFG_MODE_CONT    0x07

#define INA226_MASK_SOL         (1 << 15)  /* Shunt Over-Limit Alert */
#define INA226_MASK_POL         (1 << 14)  /* Power Over-Limit Alert */
#define INA226_MASK_AFF         (1 << 4)   /* Alert Function Flag */
#define INA226_MASK_APOL        (1 << 1)   /* Alert Polarity Active High */
#define INA226_MASK_LEN         (1 << 0)   /* Latch Enable */

#define BLACKBOX_BUFFER_SIZE    256
#define CURRENT_LSB_UA          200        /* 200 uA per LSB */
#define VOLTAGE_LSB_UV          1250       /* 1.25 mV per LSB */
#define POWER_LSB_UW            5000       /* 5 mW per LSB */

typedef enum {
    MONITOR_STATE_DISARMED = 0,
    MONITOR_STATE_SOFT_START,
    MONITOR_STATE_ARMED,
    MONITOR_STATE_FAULT_OVERCURRENT,
    MONITOR_STATE_FAULT_OVERVOLTAGE,
    MONITOR_STATE_FAULT_BROWNOUT,
    MONITOR_STATE_HARDWARE_TRIP
} MonitorState_t;

typedef struct {
    uint32_t timestamp_ms;
    int32_t  current_ma;
    uint32_t voltage_mv;
    uint32_t power_mw;
} TelemetryFrame_t;

typedef struct {
    TelemetryFrame_t frames[BLACKBOX_BUFFER_SIZE];
    uint16_t head;
    uint16_t count;
    bool is_locked;
} BlackboxRecorder_t;

typedef struct {
    uint16_t i2c_address;
    uint16_t cal_register_val;
    int32_t  max_current_limit_ma;
    uint32_t min_voltage_limit_mv;
    uint32_t max_voltage_limit_mv;
    uint32_t inrush_grace_period_ms;
    int32_t  current_ema_ma;
    uint32_t state_entered_timestamp_ms;
    MonitorState_t state;
    BlackboxRecorder_t blackbox;
    bool (*i2c_write_reg)(uint8_t addr, uint8_t reg, uint16_t val);
    bool (*i2c_read_reg)(uint8_t addr, uint8_t reg, uint16_t *val);
    void (*set_switch_state)(bool enabled);
    uint32_t (*get_system_tick_ms)(void);
} PowerMonitor_t;

static inline uint16_t swap_bytes(uint16_t val) {
    return (uint16_t)((val << 8) | (val >> 8));
}

void blackbox_record(BlackboxRecorder_t *bb, const TelemetryFrame_t *frame) {
    if (bb->is_locked) return;
    bb->frames[bb->head] = *frame;
    bb->head = (bb->head + 1) % BLACKBOX_BUFFER_SIZE;
    if (bb->count < BLACKBOX_BUFFER_SIZE) {
        bb->count++;
    }
}

void blackbox_lock(BlackboxRecorder_t *bb) {
    bb->is_locked = true;
}

bool power_monitor_init(PowerMonitor_t *mon, uint8_t i2c_addr, uint16_t cal_val,
                        int32_t limit_ma, uint32_t min_mv, uint32_t max_mv) {
    if (!mon || !mon->i2c_write_reg || !mon->i2c_read_reg || !mon->set_switch_state) {
        return false;
    }

    mon->i2c_address = i2c_addr;
    mon->cal_register_val = cal_val;
    mon->max_current_limit_ma = limit_ma;
    mon->min_voltage_limit_mv = min_mv;
    mon->max_voltage_limit_mv = max_mv;
    mon->inrush_grace_period_ms = 25; /* 25 ms inrush mask */
    mon->current_ema_ma = 0;
    mon->state = MONITOR_STATE_DISARMED;
    mon->blackbox.head = 0;
    mon->blackbox.count = 0;
    mon->blackbox.is_locked = false;

    /* Примусове розмикання силового ключа */
    mon->set_switch_state(false);

    /* Скидання мікросхеми INA226 */
    if (!mon->i2c_write_reg(mon->i2c_address, INA226_REG_CONFIG, swap_bytes(INA226_CFG_RESET))) {
        return false;
    }

    /* Запис конфігурації: 16 усереднень, час конверсії 1.1 мс для напруги та струму */
    uint16_t cfg = INA226_CFG_AVG_16 | INA226_CFG_VBUS_1100US | INA226_CFG_VSH_1100US | INA226_CFG_MODE_CONT;
    if (!mon->i2c_write_reg(mon->i2c_address, INA226_REG_CONFIG, swap_bytes(cfg))) {
        return false;
    }

    /* Запис регістра калібрування */
    if (!mon->i2c_write_reg(mon->i2c_address, INA226_REG_CALIBRATION, swap_bytes(mon->cal_register_val))) {
        return false;
    }

    /* Налаштування апаратного ALERT виводу на перевищення струму шунта */
    int16_t raw_alert_limit = (int16_t)((limit_ma * 1000) / CURRENT_LSB_UA);
    if (!mon->i2c_write_reg(mon->i2c_address, INA226_REG_ALERTLIMIT, swap_bytes((uint16_t)raw_alert_limit))) {
        return false;
    }

    uint16_t mask_enable = INA226_MASK_SOL | INA226_MASK_APOL | INA226_MASK_LEN;
    if (!mon->i2c_write_reg(mon->i2c_address, INA226_REG_MASKENABLE, swap_bytes(mask_enable))) {
        return false;
    }

    return true;
}

bool power_monitor_arm(PowerMonitor_t *mon) {
    if (mon->state != MONITOR_STATE_DISARMED) {
        return false;
    }
    mon->state_entered_timestamp_ms = mon->get_system_tick_ms();
    mon->state = MONITOR_STATE_SOFT_START;
    mon->set_switch_state(true);
    return true;
}

void power_monitor_emergency_trip(PowerMonitor_t *mon, MonitorState_t reason) {
    mon->set_switch_state(false);
    mon->state = reason;
    blackbox_lock(&mon->blackbox);
}

void power_monitor_hardware_isr_callback(PowerMonitor_t *mon) {
    /* Негайне переривання від лінії ALERT INA226 або швидкого компаратора */
    mon->set_switch_state(false);
    mon->state = MONITOR_STATE_HARDWARE_TRIP;
    blackbox_lock(&mon->blackbox);
}

void power_monitor_process(PowerMonitor_t *mon) {
    if (mon->state == MONITOR_STATE_DISARMED ||
        mon->state == MONITOR_STATE_FAULT_OVERCURRENT ||
        mon->state == MONITOR_STATE_FAULT_OVERVOLTAGE ||
        mon->state == MONITOR_STATE_FAULT_BROWNOUT ||
        mon->state == MONITOR_STATE_HARDWARE_TRIP) {
        return;
    }

    uint32_t now = mon->get_system_tick_ms();
    uint16_t raw_vbus = 0, raw_curr = 0, raw_pwr = 0, raw_mask = 0;

    if (!mon->i2c_read_reg(mon->i2c_address, INA226_REG_BUSVOLT, &raw_vbus) ||
        !mon->i2c_read_reg(mon->i2c_address, INA226_REG_CURRENT, &raw_curr) ||
        !mon->i2c_read_reg(mon->i2c_address, INA226_REG_POWER, &raw_pwr) ||
        !mon->i2c_read_reg(mon->i2c_address, INA226_REG_MASKENABLE, &raw_mask)) {
        power_monitor_emergency_trip(mon, MONITOR_STATE_HARDWARE_TRIP);
        return;
    }

    raw_vbus = swap_bytes(raw_vbus);
    raw_curr = swap_bytes(raw_curr);
    raw_pwr = swap_bytes(raw_pwr);
    raw_mask = swap_bytes(raw_mask);

    int16_t signed_raw_curr = (int16_t)raw_curr;
    int32_t current_ma = ((int32_t)signed_raw_curr * CURRENT_LSB_UA) / 1000;
    uint32_t voltage_mv = ((uint32_t)raw_vbus * VOLTAGE_LSB_UV) / 1000;
    uint32_t power_mw = ((uint32_t)raw_pwr * POWER_LSB_UW) / 1000;

    TelemetryFrame_t frame = {
        .timestamp_ms = now,
        .current_ma = current_ma,
        .voltage_mv = voltage_mv,
        .power_mw = power_mw
    };
    blackbox_record(&mon->blackbox, &frame);

    /* Оновлення експоненційного ковзного середнього (alpha = 0.25 -> 1/4) */
    if (mon->current_ema_ma == 0) {
        mon->current_ema_ma = current_ma;
    } else {
        mon->current_ema_ma = (mon->current_ema_ma * 3 + current_ma) / 4;
    }

    /* Перевірка стану плавного пуску (Soft Start Grace Period) */
    if (mon->state == MONITOR_STATE_SOFT_START) {
        if (now - mon->state_entered_timestamp_ms >= mon->inrush_grace_period_ms) {
            mon->state = MONITOR_STATE_ARMED;
        }
    }

    /* Перевірка прапорця апаратного алерту в мікросхемі */
    if (raw_mask & INA226_MASK_AFF) {
        power_monitor_emergency_trip(mon, MONITOR_STATE_FAULT_OVERCURRENT);
        return;
    }

    /* Аналіз напруги живлення на перенапругу та просідання (Brownout) */
    if (voltage_mv > mon->max_voltage_limit_mv) {
        power_monitor_emergency_trip(mon, MONITOR_STATE_FAULT_OVERVOLTAGE);
        return;
    }

    if (mon->state == MONITOR_STATE_ARMED && voltage_mv < mon->min_voltage_limit_mv) {
        power_monitor_emergency_trip(mon, MONITOR_STATE_FAULT_BROWNOUT);
        return;
    }

    /* Програмний контроль перевантаження за струмом */
    if (mon->state == MONITOR_STATE_ARMED && current_ma > mon->max_current_limit_ma) {
        power_monitor_emergency_trip(mon, MONITOR_STATE_FAULT_OVERCURRENT);
        return;
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <optional>
#include <expected>
#include <chrono>
#include <concepts>
#include <algorithm>

namespace hw::protection {

using namespace std::chrono_literals;

struct Milliamperes {
    int32_t value{0};
    constexpr auto operator<=>(const Milliamperes&) const = default;
};

struct Millivolts {
    uint32_t value{0};
    constexpr auto operator<=>(const Millivolts&) const = default;
};

struct Milliwatts {
    uint32_t value{0};
    constexpr auto operator<=>(const Milliwatts&) const = default;
};

constexpr Milliamperes operator""_mA(unsigned long long v) {
    return Milliamperes{static_cast<int32_t>(v)};
}

constexpr Millivolts operator""_mV(unsigned long long v) {
    return Millivolts{static_cast<uint32_t>(v)};
}

constexpr Milliwatts operator""_mW(unsigned long long v) {
    return Milliwatts{static_cast<uint32_t>(v)};
}

enum class ErrorCode : uint8_t {
    I2cCommunicationFailure,
    DeviceNotResponding,
    ConfigurationMismatch,
    CalibrationError,
    OverCurrentTrip,
    OverVoltageTrip,
    BrownoutTrip,
    HardwareLatchTriggered
};

struct TelemetrySample {
    std::chrono::milliseconds timestamp{0};
    Milliamperes current{0_mA};
    Millivolts voltage{0_mV};
    Milliwatts power{0_mW};
};

template <size_t Capacity>
class RingBufferTrace {
public:
    constexpr RingBufferTrace() = default;

    void push(const TelemetrySample& sample) noexcept {
        if (m_locked) return;
        m_data[m_head] = sample;
        m_head = (m_head + 1) % Capacity;
        if (m_size < Capacity) {
            ++m_size;
        }
    }

    void lock() noexcept {
        m_locked = true;
    }

    [[nodiscard]] bool is_locked() const noexcept {
        return m_locked;
    }

    [[nodiscard]] size_t size() const noexcept {
        return m_size;
    }

    [[nodiscard]] std::array<TelemetrySample, Capacity> snapshot_ordered() const noexcept {
        std::array<TelemetrySample, Capacity> result{};
        if (m_size == 0) return result;

        size_t start_idx = (m_size == Capacity) ? m_head : 0;
        for (size_t i = 0; i < m_size; ++i) {
            result[i] = m_data[(start_idx + i) % Capacity];
        }
        return result;
    }

private:
    std::array<TelemetrySample, Capacity> m_data{};
    size_t m_head{0};
    size_t m_size{0};
    bool m_locked{false};
};

template <typename I2cBus, typename GpioSwitch, typename ClockSource>
class CurrentLimitMonitor {
public:
    struct Config {
        uint8_t i2c_address{0x40};
        uint16_t calibration_reg{2560};
        Milliamperes current_limit{500_mA};
        Millivolts min_voltage{4500_mV};
        Millivolts max_voltage{5500_mV};
        std::chrono::milliseconds inrush_grace{30ms};
    };

    enum class State : uint8_t {
        Disarmed,
        SoftStart,
        Armed,
        TrippedOverCurrent,
        TrippedOverVoltage,
        TrippedBrownout,
        TrippedHardwareLatch
    };

    explicit CurrentLimitMonitor(I2cBus& i2c, GpioSwitch& sw, ClockSource& clock, Config cfg) noexcept
        : m_i2c{i2c}, m_switch{sw}, m_clock{clock}, m_config{cfg} {}

    ~CurrentLimitMonitor() noexcept {
        // RAII: Гарантоване знеструмлення при знищенні об'єкта
        m_switch.disable();
    }

    CurrentLimitMonitor(const CurrentLimitMonitor&) = delete;
    CurrentLimitMonitor& operator=(const CurrentLimitMonitor&) = delete;
    CurrentLimitMonitor(CurrentLimitMonitor&&) noexcept = default;
    CurrentLimitMonitor& operator=(CurrentLimitMonitor&&) noexcept = default;

    [[nodiscard]] std::expected<void, ErrorCode> init() noexcept {
        m_switch.disable();
        m_state = State::Disarmed;

        // Скидання конфігурації INA226
        if (!write_register(0x00, 0x8000)) {
            return std::unexpected(ErrorCode::I2cCommunicationFailure);
        }

        // Конфігурація: 16x усереднення, 1.1 мс час конверсії, безперервний режим
        uint16_t cfg_word = (0x02 << 9) | (0x04 << 6) | (0x04 << 3) | 0x07;
        if (!write_register(0x00, cfg_word)) {
            return std::unexpected(ErrorCode::ConfigurationMismatch);
        }

        // Запис регістра калібрування
        if (!write_register(0x05, m_config.calibration_reg)) {
            return std::unexpected(ErrorCode::CalibrationError);
        }

        // Налаштування аварійного порогу ALERT
        int16_t alert_raw = static_cast<int16_t>((m_config.current_limit.value * 1000) / 200);
        if (!write_register(0x07, static_cast<uint16_t>(alert_raw))) {
            return std::unexpected(ErrorCode::ConfigurationMismatch);
        }

        // Увімкнення переривання за перевищенням струму шунта (SOL + APOL + LEN)
        uint16_t mask = (1 << 15) | (1 << 1) | (1 << 0);
        if (!write_register(0x06, mask)) {
            return std::unexpected(ErrorCode::ConfigurationMismatch);
        }

        return {};
    }

    [[nodiscard]] std::expected<void, ErrorCode> arm() noexcept {
        if (m_state != State::Disarmed) {
            return std::unexpected(ErrorCode::ConfigurationMismatch);
        }
        m_arm_start_time = m_clock.now();
        m_state = State::SoftStart;
        m_switch.enable();
        return {};
    }

    void handle_hardware_trip_isr() noexcept {
        m_switch.disable();
        m_state = State::TrippedHardwareLatch;
        m_trace.lock();
    }

    [[nodiscard]] std::expected<TelemetrySample, ErrorCode> poll() noexcept {
        if (m_state == State::Disarmed || is_tripped()) {
            return std::unexpected(ErrorCode::HardwareLatchTriggered);
        }

        auto now = m_clock.now();
        auto raw_vbus = read_register(0x02);
        auto raw_curr = read_register(0x04);
        auto raw_pwr  = read_register(0x03);
        auto raw_mask = read_register(0x06);

        if (!raw_vbus || !raw_curr || !raw_pwr || !raw_mask) {
            trip(State::TrippedHardwareLatch);
            return std::unexpected(ErrorCode::I2cCommunicationFailure);
        }

        auto signed_curr = static_cast<int16_t>(*raw_curr);
        Milliamperes current{static_cast<int32_t>(signed_curr * 200 / 1000)};
        Millivolts voltage{static_cast<uint32_t>(*raw_vbus * 1250 / 1000)};
        Milliwatts power{static_cast<uint32_t>(*raw_pwr * 5000 / 1000)};

        TelemetrySample sample{now, current, voltage, power};
        m_trace.push(sample);

        // Перевірка часу завершення м'якого старту
        if (m_state == State::SoftStart) {
            if (now - m_arm_start_time >= m_config.inrush_grace) {
                m_state = State::Armed;
            }
        }

        // Апаратний прапорець виходу за межі
        if (*raw_mask & (1 << 4)) {
            trip(State::TrippedOverCurrent);
            return std::unexpected(ErrorCode::OverCurrentTrip);
        }

        // Валідація напруги
        if (voltage > m_config.max_voltage) {
            trip(State::TrippedOverVoltage);
            return std::unexpected(ErrorCode::OverVoltageTrip);
        }

        if (m_state == State::Armed && voltage < m_config.min_voltage) {
            trip(State::TrippedBrownout);
            return std::unexpected(ErrorCode::BrownoutTrip);
        }

        // Програмна перевірка струму
        if (m_state == State::Armed && current > m_config.current_limit) {
            trip(State::TrippedOverCurrent);
            return std::unexpected(ErrorCode::OverCurrentTrip);
        }

        return sample;
    }

    [[nodiscard]] State state() const noexcept { return m_state; }
    [[nodiscard]] bool is_tripped() const noexcept {
        return m_state == State::TrippedOverCurrent ||
               m_state == State::TrippedOverVoltage ||
               m_state == State::TrippedBrownout ||
               m_state == State::TrippedHardwareLatch;
    }

    [[nodiscard]] const RingBufferTrace<256>& trace() const noexcept { return m_trace; }

private:
    void trip(State reason) noexcept {
        m_switch.disable();
        m_state = reason;
        m_trace.lock();
    }

    [[nodiscard]] bool write_register(uint8_t reg, uint16_t val) noexcept {
        uint16_t swapped = static_cast<uint16_t>((val << 8) | (val >> 8));
        return m_i2c.write(m_config.i2c_address, reg, swapped);
    }

    [[nodiscard]] std::optional<uint16_t> read_register(uint8_t reg) noexcept {
        auto val = m_i2c.read(m_config.i2c_address, reg);
        if (!val) return std::nullopt;
        return static_cast<uint16_t>((*val << 8) | (*val >> 8));
    }

    I2cBus& m_i2c;
    GpioSwitch& m_switch;
    ClockSource& m_clock;
    Config m_config;
    State m_state{State::Disarmed};
    std::chrono::milliseconds m_arm_start_time{0ms};
    RingBufferTrace<256> m_trace{};
};

} // namespace hw::protection
```
:::

## Постмортальний аналіз та декодування чорної скриньки (Blackbox Trace)

Наявність вбудованого кільцевого буфера на 256 кадрів телеметрії дозволяє інженеру реконструювати послідовність подій, що призвели до аварійного відключення. При частоті опитування 1 кГц буфер зберігає історію за останні 256 мілісекунд до моменту спрацьовування захисту.

Аналіз збереженої траєкторії напруги та струму дає змогу точно класифікувати фізичну природу дефекту:

```txt
Сценарій 1: Пробій керамічного конденсатора MLCC (Миттєвий стрибок)
Напруга V_bus (В):  5.0 ── 5.0 ── 5.0 ── 4.8 ── 0.2 (Провал за 1 мс)
Струм I_load (мА):   45 ──  48 ──  50 ── 980 ── 4500 (Trip!)

Сценарій 2: Тепловий розгін LDO / мікросхеми (Експоненційне наростання)
Напруга V_bus (В):  5.0 ── 5.0 ── 4.95 ── 4.90 ── 4.85
Струм I_load (мА):   60 ── 120 ──  280 ──  550 ── 1100 (Trip!)
```

1. **Миттєвий колапс напруги при стрибку струму (Сценарій 1):** Свідчить про пробій діелектрика (керамічний конденсатор або силовий діод). Енергія короткого замикання обчислюється як інтеграл потужності:

```txt
E_fault = ∑ (V_bus[i] · I_load[i] · Δt)
```

Завдяки швидкому відсіканню час аварії не перевищує кількох мілісекунд, а сумарна виділена енергія `E_fault < 50 мДж`, що запобігає обвуглюванню склотекстоліту FR-4.

2. **Плавне експоненційне зростання струму (Сценарій 2):** Свідчить про внутрішній перегрів кремнієвого кристала внаслідок відсутності термопасти, неправильного резистора у дільнику зворотного зв'язку або паразитного тиристорного ефекту (Latch-up).

## Методика калібрування та верифікації вимірювального стенду

Перед використанням розробленого монітора для діагностики нових дослідних плат сам прилад проходить метрологічну валідацію:

1. **Калібрування нульового зміщення (Zero-Offset Nulling):** При відключеному навантаженні зчитується сире значення регістра `Shunt Voltage` протягом 1000 циклів. Отримане середнє арифметичне зміщення зберігається в енергонезалежній пам'яті мікроконтролера та програмно віднімається від кожного вимірювання.
2. **Двоточкова лінеаризація струмового тракту:** До виходу монітора підключається програмоване електронне навантаження в режимі стабілізації струму. Подаються дві калібрувальні точки: `I_cal1 = 100.0 мА` та `I_cal2 = 2.000 А`. Паралельно напруга на шунті вимірюється лабораторним мультиметром розрядністю 6.5 цифр. За результатами вимірів уточнюється фактичний опір шунта `R_shunt_actual`, який підставляється у формулу розрахунку константи регістра `CAL`.
3. **Динамічний тест швидкодії аварійного відсікання:** До виходу стенда через зовнішній комутатор на базі GaN-транзистора підключається тестовий безіндуктивний резистор опором 0.05 Ом. Осцилографом фіксується затримка між фронтом наростання струму та повним закриванням силового ключа. Норматив вважається виконаним, якщо загальний час знеструмлення `t_trip < 1.2 мкс` для аналогового каналу та `t_trip < 180 мкс` для каналу ALERT INA226.

## Інженерні крайові випадки, тепловий дрейф та апаратні пастки

Під час проектування та практичної експлуатації стендового монітора струму виникає низка специфічних апаратних ефектів, неврахування яких призводить або до хибних аварійних вимкнень, або до фатального руйнування досліджуваного пристрою.

### Індуктивний викид напруги під час швидкого розриву кола

Коли силовий комутатор монітора аварійно вимикає струм короткого замикання 5 А за час менше 1 мікросекунди, у підвідних кабелях довжиною 0.5–1 м виникає явище електромагнітної самоіндукції. Індуктивність пари силових проводів становить приблизно `L_wire ≈ 1.5 мкГн`. Згідно із законом Фарадея, амплітуда перенапруги на клемах комутатора досягає:

```txt
V_spike = L_wire · (di / dt)
        = 1.5 · 10^-6 · (5.0 / 1 · 10^-6)
        = 7.5 В       [амплітуда перенапруги самоіндукції]
```

Якщо монітор живиться від напруги 24 В, сумарний імпульс напруги досягає `24 + 7.5 = 31.5 В`. Якщо швидкість закривання затвора форсувати до 100 нс, амплітуда викиду перевищить 75 В, що миттєво проб'є діелектрик затвора MOSFET або випалить аналоговий вхідний каскад мікросхеми INA226 (абсолютний максимум якої становить 36 В).

Для запобігання цій аварії застосовується демпферний RC-снубер паралельно вхідним клемам та швидкодіючий захисний діод TVS (Transient Voltage Suppressor) з напругою відкривання 28–30 В, встановлений безпосередньо біля виводів живлення монітора.

### Термо-ЕРС та тепловий дрейф шунта

При протіканні вимірюваного струму на шунті виділяється теплова потужність `P = I^2 · R`. У місцях контакту між мідними доріжками плати та сплавом резистора виникають два термопари. Якщо градієнт охолодження плати несиметричний (наприклад, з одного боку шунта розташований мідний полігон заземлення великої площі, а з іншого — вузька доріжка), різниця температур спаїв `ΔT = 15 °C` за рахунок ефекту Зеєбека (Seebeck effect) генерує паразитну термо-ЕРС до 50–100 мкВ.

Для 16-бітного вимірювача з роздільною здатністю 2.5 мкВ на розряд ця паразитна напруга додає зміщення нуля в 20–40 квантів (що еквівалентно уявній похибці струму 4–8 мА). Тому топологія контактних площадок під шунт повинна бути абсолютно теплосиметричною з однаковою геометрією тепловідвідних мідних полігонів з обох боків резистора.

### Обмеження швидкодії шини I2C

Опитування регістрів струму та напруги по шині I2C на стандартній частоті 400 кГц вимагає передачі адресного байта, байта регістра та двох байтів даних, що займає близько 75–100 мікросекунд на одну транзакцію. Якщо алгоритм аварійного захисту покладається виключно на періодичне опитування регістрів, загальний час виявлення короткого замикання з урахуванням конвеєра обчислень складе від 1.5 до 3 мілісекунд.

Цього часу більш ніж достатньо для пошкодження тонких провідників на платі. Тому програмне опитування застосовується виключно для телеметрії, реєстрації трендів та запису чорної скриньки. Первинний захист від короткого замикання зобов'язаний бути апаратним: вивід `ALERT` мікросхеми або вихід швидкісного аналогового компаратора повинен заводитися на апаратний вхід драйвера MOSFET для прямого відключення живлення без очікування реакції мікроконтролера.
