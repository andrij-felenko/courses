# 📋 Специфікація API та структур даних планувальника BCD

Цей довідник інтерфейсу містить повну специфікацію структур даних, функціональних сигнатур, конфігураційних параметрів та інваріантів бібліотеки бустрофедонного клітинного розкладу (BCD Coverage Planner). Він призначений для розробників систем автономного керування роботами (AGV, БПЛА, підводні апарати AUV, автоматичні газонокосарки та збиральні машини), яким потрібен стандартизований контракт взаємодії між модулем геометрії місії та виконавчим автопілотом.

Без чіткого інтерфейсного контракту підсистема планування покриття стає крихкою: неправильне керування пам'яттю при передачі списків точок маршруту, відсутність перевірки коректності вхідних контурів і неоднозначність життєвого циклу об'єктів плану призводять до витоків пам'яті та збоїв у режимі реального часу. Описаний нижче інтерфейс надає як низькорівневий чистий C-API для вбудованих мікроконтролерів (MCU/RTOS), так і високорівневий ідіоматичний C++20 API на базі RAII для бортових Linux-комп'ютерів.

## Загальна архітектура інтерфейсу

Бібліотека надає модульний конвеєр обробки геометрії:

1. **Конфігурування:** завдання робочої ширини інструмента, бажаного відсотка бічного перекриття смуг, радіуса безпечного відступу від перешкод та стратегії вибору кута замітання.
2. **Введення геометрії:** передача зовнішнього полігонального контуру робочої зони та довільної кількості полігональних перешкод (отворів/островів).
3. **Обчислення розкладу:** запуск алгоритму замітання лінії для знаходження критичних точок та побудови топологічного графа комірок.
4. **Генерація траєкторії:** розрахунок локальних галсів та обхід графа для формування єдиного зв'язного списку точок маршруту (waypoint list).
5. **Експорт місії:** отримання результатів у вигляді масиву координат, метрик покриття або бінарного буфера протоколу MAVLink / ROS 2 Path.

## Структури даних та сигнатури функцій

:::tabs
```c
#ifndef BCD_PLANNER_H
#define BCD_PLANNER_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди повернення та помилок планувальника */
typedef enum {
    BCD_STATUS_OK = 0,
    BCD_STATUS_INVALID_ARGUMENT = -1,
    BCD_STATUS_NON_CONVEX_HOLE = -2,
    BCD_STATUS_SELF_INTERSECTING = -3,
    BCD_STATUS_OUT_OF_MEMORY = -4,
    BCD_STATUS_DECOMPOSITION_FAILED = -5,
    BCD_STATUS_NO_VALID_PATH = -6
} bcd_status_t;

/* Стратегія вибору кута замітання */
typedef enum {
    BCD_ANGLE_FIXED = 0,             /* Заданий користувачем фіксований кут */
    BCD_ANGLE_AUTO_LONGEST_EDGE = 1,  /* Автоматичний вибір вздовж найдовшого ребра */
    BCD_ANGLE_AUTO_MIN_TURNS = 2     /* Повний перебір для мінімізації поворотів */
} bcd_angle_mode_t;

/* Точка у 2D декартовій системі координат (метри) */
typedef struct {
    double x;
    double y;
} bcd_point_t;

/* Конфігураційні параметри планувальника покриття */
typedef struct {
    double swath_width;              /* Фізична ширина захвату сенсора/інструмента (м) */
    double lateral_overlap;          /* Коефіцієнт перекриття [0.0 .. 0.9] */
    double safety_margin;            /* Захисний відступ від меж та перешкод (м) */
    double min_turn_radius;          /* Мінімальний радіус розвороту апарата (м) */
    bcd_angle_mode_t angle_mode;     /* Режим визначення кута замітання */
    double custom_sweep_angle_rad;   /* Кут замітання при режимі BCD_ANGLE_FIXED */
} bcd_config_t;

/* Статистика та метрики сформованого плану */
typedef struct {
    size_t cell_count;               /* Кількість отриманих монотонних комірок */
    size_t stripe_count;             /* Загальна кількість робочих галсів */
    size_t turn_count;               /* Загальна кількість розворотів */
    double total_work_distance_m;    /* Довжина корисних робочих проходів (м) */
    double total_transit_distance_m; /* Довжина міжкоміркових перельотів/переїздів (м) */
    double estimated_area_m2;        /* Покрита корисна площа (м²) */
} bcd_metrics_t;

/* Непрозорий дескриптор об'єкта планувальника */
typedef struct bcd_context bcd_context_t;

/* Створення та знищення контексту планувальника */
bcd_context_t* bcd_create(const bcd_config_t *config);
void bcd_destroy(bcd_context_t *ctx);

/* Задання геометрії середовища */
bcd_status_t bcd_set_boundary(bcd_context_t *ctx, const bcd_point_t *vertices, size_t count);
bcd_status_t bcd_add_obstacle(bcd_context_t *ctx, const bcd_point_t *vertices, size_t count);
void bcd_clear_obstacles(bcd_context_t *ctx);

/* Виконання розкладу та планування місії */
bcd_status_t bcd_compute(bcd_context_t *ctx);

/* Отримання результатів планування */
bcd_status_t bcd_get_waypoint_count(const bcd_context_t *ctx, size_t *out_count);
bcd_status_t bcd_get_waypoints(const bcd_context_t *ctx, bcd_point_t *out_buffer, size_t buffer_size);
bcd_status_t bcd_get_metrics(const bcd_context_t *ctx, bcd_metrics_t *out_metrics);

#ifdef __cplusplus
}
#endif

#endif /* BCD_PLANNER_H */
```
```cpp
#ifndef BCD_PLANNER_HPP
#define BCD_PLANNER_HPP

#include <span>
#include <vector>
#include <memory>
#include <expected>
#include <system_error>
#include <cmath>

namespace robotics::coverage {

enum class StatusCode {
    Ok = 0,
    InvalidArgument = -1,
    NonConvexHole = -2,
    SelfIntersecting = -3,
    OutOfMemory = -4,
    DecompositionFailed = -5,
    NoValidPath = -6
};

enum class AngleMode {
    Fixed,
    AutoLongestEdge,
    AutoMinTurns
};

struct Point2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr bool operator==(const Point2D& other) const noexcept {
        return std::abs(x - other.x) < 1e-7 && std::abs(y - other.y) < 1e-7;
    }
};

struct PlannerConfig {
    double swath_width{10.0};
    double lateral_overlap{0.5};
    double safety_margin{1.0};
    double min_turn_radius{2.0};
    AngleMode angle_mode{AngleMode::AutoMinTurns};
    double custom_sweep_angle_rad{0.0};
};

struct CoverageMetrics {
    std::size_t cell_count{0};
    std::size_t stripe_count{0};
    std::size_t turn_count{0};
    double total_work_distance_m{0.0};
    double total_transit_distance_m{0.0};
    double estimated_area_m2{0.0};
};

class BcdCoveragePlanner {
public:
    explicit BcdCoveragePlanner(PlannerConfig config) noexcept;
    ~BcdCoveragePlanner() noexcept;

    BcdCoveragePlanner(const BcdCoveragePlanner&) = delete;
    BcdCoveragePlanner& operator=(const BcdCoveragePlanner&) = delete;

    BcdCoveragePlanner(BcdCoveragePlanner&&) noexcept;
    BcdCoveragePlanner& operator=(BcdCoveragePlanner&&) noexcept;

    std::expected<void, StatusCode> set_boundary(std::span<const Point2D> boundary);
    std::expected<void, StatusCode> add_obstacle(std::span<const Point2D> obstacle);
    void clear_obstacles() noexcept;

    std::expected<std::vector<Point2D>, StatusCode> compute_plan();
    [[nodiscard]] std::expected<CoverageMetrics, StatusCode> get_metrics() const noexcept;

private:
    class Impl;
    std::unique_ptr<Impl> pimpl_;
};

} // namespace robotics::coverage

#endif /* BCD_PLANNER_HPP */
```
:::

## Детальний опис функцій та інваріантів

### 1. `bcd_create` / Конструктор `BcdCoveragePlanner`

- **Призначення:** виділяє ресурси контексту планувальника та ініціалізує конфігураційні параметри.
- **Вхідні параметри:** вказівник на структуру `bcd_config_t` (або об'єкт `PlannerConfig`).
- **Передумови (Preconditions):**
  - `swath_width > 0.0` — фізична ширина смуги сенсора або робочого органа повинна бути строго додатною величиною.
  - `0.0 <= lateral_overlap < 1.0` — коефіцієнт бічного перекриття має перебувати в діапазоні від 0 до 90%. Значення 0.7 відповідає фотограмметричному перекриттю 70%.
  - `safety_margin >= 0.0` — захисний відступ від меж та перешкод (буфер безпеки).
  - `min_turn_radius >= 0.0` — мінімальний радіус розвороту транспортного засобу (для дифприводу може дорівнювати 0, для літаків і колісних шасі Аккермана — обмежений кінематикою).
- **Повертане значення:** валідний дескриптор контексту або `nullptr` у разі браку динамічної пам'яті.

### 2. `bcd_set_boundary` / Метод `set_boundary`

- **Призначення:** задає зовнішню замкнену межу полігону робочої зони.
- **Вхідні параметри:** масив точок `vertices` та кількість точок `count` (або `std::span<const Point2D>`).
- **Вимоги до геометрії:**
  - Кількість вершин `count >= 3`.
  - Контур повинен бути простим многокутником без самоперетинів (Simple Polygon).
  - Орієнтація вершин: проти годинникової стрілки (Counter-Clockwise, CCW). Якщо передано контур за годинниковою стрілкою, планувальник автоматично нормалізує орієнтацію.
- **Коди помилок:**
  - `BCD_STATUS_INVALID_ARGUMENT` — передано `nullptr` або менше трьох вершин.
  - `BCD_STATUS_SELF_INTERSECTING` — виявлено самоперетин ребер контуру.

### 3. `bcd_add_obstacle` / Метод `add_obstacle`

- **Призначення:** додає полігональну перешкоду (заборонену зону або внутрішній острів).
- **Вхідні параметри:** масив точок контуру перешкоди.
- **Вимоги до геометрії:**
  - Перешкода повинна повністю лежати всередині зовнішньої межі робочої зони.
  - Орієнтація вершин перешкоди: за годинниковою стрілкою (Clockwise, CW).
  - Внутрішні перешкоди не повинні взаємно перетинатися.

### 4. `bcd_compute` / Метод `compute_plan`

- **Призначення:** виконує розрахунок бустрофедонного клітинного розкладу, формує граф суміжності та зшиває галси в єдиний маршрут.
- **Пост-умови (Postconditions):**
  - Усі комірки вільного простору є строго монотонними вздовж обраного вектора замітання.
  - Кожна точка простору (за вирахуванням захисного радіуса `safety_margin`) відвідується щонайменше один раз сенсорною плямою захвату `swath_width`.
  - Відстань між сусідніми робочими галсами строго дорівнює `d = swath_width · (1.0 − lateral_overlap)`.
  - Фінальний масив містить послідовні точки переміщення робота без перетину перешкод.

## Коди помилок та стратегії відновлення

1. `BCD_STATUS_INVALID_ARGUMENT`:
   Виникає, коли параметри конфігурації або масив координат містять неприпустимі значення (наприклад, нульова ширина захвату `swath_width <= 0`, некоректний коефіцієнт перекриття `lateral_overlap >= 1.0` або `count < 3`).
   *Стратегія відновлення:* перевірити валідність числових меж конфігурації перед передачею в планувальник.

2. `BCD_STATUS_SELF_INTERSECTING`:
   Виникає, коли зовнішній периметр або контур перешкоди має самоперетин ребер.
   *Стратегія відновлення:* виконати попередню валідацію полігону через алгоритм Бентлі — Оттманна або спростити контур за допомогою булевих операцій над многокутниками (ClipperLib).

3. `BCD_STATUS_NO_VALID_PATH`:
   Виникає, коли через надмірний захисний радіус `safety_margin` або завелику ширину `swath_width` вільний простір розпадається на ізольовані кишені, куди робот не може проїхати без порушення обмежень безпеки.
   *Стратегія відновлення:* зменшити `safety_margin` або перевірити прохідність вузьких коридорів.

## Керування пам'яттю та життєвий цикл

- **C-інтерфейс (Оренда буферів користувача):**
  Функція `bcd_get_waypoints()` навмисно не виділяє пам'ять всередині бібліотеки через `malloc`, а приймає готовий буфер `out_buffer`, виділений стороною, що викликає. Це дозволяє вбудованим системам на мікроконтролерах працювати зі статичними масивами фіксованого розміру без динамічної фрагментації купи (Heap Fragmentation). Кількість необхідних точок попередньо запитується викликом `bcd_get_waypoint_count()`.

- **C++20 інтерфейс (RAII та семантика переміщення):**
  Клас `BcdCoveragePlanner` використовує ідіому PIMPL (Pointer to Implementation) для повної інкапсуляції внутрішніх типів геометрії. Ресурси автоматично звільняються у деструкторі. Результати повертаються у вигляді `std::expected<std::vector<Point2D>, StatusCode>`, що виключає витоки ресурсів та забезпечує безпеку винятків.

## Перетворення у глобальні координати GPS (WGS-84)

Вихідні точки маршруту `bcd_point_t` розраховуються в метричній декартовій системі дотичної площини (Local Tangent Plane / ENU — East, North, Up) відносно опорної базової точки `(lat₀, lon₀)`.

Для завантаження в автопілот ArduPilot або PX4 кожна точка `(x, y)` конвертується в географічні координати широти `lat` та довготи `lon` за формулами сферичної геодезії:

```
lat = lat₀ + (y / R_Earth) · (180 / π)
lon = lon₀ + (x / (R_Earth · cos(lat₀ · π / 180))) · (180 / π)
```

де `R_Earth ≈ 6378137.0` метрів (радіус земного еліпсоїда WGS-84).

## Приклад виклику та інтеграції з автопілотом

Нижче наведено повний цикл використання API для планування місії над полем із внутрішньою забороненою зоною:

:::tabs
```c
#include "bcd_planner.h"
#include <stdio.h>

int main(void) {
    bcd_config_t cfg = {
        .swath_width = 12.0,
        .lateral_overlap = 0.6,
        .safety_margin = 2.0,
        .min_turn_radius = 5.0,
        .angle_mode = BCD_ANGLE_AUTO_MIN_TURNS,
        .custom_sweep_angle_rad = 0.0
    };

    bcd_context_t *ctx = bcd_create(&cfg);
    if (!ctx) {
        fprintf(stderr, "Помилка виділення пам'яті під планувальник BCD\n");
        return -1;
    }

    /* Зовнішня межа поля (прямокутник 200x120 метрів) */
    bcd_point_t boundary[] = {
        { 0.0, 0.0 }, { 200.0, 0.0 }, { 200.0, 120.0 }, { 0.0, 120.0 }
    };
    bcd_set_boundary(ctx, boundary, 4);

    /* Заборонена зона (будівля посередині поля) */
    bcd_point_t obstacle[] = {
        { 80.0, 40.0 }, { 120.0, 40.0 }, { 120.0, 80.0 }, { 80.0, 80.0 }
    };
    bcd_add_obstacle(ctx, obstacle, 4);

    /* Розрахунок покриття */
    bcd_status_t status = bcd_compute(ctx);
    if (status == BCD_STATUS_OK) {
        size_t wp_count = 0;
        bcd_get_waypoint_count(ctx, &wp_count);

        bcd_metrics_t metrics;
        bcd_get_metrics(ctx, &metrics);

        printf("Успішно сплановано місію:\n");
        printf("  Кількість комірок розкладу: %zu\n", metrics.cell_count);
        printf("  Кількість точок маршруту: %zu\n", wp_count);
        printf("  Робоча довжина галсів: %.1f м\n", metrics.total_work_distance_m);
        printf("  Транзитна довжина: %.1f м\n", metrics.total_transit_distance_m);
    } else {
        fprintf(stderr, "Помилка обчислення розкладу: код %d\n", status);
    }

    bcd_destroy(ctx);
    return 0;
}
```
```cpp
#include "bcd_planner.hpp"
#include <iostream>
#include <vector>

int main() {
    using namespace robotics::coverage;

    PlannerConfig config{
        .swath_width = 12.0,
        .lateral_overlap = 0.6,
        .safety_margin = 2.0,
        .min_turn_radius = 5.0,
        .angle_mode = AngleMode::AutoMinTurns
    };

    BcdCoveragePlanner planner(config);

    const std::vector<Point2D> boundary = {
        { 0.0, 0.0 }, { 200.0, 0.0 }, { 200.0, 120.0 }, { 0.0, 120.0 }
    };
    if (auto res = planner.set_boundary(boundary); !res) {
        std::cerr << "Некоректна зовнішня межа!\n";
        return -1;
    }

    const std::vector<Point2D> obstacle = {
        { 80.0, 40.0 }, { 120.0, 40.0 }, { 120.0, 80.0 }, { 80.0, 80.0 }
    };
    planner.add_obstacle(obstacle);

    auto plan_result = planner.compute_plan();
    if (plan_result.has_value()) {
        const auto& waypoints = plan_result.value();
        auto metrics = planner.get_metrics().value();

        std::cout << "Успішно сплановано C++ місію:\n"
                  << "  Кількість точок: " << waypoints.size() << "\n"
                  << "  Кількість комірок: " << metrics.cell_count << "\n"
                  << "  Корисна площа: " << metrics.estimated_area_m2 << " м²\n";
    } else {
        std::cerr << "Помилка планування: " << static_cast<int>(plan_result.error()) << "\n";
    }

    return 0;
}
```
:::
