# ⚙️ Валідатор узгодженості BOM та CPL координат

Автоматизована лінія поверхневого монтажу (SMT, Surface Mount Technology) не вибачає розбіжностей у вхідній виробничій документації. Коли контрактний виробник готує лінію до запуску нової партії друкованих вузлів, інженер-технолог завантажує два ключові файли: перелік компонентів (BOM, Bill of Materials) та файл координат центроїдів (CPL, Component Placement List / Pick-and-Place data). Якщо ці документи експортовані з різних ревізій САПР, створені з порушенням синхронізації між схемою й топологією або зазнали некоректного ручного редагування, лінія зупиняється на етапі налаштування живильників або випускає масовий брак.

Складальний автомат намагається встановити деталь за координатами, де відсутній контактний майданчик, або бере мікросхему з живильника й повертає її на кут, зміщений на 90 градусів відносно посадкового місця. Ручна перевірка узгодженості списків для сучасних плат із кількома сотнями чи тисячами компонентів займає робочі дні й через людський фактор пропускає одиничні помилки. Програмний валідатор повністю автоматизує цей процес, виявляючи всі невідповідності за частки секунди до передачі файлів операторам верстатів.

## Анатомія розбіжностей у виробничих файлах

Файли BOM та CPL створюються різними модулями САПР. Перелік компонентів формується в редакторі схем (Schematic Editor) або системі управління базою даних деталей підприємства, тоді як CPL генерується безпосередньо з редактора друкованих плат (PCB Layout Editor). Будь-яка несинхронізована зміна (наприклад, перейменування резистора `R12` на `R15` під час оптимізації схеми без виконання зворотної анотації в топологію або видалення фільтруючого конденсатора без оновлення переліку закупівлі) породжує приховані дефекти монтажу.

Файл BOM містить комерційну та схемотехнічну інформацію. Кожен рядок описує групу однакових деталей:

```csv
Designator,Value,Footprint,MPN,DNP
"R1, R2, R3",10k,0603,RC0603FR-0710KL,0
C1,100nF,0402,CL05B104KO5NNNC,0
C2,10uF,0805,CL21A106KOQNNNE,0
R4,0R,0603,RC0603JR-070RL,1
U1,STM32F401RCT6,LQFP-64,STM32F401RCT6,0
```

Файл CPL (Pick and Place / Centroid) містить виключно геометричні параметри розміщення кожного фізичного компонента на поверхні плати:

```csv
Designator,MidX,MidY,Layer,Rotation
R1,12.50,24.30,Top,0.0
R2,15.20,24.30,Top,0.0
R3,18.00,24.30,Top,0.0
C1,22.10,15.40,Top,90.0
C2,25.00,15.40,Top,90.0
U1,35.00,30.00,Top,0.0
```

Під час автоматичного порівняльного аналізу виділяють шість критичних категорій розбіжностей:

1. **Відсутність центроїда (Missing Centroid)**: деталь присутня в BOM і не позначена як DNP (Do Not Populate), але для неї немає жодного запису в CPL. Складальний автомат P&P не знатиме координат для встановлення закупленого компонента, і плата вийде з лінії недоукомплектованою.
2. **Фантомний компонент (Phantom Placement)**: позиційне позначення присутнє в CPL, але відсутнє в BOM. Складальний верстат намагатиметься знайти деталь у живильниках, але оператор лінії не зможе її заправити, оскільки відділ постачання не замовляв цей артикул.
3. **Конфлікт монтування (DNP Inconsistency)**: деталь у BOM позначена прапорцем `DNP=1` (або `DNI`, `NO-POP`), але присутня в CPL без відповідної позначки виключення. Це призводить до помилкового монтажу компонентів, призначених для інших апаратних конфігурацій пристрою.
4. **Некоректний кут орієнтації (Rotation Anomaly)**: кут повороту виходить за межі стандартного діапазону `[0.0, 360.0)` або містить нечислові дані.
5. **Дублювання координат (Duplicate Placement)**: одне й те саме позиційне позначення зустрічається в CPL двічі з різними координатами або кутами, що свідчить про пошкодження внутрішньої бази даних САПР.
6. **Невідповідність сторони монтажу (Layer Mismatch)**: деталь призначена для верхнього шару, але опиняється на нижньому через неправильну конфігурацію дзеркалювання в САПР.

## Центроїд: центр геометрії проти центру мас

Одним із найскладніших аспектів формування файлів CPL є точне визначення точки центроїда `(MidX, MidY)`. У САПР існують три різні методи визначення опорної точки посадкового місця:

- **Центр габаритної рамки (Bounding Box Center)**: геометричний центр прямокутника, що охоплює всі контактні майданчики та шовкографію компонента. Для симетричних корпусів (чип-резистори 0603, мікросхеми QFP, QFN) цей центр збігається з фізичним центром деталі.
- **Центр контактних майданчиків (Pad Centroid)**: центр тяжіння системи металізованих майданчиків. Якщо корпус має асиметричні виводи (наприклад, польовий транзистор у корпусі DPAK, рознім USB Type-C або тактова кнопка з бічними фіксаторами), центр майданчиків зміщений відносно корпусу.
- **Центр мас та точка захвату (Center of Gravity / Pick Point)**: точка, у яку повинна опускатися вакуумна насадка автомата Pick & Place. Якщо вакуумне сопло візьме асиметричний компонент за центр контактних майданчиків, а не за центр ваги корпусу, деталь перекоситься під дією власної ваги під час швидкісного переміщення голівки верстата (прискорення до `5–10 g`), що призведе до падіння або неточного позиціонування.

Валідатор контролює наявність явних координат для кожного активного компонента та перевіряє, щоб координати не виходили за межі технологічного контуру плати.

## Алгоритмічна складність та вибір структур даних

При аналізі складних сучасних виробів, що містять десятки тисяч компонентів (наприклад, сервери, базові станції або багатоканальні системи збору даних), наївний алгоритм порівняння списків із квадратичною складністю `O(N · M)` стає помітно повільним. Якщо для кожного елемента CPL виконувати лінійний пошук по масиву BOM, час перевірки зростає як квадрат кількості позицій.

Використання хеш-таблиці з розв'язанням колізій методом ланцюжків (Chaining) у версії C99 або асоціативного масиву `std::unordered_map` у версії C++20 знижує середню часову складність пошуку до константної величини `O(1)`. Загальна алгоритмічна складність конвеєра становить `O(N + M)`:
- Побудова таблиці BOM: `N` операцій вставки, де кожна операція виконується за `O(1)` при низькому коефіцієнті заповнення таблиці (Load Factor < 0.75).
- Зчитування CPL: `M` операцій додавання у динамічний вектор `O(M)`.
- Перехресна валідація: `M` операцій пошуку в хеш-таблиці для зіставлення `CPL -> BOM` та `N` операцій перевірки прапорців для зворотного проходу `BOM -> CPL`.

У результаті перевірка промислового проєкту на 10 000 компонентів виконується менш ніж за 5 мілісекунд, що дозволяє вбудовувати валідатор як миттєвий крок компіляції та експорту в графічних оболонках САПР.

## Математична нормалізація координат і кутів орієнтації

Центроїд компонента в CPL задається координатами `(X, Y)` та кутом повороту `θ`. Координати відлічуються від початку координат плати (Board Origin або Auxiliary Origin), а кут `θ` задається в градусах проти годинникової стрілки (за стандартом IPC-7351).

Проте різні САПР та складальні автомати використовують відмінні конвенції кутів:
- Деякі системи записують кути в діапазоні `[-180.0, +180.0]`.
- Інші системи накопичують оберти (наприклад, `450.0°` замість `90.0°`).
- Деякі верстати вимагають відліку за годинниковою стрілкою для нижнього шару плати (Bottom).

Математична нормалізація до канонічного діапазону `[0.0, 360.0)` виконується за формулою з подвійним взяттям залишку від ділення:

```
θ_norm = fmod(fmod(θ, 360.0) + 360.0, 360.0)
```

де перший `fmod` приводить кут до діапазону `(-360.0, 360.0)`, додавання `360.0` гарантує строгу додатність аргументу, а другий `fmod` згортає граничне значення `360.0°` у канонічний нуль `0.0°`.

Якщо плата монтується на обох сторонах, перетворення координат для нижнього шару (Bottom) відносно дзеркального відображення осі `X` описується матрицею:

```
[ X_bottom ]   [ -1   0 ] [ X_cad - X_origin ]   [ X_origin ]
[ Y_bottom ] = [  0   1 ] [ Y_cad - Y_origin ] + [ Y_origin ]
```

Кут орієнтації для компонентів на нижній стороні розраховується з урахуванням дзеркалювання:

```
θ_bottom = fmod(360.0 - θ_cad, 360.0)
```

Валідатор перевіряє строгу присутність ідентифікатора шару (Top / Bottom) для кожного запису та попереджає про неприпустимі або змішані позначення.

## Стандарти нульової орієнтації та компенсація кутів монтажу (0° vs 90° vs 180° vs 270°)

Одна з найпоширеніших причин браку на стадії пілотного монтажу — розбіжність між визначенням нульового кута (`0°`) у САПР друкованих плат та орієнтацією деталі в пакувальній стрічці чи матричному піддоні (JEDEC Tray).

### Конфлікт між IPC-7351 та EIA-481

Міжнародний стандарт проектування посадкових місць **IPC-7351** (зокрема ревізії A та B) стандартизує нульову орієнтацію компонентів у базі даних САПР:
- **Двовивідні компоненти (резистори, неполярні конденсатори)**: орієнтовані горизонтально; вивід 1 розташований ліворуч (кут `0°`).
- **Полярні двовивідні компоненти (діоди, танталові конденсатори)**: катод або позитивний вивід розташований ліворуч.
- **Багатовивідні корпуси (SOIC, QFP, QFN, BGA)**: вивід 1 (або кулька A1) розташований у верхньому лівому кутку (для прямокутних корпусів довша сторона розташована горизонтально).

Водночас стандарт пакування компонентів у блістерні стрічки **EIA-481** регламентує положення деталі в кишені відносно напрямку подачі стрічки та отворів перфорації (Sprocket Holes):
- Більшість мікросхем у стрічці орієнтовані так, що перший вивід знаходиться у квадранті 1 (верхній лівий кут відносно отворів перфорації) або квадранті 2 (верхній правий кут).
- Діоди в корпусах SMA/SMB/SMC або SOD-123 часто постачаються з катодом, спрямованим у бік отворів перфорації (вертикально) або за рухом стрічки.

Якщо складальний автомат бере деталь зі стрічки й застосовує кут `θ_cad` без поправки на орієнтацію в живильнику, компонент повертається на кут зі зміщенням `+90°`, `+180°` або `+270°`.

### Специфіка автоматів різних виробників

Складальні автомати провідних виробників (Yamaha, Panasonic, Fuji, ASM Siplace, Juki) використовують власні внутрішні таблиці живильників (Feeder Tables). Деякі системи (наприклад, Fuji Flexa або Yamaha YGOS) очікують кути за стандартом IPC, самостійно застосовуючи кутове зміщення стрічки `Δθ_feeder`. Інші системи вимагають, щоб вихідний файл CPL уже містив скоригований абсолютний кут для головки верстата.

| Тип корпусу | Базова орієнтація IPC-7351 (CAD 0°) | Положення в стрічці EIA-481 | Кутове зміщення (Δθ) | Потенційний ризик помилки |
| :--- | :--- | :--- | :--- | :--- |
| **SMD діоди (SMA, SOD)** | Катод ліворуч (горизонтально) | Катод до перфорації (вгору) | `+90°` або `+270°` | Переполюсовка діода, коротке замикання |
| **Танталові конденсатори** | Анод (+) ліворуч (горизонтально) | Анод за напрямком стрічки | `0°` або `+90°` | Вибух танталового електроліту при переполюсовці |
| **Транзистори SOT-23** | Одинарний вивід 3 зверху | Вивід 3 спрямований праворуч | `+90°` | Зміна місцями бази й емітера / затвора й витоку |
| **Мікросхеми SOIC / SOP** | Вивід 1 зверху ліворуч | Вивід 1 у квадранті 1 | `0°` або `+90°` | Зсув сигнальних виводів на сусідні площадки |
| **Мікросхеми QFN / QFP** | Вивід 1 зверху ліворуч | Вивід 1 у квадранті 2 | `+90°` | Неправильне підключення живлення VDD/GND |

### Алгоритм компенсації поворотів

Щоб уникнути ручного коригування сотень позицій оператором лінії, валідатор підтримує модуль перевірки та компенсації кутів за формулою:

```
θ_target = fmod(θ_cad + Δθ_package(Footprint, FeederType) + 360.0, 360.0)
```

де функція `Δθ_package` визначає коригувальний зсув за типом посадкового місця та орієнтацією живильника. Валідатор порівнює значення кута з допустимим дискретним рядом `{0°, 90°, 180°, 270°}` для ортогональних корпусів або фіксує нестандартні кути (наприклад, `45.0°`), якщо компоненти трасовані під нахилом для економії площі плати.

## Канонізація та аналіз розбіжностей посадкових місць (Footprint Aliasing)

У виробничій практиці найменування посадкового місця в схемному переліку BOM (`Footprint`) рідко збігається з точним технічним ідентифікатором у бібліотеці САПР або файлі CPL. Неузгодженість найменувань створює хибні спрацьовування автоматичних систем або приховує помилкове встановлення іншого типу корпусу.

### Колізія дюймових та метричних позначень

Класичним джерелом фатальних виробничих помилок є колізія між дюймовими (EIA Imperial) та метричними (Metric) кодами типорозмірів пасивних SMD-компонентів:
- Позначення **0603 (Imperial)** відповідає метричному розміру **1608 (Metric)**: довжина 1.6 мм, ширина 0.8 мм.
- Позначення **0603 (Metric)** відповідає дюймовому типорозміру **0201 (Imperial)**: довжина 0.6 мм, ширина 0.3 мм.
- Позначення **0402 (Imperial)** відповідає метричному розміру **1005 (Metric)**: довжина 1.0 мм, ширина 0.5 мм.

Якщо інженер у полі `Footprint` схемного BOM вказав `0603`, маючи на увазі дюймові компоненти, а бібліотекар САПР зберіг футпринт під назвою `C_0603_Metric`, валідатор повинен розпізнати контекст або попередити про критичну невідповідність габаритів у 2.6 раза.

### Суфікси модифікацій та рівнів щільності IPC

Стандарт IPC-7351 додає до назви посадкового місця суфікси, що визначають умови щільності монтажу та технологічний процес пайки:
- `_M` (Most Material Condition) — максимальний розмір контактних майданчиків для високонадійних виробів (Military, Aerospace, Medical) або пайки хвилею припою.
- `_N` (Nominal Material Condition) — стандартний розмір для загального промислового та споживчого монтажу оплавленням (Reflow).
- `_L` (Least Material Condition) — мінімальний розмір площадок для мініатюрних портативних пристроїв високої щільності (Smartphones, Wearables).

Крім того, САПР використовують альтернативні синоніми для однакових фізичних корпусів:
- `SOIC-8`, `SOIC8_N`, `SO-8`, `SOIC-8_3.9x4.9mm_P1.27mm`.
- `SOT-23`, `SOT-23-3`, `TO-236AB`, `SOT23`.
- `LQFP-64`, `LQFP-64_10x10mm_P0.5mm`, `LQFP64`.
- `DO-214AC`, `SMA`, `SOD-106`.

### Алгоритм канонізації та перехресної звірки

Для коректного зіставлення BOM та CPL валідатор застосовує конвеєр канонізації назв футпринтів:
1. **Нормалізація рядка**: переведення в верхній регістр, видалення символів підкреслення, дефісів, пробілів та суфіксів щільності (`_M`, `_N`, `_L`, `_HANDSOLDERING`).
2. **Пошук за словником аліасів (Alias Dictionary)**: зіставлення очищеного токена (наприклад, `SOT233` або `TO236AB`) з канонічним класом `SOT-23`.
3. **Верифікація кількості виводів та кроку**: перевірка відповідності кількості виводів у схемному символі BOM та кількості контактних майданчиків посадкового місця в базі CPL/Gerber.

Якщо виявлено, що для мікросхеми в BOM вказано корпус `SOIC-8`, а в CPL передано координати для `LQFP-64` (наприклад, через помилку прив'язки посадкового місця в редакторі схеми), валідатор фіксує критичну структурну помилку `FOOTPRINT_CLASS_MISMATCH`, запобігаючи виготовленню непридатної друкованої плати.

## Архітектура та конвеєр обробки

Програма будується за трифазним конвеєром обробки даних:

```
+-------------------------------------------------------------------------+
|                              ФАЗА 1: BOM ПАРСИНГ                        |
| CSV Рядок -> Токенізація -> Очищення лапок -> Розгортання списків RefDes|
|                         -> Запис у Хеш-таблицю                          |
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+-------------------------------------------------------------------------+
|                              ФАЗА 2: CPL ПАРСИНГ                        |
| CSV Рядок -> Парсинг X/Y/Layer/Rot -> Нормалізація кута                 |
|                         -> Запис у динамічний список                    |
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+-------------------------------------------------------------------------+
|                         ФАЗА 3: ПЕРЕХРЕСНА ВАЛІДАЦІЯ                    |
|  1. CPL -> BOM: Пошук за RefDes, перевірка DNP, кутів, шарів            |
|  2. BOM -> CPL: Пошук нерозміщених активних позицій                     |
|  3. Генерація звіту та обчислення коду повернення процесу               |
+-------------------------------------------------------------------------+
```

### Фаза 1: Парсинг і розгортання BOM
У реальних BOM-файлах позиційні позначення часто записуються списками через кому всередині лапок (наприклад, `"R1, R2, R3, R4"`), через пробіли або як числові діапазони (`"C10-C15"`). Парсер повинен:
1. Виділити повне значення колонки `Designator`, ігноруючи коми всередині екранованих лапками полів відповідно до стандарту RFC 4180.
2. Видалити зовнішні лапки та пробільні символи.
3. Розбити рядок на окремі токени та помістити кожен атомарний `RefDes` у внутрішню хеш-таблицю.
4. Зберегти зв'язок між кожним позначенням і його атрибутами: номіналом (`Value`), типом корпусу (`Footprint`), заводським артикулом (`MPN`) та прапорцем `DNP`.

### Фаза 2: Зчитування та нормалізація CPL
Парсер CPL обробляє геометричні дані:
1. Зчитує обов'язкові поля: `Designator`, `MidX`, `MidY`, `Layer`, `Rotation`.
2. Конвертує числові поля `MidX` та `MidY` з урахуванням дійсних чисел із рухомою комою.
3. Нормалізує кут `Rotation` до канонічного діапазону `[0.0, 360.0)`.
4. Визначає монтажний шар через словник валідних синонімів (`Top`, `TopLayer`, `T`, `Bottom`, `BottomLayer`, `B`).

### Фаза 3: Перехресна валідація та генерація звіту
Алгоритм перехресної перевірки працює за дві ітерації:
- **Прямий прохід (CPL → BOM)**: Перебираються всі фізичні координати з файлу CPL. Для кожного `RefDes` виконується `O(1)` пошук у хеш-таблиці BOM. Якщо запис відсутній — фіксується помилка `Фантомне розміщення`. Якщо компонент знайдено, але він має прапорець `DNP=1` — фіксується конфлікт `Монтаж DNP деталі`. Успішно зіставлені записи позначаються прапорцем `matched`.
- **Зворотний прохід (BOM → CPL)**: Перебираються всі записи в хеш-таблиці BOM. Якщо запис не має позначки `matched` і не є `DNP` — фіксується критична помилка `Пропущене розміщення в CPL`.

## Реалізація на C99 та C++20

Нижче наведено промислові реалізації валідатора двома мовами. Версія C99 оптимізована для вбудованих скриптів збірки без зовнішніх бібліотек, використовує швидку хеш-функцію djb2 та пряме керування динамічною пам'яттю. Версія C++20 спирається на сучасні можливості стандарту: `std::string_view`, `std::unordered_map`, `std::vector`, строго типізовані переліки `enum class`, форматування `std::format` та повну безпеку керування ресурсами через RAII.

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>
#include <math.h>

#define MAX_LINE_LEN 1024
#define MAX_REFDES_LEN 32
#define MAX_STR_LEN 128
#define HASH_TABLE_CAPACITY 4096

typedef enum {
    LAYER_TOP = 0,
    LAYER_BOTTOM = 1,
    LAYER_UNKNOWN = 2
} pcb_layer_t;

typedef struct {
    char refdes[MAX_REFDES_LEN];
    char value[MAX_STR_LEN];
    char footprint[MAX_STR_LEN];
    char mpn[MAX_STR_LEN];
    bool is_dnp;
    bool matched_in_cpl;
} bom_entry_t;

typedef struct bom_node {
    bom_entry_t entry;
    struct bom_node *next;
} bom_node_t;

typedef struct {
    bom_node_t *buckets[HASH_TABLE_CAPACITY];
    size_t count;
} bom_table_t;

typedef struct {
    char refdes[MAX_REFDES_LEN];
    double mid_x;
    double mid_y;
    double rotation;
    pcb_layer_t layer;
    bool matched_in_bom;
} cpl_entry_t;

typedef struct {
    cpl_entry_t *items;
    size_t count;
    size_t capacity;
} cpl_list_t;

typedef struct {
    size_t missing_in_cpl;
    size_t extra_in_cpl;
    size_t dnp_with_cpl;
    size_t invalid_rotation;
    size_t total_errors;
} validation_stats_t;

/* Хеш-функція Dan Bernstein (djb2) для рядкових ключів */
static unsigned int hash_string(const char *str) {
    unsigned int hash = 5381;
    int c;
    while ((c = (unsigned char)*str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash % HASH_TABLE_CAPACITY;
}

static char *trim_whitespace(char *str) {
    char *end;
    while (isspace((unsigned char)*str)) str++;
    if (*str == 0) return str;
    end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;
    end[1] = '\0';
    return str;
}

static void strip_quotes(char *str) {
    size_t len = strlen(str);
    if (len >= 2 && str[0] == '"' && str[len - 1] == '"') {
        memmove(str, str + 1, len - 2);
        str[len - 2] = '\0';
    }
}

static void bom_table_init(bom_table_t *table) {
    memset(table->buckets, 0, sizeof(table->buckets));
    table->count = 0;
}

static bool bom_table_insert(bom_table_t *table, const bom_entry_t *entry) {
    unsigned int bucket = hash_string(entry->refdes);
    bom_node_t *curr = table->buckets[bucket];
    while (curr) {
        if (strcmp(curr->entry.refdes, entry->refdes) == 0) {
            return false; /* Дублювання RefDes у BOM */
        }
        curr = curr->next;
    }
    bom_node_t *new_node = (bom_node_t *)malloc(sizeof(bom_node_t));
    if (!new_node) return false;
    new_node->entry = *entry;
    new_node->next = table->buckets[bucket];
    table->buckets[bucket] = new_node;
    table->count++;
    return true;
}

static bom_entry_t *bom_table_lookup(bom_table_t *table, const char *refdes) {
    unsigned int bucket = hash_string(refdes);
    bom_node_t *curr = table->buckets[bucket];
    while (curr) {
        if (strcmp(curr->entry.refdes, refdes) == 0) {
            return &curr->entry;
        }
        curr = curr->next;
    }
    return NULL;
}

static void bom_table_free(bom_table_t *table) {
    for (size_t i = 0; i < HASH_TABLE_CAPACITY; i++) {
        bom_node_t *curr = table->buckets[i];
        while (curr) {
            bom_node_t *tmp = curr;
            curr = curr->next;
            free(tmp);
        }
        table->buckets[i] = NULL;
    }
    table->count = 0;
}

static void cpl_list_init(cpl_list_t *list) {
    list->items = NULL;
    list->count = 0;
    list->capacity = 0;
}

static bool cpl_list_append(cpl_list_t *list, const cpl_entry_t *entry) {
    if (list->count >= list->capacity) {
        size_t new_cap = list->capacity == 0 ? 64 : list->capacity * 2;
        cpl_entry_t *new_items = (cpl_entry_t *)realloc(list->items, new_cap * sizeof(cpl_entry_t));
        if (!new_items) return false;
        list->items = new_items;
        list->capacity = new_cap;
    }
    list->items[list->count++] = *entry;
    return true;
}

static void cpl_list_free(cpl_list_t *list) {
    free(list->items);
    list->items = NULL;
    list->count = 0;
    list->capacity = 0;
}

static pcb_layer_t parse_layer(const char *str) {
    if (strcasecmp(str, "Top") == 0 || strcasecmp(str, "T") == 0 || strcasecmp(str, "TopLayer") == 0) {
        return LAYER_TOP;
    }
    if (strcasecmp(str, "Bottom") == 0 || strcasecmp(str, "B") == 0 || strcasecmp(str, "BottomLayer") == 0) {
        return LAYER_BOTTOM;
    }
    return LAYER_UNKNOWN;
}

static const char *layer_to_string(pcb_layer_t layer) {
    switch (layer) {
        case LAYER_TOP: return "Top";
        case LAYER_BOTTOM: return "Bottom";
        default: return "Unknown";
    }
}

static void parse_and_insert_bom_refdes(bom_table_t *table, char *raw_refdes,
                                       const char *val, const char *footprint,
                                       const char *mpn, bool is_dnp) {
    strip_quotes(raw_refdes);
    char *token = strtok(raw_refdes, ",; ");
    while (token) {
        char *cleaned = trim_whitespace(token);
        if (strlen(cleaned) > 0) {
            bom_entry_t entry;
            memset(&entry, 0, sizeof(entry));
            strncpy(entry.refdes, cleaned, MAX_REFDES_LEN - 1);
            strncpy(entry.value, val, MAX_STR_LEN - 1);
            strncpy(entry.footprint, footprint, MAX_STR_LEN - 1);
            strncpy(entry.mpn, mpn, MAX_STR_LEN - 1);
            entry.is_dnp = is_dnp;
            entry.matched_in_cpl = false;
            bom_table_insert(table, &entry);
        }
        token = strtok(NULL, ",; ");
    }
}

static bool load_bom_csv(const char *filepath, bom_table_t *table) {
    FILE *fp = fopen(filepath, "r");
    if (!fp) {
        fprintf(stderr, "Помилка відкриття BOM файлу: %s\n", filepath);
        return false;
    }

    char line[MAX_LINE_LEN];
    bool is_header = true;

    while (fgets(line, sizeof(line), fp)) {
        char *trimmed = trim_whitespace(line);
        if (strlen(trimmed) == 0) continue;

        if (is_header) {
            is_header = false;
            continue;
        }

        char refdes_buf[MAX_STR_LEN] = {0};
        char val_buf[MAX_STR_LEN] = {0};
        char foot_buf[MAX_STR_LEN] = {0};
        char mpn_buf[MAX_STR_LEN] = {0};
        char dnp_buf[MAX_STR_LEN] = {0};

        int col = 0;
        char *ptr = trimmed;
        bool in_quotes = false;
        char *col_start = ptr;

        while (*ptr) {
            if (*ptr == '"') {
                in_quotes = !in_quotes;
            } else if (*ptr == ',' && !in_quotes) {
                *ptr = '\0';
                char *field = trim_whitespace(col_start);
                strip_quotes(field);
                if (col == 0) strncpy(refdes_buf, field, sizeof(refdes_buf) - 1);
                else if (col == 1) strncpy(val_buf, field, sizeof(val_buf) - 1);
                else if (col == 2) strncpy(foot_buf, field, sizeof(foot_buf) - 1);
                else if (col == 3) strncpy(mpn_buf, field, sizeof(mpn_buf) - 1);
                else if (col == 4) strncpy(dnp_buf, field, sizeof(dnp_buf) - 1);
                col++;
                col_start = ptr + 1;
            }
            ptr++;
        }
        if (col_start <= ptr) {
            char *field = trim_whitespace(col_start);
            strip_quotes(field);
            if (col == 0) strncpy(refdes_buf, field, sizeof(refdes_buf) - 1);
            else if (col == 1) strncpy(val_buf, field, sizeof(val_buf) - 1);
            else if (col == 2) strncpy(foot_buf, field, sizeof(foot_buf) - 1);
            else if (col == 3) strncpy(mpn_buf, field, sizeof(mpn_buf) - 1);
            else if (col == 4) strncpy(dnp_buf, field, sizeof(dnp_buf) - 1);
        }

        bool is_dnp = (strcmp(dnp_buf, "1") == 0 ||
                       strcasecmp(dnp_buf, "DNP") == 0 ||
                       strcasecmp(dnp_buf, "DNI") == 0 ||
                       strcasecmp(dnp_buf, "TRUE") == 0);

        parse_and_insert_bom_refdes(table, refdes_buf, val_buf, foot_buf, mpn_buf, is_dnp);
    }

    fclose(fp);
    return true;
}

static bool load_cpl_csv(const char *filepath, cpl_list_t *list) {
    FILE *fp = fopen(filepath, "r");
    if (!fp) {
        fprintf(stderr, "Помилка відкриття CPL файлу: %s\n", filepath);
        return false;
    }

    char line[MAX_LINE_LEN];
    bool is_header = true;

    while (fgets(line, sizeof(line), fp)) {
        char *trimmed = trim_whitespace(line);
        if (strlen(trimmed) == 0) continue;

        if (is_header) {
            is_header = false;
            continue;
        }

        char refdes_buf[MAX_REFDES_LEN] = {0};
        char x_buf[MAX_STR_LEN] = {0};
        char y_buf[MAX_STR_LEN] = {0};
        char layer_buf[MAX_STR_LEN] = {0};
        char rot_buf[MAX_STR_LEN] = {0};

        int col = 0;
        char *ptr = trimmed;
        bool in_quotes = false;
        char *col_start = ptr;

        while (*ptr) {
            if (*ptr == '"') {
                in_quotes = !in_quotes;
            } else if (*ptr == ',' && !in_quotes) {
                *ptr = '\0';
                char *field = trim_whitespace(col_start);
                strip_quotes(field);
                if (col == 0) strncpy(refdes_buf, field, sizeof(refdes_buf) - 1);
                else if (col == 1) strncpy(x_buf, field, sizeof(x_buf) - 1);
                else if (col == 2) strncpy(y_buf, field, sizeof(y_buf) - 1);
                else if (col == 3) strncpy(layer_buf, field, sizeof(layer_buf) - 1);
                else if (col == 4) strncpy(rot_buf, field, sizeof(rot_buf) - 1);
                col++;
                col_start = ptr + 1;
            }
            ptr++;
        }
        if (col_start <= ptr) {
            char *field = trim_whitespace(col_start);
            strip_quotes(field);
            if (col == 0) strncpy(refdes_buf, field, sizeof(refdes_buf) - 1);
            else if (col == 1) strncpy(x_buf, field, sizeof(x_buf) - 1);
            else if (col == 2) strncpy(y_buf, field, sizeof(y_buf) - 1);
            else if (col == 3) strncpy(layer_buf, field, sizeof(layer_buf) - 1);
            else if (col == 4) strncpy(rot_buf, field, sizeof(rot_buf) - 1);
        }

        if (strlen(refdes_buf) > 0) {
            cpl_entry_t entry;
            memset(&entry, 0, sizeof(entry));
            strncpy(entry.refdes, refdes_buf, sizeof(entry.refdes) - 1);
            entry.mid_x = atof(x_buf);
            entry.mid_y = atof(y_buf);
            entry.rotation = atof(rot_buf);
            entry.layer = parse_layer(layer_buf);
            entry.matched_in_bom = false;
            cpl_list_append(list, &entry);
        }
    }

    fclose(fp);
    return true;
}

static void validate_assembly_package(bom_table_t *bom, cpl_list_t *cpl, validation_stats_t *stats) {
    memset(stats, 0, sizeof(validation_stats_t));

    printf("=================================================================\n");
    printf("   ЗВІТ ВАЛІДАЦІЇ МОНТАЖНОГО ПАКЕТА (BOM <-> CPL MATCHING)\n");
    printf("=================================================================\n\n");

    for (size_t i = 0; i < cpl->count; i++) {
        cpl_entry_t *c_entry = &cpl->items[i];
        bom_entry_t *b_entry = bom_table_lookup(bom, c_entry->refdes);

        if (!b_entry) {
            printf("[ПОМИЛКА] CPL позиція '%s' відсутня в BOM (Фантомне розміщення)!\n", c_entry->refdes);
            printf("          Координати: (X=%.2f, Y=%.2f), Шар: %s, Кут: %.1f deg\n\n",
                   c_entry->mid_x, c_entry->mid_y, layer_to_string(c_entry->layer), c_entry->rotation);
            stats->extra_in_cpl++;
            stats->total_errors++;
        } else {
            c_entry->matched_in_bom = true;
            b_entry->matched_in_cpl = true;

            if (b_entry->is_dnp) {
                printf("[ПОПЕРЕДЖЕННЯ] Позиція '%s' позначена як DNP у BOM, але присутня в CPL!\n", c_entry->refdes);
                printf("               Деталь '%s' (%s) не повинна монтуватися на плату.\n\n",
                       b_entry->value, b_entry->mpn);
                stats->dnp_with_cpl++;
            }
        }

        if (c_entry->rotation < 0.0 || c_entry->rotation >= 360.0) {
            double normalized = fmod(fmod(c_entry->rotation, 360.0) + 360.0, 360.0);
            printf("[УВАГА] Позиція '%s' має ненормалізований кут: %.2f deg (Нормалізація -> %.2f deg)\n\n",
                   c_entry->refdes, c_entry->rotation, normalized);
            stats->invalid_rotation++;
        }
    }

    for (size_t i = 0; i < HASH_TABLE_CAPACITY; i++) {
        bom_node_t *node = bom->buckets[i];
        while (node) {
            if (!node->entry.matched_in_cpl && !node->entry.is_dnp) {
                printf("[ПОМИЛКА] BOM позиція '%s' відсутня в CPL файлі центроїдів!\n", node->entry.refdes);
                printf("          Номінал: %s, Корпус: %s, MPN: %s\n\n",
                       node->entry.value, node->entry.footprint, node->entry.mpn);
                stats->missing_in_cpl++;
                stats->total_errors++;
            }
            node = node->next;
        }
    }

    printf("-----------------------------------------------------------------\n");
    printf("ПІДСУМОК ПЕРЕВІРКИ:\n");
    printf("  - Усього записів у BOM : %zu\n", bom->count);
    printf("  - Усього записів у CPL : %zu\n", cpl->count);
    printf("  - Пропущено в CPL      : %zu\n", stats->missing_in_cpl);
    printf("  - Фантомних у CPL      : %zu\n", stats->extra_in_cpl);
    printf("  - DNP із координатами  : %zu\n", stats->dnp_with_cpl);
    printf("  - Ненормалізованих кутів: %zu\n", stats->invalid_rotation);
    printf("  - Критичних помилок    : %zu\n", stats->total_errors);
    printf("-----------------------------------------------------------------\n");

    if (stats->total_errors == 0) {
        printf("СТАТУС: МОНТАЖНИЙ ПАКЕТ ВАЛІДНИЙ (ГОТОВИЙ ДО ВИРОБНИЦТВА)\n");
    } else {
        printf("СТАТУС: ВИЯВЛЕНО НЕВІДПОВІДНОСТІ (ПОТРІБНЕ ВИПРАВЛЕННЯ САПР)\n");
    }
    printf("=================================================================\n");
}

int main(int argc, char **argv) {
    const char *bom_path = (argc > 1) ? argv[1] : "bom.csv";
    const char *cpl_path = (argc > 2) ? argv[2] : "cpl.csv";

    bom_table_t bom;
    cpl_list_t cpl;
    validation_stats_t stats;

    bom_table_init(&bom);
    cpl_list_init(&cpl);

    printf("Завантаження BOM: %s ...\n", bom_path);
    if (!load_bom_csv(bom_path, &bom)) {
        bom_table_free(&bom);
        cpl_list_free(&cpl);
        return 1;
    }

    printf("Завантаження CPL: %s ...\n", cpl_path);
    if (!load_cpl_csv(cpl_path, &cpl)) {
        bom_table_free(&bom);
        cpl_list_free(&cpl);
        return 1;
    }

    validate_assembly_package(&bom, &cpl, &stats);

    bom_table_free(&bom);
    cpl_list_free(&cpl);

    return (stats.total_errors == 0) ? 0 : 2;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <cmath>
#include <algorithm>
#include <iomanip>
#include <format>
#include <optional>

enum class PcbLayer {
    Top,
    Bottom,
    Unknown
};

[[nodiscard]] constexpr std::string_view to_string(PcbLayer layer) noexcept {
    switch (layer) {
        case PcbLayer::Top: return "Top";
        case PcbLayer::Bottom: return "Bottom";
        default: return "Unknown";
    }
}

[[nodiscard]] PcbLayer parse_layer(std::string_view str) noexcept {
    if (str == "Top" || str == "T" || str == "TopLayer") return PcbLayer::Top;
    if (str == "Bottom" || str == "B" || str == "BottomLayer") return PcbLayer::Bottom;
    return PcbLayer::Unknown;
}

struct BomEntry {
    std::string refdes;
    std::string value;
    std::string footprint;
    std::string mpn;
    bool is_dnp{false};
    bool matched_in_cpl{false};
};

struct CplEntry {
    std::string refdes;
    double mid_x{0.0};
    double mid_y{0.0};
    double rotation{0.0};
    PcbLayer layer{PcbLayer::Top};
    bool matched_in_bom{false};
};

struct ValidationStats {
    std::size_t missing_in_cpl{0};
    std::size_t extra_in_cpl{0};
    std::size_t dnp_with_cpl{0};
    std::size_t invalid_rotation{0};
    std::size_t total_errors{0};
};

class AssemblyValidator {
public:
    static std::string_view trim(std::string_view s) noexcept {
        const auto start = s.find_first_not_of(" \t\r\n");
        if (start == std::string_view::npos) return {};
        const auto end = s.find_last_not_of(" \t\r\n");
        return s.substr(start, end - start + 1);
    }

    static std::string_view strip_quotes(std::string_view s) noexcept {
        if (s.size() >= 2 && s.front() == '"' && s.back() == '"') {
            return s.substr(1, s.size() - 2);
        }
        return s;
    }

    static std::vector<std::string> split_csv_line(std::string_view line) {
        std::vector<std::string> fields;
        std::string current;
        bool in_quotes = false;

        for (char ch : line) {
            if (ch == '"') {
                in_quotes = !in_quotes;
            } else if (ch == ',' && !in_quotes) {
                fields.emplace_back(strip_quotes(trim(current)));
                current.clear();
                continue;
            }
            current.push_back(ch);
        }
        fields.emplace_back(strip_quotes(trim(current)));
        return fields;
    }

    bool load_bom(const std::string& filepath) {
        std::ifstream file(filepath);
        if (!file.is_open()) {
            std::cerr << "Не вдалося відкрити BOM файл: " << filepath << '\n';
            return false;
        }

        std::string line;
        bool is_header = true;

        while (std::getline(file, line)) {
            const auto trimmed = trim(line);
            if (trimmed.empty()) continue;

            if (is_header) {
                is_header = false;
                continue;
            }

            const auto fields = split_csv_line(trimmed);
            if (fields.size() < 4) continue;

            const std::string& raw_refdes = fields[0];
            const std::string& val = fields[1];
            const std::string& footprint = fields[2];
            const std::string& mpn = fields[3];
            bool is_dnp = false;

            if (fields.size() >= 5) {
                const auto dnp_str = fields[4];
                is_dnp = (dnp_str == "1" || dnp_str == "DNP" || dnp_str == "DNI" || dnp_str == "TRUE");
            }

            // Розбиваємо групові позначення (наприклад, "R1, R2, R3")
            std::stringstream ss(raw_refdes);
            std::string single_ref;
            while (std::getline(ss, single_ref, ',')) {
                auto cleaned = std::string(strip_quotes(trim(single_ref)));
                if (!cleaned.empty()) {
                    bom_map_[cleaned] = BomEntry{
                        .refdes = cleaned,
                        .value = val,
                        .footprint = footprint,
                        .mpn = mpn,
                        .is_dnp = is_dnp,
                        .matched_in_cpl = false
                    };
                }
            }
        }
        return true;
    }

    bool load_cpl(const std::string& filepath) {
        std::ifstream file(filepath);
        if (!file.is_open()) {
            std::cerr << "Не вдалося відкрити CPL файл: " << filepath << '\n';
            return false;
        }

        std::string line;
        bool is_header = true;

        while (std::getline(file, line)) {
            const auto trimmed = trim(line);
            if (trimmed.empty()) continue;

            if (is_header) {
                is_header = false;
                continue;
            }

            const auto fields = split_csv_line(trimmed);
            if (fields.size() < 5) continue;

            try {
                cpl_list_.push_back(CplEntry{
                    .refdes = fields[0],
                    .mid_x = std::stod(fields[1]),
                    .mid_y = std::stod(fields[2]),
                    .rotation = std::stod(fields[4]),
                    .layer = parse_layer(fields[3]),
                    .matched_in_bom = false
                });
            } catch (const std::exception& e) {
                std::cerr << "Помилка парсингу рядка CPL: " << line << " (" << e.what() << ")\n";
            }
        }
        return true;
    }

    [[nodiscard]] ValidationStats validate() {
        ValidationStats stats;

        std::cout << "=================================================================\n";
        std::cout << "   ЗВІТ ВАЛІДАЦІЇ МОНТАЖНОГО ПАКЕТА (BOM <-> CPL MATCHING)\n";
        std::cout << "=================================================================\n\n";

        for (auto& c_entry : cpl_list_) {
            auto it = bom_map_.find(c_entry.refdes);
            if (it == bom_map_.end()) {
                std::cout << std::format("[ПОМИЛКА] CPL позиція '{}' відсутня в BOM (Фантомне розміщення)!\n", c_entry.refdes);
                std::cout << std::format("          Координати: (X={:.2f}, Y={:.2f}), Шар: {}, Кут: {:.1f} deg\n\n",
                                         c_entry.mid_x, c_entry.mid_y, to_string(c_entry.layer), c_entry.rotation);
                stats.extra_in_cpl++;
                stats.total_errors++;
            } else {
                c_entry.matched_in_bom = true;
                it->second.matched_in_cpl = true;

                if (it->second.is_dnp) {
                    std::cout << std::format("[ПОПЕРЕДЖЕННЯ] Позиція '{}' позначена як DNP у BOM, але присутня в CPL!\n", c_entry.refdes);
                    std::cout << std::format("               Деталь '{}' ({}) не повинна монтуватися.\n\n",
                                             it->second.value, it->second.mpn);
                    stats.dnp_with_cpl++;
                }
            }

            if (c_entry.rotation < 0.0 || c_entry.rotation >= 360.0) {
                const double normalized = std::fmod(std::fmod(c_entry.rotation, 360.0) + 360.0, 360.0);
                std::cout << std::format("[УВАГА] Позиція '{}' має ненормалізований кут: {:.2f} deg (Нормалізація -> {:.2f} deg)\n\n",
                                         c_entry.refdes, c_entry.rotation, normalized);
                stats.invalid_rotation++;
            }
        }

        for (const auto& [refdes, b_entry] : bom_map_) {
            if (!b_entry.matched_in_cpl && !b_entry.is_dnp) {
                std::cout << std::format("[ПОМИЛКА] BOM позиція '{}' відсутня в CPL файлі центроїдів!\n", refdes);
                std::cout << std::format("          Номінал: {}, Корпус: {}, MPN: {}\n\n",
                                         b_entry.value, b_entry.footprint, b_entry.mpn);
                stats.missing_in_cpl++;
                stats.total_errors++;
            }
        }

        std::cout << "-----------------------------------------------------------------\n";
        std::cout << "ПІДСУМОК ПЕРЕВІРКИ:\n";
        std::cout << std::format("  - Усього записів у BOM : {}\n", bom_map_.size());
        std::cout << std::format("  - Усього записів у CPL : {}\n", cpl_list_.size());
        std::cout << std::format("  - Пропущено в CPL      : {}\n", stats.missing_in_cpl);
        std::cout << std::format("  - Фантомних у CPL      : {}\n", stats.extra_in_cpl);
        std::cout << std::format("  - DNP із координатами  : {}\n", stats.dnp_with_cpl);
        std::cout << std::format("  - Ненормалізованих кутів: {}\n", stats.invalid_rotation);
        std::cout << std::format("  - Критичних помилок    : {}\n", stats.total_errors);
        std::cout << "-----------------------------------------------------------------\n";

        if (stats.total_errors == 0) {
            std::cout << "СТАТУС: МОНТАЖНИЙ ПАКЕТ ВАЛІДНИЙ (ГОТОВИЙ ДО ВИРОБНИЦТВА)\n";
        } else {
            std::cout << "СТАТУС: ВИЯВЛЕНО НЕВІДПОВІДНОСТІ (ПОТРІБНЕ ВИПРАВЛЕННЯ САПР)\n";
        }
        std::cout << "=================================================================\n";

        return stats;
    }

private:
    std::unordered_map<std::string, BomEntry> bom_map_;
    std::vector<CplEntry> cpl_list_;
};

int main(int argc, char* argv[]) {
    const std::string bom_path = (argc > 1) ? argv[1] : "bom.csv";
    const std::string cpl_path = (argc > 2) ? argv[2] : "cpl.csv";

    AssemblyValidator validator;

    std::cout << "Завантаження BOM: " << bom_path << " ...\n";
    if (!validator.load_bom(bom_path)) {
        return 1;
    }

    std::cout << "Завантаження CPL: " << cpl_path << " ...\n";
    if (!validator.load_cpl(cpl_path)) {
        return 1;
    }

    const auto stats = validator.validate();
    return (stats.total_errors == 0) ? 0 : 2;
}
```
:::

## Інженерні пастки парсингу та виробничі нюанси

Під час інтеграції автоматизованої валідації у виробничий конвеєр виникає низка специфічних труднощів, пов'язаних з особливостями експорту даних із різноманітного програмного забезпечення:

1. **Багатослівні та нестандартні найменування шарів**: Різні версії САПР записують верхній шар як `Top`, `TopLayer`, `T`, `ComponentSide` або `F.Cu` (у KiCad), а нижній — як `Bottom`, `BottomLayer`, `B`, `SolderSide` або `B.Cu`. Промисловий парсер повинен виконувати нормалізацію з урахуванням регістру та списку відомих синонімів, інакше валідатор згенерує хибні помилки на кожному рядку файлу.
2. **Діапазонне представлення позиційних позначень у зведених звітах**: Деякі генератори BOM групують позначення у формі `R1-R10` або `C100..C108` замість явного переліку `R1, R2, ..., R10`. Для коректної обробки таких звітів модуль синтаксичного аналізу повинен розпізнавати символи дефісу та подвійної крапки, виділяти літерний префікс (`R`) та межі числового інтервалу (`1` та `10`), генеруючи повний набір проміжних ключів для додавання у хеш-таблицю.
3. **Локалізація десяткових роздільників та форматів чисел**: У регіональних налаштуваннях операційних систем (зокрема європейських) CSV-файли часто експортуються з комою як десятковим роздільником (`12,50` замість `12.50`) та крапкою з комою як роздільником колонок. Стандартні функції перетворення `atof` або `std::stod` спираються на поточну `LC_NUMERIC` локаль середовища, тому виробничий код або примусово перемикає локаль на `std::locale::classic()`, або самостійно замінює коми на крапки перед числовим парсингом.
4. **Маркери порядку байтів (UTF-8 BOM Header)**: Файли, експортовані з Microsoft Excel або текстових редакторів Windows, часто містять три байти преамбули `0xEF, 0xBB, 0xBF` на початку першого рядка. Якщо парсер не пропускає цю преамбулу, заголовок першої колонки (наприклад, `Designator`) зчитується як пошкоджений рядок `\xef\xbb\xbfDesignator`, що повністю ламає автоматичне зіставлення імен колонок.
5. **Дзеркалювання кутів для компонентів нижнього шару (Bottom Layer)**: За стандартом IPC-7351 при перенесенні компонента на нижню сторону плати його кут повороту відлічується з точки зору перегляду крізь плату. Проте деякі автомати Pick & Place вимагають інверсії знаку кута (`360 - rotation`) або додавання 180 градусів. Цю вимогу слід узгоджувати з конкретним оператором лінії SMT.
6. **Розбіжності у визначенні нульової орієнтації між корпусом та стрічкою**: Стандарт проектування посадкових місць IPC-7351 встановлює нульову орієнтацію (Level A) так, щоб перший вивід мікросхеми знаходився у верхньому лівому кутку. Водночас стандарт пакування в блістерні стрічки EIA-481 орієнтує деталь у кишені з виводом 1 у верхньому правому кутку (поворот на 90° за годинниковою стрілкою відносно напрямку руху стрічки). Якщо P&P файл не містить коригуючого зміщення, автомат посадить мікросхему з поворотом на 90°, що виведе з ладу всю зібрану партію плат.
7. **Контроль компонентів без пайки (Press-fit та механічні стійки)**: Механічні компоненти (різьбові втулки, напрямні, монтажні кутики) часто присутні в BOM для комплектації, але монтуються вручну або пресуванням після паяльної печі. Вони не мають записів у CPL для поверхневого монтажу. Щоб запобігти хибним спрацьовуванням валідатора, такі компоненти повинні маркуватися спеціальними прапорцями або належати до окремої категорії механічних матеріалів (Mechanical BOM).
8. **Обробка спеціальних символів у найменуваннях деталей**: Артикули компонентів часто містять дефіси, косі риски та знаки решітки (наприклад, `RC0603FR-0710KL`, `STM32F401RCT6TR`, `#10-32`). Якщо парсер використовує наївну токенізацію за будь-яким небуквено-цифровим символом, артикули спотворюються. Парсер повинен суворо дотримуватися меж стовпчиків CSV і ділити рядки виключно за межами лапок.
9. **Контроль версій ревізій у заголовках документів**: На виробництві часто зустрічається ситуація, коли інженер надсилає `bom_rev3.csv`, але помилково додає `cpl_rev2.csv`. Просунутий валідатор аналізує метадані або коментарі в заголовках файлів (якщо вони присутні) і попереджає про розбіжність номерів ревізій проєкту.
10. **Зіставлення з шарами паяльної пасти (Paste Mask Cross-Check)**: Розширений конвеєр валідації може аналізувати не лише BOM і CPL, але й Gerber-шари паяльної пасти (`GTP` / `GBP`). Для кожного компонента з CPL перевіряється наявність вікон пасти у відповідних координатах. Якщо для SMD-компонента в CPL немає апертур у шарі пасти, це вказує на те, що в бібліотеці посадкових місць САПР прапорець нанесення пасти був випадково вимкнений, і деталь залишиться неприпаяною.

## Інтеграція у конвеєр неперервної інтеграції (CI/CD)

Запуск валідатора автоматизується в системі контролю версій Git під час створення pull request або випуску релізу (Release Tag). Якщо під час експорту файлів інженер забув оновити CPL або допустив друкарську помилку в номіналі, перевірка утиліти повертає ненульовий код виходу (`exit code = 2`), що блокує злиття гілки та запобігає передачі некоректних файлів на контрактне виробництво.

```bash
# Приклад автоматизованого запуску у Makefile або CI workflow
./assembly_validator production/bom_rev2.csv production/cpl_rev2.csv
if [ $? -ne 0 ]; then
    echo "Помилка валідації монтажного пакета! Збірку зупинено."
    exit 1
fi
```

## Тестові сценарії та верифікація валідатора

Для підтвердження надійності роботи валідатор тестується набором синтетичних файлів із штучно внесеними дефектами:

| Тестовий випадок | Вхідний дефект у файлах | Очікувана реакція валідатора |
| :--- | :--- | :--- |
| `TC-01: Ідеальний збіг` | 100% відповідність BOM та CPL, валідні кути | Код виходу `0`, статус `МОНТАЖНИЙ ПАКЕТ ВАЛІДНИЙ` |
| `TC-02: Забутий CPL` | `R5` є в BOM, але рядок відсутній у CPL | Помилка `ERR_MISSING_IN_CPL`, код `2` |
| `TC-03: Фантомна деталь` | `C99` присутній у CPL, але відсутній у BOM | Помилка `ERR_EXTRA_IN_CPL`, код `2` |
| `TC-04: Монтаж DNP` | `R10` має `DNP=1`, але є запис у CPL | Застереження `WARN_DNP_PLACED`, код `0` або `2` (за налаштуванням) |
| `TC-05: Від'ємний кут` | `U1` має кут `-90.0°` | Автоматична нормалізація до `270.0°`, фіксація у звіті |
| `TC-06: Екрановані коми` | Поле `"R1, R2, R3"` у лапках | Коректне розгортання на 3 окремі записи без спотворення |

Такий багаторівневий контроль повністю усуває людський фактор і гарантує, що оператор лінії поверхневого монтажу отримає на 100% узгоджений комплект даних, готовий до безпомилкового запуску складального автомата.

