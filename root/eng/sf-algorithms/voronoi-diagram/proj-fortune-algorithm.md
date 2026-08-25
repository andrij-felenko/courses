# ⚙️ Реалізація побудови діаграми Вороного: замітальна лінія Форчуна

Побудова діаграми Вороного алгоритмом Форчуна є однією з найвишуканіших задач обчислювальної геометрії: вона вимагає узгодженої динамічної взаємодії двох складних структур даних — дерева пляжної лінії та черги з пріоритетом геометричних подій.

Нижче наведено розбір внутрішніх інваріантів методу, повну реалізацію алгоритму мовами C та C++, включаючи обчислення точок зламу парабол, генерацію коло-подій, алгоритм відсікання нескінченних променів прямокутним вікном (*bounding box*) та порівняльний аналіз із підходом тривимірного підняття Квікхалла (*Qhull*).

## Архітектура структур даних та життєвий цикл об'єктів

У промисловій реалізації алгоритму виділяють чотири взаємопов'язані структури, що підтримують геометричний інваріант у міру просування замітальної прямої:

1. **Топологічні елементи (DCEL — Doubly Connected Edge List):**
   Кожне ребро діаграми Вороного зберігає індекси двох сайтів-генераторів, які воно розділяє (лівий та правий генератори), а також дві кінцеві вершини — початкову `start` та кінцеву `end`. На початку побудови, коли точка зламу тільки починає свій рух по серединному перпендикуляру, фіксується лише вектор напрямку `direction`. Якщо ребро є нескінченним променем, один із його кінців лишається невизначеним до етапу фінального кліпінгу на межах області перегляду.

2. **Дерево статусу пляжної лінії (*Beach Line*):**
   Пляжна лінія представляє горизонтальну послідовність параболічних дуг зліва направо. У збалансованому двійковому дереві пошуку листки відповідають активним дугам (і зберігають сайт-фокус `site`), а внутрішні вузли представляють рухомі точки зламу між сусідніми дугами. Коли дерево розщеплює листок при сайт-події, старий вузол замінюється піддеревом із трьох нових дуг.

3. **Черга подій (*Event Queue*):**
   Черга з пріоритетом впорядковує події за спаданням `Y`-координати (від найвищої до найнижчої). Існує два типи подій:
   - **Сайт-подія (`SITE`):** пряма зустрічає новий сайт, додаючи нову дугу в пляжну лінію.
   - **Коло-подія (`CIRCLE`):** дуга стискається в нуль у нижній точці описаного кола трьох сусідніх сайтів, утворюючи вершину Вороного.

4. **Інвалідація коло-подій (Lazy Deletion):**
   Коли між трьома суміжними дугами виникає потенційна коло-подія, вказівник на неї записується в середню дугу. Якщо пізніше новий сайт розщеплює будь-яку з цих трьох дуг, стара коло-подія втрачає геометричний сенс. Замість важкого пошуку та видалення події з середини двійкової купи, алгоритм просто виставляє прапорець `valid = false`. Під час вилучення з вершини купи невалідні події миттєво відкидаються.

## Програмна реалізація: C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define EPS 1e-9

typedef struct {
    double x;
    double y;
} Point;

typedef struct {
    Point start;
    Point end;
    Point direction;
    int site_left;
    int site_right;
    bool has_start;
    bool has_end;
} VoronoiEdge;

typedef enum { EVENT_SITE, EVENT_CIRCLE } EventType;

typedef struct Arc Arc;

typedef struct Event {
    double y;           /* Y-координата події для сортування в купі */
    Point point;        /* Координати сайта або центру кола */
    EventType type;
    Arc* arc;           /* Дуга, яка зникає (для коло-події) */
    bool valid;         /* Прапорець валідності події */
} Event;

struct Arc {
    Point site;
    int site_idx;
    Arc* prev;
    Arc* next;
    Event* circle_event;
    VoronoiEdge* edge_left;
    VoronoiEdge* edge_right;
};

/* Обчислення перетину двох парабол при поточному y_sweep */
static double get_breakpoint_x(Point p1, Point p2, double y_sweep) {
    if (fabs(p1.y - p2.y) < EPS) {
        return (p1.x + p2.x) / 2.0;
    }
    if (fabs(p1.y - y_sweep) < EPS) return p1.x;
    if (fabs(p2.y - y_sweep) < EPS) return p2.x;

    double d1 = 1.0 / (2.0 * (p1.y - y_sweep));
    double d2 = 1.0 / (2.0 * (p2.y - y_sweep));
    double a = d1 - d2;
    double b = 2.0 * (p2.x * d2 - p1.x * d1);
    double c = (p1.x * p1.x + p1.y * p1.y - y_sweep * y_sweep) * d1 -
               (p2.x * p2.x + p2.y * p2.y - y_sweep * y_sweep) * d2;

    double discr = b * b - 4.0 * a * c;
    if (discr < 0.0) discr = 0.0;
    double sq = sqrt(discr);

    double x1 = (-b + sq) / (2.0 * a);
    double x2 = (-b - sq) / (2.0 * a);

    return (p1.y < p2.y) ? fmax(x1, x2) : fmin(x1, x2);
}

/* Обчислення центру та радіуса описаного кола трьох точок */
static bool get_circumcenter(Point a, Point b, Point c, Point* center, double* bottom_y) {
    double d = 2.0 * (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y));
    if (d <= EPS) return false; /* Точки колінеарні або орієнтовані за стрілкою */

    double a2 = a.x * a.x + a.y * a.y;
    double b2 = b.x * b.x + b.y * b.y;
    double c2 = c.x * c.x + c.y * c.y;

    center->x = (a2 * (b.y - c.y) + b2 * (c.y - a.y) + c2 * (a.y - b.y)) / d;
    center->y = (a2 * (c.x - b.x) + b2 * (a.x - c.x) + c2 * (b.x - a.x)) / d;

    double r = hypot(center->x - a.x, center->y - a.y);
    *bottom_y = center->y - r;
    return true;
}

/* Черга подій: проста масивна реалізація пріоритетної черги */
typedef struct {
    Event* items[1024];
    int size;
} PriorityQueue;

static void pq_push(PriorityQueue* pq, Event* ev) {
    int i = pq->size++;
    while (i > 0) {
        int parent = (i - 1) / 2;
        if (pq->items[parent]->y >= ev->y) break;
        pq->items[i] = pq->items[parent];
        i = parent;
    }
    pq->items[i] = ev;
}

static Event* pq_pop(PriorityQueue* pq) {
    if (pq->size == 0) return NULL;
    Event* top = pq->items[0];
    Event* last = pq->items[--pq->size];
    if (pq->size > 0) {
        int i = 0;
        while (i * 2 + 1 < pq->size) {
            int left = i * 2 + 1;
            int right = i * 2 + 2;
            int best = left;
            if (right < pq->size && pq->items[right]->y > pq->items[left]->y) {
                best = right;
            }
            if (last->y >= pq->items[best]->y) break;
            pq->items[i] = pq->items[best];
            i = best;
        }
        pq->items[i] = last;
    }
    return top;
}

/* Динамічний масив вихідних ребер */
typedef struct {
    VoronoiEdge* data;
    int count;
    int capacity;
} EdgeList;

static VoronoiEdge* add_edge(EdgeList* list, int site1, int site2) {
    if (list->count >= list->capacity) {
        list->capacity = list->capacity == 0 ? 32 : list->capacity * 2;
        list->data = (VoronoiEdge*)realloc(list->data, list->capacity * sizeof(VoronoiEdge));
    }
    VoronoiEdge* e = &list->data[list->count++];
    e->site_left = site1;
    e->site_right = site2;
    e->has_start = false;
    e->has_end = false;
    return e;
}
```
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <memory>
#include <cmath>
#include <optional>
#include <algorithm>
#include <span>

constexpr double EPS = 1e-9;

struct Point {
    double x{0.0};
    double y{0.0};
};

struct VoronoiEdge {
    Point start{};
    Point end{};
    Point direction{};
    int site_left{-1};
    int site_right{-1};
    bool has_start{false};
    bool has_end{false};
};

enum class EventType { Site, Circle };

struct Arc;

struct Event {
    double y{0.0};
    Point point{};
    EventType type{EventType::Site};
    Arc* arc{nullptr};
    bool valid{true};
};

struct EventCompare {
    bool operator()(const std::shared_ptr<Event>& a, const std::shared_ptr<Event>& b) const noexcept {
        return a->y < b->y; // Максимальний Y обробляється першим
    }
};

struct Arc {
    Point site{};
    int site_idx{-1};
    Arc* prev{nullptr};
    Arc* next{nullptr};
    std::shared_ptr<Event> circle_event{nullptr};
    VoronoiEdge* edge_left{nullptr};
    VoronoiEdge* edge_right{nullptr};

    explicit Arc(Point s, int idx) : site(s), site_idx(idx) {}
};

class FortuneVoronoi {
public:
    explicit FortuneVoronoi(std::span<const Point> sites) : sites_(sites) {}

    std::vector<VoronoiEdge> build() {
        std::priority_queue<std::shared_ptr<Event>, 
                            std::vector<std::shared_ptr<Event>>, 
                            EventCompare> event_queue;

        for (int i = 0; i < static_cast<int>(sites_.size()); ++i) {
            auto ev = std::make_shared<Event>();
            ev->y = sites_[i].y;
            ev->point = sites_[i];
            ev->type = EventType::Site;
            ev->arc = nullptr;
            ev->valid = true;
            event_queue.push(std::move(ev));
        }

        Arc* root_arc = nullptr;

        while (!event_queue.empty()) {
            auto ev = event_queue.top();
            event_queue.pop();

            if (!ev->valid) continue;

            if (ev->type == EventType::Site) {
                handle_site_event(ev->point, root_arc, event_queue);
            } else {
                handle_circle_event(ev, root_arc, event_queue);
            }
        }

        clip_edges(Point{-1000.0, -1000.0}, Point{1000.0, 1000.0});
        return std::move(edges_);
    }

private:
    std::span<const Point> sites_;
    std::vector<VoronoiEdge> edges_;
    std::vector<std::unique_ptr<Arc>> arc_pool_;

    double get_breakpoint_x(Point p1, Point p2, double y_sweep) const noexcept {
        if (std::abs(p1.y - p2.y) < EPS) {
            return (p1.x + p2.x) / 2.0;
        }
        if (std::abs(p1.y - y_sweep) < EPS) return p1.x;
        if (std::abs(p2.y - y_sweep) < EPS) return p2.x;

        const double d1 = 1.0 / (2.0 * (p1.y - y_sweep));
        const double d2 = 1.0 / (2.0 * (p2.y - y_sweep));
        const double a = d1 - d2;
        const double b = 2.0 * (p2.x * d2 - p1.x * d1);
        const double c = (p1.x * p1.x + p1.y * p1.y - y_sweep * y_sweep) * d1 -
                         (p2.x * p2.x + p2.y * p2.y - y_sweep * y_sweep) * d2;

        const double discr = std::max(0.0, b * b - 4.0 * a * c);
        const double sq = std::sqrt(discr);

        const double x1 = (-b + sq) / (2.0 * a);
        const double x2 = (-b - sq) / (2.0 * a);

        return (p1.y < p2.y) ? std::max(x1, x2) : std::min(x1, x2);
    }

    std::optional<std::pair<Point, double>> get_circumcenter(Point a, Point b, Point c) const noexcept {
        const double d = 2.0 * (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y));
        if (d <= EPS) return std::nullopt;

        const double a2 = a.x * a.x + a.y * a.y;
        const double b2 = b.x * b.x + b.y * b.y;
        const double c2 = c.x * c.x + c.y * c.y;

        Point center{
            (a2 * (b.y - c.y) + b2 * (c.y - a.y) + c2 * (a.y - b.y)) / d,
            (a2 * (c.x - b.x) + b2 * (a.x - c.x) + c2 * (b.x - a.x)) / d
        };
        const double r = std::hypot(center.x - a.x, center.y - a.y);
        return std::make_pair(center, center.y - r);
    }

    void check_circle_event(Arc* arc, double y_sweep, auto& pq) {
        if (!arc || !arc->prev || !arc->next) return;

        if (auto res = get_circumcenter(arc->prev->site, arc->site, arc->next->site)) {
            const auto& [center, bottom_y] = *res;
            if (bottom_y <= y_sweep + EPS) {
                auto ev = std::make_shared<Event>();
                ev->y = bottom_y;
                ev->point = center;
                ev->type = EventType::Circle;
                ev->arc = arc;
                ev->valid = true;
                arc->circle_event = ev;
                pq.push(ev);
            }
        }
    }

    void handle_site_event(Point site, Arc*& root, auto& pq) {
        if (!root) {
            arc_pool_.push_back(std::make_unique<Arc>(site, 0));
            root = arc_pool_.back().get();
            return;
        }

        // Пошук дуги над новим сайтом
        Arc* curr = root;
        while (curr) {
            double left_x = curr->prev ? get_breakpoint_x(curr->prev->site, curr->site, site.y) : -1e9;
            double right_x = curr->next ? get_breakpoint_x(curr->site, curr->next->site, site.y) : 1e9;

            if (site.x >= left_x && site.x <= right_x) break;
            curr = curr->next;
        }
        if (!curr) curr = root;

        if (curr->circle_event) {
            curr->circle_event->valid = false;
            curr->circle_event = nullptr;
        }

        // Розщеплення дуги curr на curr -> new_arc -> right_arc
        arc_pool_.push_back(std::make_unique<Arc>(site, 0));
        Arc* middle = arc_pool_.back().get();

        arc_pool_.push_back(std::make_unique<Arc>(curr->site, curr->site_idx));
        Arc* right = arc_pool_.back().get();

        right->next = curr->next;
        if (right->next) right->next->prev = right;
        right->prev = middle;
        middle->next = right;
        middle->prev = curr;
        curr->next = middle;

        edges_.push_back(VoronoiEdge{
            .direction = Point{-(site.y - curr->site.y), site.x - curr->site.x},
            .site_left = curr->site_idx,
            .site_right = 0
        });
        VoronoiEdge* e = &edges_.back();

        curr->edge_right = e;
        middle->edge_left = e;
        middle->edge_right = e;
        right->edge_left = e;

        check_circle_event(curr, site.y, pq);
        check_circle_event(right, site.y, pq);
    }

    void handle_circle_event(const std::shared_ptr<Event>& ev, Arc*& root, auto& pq) {
        Arc* arc = ev->arc;
        Point vertex = ev->point;

        if (arc->edge_left) {
            arc->edge_left->end = vertex;
            arc->edge_left->has_end = true;
        }
        if (arc->edge_right) {
            arc->edge_right->start = vertex;
            arc->edge_right->has_start = true;
        }

        edges_.push_back(VoronoiEdge{
            .start = vertex,
            .direction = Point{-(arc->next->site.y - arc->prev->site.y), 
                               arc->next->site.x - arc->prev->site.x},
            .has_start = true
        });
        VoronoiEdge* new_edge = &edges_.back();

        if (arc->prev) {
            arc->prev->next = arc->next;
            arc->prev->edge_right = new_edge;
        }
        if (arc->next) {
            arc->next->prev = arc->prev;
            arc->next->edge_left = new_edge;
        }
        if (arc == root) root = arc->next ? arc->next : arc->prev;

        if (arc->prev) check_circle_event(arc->prev, ev->y, pq);
        if (arc->next) check_circle_event(arc->next, ev->y, pq);
    }

    void clip_edges(Point min_box, Point max_box) noexcept {
        for (auto& edge : edges_) {
            if (!edge.has_start && !edge.has_end) {
                edge.start = Point{min_box.x, min_box.y};
                edge.end = Point{max_box.x, max_box.y};
            } else if (edge.has_start && !edge.has_end) {
                edge.end = Point{
                    edge.start.x + edge.direction.x * 2000.0,
                    edge.start.y + edge.direction.y * 2000.0
                };
            }
        }
    }
};
```
:::

## Покроковий розбір обробки подій

Розглянемо детальніше математику двох ключових обробників:

### 1. Розщеплення дуги при сайт-події (`handle_site_event`)

Коли черга подій видає новий сайт `p_new(x_s, y_s)`:
1. За допомогою бінарного пошуку в дереві статусу (або лінійного проходу по зв'язаному списку) знаходиться активна дуга `α(p_curr)`, яка розташована строго над координатою `x_s`.
2. Якщо над дугою `α(p_curr)` уже висіла запланована коло-подія, вона інвалідується (`valid = false`), оскільки нова дуга розриває старе геометричне сусідство.
3. Дуга `α(p_curr)` замінюється ланцюжком із трьох дуг: ліва копія `α(p_curr)`, нова дуга `α(p_new)` та права копія `α(p_curr)`.
4. Створюється нове напівребро Вороного, напрямок якого перпендикулярний до вектора `(p_new − p_curr)`.
5. Для двох новоутворених трійок дуг `(prev, curr_left, new)` та `(new, curr_right, next)` викликається перевірка потенційних коло-подій.

### 2. Замикання вершини при коло-події (`handle_circle_event`)

Коли замітальна пряма досягає нижньої точки описаного кола трьох сусідніх дуг `(α(p_left), α(p_mid), α(p_right))`:
1. Точка центру кола `center` стає новою вершиною Вороного `v`.
2. Два ребра, які відстежували рух лівої та правої точок зламу дуги `α(p_mid)`, завершуються у знайденій вершині `v`.
3. Створюється нове ребро, спрямоване вниз по серединному перпендикуляру між `p_left` та `p_right`. Початок цього ребра встановлюється у вершину `v`.
4. Дуга `α(p_mid)` повністю видаляється зі списку/дерева статусу.
5. Сусіди `α(p_left)` та `α(p_right)` стають безпосередньо суміжними. Для нових трійок дуг перераховуються майбутні коло-події.

## Кліпінг променів на прямокутному вікні

Оскільки сайти на опуклій оболонці генерують незамкнені комірки Вороного, відповідні ребра є нескінченними променями. Для відображення на екрані або збереження в структури полігонів ці промені перетинаються з межами обмежувального прямокутника (*bounding box*) `[x_min, x_max] × [y_min, y_max]`.

Для променя з початком `(x₀, y₀)` та напрямком `(d_x, d_y)` значення параметра `t > 0` знаходиться через перетин із чотирма прямими меж:

```
t_x1 = (x_min − x₀) / d_x
t_x2 = (x_max − x₀) / d_x
t_y1 = (y_min − y₀) / d_y
t_y2 = (y_max − y₀) / d_y
```

Вибирається мінімальне додатне значення `t = min{t_i > 0}`, що дає точну точку виходу променя за межі розрахункової області `(x₀ + t·d_x, y₀ + t·d_y)`.

## Альтернативи реалізації: замітання проти 3D-підняття (Qhull)

Хоча алгоритм Форчуна є канонічним методом площинного замітання, на практиці часто використовують дуальний підхід геометричного підняття:

1. **Проекція на параболоїд обертання:** кожній 2D-точці `p(x, y)` зіставляється 3D-точка `P(x, y, x² + y²)`.
2. **Побудова 3D-опуклої оболонки:** за допомогою алгоритму Quickhull обчислюється тривимірна опукла оболонка множини піднятих точок.
3. **Проекція нижніх граней:** грані опуклої оболонки, вектори нормалей яких спрямовані вниз (від'ємна `Z`-компонента), при проектуванні назад на площину `XY` утворюють точну тріангуляцію Делоне.
4. **Дуальний перехід до Вороного:** центри описаних кіл отриманих трикутників дають вершини Вороного, а зв'язки між суміжними трикутниками — ребра діаграми.

Алгоритм Форчуна є більш пам'ять-ефективним у 2D, оскільки опрацьовує геометрію за один лінійний прохід і не потребує зберігання повного тривимірного фасетного графу. Проте метод підняття є значно простішим для узагальнення на простори вищих розмірностей (`N ≥ 3`).
