# ⚙️ Інкрементна тріангуляція Делоне: алгоритм Бойєра–Ватсона

Алгоритм Бойєра–Ватсона (*Bowyer–Watson algorithm*) — це класичний інкрементний метод побудови тріангуляції Делоне для довільної дискретної множини точок на евклідовій площині `ℝ²`. Він базується на послідовному додаванні точок по одній у вже збудовану сітку з локальним видаленням порушених трикутників та повторним заповненням зірчастої порожнини.

## Постановка задачі та алгоритмічна ідея

**Вхідні дані:** Множина з `N` двовимірних точок `P = {p₁, p₂, ..., p_N}` у довільному просторовому положенні на площині.
**Вихідні дані:** Набір трикутників `T = {t₁, t₂, ..., t_M}`, що задовольняють критерій порожнього описаного кола Делоне та утворюють планарне розбиття опуклої оболонки `CH(P)`.

Головна перевага алгоритму полягає в його строго локальному характері: замість глобальної перебудови всієї геометричної структури вставка нової вершини змінює лише ті трикутники, чиї описані кола безпосередньо покривають нову точку.

Алгоритм виконує такі послідовні фази:

### 1. Побудова охопного супертрикутника (Super-Triangle)

Оскільки алгоритм є інкрементним, йому потрібна початкова коректна тріангуляція, у яку можна гарантовано вставити першу точку множини даних. Для цього:
- Обчислюють мінімальні та максимальні координати `min_x, max_x, min_y, max_y` множини точок (обмежувальний прямокутник / *bounding box*).
- Будують один великий допоміжний трикутник з вершинами `st_a, st_b, st_c`, розміри якого у 20–50 разів перевищують габарити вихідного набору даних.
- Цей супертрикутник поміщають у результуючий список сітки `T` як єдиний початковий елемент. Усі вхідні точки множини `P` гарантовано лежать строго всередині його площі.

### 2. Інкрементна вставка та формування каверни

Для кожної чергової точки `p ∈ P`:
1. **Пошук порушених граней:** Обходять усі поточні трикутники `t ∈ T`. За допомогою геометричного предикату `in_circumcircle(t.a, t.b, t.c, p)` визначають, чи потрапляє точка `p` всередину відкритого описаного круга трикутника `t`. Трикутники з додатним значенням предикату позначаються як «недійсні» (*bad triangles*).
2. **Виділення межі каверни:** Недійсні трикутники утворюють єдину суцільну область — **полігональну каверну** (порожнину). Внутрішні спільні ребра між недійсними трикутниками мають бути видалені, а зовнішні ребра, які межують із коректною частиною сітки, утворюють замкнений контур каверни. Ребро належить межі каверни тоді й лише тоді, коли воно фігурує у списку ребер недійсних трикутників рівно один раз.
3. **Видалення та повторна тріангуляція:** Усі недійсні трикутники вилучаються із сітки `T`. Для кожного межового ребра `e` створюється новий трикутник `Δ(e.a, e.b, p)`. Оскільки каверна гарантовано є зірчастим многокутником відносно точки `p`, нові трикутники заповнюють порожнину без взаємних перекриттів та самоперетинів.

### 3. Очищення від допоміжних вершин

Після завершення ітерацій за всіма вхідними точками з фінальної сітки `T` видаляють усі трикутники, які мають хоча б одну спільну вершину з супертрикутником (`st_a, st_b` або `st_c`). Залишаються виключно трикутники, натягнуті на точки вихідної множини `P`, які в точності утворюють тріангуляцію Делоне для опуклої оболонки вихідних точок.

## Практична реалізація: C та C++

Нижче наведено самодостатню, оптимізовану реалізацію алгоритму Бойєра–Ватсона мовами C та C++ із коректним керуванням динамічною пам'яттю, числовими предикатами та структурами даних.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double x;
    double y;
} Point2D;

typedef struct {
    Point2D a;
    Point2D b;
} Edge2D;

typedef struct {
    Point2D a;
    Point2D b;
    Point2D c;
} Triangle2D;

/* Перевірка збігу двох точок із числовою точністю */
static inline bool point_equals(Point2D p1, Point2D p2) {
    return fabs(p1.x - p2.x) < 1e-9 && fabs(p1.y - p2.y) < 1e-9;
}

/* Перевірка збігу двох ребер без урахування напрямку */
static inline bool edge_equals(Edge2D e1, Edge2D e2) {
    return (point_equals(e1.a, e2.a) && point_equals(e1.b, e2.b)) ||
           (point_equals(e1.a, e2.b) && point_equals(e1.b, e2.a));
}

/* Перевірка, чи містить трикутник задану вершину */
static inline bool triangle_has_vertex(Triangle2D t, Point2D p) {
    return point_equals(t.a, p) || point_equals(t.b, p) || point_equals(t.c, p);
}

/* Орієнтований подвійний трикутник (CCW > 0) */
static inline double orientation_ccw(Point2D a, Point2D b, Point2D c) {
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
}

/* Предикат InCircle: чи лежить точка d всередині описаного кола трикутника abc */
bool in_circumcircle(Point2D a, Point2D b, Point2D c, Point2D d) {
    /* Якщо трикутник орієнтований CW, міняємо місцями b та c */
    if (orientation_ccw(a, b, c) < 0.0) {
        Point2D tmp = b;
        b = c;
        c = tmp;
    }

    double adx = a.x - d.x;
    double ady = a.y - d.y;
    double bdx = b.x - d.x;
    double bdy = b.y - d.y;
    double cdx = c.x - d.x;
    double cdy = c.y - d.y;

    double ab_det = adx * bdy - ady * bdx;
    double bc_det = bdx * cdy - bdy * cdx;
    double ca_det = cdx * ady - cdy * adx;

    double alift = adx * adx + ady * ady;
    double blift = bdx * bdx + bdy * bdy;
    double clift = cdx * cdx + cdy * cdy;

    double det = alift * bc_det + blift * ca_det + clift * ab_det;
    return det > 1e-12;
}

/* Динамічний масив трикутників */
typedef struct {
    Triangle2D* data;
    size_t size;
    size_t capacity;
} TriangleVector;

static void tri_vector_init(TriangleVector* v, size_t cap) {
    v->data = (Triangle2D*)malloc(cap * sizeof(Triangle2D));
    v->size = 0;
    v->capacity = cap;
}

static void tri_vector_push(TriangleVector* v, Triangle2D t) {
    if (v->size >= v->capacity) {
        v->capacity = v->capacity == 0 ? 8 : v->capacity * 2;
        v->data = (Triangle2D*)realloc(v->data, v->capacity * sizeof(Triangle2D));
    }
    v->data[v->size++] = t;
}

static void tri_vector_free(TriangleVector* v) {
    free(v->data);
    v->data = NULL;
    v->size = v->capacity = 0;
}

/* Інкрементний алгоритм Бойєра-Ватсона */
TriangleVector bowyer_watson(const Point2D* points, size_t n) {
    TriangleVector mesh;
    tri_vector_init(&mesh, 16);
    if (n == 0) return mesh;

    /* Обчислення Bounding Box */
    double min_x = points[0].x, max_x = points[0].x;
    double min_y = points[0].y, max_y = points[0].y;
    for (size_t i = 1; i < n; ++i) {
        if (points[i].x < min_x) min_x = points[i].x;
        if (points[i].x > max_x) max_x = points[i].x;
        if (points[i].y < min_y) min_y = points[i].y;
        if (points[i].y > max_y) max_y = points[i].y;
    }

    double dx = max_x - min_x;
    double dy = max_y - min_y;
    double delta_max = (dx > dy ? dx : dy) * 20.0;
    if (delta_max < 1e-5) delta_max = 100.0;
    double mid_x = (min_x + max_x) * 0.5;
    double mid_y = (min_y + max_y) * 0.5;

    /* Побудова супертрикутника */
    Point2D st_a = { mid_x - delta_max, mid_y - delta_max };
    Point2D st_b = { mid_x + delta_max, mid_y - delta_max };
    Point2D st_c = { mid_x, mid_y + delta_max };
    Triangle2D super_tri = { st_a, st_b, st_c };

    tri_vector_push(&mesh, super_tri);

    /* Тимчасові буфери для полігональної порожнини */
    Edge2D* polygon = (Edge2D*)malloc(1024 * sizeof(Edge2D));
    size_t poly_capacity = 1024;

    for (size_t p_idx = 0; p_idx < n; ++p_idx) {
        Point2D pt = points[p_idx];
        size_t poly_size = 0;

        /* Знаходимо недійсні трикутники та збираємо їхні ребра */
        size_t write_idx = 0;
        for (size_t i = 0; i < mesh.size; ++i) {
            Triangle2D cur_t = mesh.data[i];
            if (in_circumcircle(cur_t.a, cur_t.b, cur_t.c, pt)) {
                Edge2D e[3] = {
                    { cur_t.a, cur_t.b },
                    { cur_t.b, cur_t.c },
                    { cur_t.c, cur_t.a }
                };
                for (int j = 0; j < 3; ++j) {
                    if (poly_size >= poly_capacity) {
                        poly_capacity *= 2;
                        polygon = (Edge2D*)realloc(polygon, poly_capacity * sizeof(Edge2D));
                    }
                    polygon[poly_size++] = e[j];
                }
            } else {
                mesh.data[write_idx++] = cur_t;
            }
        }
        mesh.size = write_idx;

        /* Знаходимо унікальні межові ребра (що з'явилися рівно один раз) */
        for (size_t i = 0; i < poly_size; ++i) {
            bool is_shared = false;
            for (size_t j = 0; j < poly_size; ++j) {
                if (i != j && edge_equals(polygon[i], polygon[j])) {
                    is_shared = true;
                    break;
                }
            }
            if (!is_shared) {
                Triangle2D new_t = { polygon[i].a, polygon[i].b, pt };
                tri_vector_push(&mesh, new_t);
            }
        }
    }

    free(polygon);

    /* Видалення трикутників, пов'язаних із супертрикутником */
    size_t final_size = 0;
    for (size_t i = 0; i < mesh.size; ++i) {
        Triangle2D t = mesh.data[i];
        if (!triangle_has_vertex(t, st_a) &&
            !triangle_has_vertex(t, st_b) &&
            !triangle_has_vertex(t, st_c)) {
            mesh.data[final_size++] = t;
        }
    }
    mesh.size = final_size;
    return mesh;
}
```
```cpp
#include <vector>
#include <span>
#include <cmath>
#include <algorithm>
#include <optional>
#include <iostream>

struct Point2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr bool operator==(const Point2D& other) const noexcept {
        return std::abs(x - other.x) < 1e-9 && std::abs(y - other.y) < 1e-9;
    }
};

struct Edge2D {
    Point2D a{};
    Point2D b{};

    [[nodiscard]] constexpr bool operator==(const Edge2D& other) const noexcept {
        return (a == other.a && b == other.b) || (a == other.b && b == other.a);
    }
};

struct Triangle2D {
    Point2D a{};
    Point2D b{};
    Point2D c{};

    [[nodiscard]] constexpr bool has_vertex(const Point2D& p) const noexcept {
        return a == p || b == p || c == p;
    }
};

class DelaunayTriangulator {
public:
    [[nodiscard]] static std::vector<Triangle2D> triangulate(std::span<const Point2D> points) {
        if (points.empty()) return {};

        auto [min_x, max_x] = std::minmax_element(points.begin(), points.end(),
            [](const Point2D& p1, const Point2D& p2) { return p1.x < p2.x; });
        auto [min_y, max_y] = std::minmax_element(points.begin(), points.end(),
            [](const Point2D& p1, const Point2D& p2) { return p1.y < p2.y; });

        const double dx = max_x->x - min_x->x;
        const double dy = max_y->y - min_y->y;
        const double delta_max = std::max(std::max(dx, dy) * 20.0, 100.0);
        const double mid_x = (min_x->x + max_x->x) * 0.5;
        const double mid_y = (min_y->y + max_y->y) * 0.5;

        /* Супертрикутник */
        const Point2D st_a{ mid_x - delta_max, mid_y - delta_max };
        const Point2D st_b{ mid_x + delta_max, mid_y - delta_max };
        const Point2D st_c{ mid_x, mid_y + delta_max };

        std::vector<Triangle2D> mesh;
        mesh.push_back(Triangle2D{ st_a, st_b, st_c });

        std::vector<Edge2D> cavity_edges;

        for (const auto& pt : points) {
            cavity_edges.clear();

            /* Відбір поганих трикутників */
            auto it = std::remove_if(mesh.begin(), mesh.end(),
                [&pt, &cavity_edges](const Triangle2D& t) {
                    if (in_circumcircle(t.a, t.b, t.c, pt)) {
                        cavity_edges.push_back(Edge2D{ t.a, t.b });
                        cavity_edges.push_back(Edge2D{ t.b, t.c });
                        cavity_edges.push_back(Edge2D{ t.c, t.a });
                        return true;
                    }
                    return false;
                });
            mesh.erase(it, mesh.end());

            /* Пошук унікальних межових ребер */
            for (std::size_t i = 0; i < cavity_edges.size(); ++i) {
                bool is_shared = false;
                for (std::size_t j = 0; j < cavity_edges.size(); ++j) {
                    if (i != j && cavity_edges[i] == cavity_edges[j]) {
                        is_shared = true;
                        break;
                    }
                }
                if (!is_shared) {
                    mesh.push_back(Triangle2D{ cavity_edges[i].a, cavity_edges[i].b, pt });
                }
            }
        }

        /* Видалення трикутників із вершинами супертрикутника */
        std::erase_if(mesh, [&](const Triangle2D& t) {
            return t.has_vertex(st_a) || t.has_vertex(st_b) || t.has_vertex(st_c);
        });

        return mesh;
    }

private:
    [[nodiscard]] static constexpr double orientation_ccw(Point2D a, Point2D b, Point2D c) noexcept {
        return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
    }

    [[nodiscard]] static bool in_circumcircle(Point2D a, Point2D b, Point2D c, Point2D d) noexcept {
        if (orientation_ccw(a, b, c) < 0.0) {
            std::swap(b, c);
        }

        const double adx = a.x - d.x;
        const double ady = a.y - d.y;
        const double bdx = b.x - d.x;
        const double bdy = b.y - d.y;
        const double cdx = c.x - d.x;
        const double cdy = c.y - d.y;

        const double ab_det = adx * bdy - ady * bdx;
        const double bc_det = bdx * cdy - bdy * cdx;
        const double ca_det = cdx * ady - cdy * adx;

        const double alift = adx * adx + ady * ady;
        const double blift = bdx * bdx + bdy * bdy;
        const double clift = cdx * cdx + cdy * cdy;

        const double det = alift * bc_det + blift * ca_det + clift * ab_det;
        return det > 1e-12;
    }
};
```
:::

## Аналіз складності, локалізація та оптимізації

Продуктивність і числова надійність алгоритму залежать від трьох ключових архітектурних факторів:

### 1. Локалізація точок та часова складність

У базовій реалізації для кожної нової точки виконується лінійне сканування всіх наявних трикутників сітки. Для `N` точок це дає сумарну квадратичну складність `O(N²)`.

Для оптимізації алгоритму до `O(N log N)` застосовують такі підходи:
- **Просторове впорядкування:** Перед початком тріангуляції координати точок упорядковують уздовж кривої просторового заповнення — кривої Гільберта або [Z-кривої Мортона](root:sf-algorithms/z-order-curve). Завдяки цьому послідовні точки у вхідному масиві розташовані поруч у фізичному просторі.
- **Крокування по трикутниках (Triangle Walking):** Замість повного перебору сітки алгоритм починає пошук із трикутника, утвореного на попередньому кроці. Рухаючись від грані до грані через суміжні ребра (перевіряючи знак орієнтації `orient2d` відносно кожного ребра), алгоритм досягає цільового трикутника в середньому за `O(N^{1/3})` або `O(1)` кроків за наявності просторового сортування.

### 2. Геометрія супертрикутника та крайові деформації

Якщо вершини супертрикутника розташовані занадто близько до крайніх точок вхідного набору даних, його описане коло може глибоко проникати у внутрішні області множини `P`. Це створює фальшиві недійсні трикутники під час вставки перших точок. Коли на фінальному кроці трикутники супертрикутника видаляються, на опуклій оболонці можуть утворитися порожні прогалини або відсіктися коректні трикутники Делоне.

Емпіричний коефіцієнт віддалення `delta_max = max(dx, dy) * 20.0` гарантує, що радіус описаного кола супертрикутника настільки великий, що його дуга сприймається внутрішніми точками як пряма лінія, усуваючи крайові артефакти.

### 3. Узагальнення на 3D: тетраедризація Делоне

Алгоритм Бойєра–Ватсона унікальний тим, що природно масштабується на тривимірний простір без зміни фундаментальної логіки:
1. Замість супертрикутника будується великий **супертетраедр**.
2. Замість перевірки кола `in_circumcircle` використовується предикат перевірки сфери `InSphere(A, B, C, D, P)` через визначник матриці `5×5` (або `4×4` зі зміщеними координатами).
3. Замість вилучення спільних ребер знаходяться спільні **двовимірні трикутні грані** тетраедрів. Межа тривимірної каверни є замкненою поліедричною поверхнею, грані якої з'єднуються з новою точкою `P`, утворюючи нові тетраедри.
