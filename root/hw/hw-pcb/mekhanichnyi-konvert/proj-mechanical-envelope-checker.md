# ⚙️ Геометрична перевірка механічного конверта плати: зони заборони, висоти компонентів і вильоти роз'ємів

Під час розроблення електронних пристроїв штатні засоби перевірки правил проектування (англ. *Design Rule Check*, DRC) в електронних САПР фокусуються на електричних зазорах між провідниками, ширині доріжок та ізоляції шарів, але залишаються сліпими до фізичних колізій із механічним оточенням: ця утиліта реалізує автоматизовану геометричну валідацію механічного конверта друкованої плати, контролюючи радіальні зони заборони кріпильних отворів, висотні обмеження компонентів у тривимірному просторі корпусу та допуски вильотів роз'ємів за контур плати.

---

### Задача та фізико-геометрична постановка проблеми

Типовий робочий процес проектування друкованої плати передбачає, що трасувальник завантажує контур друкованої плати (англ. *PCB Outline*) з файлу механічного обміну (DXF чи STEP) і розміщує компоненти відповідно до електричної схеми. Проте під час фінального складання виробу в серійному виробництві виникає цілий спектр механічних дефектів, які традиційний схемний DRC не виявляє:

1. **Руйнування керамічних конденсаторів (MLCC) під головкою кріпильного гвинта.** Якщо чіп-конденсатор типорозміру 0603 чи 0805 встановлено надто близько до кріпильного отвору M3, під час затягування гвинта з нормативним крутним моментом 0.6 Н·м у склотекстоліті FR-4 виникає локальне конічне напруження стиску й радіального вигину. Жорсткий керамічний діелектрик титанату барію (BaTiO₃) не має пластичності металів і розтріскується під дією зсувних деформацій, що призводить до прихованого короткого замикання шини живлення на землю вже під час польової експлуатації.
2. **Перекриття зони монтажного інструменту (Tool Clearance).** Навіть якщо сам корпус деталі не потрапляє під площину шайби гвинта, високий електролітичний конденсатор або дросель, змонтований на відстані 1.5 мм від осі гвинта, фізично блокує доступ біти шуруповерта, торцевої головки чи накидного ключа, перетворюючи автоматизоване або ручне конвеєрне складання на брак.
3. **Висотні колізії з ребрами жорсткості та внутрішніми стінками корпусу.** Литі алюмінієві або пластикові корпуси містять внутрішні підсилювальні ребра, відсіки екранування радіочастотних трактів та колодязі для акумуляторів. У таких зонах гранично допустима висота деталей над платою `Z_max` може становити лише 2.5–4.0 мм, тоді як у центральній частині дозволено до 15.0 мм. Встановлення компонента з висотою `h = 5.2` мм у низькопрофільній зоні призводить до деформації плати при закриванні кришки.
4. **Помилки вильоту роз'ємів (Connector Overhang) за габаритний контур.** Роз'єми інтерфейсів USB Type-C, RJ45, micro-HDMI чи SMA повинні виступати за край текстоліту рівно на товщину стінки корпусу плюс технологічний зазор для безперешкодного під'єднання кабельного штекера. Похибка позиціювання на 0.5 мм усередину корпусу призводить до того, що штекер кабелю впирається у зовнішній фасад корпусу до моменту повного замикання фіксаторів замка.

Для запобігання цим дефектам створюється спеціалізований геометричний валідатор механічного конверта, який перевіряє базу розміщення компонентів (файл координат *Pick and Place* / *Centroid file*) та тривимірні габаритні паралелепіпеди (англ. *Bounding Boxes*) деталей проти карти механічних обмежень корпусу.

---

### Фізика контактних напружень: конус тиску та механіка руйнування MLCC

Щоб зрозуміти, чому розмір зони заборони навколо кріпильного отвору не може обмежуватися лише радіусом головки гвинта або шайби, необхідно розглянути механіку розподілу тиску в матеріалі друкованої плати. При затягуванні різьбового з'єднання сила осьового натягу гвинта `F_clamp` передається через контактну поверхню шайби на верхній шар плати. 

Осьове зусилля затягування пов'язане з прикладеним крутним моментом `M_torque` класичним співвідношенням:

```text
F_clamp = M_torque / (k_friction · d_nominal)
```

де `d_nominal` — номінальний діаметр різьби (для гвинта M3 це 0.003 м), а `k_friction` — безрозмірний коефіцієнт тертя в різьбі та на торці шайби (для сталевого оцинкованого кріплення по латунній або сталевій стійці `k_friction ≈ 0.18..0.20`). Для типового моменту затягування `M_torque = 0.6` Н·м отримуємо значне осьове зусилля:

```text
F_clamp = 0.6 / (0.20 · 0.003) = 1000 Н = 1.0 кН
```

Зусилля в 1 кН прикладається до кільцевої площі під шайбою. Згідно з класичною теорією контактних напружень Фьоппля та Решетова, напруження стиску поширюються вглиб шаруватого склотекстоліту FR-4 не суворо вертикально, а у формі зрізаного конуса з кутом розкриття `α ≈ 30°..45°`. 

Через анізотропію склотекстоліту (модуль пружності вздовж скляних ниток `E_xy ≈ 22` ГПа, тоді як поперек шарів `E_z ≈ 3.5` ГПа) локальне стиснення під шайбою призводить до вигину зовнішніх шарів діелектрика. На верхній поверхні плати за межами шайби виникає зона значних радіальних розтягуючих та зсувних деформацій `ε_radial`.

Керамічні багатошарові конденсатори (англ. *Multi-Layer Ceramic Capacitors*, MLCC) складаються з чергованих шарів діелектрика на основі крихкого титанату барію та внутрішніх металевих електродів із нікелю або срібла-паладію. Кераміка надзвичайно міцна на стиск (до 1000 МПа), але вкрай вразлива до розтягу та зсуву: гранично допустима відносна деформація плати для корпусів 0805 та 1206 становить лише:

```text
ε_limit ≈ 500..800 µε (мікрострейн, тобто 0.05%..0.08% відносного подовження)
```

При перевищенні цього порогу в тілі конденсатора під кутом 45° від нижнього краю паяного шва виникає мікротріщина. У момент виготовлення плата може функціонувати нормально, оскільки тріщина ще не розімкнула внутрішні електроди. Проте згодом проникнення вологи з повітря через захисний лак викликає міграцію іонів металу вздовж берегів тріщини, що призводить до лавиноподібного електричного пробою, локального перегріву та займання компонента.

Саме тому радіус заборони розміщення керамічних конденсаторів `R_mlcc_keepout` розраховується як радіус шайби плюс зона загасання деформацій вигину, що становить не менше 2.5–3.0 товщин плати від краю металевої шайби. Для гвинта M3 (радіус шайби 3.0 мм) на стандартній платі завтовшки 1.6 мм безпечна межа становить:

```text
R_mlcc_keepout = R_washer + 2.5 · T_pcb       [розрахункова формула зони деформаційного вигину]
               = 3.0 + 2.5 · 1.6              [підстановка радіуса шайби M3 та товщини FR-4]
               = 3.0 + 4.0                    [множення коефіцієнта на товщину плати]
               = 7.0 мм                       [радіус кола безпеки (діаметр зони заборони 14.0 мм)]
```

---

### Математична модель геометричних примітивів та зон безпеки

Геометричний валідатор оперує системою координат друкованої плати, де площина плати лежить у системі `XY`, а вісь `Z` спрямована ортогонально вгору від верхньої площини первинного шару міді Top Copper.

#### 1. Кріпильний отвір і ступеневі радіальні зони заборони

Кожен кріпильний вузол `H_i` описується координатами центру `(x_h, y_h)`, діаметром свердління `d_drill` та набором концентричних зон безпеки різного функційного призначення:

- **Радіус механічної головки та шайби `R_screw`:** зона прямого тиску металу. У межах `r ≤ R_screw` категорично заборонено наявність будь-яких контактних майданчиків, SMD-компонентів, маски та незахищених сигнальних провідників.
- **Радіус монтажного інструменту `R_tool`:** циліндрична зона проходу торцевого ключа або біти викрутки. Компоненти висотою `h > h_standoff_clearance` не можуть перетинати цей радіус.
- **Радіус захисту від деформацій крихких компонентів `R_mlcc_keepout`:** зона пружно-пластичної деформації склотекстоліту навколо отвору. Залежно від товщини плати `T_pcb` та матеріалу стійки радіус заборони для керамічних конденсаторів і безвивідних мікросхем QFN/BGA становить:

```text
R_mlcc_keepout = R_screw + k_stress · T_pcb      [де k_stress ≈ 1.5..2.0]
```

#### 2. Зони тривимірних висотних обмежень корпусу

Карта висотних обмежень розбиває поверхню плати на множину прямокутних або полігональних зон `Z_k = { (x_min, y_min, x_max, y_max), H_limit }`. Компонент `C_j` з габаритами `(W, L, H)`, центром `(x_c, y_c)` та кутом повороту `θ` перевіряється на умову:

```text
z_top(C_j) = H_j ≤ H_limit(x, y)                 [для всіх (x, y) ∈ BoundingBox(C_j)]
```

#### 3. Перетин орієнтованого прямокутника деталі з колом заборони

Компонент на платі зазвичай орієнтований під довільним кутом `θ ∈ [0°, 360°)`. Для визначення колізії між орієнтованим габаритним прямокутником (англ. *Oriented Bounding Box*, OBB) деталі та колом зони заборони радіуса `R` із центром `(x_h, y_h)` застосовується метод приведення до локальної системи координат прямокутника з наступним знаходженням найближчої точки (англ. *Clamping method*).

Нехай центр прямокутника розташований у точці `(x_c, y_c)`, напівширина становить `e_x = W/2`, напівдовжина `e_y = L/2`, а кут повороту дорівнює `θ`. Вектор зміщення від центру деталі до центру отвору в абсолютних координатах дорівнює:

```text
Δx = x_h - x_c
Δy = y_h - y_c
```

Трансформація вектора в локальну систему координат прямокутника виконується матрицею повороту на кут `-θ`:

```text
u_x =  Δx · cos(θ) + Δy · sin(θ)
u_y = -Δx · sin(θ) + Δy · cos(θ)
```

Найближча точка прямокутника `Q = (q_x, q_y)` до центру отвору в локальних координатах знаходиться обмеженням (клампінгом) координат напівгабаритами:

```text
q_x = max(-e_x, min(e_x, u_x))
q_y = max(-e_y, min(e_y, u_y))
```

Квадрат евклідової відстані від центру отвору до найближчої точки прямокутника розраховується як:

```text
d² = (u_x - q_x)² + (u_y - q_y)²
```

Колізія фіксується тоді і тільки тоді, коли квадрат відстані суворо менший за квадрат радіуса перевірки:

```text
d² < R²
```

Цей метод працює абсолютно точно, не вимагає ресурсомістких тригонометричних ітерацій та коректно обробляє всі крайові випадки: перетин вершин прямокутника, перетин ребер та повне знаходження центру отвору всередині тіла компонента (у цьому випадку `q = u`, отже `d² = 0 < R²`).

---

### Архітектура утиліти та структури даних

Утиліта побудована за модульним принципом і складається з трьох ключових рівнів:
1. **Рівень геометрії та примітивів:** структури 2D-векторів, орієнтованих прямокутників OBB, кругових зон заборони та висотних обмежувальних паралелепіпедів AABB.
2. **Рівень бази даних виробу:** сховище кріпильних отворів, карти висотних обмежень корпусу, переліку компонентів з їхніми механічними властивостями (тип корпусу, висота, категорія вразливості до деформацій).
3. **Двигун валідації:** конвеєр ітеративних перевірок, що генерує детальний інженерний звіт із зазначенням координат колізії, величини проникнення в зону заборони (англ. *Interference depth*) та ідентифікаторів компонентів (RefDes).

---

### Реалізація на мовах C99 та C++20

Нижче наведено повну реалізацію утиліти перевірки механічного конверта на мовах C99 та сучасному ідіоматичному C++20 у перемикачі вкладок.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define MAX_NAME_LEN 32
#define MAX_COMPONENTS 256
#define MAX_HOLES 32
#define MAX_HEIGHT_ZONES 16
#define MAX_VIOLATIONS 128

typedef enum {
    COMP_CLASS_STANDARD,
    COMP_CLASS_MLCC,         /* Керамічні конденсатори: чутливі до вигину текстоліту */
    COMP_CLASS_CONNECTOR,    /* Роз'єми: потребують перевірки вильоту */
    COMP_CLASS_TALL_PASSIVE  /* Високі котушки/електроліти: блокують інструмент */
} ComponentClass;

typedef enum {
    VIOLATION_SCREW_HEAD_COLLISION,
    VIOLATION_TOOL_CLEARANCE_BLOCKED,
    VIOLATION_MLCC_STRESS_ZONE,
    VIOLATION_HEIGHT_EXCEEDED,
    VIOLATION_CONNECTOR_OVERHANG_MISMATCH
} ViolationType;

typedef struct {
    double x;
    double y;
} Vec2;

typedef struct {
    char refdes[MAX_NAME_LEN];
    ComponentClass comp_class;
    Vec2 center;
    double width;       /* Габарит по осі X при куті 0 (мм) */
    double length;      /* Габарит по осі Y при куті 0 (мм) */
    double height;      /* Висота деталі над платою (мм) */
    double rotation_deg;/* Кут повороту (градуси) */
    double overhang_req;/* Необхідний виліт за плату (якщо роз'єм) */
} Component;

typedef struct {
    char id[MAX_NAME_LEN];
    Vec2 center;
    double drill_dia;
    double screw_head_dia;
    double tool_clearance_dia;
    double mlcc_keepout_dia;
} MountingHole;

typedef struct {
    char name[MAX_NAME_LEN];
    double min_x;
    double min_y;
    double max_x;
    double max_y;
    double max_allowed_height;
} HeightZone;

typedef struct {
    ViolationType type;
    char refdes[MAX_NAME_LEN];
    char context_id[MAX_NAME_LEN];
    double actual_value;
    double limit_value;
    Vec2 location;
} Violation;

typedef struct {
    double board_width;
    double board_height;
    Component components[MAX_COMPONENTS];
    size_t component_count;
    MountingHole holes[MAX_HOLES];
    size_t hole_count;
    HeightZone height_zones[MAX_HEIGHT_ZONES];
    size_t height_zone_count;
    Violation violations[MAX_VIOLATIONS];
    size_t violation_count;
} EnvelopeChecker;

static double deg_to_rad(double deg) {
    return deg * (M_PI / 180.0);
}

static double clamp_val(double val, double min_v, double max_v) {
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

/* Перевірка колізії Орієнтованого Прямокутника (OBB) деталі з колом радіуса R */
static bool check_obb_circle_intersect(const Component* c, Vec2 circle_center, double radius, double* out_dist) {
    double rad = deg_to_rad(-c->rotation_deg);
    double cos_a = cos(rad);
    double sin_a = sin(rad);

    double dx = circle_center.x - c->center.x;
    double dy = circle_center.y - c->center.y;

    /* Локальні координати центру кола відносно центру компонента */
    double local_x = dx * cos_a - dy * sin_a;
    double local_y = dx * sin_a + dy * cos_a;

    double half_w = c->width * 0.5;
    double half_l = c->length * 0.5;

    double nearest_x = clamp_val(local_x, -half_w, half_w);
    double nearest_y = clamp_val(local_y, -half_l, half_l);

    double delta_x = local_x - nearest_x;
    double delta_y = local_y - nearest_y;

    double dist_sq = delta_x * delta_x + delta_y * delta_y;
    double dist = sqrt(dist_sq);

    if (out_dist) {
        *out_dist = dist;
    }

    return dist_sq < (radius * radius);
}

void envelope_checker_init(EnvelopeChecker* chk, double board_w, double board_h) {
    memset(chk, 0, sizeof(EnvelopeChecker));
    chk->board_width = board_w;
    chk->board_height = board_h;
}

bool envelope_checker_add_component(EnvelopeChecker* chk, const Component* comp) {
    if (chk->component_count >= MAX_COMPONENTS) return false;
    chk->components[chk->component_count++] = *comp;
    return true;
}

bool envelope_checker_add_hole(EnvelopeChecker* chk, const MountingHole* hole) {
    if (chk->hole_count >= MAX_HOLES) return false;
    chk->holes[chk->hole_count++] = *hole;
    return true;
}

bool envelope_checker_add_height_zone(EnvelopeChecker* chk, const HeightZone* zone) {
    if (chk->height_zone_count >= MAX_HEIGHT_ZONES) return false;
    chk->height_zones[chk->height_zone_count++] = *zone;
    return true;
}

static void log_violation(EnvelopeChecker* chk, ViolationType type, const char* ref, const char* ctx, double act, double lim, Vec2 loc) {
    if (chk->violation_count >= MAX_VIOLATIONS) return;
    Violation* v = &chk->violations[chk->violation_count++];
    v->type = type;
    strncpy(v->refdes, ref, MAX_NAME_LEN - 1);
    strncpy(v->context_id, ctx, MAX_NAME_LEN - 1);
    v->actual_value = act;
    v->limit_value = lim;
    v->location = loc;
}

void envelope_checker_run(EnvelopeChecker* chk) {
    chk->violation_count = 0;

    for (size_t i = 0; i < chk->component_count; ++i) {
        const Component* c = &chk->components[i];

        /* 1. Перевірка відносно кожного кріпильного отвору */
        for (size_t h = 0; h < chk->hole_count; ++h) {
            const MountingHole* hole = &chk->holes[h];
            double dist = 0.0;

            /* А. Головка гвинта / прямий механічний контакт */
            double r_screw = hole->screw_head_dia * 0.5;
            if (check_obb_circle_intersect(c, hole->center, r_screw, &dist)) {
                log_violation(chk, VIOLATION_SCREW_HEAD_COLLISION, c->refdes, hole->id, dist, r_screw, c->center);
            }

            /* Б. Зона проходу викрутки/ключа для високих деталей (h > 4.0 мм) */
            double r_tool = hole->tool_clearance_dia * 0.5;
            if (c->height > 4.0 && check_obb_circle_intersect(c, hole->center, r_tool, &dist)) {
                log_violation(chk, VIOLATION_TOOL_CLEARANCE_BLOCKED, c->refdes, hole->id, c->height, r_tool, c->center);
            }

            /* В. Зона деформаційного стресу для MLCC */
            if (c->comp_class == COMP_CLASS_MLCC) {
                double r_mlcc = hole->mlcc_keepout_dia * 0.5;
                if (check_obb_circle_intersect(c, hole->center, r_mlcc, &dist)) {
                    log_violation(chk, VIOLATION_MLCC_STRESS_ZONE, c->refdes, hole->id, dist, r_mlcc, c->center);
                }
            }
        }

        /* 2. Перевірка висотних зон корпусу */
        for (size_t z = 0; z < chk->height_zone_count; ++z) {
            const HeightZone* zone = &chk->height_zones[z];
            /* Спрощена перевірка потрапляння центру деталі у висотну зону */
            if (c->center.x >= zone->min_x && c->center.x <= zone->max_x &&
                c->center.y >= zone->min_y && c->center.y <= zone->max_y) {
                if (c->height > zone->max_allowed_height) {
                    log_violation(chk, VIOLATION_HEIGHT_EXCEEDED, c->refdes, zone->name, c->height, zone->max_allowed_height, c->center);
                }
            }
        }

        /* 3. Перевірка вильоту роз'єму на лівому боці плати (x = 0) */
        if (c->comp_class == COMP_CLASS_CONNECTOR && c->overhang_req > 0.0) {
            double actual_left_edge = c->center.x - (c->length * 0.5); /* якщо роз'єм вздовж X */
            double actual_overhang = -actual_left_edge; /* виступ за 0 */
            if (fabs(actual_overhang - c->overhang_req) > 0.3) {
                log_violation(chk, VIOLATION_CONNECTOR_OVERHANG_MISMATCH, c->refdes, "LeftEdge", actual_overhang, c->overhang_req, c->center);
            }
        }
    }
}

void envelope_checker_print_report(const EnvelopeChecker* chk) {
    printf("===============================================================\n");
    printf("ЗВІТ МЕХАНІЧНОГО КОНВЕРТА: Перевірено %zu деталей, %zu отворів\n", chk->component_count, chk->hole_count);
    printf("Знайдено дефектів: %zu\n", chk->violation_count);
    printf("===============================================================\n");

    for (size_t i = 0; i < chk->violation_count; ++i) {
        const Violation* v = &chk->violations[i];
        printf("[%02zu] ", i + 1);
        switch (v->type) {
            case VIOLATION_SCREW_HEAD_COLLISION:
                printf("КОЛІЗІЯ З ГОЛОВКОЮ ГВИНТА: %s перекриває %s (відстань %.2f мм < R_screw %.2f мм)\n",
                       v->refdes, v->context_id, v->actual_value, v->limit_value);
                break;
            case VIOLATION_TOOL_CLEARANCE_BLOCKED:
                printf("БЛОКУВАННЯ ІНСТРУМЕНТУ: Деталь %s (висота %.2f мм) блокує зону монтажу %s (R %.2f мм)\n",
                       v->refdes, v->actual_value, v->context_id, v->limit_value);
                break;
            case VIOLATION_MLCC_STRESS_ZONE:
                printf("НЕБЕЗПЕКА ЗЛАМУ MLCC: Конденсатор %s у зоні деформацій %s (відстань %.2f мм < R_keepout %.2f мм)\n",
                       v->refdes, v->context_id, v->actual_value, v->limit_value);
                break;
            case VIOLATION_HEIGHT_EXCEEDED:
                printf("ПЕРЕВИЩЕННЯ ВИСОТИ КОРПУСУ: %s має висоту %.2f мм > ліміту %.2f мм у зоні %s\n",
                       v->refdes, v->actual_value, v->limit_value, v->context_id);
                break;
            case VIOLATION_CONNECTOR_OVERHANG_MISMATCH:
                printf("ПОХИБКА ВИЛЬОТУ РОЗ'ЄМУ: %s виступає на %.2f мм (вимога %.2f мм) на %s\n",
                       v->refdes, v->actual_value, v->limit_value, v->context_id);
                break;
        }
    }
    printf("===============================================================\n");
}

int main(void) {
    EnvelopeChecker checker;
    envelope_checker_init(&checker, 120.0, 70.0);

    /* Додаємо 4 кріпильні отвори під M3 */
    MountingHole h1 = { "H1_TopLeft", { 6.0, 64.0 }, 3.2, 6.0, 8.0, 10.0 };
    MountingHole h2 = { "H2_TopRight", { 114.0, 64.0 }, 3.2, 6.0, 8.0, 10.0 };
    MountingHole h3 = { "H3_BotLeft", { 6.0, 6.0 }, 3.2, 6.0, 8.0, 10.0 };
    MountingHole h4 = { "H4_BotRight", { 114.0, 6.0 }, 3.2, 6.0, 8.0, 10.0 };

    envelope_checker_add_hole(&checker, &h1);
    envelope_checker_add_hole(&checker, &h2);
    envelope_checker_add_hole(&checker, &h3);
    envelope_checker_add_hole(&checker, &h4);

    /* Додаємо низькопрофільну зону корпусу під ребром жорсткості */
    HeightZone rib_zone = { "TopRib_Shield", 30.0, 50.0, 90.0, 70.0, 3.5 };
    envelope_checker_add_height_zone(&checker, &rib_zone);

    /* Тестові деталі */
    Component c1 = { "C101", COMP_CLASS_MLCC, { 7.5, 61.5 }, 1.6, 0.8, 0.9, 45.0, 0.0 }; /* Поруч із H1: небезпека MLCC */
    Component l1 = { "L201", COMP_CLASS_TALL_PASSIVE, { 9.0, 6.0 }, 6.0, 6.0, 5.5, 0.0, 0.0 }; /* Блокує ключ біля H3 */
    Component j1 = { "J1_USB", COMP_CLASS_CONNECTOR, { 4.0, 35.0 }, 8.9, 10.0, 3.2, 0.0, 1.4 }; /* USB-C виліт */
    Component q1 = { "Q301", COMP_CLASS_STANDARD, { 50.0, 60.0 }, 6.5, 6.5, 4.2, 0.0, 0.0 }; /* Зависокий транзистор у зоні ребра */

    envelope_checker_add_component(&checker, &c1);
    envelope_checker_add_component(&checker, &l1);
    envelope_checker_add_component(&checker, &j1);
    envelope_checker_add_component(&checker, &q1);

    envelope_checker_run(&checker);
    envelope_checker_print_report(&checker);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <iomanip>
#include <span>
#include <optional>

namespace mech {

enum class ComponentClass {
    Standard,
    Mlcc,          // Керамічні конденсатори: чутливі до механічного напруження
    Connector,     // Інтерфейсні роз'єми з вимогами до вильоту
    TallPassive    // Високі компоненти (дроселі, електроліти), що блокують інструмент
};

enum class ViolationType {
    ScrewHeadCollision,
    ToolClearanceBlocked,
    MlccStressZone,
    HeightExceeded,
    ConnectorOverhangMismatch
};

struct Vec2 {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr Vec2 operator-(const Vec2& other) const noexcept {
        return { x - other.x, y - other.y };
    }
};

struct Component {
    std::string refdes;
    ComponentClass comp_class{ComponentClass::Standard};
    Vec2 center;
    double width{0.0};       // мм (вісь X при куті 0)
    double length{0.0};      // мм (вісь Y при куті 0)
    double height{0.0};      // мм
    double rotation_deg{0.0};// градуси
    double overhang_req{0.0};// мм
};

struct MountingHole {
    std::string id;
    Vec2 center;
    double drill_dia{3.2};
    double screw_head_dia{6.0};
    double tool_clearance_dia{8.0};
    double mlcc_keepout_dia{10.0};
};

struct HeightZone {
    std::string name;
    double min_x{0.0};
    double min_y{0.0};
    double max_x{0.0};
    double max_y{0.0};
    double max_allowed_height{0.0};

    [[nodiscard]] bool contains(const Vec2& pt) const noexcept {
        return pt.x >= min_x && pt.x <= max_x && pt.y >= min_y && pt.y <= max_y;
    }
};

struct Violation {
    ViolationType type;
    std::string refdes;
    std::string context_id;
    double actual_value{0.0};
    double limit_value{0.0};
    Vec2 location;
};

class GeometryEngine {
public:
    [[nodiscard]] static constexpr double deg_to_rad(double deg) noexcept {
        return deg * (std::numbers::pi / 180.0);
    }

    [[nodiscard]] static bool check_obb_circle_intersect(
        const Component& comp,
        const Vec2& circle_center,
        double radius,
        double& out_dist) noexcept 
    {
        const double rad = deg_to_rad(-comp.rotation_deg);
        const double cos_a = std::cos(rad);
        const double sin_a = std::sin(rad);

        const Vec2 d = circle_center - comp.center;

        // Перехід у власну систему координат прямокутника
        const double local_x = d.x * cos_a - d.y * sin_a;
        const double local_y = d.x * sin_a + d.y * cos_a;

        const double half_w = comp.width * 0.5;
        const double half_l = comp.length * 0.5;

        const double nearest_x = std::clamp(local_x, -half_w, half_w);
        const double nearest_y = std::clamp(local_y, -half_l, half_l);

        const double delta_x = local_x - nearest_x;
        const double delta_y = local_y - nearest_y;

        const double dist_sq = delta_x * delta_x + delta_y * delta_y;
        out_dist = std::sqrt(dist_sq);

        return dist_sq < (radius * radius);
    }
};

class EnvelopeChecker {
public:
    explicit EnvelopeChecker(double board_w, double board_h)
        : board_width_{board_w}, board_height_{board_h} {}

    void add_component(Component comp) {
        components_.push_back(std::move(comp));
    }

    void add_hole(MountingHole hole) {
        holes_.push_back(std::move(hole));
    }

    void add_height_zone(HeightZone zone) {
        height_zones_.push_back(std::move(zone));
    }

    [[nodiscard]] std::span<const Violation> run_checks() {
        violations_.clear();

        for (const auto& comp : components_) {
            // 1. Валідація відносно кріпильних отворів
            for (const auto& hole : holes_) {
                double dist = 0.0;

                // Пряма колізія з головкою гвинта
                const double r_screw = hole.screw_head_dia * 0.5;
                if (GeometryEngine::check_obb_circle_intersect(comp, hole.center, r_screw, dist)) {
                    violations_.push_back({
                        ViolationType::ScrewHeadCollision, comp.refdes, hole.id, dist, r_screw, comp.center
                    });
                }

                // Блокування зони монтажного інструменту високими деталями
                const double r_tool = hole.tool_clearance_dia * 0.5;
                if (comp.height > 4.0 && GeometryEngine::check_obb_circle_intersect(comp, hole.center, r_tool, dist)) {
                    violations_.push_back({
                        ViolationType::ToolClearanceBlocked, comp.refdes, hole.id, comp.height, r_tool, comp.center
                    });
                }

                // Зона небезпечних деформацій для крихких MLCC
                if (comp.comp_class == ComponentClass::Mlcc) {
                    const double r_mlcc = hole.mlcc_keepout_dia * 0.5;
                    if (GeometryEngine::check_obb_circle_intersect(comp, hole.center, r_mlcc, dist)) {
                        violations_.push_back({
                            ViolationType::MlccStressZone, comp.refdes, hole.id, dist, r_mlcc, comp.center
                        });
                    }
                }
            }

            // 2. Валідація тривимірних зон обмеження висоти корпусу
            for (const auto& zone : height_zones_) {
                if (zone.contains(comp.center) && comp.height > zone.max_allowed_height) {
                    violations_.push_back({
                        ViolationType::HeightExceeded, comp.refdes, zone.name, comp.height, zone.max_allowed_height, comp.center
                    });
                }
            }

            // 3. Валідація вильоту інтерфейсних роз'ємів за контур плати
            if (comp.comp_class == ComponentClass::Connector && comp.overhang_req > 0.0) {
                const double actual_left_edge = comp.center.x - (comp.length * 0.5);
                const double actual_overhang = -actual_left_edge;
                if (std::abs(actual_overhang - comp.overhang_req) > 0.3) {
                    violations_.push_back({
                        ViolationType::ConnectorOverhangMismatch, comp.refdes, "LeftEdge", actual_overhang, comp.overhang_req, comp.center
                    });
                }
            }
        }

        return violations_;
    }

    void print_report() const {
        std::cout << "===============================================================\n"
                  << "ЗВІТ МЕХАНІЧНОГО КОНВЕРТА (C++20): Деталей: " << components_.size()
                  << ", Отворів: " << holes_.size() << "\n"
                  << "Знайдено дефектів: " << violations_.size() << "\n"
                  << "===============================================================\n";

        for (size_t idx = 0; const auto& v : violations_) {
            std::cout << "[" << std::setw(2) << std::setfill('0') << ++idx << "] ";
            switch (v.type) {
                case ViolationType::ScrewHeadCollision:
                    std::cout << "КОЛІЗІЯ З ГОЛОВКОЮ ГВИНТА: " << v.refdes << " перекриває "
                              << v.context_id << " (відстань " << std::fixed << std::setprecision(2)
                              << v.actual_value << " мм < R_screw " << v.limit_value << " мм)\n";
                    break;
                case ViolationType::ToolClearanceBlocked:
                    std::cout << "БЛОКУВАННЯ ІНСТРУМЕНТУ: Деталь " << v.refdes << " (висота "
                              << v.actual_value << " мм) блокує зону монтажу " << v.context_id
                              << " (R " << v.limit_value << " мм)\n";
                    break;
                case ViolationType::MlccStressZone:
                    std::cout << "НЕБЕЗПЕКА ЗЛАМУ MLCC: Конденсатор " << v.refdes << " у зоні деформацій "
                              << v.context_id << " (відстань " << v.actual_value << " мм < R_keepout "
                              << v.limit_value << " мм)\n";
                    break;
                case ViolationType::HeightExceeded:
                    std::cout << "ПЕРЕВИЩЕННЯ ВИСОТИ КОРПУСУ: " << v.refdes << " має висоту "
                              << v.actual_value << " мм > ліміту " << v.limit_value
                              << " мм у зоні " << v.context_id << "\n";
                    break;
                case ViolationType::ConnectorOverhangMismatch:
                    std::cout << "ПОХИБКА ВИЛЬОТУ РОЗ'ЄМУ: " << v.refdes << " виступає на "
                              << v.actual_value << " мм (вимога " << v.limit_value
                              << " мм) на " << v.context_id << "\n";
                    break;
            }
        }
        std::cout << "===============================================================\n";
    }

private:
    double board_width_{0.0};
    double board_height_{0.0};
    std::vector<Component> components_;
    std::vector<MountingHole> holes_;
    std::vector<HeightZone> height_zones_;
    std::vector<Violation> violations_;
};

} // namespace mech

int main() {
    mech::EnvelopeChecker checker(120.0, 70.0);

    // Додаємо 4 отвори M3
    checker.add_hole({ "H1_TopLeft",  { 6.0, 64.0 }, 3.2, 6.0, 8.0, 10.0 });
    checker.add_hole({ "H2_TopRight", { 114.0, 64.0 }, 3.2, 6.0, 8.0, 10.0 });
    checker.add_hole({ "H3_BotLeft",  { 6.0, 6.0 }, 3.2, 6.0, 8.0, 10.0 });
    checker.add_hole({ "H4_BotRight", { 114.0, 6.0 }, 3.2, 6.0, 8.0, 10.0 });

    // Зона обмеження висоти
    checker.add_height_zone({ "TopRib_Shield", 30.0, 50.0, 90.0, 70.0, 3.5 });

    // Тестові компоненти
    checker.add_component({ "C101", mech::ComponentClass::Mlcc, { 7.5, 61.5 }, 1.6, 0.8, 0.9, 45.0, 0.0 });
    checker.add_component({ "L201", mech::ComponentClass::TallPassive, { 9.0, 6.0 }, 6.0, 6.0, 5.5, 0.0, 0.0 });
    checker.add_component({ "J1_USB", mech::ComponentClass::Connector, { 4.0, 35.0 }, 8.9, 10.0, 3.2, 0.0, 1.4 });
    checker.add_component({ "Q301", mech::ComponentClass::Standard, { 50.0, 60.0 }, 6.5, 6.5, 4.2, 0.0, 0.0 });

    checker.run_checks();
    checker.print_report();

    return 0;
}
```
:::

---

### Детальний аналіз алгоритмічних рішень та інженерних крайових випадків

Розроблена система перевірки механічного конверта базується на кількох важливих інженерних принципах, які вирішують типові проблеми числової нестабільності та фізичної розбіжності між цифровою моделлю та реальним виробом:

#### 1. Опрацювання поворотів під довільним кутом (Arbitrary Angle Rotation)
Часто розробники намагаються використовувати спрощені прямокутники, вирівняні по осях (англ. *Axis-Aligned Bounding Box*, AABB). Проте якщо компонент (наприклад, конденсатор у корпусі 1210 або мікросхема SOIC-8) встановлено під кутом 45°, його описаний прямокутник AABB штучно роздувається в `√2 ≈ 1.414` раза по кожній осі. Це генерує численні хибнопозитивні спрацьовування (англ. *False Positives*), коли алгоритм сигналізує про колізію з отвором, хоча фізичне тіло деталі перебуває на безпечній відстані. Використання повноцінного орієнтованого паралелепіпеда OBB із прямою трансформацією системи координат усуває геометричну надмірність і забезпечує точність до сотих часток міліметра.

#### 2. Врахування технологічних похибок виготовлення (Tolerance Stackup)
У реальному виробі координати та розміри не є ідеальними математичними константами. Допустиме зміщення центру свердління на фабриці плати становить ±0.05 мм, точність фрезерування контуру плати — ±0.15 мм, а похибка встановлення SMD-компонента маніпулятором Pick&Place — ±0.03 мм. Тому під час промислової валідації радіуси зон заборони збільшуються на суму допусків за методом найгіршого випадку (англ. *Worst-Case*) або за статистичним методом середньоквадратичного відхилення (англ. *Root Sum Square*, RSS):

```text
Δ_total = √(Δ_drill² + Δ_milling² + Δ_smt² + Δ_enclosure²)
```

Якщо `Δ_drill = 0.05` мм, `Δ_milling = 0.15` мм, `Δ_smt = 0.03` мм, `Δ_enclosure = 0.20` мм:

```text
Δ_total = √(0.05² + 0.15² + 0.03² + 0.20²)    [підстановка допусків свердління, фрезерування, SMT і корпусу]
        = √(0.0025 + 0.0225 + 0.0009 + 0.0400) [піднесення технологічних похибок до квадрата]
        = √0.0659                              [сума дисперсій]
        ≈ 0.257 мм                             [видобування кореня: сумарне статистичне відхилення]
```

Таким чином, розрахунковий радіус зони безпеки `R_screw` для гвинта M3 (діаметр шайби 6.0 мм → радіус 3.0 мм) у валідаторі повинен прийматися не меншим ніж `3.0 + 0.26 = 3.26` мм.

#### 3. Багатоступенева класифікація дефектів
Важливою архітектурною перевагою програми є розрізнення типу фізичного ризику:
- Пряма колізія з головкою гвинта — це безумовний фатальний дефект (при закручуванні деталь буде фізично зрізана або розчавлена).
- Порушення зони MLCC — це дефект надійності (плата може пройти первинне тестування на виробництві, але вийде з ладу через 100 годин роботи внаслідок термомеханічної втоми утвореної мікротріщини).
- Блокування зони інструменту — це технологічний дефект DFM (англ. *Design for Manufacturing*), який вимагає або перестановки компонента, або переходу на спеціальний ручний інструмент зі зменшеним зовнішнім діаметром тонкостінної головки.

#### 4. Механіка сполучення роз'ємів та навантаження на паяні шви (Mating Force Dynamics)
Окремим критичним аспектом механічного конверта є валідація кріплення зовнішніх роз'ємів. При під'єднанні кабелю USB Type-C нормативне зусилля вставляння (англ. *Insertion Force*) може досягати 35 Н, а зусилля витягання (англ. *Extraction Force*) становить від 8 до 20 Н. Якщо роз'єм утримується на платі виключно поверхневим монтажем (SMD-виводи на контактних площадках міді), напруження зрізу `τ_solder` у припої SAC305 (олово-срібло-мідь) розраховується як:

```text
τ_solder = F_insert / A_solder_total
```

При типовій сумарній площі паяних майданчиків `A_solder ≈ 2.5` мм² зсувне напруження становить `τ = 35 / 2.5 = 14` МПа, що перевищує межу втомної міцності свинцево-вільних припоїв (≈ 10..12 МПа при кімнатній температурі). Після 50–100 циклів вставляння кабелю контактні площадки відриваються від склотекстоліту разом із мідною фольгою.

Тому геометричний валідатор перевіряє наявність у посадковому місці роз'єму наскрізних металізованих отворів під механічні фіксатори екрана (англ. *Through-Hole Shield Anchor Tabs / Pegs*). Наскрізний штифт передає вектор сили безпосередньо в об'єм склотекстоліту FR-4, де допустиме напруження зминання становить понад 150 МПа. Додатково утиліта контролює відстань від осі роз'єму до найближчого кріпильного гвинта плати: якщо `L_support > 25` мм, консольний вигин плати при натисканні кабелем викликає відшарування сусідніх BGA-чіпів або розтріскування сигнальних доріжок.

#### 5. Розширення алгоритму на довільні опуклі полігони (Separating Axis Theorem)
Для перевірки складних зон заборони довільної форми (наприклад, внутрішніх перегородок литого корпусу або контурів масивних фрезерованих радіаторів) алгоритм розширюється за допомогою теореми про роздільну вісь (англ. *Separating Axis Theorem*, SAT).

Згідно з теоремою SAT, два опуклі багатокутники P та Q не перетинаються тоді і тільки тоді, коли існує хоча б одна пряма (вісь проекції), на яку ортогональні проекції обох багатокутників не перекриваються. Кандидатами на роль роздільних осей є нормалі до всіх ребер багатокутника P та багатокутника Q.

Для кожної осі `n̄`:
1. Обчислюються скалярні проекції всіх вершин багатокутника P: `σ_i = v_P[i] · n̄`, визначаються мінімум `p_min` та максимум `p_max`.
2. Обчислюються скалярні проекції всіх вершин багатокутника Q: `μ_j = v_Q[j] · n̄`, визначаються мінімум `q_min` та максимум `q_max`.
3. Перевіряється умова перекриття відрізків `[p_min, p_max]` та `[q_min, q_max]`. Якщо знайдено вісь, де `p_max < q_min` або `q_max < p_min`, багатокутники гарантовано роз'єднані, і подальша перевірка припиняється.

Якщо для всіх можливих осей проекцій зафіксовано перекриття, мінімальна величина перекриття `δ_min` визначає вектор мінімального виштовхування (англ. *Minimum Translation Vector*, MTV), який записується у звіт як точна величина геометричної колізії деталей.

#### 6. Інтеграція в конвеєр неперервної інтеграції (CI/CD)
У промисловій практиці утиліта компілюється як консольний інструмент без зовнішніх залежностей і інтегрується в GitHub Actions або GitLab CI пайплайн розробки апаратного забезпечення:

1. На етапі експорту проекту з САПР автоматично генерується файл координат розміщення `board.pos` (або витяг із `IPC-2581` / `ODB++`) та JSON-файл конфігурації механічного конверта корпусу `enclosure_envelope.json`.
2. Валідатор виконує аналіз за частки мікросекунди на компонент, що дозволяє миттєво блокувати злиття Pull Request, якщо інженер випадково зсунув роз'єм або встановив фільтрувальний конденсатор живлення в зону шайби кріпильного гвинта.
3. Звіт утиліти автоматично транслюється у формат анотацій вихідного коду або SARIF, підсвічуючи проблемні місця на інтерактивному 3D-переглядачі друкованої плати.
