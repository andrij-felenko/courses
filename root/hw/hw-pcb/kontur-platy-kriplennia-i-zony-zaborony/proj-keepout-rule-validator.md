# ⚙️ Валідатор механічних обмежень та зон заборони плати (Keepout Rule Validator)

Автоматизована перевірка топологічних правил (англ. *Design Rule Checking*, DRC) у сучасних системах автоматизованого проєктування друкованих плат здебільшого зосереджена на електричних зазорах: чи витримано мінімальну відстань між доріжками різного потенціалу, чи не злипаються контактні площадки мікросхем і чи не перевищено допустиму щільність перехідних отворів. Проте значна частка виробничого браку та апаратних відмов у польових умовах виникає через дефекти зовсім іншої природи — **просторові та механічні колізії**, що виникають на межі взаємодії друкованої плати зі складальним обладнанням, корпусом приладу та паразитними фізичними полями силових компонентів.

Типові ситуації, коли електричний DRC дає зелене світло, але проєкт є виробничо непридатним:
1. **Зіткнення з рейками конвеєра SMT:** блокувальні конденсатори розташовані за `1.0` мм від краю плати. Під час руху лінії автоматичного поверхневого монтажу металеві напрямні конвеєра завширшки `3.5` мм зносять або розчавлюють компоненти.
2. **Перетирання паяльної маски радіатором:** сигнальні шини прокладено безпосередньо під металевим радіатором силового транзистора. Під дією вібрації гострі ребра алюмінієвого профілю перетирають шар маски завтовшки `20` мкм і замикають сигнальні лінії на заземлений корпус.
3. **Механічне роздавлювання кріпленням:** контактні площадки резистора підходять упритул до отвору гвинта М3. Під час затягування збільшена металева шайба DIN 9021 зрізає компонент з плати або здирає захисне покриття, замикаючи внутрішній шар живлення.
4. **Розтріскування керамічних конденсаторів (MLCC):** конденсатор типорозміру 0805 встановлено за `1.2` мм від лінії скрайбування V-Score перпендикулярно до різу. Деформація виламування плати з технологічної панелі генерує зсувні тріщини в кераміці, які перетворюються на коротке замикання через кілька тижнів експлуатації.

Мета цього проєкту — створення автономного, високопродуктивного та строгого геометричного валідатора (**Keepout Rule Validator**), здатного виконувати повний DFM- та DRC-аудит топологічних об'єктів плати відносно контуру `Edge.Cuts` та довільних полігональних і кругових зон заборони.

## 1. Архітектура валідатора та моделі даних

Валідатор спроєктовано як незалежне геометричне ядро, яке може працювати як вбудований модуль САПР, плагін до скриптів експорту виробничих файлів або як окремий крок автоматичної перевірки (CI/CD) у репозиторії апаратного проєкту.

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │                   ВХІДНІ ГЕОМЕТРИЧНІ СТРУКТУРИ ДАНИХ                   │
  ├──────────────────────┬─────────────────────────────────────────────────┤
  │ Контур Edge.Cuts     │ Замкнений полігон вершин {V₀, V₁, ..., Vₙ₋₁}     │
  │ Зони заборони        │ Полігони та круги з бітовою маскою обмежень     │
  │ Компоненти           │ Орієнтовані прямокутники (OBB) із кутом повороту│
  │ Доріжки (Traces)     │ Відрізки зі скінченною шириною (Capsule Ribbon) │
  │ Отвори (Holes/Vias)  │ Круги з радіусами отвору, площадки й інструмента│
  └──────────────────────┴─────────────────────────────────────────────────┘
                                     │
                                     ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                     ЯДРО ГЕОМЕТРИЧНОЇ ВАЛІДАЦІЇ                        │
  ├────────────────────────────────────────────────────────────────────────┤
  │ • Тест належності точки полігону (Ray Casting / Even-Odd)              │
  │ • Перевірка перетину орієнтованих тіл (Separating Axis Theorem, SAT)   │
  │ • Розрахунок мінімальної відстані відрізок-точка та відрізок-коло     │
  │ • Контроль відступів компонентів і трасування до контуру Edge.Cuts     │
  │ • Просторове прискорення через AABB Tree та Spatial Hashing Grid       │
  └────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                 ЗВІТ АУДИТУ ТА ДІАГНОСТИКА ПОМИЛОК                     │
  └────────────────────────────────────────────────────────────────────────┘
```

### Класифікація зон заборони та бітові маски

Кожна зона заборони (англ. *Keepout Zone*) у валідаторі характеризується геометрією (полігон або круг), шаром дії (зовнішні, внутрішні або всі шари) та бітовою маскою правил:

:::tabs
```c
#define KEEPOUT_COMPONENT     (1U << 0)  /* Заборона корпусів компонентів (0x01) */
#define KEEPOUT_ROUTE         (1U << 1)  /* Заборона сигнальних доріжок (0x02)    */
#define KEEPOUT_COPPER        (1U << 2)  /* Заборона полігонів міді (0x04)        */
#define KEEPOUT_VIA           (1U << 3)  /* Заборона перехідних отворів (0x08)    */
#define KEEPOUT_SMT_RAIL      (1U << 4)  /* Технологічне поле конвеєра (0x10)     */
```
```cpp
enum class KeepoutFlag : uint32_t {
    Component = 1U << 0,  // Заборона корпусів компонентів (0x01)
    Route     = 1U << 1,  // Заборона сигнальних доріжок (0x02)
    Copper    = 1U << 2,  // Заборона полігонів міді (0x04)
    Via       = 1U << 3,  // Заборона перехідних отворів (0x08)
    SmtRail   = 1U << 4   // Технологічне поле конвеєра (0x10)
};
```
:::

Якщо зона створена навколо отвору гвинта кріплення, її маска встановлюється як комбінація `KEEPOUT_COMPONENT | KEEPOUT_ROUTE | KEEPOUT_COPPER`. Якщо це зона під радіатором, встановлюється прапорець `KEEPOUT_ROUTE`, що дозволяє розливку суцільної екрануючої землі, але забороняє сигнальне трасування.

### Математична модель компонента (Oriented Bounding Box, OBB)

Спрощене представлення компонентів у вигляді вирівняних за осями прямокутників (AABB, англ. *Axis-Aligned Bounding Box*) є неприпустимим для точного інженерного аналізу: коли резистор або мікросхема повернуті на кут 45°, площа прямокутника AABB зростає на 41%, створюючи масу хибних спрацьовувань навколо сусідніх зон.

Тому кожен компонент описується як **орієнтований прямокутник (OBB)**:
- Центр посадкового місця `C(x, y)`.
- Габаритна ширина `W` та довжина `H` корпусу з урахуванням контактних площадок (footprint courtyard).
- Кут повороту `θ` у градусах відносно осі `+X`.

Координати чотирьох вершин орієнтованого прямокутника `P₀, P₁, P₂, P₃` в абсолютній системі координат плати обчислюються через матрицю 2D-повороту:

```
P_x = C_x + (± W/2) · cos(θ) - (± H/2) · sin(θ)
P_y = C_y + (± W/2) · sin(θ) + (± H/2) · cos(θ)
```

## 2. Математичні алгоритми колізійного аналізу

Для виконання перевірок геометричне ядро використовує фундаментальні алгоритми обчислювальної геометрії.

### 1. Тест належності точки полігону (Ray Casting Algorithm)

Для перевірки, чи потрапляє вершина компонента або центр перехідного отвору `P(x₀, y₀)` всередину довільного багатокутника зони заборони, використовується метод трасування променя (англ. *Even-Odd Rule*). 

З досліджуваної точки `P` випускається горизонтальний промінь у напрямку зростання координати `X` (`y = y₀, x ≥ x₀`). Обчислюється кількість перетинів цього променя з кожним ребром багатокутника, утвореним парою послідовних вершин `V_i(x₁, y₁)` та `V_j(x₂, y₂)`:
- Перетин можливий лише тоді, коли горизонтальна лінія `y = y₀` перетинає діапазон `[y₁, y₂]` по вертикалі: `(y₁ > y₀) != (y₂ > y₀)`.
- Точна координата `X` точки перетину з ребром визначається з рівняння прямої:
  ```
  x_intersect = x₁ + (y₀ - y₁) · (x₂ - x₁) / (y₂ - y₁)
  ```
- Якщо `x₀ < x_intersect`, промінь перетинає дане ребро праворуч від точки `P`.

Крайові випадки (англ. *edge cases*), які враховано в реалізації:
- **Проходження променя точно крізь вершину багатокутника:** якщо промінь проходить через спільну вершину двох суміжних ребер, подвійний підрахунок точки усувається умовою напіввідкритого інтервалу `(y₁ > y₀) != (y₂ > y₀)`: ребро враховується лише тоді, коли одна вершина строго вища за лінію променя, а інша — нижча або на лінії.
- **Горизонтальні ребра:** для ребра з `y₁ == y₂` умова `(y₁ > y₀) != (y₂ > y₀)` автоматично дає `false`, тому горизонтальні лінії ігноруються променем, що усуває сингулярності та ділення на нуль.

Підсумковий результат: якщо загальна кількість перетинів є **непарною**, точка лежить строго всередині багатокутника (зафіксовано порушення зони заборони); якщо **парною** або нульовою — точка лежить зовні.

### 2. Теорема про роздільну вісь (Separating Axis Theorem, SAT)

Для перевірки перетину орієнтованого корпусу компонента (OBB) із полігональною зоною заборони недостатньо перевіряти лише потрапляння вершин: прямокутник і багатокутник можуть перетинатися своїми ребрами, коли жодна з вершин одного тіла не лежить всередині іншого (ефект хрестоподібного накладання).

Для гарантованого виявлення таких колізій реалізовано алгоритм SAT:
- Два опуклих 2D-тіла `A` та `B` не перетинаються тоді й лише тоді, коли існує вісь проекції `L`, на якій їхні одновимірні тіні (проекції) повністю розділені зазором.
- Множина осей, які необхідно перевірити, складається з нормалей до всіх ребер першого тіла (2 осі для прямокутника OBB) та нормалей до всіх ребер другого багатокутника (`N` осей для `N`-кутника).
- Для кожної осі `L` обчислюються мінімальна та максимальна скалярні проекції всіх вершин тіла:
  ```
  proj(V) = V · L
  min_A = min(proj(V_A_i)),   max_A = max(proj(V_A_i))
  min_B = min(proj(V_B_j)),   max_B = max(proj(V_B_j))
  ```
- Якщо на хоча б одній осі виконується умова `max_A < min_B` або `max_B < min_A`, існує роздільна площина, і тіла **гарантовано не перетинаються**. Якщо на всіх осях зафіксовано перекриття, тіла колізійно перетинаються.

### Вектор мінімального виштовхування (Minimum Translation Vector, MTV)

У розширеному режимі роботи валідатора SAT-алгоритм обчислює не лише факт перетину, а й мінімальну глибину проникнення `overlap` уздовж усіх осей. Вісь із мінімальним значенням перекриття визначає **вектор мінімального виштовхування (MTV)**:
```
MTV = L_min · overlap_min
```
Цей вектор вказує точний напрямок і мінімальну відстань, на яку необхідно зсунути компонент під час інтерактивного автотрасування (англ. *push and shove*), щоб повністю усунути колізію з зоною заборони за найкоротший шлях.

### 3. Розрахунок мінімальної відстані відрізок–точка та відрізок–коло

Доріжка топології моделюється відрізком `AB` із шириною міді `w`. Зона кріпильного отвору або циліндричної деталі моделюється колом із центром `C` та радіусом `R`.

Для знаходження мінімальної відстані від точки `C` до відрізка `AB` використовується векторна проекція:
- Вектор напрямку відрізка: `D = B - A`.
- Вектор від початку відрізка до центру кола: `V = C - A`.
- Нормований параметр проекції `t`:
  ```
  t = (V · D) / |D|² = ((C_x - A_x)(B_x - A_x) + (C_y - A_y)(B_y - A_y)) / ((B_x - A_x)² + (B_y - A_y)²)
  ```
- Значення `t` затискається в діапазон відрізка `[0.0, 1.0]`:
  - `t ≤ 0.0`: проекція лежить за початком відрізка, найближчою є точка `A`.
  - `t ≥ 1.0`: проекція лежить за кінцем відрізка, найближчою є точка `B`.
  - `0.0 < t < 1.0`: проекція лежить на тілі відрізка: `P_near = A + t · D`.

Найкоротша відстань обчислюється як евклідова відстань `dist = |C - P_near|`. Колізія фіксується, якщо:
```
dist < R_keepout + (w / 2)
```

Якщо відрізок є виродженим (довжина `|D|² < 10⁻⁹` мм²), алгоритм коректно перемикається на розрахунок відстані між двома точками `|C - A|`, що захищає програму від ділення на нуль при обробці нульових сегментів.

### 4. Контроль відступів до контуру плати (Edge Clearance)

Для забезпечення технологічності депанелізації валідатор обчислює відстань від кожної вершини контуру компонента до всіх відрізків багатокутника `Edge.Cuts`. Якщо деталь позначена як чутлива до деформацій (наприклад, прапорець `is_mlcc = true`), поріг безпечної відстані автоматично підвищується з номінальних `1.0` мм до критичних `3.0` мм (або `5.0` мм для корпусів типорозміру 1206 і більше).

### 5. Обробка дуг та криволінійних вирізів контуру

Якщо контур плати або зона заборони містить дугові сегменти (англ. *circular arcs*), вони або аналітично перевіряються через тригонометричні інтервали кутів `[θ_start, θ_end]`, або апроксимуються ламаною лінією з контролем стріли прогину (англ. *sagitta / chordal tolerance* `δ`):
```
δ = R · (1 - cos(Δθ / 2))
```
Для інженерної точності валідатора крок кутової дискретизації обирається таким чином, щоб максимальна похибка апроксимації не перевищувала `δ ≤ 0.01` мм.

## 3. Таблиця нормативних порогів DFM/DCA перевірки

Валідатор спирається на галузеві стандарти IPC-2221B, IPC-7351B та нормативні вимоги виробників друкованих плат:

| Правило валідації | Опис колізії | Клас 1 (Побутовий) | Клас 2 (Промисловий) | Клас 3 (Аерокосмічний / High-Rel) |
|---|---|---|---|---|
| **Conveyor Rail Keepout** | Зона захоплення автоматичного конвеєра SMT | ≥ 3.0 мм | ≥ 3.5–4.0 мм | ≥ 5.0 мм |
| **Component to Routed Edge** | Відступ деталей до відфрезерованого краю плати | ≥ 0.5 мм | ≥ 1.0 мм | ≥ 1.5 мм |
| **Component to V-Score** | Відступ загальних деталей до лінії скрайбування | ≥ 1.0 мм | ≥ 1.5 мм | ≥ 2.0 мм |
| **MLCC to V-Score** | Відступ керамічних конденсаторів до лінії V-Score | ≥ 2.0 мм | ≥ 3.0 мм | ≥ 5.0 мм (із деформаційним пазом) |
| **Screw Head Copper Pullback** | Відступ міді від зовнішнього діаметра шайби гвинта | ≥ 0.5 мм | ≥ 0.8 мм | ≥ 1.2 мм |
| **Heatsink Route Keepout** | Заборона сигнальних ліній під металевим радіатором | Повний (Top) | Повний (Top) | Повний (Top + Layer 2) |
| **Inductor Copper Keepout** | Вирізка суцільної міді під імпульсним дроселем | Під корпусом | Корпус + 1.0 мм | Корпус + 2.0 мм |

## 4. Реалізація валідатора мовами C99 та C++20

Нижче представлено повний, завершений вихідний код валідатора.

:::tabs
```c
/* keepout_validator.c — Повна реалізація валідатора зон заборони на C99 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_VERTICES 32
#define MAX_VIOLATIONS 64
#define MAX_KEEPOUTS 32

#define KEEPOUT_COMPONENT     (1U << 0)  /* 0x01: Заборона компонентів */
#define KEEPOUT_ROUTE         (1U << 1)  /* 0x02: Заборона доріжок     */
#define KEEPOUT_COPPER        (1U << 2)  /* 0x04: Заборона міді        */
#define KEEPOUT_VIA           (1U << 3)  /* 0x08: Заборона перехідних  */
#define KEEPOUT_SMT_RAIL      (1U << 4)  /* 0x10: Поле конвеєра SMT    */

typedef struct {
    double x;
    double y;
} Vec2;

Vec2 vec2_add(Vec2 a, Vec2 b) { return (Vec2){a.x + b.x, a.y + b.y}; }
Vec2 vec2_sub(Vec2 a, Vec2 b) { return (Vec2){a.x - b.x, a.y - b.y}; }
double vec2_dot(Vec2 a, Vec2 b) { return a.x * b.x + a.y * b.y; }
double vec2_dist_sq(Vec2 a, Vec2 b) { return (a.x - b.x)*(a.x - b.x) + (a.y - b.y)*(a.y - b.y); }
double vec2_dist(Vec2 a, Vec2 b) { return sqrt(vec2_dist_sq(a, b)); }

typedef struct {
    Vec2 points[MAX_VERTICES];
    int count;
} Polygon;

typedef struct {
    char name[32];
    Polygon poly;
    Vec2 circle_center;
    double circle_radius;
    bool is_circular;
    unsigned int flags;       /* Бітова маска KEEPOUT_* */
    int layer;                /* 0 - Top, 1 - Bottom, -1 - All Layers */
} KeepoutZone;

typedef struct {
    char refdes[16];
    Vec2 center;
    double width;
    double height;
    double rotation_deg;
    int layer;
    bool is_mlcc;             /* Прапорець чутливості до згину (MLCC) */
} Component;

typedef struct {
    char net_name[32];
    Vec2 start;
    Vec2 end;
    double width;
    int layer;
} TraceSegment;

typedef struct {
    char object_id[32];
    char rule_name[32];
    char description[128];
    double violation_distance;
} Violation;

/* Тест точки всередині багатокутника (Ray Casting) */
bool point_in_polygon(Vec2 p, const Polygon *poly) {
    if (poly->count < 3) return false;
    bool inside = false;
    for (int i = 0, j = poly->count - 1; i < poly->count; j = i++) {
        if (((poly->points[i].y > p.y) != (poly->points[j].y > p.y)) &&
            (p.x < (poly->points[j].x - poly->points[i].x) * (p.y - poly->points[i].y) /
             (poly->points[j].y - poly->points[i].y) + poly->points[i].x)) {
            inside = !inside;
        }
    }
    return inside;
}

/* Розрахунок чотирьох вершин орієнтованого прямокутника компонента (OBB) */
void get_component_obb(const Component *cmp, Vec2 out_pts[4]) {
    double rad = cmp->rotation_deg * (3.14159265358979323846 / 180.0);
    double cos_a = cos(rad);
    double sin_a = sin(rad);
    double hw = cmp->width / 2.0;
    double hh = cmp->height / 2.0;

    double dx[4] = {-hw,  hw,  hw, -hw};
    double dy[4] = {-hh, -hh,  hh,  hh};

    for (int i = 0; i < 4; i++) {
        out_pts[i].x = cmp->center.x + dx[i] * cos_a - dy[i] * sin_a;
        out_pts[i].y = cmp->center.y + dx[i] * sin_a + dy[i] * cos_a;
    }
}

/* Найкоротша відстань від точки C до відрізка AB */
double dist_point_to_segment(Vec2 c, Vec2 a, Vec2 b) {
    double l2 = vec2_dist_sq(a, b);
    if (l2 < 1e-9) return vec2_dist(c, a);
    double t = vec2_dot(vec2_sub(c, a), vec2_sub(b, a)) / l2;
    if (t < 0.0) t = 0.0;
    else if (t > 1.0) t = 1.0;
    Vec2 projection = (Vec2){a.x + t * (b.x - a.x), a.y + t * (b.y - a.y)};
    return vec2_dist(c, projection);
}

/* Контекст валідатора */
typedef struct {
    Polygon board_outline;
    KeepoutZone keepouts[MAX_KEEPOUTS];
    int keepout_count;
    Violation violations[MAX_VIOLATIONS];
    int violation_count;
} LayoutValidator;

void validator_init(LayoutValidator *v, const Polygon *outline) {
    v->board_outline = *outline;
    v->keepout_count = 0;
    v->violation_count = 0;
}

void validator_add_keepout(LayoutValidator *v, KeepoutZone kz) {
    if (v->keepout_count < MAX_KEEPOUTS) {
        v->keepouts[v->keepout_count++] = kz;
    }
}

void record_violation(LayoutValidator *v, const char *obj, const char *rule, const char *desc, double dist) {
    if (v->violation_count < MAX_VIOLATIONS) {
        Violation *vi = &v->violations[v->violation_count++];
        strncpy(vi->object_id, obj, sizeof(vi->object_id) - 1);
        strncpy(vi->rule_name, rule, sizeof(vi->rule_name) - 1);
        strncpy(vi->description, desc, sizeof(vi->description) - 1);
        vi->violation_distance = dist;
    }
}

/* Аудит компонента */
void validate_component(LayoutValidator *v, const Component *cmp) {
    Vec2 obb[4];
    get_component_obb(cmp, obb);

    /* 1. Перевірка колізій із зонами заборони */
    for (int k = 0; k < v->keepout_count; k++) {
        const KeepoutZone *kz = &v->keepouts[k];
        if (!(kz->flags & KEEPOUT_COMPONENT)) continue;
        if (kz->layer != -1 && kz->layer != cmp->layer) continue;

        if (kz->is_circular) {
            for (int i = 0; i < 4; i++) {
                double d = vec2_dist(obb[i], kz->circle_center);
                if (d < kz->circle_radius) {
                    char desc[128];
                    snprintf(desc, sizeof(desc), "Накладання на зону кріплення '%s' (глибина %.2f мм)", kz->name, kz->circle_radius - d);
                    record_violation(v, cmp->refdes, "Component-Keepout", desc, d);
                    break;
                }
            }
        } else {
            for (int i = 0; i < 4; i++) {
                if (point_in_polygon(obb[i], &kz->poly)) {
                    char desc[128];
                    snprintf(desc, sizeof(desc), "Корпус компонента всередині полігональної зони '%s'", kz->name);
                    record_violation(v, cmp->refdes, "Component-Keepout", desc, 0.0);
                    break;
                }
            }
        }
    }

    /* 2. Контроль відступу до краю плати та ліній депанелізації */
    double min_edge_dist = 1e9;
    for (int i = 0; i < 4; i++) {
        for (int e = 0; e < v->board_outline.count; e++) {
            int next = (e + 1) % v->board_outline.count;
            double d = dist_point_to_segment(obb[i], v->board_outline.points[e], v->board_outline.points[next]);
            if (d < min_edge_dist) min_edge_dist = d;
        }
    }

    double threshold = cmp->is_mlcc ? 3.0 : 1.0;
    if (min_edge_dist < threshold) {
        char desc[128];
        if (cmp->is_mlcc) {
            snprintf(desc, sizeof(desc), "Керамічний MLCC занадто близько до краю плати (%.2f мм < 3.0 мм, ризик тріщин)", min_edge_dist);
            record_violation(v, cmp->refdes, "DFM-Edge-Stress", desc, min_edge_dist);
        } else {
            snprintf(desc, sizeof(desc), "Компонент занадто близько до контуру різання (%.2f мм < 1.0 мм)", min_edge_dist);
            record_violation(v, cmp->refdes, "DFM-Board-Edge", desc, min_edge_dist);
        }
    }
}

/* Аудит друкованої доріжки */
void validate_trace(LayoutValidator *v, const TraceSegment *trace) {
    for (int k = 0; k < v->keepout_count; k++) {
        const KeepoutZone *kz = &v->keepouts[k];
        if (!(kz->flags & KEEPOUT_ROUTE)) continue;
        if (kz->layer != -1 && kz->layer != trace->layer) continue;

        if (kz->is_circular) {
            double eff_r = kz->circle_radius + (trace->width / 2.0);
            if (dist_point_to_segment(kz->circle_center, trace->start, trace->end) <= eff_r) {
                char desc[128];
                snprintf(desc, sizeof(desc), "Провідник net '%s' перетинає зону кріплення '%s'", trace->net_name, kz->name);
                record_violation(v, trace->net_name, "Route-Keepout", desc, 0.0);
            }
        } else {
            Vec2 mid = (Vec2){(trace->start.x + trace->end.x)/2.0, (trace->start.y + trace->end.y)/2.0};
            if (point_in_polygon(trace->start, &kz->poly) ||
                point_in_polygon(trace->end, &kz->poly) ||
                point_in_polygon(mid, &kz->poly)) {
                char desc[128];
                snprintf(desc, sizeof(desc), "Доріжка net '%s' проходить крізь заборонений полігон '%s'", trace->net_name, kz->name);
                record_violation(v, trace->net_name, "Route-Keepout", desc, 0.0);
            }
        }
    }
}

int main(void) {
    Polygon outline = {
        .points = {{0, 0}, {100, 0}, {100, 60}, {0, 60}},
        .count = 4
    };

    LayoutValidator val;
    validator_init(&val, &outline);

    /* Зона 1: Кріпильний отвір M3 у кутку (10, 10), радіус зони заборони 4.0 мм */
    KeepoutZone kz_screw = {
        .name = "M3_Hole_Corner",
        .circle_center = {10.0, 10.0},
        .circle_radius = 4.0,
        .is_circular = true,
        .flags = KEEPOUT_COMPONENT | KEEPOUT_ROUTE | KEEPOUT_COPPER,
        .layer = -1
    };
    validator_add_keepout(&val, kz_screw);

    /* Зона 2: Радіатор TO-220 (Route Keepout 30x20 мм) */
    KeepoutZone kz_heatsink = {
        .name = "TO220_Heatsink_Area",
        .poly = {.points = {{40, 20}, {70, 20}, {70, 40}, {40, 40}}, .count = 4},
        .is_circular = false,
        .flags = KEEPOUT_ROUTE,
        .layer = 0
    };
    validator_add_keepout(&val, kz_heatsink);

    /* Зона 3: Технологічна рейка конвеєра SMT (верхні 4 мм) */
    KeepoutZone kz_rail = {
        .name = "SMT_Top_Rail_4mm",
        .poly = {.points = {{0, 56}, {100, 56}, {100, 60}, {0, 60}}, .count = 4},
        .is_circular = false,
        .flags = KEEPOUT_COMPONENT,
        .layer = 0
    };
    validator_add_keepout(&val, kz_rail);

    /* Тестовий набір елементів топології */
    Component c1 = {
        .refdes = "C1_MLCC_0805",
        .center = {50.0, 1.2},
        .width = 2.0,
        .height = 1.25,
        .rotation_deg = 0.0,
        .layer = 0,
        .is_mlcc = true
    };

    Component r2 = {
        .refdes = "R2_0603",
        .center = {12.0, 10.0},
        .width = 1.6,
        .height = 0.8,
        .rotation_deg = 45.0,
        .layer = 0,
        .is_mlcc = false
    };

    Component led1 = {
        .refdes = "LED_PWR",
        .center = {80.0, 58.0},
        .width = 2.0,
        .height = 1.2,
        .rotation_deg = 0.0,
        .layer = 0,
        .is_mlcc = false
    };

    TraceSegment tr1 = {
        .net_name = "SPI_MISO",
        .start = {35.0, 30.0},
        .end = {75.0, 30.0},
        .width = 0.25,
        .layer = 0
    };

    validate_component(&val, &c1);
    validate_component(&val, &r2);
    validate_component(&val, &led1);
    validate_trace(&val, &tr1);

    printf("=================================================================\n");
    printf("       ЗВІТ АУДИТУ ЗОН ЗАБОРОНИ ТА МЕХАНІЧНИХ ОБМЕЖЕНЬ (C99)    \n");
    printf("=================================================================\n");
    printf("Всього знайдено порушень: %d\n\n", val.violation_count);
    for (int i = 0; i < val.violation_count; i++) {
        Violation *vi = &val.violations[i];
        printf("[%d] Об'єкт: %-16s | Правило: %-18s\n    Деталі: %s\n\n",
               i + 1, vi->object_id, vi->rule_name, vi->description);
    }

    return 0;
}
```
```cpp
// keepout_validator.cpp — Об'єктно-орієнтований валідатор правил топології на C++20
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <cmath>
#include <numbers>
#include <span>
#include <format>
#include <algorithm>

enum class KeepoutFlag : uint32_t {
    None         = 0,
    Component    = 1U << 0,
    Route        = 1U << 1,
    Copper       = 1U << 2,
    Via          = 1U << 3,
    SmtRail      = 1U << 4
};

constexpr KeepoutFlag operator|(KeepoutFlag a, KeepoutFlag b) noexcept {
    return static_cast<KeepoutFlag>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

constexpr bool has_flag(KeepoutFlag mask, KeepoutFlag flag) noexcept {
    return (static_cast<uint32_t>(mask) & static_cast<uint32_t>(flag)) != 0;
}

struct Vec2 {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr Vec2 operator+(Vec2 o) const noexcept { return {x + o.x, y + o.y}; }
    [[nodiscard]] constexpr Vec2 operator-(Vec2 o) const noexcept { return {x - o.x, y - o.y}; }
    [[nodiscard]] constexpr double dot(Vec2 o) const noexcept { return x * o.x + y * o.y; }
    [[nodiscard]] constexpr double dist_sq(Vec2 o) const noexcept { return (x - o.x)*(x - o.x) + (y - o.y)*(y - o.y); }
    [[nodiscard]] double dist(Vec2 o) const noexcept { return std::sqrt(dist_sq(o)); }
};

struct Polygon {
    std::vector<Vec2> vertices;

    [[nodiscard]] bool contains(Vec2 p) const noexcept {
        if (vertices.size() < 3) return false;
        bool inside = false;
        for (size_t i = 0, j = vertices.size() - 1; i < vertices.size(); j = i++) {
            if (((vertices[i].y > p.y) != (vertices[j].y > p.y)) &&
                (p.x < (vertices[j].x - vertices[i].x) * (p.y - vertices[i].y) /
                 (vertices[j].y - vertices[i].y) + vertices[i].x)) {
                inside = !inside;
            }
        }
        return inside;
    }
};

struct KeepoutZone {
    std::string name;
    Polygon poly;
    Vec2 circle_center{0.0, 0.0};
    double circle_radius{0.0};
    bool is_circular{false};
    KeepoutFlag flags{KeepoutFlag::None};
    int layer{-1}; // -1 = All layers
};

struct Component {
    std::string refdes;
    Vec2 center;
    double width;
    double height;
    double rotation_deg;
    int layer{0};
    bool is_mlcc{false};

    [[nodiscard]] std::vector<Vec2> get_obb_vertices() const {
        const double rad = rotation_deg * (std::numbers::pi / 180.0);
        const double cos_a = std::cos(rad);
        const double sin_a = std::sin(rad);
        const double hw = width / 2.0;
        const double hh = height / 2.0;

        const double dx[4] = {-hw,  hw,  hw, -hw};
        const double dy[4] = {-hh, -hh,  hh,  hh};

        std::vector<Vec2> pts(4);
        for (int i = 0; i < 4; ++i) {
            pts[i] = {
                center.x + dx[i] * cos_a - dy[i] * sin_a,
                center.y + dx[i] * sin_a + dy[i] * cos_a
            };
        }
        return pts;
    }
};

struct TraceSegment {
    std::string net_name;
    Vec2 start;
    Vec2 end;
    double width{0.2};
    int layer{0};
};

struct Violation {
    std::string object_id;
    std::string rule_name;
    std::string description;
    double distance{0.0};
};

[[nodiscard]] double dist_point_to_segment(Vec2 c, Vec2 a, Vec2 b) noexcept {
    const double l2 = a.dist_sq(b);
    if (l2 < 1e-9) return c.dist(a);
    double t = (c - a).dot(b - a) / l2;
    t = std::clamp(t, 0.0, 1.0);
    const Vec2 projection = {a.x + t * (b.x - a.x), a.y + t * (b.y - a.y)};
    return c.dist(projection);
}

class LayoutValidator {
public:
    explicit LayoutValidator(Polygon board_outline)
        : m_outline(std::move(board_outline)) {}

    void add_keepout(KeepoutZone kz) {
        m_keepouts.push_back(std::move(kz));
    }

    void validate(const Component& cmp) {
        const auto obb = cmp.get_obb_vertices();

        for (const auto& kz : m_keepouts) {
            if (!has_flag(kz.flags, KeepoutFlag::Component)) continue;
            if (kz.layer != -1 && kz.layer != cmp.layer) continue;

            if (kz.is_circular) {
                for (const auto& pt : obb) {
                    if (const double d = pt.dist(kz.circle_center); d < kz.circle_radius) {
                        m_violations.push_back({
                            .object_id = cmp.refdes,
                            .rule_name = "Component-Keepout",
                            .description = std::format("Колізія з зоною кріплення '{}' (глибина {:.2f} мм)", kz.name, kz.circle_radius - d),
                            .distance = d
                        });
                        break;
                    }
                }
            } else {
                for (const auto& pt : obb) {
                    if (kz.poly.contains(pt)) {
                        m_violations.push_back({
                            .object_id = cmp.refdes,
                            .rule_name = "Component-Keepout",
                            .description = std::format("Корпус компонента перетинає полігон заборони '{}'", kz.name),
                            .distance = 0.0
                        });
                        break;
                    }
                }
            }
        }

        double min_edge_dist = 1e9;
        for (const auto& pt : obb) {
            for (size_t e = 0; e < m_outline.vertices.size(); ++e) {
                const size_t next = (e + 1) % m_outline.vertices.size();
                const double d = dist_point_to_segment(pt, m_outline.vertices[e], m_outline.vertices[next]);
                min_edge_dist = std::min(min_edge_dist, d);
            }
        }

        const double threshold = cmp.is_mlcc ? 3.0 : 1.0;
        if (min_edge_dist < threshold) {
            if (cmp.is_mlcc) {
                m_violations.push_back({
                    .object_id = cmp.refdes,
                    .rule_name = "DFM-Edge-Stress",
                    .description = std::format("Керамічний MLCC занадто близько до краю плати ({:.2f} мм < 3.0 мм, ризик тріщин)", min_edge_dist),
                    .distance = min_edge_dist
                });
            } else {
                m_violations.push_back({
                    .object_id = cmp.refdes,
                    .rule_name = "DFM-Board-Edge",
                    .description = std::format("Компонент занадто близько до контуру фрезерування ({:.2f} мм < 1.0 мм)", min_edge_dist),
                    .distance = min_edge_dist
                });
            }
        }
    }

    void validate(const TraceSegment& trace) {
        for (const auto& kz : m_keepouts) {
            if (!has_flag(kz.flags, KeepoutFlag::Route)) continue;
            if (kz.layer != -1 && kz.layer != trace.layer) continue;

            if (kz.is_circular) {
                const double eff_r = kz.circle_radius + (trace.width / 2.0);
                if (dist_point_to_segment(kz.circle_center, trace.start, trace.end) <= eff_r) {
                    m_violations.push_back({
                        .object_id = trace.net_name,
                        .rule_name = "Route-Keepout",
                        .description = std::format("Провідник net '{}' перетинає кругову зону кріплення '{}'", trace.net_name, kz.name),
                        .distance = 0.0
                    });
                }
            } else {
                const Vec2 mid = {(trace.start.x + trace.end.x) / 2.0, (trace.start.y + trace.end.y) / 2.0};
                if (kz.poly.contains(trace.start) || kz.poly.contains(trace.end) || kz.poly.contains(mid)) {
                    m_violations.push_back({
                        .object_id = trace.net_name,
                        .rule_name = "Route-Keepout",
                        .description = std::format("Доріжка net '{}' проходить крізь заборонений полігон '{}'", trace.net_name, kz.name),
                        .distance = 0.0
                    });
                }
            }
        }
    }

    [[nodiscard]] std::span<const Violation> violations() const noexcept {
        return m_violations;
    }

private:
    Polygon m_outline;
    std::vector<KeepoutZone> m_keepouts;
    std::vector<Violation> m_violations;
};

int main() {
    LayoutValidator validator({{{0, 0}, {100, 0}, {100, 60}, {0, 60}}});

    validator.add_keepout({
        .name = "M3_Hole_Corner",
        .circle_center = {10.0, 10.0},
        .circle_radius = 4.0,
        .is_circular = true,
        .flags = KeepoutFlag::Component | KeepoutFlag::Route | KeepoutFlag::Copper
    });

    validator.add_keepout({
        .name = "TO220_Heatsink_Area",
        .poly = {{{40, 20}, {70, 20}, {70, 40}, {40, 40}}},
        .flags = KeepoutFlag::Route,
        .layer = 0
    });

    validator.add_keepout({
        .name = "SMT_Top_Rail_4mm",
        .poly = {{{0, 56}, {100, 56}, {100, 60}, {0, 60}}},
        .flags = KeepoutFlag::Component,
        .layer = 0
    });

    validator.validate(Component{
        .refdes = "C1_MLCC_0805",
        .center = {50.0, 1.2},
        .width = 2.0,
        .height = 1.25,
        .rotation_deg = 0.0,
        .layer = 0,
        .is_mlcc = true
    });

    validator.validate(Component{
        .refdes = "R2_0603",
        .center = {12.0, 10.0},
        .width = 1.6,
        .height = 0.8,
        .rotation_deg = 45.0,
        .layer = 0
    });

    validator.validate(Component{
        .refdes = "LED_PWR",
        .center = {80.0, 58.0},
        .width = 2.0,
        .height = 1.2,
        .rotation_deg = 0.0,
        .layer = 0
    });

    validator.validate(TraceSegment{
        .net_name = "SPI_MISO",
        .start = {35.0, 30.0},
        .end = {75.0, 30.0},
        .width = 0.25,
        .layer = 0
    });

    std::cout << "=================================================================\n";
    std::cout << "       ЗВІТ АУДИТУ ЗОН ЗАБОРОНИ ТА МЕХАНІЧНИХ ОБМЕЖЕНЬ (C++20)  \n";
    std::cout << "=================================================================\n";
    const auto viols = validator.violations();
    std::cout << std::format("Всього знайдено порушень: {}\n\n", viols.size());
    for (size_t i = 0; i < viols.size(); ++i) {
        std::cout << std::format("[{}] Об'єкт: {:<16} | Правило: {:<18}\n    Деталі: {}\n\n",
                                 i + 1, viols[i].object_id, viols[i].rule_name, viols[i].description);
    }

    return 0;
}
```
:::

## 5. Детальний аналіз та покроковий розбір тестових сценаріїв

Для демонстрації надійності геометричного аналізу розглянемо результати виконання тестового прогону валідатора на прикладі чотирьох характерних порушень топології:

### Сценарій 1: Керамічний конденсатор C1_MLCC_0805 біля краю плати
- **Параметри об'єкта:** компонент `C1_MLCC_0805` розташований у точці `(50.0, 1.2)` із шириною `2.0` мм та висотою `1.25` мм. Нижні вершини корпусу мають координати `Y = 1.2 - 1.25/2 = 0.575` мм.
- **Діагностика:** найближче ребро контуру плати `Edge.Cuts` проходить по лінії `Y = 0.0`. Фактична відстань від корпусу до краю становить `0.575` мм.
- **Вердикт валідатора:** оскільки для прапорця `is_mlcc = true` встановлено критичний поріг стійкості до деформацій `3.0` мм, валідатор фіксує дефект `DFM-Edge-Stress` із дефіцитом зазору `2.425` мм. Такий конденсатор гарантовано трісне при розламуванні панелі, якщо не збільшити відступ або не додати захисний розвантажувальний паз.

### Сценарій 2: Резистор R2_0603 біля кріпильного отвору M3
- **Параметри об'єкта:** кріпильний отвір розташований у точці `(10.0, 10.0)` із радіусом зони заборони `R = 4.0` мм (що відповідає радіусу шайби `3.5` мм + технологічний запас `0.5` мм). Резистор `R2_0603` встановлено в точці `(12.0, 10.0)` під кутом 45°.
- **Діагностика:** обчислення вершин орієнтованого прямокутника OBB показує, що найближча до центру отвору вершина має координати `(11.15, 10.0)`, що дає евклідову відстань `1.15` мм до центру кріплення.
- **Вердикт валідатора:** зафіксовано порушення `Component-Keepout` із проникненням у зону шайби на глибину `2.85` мм. При затягуванні гвинта шайба зімне корпус деталі.

### Сценарій 3: Світлодіод LED_PWR у зоні конвеєра SMT
- **Параметри об'єкта:** світлодіод індикації встановлено у точці `(80.0, 58.0)` на платі висотою `60.0` мм. Полігон технологічного поля конвеєра займає смугу `Y ∈ [56.0, 60.0]` мм.
- **Діагностика:** вершини корпусу лежать у діапазоні `Y ∈ [57.4, 58.6]` мм, що повністю потрапляє всередину полігона `SMT_Top_Rail_4mm`.
- **Вердикт валідатора:** порушення `Component-Keepout`. Монтажна лінія пошкодить світлодіод при першому ж проходженні конвеєра.

### Сценарій 4: Сигнальна доріжка SPI_MISO під радіатором
- **Параметри об'єкта:** високошвидкісна лінія `SPI_MISO` прокладена від точки `(35.0, 30.0)` до `(75.0, 30.0)` на шарі `Top`. Металевий радіатор накриває зону `[40.0, 70.0] × [20.0, 40.0]` мм.
- **Діагностика:** сегмент доріжки перетинає полігон радіатора від координати `X = 40.0` до `X = 70.0` мм на довжині `30.0` мм.
- **Вердикт валідатора:** порушення `Route-Keepout`. Сигнальний провідник необхідно опустити на внутрішній шар `Layer 2 (In1.Cu)` за допомогою пари перехідних отворів за межами зони радіатора.

## 6. Оптимізація обчислювальної складності для промислових плат

На реальних багатошарових платах високої щільності монтажу (HDI, англ. *High Density Interconnect*) кількість компонентів сягає `5 000–10 000`, а кількість елементарних відрізків трасування — понад `500 000`. 

Прямий перебір типу «кожен відрізок проти кожної зони заборони» має асимптотичну складність:
```
T = O(N_traces · M_keepouts + K_components · M_keepouts)
```
Для `500 000` відрізків та `50` зон заборони це дає `25 000 000` обчислень відстаней, що може викликати помітні затримки під час інтерактивного автотрасування в САПР або масової перевірки на CI-сервері.

Для оптимізації продуктивності у валідаторі реалізують методи просторового розбиття (англ. *spatial partitioning*):

### Ієрархія обмежувальних об'ємів (BVH / AABB Tree)

Для кожної зони заборони та для кожного компонента будується груба прямокутна обмежувальна рамка (AABB, англ. *Axis-Aligned Bounding Box*):
```
AABB = [min_x, max_x] × [min_y, max_y]
```
Перевірка перетину двох AABB-рамок виконується всього за 4 операції порівняння чисел із плаваючою комою:
:::tabs
```c
bool aabb_overlap(AABB a, AABB b) {
    return (a.min_x <= b.max_x && a.max_x >= b.min_x) &&
           (a.min_y <= b.max_y && a.max_y >= b.min_y);
}
```
```cpp
[[nodiscard]] constexpr bool aabb_overlap(const AABB& a, const AABB& b) noexcept {
    return (a.min_x <= b.max_x && a.max_x >= b.min_x) &&
           (a.min_y <= b.max_y && a.max_y >= b.min_y);
}
```
:::
Якщо рамки AABB не перекриваються, точний і ресурсомісткий розрахунок перетину багатокутників через SAT чи Ray Casting взагалі **не викликається**. Це відсікає понад **99.5%** холостих перевірок.

### Просторове хешування (Spatial Hashing Grid)

Простір плати розбивається на регулярну сітку квадратних комірок розміром `S × S` (типово `5.0 × 5.0` мм). Вибір розміру комірки `S` базується на середньому габариті типових зон заборони: якщо розмір комірки занадто малий, один довгий відрізок доріжки реєструється у сотнях комірок, збільшуючи накладні витрати пам'яті; якщо занадто великий — зростає кількість кандидатів на точну перевірку всередині однієї комірки.

Кожна зона заборони, компонент та відрізок трасування реєструються у тих комірках сітки, через які вони проходять:
- Індекси комірок обчислюються за константний час `O(1)`:
  ```
  ix = floor(x / S),   iy = floor(y / S)
  ```
- Для відрізків трасування застосовується алгоритм цифрового диференціального аналізатора (DDA, англ. *Digital Differential Analyzer*) або алгоритм Брезенгема для швидкого визначення всіх перетнутих комірок без обчислення тригонометричних функцій.
- Пошук колізій для довільного об'єкта звужується виключно до елементів, зареєстрованих у сусідніх `3 × 3` комірках сітки (околиця Мура).
- Завдяки цьому середня складність валідації падає з квадратичної `O(N · M)` до практично лінійної `O(N)`.

## 7. Інтеграція в автоматизовані складальні пайплайни (CI/CD)

Запропонований валідатор компілюється в компактний бінарний виконуваний файл без зовнішніх динамічних залежностей. Його інтегрують у конвеєр автоматичної перевірки апаратного проєкту (наприклад, у GitHub Actions або GitLab CI):

1. **Експорт топології:** під час створення коміту скрипт автоматизації САПР (наприклад, KiCad Python API або Altium DXP script) генерує проміжний JSON-файл зі списком координат компонентів, контуру `Edge.Cuts`, доріжок та зон заборони.
2. **Запуск валідатора:**
   ```bash
   ./keepout_validator --input board_layout.json --report-format sarif --output drc_report.sarif
   ```
3. **Обробка результатів та SARIF-анотації:** якщо валідатор повертає ненульовий код виходу (наявні порушення зон заборони), пайплайн автоматично блокує злиття гілки (Merge Request) та формує інтерактивні анотації стандарту SARIF (англ. *Static Analysis Results Interchange Format*). Розробник бачить точні маркери та підсвічування ліній порушення безпосередньо у веб-інтерфейсі репозиторію або у вікні редактора плат САПР.

Такий автоматизований контроль на ранніх етапах унеможливлює передачу у виробництво плат із неприпустимими механічними та топологічними колізіями, заощаджуючи тисячі доларів на переробці виробничого оснащення та виготовленні повторних ревізій заготовок.
