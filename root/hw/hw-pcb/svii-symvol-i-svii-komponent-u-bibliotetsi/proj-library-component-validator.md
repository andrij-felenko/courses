# ⚙️ Валідатор цілісності бібліотек компонентів та перевірки пінів

Консольна утиліта автоматизованої верифікації бібліотечних компонентів дозволяє виявляти помилки розпіновки, незмаплені контактні площадки, дублювання виводів, відсутність обов'язкових атрибутів закупівлі та електричні конфлікти ще до початку розведення друкованої плати.

<preknowlist>
- [Свій символ і свій компонент у бібліотеці](root:hw-pcb/svii-symvol-i-svii-komponent-u-bibliotetsi) — концепція атомарних бібліотек, типи виводів та пастки Pin-to-Pad маппінгу.
- [Принципова схема](root:hw-pcb/schematic-purpose) — вузли, зв'язки та генерація списку з'єднань.
- [Перелік компонентів (BOM)](root:hw-pcb/bom) — структура та обов'язкові атрибути виробів.
</preknowlist>

---

## 1. Задача: автоматичний контроль бібліотек у конвеєрі розробки

У сучасній розробці електронних пристроїв діє фундаментальне економічне «правило десятикратного зростання вартості помилки» (*Rule of Ten*). Виявлення та виправлення дефекту компонента на етапі створення бібліотечного символу коштує умовно один долар робочого часу інженера. Якщо та сама помилка проходить непоміченою на етап принципової схеми, її виправлення коштує вже десять доларів. На етапі виготовлення голої друкованої плати на заводі ціна помилки зростає до ста доларів. Коли партія плат змонтована складальним автоматом і компоненти припаяні, вартість браку сягає тисячі доларів. А якщо дефект просочується в кінцевий прилад, поставлений замовнику або змонтований на промисловому об'єкті, ціна відкликання та ремонту перевищує десятки тисяч доларів.

Найчастіше причиною таких катастроф стає не складність алгоритмів чи нелінійність аналогових кіл, а банальні розбіжності в базі даних бібліотек: переплутані місцями анод і катод діода, випадково пропущений вивід землі в кульковому масиві BGA, дубльований номер піна в багатосекційній мікросхемі або порожній артикул виробника (MPN) у списку матеріалів BOM.

У розподілених інженерних командах бібліотеки налічують десятки тисяч компонентів і поповнюються щодня різними інженерами. Спроба верифікувати кожен новий компонент ручним переглядом даташитів і посадкових місць неминуче призводить до пропусків дефектів через втому та людський фактор. Єдиний надійний інженерний підхід — повна автоматизація валідації в конвеєрі безперервної інтеграції (CI/CD) та запуск строгих перевірок у вигляді локальних pre-commit хуків у системі контролю версій Git.

Головна мета розроблюваного валідатора — провести глибокий структурний, синтаксичний та топологічний аудит файлу компонента за чіткими формальними критеріями й заблокувати злиття гілки (*merge*), якщо компонент містить бодай одне критичне порушення.

---

## 2. Архітектура та математична модель верифікатора

Для побудови надійного аналізатора компонент розглядається як формальна реляційна модель, що зв'язує логічні символи схеми, фізичні площадки друкованої плати та атрибути виробничої бази даних.

Формально атомарний бібліотечний компонент задається як четвірка множин:

```
C = (S, F, M, A)
```

де:
- `S = {p₁, p₂, ..., pₙ}` — скінченна множина логічних виводів схемного символу (пінів);
- `F = {f₁, f₂, ..., fₘ}` — скінченна множина фізичних контактних площадок посадкового місця (падів);
- `M ⊆ S × F` — відношення зіставлення (маппінг) виводів символу на контактні площадки плати;
- `A = {(k₁, v₁), (k₂, v₂), ...}` — множина пар параметричних атрибутів закупівлі «ключ — значення».

### Формальні перевірочні правила та інваріанти

Валідатор послідовно обчислює шість фундаментальних предикатів цілісності:

1. **Інваріант унікальності логічних виводів символу:**
   ```
   ∀ pᵢ, pⱼ ∈ S : (i ≠ j) ∧ (pᵢ.unit = pⱼ.unit) ⇒ (pᵢ.num ≠ pⱼ.num)
   ```
   У межах однієї функційної секції (`Unit`) символу заборонено існування двох або більше виводів з однаковим номером ніжки. Якщо мікроконтролер має кілька виводів землі `GND`, вони мусять мати унікальні фізичні номери на корпусі (наприклад, `Pin 12`, `Pin 28`, `Pin 44`).

2. **Інваріант відповідності стандарту JEDEC JESD95-1 для BGA:**
   ```
   ∀ f ∈ F, ∀ c ∈ f.name : c ∉ {'I', 'O', 'Q', 'S', 'X', 'Z'}
   ```
   Матричні корпуси BGA та LGA не повинні містити у своїх буквено-цифрових позначеннях контактів літери, що мають візуальну схожість із цифрами 1, 0, 5, 2 або позначкою відсутності виводу.

3. **Інваріант строгої бієктивності зв'язку (Pin-to-Pad Bijection):**
   ```
   ∀ p ∈ S \ {p | p.type = PIN_NC} : ∃! f ∈ F : (p, f) ∈ M
   ```
   Кожен функційний вивід символу (крім виводів з типом `Not Connected`) мусить мати рівно одну відповідну контактну площадку на посадковому місці. Якщо пін оголошений на схемі, але не має адреси на платі, такий компонент неможливо розвести без втрати сигналу.

4. **Інваріант відсутності ізольованої робочої міді (No Orphan Pads):**
   ```
   ∀ f ∈ F \ {f | f.is_mechanical = true} : ∃ p ∈ S : (p, f) ∈ M
   ```
   Кожна контактна площадка на платі, призначена для електричного монтажу, мусить бути прив'язана до логічного виводу схеми. Наявність незмаплених площадок призводить до того, що доріжки не підключаються до важливих функційних виводів чи підкладок мікросхем.

5. **Інваріант повноти паспорта виробу (BOM Completeness):**
   ```
   (A["MPN"] ≠ ∅) ∧ (A["Manufacturer"] ≠ ∅) ∧ (A["Footprint"] ≠ ∅) ∧ (A["Datasheet"] ≠ ∅)
   ```
   Компонент не може бути доданий до виробничої бібліотеки, якщо в ньому відсутній точний номер деталі за каталогом виробника, назва бренду, посилання на офіційний технічний опис або назва сумісного посадкового місця.

6. **Інваріант узгодженості Active-Low позначень:**
   ```
   ∀ p ∈ S : (p.is_active_low = true) ⇒ (p.name[0] = '~' ∨ p.name[0] = 'n' ∨ p.name[end] = '#')
   ```
   Якщо прапорець виводу оголошує сигнал як активний за низьким рівнем, його текстова назва мусить містити стандартизований префікс або суфікс інверсії, щоб уникнути непорозумінь під час читання принципової схеми іншими інженерами.

---

## 3. Синтаксичний аналіз та побудова синтаксичного дерева (AST)

Сучасні бібліотеки систем проектування зберігаються у текстових форматах S-виразів (*S-expressions*). Валідатор будує синтаксичне дерево (AST, *Abstract Syntax Tree*), виконуючи рекурсивний спуск по структурі файлу.

Аналізатор реалізує три фази обробки:
1. **Лексичний аналіз (Tokenization):** вхідний потік символів розбивається на атоми (ідентифікатори), рядкові літерали в лапках, числові координати та керуючі дужки `(` і `)`. Під час лексичного аналізу відсікаються коментарі та нормалізуються пробільні символи.
2. **Побудова вузлів дерева:** кожен блок `(symbol ...)` чи `(footprint ...)` перетворюється на вузол дерева з параметрами та списком дочірніх елементів. Вузол зберігає координати розташування піна, його графічну довжину, орієнтацію (кут 0, 90, 180, 270 градусів), електричний тип виводу (`input`, `output`, `power_in`, `bidirectional`, `passive`) та текстові властивості.
3. **Семантична нормалізація:** значення координат із внутрішніх одиниць САПР (наприклад, нанометрів або децимілів) переводяться в міліметри з перевіркою вирівнювання за стандартною координатною сіткою (типово крок 2.54 мм або 1.27 мм для символів).

```
   Дерево S-виразів компонента в пам'яті валідатора:
   
   Root Node: (symbol "STM32F401RET6")
     ├── Properties:
     │     ├── "Reference" -> "U"
     │     ├── "Value" -> "STM32F401RET6"
     │     ├── "Footprint" -> "Package_QFP:LQFP-64_10x10mm_P0.5mm"
     │     └── "MPN" -> "STM32F401RET6"
     └── Sub-Units:
           ├── Unit A (Core, Clock, Reset):
           │     ├── Pin 1: "VBAT", Type: PowerIn
           │     └── Pin 7: "~{NRST}", Type: Input, Inverted: true
           └── Unit B (GPIO Banks):
                 ├── Pin 2: "PC13", Type: Bidirectional
                 └── Pin 3: "PC14", Type: Bidirectional
```

---

## 4. Верифікація топологічних параметрів посадкового місця (IPC-7351 Rules Engine)

Окрім перевірки зв'язків між символом і футпринтом, валідатор аналізує фізичні розміри та шари посадкового місця відповідно до стандарту IPC-7351B/C:

### Контроль зазорів паяльної маски (Solder Mask Expansion)

Контактні площадки повинні бути відкриті від паяльної маски на строго задану величину — зазор розширення маски (*Solder Mask Clearance / Expansion*). Стандартне значення становить **0.05 мм** на кожну сторону площадки. Якщо зазор нульовий або від'ємний, маска затікає на мідну площадку, зменшуючи корисну площу паяння та спричиняючи дефекти холодного паяння. Якщо зазор завеликий (понад 0.1 мм), місток маски між сусідніми ніжками мікросхеми з дрібним кроком (0.5 мм) стає тоншим за технологічний ліміт фабрики (0.075 мм) і руйнується під час виробництва, викликаючи перемички припою (*Solder Bridging*).

### Контроль розбиття термоплощадок паяльної пасти (Stencil Windowing)

Для мікросхем у корпусах QFN, DFN або PowerSOIC з великою металевою площадкою тепловідведення (Exposed Pad) валідатор обчислює коефіцієнт покриття паяльною пастою:

```
K_paste = (S_paste_total) / (S_copper_pad)
```

Правило валідації вимагає: **0.50 ≤ K_paste ≤ 0.70** (від 50% до 70% площі міді). Якщо площа пасти перевищує 70% або вікно не розбито на окремі сегменти, валідатор фіксує критичне попередження про небезпеку утворення газових порожнин і випливання компонента під час оплавлення.

### Контроль контуру обмеження (Courtyard Envelope)

Валідатор будує опуклу оболонку навколо всіх контактних площадок і шовкографії деталі та перевіряє шар `Courtyard`. Контур обмеження повинен виступати за межі крайніх точок деталі мінімум на **0.25 мм** (для рівня щільності B). Відсутність шару Courtyard або розриви в його полілінії роблять неможливою роботу системи автоматичної перевірки колізій на платі.

---

## 5. Графова модель перевірки електричних правил (ERC Graph Engine)

Для виявлення прихованих схемотехнічних колізій валідатор будує зважений двочастковий граф `G = (V_pins, V_nets, E)`, де вершини виводів `V_pins` з'єднуються з вершинами електричних кіл `V_nets`.

Алгоритм обходу графа перевіряє топологічні інваріанти:
1. **Пошук конфліктів виходів низького імпедансу:** кожне коло `v_net ∈ V_nets` сканується на кількість інцидентних вершин типу `PIN_TYPE_OUTPUT` та `PIN_TYPE_POWER_OUT`. Якщо в одному колі зустрічаються два або більше виходів із жорстким рівнем напруги, алгоритм реєструє критичну помилку короткого замикання (Short Circuit Contention).
2. **Пошук висячих входів (Floating Inputs):** якщо коло містить виводи типу `PIN_TYPE_INPUT`, але не містить жодного виводу типу `PIN_TYPE_OUTPUT`, `PIN_TYPE_POWER_OUT`, `PIN_TYPE_BIDIRECTIONAL` чи пасивного елемента підтяжки, генерується попередження про небезпеку наведення статичних перешкод на високоелементні затвори КМОН-транзисторів.
3. **Пошук відкритих стоків без навантаження:** кола з виводами `PIN_TYPE_OPEN_DRAIN` перевіряються на наявність зв'язку з шиною живлення через резистор. Якщо підтяжка відсутня, шина I2C або лінія скидання не зможе повернутися у високий стан після відпускання транзистора.

---

## 6. Контроль нульової орієнтації та упаковки у стрічку (EIA-481 vs IPC-7351)

Під час підготовки файлів для складального автомата (*Pick-and-Place machine*) критично важливою є початкова орієнтація деталі в посадковому місці (кут 0 градусів).

Існує класичний конфлікт між стандартами:
- **Стандарт IPC-7351:** нульовою орієнтацією для мікросхем вважається положення, коли вивід номер 1 знаходиться у верхньому лівому кутку (квадрант 2); для двовивідних компонентів — катод або позитивний вивід знаходиться ліворуч.
- **Стандарт пакування у стрічку EIA-481:** визначає орієнтацію деталі в блістерній стрічці відносно перфораційних отворів подавача (*feeder*).

Якщо посадкове місце створено з довільним поворотом на 90 або 180 градусів, оператор лінії змушений вручну підбирати кут корекції в програмі розстановки деталей. Якщо оператор забуде це зробити, вся партія змонтується розвернутою на 90 градусів. Валідатор аналізує координати площадки 1 відносно центру мас посадкового місця й перевіряє, чи відповідає нульовий поворот правилу IPC-7351/EIA-481.

---

## 7. Верифікація просторової моделі STEP та аналіз кліренсу

Бібліотечний компонент не є повним без тривимірної моделі у форматі STEP AP214 або AP242. Валідатор перевіряє:
1. **Збіг точки прив'язки (Origin Alignment):** геометричний центр 3D-тіла компонента мусить збігатися з центром посадкового місця (координата `(0, 0)` на платі). Якщо модель зміщена на кілька міліметрів, експорт плати в механічний САПР (SolidWorks, FreeCAD) покаже висячі в повітрі мікросхеми.
2. **Контроль висоти (Height Envelope):** параметр висоти деталі з атрибутів BOM порівнюється з максимальним габаритом за віссю Z імпортованої 3D-моделі. Це унеможливлює ситуацію, коли електролітичний конденсатор висотою 15 мм помилково встановлюється в низькопрофільний корпус приладу з обмеженням 10 мм.

---

## 8. Робоча реалізація: валідатор бібліотеки на C99 та C++20

Нижче наведено дві повноцінні, незалежні та самодостатні реалізації консольного валідатора компонентних бібліотек. Реалізація мовою C99 орієнтована на максимальну швидкодію, вбудовування у низькорівневі інструменти та відсутність динамічних залежностей. Реалізація мовою C++20 демонструє сучасний ідіоматичний підхід із застосуванням безпечних типів, `std::string_view`, контейнерів стандартної бібліотеки та механізмів обробки помилок.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

#define MAX_STR_LEN 128
#define MAX_ITEMS 512

typedef enum {
    PIN_TYPE_INPUT,
    PIN_TYPE_OUTPUT,
    PIN_TYPE_BIDIRECTIONAL,
    PIN_TYPE_TRISTATE,
    PIN_TYPE_PASSIVE,
    PIN_TYPE_POWER_IN,
    PIN_TYPE_POWER_OUT,
    PIN_TYPE_OPEN_DRAIN,
    PIN_TYPE_NOT_CONNECTED
} PinType;

const char* pin_type_to_string(PinType t) {
    switch (t) {
        case PIN_TYPE_INPUT:         return "Input";
        case PIN_TYPE_OUTPUT:        return "Output";
        case PIN_TYPE_BIDIRECTIONAL: return "Bidirectional";
        case PIN_TYPE_TRISTATE:      return "Tri-state";
        case PIN_TYPE_PASSIVE:       return "Passive";
        case PIN_TYPE_POWER_IN:      return "Power In";
        case PIN_TYPE_POWER_OUT:     return "Power Out";
        case PIN_TYPE_OPEN_DRAIN:    return "Open Drain";
        case PIN_TYPE_NOT_CONNECTED: return "Not Connected";
        default:                     return "Unknown";
    }
}

typedef struct {
    char number[32];
    char name[MAX_STR_LEN];
    char unit[8];
    PinType type;
    bool is_active_low;
} SymbolPin;

typedef struct {
    char number[32];
    char name[MAX_STR_LEN];
    bool is_mechanical;
} FootprintPad;

typedef struct {
    char symbol_pin_num[32];
    char footprint_pad_num[32];
} PinMapping;

typedef struct {
    char mpn[MAX_STR_LEN];
    char manufacturer[MAX_STR_LEN];
    char footprint_ref[MAX_STR_LEN];
    char datasheet_url[MAX_STR_LEN];
    
    SymbolPin pins[MAX_ITEMS];
    size_t pin_count;
    
    FootprintPad pads[MAX_ITEMS];
    size_t pad_count;
    
    PinMapping mappings[MAX_ITEMS];
    size_t mapping_count;
} ComponentDefinition;

// Перевірка буквено-цифрових позначень BGA за стандартом JEDEC
bool check_jedec_bga_rules(const char* pad_num, char* err_buf, size_t buf_len) {
    const char* forbidden = "IOQSXZ";
    for (size_t i = 0; i < strlen(pad_num); ++i) {
        char c = (char)toupper((unsigned char)pad_num[i]);
        if (strchr(forbidden, c) != NULL && isalpha((unsigned char)c)) {
            snprintf(err_buf, buf_len,
                     "Площадка BGA '%s' містить неприпустиму стандартом JEDEC літеру '%c'",
                     pad_num, c);
            return false;
        }
    }
    return true;
}

// Повний аудит бібліотечного компонента
int run_component_audit(const ComponentDefinition* comp) {
    int error_count = 0;
    int warning_count = 0;
    char error_buffer[256];

    printf("=====================================================\n");
    printf("АУДИТ КОМПОНЕНТА: %s (%s)\n", comp->mpn, comp->manufacturer);
    printf("Посадкове місце: %s\n", comp->footprint_ref);
    printf("=====================================================\n");

    // 1. Аудит атрибутів закупівлі BOM
    if (strlen(comp->mpn) == 0) {
        printf("[ПОМИЛКА] Відсутній номер деталі виробника (MPN)!\n");
        error_count++;
    }
    if (strlen(comp->manufacturer) == 0) {
        printf("[ПОМИЛКА] Відсутня назва фірми-виробника!\n");
        error_count++;
    }
    if (strlen(comp->footprint_ref) == 0) {
        printf("[ПОМИЛКА] Відсутня прив'язка посадкового місця!\n");
        error_count++;
    }
    if (strlen(comp->datasheet_url) == 0 || strncmp(comp->datasheet_url, "http", 4) != 0) {
        printf("[ПОПЕРЕДЖЕННЯ] Посилання на Datasheet порожнє або не є HTTP URL!\n");
        warning_count++;
    }

    // 2. Аудит виводів символу
    if (comp->pin_count == 0) {
        printf("[ПОМИЛКА] Символ не містить жодного виводу!\n");
        error_count++;
    }

    for (size_t i = 0; i < comp->pin_count; ++i) {
        const SymbolPin* p1 = &comp->pins[i];
        
        // Перевірка дублювання виводів у секції
        for (size_t j = i + 1; j < comp->pin_count; ++j) {
            const SymbolPin* p2 = &comp->pins[j];
            if (strcmp(p1->number, p2->number) == 0 && strcmp(p1->unit, p2->unit) == 0) {
                printf("[ПОМИЛКА] Дублювання виводу '%s' у секції Unit %s!\n",
                       p1->number, p1->unit);
                error_count++;
            }
        }

        // Перевірка синтаксису інверсії сигналів
        if (p1->is_active_low) {
            bool has_prefix = (p1->name[0] == '~' || p1->name[0] == 'n' || p1->name[0] == '/');
            bool has_suffix = (p1->name[strlen(p1->name) - 1] == '#' || 
                               (strlen(p1->name) >= 2 && strcmp(&p1->name[strlen(p1->name) - 2], "_N") == 0));
            if (!has_prefix && !has_suffix) {
                printf("[ПОПЕРЕДЖЕННЯ] Пін %s (%s) позначений як Active-Low, але не має позначки інверсії (~, n, #)!\n",
                       p1->number, p1->name);
                warning_count++;
            }
        }
    }

    // 3. Аудит площадок посадкового місця
    if (comp->pad_count == 0) {
        printf("[ПОМИЛКА] Посадкове місце не містить контактних площадок!\n");
        error_count++;
    }

    for (size_t i = 0; i < comp->pad_count; ++i) {
        const FootprintPad* pad1 = &comp->pads[i];
        
        // JEDEC BGA перевірка
        if (!check_jedec_bga_rules(pad1->number, error_buffer, sizeof(error_buffer))) {
            printf("[ПОМИЛКА] %s\n", error_buffer);
            error_count++;
        }

        // Перевірка дублювання номерів площадок
        for (size_t j = i + 1; j < comp->pad_count; ++j) {
            const FootprintPad* pad2 = &comp->pads[j];
            if (strcmp(pad1->number, pad2->number) == 0) {
                printf("[ПОМИЛКА] Посадкове місце містить дубльовану площадку номер '%s'!\n",
                       pad1->number);
                error_count++;
            }
        }
    }

    // 4. Аудит бієкції Pin-to-Pad
    bool pad_is_connected[MAX_ITEMS] = {false};

    for (size_t i = 0; i < comp->pin_count; ++i) {
        const SymbolPin* pin = &comp->pins[i];
        if (pin->type == PIN_TYPE_NOT_CONNECTED) {
            continue; // NC виводи не потребують прив'язки
        }

        bool mapping_found = false;
        for (size_t m = 0; m < comp->mapping_count; ++m) {
            if (strcmp(comp->mappings[m].symbol_pin_num, pin->number) == 0) {
                const char* target_pad = comp->mappings[m].footprint_pad_num;
                
                // Перевірка існування фізичної площадки
                bool pad_exists = false;
                for (size_t p = 0; p < comp->pad_count; ++p) {
                    if (strcmp(comp->pads[p].number, target_pad) == 0) {
                        pad_exists = true;
                        pad_is_connected[p] = true;
                        break;
                    }
                }

                if (!pad_exists) {
                    printf("[ПОМИЛКА] Пін символу %s (%s) прив'язаний до неіснуючої площадки '%s'!\n",
                           pin->number, pin->name, target_pad);
                    error_count++;
                }
                mapping_found = true;
                break;
            }
        }

        if (!mapping_found) {
            printf("[ПОМИЛКА] Пін %s (%s, тип: %s) не має маппінгу на жодну контактну площадку!\n",
                   pin->number, pin->name, pin_type_to_string(pin->type));
            error_count++;
        }
    }

    // 5. Пошук незмаплених ізольованих площадок
    for (size_t p = 0; p < comp->pad_count; ++p) {
        if (!pad_is_connected[p] && !comp->pads[p].is_mechanical) {
            printf("[ПОПЕРЕДЖЕННЯ] Контактна площадка '%s' (%s) не зв'язана зі схемою (ізольований метал)!\n",
                   comp->pads[p].number, comp->pads[p].name);
            warning_count++;
        }
    }

    printf("\nРЕЗУЛЬТАТ ВАЛІДАЦІЇ: Помилок: %d, Попереджень: %d\n", error_count, warning_count);
    if (error_count == 0) {
        printf("[СХВАЛЕНО] Компонент успішно пройшов усі тести якості.\n");
    } else {
        printf("[ЗАБЛОКОВАНО] Компонент містить критичні помилки. Імпорт відхилено.\n");
    }
    printf("=====================================================\n\n");

    return error_count;
}

int main(void) {
    ComponentDefinition comp;
    memset(&comp, 0, sizeof(comp));

    strncpy(comp.mpn, "STM32F401RET6", sizeof(comp.mpn) - 1);
    strncpy(comp.manufacturer, "STMicroelectronics", sizeof(comp.manufacturer) - 1);
    strncpy(comp.footprint_ref, "Package_QFP:LQFP-64_10x10mm_P0.5mm", sizeof(comp.footprint_ref) - 1);
    strncpy(comp.datasheet_url, "https://www.st.com/resource/en/datasheet/stm32f401re.pdf", sizeof(comp.datasheet_url) - 1);

    // Додавання пінів символу
    comp.pin_count = 3;
    strcpy(comp.pins[0].number, "1"); strcpy(comp.pins[0].name, "VBAT"); comp.pins[0].type = PIN_TYPE_POWER_IN; strcpy(comp.pins[0].unit, "A"); comp.pins[0].is_active_low = false;
    strcpy(comp.pins[1].number, "2"); strcpy(comp.pins[1].name, "PC13"); comp.pins[1].type = PIN_TYPE_BIDIRECTIONAL; strcpy(comp.pins[1].unit, "A"); comp.pins[1].is_active_low = false;
    strcpy(comp.pins[2].number, "7"); strcpy(comp.pins[2].name, "~{NRST}"); comp.pins[2].type = PIN_TYPE_INPUT; strcpy(comp.pins[2].unit, "A"); comp.pins[2].is_active_low = true;

    // Додавання площадок посадкового місця
    comp.pad_count = 3;
    strcpy(comp.pads[0].number, "1"); strcpy(comp.pads[0].name, "Pad_1"); comp.pads[0].is_mechanical = false;
    strcpy(comp.pads[1].number, "2"); strcpy(comp.pads[1].name, "Pad_2"); comp.pads[1].is_mechanical = false;
    strcpy(comp.pads[2].number, "7"); strcpy(comp.pads[2].name, "Pad_7"); comp.pads[2].is_mechanical = false;

    // Створення маппінгу
    comp.mapping_count = 3;
    strcpy(comp.mappings[0].symbol_pin_num, "1"); strcpy(comp.mappings[0].footprint_pad_num, "1");
    strcpy(comp.mappings[1].symbol_pin_num, "2"); strcpy(comp.mappings[1].footprint_pad_num, "2");
    strcpy(comp.mappings[2].symbol_pin_num, "7"); strcpy(comp.mappings[2].footprint_pad_num, "7");

    return run_component_audit(&comp) == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <cctype>

enum class PinType {
    Input,
    Output,
    Bidirectional,
    TriState,
    Passive,
    PowerIn,
    PowerOut,
    OpenDrain,
    NotConnected
};

std::string_view to_string(PinType t) noexcept {
    switch (t) {
        case PinType::Input:         return "Input";
        case PinType::Output:        return "Output";
        case PinType::Bidirectional: return "Bidirectional";
        case PinType::TriState:      return "Tri-state";
        case PinType::Passive:       return "Passive";
        case PinType::PowerIn:       return "Power In";
        case PinType::PowerOut:      return "Power Out";
        case PinType::OpenDrain:     return "Open Drain";
        case PinType::NotConnected:  return "Not Connected";
    }
    return "Unknown";
}

struct SymbolPin {
    std::string number;
    std::string name;
    std::string unit{"A"};
    PinType type{PinType::Passive};
    bool is_active_low{false};
};

struct FootprintPad {
    std::string number;
    std::string name;
    bool is_mechanical{false};
};

struct AuditReport {
    std::vector<std::string> errors;
    std::vector<std::string> warnings;

    [[nodiscard]] bool passed() const noexcept {
        return errors.empty();
    }
};

class ComponentValidator {
public:
    std::string mpn;
    std::string manufacturer;
    std::string footprint_ref;
    std::string datasheet_url;

    std::vector<SymbolPin> pins;
    std::vector<FootprintPad> pads;
    std::unordered_map<std::string, std::string> pin_to_pad_map;

    [[nodiscard]] AuditReport execute_audit() const {
        AuditReport report;

        // 1. Аудит атрибутів BOM
        if (mpn.empty()) {
            report.errors.push_back("Порожній номер деталі виробника (MPN)!");
        }
        if (manufacturer.empty()) {
            report.errors.push_back("Відсутня назва компанії-виробника!");
        }
        if (footprint_ref.empty()) {
            report.errors.push_back("Не задано посилання на посадкове місце (Footprint)!");
        }
        if (datasheet_url.empty() || !datasheet_url.starts_with("http")) {
            report.warnings.push_back("Посилання на Datasheet відсутнє або не є коректним HTTP URL.");
        }

        // 2. Аудит пінів символу
        if (pins.empty()) {
            report.errors.push_back("Символ компонента не містить жодного виводу.");
        }

        std::unordered_set<std::string> scoped_pins;
        for (const auto& pin : pins) {
            std::string scope_key = pin.unit + ":" + pin.number;
            if (!scoped_pins.insert(scope_key).second) {
                report.errors.push_back("Дублювання номера виводу '" + pin.number + 
                                       "' у функційній секції Unit " + pin.unit);
            }

            if (pin.is_active_low) {
                bool has_prefix = pin.name.starts_with('~') || pin.name.starts_with('n') || pin.name.starts_with('/');
                bool has_suffix = pin.name.ends_with('#') || pin.name.ends_with("_N");
                if (!has_prefix && !has_suffix) {
                    report.warnings.push_back("Пін " + pin.number + " (" + pin.name + 
                                             ") позначений Active-Low без стандартного індикатора інверсії.");
                }
            }
        }

        // 3. Аудит площадок посадкового місця та правил JEDEC
        if (pads.empty()) {
            report.errors.push_back("Посадкове місце не містить контактних площадок.");
        }

        const std::string_view forbidden_bga = "IOQSXZ";
        std::unordered_set<std::string> unique_pads;

        for (const auto& pad : pads) {
            if (!unique_pads.insert(pad.number).second) {
                report.errors.push_back("Посадкове місце містить дубльовану площадку '" + pad.number + "'!");
            }

            for (char ch : pad.number) {
                char upper_ch = static_cast<char>(std::toupper(static_cast<unsigned char>(ch)));
                if (std::isalpha(static_cast<unsigned char>(ch)) && forbidden_bga.find(upper_ch) != std::string_view::npos) {
                    report.errors.push_back("Площадка BGA '" + pad.number + 
                                           "' містить заборонену стандартом JEDEC літеру '" + 
                                           std::string(1, upper_ch) + "'");
                }
            }
        }

        // 4. Аудит бієкції Pin-to-Pad
        std::unordered_set<std::string> mapped_pads;

        for (const auto& pin : pins) {
            if (pin.type == PinType::NotConnected) {
                continue;
            }

            auto it = pin_to_pad_map.find(pin.number);
            if (it == pin_to_pad_map.end()) {
                report.errors.push_back("Пін " + pin.number + " (" + pin.name + ", тип " + 
                                       std::string(to_string(pin.type)) + ") не має прив'язки до площадки.");
            } else {
                const std::string& target_pad = it->second;
                auto pad_it = std::find_if(pads.begin(), pads.end(), [&](const FootprintPad& p) {
                    return p.number == target_pad;
                });

                if (pad_it == pads.end()) {
                    report.errors.push_back("Пін " + pin.number + " змаплений на неіснуючу контактну площадку '" + 
                                           target_pad + "'!");
                } else {
                    mapped_pads.insert(target_pad);
                }
            }
        }

        // 5. Пошук незмапленої міді
        for (const auto& pad : pads) {
            if (!pad.is_mechanical && !mapped_pads.contains(pad.number)) {
                report.warnings.push_back("Контактна площадка '" + pad.number + 
                                         "' (" + pad.name + ") на платі не зв'язана з жодним піном схеми.");
            }
        }

        return report;
    }
};

int main() {
    ComponentValidator mcu;
    mcu.mpn = "STM32F401RET6";
    mcu.manufacturer = "STMicroelectronics";
    mcu.footprint_ref = "Package_QFP:LQFP-64_10x10mm_P0.5mm";
    mcu.datasheet_url = "https://www.st.com/resource/en/datasheet/stm32f401re.pdf";

    mcu.pins = {
        {"1", "VBAT", "A", PinType::PowerIn, false},
        {"2", "PC13", "A", PinType::Bidirectional, false},
        {"7", "~{NRST}", "A", PinType::Input, true}
    };

    mcu.pads = {
        {"1", "Pad_1", false},
        {"2", "Pad_2", false},
        {"7", "Pad_7", false}
    };

    mcu.pin_to_pad_map = {
        {"1", "1"},
        {"2", "2"},
        {"7", "7"}
    };

    auto report = mcu.execute_audit();

    std::cout << "=====================================================\n";
    std::cout << "РЕЗУЛЬТАТ АУДИТУ КОМПОНЕНТА: " << mcu.mpn << "\n";
    std::cout << "=====================================================\n";

    for (const auto& err : report.errors) {
        std::cout << "[ПОМИЛКА] " << err << "\n";
    }
    for (const auto& warn : report.warnings) {
        std::cout << "[ПОПЕРЕДЖЕННЯ] " << warn << "\n";
    }

    if (report.passed()) {
        std::cout << "[СХВАЛЕНО] Усі перевірки пройдено успішно.\n";
        return 0;
    }

    std::cout << "[ВІДХИЛЕНО] Знайдено дефекти! Імпорт у бібліотеку заборонено.\n";
    return 1;
}
```
:::

---

## 9. Складні інженерні випадки та пастки реалізації

Під час проектування промислового валідатора розробник стикається з низкою граничних випадків, де проста перевірка «один-до-одного» вимагає розширення логіки:

### 1. Спільні виводи живлення у багатосекційних символах (Shared Power Pins)

У логічних мікросхемах із чотирма вентилями (наприклад, `74HC00` у корпусі `SOIC-14`) виводи живлення `VCC` (Pin 14) та `GND` (Pin 7) фізично існують в одному екземплярі на кристалі. Якщо схема розбита на секції `Unit A`, `Unit B`, `Unit C`, `Unit D` та службову секцію живлення `Unit Power`, валідатор мусить коректно обробляти ситуацію, коли піни живлення оголошені лише в одній секції, але мапляться на спільний корпус, не генеруючи хибних попереджень про непідключені виводи в секціях A–D.

### 2. Відображення багатьох виводів на одну термоплощадку (Many-to-One Thermal Pad Mapping)

У потужних імпульсних стабілізаторах, драйверах крокових двигунів і радіочастотних трансиверах центральна термоплощадка `EPAD` (Exposed Pad) на платі часто має номер площадки `33` чи `EP`. При цьому на схемі мікросхема може мати чотири окремі виводи тепловідведення та силової землі (`GND_TAB_1`, `GND_TAB_2`, `GND_TAB_3`, `GND_TAB_4`). У такому разі алгоритм валідації повинен підтримувати зіставлення декількох логічних пінів з однією фізичною площадкою, за умови що всі ці піни мають однаковий електричний тип (`Power In` або `Passive`) і належать до одного еквіпотенціального вузла.

### 3. Буквено-цифрові ідентифікатори площадок проти цілочисельних індексів

У роз'ємах живлення, USB-C портах та автомобільних колодках контакти мають змішані назви: `A1`, `B12`, `SHIELD1`, `SHIELD2`, `EPAD`, `G1`, `G2`. Валідатор не повинен конвертувати номери виводів у цілі числа (`int`), оскільки це призводить до втрати провідних нулів (перетворення `01` на `1`), колізій між літерами та числами або збоїв адресації масивів. Усі ідентифікатори виводів мусять зберігатися та порівнюватися виключно як текстові рядки.

### 4. Чотирипровідне підключення Кельвіна (Kelvin Current Sense Footprints)

Для прецизійних низькоомних шунтів вимірювання струму (номінал 1 мОм – 10 мОм) застосовують 4-вивідні корпуси. Дві площадки призначені для проходження силового струму (`Force_1`, `Force_2`), а дві окремі тонкі площадки — для зняття падіння напруги підсилювачем (`Sense_1`, `Sense_2`). Якщо валідатор не враховує таку специфіку й об'єднує площадки в один пін, вимірювальний тракт вимірює паразитний опір припою замість струму навантаження.

---

## 10. Інтеграція валідатора в конвеєр розробки (CI/CD та Pre-commit Hooks)

Для забезпечення автоматичного контролю утиліту валідатора інтегрують у робочий процес команди:

1. **Локальний Git Pre-commit Hook:** перед кожним створенням коміту в репозиторій бібліотеки скрипт автоматично перевіряє змінені файли `.kicad_sym` та `.kicad_mod`. Якщо валідатор повертає код помилки, коміт блокується:
   ```bash
   #!/usr/bin/env bash
   # .git/hooks/pre-commit
   echo "[CI] Перевірка цілісності бібліотек компонентів..."
   ./bin/component_validator --check-staged
   if [ $? -ne 0 ]; then
       echo "[CI ПОМИЛКА] Виявлено дефекти в бібліотеці компонентів. Коміт скасовано!"
       exit 1
   fi
   ```
2. **Серверний конвеєр CI/CD (GitHub Actions / GitLab CI):** під час створення запиту на злиття (*Pull Request*) серверний агент збирає валідатор, проганяє повний аудит усіх компонентів і публікує детальний звіт із зазначенням проблемних позицій у форматі JUnit XML або SARIF прямо в інтерфейсі коментарів до коду.

---

> 🔧 **Підсумок.** Автоматизований валідатор перетворює суб'єктивну перевірку компонентів на детермінований цифровий шлюз якості. Впровадження суворої машинної перевірки Pin-to-Pad маппінгу, правил JEDEC та атрибутів BOM унеможливлює потрапляння бракованих посадкових місць на виробництво.
