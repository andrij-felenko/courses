# ⚙️ Керування доменами живлення та контролер DVFS на системі-на-кристалі

У сучасних системах-на-кристалі, виготовлених за технологічними нормами менше 7 нанометрів, одночасна робота всіх наявних блоків (восьми процесорних ядер, масивного графічного прискорювача, тензорного нейропроцесора, модему зв'язку та контролерів пам'яті) на максимальній тактовій частоті призвела б до перевищення теплового ліміту кристала у 4–6 разів. Виділення тепла понад 30–50 Вт на крихітній площі 100 мм² спричиняє миттєвий перегрів і тепловий пробій напівпровідникової структури. Щоб кристал залишався у безпечних температурних межах мобільного чи вбудованого пристрою, апаратно-програмний комплекс керування живленням повинен динамічно знеструмлювати незадіяні функціональні домени та плавно підлаштовувати напругу й частоту активних ядер під поточне обчислювальне навантаження.

Нижче наведено практичну реалізацію низькорівневого драйвера та скінченного автомата (FSM) для контролера керування живленням (Power Management Controller, PMC / PPU) та підсистеми динамічного масштабування напруги й частоти (DVFS, англ. *Dynamic Voltage and Frequency Scaling*). Модуль реалізує точну фізичну послідовність увімкнення та вимкнення комутованого домену живлення з урахуванням ланцюжкового вмикання ключів для обмеження пускового струму, керування ретеншн-тригерами, активації ізоляційних комірок та безпечної зміни точок продуктивності (OPP).

![Скінченний автомат керування доменом живлення та послідовність DVFS](/book/electronics/microelectronics/system-on-chip/img/dvfs-state-machine.svg)
*Стани скінченного автомата керування доменом живлення та строгий порядок перемикання напруги й частоти DVFS.*

---

## 1. Фізична структура комутованого домену та граничні елементи

Розбиття монолітного кристала на окремі ізольовані острівці напруги (Voltage Islands) та домени живлення (Power Domains) вимагає спеціальних схемотехнічних елементів, інтегрованих у бібліотеку стандартних комірок.

### Силові ключі живлення (Power Switches)
Знеструмлення функціонального блоку здійснюється за допомогою масиву паралельних польових транзисторів, які від'єднують блок від загальної мережі живлення. Залежно від полярності розрізняють два підходи:
1. **Header-ключі на PMOS-транзисторах:** Вмикаються між реальною шиною живлення `Vdd` та віртуальною шиною живлення домену `Vdd_virtual`. Це найпоширеніша схема в цифрових SoC, оскільки вона зберігає спільну надійну підкладкову землю `Vss` (GND) незмінною по всьому кристалу.
2. **Footer-ключі на NMOS-транзисторах:** Вмикаються між віртуальною землею `Vss_virtual` та реальною землею `Vss`. NMOS-транзистори мають удвічі вищу рухливість носіїв заряду (електронів) і менший опір відкритого каналу `R_DS(on)` на одиницю площі, проте плаваючий потенціал підкладки NMOS створює паразитні зміщення порогів через ефект підкладки (Body Effect).

Силові ключі інтегрують безпосередньо в ряди стандартних комірок у вигляді регулярної сітки. Для запобігання надмірному падінню напруги (IR-Drop) сумарний опір усіх відкритих ключів домену проектують так, щоб падіння напруги не перевищувало 1–2% від `Vdd` при піковому струмі споживання.

### Комірки ізоляції (Isolation Cells)
Коли домен знеструмлюється, напруга на його віртуальній шині `Vdd_virtual` спадає до нуля через струми витоку. Вихідні сигнали такого домену переходять у плаваючий високоімпедансний стан із проміжними напругами (наприклад, 0.3–0.4 В). Якщо такий невизначений сигнал потрапить на вхід активного CMOS-вентиля у сусідньому ввімкненому домені, він одночасно відкриє і верхній PMOS, і нижній NMOS транзистори вхідного інвертора. Це спричиняє виникнення колосального наскрізного струму короткого замикання (Shoot-Through Current) між `Vdd` та `Vss`, що призводить до локального перегріву, просідання напруги та виходу мікросхеми з ладу.

Для запобігання цій аварії на всіх вихідних лініях комутованого домену встановлюють комірки ізоляції (Isolation Cells). Це логічні вентилі (AND або OR), які живляться від постійно активної шини сусіднього домену. За сигналом `ISO_EN = 1` комірка примусово фіксує вихідний сигнал у безпечному стані логічного нуля або логічної одиниці, повністю відсікаючи плаваючий вхід.

### Перетворювачі рівнів напруг (Level Shifters)
Різні домени SoC часто працюють при різних напругах: наприклад, високопродуктивне процесорне ядро працює при напрузі 0.75 В, а підсистема введення-виведення — при 1.8 В. Логічна одиниця з амплітудою 0.75 В не здатна надійно закрити PMOS-транзистор у домені 1.8 В (бо напруга затвор-витік `V_gs = 0.75 − 1.8 = −1.05 В` значно перевищує порогову напругу відкриття).

Перетворювачі рівнів (Level Shifters) містять перехресно увімкнені тригерні структури, які транслюють логічні рівні між доменами з різними напругами без виникнення витоків і з мінімальною затримкою поширення сигналу (типово 50–150 пікосекунд).

### Тригери збереження стану (Retention Flip-Flops)
Звичайний тригер втрачає свій стан у момент вимкнення живлення, що вимагало б повного холодного перезавантаження процесора (тривалістю від кількох мілісекунд до сотень мілісекунд).

Retention-тригери містять додаткову енергонезалежну «тіньову» засувку (Balloon Latch), підключену до окремої слабкострумової шини живлення `Vdd_ret` (Always-On). Перед вимкненням живлення контролер подає імпульс `SAVE`, копіюючи стан головного тригера в тіньову засувку. При пробудженні після відновлення напруги подається імпульс `RESTORE`, і процесор миттєво продовжує виконання коду з тієї самої інструкції, на якій зупинився.

---

## 2. Безглітчове перемикання тактових частот (Glitch-Free Clock Multiplexing)

Під час виконання процедури DVFS або переходу між генератором PLL та резервним низькочастотним генератором неприпустимо перемикати тактові сигнали за допомогою звичайного комбінаторного мультиплексора. Якщо сигнал керування селектором зміниться у момент, коли один тактовий сигнал перебуває у стані логічної одиниці, а інший — у стані нуля, на виході виникне короткий паразитний імпульс (глітч, тривалістю у частки наносекунди). Такий імпульс не здатний коректно перемкнути тригери конвеєра процесора, що призводить до руйнування даних і зависання системи.

Для безпечного перемикання застосовують спеціальну схему безглітчового мультиплексора (Glitch-Free MUX), побудовану на двох D-тригерах, що тактуються спадними фронтами відповідних годинникових сигналів `CLK0` та `CLK1`. Логіка схеми блокує вмикання нового тактового сигналу доти, доки поточний активний сигнал не перейде у стабільний стан логічного нуля. Це гарантує, що результуючий вихідний сигнал завжди зберігає правильні інтервали між фронтами.

---

## 3. Протоколи взаємодії з мікросхемою живлення (PMIC)

Керування напругами на рівні кристала координується із зовнішньою або вбудованою інтегральною схемою керування живленням (PMIC, англ. *Power Management IC*).

Для передавання команд зміни напруги в сучасних мобільних та серверах застосовують такі інтерфейси:
1. **MIPI SPMI (System Power Management Interface):** Спеціалізована двопровідна шина (SDATA та SCLK) із підтримкою тактових частот до 26 МГц, пріоритетного арбітражу між кількома майстрами та широкомовних команд. SPMI дозволяє змінити напругу живлення ядра за час менше 1–2 мікросекунд.
2. **I2C / PMBus:** Стандартна послідовна шина, що використовується в менш критичних за швидкістю вбудованих пристроях. Латентність передавання пакета становить 20–50 мікросекунд.
3. **Паралельні лінії VID (Voltage Identification):** Прямі цифрові лінії від SoC до фаз імпульсних стабілізаторів VRM, що забезпечують нульову протокольну затримку передавання коду напруги.

---

## 4. Ієрархія станів енергозбереження: від WFI до глибокого сну

Сучасні системи-на-кристалі не обмежуються бінарним вибором «увімкнено чи вимкнено». Замість цього PMC підтримує цілу ієрархію режимів низького споживання:
- **Рівень C0 (Active):** Усі домени увімкнені, тактування активне, ядра виконують інструкції на робочій частоті DVFS.
- **Рівень C1 (Clock Gated / WFI):** Процесор виконав інструкцію `WFI` (Wait For Interrupt). Живлення ядра залишається повним, але комірка ICG зупиняє подавання тактового сигналу на конвеєр. Економія: 30–50% енергії, вихід зі стану займає менше 1–2 тактів годинника.
- **Рівень C2 (Retention Sleep):** Тактування вимкнено, стан регістрів скопійовано у тіньові засувки, напруга живлення логіки знижується до мінімального порогу утримання (Retention Voltage `V_ret ≈ 0.5 В`). Витоки падають у 3–4 рази, вихід займає 5–10 мікросекунд.
- **Рівень C3 (Power Gated Core):** Силові ключі повністю розмикають лінію `Vdd_virtual` для окремого ядра. Стан збережено в L2-кеші або Retention-тригерах. Витоки ядра падають до нуля, час пробудження — 20–50 мікросекунд.
- **Рівень C4 (Cluster / System Deep Sleep):** Знеструмлюється весь кластер ядер разом із спільним L3-кешем та більшістю контролерів інтерконекту. Активним залишається лише домен AON із годинником реального часу RTC та лініями пробудження. Час повернення до роботи — 1–5 мілісекунд.

---

## 5. Регістрова карта контролера керування живленням (PMC)

Контролер живлення розташовується в постійно увімкненому домені (Always-On Domain, AON) і керує силовими ключами, комірками ізоляції, тактовими мультиплексорами та шиною зв'язку з PMIC.

Базова карта регістрів для кожного комутованого домену:
- `PWR_GATE_CTRL (0x00)`: Керування силовими ключами Header PMOS. Біт `0` — увімкнення першого ступеня (слабкі ключі зі збільшеним опором каналу), біт `1` — увімкнення другого ступеня (основні силові ключі з мінімальним `R_DS(on)`).
- `PWR_GATE_STATUS (0x04)`: Статус живлення. Біт `0` — апаратний сигнал `Power Good` від внутрішнього компаратора напруги домену, біт `1` — готовність каналу зв'язку з PMIC.
- `ISO_CTRL (0x08)`: Керування ізоляційними комірками. Біт `0` — сигнал `ISO_EN` (1 — виходи заблоковано в безпечному логічному рівні «0» або «1», 0 — ізоляцію знято).
- `RET_CTRL (0x0C)`: Керування збереженням/відновленням стану тригерів Retention. Біт `0` — `SAVE`, біт `1` — `RESTORE`.
- `CLK_GATE_CTRL (0x10)`: Керування тактуванням. Біт `0` — `CLK_EN` (подавання такту через комірку ICG), біти `16..31` — дільник тактової частоти.
- `RESET_CTRL (0x14)`: Скидання логіки домену. Біт `0` — `RESET_N` (активний низький рівень).
- `PMIC_VOLT_CMD (0x18)`: Регістр запису цільової напруги у мікровольтах для відправлення по шині SPMI/I2C.

---

## 6. Таблиця робочих точок продуктивності (OPP Table)

Фізична затримка поширення сигналу крізь логічні вентилі залежить від напруги живлення: вища напруга створює вищий струм заряду ємностей затворів, дозволяючи вентилям перемикатися швидше. Кожній частоті відповідає мінімально допустима напруга живлення, за якої задовольняються часові обмеження (Setup Time Constraints).

Таблиця робочих точок (Operating Performance Points, OPP):

| Рівень (OPP) | Частота `f_clk` | Напруга `V_dd` | Час стабілізації напруги `t_settle` |
| :--- | :--- | :--- | :--- |
| **OPP_LOW** | 400 МГц | 650 мВ (0.65 В) | 20 мкс |
| **OPP_NOM** | 1200 МГц | 750 мВ (0.75 В) | 25 мкс |
| **OPP_HIGH** | 2000 МГц | 900 мВ (0.90 В) | 35 мкс |
| **OPP_TURBO**| 2800 МГц | 1050 мВ (1.05 В) | 50 мкс |

---

## 7. Алгоритми та часові інваріанти

Під час перемикання станів живлення критично дотримуватися суворих часових інваріантів:

### Послідовність увімкнення домену (Power Up Sequence)
1. **Увімкнення ізоляції (`ISO_EN = 1`):** Запобігає потраплянню невизначених рівнів напруги (X-state) до зовнішніх доменів під час перехідних процесів.
2. **Ступінь 1 силових ключів (`STAGE1 = 1`):** Повільне заряджання внутрішньої паразитної ємності домену струмом, обмеженим опором перших ключів. Запобігає просіданню загальної шини живлення (Voltage Sag).
3. **Очікування сигналу `Power Good`:** Перевірка, що напруга всередині домену досягла 95% від номіналу.
4. **Ступінь 2 силових ключів (`STAGE2 = 1`):** Вмикання повної паралелі PMOS-транзисторів для мінімізації робочого падіння напруги.
5. **Відновлення стану (`RESTORE = 1`):** Копіювання збережених даних із резервних комірок у тригери процесора.
6. **Деактивація ізоляції (`ISO_EN = 0`):** Дозвіл вихідним сигналам домену надходити до інтерконекту.
7. **Увімкнення тактування (`CLK_EN = 1`):** Подавання тактового сигналу через ICG.
8. **Зняття сигналу скидання (`RESET_N = 1`):** Старт виконання інструкцій.

### Послідовність зміни режиму DVFS
- **Підвищення продуктивності (Scale UP):** Спочатку підвищуємо напругу `V_dd` через PMIC → чекаємо стабілізації `t_settle` → лише після цього підвищуємо тактову частоту `f_clk`. Якщо підвищити частоту раніше, логічні вентилі не встигнуть перемкнутися за скорочений період такту, що спричинить порушення часу встановлення (Setup Time Violation).
- **Зниження продуктивності (Scale DOWN):** Спочатку знижуємо тактову частоту `f_clk` → лише після цього надсилаємо команду на зниження напруги `V_dd`. Це запобігає роботі ядра на високій частоті при недостатньому рівні живлення.

---

## 8. Програмна реалізація мовами C та C++

У наведеному коді реалізовано повний набір функцій керування станами комутованого домену живлення та безпечного перемикання робочих точок DVFS.

У версії на C застосовано прямий доступ до відображених у пам'ять регістрів через макроси та покажчики типу `volatile uint32_t *`, що гарантує відсутність небажаної оптимізації компілятором порядку запису в апаратні регістри.

У версії на C++20 реалізація оформлена у вигляді суворо типізованого класу `PowerDomainController`, де зміщення регістрів та бітові маски інкапсульовано в типізовані переліки `enum class`, обробка помилок побудована на базі сучасного мовного засобу `std::expected` замість магічних числових кодів повернення, а для автоматичного контролю життєвого циклу активного стану домену створено обгортку `PowerDomainGuard`, яка реалізує ідіому RAII (Resource Acquisition Is Initialization).

:::tabs
```c
/* low_level_pmc_dvfs.h / .c — Драйвер керування живленням кристала SoC (C99) */
#include <stdint.h>
#include <stdbool.h>

#define PMC_BASE_ADDR           0x40020000UL
#define PMIC_I2C_TIMEOUT_CYCLES 500000UL
#define POWER_GOOD_TIMEOUT      100000UL

/* Зсуви регістрів домену */
#define REG_PWR_GATE_CTRL   0x00UL
#define REG_PWR_GATE_STATUS 0x04UL
#define REG_ISO_CTRL        0x08UL
#define REG_RET_CTRL        0x0CUL
#define REG_CLK_GATE_CTRL   0x10UL
#define REG_RESET_CTRL      0x14UL
#define REG_PMIC_VOLT_CMD   0x18UL

/* Бітові маски */
#define PWR_STAGE1_BIT      (1U << 0)
#define PWR_STAGE2_BIT      (1U << 1)
#define PWR_GOOD_BIT        (1U << 0)
#define ISO_ENABLE_BIT      (1U << 0)
#define RET_RESTORE_BIT     (1U << 1)
#define RET_SAVE_BIT        (1U << 0)
#define CLK_ENABLE_BIT      (1U << 0)
#define RESET_DEASSERT_BIT  (1U << 0)

typedef enum {
    OPP_LEVEL_LOW = 0,
    OPP_LEVEL_NOM = 1,
    OPP_LEVEL_HIGH = 2,
    OPP_LEVEL_TURBO = 3
} opp_level_t;

typedef struct {
    uint32_t freq_khz;
    uint32_t voltage_uv;
    uint32_t settle_delay_us;
} opp_point_t;

static const opp_point_t g_opp_table[4] = {
    [OPP_LEVEL_LOW]   = {  400000U,  650000U, 20U },
    [OPP_LEVEL_NOM]   = { 1200000U,  750000U, 25U },
    [OPP_LEVEL_HIGH]  = { 2000000U,  900000U, 35U },
    [OPP_LEVEL_TURBO] = { 2800000U, 1050000U, 50U }
};

static inline void mmio_write32(uintptr_t addr, uint32_t val) {
    *(volatile uint32_t *)addr = val;
}

static inline uint32_t mmio_read32(uintptr_t addr) {
    return *(volatile uint32_t *)addr;
}

static void delay_busy_cycles(uint32_t cycles) {
    for (volatile uint32_t i = 0; i < cycles; ++i) {
        __asm__ __volatile__("" ::: "memory");
    }
}

/* Імітація запису напруги у зовнішній PMIC через регістр контролера */
static bool pmic_set_voltage_uv(uintptr_t domain_base, uint32_t microvolts) {
    mmio_write32(domain_base + REG_PMIC_VOLT_CMD, microvolts);
    uint32_t timeout = PMIC_I2C_TIMEOUT_CYCLES;
    while ((mmio_read32(domain_base + REG_PWR_GATE_STATUS) & 0x02U) == 0U) {
        if (--timeout == 0U) {
            return false; /* Помилка зв'язку з PMIC */
        }
    }
    return true;
}

/* Увімкнення комутованого домену живлення */
bool soc_power_domain_up(uintptr_t domain_base) {
    /* Крок 1: Гарантувати активність ізоляції перед подаванням живлення */
    mmio_write32(domain_base + REG_ISO_CTRL, ISO_ENABLE_BIT);

    /* Крок 2: Увімкнути 1-й ступінь силових ключів (обмеження dI/dt) */
    mmio_write32(domain_base + REG_PWR_GATE_CTRL, PWR_STAGE1_BIT);

    /* Крок 3: Очікування апаратного сигналу Power Good */
    uint32_t timeout = POWER_GOOD_TIMEOUT;
    while ((mmio_read32(domain_base + REG_PWR_GATE_STATUS) & PWR_GOOD_BIT) == 0U) {
        if (--timeout == 0U) {
            /* Аварійне вимкнення ключа при збої живлення */
            mmio_write32(domain_base + REG_PWR_GATE_CTRL, 0U);
            return false;
        }
    }

    /* Крок 4: Увімкнути 2-й ступінь (основні силові PMOS-ключі) */
    mmio_write32(domain_base + REG_PWR_GATE_CTRL, PWR_STAGE1_BIT | PWR_STAGE2_BIT);

    /* Крок 5: Відновлення стану з тригерів Retention */
    mmio_write32(domain_base + REG_RET_CTRL, RET_RESTORE_BIT);
    delay_busy_cycles(500U);
    mmio_write32(domain_base + REG_RET_CTRL, 0U);

    /* Крок 6: Зняття ізоляції з виходів домену */
    mmio_write32(domain_base + REG_ISO_CTRL, 0U);

    /* Крок 7: Увімкнення тактового генератора */
    mmio_write32(domain_base + REG_CLK_GATE_CTRL, CLK_ENABLE_BIT);

    /* Крок 8: Зняття апаратного скидання (Reset Release) */
    mmio_write32(domain_base + REG_RESET_CTRL, RESET_DEASSERT_BIT);

    return true;
}

/* Знеструмлення домену живлення */
bool soc_power_domain_down(uintptr_t domain_base) {
    /* Крок 1: Встановлення апаратного скидання */
    mmio_write32(domain_base + REG_RESET_CTRL, 0U);

    /* Крок 2: Зупинка тактового сигналу */
    mmio_write32(domain_base + REG_CLK_GATE_CTRL, 0U);

    /* Крок 3: Збереження стану в Retention-тригери */
    mmio_write32(domain_base + REG_RET_CTRL, RET_SAVE_BIT);
    delay_busy_cycles(500U);
    mmio_write32(domain_base + REG_RET_CTRL, 0U);

    /* Крок 4: Увімкнення ізоляційних комірок */
    mmio_write32(domain_base + REG_ISO_CTRL, ISO_ENABLE_BIT);

    /* Крок 5: Розмикання силових ключів живлення */
    mmio_write32(domain_base + REG_PWR_GATE_CTRL, 0U);

    return true;
}

/* Безпечний перехід DVFS між робочими точками */
bool soc_dvfs_set_target_opp(uintptr_t domain_base, opp_level_t current_opp, opp_level_t target_opp) {
    if (target_opp == current_opp) {
        return true;
    }

    const opp_point_t *target = &g_opp_table[target_opp];

    if (target_opp > current_opp) {
        /* Підвищення продуктивності (Scale UP):
           1. Спочатку піднімаємо напругу */
        if (!pmic_set_voltage_uv(domain_base, target->voltage_uv)) {
            return false;
        }
        /* 2. Очікуємо стабілізації напруги */
        delay_busy_cycles(target->settle_delay_us * 100U);
        /* 3. Підвищуємо тактову частоту */
        mmio_write32(domain_base + REG_CLK_GATE_CTRL, (target->freq_khz / 1000U));
    } else {
        /* Зниження продуктивності (Scale DOWN):
           1. Спочатку знижуємо тактову частоту */
        mmio_write32(domain_base + REG_CLK_GATE_CTRL, (target->freq_khz / 1000U));
        /* 2. Знижуємо напругу для економії енергії P = C*V^2*f */
        if (!pmic_set_voltage_uv(domain_base, target->voltage_uv)) {
            return false;
        }
        /* 3. Очікуємо стабілізації перехідного процесу */
        delay_busy_cycles(target->settle_delay_us * 100U);
    }

    return true;
}
```
```cpp
// PowerDomainController.hpp — Ідіоматична C++20 обгортка керування живленням SoC
#pragma once
#include <cstdint>
#include <span>
#include <expected>
#include <array>
#include <string_view>

namespace soc::pmc {

enum class PmcError : uint8_t {
    PowerGoodTimeout,
    PmicCommunicationFailed,
    InvalidOppLevel,
    DomainAlreadyActive,
    DomainAlreadyOff
};

enum class OppLevel : uint8_t {
    Low = 0,
    Nominal = 1,
    High = 2,
    Turbo = 3
};

struct OppPoint {
    uint32_t freq_khz;
    uint32_t voltage_uv;
    uint32_t settle_delay_us;
};

class PowerDomainController {
public:
    static constexpr std::array<OppPoint, 4> OppTable = {{
        {  400'000,  650'000, 20 },
        { 1'200'000,  750'000, 25 },
        { 2'000'000,  900'000, 35 },
        { 2'800'000, 1'050'000, 50 }
    }};

    explicit constexpr PowerDomainController(uintptr_t base_address) noexcept
        : base_addr_{base_address} {}

    // Керування доменом живлення
    [[nodiscard]] std::expected<void, PmcError> power_up() const noexcept {
        // Крок 1: Ізоляція
        write_reg(RegOffset::IsoCtrl, BitMask::IsoEnable);

        // Крок 2: Перший ступінь ключів (захист від dI/dt)
        write_reg(RegOffset::PwrGateCtrl, BitMask::PwrStage1);

        // Крок 3: Очікування сигналу Power Good
        if (!wait_for_bit(RegOffset::PwrGateStatus, BitMask::PwrGood, 100'000)) {
            write_reg(RegOffset::PwrGateCtrl, 0); // Аварійне вимкнення
            return std::unexpected(PmcError::PowerGoodTimeout);
        }

        // Крок 4: Другий ступінь силових ключів
        write_reg(RegOffset::PwrGateCtrl, BitMask::PwrStage1 | BitMask::PwrStage2);

        // Крок 5: Відновлення Retention
        write_reg(RegOffset::RetCtrl, BitMask::RetRestore);
        busy_delay(500);
        write_reg(RegOffset::RetCtrl, 0);

        // Крок 6: Зняття ізоляції
        write_reg(RegOffset::IsoCtrl, 0);

        // Крок 7: Тактування
        write_reg(RegOffset::ClkGateCtrl, BitMask::ClkEnable);

        // Крок 8: Деактивація скидання
        write_reg(RegOffset::ResetCtrl, BitMask::ResetDeassert);

        return {};
    }

    [[nodiscard]] std::expected<void, PmcError> power_down() const noexcept {
        write_reg(RegOffset::ResetCtrl, 0);
        write_reg(RegOffset::ClkGateCtrl, 0);

        write_reg(RegOffset::RetCtrl, BitMask::RetSave);
        busy_delay(500);
        write_reg(RegOffset::RetCtrl, 0);

        write_reg(RegOffset::IsoCtrl, BitMask::IsoEnable);
        write_reg(RegOffset::PwrGateCtrl, 0);

        return {};
    }

    // Безпечний перехід DVFS
    [[nodiscard]] std::expected<void, PmcError> set_opp(OppLevel current, OppLevel target) const noexcept {
        if (current == target) {
            return {};
        }

        const auto curr_idx = static_cast<size_t>(current);
        const auto targ_idx = static_cast<size_t>(target);

        if (targ_idx >= OppTable.size()) {
            return std::unexpected(PmcError::InvalidOppLevel);
        }

        const auto& target_pt = OppTable[targ_idx];

        if (targ_idx > curr_idx) {
            // Scale UP: 1. Напруга -> 2. Затримка -> 3. Частота
            if (!set_pmic_voltage(target_pt.voltage_uv)) {
                return std::unexpected(PmcError::PmicCommunicationFailed);
            }
            busy_delay(target_pt.settle_delay_us * 100);
            write_reg(RegOffset::ClkGateCtrl, target_pt.freq_khz / 1'000);
        } else {
            // Scale DOWN: 1. Частота -> 2. Напруга
            write_reg(RegOffset::ClkGateCtrl, target_pt.freq_khz / 1'000);
            if (!set_pmic_voltage(target_pt.voltage_uv)) {
                return std::unexpected(PmcError::PmicCommunicationFailed);
            }
            busy_delay(target_pt.settle_delay_us * 100);
        }

        return {};
    }

private:
    enum class RegOffset : uintptr_t {
        PwrGateCtrl   = 0x00,
        PwrGateStatus = 0x04,
        IsoCtrl       = 0x08,
        RetCtrl       = 0x0C,
        ClkGateCtrl   = 0x10,
        ResetCtrl     = 0x14,
        PmicVoltCmd   = 0x18
    };

    struct BitMask {
        static constexpr uint32_t PwrStage1     = (1U << 0);
        static constexpr uint32_t PwrStage2     = (1U << 1);
        static constexpr uint32_t PwrGood       = (1U << 0);
        static constexpr uint32_t IsoEnable     = (1U << 0);
        static constexpr uint32_t RetSave       = (1U << 0);
        static constexpr uint32_t RetRestore    = (1U << 1);
        static constexpr uint32_t ClkEnable     = (1U << 0);
        static constexpr uint32_t ResetDeassert = (1U << 0);
    };

    uintptr_t base_addr_{0};

    void write_reg(RegOffset offset, uint32_t val) const noexcept {
        *reinterpret_cast<volatile uint32_t*>(base_addr_ + static_cast<uintptr_t>(offset)) = val;
    }

    [[nodiscard]] uint32_t read_reg(RegOffset offset) const noexcept {
        return *reinterpret_cast<const volatile uint32_t*>(base_addr_ + static_cast<uintptr_t>(offset));
    }

    [[nodiscard]] bool wait_for_bit(RegOffset offset, uint32_t mask, uint32_t timeout) const noexcept {
        while ((read_reg(offset) & mask) == 0U) {
            if (--timeout == 0) return false;
        }
        return true;
    }

    [[nodiscard]] bool set_pmic_voltage(uint32_t microvolts) const noexcept {
        write_reg(RegOffset::PmicVoltCmd, microvolts);
        return wait_for_bit(RegOffset::PwrGateStatus, 0x02U, 500'000);
    }

    static void busy_delay(uint32_t cycles) noexcept {
        for (volatile uint32_t i = 0; i < cycles; ++i) {
            asm volatile("" ::: "memory");
        }
    }
};

// RAII Guard для автоматичного керування життєвим циклом домену
class PowerDomainGuard {
public:
    explicit PowerDomainGuard(const PowerDomainController& controller)
        : controller_{controller} {
        is_active_ = controller_.power_up().has_value();
    }

    ~PowerDomainGuard() noexcept {
        if (is_active_) {
            (void)controller_.power_down();
        }
    }

    PowerDomainGuard(const PowerDomainGuard&) = delete;
    PowerDomainGuard& operator=(const PowerDomainGuard&) = delete;
    PowerDomainGuard(PowerDomainGuard&& other) noexcept
        : controller_{other.controller_}, is_active_{other.is_active_} {
        other.is_active_ = false;
    }

    [[nodiscard]] bool is_powered() const noexcept { return is_active_; }

private:
    const PowerDomainController& controller_;
    bool is_active_{false};
};

} // namespace soc::pmc
```
:::

---

## 9. Взаємодія з планувальником операційної системи (EAS та CPUFreq)

У сучасних мобільних операційних системах (наприклад, у ядрі Linux для Android) вибір поточної робочої точки OPP здійснюється підсистемою енергоефективного планування (Energy-Aware Scheduling, EAS) через регулятор частоти `schedutil`.

Планувальник постійно аналізує завантаженість черг запуску завдань (Pelth Metric) та температуру від вбудованих на кристал аналогових термодіодів. Якщо інтенсивність обчислень зростає або черга переповнюється, планувальник надсилає запит на підвищення OPP драйверу ядра, який виконує описану вище апаратну послідовність перемикання. При досягненні критичної температури (Thermal Throttle Threshold, зазвичай 85–95 °C) апаратний контролер безпеки примусово обмежує верхню межу OPP незалежно від запитів операційної системи, рятуючи чіп від перегріву.

---

## 10. Типові апаратні пастки та крайові випадки

1. **Стрибок пускового струму і просідання напруги живлення:**
   Одночасне замикання всіх паралельних PMOS-ключів домену миттєво відкриває шлях струму на заряджання десятків нанофарад внутрішньої розподіленої ємності. За формулою індуктивного викиду `V_drop = L_pkg · (dI/dt)` паразитні індуктивності BGA-кульок корпусу та металевих шин живлення спричиняють різке падіння напруги на сусідніх активних CPU-доменах, викликаючи їхнє аварійне перезавантаження або помилки в обчисленнях (Brownout). Лікування: суворе дво- або триступеневе послідовне вмикання ключів (Daisy-Chain Turn-on).

2. **Передчасне зняття ізоляції (`ISO_EN = 0`):**
   Якщо вимкнути ізоляційні комірки до того, як напруга всередині домену стабілізується на рівні `Power Good`, проміжні невизначені рівні напруг на входах CMOS-вентилів сусіднього активного домену призведуть до одночасного відкриття верхнього PMOS і нижнього NMOS транзисторів. Виникає колосальний струм наскрізного замикання (Shoot-Through Current), що може фізично пропалити металізацію кристала.

3. **Порушення послідовності DVFS при масштабуванні вгору:**
   Якщо підвищити частоту `f_clk` до того, як PMIC завершить регулювання напруги й заряд конденсаторів фільтрації, логічні вентилі на зниженій напрузі не встигнуть перемкнутися за скорочений період такту. Це призводить до порушення часу встановлення (Setup Time Violation) і зависання процесора.

4. **Зниження напруги до зменшення тактової частоти:**
   Зниження напруги живлення при збереженні високої тактової частоти миттєво уповільнює час проходження критичних шляхів комбінаторної логіки. Тригери фіксують старий стан до приходу нових даних, що призводить до непоправного спотворення регістрових значень операційної системи.
