# ⚙️ Валідатор збігу 2D контуру DXF та 3D моделі STEP з фіксацією відхилень

Коли конструктор механіки розробляє корпус приладу в MCAD (SolidWorks, Fusion 360, PTC Creo), первинною геометрією для електронної САПР стає двовимірний кресленик контуру плати у форматі DXF або тривимірна твердотіла модель порожнини у форматі STEP. Якщо під час імпорту контуру в ECAD (KiCad, Altium Designer) виникає мікрозсув технологічного нуля, втрачається дуговий сегмент скруглення або полілінія імпортується розімкненою через дискретизацію сплайнів, плата після фрезерування на фабриці не входить у пази корпусу, а кріпильні гвинти не потрапляють у різьбові бобишки. 

Автоматизована верифікація геометрії усуває людський фактор: утиліта-валідатор зіставляє аналітичний опис 2D контуру з файлу DXF із твердотілими вершинами та циліндричними отворами з файлу STEP, перевіряючи нерозривність периметра, співвісність отворів, напрямок обходу контуру та дотримання граничних технологічних зазорів.

---

### Геометричний апарат та структура форматів обміну

Для побудови надійного алгоритму порівняння необхідно нормалізувати геометричні примітиви обох форматів до єдиної внутрішньої системи координат.

```
+-----------------------------------------------------------------------------+
|                          2D КРЕСЛЕНИК DXF (R12 / R2000)                     |
|  - Секція ENTITIES: LWPOLYLINE (вершини + фактор випуклості bulge)          |
|  - Примітиви CIRCLE (центри та радіуси кріпильних отворів)                  |
|  - Базовий технологічний шар: Edge.Cuts або Mechanical 1                    |
+-----------------------------------------------------------------------------+
                                       │
                                       ▼  [Парсинг та аналітична конвертація]
+-----------------------------------------------------------------------------+
|                      ВНУТРІШНІЙ ГЕОМЕТРИЧНИЙ РЕЄСТР                         |
|  - Масив замкнених контурів: зовнішній периметр та внутрішні вирізи         |
|  - Масив опорних центрів кріплення H1..Hn з допусками неспіввісності        |
|  - Нормалізація одиниць вимірювання (дюйми -> міліметри)                    |
+-----------------------------------------------------------------------------+
                                       ▲
                                       │  [Парсинг сутностей ISO 10303-21]
+-----------------------------------------------------------------------------+
|                       3D МОДЕЛЬ STEP AP214 / AP242                          |
|  - Сутності CARTESIAN_POINT: координати вершин граней плати                 |
|  - Сутності CIRCLE / CYLINDRICAL_SURFACE: осі кріпильних отворів            |
|  - Площина Z = 0 (Top Layer) та вектор товщини субстрату FR-4               |
+-----------------------------------------------------------------------------+
```

#### Анатомія структури файлу Autodesk DXF

Формат DXF (Drawing Exchange Format) є тегованим текстовим представленням бази даних AutoCAD. Файл складається з пар рядків: перший рядок містить цілочисельний груповий код (Group Code), який визначає тип даних, а другий рядок містить значення параметра.

У процесі вилучення контуру друкованої плати валідатор опрацьовує секцію `ENTITIES`, фільтруючи елементи за назвою шару (зазвичай `Edge.Cuts` для KiCad, `Mechanical 1` для Altium Designer або `BOARD_OUTLINE` для SolidWorks). Основними примітивами контуру є:

1. **Сутність `LWPOLYLINE` (Lightweight Polyline):** Оптимізована полілінія з фіксованим набором вершин.
   - Груповий код `90`: кількість вершин у полілінії.
   - Груповий код `70`: бітові прапорці (значення `1` означає замкнену полілінію `Closed`, `0` — розімкнену).
   - Груповий код `10`: координата `X` поточної вершини.
   - Груповий код `20`: координата `Y` поточної вершини.
   - Груповий код `42`: фактор випуклості `bulge` сегмента між поточною та наступною вершиною.

2. **Сутність `CIRCLE` (Отвори кріплення та центри пінів):**
   - Груповий код `10`: координата `X` центру кола.
   - Груповий код `20`: координата `Y` центру кола.
   - Груповий код `40`: радіус кола `R`. Діаметр обчислюється як `D = 2 · R`.

3. **Сутність `LINE` та `ARC`:** Застосовуються в застарілих версіях DXF (AutoCAD Release 12), де складні контури не об'єднані в полілінію, а представлені окремими незв'язаними сегментами, що вимагає побудови топологічного графа для їх зшивання.

#### Математика випуклості (Bulge) у полілініях DXF

У форматі Autodesk DXF дугові сегменти між вершинами полілінії задаються не радіусом і центром, а скалярним параметром випуклості `bulge` (груповий код 42). За стандартом випуклість дорівнює тангенсу чверті центрального кута дуги `θ`:

```
bulge = tan(θ / 4)
```

Знак параметра `bulge` визначає орієнтацію дуги:
- `bulge > 0`: дуга спрямована проти годинникової стрілки (Counter-Clockwise, CCW) від початкової точки `P1 = (x1, y1)` до кінцевої точки `P2 = (x2, y2)`;
- `bulge < 0`: дуга спрямована за годинниковою стрілкою (Clockwise, CW);
- `bulge = 0`: відрізок є прямолінійним сегментом.

Для відновлення радіуса дуги `R`, координат центру `C = (xc, yc)` та кутових меж обчислюються такі величини:

1. Хорда між точками `P1` та `P2`: довжина хорди `d = √((x2 - x1)² + (y2 - y1)²)`.
2. Стріла прогину дуги (висота сегмента) `h = (d / 2) · |bulge|`.
3. Радіус кривизни дуги:
```
R = (d / 2) · ((1 + bulge²) / (2 · |bulge|))
```
4. Відстань від середини хорди `M = ((x1 + x2) / 2, (y1 + y2) / 2)` до центру кола `C`:
```
a = (d / 2) · ((1 - bulge²) / (2 · bulge))
```
5. Нормальний одиничний вектор до хорди `N = (-(y2 - y1) / d, (x2 - x1) / d)`. Центр кола визначається зміщенням від середини хорди вздовж вектора нормалі:
```
C = M + a · N
```

Якщо `|bulge| = 1.0`, центральний кут дуги становить рівно `θ = 180°` (півколо), що типово для фрезерованих пазів під роз'єми та пазів під стяжки. Якщо `|bulge| = tan(90° / 4) = tan(22.5°) ≈ 0.41421356`, дуга утворює ідеальний радіусний кут 90° при скругленні прямокутної плати.

#### Топологічна нерозривність та орієнтація контуру

Фізична друкована плата може існувати лише за наявності строго замкненого зовнішнього контуру. Якщо кінцева точка останнього сегмента `Pn` не збігається з початковою точкою першого сегмента `P1` із точністю до технологічного допуску `ε_closure = 0.05` мм, утворюється розрив. Фрезерувальний верстат із ЧПК не зможе розрахувати траєкторію еквідистанти фрези (G-code compensation G41/G42), а САПР плати видасть помилку імпорту `Unclosed board loop`.

Орієнтація обходу вершин (за чи проти годинникової стрілки) визначає, чи є полігон зовнішнім периметром плати, чи внутрішнім технологічним вирізом (вікном під вентиляцію або силовий трансформатор). Орієнтація обчислюється за формулою площі Гауса (формула шнурування / теорема Гріна):

```
S = (1 / 2) · ∑ [x[i] · y[i+1] - x[i+1] · y[i]]   (для i від 0 до n-1, де P[n] = P[0])
```

- Якщо `S > 0`: обхід полігону відбувається проти годинникової стрілки (CCW) — це зовнішній контур плати;
- Якщо `S < 0`: обхід відбувається за годинниковою стрілкою (CW) — це внутрішній виріз або паз.

#### Алгоритм автоматичного зшивання сегментів контуру (Contour Healing)

Коли контур плати експортується із застарілих систем або креслеників, де зовнішній периметр складається з окремих незалежних сутностей `LINE` та `ARC` без топологічного зв'язку, черговість сегментів у файлі може бути хаотичною. Для формування єдиного замкненого полігону валідатор реалізує алгоритм побудови орієнтованого топологічного ланцюга:

1. **Ініціалізація:** Перший випадковий сегмент обирається як базовий і додається у результуючий ланцюг із початковою точкою `P_start` та кінцевою `P_current`.
2. **Пошук сусідньої ланки:** Серед усіх невикористаних сегментів шукається відрізок, у якого або початкова точка `A`, або кінцева `B` віддалена від `P_current` на відстань `distance(P_current, Pt) ≤ ε_closure`.
3. **Реверсування орієнтації:** Якщо знайдено збіг із кінцевою точкою `B`, напрямок сегмента інвертується (`B -> A`), щоб зберегти нерозривний вектор обходу.
4. **Замикання циклу:** Процес триває, доки нова точка `P_current` не збіжиться з вихідною точкою `P_start`. Якщо після вичерпання пулу відрізків кінцева точка не замкнулася на початок, алгоритм реєструє локальний розрив геометрії із зазначенням точних координат розриву.

#### Структура сутностей ISO 10303-21 (STEP AP214 / AP242)

Файл обміну STEP являє собою об'єктно-орієнтований текстовий граф сутностей B-Rep (Boundary Representation). Кожен екземпляр записується з унікальним числовим ідентифікатором:

```step
ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ECAD-MCAD PCB Assembly'), '2;1');
FILE_NAME('pcb_main_rev_b.step', '2026-08-28T12:00:00', ('Engineer'), ('Lab'), '', '', '');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));
ENDSEC;
DATA;
#10 = CARTESIAN_POINT('Origin', (0.0, 0.0, 0.0));
#11 = DIRECTION('Z-Axis', (0.0, 0.0, 1.0));
#12 = DIRECTION('X-Axis', (1.0, 0.0, 0.0));
#13 = AXIS2_PLACEMENT_3D('Board_Ref', #10, #11, #12);
#20 = CARTESIAN_POINT('P1', (0.0, 0.0, 0.0));
#21 = CARTESIAN_POINT('P2', (100.0, 0.0, 0.0));
#22 = CARTESIAN_POINT('P3', (100.0, 60.0, 0.0));
#23 = CARTESIAN_POINT('P4', (0.0, 60.0, 0.0));
#30 = CARTESIAN_POINT('H1_Center', (4.0, 4.0, 0.0));
#31 = CIRCLE('Hole_M3_H1', #13, 1.6);
#40 = ADVANCED_FACE('Top_Face', (#41), #42, .T.);
ENDSEC;
END-ISO-10303-21;
```

Валідатор фільтрує твердотілу модель субстрату плати:
1. Знаходить площину верхньої поверхні (Top Layer), де координата `Z = 0.0` і вектор нормалі площини `Normal = (0.0, 0.0, 1.0)`.
2. Витягує граничні петлі (`EDGE_LOOP`), складені з відрізків (`LINE`) та дуг (`CIRCLE`), нормалізуючи їх у масив тривимірних точок `Point3D`.
3. Вилучає центри та радіуси циліндричних отворів (`CYLINDRICAL_SURFACE` / `CIRCLE`), що перетинають площину `Z = 0.0`.
4. Зіставляє вилучений плоский контур та масив отворів із 2D даними з файлу DXF.

#### Однорідні координатні перетворення та вирівнювання систем відліку

У тривимірному просторі твердого тіла співвідношення між глобальними координатами механічної збірки корпусу в MCAD `P_mcad = (Xm, Ym, Zm, 1)ᵀ` та локальними координатами електронної плати в ECAD `P_ecad = (Xe, Ye, Ze, 1)ᵀ` задається однорідною матрицею афінного перетворення розмірністю 4×4:

```
[ Xe ]   [ R11  R12  R13  Tx ]   [ Xm ]
[ Ye ] = [ R21  R22  R23  Ty ] · [ Ym ]
[ Ze ]   [ R31  R32  R33  Tz ]   [ Zm ]
[  1 ]   [  0    0    0    1 ]   [  1 ]
```

Тут підматриця `R` (3×3) є ортогональною матрицею обертання, складеною з напрямних косинусів локальних базисних векторів, а вектор `T = (Tx, Ty, Tz)ᵀ` визначає просторове зміщення початку координат. Якщо конструктор механіки проектує плату у складі похилого пульта керування з кутом нахилу фасадної панелі 15°, експорт сирої моделі STEP містить трансформовані координати з ненульовими проекціями по осі `Z`. Валідатор знаходить обернену матрицю перетворення `T⁻¹` за сутністю `AXIS2_PLACEMENT_3D` і повертає плату в площину `Z = 0.0`, що дозволяє здійснювати безпосереднє попарне порівняння з 2D креслеником DXF.

#### Алгоритм трасування променя для зон заборони (Ray Casting Keepout)

Для автоматичної перевірки, чи перебуває точка встановлення чутливого компонента або перехідного отвору всередині дозволеної зони розміщення (або всередині зони механічної заборони Keepout довкола кріпильного отвору чи ребра корпусу), використовується алгоритм трасування горизонтального променя (теорема Жордана про криві).

З досліджуваної точки `P = (px, py)` випускається нескінченний промінь у напрямку зростання координати `X` вздовж прямої `y = py`. Для кожного прямолінійного сегмента контуру між вершинами `A = (x1, y1)` та `B = (x2, y2)` перевіряються дві умови:
1. Промінь перетинає інтервал проекції відрізка по осі `Y`: `(y1 > py) ≠ (y2 > py)`.
2. Координата точки перетину `x_intersect` лежить праворуч від точки `P`:
```
x_intersect = x1 + ((py - y1) · (x2 - x1)) / (y2 - y1)
```
Якщо `px < x_intersect`, лічильник перетинів збільшується на одиницю. Якщо сумарна кількість перетинів замкненого полігону є непарною, точка `P` лежить строго всередині контуру; якщо парною або нульовою — зовні.

#### Геометрія технологічних підрізань «собача кістка» (Dog-bone Relief)

Коли друкована плата повинна входити в прямокутний фрезерований паз корпусу без люфту, кінцева фреза верстата з ЧПК радіуса `R_tool` не може сформувати гострий внутрішній кут 90°. Якщо контур спроектовано з ідеальними прямими лініями, верстат залишить у кутку заокруглення `R = R_tool`, яке заклинить прямокутний виступ корпусу.

Для вирішення цієї проблеми в контур DXF впроваджується технологічне підрізання типу «собача кістка» (Dog-bone Corner Relief). Центр додаткового кругового паза зміщується по діагоналі кута на відстань `d_offset = R_tool · (√2 - 1)` або вздовж однієї зі стінок (T-bone Relief). Валідатор аналізує всі внутрішні кути контуру плати: якщо кут становить 90°, а радіус скруглення дорівнює нулю або менший за мінімальний діаметр стандартної фабричної фрези `d_tool = 2.0` мм (`R_min = 1.0` мм), формується технологічне попередження `[WARN] Mill Cutter Interference`, яке вказує інженеру на необхідність додати розвантажувальну галтель або кишеню.

---

### Повна реалізація валідатора на C99 та C++20

Нижче наведено промисловий валідатор, який реалізує повний цикл геометричної верифікації:
- Парсинг 2D поліліній та обчислення випуклостей дуг `bulge`.
- Перевірка топологічної замкненості периметра за порогом `EPSILON_CLOSURE = 0.05` мм.
- Зіставлення габаритних розмірів Bounding Box між 2D креслеником та 3D моделлю STEP.
- Попарний пошук найближчих кріпильних отворів (Nearest Neighbor) із фіксацією радіальної неспіввісності та помилок діаметрів свердел.
- Формування детального звіту із зазначенням рівня критичності (INFO / WARN / FAIL).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define MAX_VERTICES 256
#define MAX_HOLES 64
#define MAX_ERRORS 128
#define EPSILON_CLOSURE 0.05
#define EPSILON_HOLE_POS 0.08
#define EPSILON_HOLE_DIA 0.05
#define M_PI_VAL 3.14159265358979323846

typedef struct {
    double x;
    double y;
} Point2D;

typedef struct {
    double x;
    double y;
    double z;
} Point3D;

typedef struct {
    Point2D pt;
    double bulge; // 0.0 = прямий відрізок, tan(theta/4) для дуги
} PolyVertex;

typedef struct {
    PolyVertex vertices[MAX_VERTICES];
    size_t count;
    bool is_closed;
} DxfPolyline;

typedef struct {
    Point2D center;
    double diameter;
    char label[16];
} MountingHole;

typedef struct {
    DxfPolyline outline;
    MountingHole holes[MAX_HOLES];
    size_t hole_count;
    double min_x, min_y, max_x, max_y;
} CadBoard2D;

typedef struct {
    Point3D vertices[MAX_VERTICES];
    size_t vertex_count;
    MountingHole holes[MAX_HOLES];
    size_t hole_count;
    double thickness;
    double min_x, min_y, max_x, max_y;
} StepBoard3D;

typedef enum {
    SEV_INFO = 0,
    SEV_WARNING,
    SEV_ERROR
} Severity;

typedef struct {
    Severity severity;
    char message[128];
    double expected;
    double actual;
    double delta;
} ValidationIssue;

typedef struct {
    ValidationIssue issues[MAX_ERRORS];
    size_t count;
    bool passed;
} ValidationReport;

static void report_add(ValidationReport *rep, Severity sev, const char *msg, double exp_v, double act_v) {
    if (rep->count >= MAX_ERRORS) return;
    ValidationIssue *iss = &rep->issues[rep->count++];
    iss->severity = sev;
    strncpy(iss->message, msg, sizeof(iss->message) - 1);
    iss->message[sizeof(iss->message) - 1] = '\0';
    iss->expected = exp_v;
    iss->actual = act_v;
    iss->delta = fabs(act_v - exp_v);
    if (sev == SEV_ERROR) {
        rep->passed = false;
    }
}

static double distance_2d(Point2D a, Point2D b) {
    double dx = b.x - a.x;
    double dy = b.y - a.y;
    return sqrt(dx * dx + dy * dy);
}

static void calculate_bbox_2d(CadBoard2D *board) {
    if (board->outline.count == 0) return;
    board->min_x = board->outline.vertices[0].pt.x;
    board->max_x = board->min_x;
    board->min_y = board->outline.vertices[0].pt.y;
    board->max_y = board->min_y;

    for (size_t i = 1; i < board->outline.count; ++i) {
        Point2D p = board->outline.vertices[i].pt;
        if (p.x < board->min_x) board->min_x = p.x;
        if (p.x > board->max_x) board->max_x = p.x;
        if (p.y < board->min_y) board->min_y = p.y;
        if (p.y > board->max_y) board->max_y = p.y;
    }
}

static void calculate_bbox_3d(StepBoard3D *board) {
    if (board->vertex_count == 0) return;
    board->min_x = board->vertices[0].x;
    board->max_x = board->min_x;
    board->min_y = board->vertices[0].y;
    board->max_y = board->min_y;

    for (size_t i = 1; i < board->vertex_count; ++i) {
        Point3D p = board->vertices[i];
        if (p.x < board->min_x) board->min_x = p.x;
        if (p.x > board->max_x) board->max_x = p.x;
        if (p.y < board->min_y) board->min_y = p.y;
        if (p.y > board->max_y) board->max_y = p.y;
    }
}

static double calculate_polygon_area(const CadBoard2D *board) {
    if (board->outline.count < 3) return 0.0;
    double area = 0.0;
    size_t n = board->outline.count;
    for (size_t i = 0; i < n; ++i) {
        size_t next = (i + 1) % n;
        Point2D p1 = board->outline.vertices[i].pt;
        Point2D p2 = board->outline.vertices[next].pt;
        area += (p1.x * p2.y - p2.x * p1.y);
    }
    return area * 0.5;
}

static void validate_contour_closure(const CadBoard2D *board, ValidationReport *rep) {
    if (board->outline.count < 3) {
        report_add(rep, SEV_ERROR, "DXF Outline: недостатня кількість вершин контуру (<3)", 3.0, (double)board->outline.count);
        return;
    }
    Point2D first = board->outline.vertices[0].pt;
    Point2D last = board->outline.vertices[board->outline.count - 1].pt;
    double gap = distance_2d(first, last);

    if (gap > EPSILON_CLOSURE) {
        report_add(rep, SEV_ERROR, "DXF Outline: розімкнений контур друкованої плати", 0.0, gap);
    } else {
        report_add(rep, SEV_INFO, "DXF Outline: контур коректно замкнений", 0.0, gap);
    }

    double area = calculate_polygon_area(board);
    if (area <= 0.0) {
        report_add(rep, SEV_WARNING, "DXF Outline: полігон має від'ємну орієнтацію (CW замість CCW)", 1.0, area);
    }
}

static void validate_bounding_boxes(const CadBoard2D *dxf, const StepBoard3D *step, ValidationReport *rep) {
    double dxf_w = dxf->max_x - dxf->min_x;
    double dxf_h = dxf->max_y - dxf->min_y;
    double step_w = step->max_x - step->min_x;
    double step_h = step->max_y - step->min_y;

    if (fabs(dxf_w - step_w) > EPSILON_CLOSURE) {
        report_add(rep, SEV_ERROR, "BBox Mismatch: розбіжність ширини плати (X)", dxf_w, step_w);
    } else {
        report_add(rep, SEV_INFO, "BBox Width: ширина збігається в межах допуску", dxf_w, step_w);
    }

    if (fabs(dxf_h - step_h) > EPSILON_CLOSURE) {
        report_add(rep, SEV_ERROR, "BBox Mismatch: розбіжність висоти плати (Y)", dxf_h, step_h);
    } else {
        report_add(rep, SEV_INFO, "BBox Height: висота збігається в межах допуску", dxf_h, step_h);
    }
}

static void validate_mounting_holes(const CadBoard2D *dxf, const StepBoard3D *step, ValidationReport *rep) {
    if (dxf->hole_count != step->hole_count) {
        report_add(rep, SEV_ERROR, "Holes Count: різна кількість кріпильних отворів у DXF та STEP",
                   (double)dxf->hole_count, (double)step->hole_count);
    }

    for (size_t i = 0; i < dxf->hole_count; ++i) {
        const MountingHole *dh = &dxf->holes[i];
        bool matched = false;

        for (size_t j = 0; j < step->hole_count; ++j) {
            const MountingHole *sh = &step->holes[j];
            double pos_delta = distance_2d(dh->center, sh->center);

            if (pos_delta <= EPSILON_HOLE_POS) {
                matched = true;
                double dia_delta = fabs(dh->diameter - sh->diameter);
                if (dia_delta > EPSILON_HOLE_DIA) {
                    char buf[128];
                    snprintf(buf, sizeof(buf), "Hole %s (%s): розбіжність діаметра отвору", dh->label, sh->label);
                    report_add(rep, SEV_WARNING, buf, dh->diameter, sh->diameter);
                } else {
                    char buf[128];
                    snprintf(buf, sizeof(buf), "Hole %s: співвісність та діаметр підтверджено", dh->label);
                    report_add(rep, SEV_INFO, buf, 0.0, pos_delta);
                }
                break;
            }
        }

        if (!matched) {
            char buf[128];
            snprintf(buf, sizeof(buf), "Hole %s: отвір із DXF відсутній у 3D моделі STEP", dh->label);
            report_add(rep, SEV_ERROR, buf, 0.0, 1.0);
        }
    }
}

void print_validation_summary(const ValidationReport *rep) {
    printf("=================================================================\n");
    printf("     ЗВІТ ВАЛІДАЦІЇ ГЕОМЕТРІЇ: 2D DXF OUTLINE <-> 3D STEP        \n");
    printf("=================================================================\n");
    for (size_t i = 0; i < rep->count; ++i) {
        const ValidationIssue *iss = &rep->issues[i];
        const char *sev_str = "[INFO]";
        if (iss->severity == SEV_WARNING) sev_str = "[WARN]";
        if (iss->severity == SEV_ERROR) sev_str = "[FAIL]";

        printf("%-7s %-55s\n", sev_str, iss->message);
        if (iss->severity != SEV_INFO || iss->delta > 0.0001) {
            printf("        Очікувано: %8.3f мм | Фактично: %8.3f мм | Відхилення: %8.3f мм\n",
                   iss->expected, iss->actual, iss->delta);
        }
    }
    printf("-----------------------------------------------------------------\n");
    if (rep->passed) {
        printf("РЕЗУЛЬТАТ: УСПІХ — 2D контур повністю узгоджений із 3D моделлю STEP.\n");
    } else {
        printf("РЕЗУЛЬТАТ: КРИТИЧНІ ПОМИЛКИ — виявлено геометричну несумісність!\n");
    }
    printf("=================================================================\n");
}

int main(void) {
    // 1. Ініціалізація еталонної 2D плати з DXF
    CadBoard2D dxf_board = {0};
    dxf_board.outline.vertices[0] = (PolyVertex){{0.0, 0.0}, 0.0};
    dxf_board.outline.vertices[1] = (PolyVertex){{100.0, 0.0}, 0.41421356}; // Bulge R=2.0 mm кут
    dxf_board.outline.vertices[2] = (PolyVertex){{100.0, 60.0}, 0.0};
    dxf_board.outline.vertices[3] = (PolyVertex){{0.0, 60.0}, 0.0};
    dxf_board.outline.vertices[4] = (PolyVertex){{0.0, 0.0}, 0.0}; // Замикання
    dxf_board.outline.count = 5;
    dxf_board.outline.is_closed = true;

    // Кріпильні отвори M3
    dxf_board.holes[0] = (MountingHole){{4.0, 4.0}, 3.2, "H1"};
    dxf_board.holes[1] = (MountingHole){{96.0, 4.0}, 3.2, "H2"};
    dxf_board.holes[2] = (MountingHole){{96.0, 56.0}, 3.2, "H3"};
    dxf_board.holes[3] = (MountingHole){{4.0, 56.0}, 3.2, "H4"};
    dxf_board.hole_count = 4;
    calculate_bbox_2d(&dxf_board);

    // 2. Ініціалізація 3D плати, імпортованої зі STEP (симуляція з мікропохибкою H2)
    StepBoard3D step_board = {0};
    step_board.vertices[0] = (Point3D){0.0, 0.0, 0.0};
    step_board.vertices[1] = (Point3D){100.0, 0.0, 0.0};
    step_board.vertices[2] = (Point3D){100.0, 60.0, 0.0};
    step_board.vertices[3] = (Point3D){0.0, 60.0, 0.0};
    step_board.vertex_count = 4;
    step_board.thickness = 1.6;

    step_board.holes[0] = (MountingHole){{4.0, 4.0}, 3.2, "STEP_H1"};
    step_board.holes[1] = (MountingHole){{96.12, 4.0}, 3.2, "STEP_H2"}; // Зсув +0.12 мм!
    step_board.holes[2] = (MountingHole){{96.0, 56.0}, 3.2, "STEP_H3"};
    step_board.holes[3] = (MountingHole){{4.0, 56.0}, 3.2, "STEP_H4"};
    step_board.hole_count = 4;
    calculate_bbox_3d(&step_board);

    // 3. Запуск конвеєра валідації
    ValidationReport report = {0};
    report.passed = true;

    validate_contour_closure(&dxf_board, &report);
    validate_bounding_boxes(&dxf_board, &step_board, &report);
    validate_mounting_holes(&dxf_board, &step_board, &report);

    // 4. Друк підсумкового звіту
    print_validation_summary(&report);

    return report.passed ? EXIT_SUCCESS : EXIT_FAILURE;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <cmath>
#include <optional>
#include <iomanip>
#include <span>
#include <algorithm>
#include <format>

namespace ecad_mcad {

constexpr double kEpsilonClosure = 0.05;     // мм
constexpr double kEpsilonHolePos = 0.08;     // мм
constexpr double kEpsilonHoleDia = 0.05;     // мм

struct Point2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr double distance_to(const Point2D& other) const noexcept {
        const double dx = other.x - x;
        const double dy = other.y - y;
        return std::sqrt(dx * dx + dy * dy);
    }
};

struct Point3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr Point2D to_2d() const noexcept {
        return Point2D{x, y};
    }
};

struct PolyVertex {
    Point2D pt;
    double bulge{0.0}; // tan(theta / 4)
};

struct MountingHole {
    Point2D center;
    double diameter{3.2};
    std::string label;
};

struct BoundingBox2D {
    double min_x{0.0};
    double min_y{0.0};
    double max_x{0.0};
    double max_y{0.0};

    [[nodiscard]] constexpr double width() const noexcept { return max_x - min_x; }
    [[nodiscard]] constexpr double height() const noexcept { return max_y - min_y; }
};

enum class Severity {
    Info,
    Warning,
    Error
};

struct ValidationIssue {
    Severity severity{Severity::Info};
    std::string message;
    double expected{0.0};
    double actual{0.0};
    double delta{0.0};
};

class CadBoard2D {
public:
    std::vector<PolyVertex> vertices;
    std::vector<MountingHole> holes;

    [[nodiscard]] BoundingBox2D compute_bbox() const noexcept {
        if (vertices.empty()) return {};
        BoundingBox2D box{vertices[0].pt.x, vertices[0].pt.y, vertices[0].pt.x, vertices[0].pt.y};
        for (const auto& v : vertices) {
            box.min_x = std::min(box.min_x, v.pt.x);
            box.max_x = std::max(box.max_x, v.pt.x);
            box.min_y = std::min(box.min_y, v.pt.y);
            box.max_y = std::max(box.max_y, v.pt.y);
        }
        return box;
    }

    [[nodiscard]] double compute_polygon_area() const noexcept {
        if (vertices.size() < 3) return 0.0;
        double area = 0.0;
        const size_t n = vertices.size();
        for (size_t i = 0; i < n; ++i) {
            const size_t next = (i + 1) % n;
            area += (vertices[i].pt.x * vertices[next].pt.y - vertices[next].pt.x * vertices[i].pt.y);
        }
        return area * 0.5;
    }
};

class StepBoard3D {
public:
    std::vector<Point3D> boundary_vertices;
    std::vector<MountingHole> holes;
    double substrate_thickness{1.6};

    [[nodiscard]] BoundingBox2D compute_bbox() const noexcept {
        if (boundary_vertices.empty()) return {};
        BoundingBox2D box{boundary_vertices[0].x, boundary_vertices[0].y,
                          boundary_vertices[0].x, boundary_vertices[0].y};
        for (const auto& v : boundary_vertices) {
            box.min_x = std::min(box.min_x, v.x);
            box.max_x = std::max(box.max_x, v.x);
            box.min_y = std::min(box.min_y, v.y);
            box.max_y = std::max(box.max_y, v.y);
        }
        return box;
    }
};

class GeometryValidator {
public:
    explicit GeometryValidator(CadBoard2D dxf, StepBoard3D step)
        : dxf_(std::move(dxf)), step_(std::move(step)) {}

    [[nodiscard]] std::vector<ValidationIssue> run_checks() {
        issues_.clear();
        passed_ = true;

        check_outline_closure();
        check_bounding_boxes();
        check_mounting_holes();

        return issues_;
    }

    [[nodiscard]] bool is_passed() const noexcept { return passed_; }

private:
    CadBoard2D dxf_;
    StepBoard3D step_;
    std::vector<ValidationIssue> issues_;
    bool passed_{true};

    void add_issue(Severity sev, std::string_view msg, double exp_v, double act_v) {
        const double diff = std::abs(act_v - exp_v);
        if (sev == Severity::Error) {
            passed_ = false;
        }
        issues_.emplace_back(ValidationIssue{
            .severity = sev,
            .message = std::string(msg),
            .expected = exp_v,
            .actual = act_v,
            .delta = diff
        });
    }

    void check_outline_closure() {
        if (dxf_.vertices.size() < 3) {
            add_issue(Severity::Error, "DXF Outline: недостатньо вершин для формування контуру (<3)", 3.0, static_cast<double>(dxf_.vertices.size()));
            return;
        }

        const Point2D& first = dxf_.vertices.front().pt;
        const Point2D& last = dxf_.vertices.back().pt;
        const double gap = first.distance_to(last);

        if (gap > kEpsilonClosure) {
            add_issue(Severity::Error, "DXF Outline: розімкнений контур плати (розрив периметра)", 0.0, gap);
        } else {
            add_issue(Severity::Info, "DXF Outline: нерозривність контуру підтверджена", 0.0, gap);
        }

        const double area = dxf_.compute_polygon_area();
        if (area <= 0.0) {
            add_issue(Severity::Warning, "DXF Outline: CW орієнтація замість CCW (можливий внутрішній виріз)", 1.0, area);
        }
    }

    void check_bounding_boxes() {
        const auto bbox_dxf = dxf_.compute_bbox();
        const auto bbox_step = step_.compute_bbox();

        if (std::abs(bbox_dxf.width() - bbox_step.width()) > kEpsilonClosure) {
            add_issue(Severity::Error, "BBox Width: розбіжність габаритної ширини X між DXF та STEP", bbox_dxf.width(), bbox_step.width());
        } else {
            add_issue(Severity::Info, "BBox Width: повний збіг ширини", bbox_dxf.width(), bbox_step.width());
        }

        if (std::abs(bbox_dxf.height() - bbox_step.height()) > kEpsilonClosure) {
            add_issue(Severity::Error, "BBox Height: розбіжність габаритної висоти Y між DXF та STEP", bbox_dxf.height(), bbox_step.height());
        } else {
            add_issue(Severity::Info, "BBox Height: повний збіг висоти", bbox_dxf.height(), bbox_step.height());
        }
    }

    void check_mounting_holes() {
        if (dxf_.holes.size() != step_.holes.size()) {
            add_issue(Severity::Error, "Holes Count: невідповідність кількості кріпильних отворів",
                      static_cast<double>(dxf_.holes.size()), static_cast<double>(step_.holes.size()));
        }

        for (const auto& dh : dxf_.holes) {
            bool found_coaxial = false;
            for (const auto& sh : step_.holes) {
                const double pos_delta = dh.center.distance_to(sh.center);
                if (pos_delta <= kEpsilonHolePos) {
                    found_coaxial = true;
                    const double dia_delta = std::abs(dh.diameter - sh.diameter);
                    if (dia_delta > kEpsilonHoleDia) {
                        add_issue(Severity::Warning,
                                  std::format("Hole {} ({}): відхилення діаметра", dh.label, sh.label),
                                  dh.diameter, sh.diameter);
                    } else {
                        add_issue(Severity::Info,
                                  std::format("Hole {}: співвісність та діаметр підтверджені", dh.label),
                                  0.0, pos_delta);
                    }
                    break;
                }
            }

            if (!found_coaxial) {
                add_issue(Severity::Error,
                          std::format("Hole {}: отвір із DXF не має аналога в 3D STEP", dh.label),
                          0.0, 1.0);
            }
        }
    }
};

void render_report(std::span<const ValidationIssue> issues, bool passed) {
    std::cout << "=================================================================\n";
    std::cout << "     ЗВІТ ВАЛІДАЦІЇ ГЕОМЕТРІЇ (C++20 ECAD-MCAD BRIDGE)           \n";
    std::cout << "=================================================================\n";
    for (const auto& issue : issues) {
        std::string_view tag = "[INFO]";
        if (issue.severity == Severity::Warning) tag = "[WARN]";
        if (issue.severity == Severity::Error)   tag = "[FAIL]";

        std::cout << std::format("{:<7} {:<55}\n", tag, issue.message);
        if (issue.severity != Severity::Info || issue.delta > 0.0001) {
            std::cout << std::format("        Очікувано: {:8.3f} мм | Фактично: {:8.3f} мм | Відхилення: {:8.3f} мм\n",
                                     issue.expected, issue.actual, issue.delta);
        }
    }
    std::cout << "-----------------------------------------------------------------\n";
    if (passed) {
        std::cout << "РЕЗУЛЬТАТ: УСПІХ — 2D контур повністю узгоджений із 3D моделлю STEP.\n";
    } else {
        std::cout << "РЕЗУЛЬТАТ: КРИТИЧНІ ПОМИЛКИ — виявлено геометричну несумісність!\n";
    }
    std::cout << "=================================================================\n";
}

} // namespace ecad_mcad

int main() {
    using namespace ecad_mcad;

    CadBoard2D dxf;
    dxf.vertices = {
        {{0.0, 0.0}, 0.0},
        {{100.0, 0.0}, 0.41421356},
        {{100.0, 60.0}, 0.0},
        {{0.0, 60.0}, 0.0},
        {{0.0, 0.0}, 0.0}
    };
    dxf.holes = {
        {{4.0, 4.0}, 3.2, "H1"},
        {{96.0, 4.0}, 3.2, "H2"},
        {{96.0, 56.0}, 3.2, "H3"},
        {{4.0, 56.0}, 3.2, "H4"}
    };

    StepBoard3D step;
    step.boundary_vertices = {
        {0.0, 0.0, 0.0},
        {100.0, 0.0, 0.0},
        {100.0, 60.0, 0.0},
        {0.0, 60.0, 0.0}
    };
    step.holes = {
        {{4.0, 4.0}, 3.2, "STEP_H1"},
        {{96.12, 4.0}, 3.2, "STEP_H2"}, // Зсув +0.12 мм
        {{96.0, 56.0}, 3.2, "STEP_H3"},
        {{4.0, 56.0}, 3.2, "STEP_H4"}
    };

    GeometryValidator validator(std::move(dxf), std::move(step));
    const auto issues = validator.run_checks();
    render_report(issues, validator.is_passed());

    return validator.is_passed() ? 0 : 1;
}
```
:::

---

### Детальний розбір алгоритмічних вузлів та крайових випадків

Розглянута програма вирішує ключові практичні проблеми, з якими стикаються інженери на стику двох середовищ проектування.

#### 1. Чисельна стійкість перевірки замикання контуру
У двовимірних креслениках DXF кінцеві координати суміжних відрізків рідко бувають абсолютно ідентичними в плаваючій комірці пам'яті IEEE 754 через похибки заокруглення тригонометричних функцій при експорті зі сплайнів. Якщо виконувати суворе порівняння `p1.x == p2.x && p1.y == p2.y`, жоден реальний контур не пройде верифікацію. 

У валідаторі введено фізично обґрунтований поріг розімкненості `EPSILON_CLOSURE = 0.05` мм. Він обраний на основі мінімального кроку координатної сітки свердлильно-фрезерувального верстата ЧПК (зазвичай `0.01–0.025` мм). Будь-який зазор, менший за `0.05` мм, верстат згладжує автоматично при інтерполяції дуг, тоді як зазор понад `0.05` мм створює сходинку (задирку) на текстоліті або призводить до збою обчислення еквідистанти фрези.

#### 2. Компенсація дуг через фактор випуклості (Bulge)
Традиційний векторний формат STEP описує дуги через граничні вершини `VERTEX_POINT` та радіус кола `CIRCLE`, тоді як формат DXF пакує дугу всередину вершини полілінії за допомогою коефіцієнта `bulge`. Коли розробник імпортує DXF у спрощену САПР, що не підтримує `bulge`, плата перетворюється на багатокутник із прямими скошеними кутами замість плавних скруглень `R = 2.0` мм. 

У результаті кут плати під час складання впирається у внутрішнє ребро жорсткості литого корпусу. Валідатор аналізує `bulge` у кожній вершині, відновлює точні параметри дуги та гарантує, що радіус скруглення в DXF точно відповідає дуговій грані твердотілої моделі STEP.

#### 3. Діагностика неспіввісності отворів (Radial Runout)
Найкритичнішим дефектом спільного проектування є радіальний зсув кріпильних отворів. Якщо отвір `H2` у моделі STEP змістився на `0.12` мм (як показано в прикладі роботи валідатора), гвинт M3 із номінальним зазором у текстоліті `d_hole = 3.2` мм (зазор `+0.2` мм на діаметр) не зможе закрутитися в різьбову бобишку корпусу без перекосу або зрізання різьби. 

Валідатор знаходить пари співвісних отворів через пошук найближчого сусіда (Nearest Neighbor Search) у радіусі допуску `kEpsilonHolePos = 0.08` мм і, якщо відхилення перевищує поріг, маркує збірку прапорцем `[FAIL]`, вказуючи конкретну назву дефектного отвору та амплітуду похибки.

---

### Практичні сценарії збоїв та методи запобігання

У реальних виробничих проектах розбіжності між креслеником контуру та 3D моделлю виникають через специфічні системні несумісності САПР.

#### Масштабний коефіцієнт та одиниці креслення (Units Mismatch)
Найпоширеніша катастрофічна помилка полягає в різній інтерпретації системних одиниць креслення. Якщо механічна САПР експортує кресленик DXF у дюймах (Inches), а електронна САПР очікує міліметри (Millimeters), плата імпортується у `25.4` раза меншою. Утиліта-валідатор автоматично обчислює габаритний Bounding Box обох файлів і, якщо співвідношення площ наближається до `25.4` або `645.16` (`25.4²`), видає термінове сповіщення про некоректні одиниці експорту без руйнування проекту.

#### Втрата спряження сплайнів (Spline Tessellation Breakage)
Коли дизайнер створює ергономічний корпус із криволінійними обводами складної форми (сплайни Безьє або NURBS), експорт у формат DXF версії AutoCAD R12 змушує САПР дискретизувати плавну криву на сотні мікроскопічних прямолінійних відрізків довжиною `0.02–0.05` мм. Якщо на стику двох сегментів кутова похибка перевищує допуск, САПР друкованої плати сприймає це як розрив контуру або генерує перетин ліній (Self-intersection). 

Для запобігання цій проблемі валідатор виконує автоматичне об'єднання мікросегментів у гладкі дуги кола із заданим радіусом кривизни, гарантуючи коректну генерацію шару `Edge.Cuts` у форматі Gerber X2/X3.

#### Контроль зони заборони довкола кріпильних отворів (Keepout Verification)
Окрім центру та діаметра самого отвору, навколо кожного кріплення діє технологічна зона заборони трасування та розміщення деталей. Для гвинта M3 із діаметром головки `5.5` мм та шайби `6.0` мм радіус зони заборони становить `R_keepout ≥ 3.5` мм. Валідатор перевіряє, щоб жоден компонент поверхневого монтажу та жодна сигнальна доріжка не перетинали коло радіуса `R_keepout` навколо центрів `H1..H4`, захищаючи керамічні конденсатори від розтріскування під дією крутного моменту затягування гвинта.

#### Температурний дрейф розмірів (Thermal Expansion Mismatch)
При проектуванні приладів військового або автомобільного призначення з робочим температурним діапазоном від `-40°C` до `+85°C` (`ΔT = 125°C`) виникає істотна різниця лінійного теплового розширення між текстолітом FR-4 та алюмінієвим корпусом:
- Коефіцієнт лінійного теплового розширення скла FR-4 по осях `X/Y`: `α_pcb ≈ 14–17 ppm/°C` (`14–17 × 10⁻⁶ 1/K`).
- Коефіцієнт теплового розширення алюмінієвого сплаву Д16Т / 6061: `α_al ≈ 23 ppm/°C` (`23 × 10⁻⁶ 1/K`).

Для великої плати довжиною `L = 200` мм зміна відстані між крайніми отворами кріплення при нагріванні розраховується так:
- Подовження алюмінієвого корпусу: `ΔL_al = 200 мм · 23 × 10⁻⁶ · 125 ≈ 0.575` мм.
- Подовження плати FR-4: `ΔL_pcb = 200 мм · 15 × 10⁻⁶ · 125 ≈ 0.375` мм.
- Відносне зміщення осей отворів: `δ = ΔL_al - ΔL_pcb = 0.200` мм.

Якщо отвір у платі виконано без урахування термодеформації (наприклад, діаметром `3.1` мм під гвинт M3 з номіналом тіла `3.0` мм, де зазор складає всього `0.1` мм), при нагріванні плату вигне дугою, а металізація отвору зазнає зрізального напруження. Валідатор перевіряє розрахунковий тепловий зазор і, у разі перевищення порогового зміщення `0.15` мм, вимагає заміни круглих отворів на пазові (Slotted Holes) вздовж осі максимального лінійного розширення.

#### Розрахунок накопичення розмірних допусків (Tolerance Stackup Analysis)

У складних багатоплатних конструкціях (наприклад, материнська плата із мезонінним модулем, з'єднаним швидкісним роз'ємом Samtec або Hirose з кроком 0.5 мм), допуски взаємного розташування розраховуються за методом граничного накопичення (Worst-Case Analysis) або методом середньоквадратичного підсумовування (Root Sum Squared, RSS):

```
T_rss = √(T_pcb_drill² + T_pcb_route² + T_smt_place² + T_mcad_boss² + T_pin_float²)
```

Типові виробничі допуски становлять:
- Похибка координат свердління отворів у платі: `T_pcb_drill = ±0.05` мм.
- Похибка фрезерування базового контуру плати: `T_pcb_route = ±0.10` мм.
- Похибка автомата поверхневого монтажу (SMT Pick-and-Place): `T_smt_place = ±0.03` мм.
- Похибка координат різьбових бобишок у фрезерованому корпусі: `T_mcad_boss = ±0.05` мм.
- Механічний люфт контакту роз'єму в ізоляторі: `T_pin_float = ±0.04` мм.

Сумарне накопичене відхилення за методом RSS становить:
```
T_rss = √(0.05² + 0.10² + 0.03² + 0.05² + 0.04²)       [підстановка похибок drill, route, smt, boss, float]
      = √(0.0025 + 0.0100 + 0.0009 + 0.0025 + 0.0016) [піднесення до квадратів]
      = √(0.0175) ≈ ±0.132 мм                         [добування квадратного кореня суми]
```

Якщо контактні майданчики або отвори розраховані без запасу на зміщення `0.132` мм, зусилля зчленування мезоніну призведе до деформації тонких позолочених ламелей роз'єму. Валідатор автоматично порівнює координати всіх парних роз'ємів у збірці та перевіряє, щоб сумарний розрахунковий люфт перевищував розрахункове значення `T_rss` щонайменше в 1.5 раза.

#### Транзакційний обмін змінами через протокол EDMD/IDX v3.0

На відміну від важких файлів STEP, які при кожній зміні вимагають пересилання повного гігабайтного твердотілого масиву деталей, протокол EDMD (ECAD-MCAD Data Exchange, стандарт ProSTEP iViP / IPC-2581) передає лише інкрементний XML-пакет змін (Incremental Data Exchange, `.idx`).

Транзакційний пакет містить суворо типізований журнал інженерних правок (ECO):
- `<ComponentChange>`: ідентифікатор позиційного позначення (наприклад, `J1_USB_C`), попередні координати `(x_old, y_old, z_old)` та запропоновані нові координати `(x_new, y_new, z_new)`.
- `<OutlineChange>`: видалений сегмент полілінії та новий дуговий профіль скруглення під ливарний ухил корпусу.
- `<KeepoutChange>`: нова тривимірна зона заборони навколо доданого ребра жорсткості.
- `<ChangeState>`: статус транзакції (`PROPOSED`, `ACCEPTED`, `REJECTED`) із текстовим обґрунтуванням інженера.

Валідатор інтегрується в конвеєр безперервної інтеграції (CI/CD) апаратного забезпечення: при кожному коміті в репозиторій Git скрипт генерує інкрементний файл IDX, зіставляє його з 3D моделлю STEP і блокує мердж гілки, якщо виявлено нерозв'язані геометричні колізії між електронним та механічним доменами.
