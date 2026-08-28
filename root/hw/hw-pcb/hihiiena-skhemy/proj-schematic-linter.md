# ⚙️ Лінтер електричних схем на C та C++

Статичний аналіз вихідного коду став невіддільною частиною культури розробки програмного забезпечення: компілятори та лінтери щодня перевіряють типи, знаходять витоки пам'яті, вказують на неініціалізовані змінні та блокують небезпечні конструкції задовго до збірки релізу. Проте в інженерії апаратного забезпечення (Hardware Engineering) підхід до верифікації тривалий час залишався консервативним і спирався переважно на ручну ревізію креслень та базову перевірку електричних правил (Electrical Rule Check, ERC) всередині графічних САПР.

Ціна помилки в апаратному забезпеченні має принципово інший масштаб, ніж у програмуванні. Помилку в коді мікроконтролера можна виправити за лічені хвилини випуском патча прошивки. Схемотехнічна ж помилка — закорочені виходи двох активних драйверів, плаваючий вхід скидання процесора, відсутність робочої напруги на фільтруючому конденсаторі чи випадкове 4-стороннє перехрестя провідників — матеріалізується у фізичному кремнії, склотекстоліті та міді. Виявлення такого дефекту після виготовлення зразків означає повну зупинку робіт, спалені мікросхеми під час першого увімкнення (bringup), необхідність ручного перерізання доріжок скальпелем і запаювання навісних дротів, а в гіршому разі — повторне замовлення друкованих плат на заводі, що забирає тижні часу й тисячі доларів бюджету.

Вбудовані засоби ERC у комерційних та відкритих САПР (Altium Designer, KiCad, Cadence OrCAD) фокусуються лише на примітивній матриці взаємодії типів пінів («Output до Output» або «Input до порожнечі»). Вони не здійснюють семантичного аналізу схеми, не розуміють фізичних особливостей поведінки пасивних компонентів під постійною напругою, не оцінюють гігієну розташування ліній і не здатні виявити помилки в інженерних позначеннях номіналів. Для вирішення цього завдання розробляють спеціалізовані схемні лінтери (Schematic Linters) — автономні інструменти статичного аналізу, які інтегруються в системи контролю версій (Git) та конвеєри безперервної інтеграції (CI/CD), автоматично блокуючи некоректні схемотехнічні рішення ще на етапі створення запиту на злиття (Pull Request).

## Архітектура та структури даних схемного лінтера

Схемний лінтер функціонує за принципом класичного компіляторного аналізу. Він перетворює графічний або текстовий опис схеми на математичний граф зв'язності (Intermediate Representation, IR), після чого послідовно запускає над цим графом набір ізольованих правил перевірки (Rule Passes).

```
┌────────────────────────────────────────────────────────────────────────┐
│                      АРХІТЕКТУРА СХЕМНОГО ЛІНТЕРА                      │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  [ Файл схеми / Нетлист ] ───> [ Синтаксичний парсер (IR) ]            │
│                                            │                           │
│                                            ▼                           │
│                           [ Граф електричних зв'язків ]                │
│                           (Компоненти, Піни, Ланцюги, Вузли)           │
│                                            │                           │
│         ┌──────────────────────────────────┴──────────────────┐        │
│         ▼                                                     ▼        │
│  [ Модуль топологічної гігієни ]            [ Модуль фізичної семантики ]
│  - Пошук 4-way перехресть                   - Плаваючі входи КМОН      │
│  - Зміщені Т-вузли                          - Конфлікти драйверів      │
│  - Одинарні мітки (Single-pin)              - DC-bias деградація MLCC  │
│  - Векторна узгодженість шин                - Pull-up для Open-Drain   │
│  - Баланс Decoupling конденсаторів          - Захист від переполюсовки │
│         │                                                     │        │
│         └──────────────────────────────────┬──────────────────┘        │
│                                            ▼                           │
│                           [ Генератор звітів (CLI / JSON) ]            │
└────────────────────────────────────────────────────────────────────────┘
```

Модель даних лінтера оперує чотирма базовими сутностями:
1. **Компонент (`Component`):** Базовий елемент схеми, що має позиційне позначення (RefDes, наприклад `R101`, `C204`, `U1`), вихідний текстовий номінал (`Value`), посадкове місце (`Footprint`), рівень робочої напруги (`VoltageRating`), тип діелектрика або технології, прапорець монтажу (`IsDNP`) та перелік індексів фізичних виводів.
2. **Вивід (`Pin`):** Точка електричного підключення всередині компонента. Характеризується електричним типом (Input, Output, Open-Drain, Power In, Power Out, Passive), номером контакту та зв'язком з еквіпотенціальним ланцюгом.
3. **Електричний ланцюг (`Net`):** Еквіпотенціальний вузол схеми, утворений з'єднанням провідників або збігом імен міток. Містить ім'я ланцюга, тип області видимості (Local, Hierarchical, Global), розрахунковий рівень постійної напруги та перелік усіх підключених виводів компонентів.
4. **Геометричний вузол (`Junction`):** Точка на аркуші схеми, де сходяться фізичні лінії провідників. Зберігає координати (X, Y), назву аркуша та кількість підключених лінійних сегментів.

Зв'язок між виводами компонентів та ланцюгами будується за допомогою алгоритму системи неперетинних множин (Disjoint-Set Union, DSU / Union-Find). Це забезпечує лінійну часову складність `O(N · α(N))` під час об'єднання тисяч провідників і міток у єдині електричні кола.

## Синтаксичний аналіз та обробка форматів САПР

Для того щоб лінтер міг працювати безпосередньо з вихідними файлами схем, він містить синтаксичний аналізатор форматів EDA. Сучасний стандарт KiCad (версії 6, 7, 8) використовує S-expression формат (`.kicad_sch`), де кожен об'єкт креслення описується вкладеним списком:

```
(kicad_sch (version 20231120) (generator eeschema)
  (symbol (lib_id "Device:R_Small") (at 140.97 78.74 0) (unit 1)
    (property "Reference" "R101" (at 143.51 77.47 0))
    (property "Value" "4k7" (at 143.51 80.01 0))
    (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 140.97 78.74 0))
    (pin "1" (uuid "4f7a9c21-8b3e-4d1a-a1b2-c3d4e5f60001"))
    (pin "2" (uuid "4f7a9c21-8b3e-4d1a-a1b2-c3d4e5f60002"))
  )
  (wire (pts (xy 135.89 78.74) (xy 140.97 78.74)))
  (junction (at 135.89 78.74) (diameter 0) (color 0 0 0 0))
)
```

Лінтер реалізує швидкий потоковий лексер і рекурсивний спуск (Recursive Descent Parser). Під час проходження файлу парсер витягує координати лінійних сегментів `wire`, координати вузлів `junction`, позиційні позначення та властивості компонентів `property`. Якщо схема складається з багатьох ієрархічних аркушів, парсер рекурсивно завантажує всі дочірні файли, формуючи повне дерево проекту з розмежуванням областей видимості імен.

## Просторове хешування для пошуку геометричних перетинів

У великих схемах кількість лінійних сегментів провідників сягає десятків тисяч. Наївний алгоритм пошуку геометричних перетинів та підрахунку степеня кожного вузла має квадратичну складність `O(W²)`, де W — кількість сегментів. Це призводить до неприпустимих затримок під час роботи лінтера в CI/CD конвеєрах.

Для забезпечення миттєвого аналізу лінтер використовує метод просторового хешування (Spatial Hashing). Полотно кожного аркуша розбивається на віртуальну сітку з розміром комірки 100 mil × 100 mil (2.54 мм × 2.54 мм). Кожен відрізок провідника реєструється в хеш-таблиці лише для тих комірок, які перетинає його обмежувальний прямокутник (Bounding Box). Коли лінтер аналізує конкретний вузол `Junction` у точці (X, Y), він опитує виключно відповідну комірку просторової сітки та її 8 сусідів. Це знижує часову складність геометричного аудиту до строго лінійної `O(W)`, дозволяючи обробляти схеми на 50 000 компонентів менш ніж за 50 мілісекунд.

## П'ять обов'язкових правил схемотехнічного аудиту

Ядро лінтера реалізує набір правил, кожне з яких спрямоване на виявлення конкретної фізичної або топологічної проблеми:

### 1. Детектор 4-сторонніх перехресть (4-Way Junction Rule)
Під час креслення схем сходження чотирьох провідників в одну спільну точку є найнебезпечнішим джерелом помилок. Якщо графічна точка вузла зникне під час друку або растрування, 4-сторонній вузол стає візуально невідрізним від звичайного перетину двох ізольованих ліній. Лінтер аналізує всі вузлові об'єкти типу `Junction`: якщо степінь вузла (кількість підключених провідників) дорівнює або перевищує 4, правило генерує помилку `Severity::Error` і вказує координати, вимагаючи замінити хрестоподібне з'єднання на два зміщені Т-вузли (Staggered T-junctions).

### 2. Валідатор плаваючих КМОН-входів (Floating CMOS Inputs & Pull-Ups)
Вхідні каскади сучасних цифрових мікросхем виконані за технологією КМОН (CMOS) і мають вхідний опір понад 10¹² Ом. Якщо такий вхід залишається ні до чого не під'єднаним (плаваючий вхід, Floating Input), він вловлює навіть слабкі електромагнітні завади від сусідніх ліній. Напруга на затворах вхідних польових транзисторів встановлюється на проміжному рівні (близько половини напруги живлення), через що p-канальний та n-канальний транзистори вхідного інвертора одночасно відкриваються. Це викликає наскрізний струм короткого замикання крізь кристал мікросхеми величиною від одиниць до десятків міліампер на кожен вентиль, спричиняючи спотворення логічних рівнів, паразитичний нагрів та раптове зависання процесора.

Лінтер перевіряє кожен ланцюг: якщо в ньому присутні піни типу `PIN_TYPE_INPUT`, але немає жодного активного виходу (`PIN_TYPE_OUTPUT`, `PIN_TYPE_POWER_OUT`), лінтер перевіряє наявність резисторів підтяжки (Pull-Up до живлення або Pull-Down до землі). Якщо підтяжка відсутня і ланцюг не є рейкою живлення, генерується попередження `Severity::Warning`.

### 3. Контроль конфліктів активних драйверів (Driver Collision Check)
Якщо до одного ланцюга підключено два або більше виводів типу `PIN_TYPE_OUTPUT` або `PIN_TYPE_POWER_OUT`, виникає пряме коротке замикання у разі встановлення ними протилежних логічних рівнів. Верхній транзистор одного драйвера закорочується на нижній транзистор другого через міліомний опір відкритого каналу, що спалює вихідний каскад за мікросекунди. Лінтер забороняє наявність більше одного активного виходу на ланцюг. Виняток робиться виключно для виводів типу `PIN_TYPE_OPEN_DRAIN` / `PIN_TYPE_OPEN_COLLECTOR` (наприклад, шини I2C, 1-Wire), для яких лінтер додатково перевіряє наявність обов'язкового резистора підтяжки до шини живлення.

### 4. Контроль одиночних висячих міток та шинної консистентності (Single-Pin Nets & Buses)
Коли інженер на одному аркуші підписує провідник `SPI_MISO`, а на іншому через одруківку створює мітку `SPI_MIS0` (із цифрою нуль замість літери O), САПР тихо створює два окремі незалежні ланцюги. Редактор не видасть попередження, але зв'язок між мікроконтролером та датчиком буде фізично розірвано. Лінтер виявляє всі ланцюги, що мають мітку, але містять лише один контактний вивід (Single-Pin Net), попереджаючи про ймовірну друкарську помилку. Також перевіряється консистентність векторних шин: чи відповідають сигнали `DATA0`..`DATA7` діапазону оголошеної шини `DATA[7..0]`.

### 5. Розрахунок дейтингу напруги керамічних конденсаторів (DC-Bias Derating)
Популярні багатошарові керамічні конденсатори (MLCC) класу діелектрика X7R, X5R та Y5V мають виражену залежність ємності від прикладеної постійної напруги зміщення (DC-bias effect). За напруги, близької до номінальної робочої напруги конденсатора, реальна ефективна ємність сегнетоелектрика через насичення доменної структури падає на 50-80% від номіналу.

Якщо на шині живлення 12V встановити конденсатор `10uF 16V X5R`, його реальна ємність у робочому режимі складе лише 3-4 мкФ. Для імпульсного перетворювача це означає катастрофічне зростання вихідних пульсацій та вихід контуру регулювання зі стану фазової стійкості. Лінтер зіставляє робочу напругу шини живлення з атрибутом `VoltageRating` конденсатора. Якщо коефіцієнт запасу становить менше 1.5x (рекомендовано 2.0x), лінтер видає попередження про дефект дейтингу. Крім того, лінтер перевіряє інженерний синтаксис запису номіналів пасивних елементів, відхиляючи небезпечні крапки (`4.7k` -> `4k7`, `0.1u` -> `100n`).

## Розширені правила: баланс блокувальних ємностей та диференціальні пари

Окрім базових топологічних перевірок, повнофункціональний схемний лінтер містить правила аудиту живлення, цілісності сигналів та аналого-цифрового поділу:

1. **Баланс блокувальних конденсаторів (Decoupling Balance):** Для великих цифрових ІС (мікроконтролерів, FPGA) лінтер підраховує кількість пар виводів живлення `VDD`/`VSS`. На кожну таку пару в схемі повинен припадати щонайменше один високочастотний керамічний конденсатор ємністю 100 нФ. Якщо мікроконтролер має 6 виводів `VDD`, а на схемі встановлено лише 2 конденсатори, лінтер генерує дефект `Severity::Warning` про загрозу виникнення шуму одночасного перемикання (Simultaneous Switching Noise, SSN / Ground Bounce).
2. **Симетрія диференціальних пар:** Лінтер знаходить ланцюги з суфіксами `_P` та `_N` (наприклад, `USB_D_P` та `USB_D_N`). Він перевіряє наявність однакових пасивних компонентів (наприклад, узгоджувальних послідовних резисторів або синфазного дроселя) в обох плечах пари. Якщо резистор встановлено лише в плюсовому плечі, лінтер попереджає про асиметрію імпедансу.
3. **Захист від переполюсовки зовнішніх джерел:** Лінтер перевіряє ланцюги, що починаються від зовнішніх роз'ємів живлення (`VBUS`, `DC_JACK`, `BAT_IN`). Якщо між контактом роз'єму та внутрішньою шиною живлення відсутній захисний діод Шотткі або комутуючий P-канальний MOSFET, лінтер генерує застереження `Severity::Warning` про відсутність апаратного захисту від помилкового підключення живлення зворотної полярності.
4. **Фільтрація аналогового живлення (VDDA / VREF):** Для змішаних мікросхем (MCU з АЦП) лінтер відстежує зв'язок між цифровою шиною `+3.3V` та аналоговим виводом `VDDA`. Якщо ці кола з'єднані безпосередньо без феритової намистини (Ferrite Bead `FB`) або LC-фільтра, лінтер попереджає про проникнення цифрового комутаційного шуму в аналоговий тракт перетворення.
5. **Контроль топології Net-Tie:** Лінтер перевіряє, чи правильно підключено розділені земляні полігони `AGND` та `DGND`. Якщо на схемі виявлено паразитне друге з'єднання цих земель в обхід центрального компонента `NT1` (Net-Tie), лінтер фіксує виникнення земляної петлі (Ground Loop).

## Повна реалізація лінтера мовами C99 та C++20

Нижче наведено повну реалізацію лінтера принципових схем. Програма моделює граф зв'язності типової схемотехнічної підсистеми з навмисно закладеними помилками (4-сторонній вузол, колізія двох виходів на шині MISO, плаваючий вхід переривання, поодинока висяча мітка через одруківку, нестача запасу напруги на блокувальному конденсаторі 12V та незахищена крапка в номіналі резистора) і генерує повний діагностичний звіт.

:::tabs
@tab C (C99)
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>

#define MAX_NAME_LEN    32
#define MAX_PINS        64
#define MAX_COMPONENTS  32
#define MAX_NETS        32
#define MAX_JUNCTIONS   32
#define MAX_ISSUES      64

typedef enum {
    SEVERITY_INFO,
    SEVERITY_WARNING,
    SEVERITY_ERROR
} IssueSeverity;

typedef enum {
    PIN_INPUT,
    PIN_OUTPUT,
    PIN_OPEN_DRAIN,
    PIN_POWER_IN,
    PIN_POWER_OUT,
    PIN_PASSIVE
} PinType;

typedef struct {
    char name[MAX_NAME_LEN];
    PinType type;
    int parent_comp_idx;
    int net_idx;
} Pin;

typedef struct {
    char refdes[MAX_NAME_LEN];
    char value_raw[MAX_NAME_LEN];
    double value_numeric;
    double voltage_rating;
    bool is_dnp;
    int pin_indices[16];
    int pin_count;
} Component;

typedef struct {
    char name[MAX_NAME_LEN];
    int pin_indices[MAX_PINS];
    int pin_count;
    double operating_voltage;
    bool is_power_rail;
} Net;

typedef struct {
    double x;
    double y;
    int connected_wires_count;
    char sheet[MAX_NAME_LEN];
} Junction;

typedef struct {
    IssueSeverity severity;
    char rule_code[16];
    char message[128];
} LintIssue;

typedef struct {
    Component components[MAX_COMPONENTS];
    int comp_count;
    Pin pins[MAX_PINS];
    int pin_count;
    Net nets[MAX_NETS];
    int net_count;
    Junction junctions[MAX_JUNCTIONS];
    int junction_count;
    LintIssue issues[MAX_ISSUES];
    int issue_count;
} SchematicDesign;

void init_design(SchematicDesign *d) {
    memset(d, 0, sizeof(SchematicDesign));
}

void add_issue(SchematicDesign *d, IssueSeverity sev, const char *code, const char *msg) {
    if (d->issue_count >= MAX_ISSUES) return;
    LintIssue *iss = &d->issues[d->issue_count++];
    iss->severity = sev;
    strncpy(iss->rule_code, code, sizeof(iss->rule_code) - 1);
    strncpy(iss->message, msg, sizeof(iss->message) - 1);
}

int add_component(SchematicDesign *d, const char *refdes, const char *val, double volt_rating) {
    if (d->comp_count >= MAX_COMPONENTS) return -1;
    int idx = d->comp_count++;
    Component *c = &d->components[idx];
    strncpy(c->refdes, refdes, MAX_NAME_LEN - 1);
    strncpy(c->value_raw, val, MAX_NAME_LEN - 1);
    c->voltage_rating = volt_rating;
    c->is_dnp = false;
    c->pin_count = 0;
    return idx;
}

int add_net(SchematicDesign *d, const char *name, double op_voltage, bool is_pwr) {
    if (d->net_count >= MAX_NETS) return -1;
    int idx = d->net_count++;
    Net *n = &d->nets[idx];
    strncpy(n->name, name, MAX_NAME_LEN - 1);
    n->operating_voltage = op_voltage;
    n->is_power_rail = is_pwr;
    n->pin_count = 0;
    return idx;
}

void connect_pin(SchematicDesign *d, int comp_idx, const char *pin_name, PinType type, int net_idx) {
    if (d->pin_count >= MAX_PINS || comp_idx < 0 || net_idx < 0) return;
    int p_idx = d->pin_count++;
    Pin *p = &d->pins[p_idx];
    strncpy(p->name, pin_name, MAX_NAME_LEN - 1);
    p->type = type;
    p->parent_comp_idx = comp_idx;
    p->net_idx = net_idx;

    Component *c = &d->components[comp_idx];
    c->pin_indices[c->pin_count++] = p_idx;

    Net *n = &d->nets[net_idx];
    n->pin_indices[n->pin_count++] = p_idx;
}

void add_junction(SchematicDesign *d, double x, double y, int wires, const char *sheet) {
    if (d->junction_count >= MAX_JUNCTIONS) return;
    Junction *j = &d->junctions[d->junction_count++];
    j->x = x;
    j->y = y;
    j->connected_wires_count = wires;
    strncpy(j->sheet, sheet, MAX_NAME_LEN - 1);
}

// ── ПЕРЕВІРКА 1: Детекція 4-сторонніх перехресть ─────────────────────────────
void check_4way_junctions(SchematicDesign *d) {
    for (int i = 0; i < d->junction_count; ++i) {
        Junction *j = &d->junctions[i];
        if (j->connected_wires_count >= 4) {
            char buf[128];
            snprintf(buf, sizeof(buf), "4-сторонній вузол на аркуші '%s' (X=%.1f, Y=%.1f). Замініть на зміщені Т-вузли!",
                     j->sheet, j->x, j->y);
            add_issue(d, SEVERITY_ERROR, "HYG-01-4WAY", buf);
        }
    }
}

// ── ПЕРЕВІРКА 2: Конфлікти драйверів та плаваючі входи ──────────────────────
void check_net_drivers(SchematicDesign *d) {
    for (int i = 0; i < d->net_count; ++i) {
        Net *n = &d->nets[i];
        int drivers_out = 0;
        int drivers_od = 0;
        int inputs_count = 0;
        int passives_count = 0;

        for (int p = 0; p < n->pin_count; ++p) {
            Pin *pin = &d->pins[n->pin_indices[p]];
            if (pin->type == PIN_OUTPUT || pin->type == PIN_POWER_OUT) drivers_out++;
            else if (pin->type == PIN_OPEN_DRAIN) drivers_od++;
            else if (pin->type == PIN_INPUT || pin->type == PIN_POWER_IN) inputs_count++;
            else if (pin->type == PIN_PASSIVE) passives_count++;
        }

        // Конфлікт виходів: більше 1 активного виходу без Open-Drain
        if (drivers_out > 1) {
            char buf[128];
            snprintf(buf, sizeof(buf), "Ланцюг '%s' має %d активних виходів Output. Коротке замикання драйверів!",
                     n->name, drivers_out);
            add_issue(d, SEVERITY_ERROR, "ERC-02-COLLISION", buf);
        }

        // Плаваючий вхід: є входи, але немає жодного драйвера і жодного пасивного компонента (підтяжки)
        if (inputs_count > 0 && drivers_out == 0 && drivers_od == 0 && passives_count == 0 && !n->is_power_rail) {
            char buf[128];
            snprintf(buf, sizeof(buf), "Ланцюг '%s' має %d входів, але не має джерела сигналу або підтяжки (Floating Input).",
                     n->name, inputs_count);
            add_issue(d, SEVERITY_WARNING, "ERC-03-FLOATING", buf);
        }

        // Поодинока висяча мітка (Single-pin net)
        if (n->pin_count == 1 && !n->is_power_rail) {
            char buf[128];
            snprintf(buf, sizeof(buf), "Ланцюг '%s' підключений лише до одного виводу. Можлива одруківка в мітці!",
                     n->name);
            add_issue(d, SEVERITY_WARNING, "HYG-04-SINGLEPIN", buf);
        }
    }
}

// ── ПЕРЕВІРКА 3: Запас напруги та синтаксис номіналів ────────────────────────
void check_components_hygiene(SchematicDesign *d) {
    for (int i = 0; i < d->comp_count; ++i) {
        Component *c = &d->components[i];
        if (c->is_dnp) continue;

        // Перевірка конденсаторів на DC-bias запас напруги
        if (c->refdes[0] == 'C') {
            for (int p = 0; p < c->pin_count; ++p) {
                Net *n = &d->nets[d->pins[c->pin_indices[p]].net_idx];
                if (n->is_power_rail && n->operating_voltage > 0.0) {
                    if (c->voltage_rating <= 0.0) {
                        char buf[128];
                        snprintf(buf, sizeof(buf), "Конденсатор %s (%s) на шині %.1fV не має вказаної робочої напруги!",
                                 c->refdes, c->value_raw, n->operating_voltage);
                        add_issue(d, SEVERITY_ERROR, "HYG-05-NOVOLD", buf);
                    } else if (c->voltage_rating < n->operating_voltage * 1.5) {
                        char buf[128];
                        snprintf(buf, sizeof(buf), "Конденсатор %s (номінал %.0fV) на шині %.1fV має недостатній запас напруги (<1.5x). Ризик DC-bias деградації ємності!",
                                 c->refdes, c->voltage_rating, n->operating_voltage);
                        add_issue(d, SEVERITY_WARNING, "HYG-06-DERATING", buf);
                    }
                }
            }
        }

        // Перевірка інженерного форматування (небезпечна крапка замість R-S-H)
        if (strchr(c->value_raw, '.') != NULL) {
            char buf[128];
            snprintf(buf, sizeof(buf), "Компонент %s: Номінал '%s' містить крапку. Рекомендовано синтаксис IEC (напр. '4k7', '0R1').",
                     c->refdes, c->value_raw);
            add_issue(d, SEVERITY_INFO, "HYG-07-DOTVALUE", buf);
        }
    }
}

void run_all_linter_checks(SchematicDesign *d) {
    check_4way_junctions(d);
    check_net_drivers(d);
    check_components_hygiene(d);
}

void print_linter_report(const SchematicDesign *d) {
    printf("====================================================================\n");
    printf("                  ЗВІТ СХЕМНОГО ЛІНТЕРА (C99)                       \n");
    printf("====================================================================\n");
    printf("Проаналізовано: %d компонентів, %d ланцюгів, %d вузлів.\n\n",
           d->comp_count, d->net_count, d->junction_count);

    if (d->issue_count == 0) {
        printf("[OK] Усі перевірки пройдено успішно. Дефектів не виявлено.\n");
        return;
    }

    for (int i = 0; i < d->issue_count; ++i) {
        const LintIssue *iss = &d->issues[i];
        const char *sev_str = "INFO";
        if (iss->severity == SEVERITY_WARNING) sev_str = "ПОПЕРЕДЖЕННЯ";
        else if (iss->severity == SEVERITY_ERROR) sev_str = "ПОМИЛКА";

        printf("[%s] [%s] %s\n", sev_str, iss->rule_code, iss->message);
    }
    printf("====================================================================\n");
    printf("Разом знайдено зауважень: %d\n", d->issue_count);
}

int main(void) {
    SchematicDesign design;
    init_design(&design);

    // Створюємо ланцюги живлення та сигналів
    int net_vcc12 = add_net(&design, "+12V", 12.0, true);
    int net_gnd   = add_net(&design, "GND", 0.0, true);
    int net_miso  = add_net(&design, "SPI_MISO", 3.3, false);
    int net_alert = add_net(&design, "IRQ_ALERT", 3.3, false);
    int net_typo  = add_net(&design, "SENSOR_DAT0", 3.3, false);

    // Додаємо компоненти
    int c1 = add_component(&design, "C101", "10u", 16.0); // 16V на лінії 12V -> Derating warning
    connect_pin(&design, c1, "1", PIN_PASSIVE, net_vcc12);
    connect_pin(&design, c1, "2", PIN_PASSIVE, net_gnd);

    int r1 = add_component(&design, "R101", "4.7k", 0.0); // Крапка в номіналі -> Info warning
    connect_pin(&design, r1, "1", PIN_PASSIVE, net_vcc12);
    connect_pin(&design, r1, "2", PIN_PASSIVE, net_miso);

    int u1 = add_component(&design, "U1", "STM32F4", 0.0);
    connect_pin(&design, u1, "PA6", PIN_OUTPUT, net_miso); // Вихід 1 на MISO
    connect_pin(&design, u1, "PB0", PIN_INPUT, net_alert); // Плаваючий вхід ALERT

    int u2 = add_component(&design, "U2", "ADC_DRIVER", 0.0);
    connect_pin(&design, u2, "SDO", PIN_OUTPUT, net_miso); // Вихід 2 на MISO -> Driver collision!
    connect_pin(&design, u2, "DATA", PIN_OUTPUT, net_typo); // Єдиний пін на net_typo -> Single pin warning!

    // Додаємо заборонений 4-сторонній вузол
    add_junction(&design, 125.0, 80.0, 4, "Power_Sheet.kicad_sch");

    // Запуск аудиту
    run_all_linter_checks(&design);
    print_linter_report(&design);

    return 0;
}
```
@tab C++ (C++20)
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <unordered_map>
#include <format>
#include <algorithm>

enum class Severity {
    Info,
    Warning,
    Error
};

enum class PinType {
    Input,
    Output,
    OpenDrain,
    PowerIn,
    PowerOut,
    Passive
};

struct Pin {
    std::string name;
    PinType type;
    size_t parent_component_idx;
    size_t net_idx;
};

struct Component {
    std::string refdes;
    std::string value_raw;
    std::optional<double> voltage_rating;
    bool is_dnp{false};
    std::vector<size_t> pin_indices;
};

struct Net {
    std::string name;
    double operating_voltage{0.0};
    bool is_power_rail{false};
    std::vector<size_t> pin_indices;
};

struct Junction {
    double x{0.0};
    double y{0.0};
    int connected_wires{0};
    std::string sheet_name;
};

struct Issue {
    Severity severity;
    std::string rule_code;
    std::string message;
};

class SchematicLinter {
public:
    size_t add_net(std::string name, double op_voltage = 0.0, bool is_pwr = false) {
        nets_.push_back(Net{
            .name = std::move(name),
            .operating_voltage = op_voltage,
            .is_power_rail = is_pwr,
            .pin_indices = {}
        });
        return nets_.size() - 1;
    }

    size_t add_component(std::string refdes, std::string val, std::optional<double> volt_rating = std::nullopt) {
        components_.push_back(Component{
            .refdes = std::move(refdes),
            .value_raw = std::move(val),
            .voltage_rating = volt_rating,
            .is_dnp = false,
            .pin_indices = {}
        });
        return components_.size() - 1;
    }

    void connect_pin(size_t comp_idx, std::string pin_name, PinType type, size_t net_idx) {
        if (comp_idx >= components_.size() || net_idx >= nets_.size()) return;

        const size_t pin_idx = pins_.size();
        pins_.push_back(Pin{
            .name = std::move(pin_name),
            .type = type,
            .parent_component_idx = comp_idx,
            .net_idx = net_idx
        });

        components_[comp_idx].pin_indices.push_back(pin_idx);
        nets_[net_idx].pin_indices.push_back(pin_idx);
    }

    void add_junction(double x, double y, int wires, std::string sheet) {
        junctions_.push_back(Junction{
            .x = x,
            .y = y,
            .connected_wires = wires,
            .sheet_name = std::move(sheet)
        });
    }

    void run_checks() {
        issues_.clear();
        check_4way_junctions();
        check_net_drivers();
        check_component_hygiene();
    }

    void print_report() const {
        std::cout << "====================================================================\n";
        std::cout << "                 ЗВІТ СХЕМНОГО ЛІНТЕРА (C++20)                      \n";
        std::cout << "====================================================================\n";
        std::cout << std::format("Проаналізовано: {} компонентів, {} ланцюгів, {} вузлів.\n\n",
                                 components_.size(), nets_.size(), junctions_.size());

        if (issues_.empty()) {
            std::cout << "[OK] Усі правила гігієни виконано успішно.\n";
            return;
        }

        for (const auto &iss : issues_) {
            std::string_view sev_str = "INFO";
            if (iss.severity == Severity::Warning) sev_str = "ПОПЕРЕДЖЕННЯ";
            else if (iss.severity == Severity::Error) sev_str = "ПОМИЛКА";

            std::cout << std::format("[{}] [{}] {}\n", sev_str, iss.rule_code, iss.message);
        }
        std::cout << "====================================================================\n";
        std::cout << std::format("Разом зафіксовано зауважень: {}\n", issues_.size());
    }

    [[nodiscard]] const std::vector<Issue>& issues() const noexcept { return issues_; }

private:
    void add_issue(Severity sev, std::string code, std::string msg) {
        issues_.push_back(Issue{.severity = sev, .rule_code = std::move(code), .message = std::move(msg)});
    }

    void check_4way_junctions() {
        for (const auto &j : junctions_) {
            if (j.connected_wires >= 4) {
                add_issue(Severity::Error, "HYG-01-4WAY",
                    std::format("4-сторонній вузол на аркуші '{}' (X={:.1f}, Y={:.1f}). Замініть на зміщені Т-вузли!",
                                j.sheet_name, j.x, j.y));
            }
        }
    }

    void check_net_drivers() {
        for (const auto &net : nets_) {
            int out_drivers = 0;
            int od_drivers = 0;
            int inputs = 0;
            int passives = 0;

            for (size_t p_idx : net.pin_indices) {
                switch (pins_[p_idx].type) {
                    case PinType::Output:
                    case PinType::PowerOut:
                        out_drivers++;
                        break;
                    case PinType::OpenDrain:
                        od_drivers++;
                        break;
                    case PinType::Input:
                    case PinType::PowerIn:
                        inputs++;
                        break;
                    case PinType::Passive:
                        passives++;
                        break;
                }
            }

            // Колізія виходів
            if (out_drivers > 1) {
                add_issue(Severity::Error, "ERC-02-COLLISION",
                    std::format("Ланцюг '{}' має {} активних виходів Output. Коротке замикання драйверів!",
                                net.name, out_drivers));
            }

            // Плаваючий вхід
            if (inputs > 0 && out_drivers == 0 && od_drivers == 0 && passives == 0 && !net.is_power_rail) {
                add_issue(Severity::Warning, "ERC-03-FLOATING",
                    std::format("Ланцюг '{}' має {} входів без джерела сигналу або резистора підтяжки.",
                                net.name, inputs));
            }

            // Поодинока мітка
            if (net.pin_indices.size() == 1 && !net.is_power_rail) {
                add_issue(Severity::Warning, "HYG-04-SINGLEPIN",
                    std::format("Ланцюг '{}' має лише одне підключення. Перевірте наявність одруківок у мітці!",
                                net.name));
            }
        }
    }

    void check_component_hygiene() {
        for (const auto &comp : components_) {
            if (comp.is_dnp) continue;

            // Перевірка конденсаторів
            if (!comp.refdes.empty() && comp.refdes[0] == 'C') {
                for (size_t p_idx : comp.pin_indices) {
                    const auto &net = nets_[pins_[p_idx].net_idx];
                    if (net.is_power_rail && net.operating_voltage > 0.0) {
                        if (!comp.voltage_rating.has_value() || *comp.voltage_rating <= 0.0) {
                            add_issue(Severity::Error, "HYG-05-NOVOLD",
                                std::format("Конденсатор {} ({}) на шині {:.1f}V не має робочої напруги!",
                                            comp.refdes, comp.value_raw, net.operating_voltage));
                        } else if (*comp.voltage_rating < net.operating_voltage * 1.5) {
                            add_issue(Severity::Warning, "HYG-06-DERATING",
                                std::format("Конденсатор {} ({:.0f}V) на шині {:.1f}V має недостатній запас (<1.5x). Ризик DC-bias деградації!",
                                            comp.refdes, *comp.voltage_rating, net.operating_voltage));
                        }
                    }
                }
            }

            // Перевірка крапки у номіналі
            if (comp.value_raw.find('.') != std::string::npos) {
                add_issue(Severity::Info, "HYG-07-DOTVALUE",
                    std::format("Компонент {}: Номінал '{}' містить крапку замість синтаксису R-S-H.",
                                comp.refdes, comp.value_raw));
            }
        }
    }

    std::vector<Component> components_;
    std::vector<Pin> pins_;
    std::vector<Net> nets_;
    std::vector<Junction> junctions_;
    std::vector<Issue> issues_;
};

int main() {
    SchematicLinter linter;

    const auto vcc12 = linter.add_net("+12V", 12.0, true);
    const auto gnd   = linter.add_net("GND", 0.0, true);
    const auto miso  = linter.add_net("SPI_MISO", 3.3, false);
    const auto alert = linter.add_net("IRQ_ALERT", 3.3, false);
    const auto typo  = linter.add_net("SENSOR_DAT0", 3.3, false);

    const auto c1 = linter.add_component("C101", "10u", 16.0); // 16V на 12V -> Derating warning
    linter.connect_pin(c1, "1", PinType::Passive, vcc12);
    linter.connect_pin(c1, "2", PinType::Passive, gnd);

    const auto r1 = linter.add_component("R101", "4.7k"); // Крапка -> Info warning
    linter.connect_pin(r1, "1", PinType::Passive, vcc12);
    linter.connect_pin(r1, "2", PinType::Passive, miso);

    const auto u1 = linter.add_component("U1", "STM32F4");
    linter.connect_pin(u1, "PA6", PinType::Output, miso);
    linter.connect_pin(u1, "PB0", PinType::Input, alert); // Плаваючий вхід

    const auto u2 = linter.add_component("U2", "ADC_DRIVER");
    linter.connect_pin(u2, "SDO", PinType::Output, miso); // Колізія виходів на MISO
    linter.connect_pin(u2, "DATA", PinType::Output, typo); // Single-pin net

    linter.add_junction(125.0, 80.0, 4, "Power_Sheet.kicad_sch"); // 4-way перехрестя

    linter.run_checks();
    linter.print_report();

    return 0;
}
```
:::

## Інтеграція лінтера в конвеєри безперервної інтеграції (Hardware CI/CD)

Впровадження схемного лінтера у виробничий процес розробки електронних пристроїв докорінно змінює культуру проектування в інженерних командах. Замість тривалого суб'єктивного узгодження схем на нарадах перевірка базових правил гігієни стає повністю автоматизованою та математично детермінованою.

Типовий конвеєр автоматичної перевірки схем в інфраструктурі GitLab CI або GitHub Actions складається з таких обов'язкових кроків:

1. **Тригер репозиторію:** Конвеєр запускається автоматично під час створення нового запиту на злиття (Merge Request) або кожного оновлення гілки розробки апаратного забезпечення.
2. **Експорт артефактів проектування:** Утиліта командного рядка САПР у headless-режимі (наприклад, `kicad-cli sch export netlist` або скрипт парсингу формату `.kicad_sch`) вивантажує актуальний нетлист проекту та координатні карти вузлів і з'єднань у форматі JSON.
3. **Виконання аудиту схемним лінтером:** Бінарний файл лінтера запускається над згенерованими даними. Для інтеграції зі стандартними панелями звітності CI/CD вивід результатів додатково дублюється у форматі JUnit XML (`--format=junit --output=report.xml`) або SARIF (Static Analysis Results Interchange Format) для GitHub Code Scanning.
4. **Блокування небезпечних змін (Quality Gate):** Якщо лінтер фіксує хоча б одну помилку рівня `Severity::Error` (виявлено 4-сторонній вузол, колізію двох вихідних драйверів, незахищений вхід або відсутність номіналу робочої напруги на силовому конденсаторі), процес повертає ненульовий код завершення `exit(1)`. Це автоматично блокує можливість злиття коду в головну гілку (main/master).
5. **Автоматичне коментування та анотації:** Бот конвеєра аналізує отриманий звіт і публікує детальні коментарі безпосередньо у відповідних рядках схемного коду в інтерфейсі code review, вказуючи координати дефектів на аркуші та надаючи чіткі інженерні рекомендації щодо виправлення.
6. **Звірення з базою сертифікованих компонентів (BOM Validation):** Лінтер порівнює витягнуті позиційні позначення та номінали з корпоративною базою Approved Vendor List (AVL), миттєво сигналізуючи про використання компонентів зі статусом EOL (End of Life) або відсутність партномера виробника (MPN).

Завдяки такій автоматизації розробник отримує миттєвий зворотний зв'язок ще під час роботи над кресленням, виключаючи потрапляння неохайних, помилкових або небезпечних схемних рішень на фабрику виробництва друкованих плат.
