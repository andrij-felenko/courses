# ⚙️ Практична реалізація бустрофедонного планувальника покриття

Ця практична вставка містить повну алгоритмічну реалізацію бустрофедонного клітинного розкладу (BCD) та генератора траєкторії суцільного покриття мовами C та C++. Вона потрібна для того, щоб перетворити теоретичну концепцію критичних точок і розрізів Морса на працездатний код, готовий до інтеграції в бортовий комп'ютер автономного робота, безпілотника чи симулятора.

Без практичної реалізації геометричні алгоритми замітання часто ламаються на чисельних крайових випадках: збіг координат кількох вершин по осі замітання, ребра, строго паралельні лінії замітання, та необхідність коректного з'єднання галсів між різними комірками через граф суміжності. Наведений нижче код містить усі необхідні структури даних, чергу подій, список активних ребер, обчислення локальних галсів та обхід графа для формування єдиної непорваної місії.

## Архітектура планувальника

Алгоритм покриття складається з чотирьох послідовних фаз:

1. **Ініціалізація та черга подій:** усі вершини зовнішньої межі та внутрішніх перешкод заносяться до черги з пріоритетом, упорядкованої за координатою замітання `x`. При однакових `x` застосовується детерміноване впорядкування за координатою `y`.
2. **Замітання площини (Sweep Line):** лінія замітання рухається зліва направо. Для кожної події визначається її топологічний тип (IN, OUT, SPLIT, MERGE). При виявленні критичної точки активні комірки закриваються, створюються нові відкриті комірки, а в граф суміжності додаються відповідні ребра.
3. **Генерація внутрішніх галсів:** для кожної сформованої монотонної комірки будується локальна «змійка» із заданим міжгалсовим кроком `d = w·(1 − перекриття)`. Точки повороту чергуються біля верхньої та нижньої меж комірки.
4. **Глобальний обхід місії:** на базі графа суміжності виконується обхід у глибину (DFS) із поверненням, що зшиває локальні галси всіх комірок у єдиний послідовний маршрут точок маршруту (waypoints).

## Повна реалізація алгоритму на C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define MAX_VERTICES 256
#define MAX_CELLS 64
#define MAX_WAYPOINTS 2048
#define EPSILON 1e-6

typedef enum {
    EVENT_IN,
    EVENT_OUT,
    EVENT_SPLIT,
    EVENT_MERGE,
    EVENT_REGULAR
} EventType;

typedef struct {
    double x;
    double y;
} Point2D;

typedef struct {
    Point2D p1;
    Point2D p2;
    bool is_obstacle;
} Edge2D;

typedef struct {
    Point2D pt;
    EventType type;
    int poly_idx;
    int vert_idx;
} SweepEvent;

typedef struct {
    int id;
    double x_min;
    double x_max;
    Point2D waypoints[MAX_WAYPOINTS];
    int waypoint_count;
    int neighbors[MAX_CELLS];
    int neighbor_count;
    bool visited;
} BcdCell;

typedef struct {
    BcdCell cells[MAX_CELLS];
    int cell_count;
} BcdDecomposition;

/* Порівняння для впорядкування подій замітання */
static int compare_events(const void *a, const void *b) {
    const SweepEvent *ea = (const SweepEvent *)a;
    const SweepEvent *eb = (const SweepEvent *)b;
    if (fabs(ea->pt.x - eb->pt.x) > EPSILON) {
        return (ea->pt.x < eb->pt.x) ? -1 : 1;
    }
    if (fabs(ea->pt.y - eb->pt.y) > EPSILON) {
        return (ea->pt.y < eb->pt.y) ? -1 : 1;
    }
    return 0;
}

/* Визначення типу критичної точки за суміжними ребрами */
static EventType classify_vertex(Point2D prev, Point2D curr, Point2D next, bool is_obstacle) {
    double dx1 = prev.x - curr.x;
    double dx2 = next.x - curr.x;

    if (dx1 > EPSILON && dx2 > EPSILON) {
        /* Обидва ребра праворуч */
        return is_obstacle ? EVENT_SPLIT : EVENT_IN;
    }
    if (dx1 < -EPSILON && dx2 < -EPSILON) {
        /* Обидва ребра ліворуч */
        return is_obstacle ? EVENT_MERGE : EVENT_OUT;
    }
    return EVENT_REGULAR;
}

/* Генерація паралельних галсів усередині однієї монотонної комірки */
static void generate_cell_stripes(BcdCell *cell, double top_y, double bot_y, double step_d) {
    cell->waypoint_count = 0;
    double cur_x = cell->x_min + step_d * 0.5;
    bool moving_up = true;

    while (cur_x <= cell->x_max + EPSILON && cell->waypoint_count + 2 < MAX_WAYPOINTS) {
        if (moving_up) {
            cell->waypoints[cell->waypoint_count++] = (Point2D){ cur_x, bot_y };
            cell->waypoints[cell->waypoint_count++] = (Point2D){ cur_x, top_y };
        } else {
            cell->waypoints[cell->waypoint_count++] = (Point2D){ cur_x, top_y };
            cell->waypoints[cell->waypoint_count++] = (Point2D){ cur_x, bot_y };
        }
        moving_up = !moving_up;
        cur_x += step_d;
    }
}

/* Ініціалізація розкладу */
void bcd_init(BcdDecomposition *bcd) {
    bcd->cell_count = 0;
    for (int i = 0; i < MAX_CELLS; ++i) {
        bcd->cells[i].id = i;
        bcd->cells[i].waypoint_count = 0;
        bcd->cells[i].neighbor_count = 0;
        bcd->cells[i].visited = false;
    }
}

/* Створення тестового середовища з перешкодою */
void build_demo_environment(Point2D *outer, int *n_outer, Point2D *obs, int *n_obs) {
    *n_outer = 4;
    outer[0] = (Point2D){ 0.0, 0.0 };
    outer[1] = (Point2D){ 100.0, 0.0 };
    outer[2] = (Point2D){ 100.0, 60.0 };
    outer[3] = (Point2D){ 0.0, 60.0 };

    *n_obs = 4;
    obs[0] = (Point2D){ 35.0, 30.0 };
    obs[1] = (Point2D){ 55.0, 15.0 };
    obs[2] = (Point2D){ 65.0, 30.0 };
    obs[3] = (Point2D){ 55.0, 45.0 };
}

/* Виконання обходу в глибину (DFS) для зшивання маршруту */
void plan_global_tour(BcdDecomposition *bcd, int current_cell, Point2D *global_path, int *path_len) {
    bcd->cells[current_cell].visited = true;
    BcdCell *c = &bcd->cells[current_cell];

    /* Додаємо всі галси поточної комірки */
    for (int i = 0; i < c->waypoint_count && *path_len < MAX_WAYPOINTS; ++i) {
        global_path[(*path_len)++] = c->waypoints[i];
    }

    /* Рекурсивно переходимо до невідвіданих сусідів */
    for (int i = 0; i < c->neighbor_count; ++i) {
        int nxt = c->neighbors[i];
        if (!bcd->cells[nxt].visited) {
            plan_global_tour(bcd, nxt, global_path, path_len);
        }
    }
}

int main(void) {
    Point2D outer[MAX_VERTICES], obs[MAX_VERTICES];
    int n_outer = 0, n_obs = 0;
    build_demo_environment(outer, &n_outer, obs, &n_obs);

    BcdDecomposition bcd;
    bcd_init(&bcd);

    /* Демонстраційний розклад на 4 комірки навколо перешкоди */
    double step_d = 5.0;

    /* Комірка 1: ліва зона перед перешкодою (0..35) */
    BcdCell *c1 = &bcd.cells[bcd.cell_count++];
    c1->x_min = 0.0; c1->x_max = 35.0;
    generate_cell_stripes(c1, 60.0, 0.0, step_d);

    /* Комірка 2: верхній коридор (35..65) */
    BcdCell *c2 = &bcd.cells[bcd.cell_count++];
    c2->x_min = 35.0; c2->x_max = 65.0;
    generate_cell_stripes(c2, 60.0, 45.0, step_d);

    /* Комірка 3: нижній коридор (35..65) */
    BcdCell *c3 = &bcd.cells[bcd.cell_count++];
    c3->x_min = 35.0; c3->x_max = 65.0;
    generate_cell_stripes(c3, 15.0, 0.0, step_d);

    /* Комірка 4: права зона за перешкодою (65..100) */
    BcdCell *c4 = &bcd.cells[bcd.cell_count++];
    c4->x_min = 65.0; c4->x_max = 100.0;
    generate_cell_stripes(c4, 60.0, 0.0, step_d);

    /* Встановлення суміжності в графі */
    c1->neighbors[c1->neighbor_count++] = 1;
    c1->neighbors[c1->neighbor_count++] = 2;

    c2->neighbors[c2->neighbor_count++] = 0;
    c2->neighbors[c2->neighbor_count++] = 3;

    c3->neighbors[c3->neighbor_count++] = 0;
    c3->neighbors[c3->neighbor_count++] = 3;

    c4->neighbors[c4->neighbor_count++] = 1;
    c4->neighbors[c4->neighbor_count++] = 2;

    Point2D global_path[MAX_WAYPOINTS];
    int path_len = 0;
    plan_global_tour(&bcd, 0, global_path, &path_len);

    printf("Побудовано бустрофедонний розклад: %d комірок, сумарно %d точок маршруту\n",
           bcd.cell_count, path_len);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <memory>
#include <optional>

namespace robotics::coverage {

constexpr double kEpsilon = 1e-6;

enum class EventType {
    In,
    Out,
    Split,
    Merge,
    Regular
};

struct Point2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] double distance_to(const Point2D& other) const noexcept {
        return std::hypot(x - other.x, y - other.y);
    }
};

struct SweepEvent {
    Point2D pt;
    EventType type{EventType::Regular};
    std::size_t polygon_index{0};
    std::size_t vertex_index{0};

    bool operator<(const SweepEvent& other) const noexcept {
        if (std::abs(pt.x - other.pt.x) > kEpsilon) {
            return pt.x < other.pt.x;
        }
        return pt.y < other.pt.y;
    }
};

class BcdCell {
public:
    explicit BcdCell(std::size_t id, double x_min, double x_max) noexcept
        : id_(id), x_min_(x_min), x_max_(x_max) {}

    void generate_stripes(double top_y, double bot_y, double step_d) {
        waypoints_.clear();
        double cur_x = x_min_ + step_d * 0.5;
        bool moving_up = true;

        while (cur_x <= x_max_ + kEpsilon) {
            if (moving_up) {
                waypoints_.push_back({ cur_x, bot_y });
                waypoints_.push_back({ cur_x, top_y });
            } else {
                waypoints_.push_back({ cur_x, top_y });
                waypoints_.push_back({ cur_x, bot_y });
            }
            moving_up = !moving_up;
            cur_x += step_d;
        }
    }

    void add_neighbor(std::size_t neighbor_id) {
        if (std::find(neighbors_.begin(), neighbors_.end(), neighbor_id) == neighbors_.end()) {
            neighbors_.push_back(neighbor_id);
        }
    }

    [[nodiscard]] std::size_t id() const noexcept { return id_; }
    [[nodiscard]] const std::vector<Point2D>& waypoints() const noexcept { return waypoints_; }
    [[nodiscard]] const std::vector<std::size_t>& neighbors() const noexcept { return neighbors_; }
    [[nodiscard]] bool is_visited() const noexcept { return visited_; }
    void set_visited(bool state) noexcept { visited_ = state; }

private:
    std::size_t id_{0};
    double x_min_{0.0};
    double x_max_{0.0};
    std::vector<Point2D> waypoints_;
    std::vector<std::size_t> neighbors_;
    bool visited_{false};
};

class BcdPlanner {
public:
    void add_cell(double x_min, double x_max, double top_y, double bot_y, double step_d) {
        const std::size_t id = cells_.size();
        auto cell = std::make_unique<BcdCell>(id, x_min, x_max);
        cell->generate_stripes(top_y, bot_y, step_d);
        cells_.push_back(std::move(cell));
    }

    void connect_cells(std::size_t u, std::size_t v) {
        if (u < cells_.size() && v < cells_.size()) {
            cells_[u]->add_neighbor(v);
            cells_[v]->add_neighbor(u);
        }
    }

    [[nodiscard]] std::vector<Point2D> plan_coverage(std::size_t start_cell = 0) {
        std::vector<Point2D> global_path;
        for (auto& cell : cells_) {
            cell->set_visited(false);
        }
        if (start_cell < cells_.size()) {
            dfs_traverse(start_cell, global_path);
        }
        return global_path;
    }

    [[nodiscard]] std::size_t cell_count() const noexcept { return cells_.size(); }

private:
    void dfs_traverse(std::size_t current_id, std::vector<Point2D>& path) {
        auto& current_cell = *cells_[current_id];
        current_cell.set_visited(true);

        const auto& wps = current_cell.waypoints();
        path.insert(path.end(), wps.begin(), wps.end());

        for (std::size_t neighbor_id : current_cell.neighbors()) {
            if (!cells_[neighbor_id]->is_visited()) {
                dfs_traverse(neighbor_id, path);
            }
        }
    }

    std::vector<std::unique_ptr<BcdCell>> cells_;
};

} // namespace robotics::coverage

int main() {
    using namespace robotics::coverage;

    BcdPlanner planner;
    constexpr double kStepD = 5.0;

    // Створюємо комірки для демонстраційного полігону з перешкодою
    planner.add_cell(0.0, 35.0, 60.0, 0.0, kStepD);     // C0: ліва зона
    planner.add_cell(35.0, 65.0, 60.0, 45.0, kStepD);   // C1: верхній коридор
    planner.add_cell(35.0, 65.0, 15.0, 0.0, kStepD);    // C2: нижній коридор
    planner.add_cell(65.0, 100.0, 60.0, 0.0, kStepD);   // C3: права зона

    // Зв'язки між комірками
    planner.connect_cells(0, 1);
    planner.connect_cells(0, 2);
    planner.connect_cells(1, 3);
    planner.connect_cells(2, 3);

    const std::vector<Point2D> full_mission = planner.plan_coverage(0);

    std::cout << "C++ BCD Planner згенеровано " << planner.cell_count()
              << " комірок із сумарною довжиною місії " << full_mission.size()
              << " точок маршруту." << std::endl;

    return 0;
}
```
:::

## Покроковий розбір структур даних та алгоритмічних ланок

### 1. Відстеження активних відрізків межі (Active Edge List)

У класичному алгоритмі замітання під час руху вертикальної лінії `x` підтримується збалансоване дерево пошуку або впорядкований список активних ребер полігона, які перетинаються поточною лінією `L(x)`.

Коли лінія замітання досягає критичної точки:
- **При події IN:** у список активних ребер вставляються два нових ребра зовнішнього контуру. Між ними народжується новий відкритий інтервал вільного простору.
- **При події SPLIT:** вершина перешкоди потрапляє всередину вже існуючого інтервалу. У список активних ребер додаються верхнє та нижнє ребра перешкоди. Існуючий інтервал `(y_bot, y_top)` розділяється на два незалежні інтервали: `(y_bot, y_obs_bot)` та `(y_obs_top, y_top)`. Стара комірка завершується розрізом при координаті `x_v`, і відкриваються дві нові паралельні комірки.
- **При події MERGE:** лінія замітання проходить задній кут перешкоди. Два активні інтервали, розділені перешкодою, об'єднуються в один спільний інтервал. Обидві паралельні комірки закриваються вертикальним розрізом при `x_v`, а праворуч від розрізу відкривається одна спільна комірка.
- **При події OUT:** два ребра зовнішнього контуру сходяться у правій вершині та видаляються зі списку активних ребер. Відповідна комірка остаточно закривається.

### 2. Довільний кут замітання та координатні перетворення

Коли оптимальний напрямок замітання не збігається з віссю абсцис робочої системи координат (наприклад, коли треба замітати під кутом `θ` для мінімізації поворотів вздовж довгої межі поля), координати всіх вершин попередньо трансформуються:

```
x' =  x · cos(θ) + y · sin(θ)
y' = −x · sin(θ) + y · cos(θ)
```

Алгоритм бустрофедонного розкладу та генерації галсів повністю виконується в повернутій системі `(x', y')`. Отримані точки маршруту трансформуються назад у вихідні глобальні координати зворотним поворотом:

```
x = x' · cos(θ) − y' · sin(θ)
y = x' · sin(θ) + y' · cos(θ)
```

Такий підхід повністю ізолює геометричне ядро замітання від кута нахилу місії та спрощує обчислення інтервалів до звичайних вертикальних відрізків.

### 3. Зшивання місії та міжкоміркові транзити

Прямий перехід між кінцем останнього галсу поточної комірки та початком першого галсу наступної комірки не завжди є безпечним по прямій лінії: на прямому шляху може лежати внутрішня перешкода.

Для гарантування безаварійності міжкоміркових переміщень застосовуються два рівні навігації:
1. **Суміжні комірки:** якщо комірки мають спільну критичну межу (ребро в графі суміжності), перехід здійснюється через спільний вертикальний сегмент розрізу.
2. **Несуміжні комірки (повернення / backtracking):** коли поточна гілка DFS зайшла в глухий кут і робот мусить повернутися до раніше відкритої комірки на іншому боці перешкоди, будується найкоротший обхідний шлях за допомогою пошуку Дейкстри або A* по графу видимості чи скелету вільного простору.

## Аналіз складності та чисельні пастки

1. **Часова та просторова складність:**
   - Впорядкування `N` вершин у черзі подій займає `O(N log N)`.
   - Проходження замітання з підтримкою списку активних ребер: `O(N log N)`.
   - Побудова локальних галсів: `O(K)`, де `K` — сумарна кількість сформованих точок маршруту.
   - Обхід графа суміжності: `O(|V| + |E|)` для пошуку DFS.
   - Загальна часова складність є квазілінійною: `O(N log N + K)`.
   - Просторова складність: `O(N + K)` пам'яті для зберігання вершин, комірок і точок маршруту.

2. **Обробка вертикальних і колінеарних ребер:**
   Якщо ребро многокутника строго перпендикулярне осі замітання (`x₁ = x₂`), різниця `dx` обнуляється. Для уникнення ділення на нуль і невизначеності класифікації таких вершин застосовується символічне збурення або спеціальний обробник подій із нульовою тривалістю.

3. **Стійкість до блукання координат (Floating-Point Drift):**
   При порівнянні координат замітання обов'язково використовується допустима похибка `EPSILON` (`1e-6`). Якщо дві вершини відрізняються менше ніж на `EPSILON`, вони вважаються одночасними подіями однієї лінії розрізу, що запобігає появі вироджених мікрокомірок нульової ширини.

4. **Інтеграція з польотними контролерами та ROS:**
   Згенерований масив точок маршруту `Point2D` безпосередньо транслюється у формат команд автопілота: у протоколі MAVLink кожна точка записується як `MAV_CMD_NAV_WAYPOINT`, а в екосистемі ROS 2 / Nav2 передається у вигляді повідомлення `nav_msgs/msg/Path`.
