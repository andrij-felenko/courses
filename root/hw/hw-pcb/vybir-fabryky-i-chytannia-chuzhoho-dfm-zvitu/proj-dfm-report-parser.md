# ⚙️ Утиліта автоматизованого аналізу DFM-зауважень та аудиту герберів

Коли інженер проєктує друковану плату високої щільності компонування (англ. *High-Density Interconnect*, HDI) або складний багатошаровий пристрій із тонконіжковими мікросхемами QFN, BGA та пасивними компонентами типорозміру 0402, відправка гербер-файлів на виробництво без попередньої локальної верифікації неминуче призводить до затримок. Якщо виробнича фабрика розташована в іншому часовому поясі, отримання інженерного запиту (англ. *Engineering Questions*, EQ) через виявлення однієї пастки кислоти чи мікроскопічного зазору паяльної маски зупиняє замовлення щонайменше на добу.

Ще більшу небезпеку становить режим «тихого виправлення» (англ. *Auto-CAM correction*), коли програмний комплекс фабрики автоматично зрізає елементи міді або модифікує вікна маски без участі розробника. Наслідком такого втручання може стати зміна хвильового опору диференційних ліній, підрізання позначень полярності або порушення площі контакту під критичними компонентами. Щоб усунути людський фактор і отримати повний контроль над технологічністю плати, інженеру необхідний власний інструмент локального геометричного аудиту, інтегрований у процес розробки та конвеєр неперервної інтеграції (CI/CD).

Цей проєкт реалізує модульну систему перевірки топологічних правил DFM. Програма аналізує координати та геометрію примітивів друкованої плати, розраховує векторні кути сходження трас, визначає найкоротші відстані до ліній механічного контуру, оптимізує просторовий пошук за допомогою сіткового індексування та моделює поведінку отворів із урахуванням виробничого розкиду свердлильних верстатів.

## Чому вбудованого DRC у САПР недостатньо

Більшість інженерів-початківців вважає, що успішне проходження вбудованої перевірки правил проектування (англ. *Design Rule Check*, DRC) у середовищі проектування (Altium Designer, KiCad, Cadence Allegro чи Eagle) гарантує безпроблемне виготовлення плати на будь-якому заводі. Проте між логічним DRC у CAD-системі та фізичним DFM-аудитом на фабриці існує принципова прірва.

Вбудований DRC у САПР перевіряє дотримання **електричних та сіткових зазорів** між логічними колами схеми (*Net-to-Net Clearance*):
- Якщо дві доріжки належать до одного електричного кола (наприклад, `GND` або `+3V3`), вбудований DRC САПР дозволяє їм з'єднуватися під будь-яким кутом — навіть 15° чи 30°. Для схемотехнічного редактора це цілісний електричний вузол. Але для лінії хімічного травлення гострий кут 30° є фізичною пасткою травильного розчину (Acid Trap), де через капілярні сили розчин не вимивається водою і перетравлює мідь.
- Вбудований DRC перевіряє номінальний зазор від центру отвору до краю мідного майданчика. Проте CAD не враховує технологічний ланцюг виробництва: верстат ЧПК використовує свердло більшого діаметра під наступну гальванічну металізацію стінок отвору (Drill Oversize), шпиндель верстата має динамічне радіальне биття (Spindle Runout), а склотекстоліт деформується під час гарячого пресування шарів. У результаті номінально коректний перехідний отвір на практиці отримує дефект повного прориву пояска (Breakout).
- Вбудований DRC контролює відступ шовкографії від міді, але рідко аналізує копланарність та мінімальну ширину перемички рідкої фотополімерної паяльної маски (LPI Mask Dam) між контактами мікросхем із дрібним кроком. Якщо смужка маски має ширину 0.06 мм, вона не полімеризується надійно під УФ-лампою і відшаровується у промивній ванні, що призводить до паяльних перемичок рідким припоєм під час монтажу.

Комерційні CAM-пакети заводів (Frontline InCAM, Genesis 2000, UcamX) коштують десятки тисяч доларів за робоче місце. Створення власної компактної консольної утиліти мовами C99 та C++20 дозволяє розробнику отримати строгий ідентичний контроль геометрії безпосередньо на робочому комп'ютері або у хмарному пайплайні перевірки репозиторію.

## Анатомія векторних форматів Gerber X2 та Excellon

Щоб зрозуміти, як програма аналізує плату, необхідно розглянути структуру вхідних виробничих файлів. Сучасний стандарт Gerber (RS-274X та розширений Gerber X2) описує кожен фізичний шар друкованої плати як послідовність векторних операцій над геометричними апертурами (англ. *apertures*):

1. **Оголошення апертур (Aperture Definitions, `%ADD...%`):** Задають форму та розмір віртуального інструмента експонування:
   - Кругла апертура: `%ADD10C,0.1500*%` — круг діаметром 0.15 мм для трасування сигнальних ліній;
   - Прямокутна апертура: `%ADD11R,0.3000X1.2000*%` — прямокутник 0.3×1.2 мм для контактного майданчика мікросхеми SOIC/QFP;
   - Овальна апертура (Obround): `%ADD12O,0.6000X1.8000*%` — витягнутий овал для контактів рознімів;
   - Спеціальні макроси: `%AM...%` — комплексні фігури з тепловими бар'єрами (Thermal Relief) для терморозв'язки полігонів.
2. **Операції переміщення та засвічення (D-коди):**
   - `D01` (*Interpolate / Expose*): переміщення в задані координати `(X, Y)` з увімкненим променем (малювання відрізка доріжки або дуги кола);
   - `D02` (*Move*): холосте переміщення в точку `(X, Y)` із вимкненим променем;
   - `D03` (*Flash*): одноразовий спалах поточної апертури в точці `(X, Y)` (формування контактного майданчика SMD або перехідного отвору).
3. **Полярність шару (Layer Polarity, `%LPD% / %LPC%`):** Визначає, чи додає поточний шар матеріал (*Dark*), чи вирізає його з попередніх шарів (*Clear*), що критично для негативних шарів внутрішніх полігонів живлення.
4. **Файли свердління (Excellon / NC Drill):** Текстовий формат керування свердлильними верстатами. У заголовку задається таблиця інструментів:
   ```
   M48
   METRIC,LZ
   T01C0.300
   T02C0.800
   %
   T01
   X12000Y15000
   X25000Y30000
   ```
   Тут інструмент `T01` має діаметр 0.300 мм і свердлить отвори в точках з координатами (12.0 мм, 15.0 мм) та (25.0 мм, 30.0 мм).

Утиліта зчитує ці дані, парсить команди, перетворює координати у внутрішнє векторне представлення (масиви точок, відрізків, кіл та полігонів) і запускає математичні алгоритми аналізу технологічності.

## Математичні моделі та алгоритми аудиту

Перевірка правил проектування для виробництва спирається на точні аналітичні алгоритми обчислювальної геометрії на площині.

```
[Огляд обчислювального конвеєра аналізатора DFM]

  Вхідні шари (Gerber / Drill)
        │
        ├── Траси та провідники  ──> [ Алгоритм 1: Детекція пасток кислоти ]
        │                             Векторний скалярний добуток, кути < 85°
        │
        ├── Переходи та отвори   ──> [ Алгоритм 2: Моделювання зсуву свердла ]
        │                             Найгірший радіальний зсув, залишок пояска
        │
        ├── Паяльна маска        ──> [ Алгоритм 3: Аналіз стійкості містків ]
        │                             Зазор між паралельними вікнами < 0.09 мм
        │
        └── Контур (Edge Cuts)   ──> [ Алгоритм 4: Евклідова відстань до фрези ]
                                      Проєкція точки на відрізок, зазор < 0.30 мм
```

### 1. Векторний аналіз пасток кислоти (Acid Traps)

Пастка кислоти утворюється в місці сходження двох провідників під гострим кутом. Нехай два лінійні сегменти траси з'єднуються у спільній вершині `V(x_v, y_v)` і прямують до точок `A(x_a, y_a)` та `B(x_b, y_b)`.

Формуємо напрямні вектори провідників, спрямовані від точки їхнього контакту:

```
v1 = (x_a - x_v, y_a - y_v)
v2 = (x_b - x_v, y_b - y_v)
```

Скалярний добуток двох векторів пов'язаний із кутом `θ` між ними фундаментальним співвідношенням векторної алгебри:

```
v1 · v2 = v1_x · v2_x + v1_y · v2_y = |v1| · |v2| · cos(θ)
```

Норми векторів (їхні евклідові довжини на площині):

```
|v1| = sqrt(v1_x² + v1_y²)
|v2| = sqrt(v2_x² + v2_y²)
```

Значення косинуса кута між напрямками трас визначається як:

```
cos(θ) = (v1 · v2) / (|v1| · |v2|)   [косинус кута між напрямними векторами]
```

Значення кута `θ` в градусах обчислюється через арккосинус із захистом від похибок чисел із рухомою комою (обмеження аргументу діапазоном `[-1.0, 1.0]`):

```
θ = acos(clamp(cos(θ), -1.0, 1.0)) · (180.0 / π)
```

Якщо обчислений кут `θ < 85.0°`, топологічний клин класифікується як пастка травильного розчину. Під час мокрого хімічного травлення в розчинах хлориду заліза або мідно-аміачного комплексу поверхневий натяг кислоти затримує рідину у вершині кута. На етапі промивання водою кислота не вимивається з мікрощілини і продовжує розчиняти мідь, викликаючи стоншення провідника (Necking) або обрив кола під час термоциклування.

### 2. Моделювання механічного зсуву свердла та розрахунок пояска металізації

Для кожного перехідного або вивідного отвору програма розраховує стійкість пояска металізації до зміщення інструменту на верстаті ЧПК.

У розрахунку використовуються фізичні параметри технологічного процесу:
- `D_pad`: діаметр мідного майданчика на зовнішньому або внутрішньому шарі;
- `D_fhs`: номінальний кінцевий діаметр отвору (Finished Hole Size) з файлу свердління;
- `Δ_plating`: технологічна поправка на товщину шару міді, осадженої гальванічним способом на стінки циліндра (зазвичай `0.10 мм`);
- `Δ_wander`: сумарний радіальний розкид позиціонування шпинделя, механічного прогину свердла та температурної усадки склотекстоліту FR-4 (зазвичай `0.04–0.06 мм`).

Діаметр інструментального свердла, яке обирає верстат:

```
D_tool = D_fhs + Δ_plating   [технологічний діаметр інструментального свердла]
```

Номінальна ширина пояска за ідеального центрування отвору:

```
AR_nominal = (D_pad - D_tool) / 2.0
```

Ширина пояска в найгіршому напрямку радіального відхилення осі свердління:

```
AR_worst = AR_nominal - Δ_wander   [залишковий поясок при максимальному зсуві]
```

Критерії класифікації стану пояска:
- Якщо `AR_worst < 0.0`: відбувається фізичний розрив мідного кільця (дефект *Annular Ring Breakout*), що загрожує повною втратою контакту з провідником.
- Якщо `0.0 <= AR_worst < Min_AR` (де `Min_AR = 0.05 мм` відповідно до вимог стандарту IPC-6012 Class 3): отвір утворює критичне стоншення або дотик до межі майданчика (*Tangency*).

### 3. Найкоротша відстань від провідників до контуру плати (Copper-to-Edge)

Шар контуру обрізки плати (*Edge Cuts*) складається з набору лінійних відрізків. Нехай відрізок контуру задано початковою точкою `P1(x1, y1)` та кінцевою точкою `P2(x2, y2)`.

Для довільного центру мідного майданчика `C(x_c, y_c)` вектор відрізка контуру дорівнює `d = P2 - P1`. Параметрична проєкція точки `C` на пряму, що містить відрізок, обчислюється через відношення скалярних добутків:

```
t = ((C - P1) · d) / (d · d)
```

Параметр `t` обмежується межами фізичного відрізка:

```
t_clamped = max(0.0, min(1.0, t))
```

Точка на відрізку, найближча до центру майданчика:

```
P_near = P1 + t_clamped · d
```

Евклідова відстань від центру майданчика до лінії контуру:

```
Dist_center = sqrt((C_x - P_near_x)² + (C_y - P_near_y)²)
```

Фактична відстань від краю міді до контуру обрізки плати з урахуванням радіуса майданчика `R_pad = D_pad / 2`:

```
Clearance_copper = Dist_center - R_pad   [чистий зазор від міді до лінії фрези]
```

Якщо `Clearance_copper < Min_Edge_Clearance` (0.30 мм для фрезерування кінцевою фрезою або 0.50 мм для надрізання дисками V-Scoring), утиліта фіксує дефект недопустимого наближення міді до краю плати.

### 4. Розрахунок мінімальної стійкості містків паяльної маски (Mask Slivers)

Між двома сусідніми вікнами паяльної маски `R1` та `R2` із габаритними розмірами `(w1, h1)` та `(w2, h2)` обчислюється фактичний зазор між їхніми прямокутними межами вздовж координатних осей:

```
Gap_X = max(0.0, |Center1_x - Center2_x| - (w1 + w2) / 2.0)
Gap_Y = max(0.0, |Center1_y - Center2_y| - (h1 + h2) / 2.0)
```

Якщо між вікнами маски залишається смужка полімеру з розміром `0.0 < Gap < Min_Mask_Sliver` (де `Min_Mask_Sliver = 0.09 мм / 3.5 mil`), маска не має достатньої адгезійної площі зчеплення зі склотекстолітом. Під час проявлення лужним розчином карбонату натрію та промивання під тиском смужка лаку відривається, перетворюючись на плаваючий фрагмент. Під час монтажу мікросхем це викликає паяльні містки між ніжками або потрапляння луски маски на контактні майданчики, що призводить до повного порушення контакту.

## Просторове індексування та масштабованість алгоритмів

Прямий попарний перебір усіх геометричних елементів має квадратичну часову складність `O(N²)`. На складній восьмишаровій материнській платі із 150 000 сигнальних сегментів і 25 000 перехідних отворів пряме попарне порівняння вимагало б виконання понад `10¹⁰` обчислень відстаней, що займало б кілька хвилин процесорного часу.

Для досягнення миттєвої швидкодії (менше ніж 100 мілісекунд на плату) утиліта застосовує просторове сіткове індексування (англ. *Uniform Spatial Grid*):
1. Простір плати розбивається на регулярну двовимірну сітку комірок розміром `Cell_size = Max_search_radius` (наприклад, 2.0 мм).
2. Кожен об'єкт реєструється у хеш-таблиці або масиві індексів лише тих комірок, які перетинає його обмежувальний прямокутник (AABB, *Axis-Aligned Bounding Box*).
3. Пошук сусідніх провідників та розрахунок відстаней виконується виключно в межах поточної та 8 сусідніх комірок сітки (шаблон 3×3). Це знижує асимптотичну складність до лінійної `O(N)`, забезпечуючи обробку масивних промислових плат у реальному часі.

## Геометрія синтезу краплеподібних переходів (Teardrop Fillets)

Коли утиліта виявляє ризик зриву пояска (Breakout) або надмірне механічне напруження на стику тонкої доріжки з майданчиком, алгоритм може виконати автоматичний розрахунок параметрів краплеподібного посилення (Teardrop).

Краплеподібний перехід формується двома дотичними відрізками, що з'єднують коло контактного майданчика радіуса `R` із паралельними лініями доріжки ширини `W` на відстані `L_teardrop` від центру отвору:

```
[Геометрія розрахунку дотичних ліній Teardrop]

           ┌─────────────────── Точка дотику T1 (R, α)
          /                     \
         /                       \
   ( Центр C )                    ══════════ Верхній край доріжки (w/2)
         \                       /
          \                     /
           └─────────────────── Точка дотику T2 (R, -α)
```

Кут дотику `α` та координати точок спряження `T1` і `T2` визначаються через розв'язання системи тригонометричних рівнянь дотичних до кола. Додавання такої мідної косинки плавно розподіляє механічне напруження та компенсує зміщення свердла на величину до `0.08 мм`.

## Обробка крайових випадків у векторній геометрії

Під час обробки реальних гербер-файлів алгоритм стикається з низкою специфічних топологічних ситуацій:
- **Колінеарні провідники (Кут 180°):** Пряма лінія, розділена на два сегменти в одній точці, дає скалярний добуток `v1 · v2 = -|v1||v2|` і косинус `-1.0`. Алгоритм коректно розпізнає це як безперервний провідник без пастки кислоти.
- **Накладені зустрічні сегменти (Кут 0°):** У разі помилкового подвійного трасування тієї самої ділянки скалярний добуток дає кут `0°`. Програма фільтрує такі збіги й генерує окреме попередження про надлишкові дубльовані вектори.
- **Внутрішні некруглі вирізи (Internal Cutouts / Slots):** Крім зовнішнього прямокутного контуру, шар *Edge Cuts* містить довільні замкнені полігони для внутрішніх вікон і пазів під розніми. Алгоритм розглядає всі відрізки внутрішніх контурів на рівних правах із зовнішнім периметром, гарантуючи безпечний відступ міді від будь-якого фрезерованого паза.
- **Терморозв'язки полігонів (Thermal Relief Spokes):** Під час підключення виводів до великих мідних полігонів земляних чи силових шарів використовуються хрестоподібні перемички. Якщо ширина перемички надто мала (< 0.15 мм), під час травлення вона може повністю перетравитися, розірвавши контакт. Якщо перемичка занадто широка, тепловий відтік у полігон під час паяння викликає дефект холодної пайки. Модуль виконує автоматичну перевірку ширини спиць термобар'єрів.

## Реалізація аналізатора мовами C99 та C++20

Нижче наведено дві повноцінні еквівалентні реалізації рушія DFM-аудиту:
- Вкладка **C**: процедурний модуль стандарту C99 без динамічних алокацій, призначений для вбудованих систем і швидких утиліт перевірки.
- Вкладка **C++**: сучасний об'єктно-орієнтований рушій стандарту C++20 із застосуванням `std::span`, `enum class`, строгої типізації геометрії та виразного звітування.

:::tabs
```c
/*
 * dfm_parser.c — Модуль геометричного аудиту технологічності плати (C99).
 * Виконує аналіз векторних примітивів, кутів, поясів та контурних зазорів.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef enum {
    SEV_INFO = 0,
    SEV_WARNING = 1,
    SEV_CRITICAL = 2
} severity_t;

typedef enum {
    DEFECT_NONE = 0,
    DEFECT_ACID_TRAP,
    DEFECT_MASK_SLIVER,
    DEFECT_ANNULAR_BREAKOUT,
    DEFECT_ANNULAR_TANGENCY,
    DEFECT_COPPER_TO_EDGE
} defect_type_t;

typedef struct {
    double x;
    double y;
} point2d_t;

typedef struct {
    point2d_t start;
    point2d_t end;
    double width_mm;
    char net_name[32];
} trace_segment_t;

typedef struct {
    point2d_t center;
    double pad_dia_mm;
    double drill_dia_mm;
    char net_name[32];
} via_element_t;

typedef struct {
    point2d_t center;
    double width_mm;
    double height_mm;
    char refdes[16];
} mask_aperture_t;

typedef struct {
    point2d_t p1;
    point2d_t p2;
} outline_segment_t;

typedef struct {
    double min_trace_width_mm;
    double min_trace_clearance_mm;
    double min_mask_sliver_mm;
    double min_annular_ring_mm;
    double min_copper_to_edge_mm;
    double max_acute_angle_deg;
    double drill_runout_tolerance_mm;
    double drill_plating_allowance_mm;
} dfm_rules_config_t;

typedef struct {
    defect_type_t type;
    severity_t severity;
    point2d_t location;
    char description[128];
    char recommendation[128];
} dfm_issue_t;

static double vec_length(point2d_t v) {
    return sqrt(v.x * v.x + v.y * v.y);
}

static double compute_vector_angle_deg(point2d_t v1, point2d_t v2) {
    double l1 = vec_length(v1);
    double l2 = vec_length(v2);
    if (l1 < 1e-6 || l2 < 1e-6) return 180.0;

    double dot = v1.x * v2.x + v1.y * v2.y;
    double cos_val = dot / (l1 * l2);

    if (cos_val > 1.0) cos_val = 1.0;
    if (cos_val < -1.0) cos_val = -1.0;

    return acos(cos_val) * (180.0 / M_PI);
}

static double point_to_segment_distance(point2d_t pt, outline_segment_t seg) {
    double dx = seg.p2.x - seg.p1.x;
    double dy = seg.p2.y - seg.p1.y;
    double len_sq = dx * dx + dy * dy;

    if (len_sq < 1e-9) {
        double px = pt.x - seg.p1.x;
        double py = pt.y - seg.p1.y;
        return sqrt(px * px + py * py);
    }

    double t = ((pt.x - seg.p1.x) * dx + (pt.y - seg.p1.y) * dy) / len_sq;
    if (t < 0.0) t = 0.0;
    if (t > 1.0) t = 1.0;

    double near_x = seg.p1.x + t * dx;
    double near_y = seg.p1.y + t * dy;

    double rx = pt.x - near_x;
    double ry = pt.y - near_y;
    return sqrt(rx * rx + ry * ry);
}

int audit_acid_traps(const trace_segment_t *traces, size_t count,
                     const dfm_rules_config_t *cfg, dfm_issue_t *issues, int max_issues) {
    int found = 0;
    for (size_t i = 0; i < count; i++) {
        for (size_t j = i + 1; j < count; j++) {
            if (found >= max_issues) return found;

            bool connected = false;
            point2d_t vertex;
            point2d_t v1, v2;

            if (fabs(traces[i].start.x - traces[j].start.x) < 1e-4 &&
                fabs(traces[i].start.y - traces[j].start.y) < 1e-4) {
                connected = true;
                vertex = traces[i].start;
                v1 = (point2d_t){traces[i].end.x - vertex.x, traces[i].end.y - vertex.y};
                v2 = (point2d_t){traces[j].end.x - vertex.x, traces[j].end.y - vertex.y};
            } else if (fabs(traces[i].end.x - traces[j].start.x) < 1e-4 &&
                       fabs(traces[i].end.y - traces[j].start.y) < 1e-4) {
                connected = true;
                vertex = traces[i].end;
                v1 = (point2d_t){traces[i].start.x - vertex.x, traces[i].start.y - vertex.y};
                v2 = (point2d_t){traces[j].end.x - vertex.x, traces[j].end.y - vertex.y};
            } else if (fabs(traces[i].end.x - traces[j].end.x) < 1e-4 &&
                       fabs(traces[i].end.y - traces[j].end.y) < 1e-4) {
                connected = true;
                vertex = traces[i].end;
                v1 = (point2d_t){traces[i].start.x - vertex.x, traces[i].start.y - vertex.y};
                v2 = (point2d_t){traces[j].end.x - vertex.x, traces[j].end.y - vertex.y};
            }

            if (connected) {
                double angle = compute_vector_angle_deg(v1, v2);
                if (angle < cfg->max_acute_angle_deg) {
                    dfm_issue_t *iss = &issues[found++];
                    iss->type = DEFECT_ACID_TRAP;
                    iss->severity = SEV_WARNING;
                    iss->location = vertex;
                    snprintf(iss->description, sizeof(iss->description),
                             "Гострий кут трасування: %.1f deg (поріг %.1f deg) у ланцюзі %s",
                             angle, cfg->max_acute_angle_deg, traces[i].net_name);
                    snprintf(iss->recommendation, sizeof(iss->recommendation),
                             "Збільште кут сходження або застосуйте скруглення кутів (filleting)");
                }
            }
        }
    }
    return found;
}

int audit_annular_rings(const via_element_t *vias, size_t count,
                        const dfm_rules_config_t *cfg, dfm_issue_t *issues, int max_issues) {
    int found = 0;
    for (size_t i = 0; i < count; i++) {
        if (found >= max_issues) return found;

        double tool_drill = vias[i].drill_dia_mm + cfg->drill_plating_allowance_mm;
        double nominal_ar = (vias[i].pad_dia_mm - tool_drill) / 2.0;
        double worst_case_ar = nominal_ar - cfg->drill_runout_tolerance_mm;

        if (worst_case_ar < 0.0) {
            dfm_issue_t *iss = &issues[found++];
            iss->type = DEFECT_ANNULAR_BREAKOUT;
            iss->severity = SEV_CRITICAL;
            iss->location = vias[i].center;
            snprintf(iss->description, sizeof(iss->description),
                     "Прорив пояска переходу (Breakout): пад %.2f мм, отвір %.2f мм (дефіцит %.3f мм)",
                     vias[i].pad_dia_mm, tool_drill, -worst_case_ar);
            snprintf(iss->recommendation, sizeof(iss->recommendation),
                     "Збільште діаметр мідного майданчика або додайте Teardrop");
        } else if (worst_case_ar < cfg->min_annular_ring_mm) {
            dfm_issue_t *iss = &issues[found++];
            iss->type = DEFECT_ANNULAR_TANGENCY;
            iss->severity = SEV_WARNING;
            iss->location = vias[i].center;
            snprintf(iss->description, sizeof(iss->description),
                     "Поясок менший за вимоги IPC Class 3: залишок %.3f мм (норма %.2f мм)",
                     worst_case_ar, cfg->min_annular_ring_mm);
            snprintf(iss->recommendation, sizeof(iss->recommendation),
                     "Збільште розмір майданчика на 0.05-0.10 мм");
        }
    }
    return found;
}

int audit_copper_to_edge(const via_element_t *vias, size_t via_count,
                         const outline_segment_t *outline, size_t seg_count,
                         const dfm_rules_config_t *cfg, dfm_issue_t *issues, int max_issues) {
    int found = 0;
    for (size_t i = 0; i < via_count; i++) {
        double min_dist = 1e9;
        for (size_t s = 0; s < seg_count; s++) {
            double d = point_to_segment_distance(vias[i].center, outline[s]);
            if (d < min_dist) min_dist = d;
        }

        double copper_clearance = min_dist - (vias[i].pad_dia_mm / 2.0);
        if (copper_clearance < cfg->min_copper_to_edge_mm) {
            if (found >= max_issues) return found;
            dfm_issue_t *iss = &issues[found++];
            iss->type = DEFECT_COPPER_TO_EDGE;
            iss->severity = SEV_CRITICAL;
            iss->location = vias[i].center;
            snprintf(iss->description, sizeof(iss->description),
                     "Мідь занадто близько до контуру: зазор %.3f мм (норма >= %.2f мм)",
                     copper_clearance, cfg->min_copper_to_edge_mm);
            snprintf(iss->recommendation, sizeof(iss->recommendation),
                     "Зсуньте елемент усередину плати на >= %.3f мм від лінії фрезерування",
                     cfg->min_copper_to_edge_mm - copper_clearance);
        }
    }
    return found;
}

void output_console_report(const dfm_issue_t *issues, int count) {
    printf("=================================================================\n");
    printf("                  РЕЗУЛЬТАТИ АУДИТУ ТЕХНОЛОГІЧНОСТІ DFM          \n");
    printf("=================================================================\n");

    if (count == 0) {
        printf(" [OK] Топологія відповідає всім заданим технологічним нормам.\n");
        printf("=================================================================\n");
        return;
    }

    int crit_count = 0;
    int warn_count = 0;

    for (int i = 0; i < count; i++) {
        const char *tag = "INFO";
        if (issues[i].severity == SEV_CRITICAL) {
            tag = "CRITICAL";
            crit_count++;
        } else if (issues[i].severity == SEV_WARNING) {
            tag = "WARNING";
            warn_count++;
        }

        printf("[%s] Порушення #%d у точці (X: %.2f, Y: %.2f)\n",
               tag, i + 1, issues[i].location.x, issues[i].location.y);
        printf("  Суть:  %s\n", issues[i].description);
        printf("  Усунення: %s\n\n", issues[i].recommendation);
    }

    printf("-----------------------------------------------------------------\n");
    printf("Всього знайдено: %d критичних помилок, %d попереджень надійності.\n",
           crit_count, warn_count);
    printf("=================================================================\n");
}

int main(void) {
    dfm_rules_config_t config = {
        .min_trace_width_mm = 0.10,
        .min_trace_clearance_mm = 0.10,
        .min_mask_sliver_mm = 0.09,
        .min_annular_ring_mm = 0.05,
        .min_copper_to_edge_mm = 0.30,
        .max_acute_angle_deg = 85.0,
        .drill_runout_tolerance_mm = 0.04,
        .drill_plating_allowance_mm = 0.10
    };

    trace_segment_t sample_traces[] = {
        {{12.0, 15.0}, {25.0, 25.0}, 0.15, "NET_SPI_MOSI"},
        {{25.0, 25.0}, {28.0, 16.0}, 0.15, "NET_SPI_MOSI"}
    };

    via_element_t sample_vias[] = {
        {{30.0, 40.0}, 0.45, 0.30, "NET_VDD_IO"},
        {{49.85, 25.0}, 0.50, 0.30, "NET_GND"}
    };

    outline_segment_t sample_outline[] = {
        {{0.0, 0.0}, {50.0, 0.0}},
        {{50.0, 0.0}, {50.0, 50.0}},
        {{50.0, 50.0}, {0.0, 50.0}},
        {{0.0, 50.0}, {0.0, 0.0}}
    };

    dfm_issue_t issues_buffer[32];
    int issue_count = 0;

    issue_count += audit_acid_traps(sample_traces, sizeof(sample_traces)/sizeof(sample_traces[0]),
                                    &config, issues_buffer + issue_count, 32 - issue_count);
    issue_count += audit_annular_rings(sample_vias, sizeof(sample_vias)/sizeof(sample_vias[0]),
                                      &config, issues_buffer + issue_count, 32 - issue_count);
    issue_count += audit_copper_to_edge(sample_vias, sizeof(sample_vias)/sizeof(sample_vias[0]),
                                       sample_outline, sizeof(sample_outline)/sizeof(sample_outline[0]),
                                       &config, issues_buffer + issue_count, 32 - issue_count);

    output_console_report(issues_buffer, issue_count);
    return 0;
}
```
```cpp
/*
 * dfm_parser.cpp — Об'єктно-орієнтований рушій DFM-аудиту друкованих плат (C++20).
 */

#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <cmath>
#include <numbers>
#include <expected>
#include <iomanip>
#include <algorithm>

namespace dfm {

enum class Severity : uint8_t {
    Info,
    Warning,
    Critical
};

enum class DefectCategory : uint8_t {
    AcidTrap,
    MaskSliver,
    AnnularBreakout,
    AnnularTangency,
    CopperToEdge
};

struct Point2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] double distance_to(const Point2D& other) const noexcept {
        return std::hypot(x - other.x, y - other.y);
    }
};

struct TraceSegment {
    Point2D start;
    Point2D end;
    double width_mm{0.15};
    std::string net_name;
};

struct ViaElement {
    Point2D center;
    double pad_diameter_mm{0.60};
    double finished_hole_mm{0.30};
    std::string net_name;
};

struct OutlineSegment {
    Point2D p1;
    Point2D p2;
};

struct AuditRules {
    double min_trace_width_mm{0.10};
    double min_trace_clearance_mm{0.10};
    double min_mask_sliver_mm{0.09};
    double min_annular_ring_mm{0.05};
    double min_copper_to_edge_mm{0.30};
    double max_acute_angle_deg{85.0};
    double drill_runout_tolerance_mm{0.04};
    double drill_plating_allowance_mm{0.10};
};

struct DefectRecord {
    DefectCategory category;
    Severity severity;
    Point2D position;
    std::string description;
    std::string recommendation;
};

class DfmEngine {
public:
    explicit DfmEngine(AuditRules rules) : rules_(std::move(rules)) {}

    [[nodiscard]] std::vector<DefectRecord> execute_audit(
        std::span<const TraceSegment> traces,
        std::span<const ViaElement> vias,
        std::span<const OutlineSegment> outline) const
    {
        std::vector<DefectRecord> report;
        inspect_acid_traps(traces, report);
        inspect_annular_rings(vias, report);
        inspect_copper_to_edge(vias, outline, report);
        return report;
    }

private:
    AuditRules rules_;

    static double vector_angle_deg(Point2D v1, Point2D v2) noexcept {
        const double l1 = std::hypot(v1.x, v1.y);
        const double l2 = std::hypot(v2.x, v2.y);
        if (l1 < 1e-6 || l2 < 1e-6) return 180.0;

        const double dot = v1.x * v2.x + v1.y * v2.y;
        const double cos_val = std::clamp(dot / (l1 * l2), -1.0, 1.0);
        return std::acos(cos_val) * (180.0 / std::numbers::pi);
    }

    static double distance_to_segment(Point2D pt, const OutlineSegment& seg) noexcept {
        const double dx = seg.p2.x - seg.p1.x;
        const double dy = seg.p2.y - seg.p1.y;
        const double len_sq = dx * dx + dy * dy;

        if (len_sq < 1e-9) {
            return pt.distance_to(seg.p1);
        }

        const double t = std::clamp(
            ((pt.x - seg.p1.x) * dx + (pt.y - seg.p1.y) * dy) / len_sq,
            0.0, 1.0
        );

        const Point2D nearest_point{seg.p1.x + t * dx, seg.p1.y + t * dy};
        return pt.distance_to(nearest_point);
    }

    void inspect_acid_traps(std::span<const TraceSegment> traces, std::vector<DefectRecord>& report) const {
        for (size_t i = 0; i < traces.size(); ++i) {
            for (size_t j = i + 1; j < traces.size(); ++j) {
                bool is_joined = false;
                Point2D vertex{};
                Point2D v1{}, v2{};

                if (traces[i].start.distance_to(traces[j].start) < 1e-4) {
                    is_joined = true;
                    vertex = traces[i].start;
                    v1 = {traces[i].end.x - vertex.x, traces[i].end.y - vertex.y};
                    v2 = {traces[j].end.x - vertex.x, traces[j].end.y - vertex.y};
                } else if (traces[i].end.distance_to(traces[j].start) < 1e-4) {
                    is_joined = true;
                    vertex = traces[i].end;
                    v1 = {traces[i].start.x - vertex.x, traces[i].start.y - vertex.y};
                    v2 = {traces[j].end.x - vertex.x, traces[j].end.y - vertex.y};
                } else if (traces[i].end.distance_to(traces[j].end) < 1e-4) {
                    is_joined = true;
                    vertex = traces[i].end;
                    v1 = {traces[i].start.x - vertex.x, traces[i].start.y - vertex.y};
                    v2 = {traces[j].end.x - vertex.x, traces[j].end.y - vertex.y};
                }

                if (is_joined) {
                    const double angle = vector_angle_deg(v1, v2);
                    if (angle < rules_.max_acute_angle_deg) {
                        report.push_back(DefectRecord{
                            .category = DefectCategory::AcidTrap,
                            .severity = Severity::Warning,
                            .position = vertex,
                            .description = "Гострий кут сходження доріжок " + std::to_string(angle) +
                                           " deg у колі " + traces[i].net_name,
                            .recommendation = "Застосуйте поворот на 45 deg або додайте скруглення"
                        });
                    }
                }
            }
        }
    }

    void inspect_annular_rings(std::span<const ViaElement> vias, std::vector<DefectRecord>& report) const {
        for (const auto& via : vias) {
            const double tool_size = via.finished_hole_mm + rules_.drill_plating_allowance_mm;
            const double nominal_ar = (via.pad_diameter_mm - tool_size) / 2.0;
            const double worst_case_ar = nominal_ar - rules_.drill_runout_tolerance_mm;

            if (worst_case_ar < 0.0) {
                report.push_back(DefectRecord{
                    .category = DefectCategory::AnnularBreakout,
                    .severity = Severity::Critical,
                    .position = via.center,
                    .description = "Критичний зрив пояска (Breakout) переходу " + via.net_name +
                                   ": дефіцит " + std::to_string(-worst_case_ar) + " мм",
                    .recommendation = "Збільште розмір контактного майданчика або додайте Teardrop"
                });
            } else if (worst_case_ar < rules_.min_annular_ring_mm) {
                report.push_back(DefectRecord{
                    .category = DefectCategory::AnnularTangency,
                    .severity = Severity::Warning,
                    .position = via.center,
                    .description = "Поясок переходу " + via.net_name +
                                   " менший за норму IPC Class 3 (" + std::to_string(worst_case_ar) + " мм)",
                    .recommendation = "Збільште діаметр майданчика на 0.05 мм"
                });
            }
        }
    }

    void inspect_copper_to_edge(
        std::span<const ViaElement> vias,
        std::span<const OutlineSegment> outline,
        std::vector<DefectRecord>& report) const
    {
        for (const auto& via : vias) {
            double min_edge_dist = 1e9;
            for (const auto& seg : outline) {
                min_edge_dist = std::min(min_edge_dist, distance_to_segment(via.center, seg));
            }

            const double net_clearance = min_edge_dist - (via.pad_diameter_mm / 2.0);
            if (net_clearance < rules_.min_copper_to_edge_mm) {
                report.push_back(DefectRecord{
                    .category = DefectCategory::CopperToEdge,
                    .severity = Severity::Critical,
                    .position = via.center,
                    .description = "Неприпустимо малий відступ міді до контуру плати: " +
                                   std::to_string(net_clearance) + " мм",
                    .recommendation = "Зсуньте елемент усередину плати на безпечну відстань >= 0.30 мм"
                });
            }
        }
    }
};

} // namespace dfm

int main() {
    dfm::AuditRules rules{
        .min_trace_width_mm = 0.10,
        .min_trace_clearance_mm = 0.10,
        .min_mask_sliver_mm = 0.09,
        .min_annular_ring_mm = 0.05,
        .min_copper_to_edge_mm = 0.30,
        .max_acute_angle_deg = 85.0,
        .drill_runout_tolerance_mm = 0.04,
        .drill_plating_allowance_mm = 0.10
    };

    dfm::DfmEngine auditor(rules);

    std::vector<dfm::TraceSegment> traces{
        {{12.0, 15.0}, {25.0, 25.0}, 0.15, "NET_SPI_MOSI"},
        {{25.0, 25.0}, {28.0, 16.0}, 0.15, "NET_SPI_MOSI"}
    };

    std::vector<dfm::ViaElement> vias{
        {{30.0, 40.0}, 0.45, 0.30, "NET_VDD_IO"},
        {{49.85, 25.0}, 0.50, 0.30, "NET_GND"}
    };

    std::vector<dfm::OutlineSegment> outline{
        {{0.0, 0.0}, {50.0, 0.0}},
        {{50.0, 0.0}, {50.0, 50.0}},
        {{50.0, 50.0}, {0.0, 50.0}},
        {{0.0, 50.0}, {0.0, 0.0}}
    };

    const auto findings = auditor.execute_audit(traces, vias, outline);

    std::cout << "=================================================================\n";
    std::cout << "             ЗВІТ АУДИТУ DFM (C++20 ENGINE)                      \n";
    std::cout << "=================================================================\n";

    for (size_t idx = 0; idx < findings.size(); ++idx) {
        const auto& item = findings[idx];
        std::string_view tag = (item.severity == dfm::Severity::Critical) ? "CRITICAL" : "WARNING";
        std::cout << "[" << tag << "] Порушення #" << (idx + 1)
                  << " у координаті (X: " << std::fixed << std::setprecision(2)
                  << item.position.x << ", Y: " << item.position.y << ")\n";
        std::cout << "  Опис: " << item.description << "\n";
        std::cout << "  Дія:  " << item.recommendation << "\n\n";
    }

    std::cout << "=================================================================\n";
    return 0;
}
```
:::

## Інтеграція в CI/CD та Pre-commit хуки

Автоматизована перевірка топологічних норм розгортається у конвеєрі розробки як консольний крок валідації:

1. **Генерація вихідних герберів через командний рядок CAD:**
   Утиліта командного рядка `kicad-cli` виконує експорт усіх шарів плати без відкриття графічного інтерфейсу:
   ```bash
   kicad-cli pcb export gerbers -o build/gerber/ my_board.kicad_pcb
   kicad-cli pcb export drill -o build/gerber/ my_board.kicad_pcb
   ```
2. **Запуск геометричного аналізатора DFM:**
   Бінарний файл `dfm_auditor` зчитує згенеровані файли і формує структурований звіт у форматі JSON або SARIF (Static Analysis Results Interchange Format):
   ```bash
   ./dfm_auditor --input build/gerber/ --rules standard_ipc_class3.json --json report.json
   ```
3. **Блокування некоректного коміту:**
   Утиліта повертає код виходу `EXIT_FAILURE` (`1`), якщо виявлено дефекти рівня `CRITICAL` (прориви поясів, замикання на контур або пастки кислоти). У конвеєрі GitHub Actions або GitLab CI це зупиняє збірку й блокує злиття гілки до усунення помилок інженером-розробником.

## Формат звіту SARIF для інтеграції з IDE

Сучасні середовища розробки (VS Code, CLion, Neovim) підтримують відображення помилок безпосередньо над графічним редактором топології через стандартний формат SARIF. Утиліта формує файл `dfm_report.sarif`, де кожне порушення містить точні координати, фізичний шар плати, ступінь критичності та посилання на відповідний пункт стандарту IPC:

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "dfm_auditor",
          "version": "1.2.0",
          "rules": [
            {
              "id": "DFM001",
              "name": "AnnularRingBreakout",
              "shortDescription": { "text": "Критичний розрив пояска металізації отвору" }
            },
            {
              "id": "DFM002",
              "name": "AcidTrapAcuteAngle",
              "shortDescription": { "text": "Пастка кислоти в куті сходження трас" }
            }
          ]
        }
      },
      "results": [
        {
          "ruleId": "DFM001",
          "level": "error",
          "message": { "text": "Розрахунковий залишковий поясок менший за 0 мм через зсув свердла 0.04 мм." },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": { "uri": "gerber/copper_top.gbr" },
                "region": { "startLine": 142, "startColumn": 1 }
              }
            }
          ]
        }
      ]
    }
  ]
}
```

Такий формат дозволяє переглядати зауваження DFM паралельно з редагуванням топології, що усуває потребу в тривалому листуванні з технологами фабрики та скорочує час виходу готового виробу на виробничий конвеєр.
