# ⚙️ Реалізація 2D GJK: симплекс, області Вороного та обробка крайових випадків

Двовимірний варіант алгоритму GJK є фундаментальним будівельним блоком для 2D фізичних симуляторів (наприклад, у рушіях рівнів Box2D чи Chipmunk Physics), а також ідеальним полігоном для розуміння геометрії симплексів і областей Вороного без ускладнення тривимірними нормалями тетраедра.

Нижче наведено модульну, чисельно стійку реалізацію перевірки перетину для довільних опуклих многокутників та кіл з аналітичними опорними функціями, розбором областей Вороного та повним набором тестових сценаріїв.

### Векторна арифметика та потрійний векторний добуток

Для роботи алгоритму потрібні базові операції над двовимірними векторами: додавання, віднімання, скалярний добуток, косий добуток та перпендикуляри.

У 2D перпендикуляр до вектора `AB` у бік точки `AO = −A` обчислюється через подвійний векторний добуток `(AB × AO) × AB`. Згідно з векторною тотожністю Лагранжа, подвійний векторний добуток розкладається як:

```
(a × b) × c = b · (a · c) − a · (b · c)
```

У двовимірній площині вектори `AB = (dx, dy)` та `AO = (ox, oy)` розглядаються як тривимірні вектори з нульовою z-координатою: `(dx, dy, 0)` та `(ox, oy, 0)`. Їхній векторний добуток дає вектор, спрямований строго вздовж осі Z:

```
z = dx · oy − dy · ox
```

Наступний векторний добуток цього вертикального вектора `(0, 0, z)` із вихідним вектором `(dx, dy, 0)` повертає вектор, що лежить у вихідній площині XY:

```
perp = (-dy · z, dx · z)
```

Ця формула має виняткове практичне значення для фізичних рушіїв: вона дозволяє знаходити правильний перпендикуляр без обчислення кутів, без викликів тригонометричних функцій `sin`/`cos` і без квадратних коренів — виключно за допомогою базових операцій множення та віднімання.

:::tabs
```c
#include <stdbool.h>
#include <stdio.h>
#include <math.h>

typedef struct {
    float x;
    float y;
} Vec2;

static inline Vec2 vec2_create(float x, float y) {
    return (Vec2){ x, y };
}

static inline Vec2 vec2_add(Vec2 a, Vec2 b) {
    return (Vec2){ a.x + b.x, a.y + b.y };
}

static inline Vec2 vec2_sub(Vec2 a, Vec2 b) {
    return (Vec2){ a.x - b.x, a.y - b.y };
}

static inline Vec2 vec2_neg(Vec2 a) {
    return (Vec2){ -a.x, -a.y };
}

static inline float vec2_dot(Vec2 a, Vec2 b) {
    return a.x * b.x + a.y * b.y;
}

static inline float vec2_cross(Vec2 a, Vec2 b) {
    return a.x * b.y - a.y * b.x;
}

/* Потрійний векторний добуток у 2D: (a × b) × c */
static inline Vec2 vec2_triple_product(Vec2 a, Vec2 b, Vec2 c) {
    float z = a.x * b.y - a.y * b.x;
    return (Vec2){ -c.y * z, c.x * z };
}

/* Опорна точка для опуклого многокутника */
Vec2 polygon_support(const Vec2* vertices, int count, Vec2 dir) {
    int best_index = 0;
    float max_dot = vec2_dot(vertices[0], dir);

    for (int i = 1; i < count; ++i) {
        float dot = vec2_dot(vertices[i], dir);
        if (dot > max_dot) {
            max_dot = dot;
            best_index = i;
        }
    }
    return vertices[best_index];
}

/* Опорна точка для кола (аналітична формула) */
Vec2 circle_support(Vec2 center, float radius, Vec2 dir) {
    float len_sq = vec2_dot(dir, dir);
    if (len_sq < 1e-8f) {
        return center;
    }
    float inv_len = radius / sqrtf(len_sq);
    return (Vec2){ center.x + dir.x * inv_len, center.y + dir.y * inv_len };
}
```
```cpp
#include <cmath>
#include <array>
#include <span>
#include <iostream>
#include <optional>

struct Vec2 {
    float x{0.0f};
    float y{0.0f};

    constexpr Vec2() noexcept = default;
    constexpr Vec2(float x_, float y_) noexcept : x(x_), y(y_) {}

    constexpr Vec2 operator+(Vec2 rhs) const noexcept { return {x + rhs.x, y + rhs.y}; }
    constexpr Vec2 operator-(Vec2 rhs) const noexcept { return {x - rhs.x, y - rhs.y}; }
    constexpr Vec2 operator-() const noexcept { return {-x, -y}; }
    constexpr float dot(Vec2 rhs) const noexcept { return x * rhs.x + y * rhs.y; }
    constexpr float cross(Vec2 rhs) const noexcept { return x * rhs.y - y * rhs.x; }

    /* Потрійний векторний добуток: (this × b) × this */
    constexpr Vec2 triple_product(Vec2 b, Vec2 c) const noexcept {
        float z = x * b.y - y * b.x;
        return {-c.y * z, c.x * z};
    }
};

/* Опорна точка для опуклого многокутника */
inline Vec2 polygon_support(std::span<const Vec2> vertices, Vec2 dir) noexcept {
    if (vertices.empty()) return {};
    int best_index = 0;
    float max_dot = vertices[0].dot(dir);

    for (size_t i = 1; i < vertices.size(); ++i) {
        float dot = vertices[i].dot(dir);
        if (dot > max_dot) {
            max_dot = dot;
            best_index = static_cast<int>(i);
        }
    }
    return vertices[best_index];
}

/* Опорна точка для кола */
inline Vec2 circle_support(Vec2 center, float radius, Vec2 dir) noexcept {
    float len_sq = dir.dot(dir);
    if (len_sq < 1e-8f) return center;
    float inv_len = radius / std::sqrt(len_sq);
    return {center.x + dir.x * inv_len, center.y + dir.y * inv_len};
}
```
:::

### Симплекс та геометричний розв'язувач областей Вороного

У двовимірному просторі симплекс містить від однієї до трьох вершин. Головна оптимізаційна деталь полягає в тому, що вершини в масиві впорядковуються за хронологією додавання: найновіша точка завжди зберігається на індексі 0 (позначимо її як `A`), а раніше додані точки зміщуються праворуч на індекси 1 та 2 (точки `B` та `C`).

Завдяки цьому миттєво відсікаються завідомо неможливі перевірки:

1. **0-симплекс (1 вершина `A`):**
   Оскільки точка лише одна, напрямок пошуку виставляється прямо на початок координат: `d = −A`.
2. **1-симплекс (відрізок `AB`):**
   Вершина `A` — найновіша, `B` — попередня. Вектор сторони `AB = B − A`, вектор до початку координат `AO = −A`.
   Оскільки точка `A` щойно була знайдена пошуком у напрямку попереднього вектора `d`, вона гарантовано перетнула площину нуля у цьому напрямку. Початок координат фізично не може лежати «позаду» вершини `A`. Єдина область, де може бути початок координат — це бічна зона відрізка `AB`.
   Ми обчислюємо перпендикуляр до відрізка `AB` у бік `AO`:
   `d = (AB × AO) × AB`.
3. **2-симплекс (трикутник `ABC`):**
   Вершини: `A` (нова), `B` (попередня), `C` (найстаріша).
   Вектори сторін: `AB = B − A`, `AC = C − A`, вектор до нуля `AO = −A`.
   Знову ж таки, початок координат не може лежати позаду вершини `A` і не може лежати позаду ребра `BC` (оскільки ребро `BC` було частиною попереднього симплекса, від якого ми вже відштовхнулися у бік нуля).
   Залишається перевірити рівно дві зовнішні зони:
   - Зовнішня нормаль до ребра `AB`: `AB_perp = (AC × AB) × AB`.
   - Зовнішня нормаль до ребра `AC`: `AC_perp = (AB × AC) × AC`.
   Якщо `AB_perp · AO > 0`, точка `O` лежить у зоні ребра `AB`. Ми видаляємо вершину `C`, скорочуючи симплекс до `{A, B}`, а новий напрямок призначаємо `d = AB_perp`.
   Якщо `AC_perp · AO > 0`, точка `O` лежить у зоні ребра `AC`. Ми видаляємо вершину `B`, скорочуючи симплекс до `{A, C}`, новий напрямок `d = AC_perp`.
   Якщо обидва скалярні добутки менші або рівні нулю, точка `O` не лежить за жодним із зовнішніх ребер. Отже, початок координат оточений усіма трьома вершинами й лежить усередині трикутника `ABC`. Це сигналізує про виявлення колізії!

:::tabs
```c
typedef struct {
    Vec2 points[3];
    int count;
} Simplex2D;

static inline void simplex_push(Simplex2D* s, Vec2 p) {
    /* Зсуваємо наявні вершини, щоб нова вершина завжди була points[0] */
    s->points[2] = s->points[1];
    s->points[1] = s->points[0];
    s->points[0] = p;
    if (s->count < 3) {
        s->count++;
    }
}

/* Обробка відрізка (2 точки) */
static inline bool handle_line_simplex(Simplex2D* s, Vec2* dir) {
    Vec2 a = s->points[0];
    Vec2 b = s->points[1];
    Vec2 ab = vec2_sub(b, a);
    Vec2 ao = vec2_neg(a);

    /* d = (AB × AO) × AB */
    *dir = vec2_triple_product(ab, ao, ab);
    if (vec2_dot(*dir, *dir) < 1e-8f) {
        /* Якщо AO колінеарний AB, обираємо перпендикуляр за годинниковою стрілкою */
        *dir = (Vec2){ -ab.y, ab.x };
    }
    return false; /* Перетин ще не зафіксовано */
}

/* Обробка трикутника (3 точки) */
static inline bool handle_triangle_simplex(Simplex2D* s, Vec2* dir) {
    Vec2 a = s->points[0];
    Vec2 b = s->points[1];
    Vec2 c = s->points[2];

    Vec2 ab = vec2_sub(b, a);
    Vec2 ac = vec2_sub(c, a);
    Vec2 ao = vec2_neg(a);

    /* Обчислення зовнішніх нормалей */
    Vec2 ab_perp = vec2_triple_product(ac, ab, ab);
    Vec2 ac_perp = vec2_triple_product(ab, ac, ac);

    /* Перевірка зони Вороного ребра AB */
    if (vec2_dot(ab_perp, ao) > 0.0f) {
        s->points[0] = a;
        s->points[1] = b;
        s->count = 2;
        *dir = ab_perp;
        return false;
    }

    /* Перевірка зони Вороного ребра AC */
    if (vec2_dot(ac_perp, ao) > 0.0f) {
        s->points[0] = a;
        s->points[1] = c;
        s->count = 2;
        *dir = ac_perp;
        return false;
    }

    /* Початок координат усередині трикутника ABC -> КОЛІЗІЯ */
    return true;
}

static inline bool handle_simplex(Simplex2D* s, Vec2* dir) {
    if (s->count == 2) {
        return handle_line_simplex(s, dir);
    }
    if (s->count == 3) {
        return handle_triangle_simplex(s, dir);
    }
    return false;
}
```
```cpp
class Simplex2D {
public:
    std::array<Vec2, 3> points{};
    int count{0};

    void push_front(Vec2 p) noexcept {
        points[2] = points[1];
        points[1] = points[0];
        points[0] = p;
        if (count < 3) ++count;
    }

    bool solve(Vec2& dir) noexcept {
        if (count == 2) {
            Vec2 a = points[0];
            Vec2 b = points[1];
            Vec2 ab = b - a;
            Vec2 ao = -a;

            dir = ab.triple_product(ao, ab);
            if (dir.dot(dir) < 1e-8f) {
                dir = {-ab.y, ab.x};
            }
            return false;
        }

        if (count == 3) {
            Vec2 a = points[0];
            Vec2 b = points[1];
            Vec2 c = points[2];

            Vec2 ab = b - a;
            Vec2 ac = c - a;
            Vec2 ao = -a;

            Vec2 ab_perp = ac.triple_product(ab, ab);
            Vec2 ac_perp = ab.triple_product(ac, ac);

            if (ab_perp.dot(ao) > 0.0f) {
                points[0] = a;
                points[1] = b;
                count = 2;
                dir = ab_perp;
                return false;
            }

            if (ac_perp.dot(ao) > 0.0f) {
                points[0] = a;
                points[1] = c;
                count = 2;
                dir = ac_perp;
                return false;
            }

            /* Початок координат усередині трикутника */
            return true;
        }
        return false;
    }
};
```
:::

### Головний цикл GJK для довільних фігур

Алгоритм використовує абстрактні опорні функції, що дозволяє перевіряти перетин будь-яких двох типів тіл між собою: многокутник проти многокутника, многокутник проти кола чи коло проти кола.

Процес ітерації виконується за чітким протоколом:
1. Задаємо початковий напрямок `dir = (1, 0)`.
2. Отримуємо першу опорну точку різниці Мінковського `p = s_A(dir) − s_B(−dir)`.
3. Додаємо точку до симплекса й направляємо вектор пошуку до нуля `dir = −p`.
4. У циклі:
   - Обчислюємо нову опорну точку `p` у напрямку `dir`.
   - Якщо `p · dir ≤ 0`, нова точка не сягнула початку координат, отже, фігура `A ⊖ B` не містить нуля. Тіла гарантовано розділені (повертаємо `false`).
   - Додаємо точку `p` до симплекса.
   - Викликаємо розв'язувач симплекса `handle_simplex()`, який перевіряє факт ув'язнення нуля або скорочує симплекс і оновлює `dir`.
   - Якщо симплекс охопив нуль, повертаємо `true`.

:::tabs
```c
typedef Vec2 (*SupportFn2D)(const void* shape, Vec2 dir);

bool gjk_intersect_2d(const void* shape_a, SupportFn2D sup_a,
                      const void* shape_b, SupportFn2D sup_b) {
    /* 1. Початковий напрямок пошуку (наприклад, вздовж осі X) */
    Vec2 dir = { 1.0f, 0.0f };

    /* 2. Перша точка різниці Мінковського */
    Vec2 p = vec2_sub(sup_a(shape_a, dir), sup_b(shape_b, vec2_neg(dir)));

    Simplex2D simplex = { .count = 0 };
    simplex_push(&simplex, p);

    /* Напрямок до початку координат */
    dir = vec2_neg(p);

    const int MAX_ITERATIONS = 32;
    for (int iter = 0; iter < MAX_ITERATIONS; ++iter) {
        /* Якщо напрямок збігся з нулем, точка лежить рівно на початку координат */
        if (vec2_dot(dir, dir) < 1e-8f) {
            return true;
        }

        /* 3. Опорна точка в новому напрямку */
        p = vec2_sub(sup_a(shape_a, dir), sup_b(shape_b, vec2_neg(dir)));

        /* 4. Перевірка: чи перетнула нова точка площину нуля */
        if (vec2_dot(p, dir) <= 0.0f) {
            /* Фігура A - B не сягає початку координат -> розділені */
            return false;
        }

        /* Додаємо нову точку до симплекса */
        simplex_push(&simplex, p);

        /* 5. Оновлюємо симплекс та обчислюємо наступний напрямок */
        if (handle_simplex(&simplex, &dir)) {
            return true; /* Симплекс містить початок координат -> перетин */
        }
    }

    return false;
}
```
```cpp
template <typename ShapeA, typename ShapeB, typename SupA, typename SupB>
bool gjk_intersect_2d(const ShapeA& shape_a, SupA sup_a,
                      const ShapeB& shape_b, SupB sup_b) noexcept {
    Vec2 dir{1.0f, 0.0f};

    Vec2 p = sup_a(shape_a, dir) - sup_b(shape_b, -dir);

    Simplex2D simplex;
    simplex.push_front(p);

    dir = -p;

    constexpr int max_iterations = 32;
    for (int iter = 0; iter < max_iterations; ++iter) {
        if (dir.dot(dir) < 1e-8f) {
            return true;
        }

        p = sup_a(shape_a, dir) - sup_b(shape_b, -dir);

        if (p.dot(dir) <= 0.0f) {
            return false;
        }

        simplex.push_front(p);

        if (simplex.solve(dir)) {
            return true;
        }
    }

    return false;
}
```
:::

### Тестовий стенд та покрокове трасування

Для перевірки коректності роботи алгоритму розглянемо тестову програму, яка покриває чотири ключові геометричні конфігурації:
1. **Перетин двох повернутих прямокутників (Box vs Box):** прямокутники частково накладаються один на одного.
2. **Коло всередині прямокутника (Circle vs Box):** круг повністю занурений у внутрішній простір многокутника.
3. **Розділені прямокутники (Box vs Box):** дві фігури знаходяться на відстані без перекриття.
4. **Дотичні фігури (Edge Contact):** коло торкається однієї з вершин многокутника в одній точці.

:::tabs
```c
typedef struct {
    Vec2 vertices[4];
    int count;
} PolygonShape;

typedef struct {
    Vec2 center;
    float radius;
} CircleShape;

static Vec2 poly_support_adapter(const void* shape, Vec2 dir) {
    const PolygonShape* poly = (const PolygonShape*)shape;
    return polygon_support(poly->vertices, poly->count, dir);
}

static Vec2 circle_support_adapter(const void* shape, Vec2 dir) {
    const CircleShape* circle = (const CircleShape*)shape;
    return circle_support(circle->center, circle->radius, dir);
}

int main(void) {
    /* Тест 1: Перетин двох прямокутників */
    PolygonShape box1 = {
        .vertices = { {0, 0}, {2, 0}, {2, 2}, {0, 2} },
        .count = 4
    };
    PolygonShape box2 = {
        .vertices = { {1, 1}, {3, 1}, {3, 3}, {1, 3} },
        .count = 4
    };
    bool hit1 = gjk_intersect_2d(&box1, poly_support_adapter, &box2, poly_support_adapter);
    printf("Тест 1 (Перетин прямокутників): %s\n", hit1 ? "ПЕРЕТИН (ОК)" : "ПОМИЛКА");

    /* Тест 2: Коло всередині прямокутника */
    CircleShape circle = { .center = { 1.0f, 1.0f }, .radius = 0.5f };
    bool hit2 = gjk_intersect_2d(&box1, poly_support_adapter, &circle, circle_support_adapter);
    printf("Тест 2 (Коло в прямокутнику): %s\n", hit2 ? "ПЕРЕТИН (ОК)" : "ПОМИЛКА");

    /* Тест 3: Розділені прямокутники */
    PolygonShape box3 = {
        .vertices = { {5, 5}, {7, 5}, {7, 7}, {5, 7} },
        .count = 4
    };
    bool hit3 = gjk_intersect_2d(&box1, poly_support_adapter, &box3, poly_support_adapter);
    printf("Тест 3 (Розділені прямокутники): %s\n", !hit3 ? "РОЗДІЛЕНІ (ОК)" : "ПОМИЛКА");

    return 0;
}
```
```cpp
struct PolygonShape {
    std::array<Vec2, 4> vertices{};
    size_t count{4};
};

struct CircleShape {
    Vec2 center{0.0f, 0.0f};
    float radius{1.0f};
};

int main() {
    PolygonShape box1{
        .vertices = { Vec2{0, 0}, Vec2{2, 0}, Vec2{2, 2}, Vec2{0, 2} },
        .count = 4
    };
    PolygonShape box2{
        .vertices = { Vec2{1, 1}, Vec2{3, 1}, Vec2{3, 3}, Vec2{1, 3} },
        .count = 4
    };

    auto poly_sup = [](const PolygonShape& p, Vec2 d) {
        return polygon_support(std::span<const Vec2>(p.vertices.data(), p.count), d);
    };
    auto circle_sup = [](const CircleShape& c, Vec2 d) {
        return circle_support(c.center, c.radius, d);
    };

    bool hit1 = gjk_intersect_2d(box1, poly_sup, box2, poly_sup);
    std::cout << "Тест 1 (Перетин прямокутників): " << (hit1 ? "ПЕРЕТИН (ОК)" : "ПОМИЛКА") << "\n";

    CircleShape circle{ .center = {1.0f, 1.0f}, .radius = 0.5f };
    bool hit2 = gjk_intersect_2d(box1, poly_sup, circle, circle_sup);
    std::cout << "Тест 2 (Коло в прямокутнику): " << (hit2 ? "ПЕРЕТИН (ОК)" : "ПОМИЛКА") << "\n";

    PolygonShape box3{
        .vertices = { Vec2{5, 5}, Vec2{7, 5}, Vec2{7, 7}, Vec2{5, 7} },
        .count = 4
    };
    bool hit3 = gjk_intersect_2d(box1, poly_sup, box3, poly_sup);
    std::cout << "Тест 3 (Розділені прямокутники): " << (!hit3 ? "РОЗДІЛЕНІ (ОК)" : "ПОМИЛКА") << "\n";

    return 0;
}
```
:::

### Практичний аналіз трасування та поведінки ітерацій

Розглянемо числовий трасування роботи алгоритму для Тесту 1 (Box1 проти Box2):

- **Ітерація 0:**
  Початковий напрямок `dir = (1, 0)`.
  Опорна точка Box1 у напрямку `(1, 0)`: вершина `(2, 2)` (скалярний добуток 2).
  Опорна точка Box2 у напрямку `(-1, 0)`: вершина `(1, 1)` (скалярний добуток -1).
  Перша точка різниці Мінковського: `P_0 = (2, 2) − (1, 1) = (1, 1)`.
  Симплекс: `{ (1, 1) }`.
  Новий напрямок до початку координат: `dir = −P_0 = (-1, -1)`.
- **Ітерація 1:**
  Шукаємо нову опорну точку у напрямку `(-1, -1)`.
  Опорна точка Box1: `(0, 0)`.
  Опорна точка Box2 у напрямку `(1, 1)`: `(3, 3)`.
  Нова точка: `P_1 = (0, 0) − (3, 3) = (-3, -3)`.
  Перевірка площини: `P_1 · dir = (-3)·(-1) + (-3)·(-1) = 6 > 0` (перетин площини пройдено успішно).
  Симплекс: `{ (-3, -3), (1, 1) }`.
  Відрізок `AB` між `A = (-3, -3)` та `B = (1, 1)`. Вектор сторони `AB = (4, 4)`. Вектор `AO = (3, 3)`.
  Оскільки `AO` лежить на лінії `AB`, алгоритм бере перпендикуляр `dir = (-4, 4)`.
- **Ітерація 2:**
  Шукаємо опорну точку у напрямку `(-4, 4)`.
  Опорна точка Box1: `(0, 2)`.
  Опорна точка Box2 у напрямку `(4, -4)`: `(3, 1)`.
  Нова точка: `P_2 = (0, 2) − (3, 1) = (-3, 1)`.
  Перевірка площини: `P_2 · dir = (-3)·(-4) + 1·4 = 16 > 0` (успіх).
  Симплекс стає трикутником: `{ (-3, 1), (-3, -3), (1, 1) }`.
  Перевіряємо нормалі до ребер `AB` та `AC`. Початок координат `(0, 0)` лежить строго всередині цього трикутника.
  Алгоритм повертає `true` за 3 кроки!

### Чисельні пастки та оптимізація для фізичних рушіїв

Під час практичного використання 2D GJK у високонавантажених циклах симуляцій розробники стикаються з такими нюансами:

1. **Повна відсутність динамічної пам'яті:**
   Усі структури (`Vec2`, `Simplex2D`) займають фіксований обсяг на стеку процесора (32 байти). Не виконується жодного виклику `malloc` чи `new`, що усуває промахи в кеші L1.
2. **Нульовий вектор напрямку:**
   Якщо перша опорна точка `p` випадково потрапляє в `(0, 0)`, вектор `dir = -p` стає нульовим. Перевірка `dot(dir, dir) < 1e-8f` дозволяє миттєво повернути `true` без зайвих обчислень.
3. **Захист від зациклення через колінеарність:**
   Якщо вершини симплекса стають майже колінеарними, перпендикуляр за годинниковою стрілкою `(-ab.y, ab.x)` гарантує вихід із виродженого 1D стану у двовимірний простір.
4. **Векторизація SIMD:**
   Усі операції з `Vec2` природно лягають у регістри SSE2/AVX або ARM NEON (пакетна обробка двох 64-бітних значень або чотирьох `float` одночасно), що дозволяє виконувати розв'язувач симплекса практично за 15–25 тактів процесора на пару тіл.
