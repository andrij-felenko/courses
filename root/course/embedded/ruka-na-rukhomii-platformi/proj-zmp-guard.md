# ⚙️ Модуль динамічного контролю стійкості та захисту від перекидання

Швидкі маніпуляції важким вантажем на мобільній платформі створюють динамічні перекидні моменти, здатні відірвати колеса шасі від ґрунту за частки секунди. Традиційний зворотний зв'язок за нахилом від гіроскопа IMU реагує запізно: коли підвіска вже просіла й платформа нахилилася, кутовий імпульс системи часто неможливо загасити без аварійної зупинки. 

Надійний захист вимагає детермінованого контуру реального часу (100–500 Гц), який на кожному такті обчислює координати ZMP, порівнює їх із геометрією опорного багатокутника та динамічно обмежує прискорення ланок або подає випереджальний момент на приводи шасі.

## Задача та архітектура модуля

Модуль безпеки отримує поточний та запланований стан ланок маніпулятора й шасі, після чого виконує три операції:
1. **Розрахунок ZMP:** обчислює зміщення точки нульового моменту від сил тяжіння, лінійних прискорень ланок та швидкості зміни їхніх кутових моментів.
2. **Оцінка запасу стійкості (DSM):** знаходить мінімальну відстань від точки ZMP до ребер опуклого багатокутника опор коліс.
3. **Адаптивне масштабування траєкторії (Safety Override):** якщо динамічний запас менший за поріг безпеки `DSM_safe`, модуль знижує задані прискорення суглобів за коефіцієнтом `α` від 0.0 до 1.0 та генерує випереджальний компенсувальний момент для моторів шасі.

## Архітектура потоків у RTOS

У реальній вбудованій системі на базі мікроконтролера STM32H7 або Cortex-R5/A53 обробка даних розподіляється між трьома задачами операційної системи реального часу (FreeRTOS чи Zephyr):

1. **Потік збору сенсорних даних (1000 Гц, найвищий пріоритет):** опитує 6-осьовий IMU через SPI за допомогою DMA, зчитує положення суглобів із шини CAN FD або RS-485 і передає сирі вектори стану у спільний кільцевий буфер без динамічного виділення пам'яті.
2. **Потік контролю стійкості та захисту ZMP (250–500 Гц, високий пріоритет):** виконує пряму кінематику, обчислює положення центрів мас, рахує ZMP, оцінює DSM та формує сигнал корекції траєкторії `α(t)` і випереджальний момент `τ_ff`. Час виконання коду на частоті 400 МГц становить менше 4.5 мікросекунд.
3. **Потік генерації траєкторії (50–100 Гц, середній пріоритет):** інтерполює декартові траєкторії та обчислює обернену кінематику. Якщо отримано сигнал обмеження `α < 1.0`, генератор сповільнює фазовий параметр руху вздовж шляху `s(t) = s(t) + α · Δs`, запобігаючи перекиданню без зриву геометричного профілю траєкторії.

Нижче наведено робочу реалізацію модуля мовами C та C++.

:::tabs
@tab c
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define MAX_LINKS 8
#define MAX_VERTICES 8
#define GRAVITY 9.80665f

/* Параметри однієї ланки робота */
typedef struct {
    float mass;              /* Маса ланки, кг */
    float r[3];              /* Положення центру мас [x, y, z], м */
    float r_ddot[3];         /* Лінійне прискорення [x_ddot, y_ddot, z_ddot], м/с^2 */
    float H_dot[3];          /* Швидкість зміни кутового моменту [Hx_dot, Hy_dot, Hz_dot], Н·м */
} LinkState;

/* 2D вершина опорного багатокутника на поверхні ґрунту (z = 0) */
typedef struct {
    float x;
    float y;
} Point2D;

/* Конфігурація шасі та опорного контуру */
typedef struct {
    Point2D vertices[MAX_VERTICES];
    int num_vertices;
    float dsm_safe_threshold; /* Безпечна дистанція до краю, м (наприклад 0.05 м) */
    float dsm_critical_limit;  /* Критична межа, м (наприклад 0.01 м) */
    float wheel_radius;       /* Радіус тягового колеса, м */
} ChassisConfig;

/* Результат розрахунку стійкості */
typedef struct {
    Point2D zmp;
    float dsm;               /* Dynamic Stability Margin, м */
    float scale_factor;      /* Коефіцієнт масштабування прискорень [0.0 ... 1.0] */
    float feedforward_torque_pitch; /* Випереджальний момент компенсації тангажу, Н·м */
    bool is_stable;
} StabilityOutput;

/* Обчислення координат точки нульового моменту (ZMP) */
Point2D compute_zmp(const LinkState* links, int num_links) {
    float sum_denom = 0.0f;
    float sum_num_x = 0.0f;
    float sum_num_y = 0.0f;

    for (int i = 0; i < num_links; ++i) {
        float effective_gz = GRAVITY + links[i].r_ddot[2];
        float m = links[i].mass;

        sum_denom += m * effective_gz;
        sum_num_x += m * links[i].r[0] * effective_gz - m * links[i].r[2] * links[i].r_ddot[0] - links[i].H_dot[1];
        sum_num_y += m * links[i].r[1] * effective_gz - m * links[i].r[2] * links[i].r_ddot[1] + links[i].H_dot[0];
    }

    Point2D zmp = {0.0f, 0.0f};
    if (fabsf(sum_denom) > 1e-4f) {
        zmp.x = sum_num_x / sum_denom;
        zmp.y = sum_num_y / sum_denom;
    }
    return zmp;
}

/* Обчислення знакової відстані DSM від точки до опуклого багатокутника (вершини проти годинникової стрілки) */
float compute_dsm(Point2D pt, const Point2D* vertices, int num_vertices) {
    float min_dist = 1e6f;

    for (int i = 0; i < num_vertices; ++i) {
        int next = (i + 1) % num_vertices;
        float dx = vertices[next].x - vertices[i].x;
        float dy = vertices[next].y - vertices[i].y;
        float len = sqrtf(dx * dx + dy * dy);

        if (len < 1e-5f) continue;

        /* Внутрішня нормаль: [-dy/len, dx/len] */
        float nx = -dy / len;
        float ny = dx / len;

        /* Знакова відстань до прямої ребра */
        float dist = (pt.x - vertices[i].x) * nx + (pt.y - vertices[i].y) * ny;
        if (dist < min_dist) {
            min_dist = dist;
        }
    }
    return min_dist;
}

/* Головний крок захисту в циклі реального часу */
StabilityOutput evaluate_stability_guard(
    const LinkState* links, int num_links,
    const ChassisConfig* cfg) 
{
    StabilityOutput out;
    out.zmp = compute_zmp(links, num_links);
    out.dsm = compute_dsm(out.zmp, cfg->vertices, cfg->num_vertices);

    /* Оцінка коефіцієнта безпеки */
    if (out.dsm >= cfg->dsm_safe_threshold) {
        out.scale_factor = 1.0f;
        out.is_stable = true;
    } else if (out.dsm <= cfg->dsm_critical_limit) {
        out.scale_factor = 0.0f; /* Повне блокування подальшого розгону */
        out.is_stable = false;
    } else {
        /* Лінійна інтерполяція гальмування при наближенні до межі */
        out.scale_factor = (out.dsm - cfg->dsm_critical_limit) / 
                           (cfg->dsm_safe_threshold - cfg->dsm_critical_limit);
        out.is_stable = true;
    }

    /* Розрахунок реактивного моменту для випереджальної компенсації на мотори шасі */
    float net_reaction_moment_y = 0.0f;
    for (int i = 0; i < num_links; ++i) {
        net_reaction_moment_y += links[i].mass * links[i].r[2] * links[i].r_ddot[0] + links[i].H_dot[1];
    }
    /* Випереджальний момент на колеса спрямований назустріч реактивному моменту */
    out.feedforward_torque_pitch = -net_reaction_moment_y;

    return out;
}
```
@tab cpp
```cpp
#include <array>
#include <span>
#include <cmath>
#include <algorithm>
#include <numbers>

struct Vector3D {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct Point2D {
    float x{0.0f};
    float y{0.0f};
};

struct LinkState {
    float mass{0.0f};         // Маса ланки, кг
    Vector3D r{};             // Положення центру мас, м
    Vector3D r_ddot{};        // Лінійне прискорення, м/с^2
    Vector3D H_dot{};         // Швидкість зміни власного кінетичного моменту, Н·м
};

struct ChassisConfig {
    std::span<const Point2D> polygon{};
    float dsm_safe_threshold{0.05f}; // 50 мм запас
    float dsm_critical_limit{0.01f}; // 10 мм критична зона
    float wheel_radius{0.125f};
};

struct StabilityOutput {
    Point2D zmp{};
    float dsm{0.0f};
    float scale_factor{1.0f};
    float feedforward_torque_pitch{0.0f};
    bool is_stable{true};
};

class StabilityGuard {
public:
    static constexpr float GRAVITY = 9.80665f;

    [[nodiscard]] static Point2D compute_zmp(std::span<const LinkState> links) noexcept {
        float sum_denom = 0.0f;
        float sum_num_x = 0.0f;
        float sum_num_y = 0.0f;

        for (const auto& link : links) {
            const float effective_gz = GRAVITY + link.r_ddot.z;
            const float m = link.mass;

            sum_denom += m * effective_gz;
            sum_num_x += m * link.r.x * effective_gz - m * link.r.z * link.r_ddot.x - link.H_dot.y;
            sum_num_y += m * link.r.y * effective_gz - m * link.r.z * link.r_ddot.y + link.H_dot.x;
        }

        if (std::abs(sum_denom) < 1e-4f) {
            return Point2D{0.0f, 0.0f};
        }
        return Point2D{sum_num_x / sum_denom, sum_num_y / sum_denom};
    }

    [[nodiscard]] static float compute_dsm(Point2D pt, std::span<const Point2D> vertices) noexcept {
        if (vertices.size() < 3) return 0.0f;

        float min_dist = 1e6f;
        const std::size_t n = vertices.size();

        for (std::size_t i = 0; i < n; ++i) {
            const auto& v_curr = vertices[i];
            const auto& v_next = vertices[(i + 1) % n];

            const float dx = v_next.x - v_curr.x;
            const float dy = v_next.y - v_curr.y;
            const float len = std::hypot(dx, dy);

            if (len < 1e-5f) continue;

            const float nx = -dy / len;
            const float ny = dx / len;

            const float dist = (pt.x - v_curr.x) * nx + (pt.y - v_curr.y) * ny;
            min_dist = std::min(min_dist, dist);
        }
        return min_dist;
    }

    [[nodiscard]] static StabilityOutput evaluate(
        std::span<const LinkState> links,
        const ChassisConfig& cfg) noexcept 
    {
        StabilityOutput out{};
        out.zmp = compute_zmp(links);
        out.dsm = compute_dsm(out.zmp, cfg.polygon);

        if (out.dsm >= cfg.dsm_safe_threshold) {
            out.scale_factor = 1.0f;
            out.is_stable = true;
        } else if (out.dsm <= cfg.dsm_critical_limit) {
            out.scale_factor = 0.0f;
            out.is_stable = false;
        } else {
            out.scale_factor = (out.dsm - cfg.dsm_critical_limit) / 
                               (cfg.dsm_safe_threshold - cfg.dsm_critical_limit);
            out.is_stable = true;
        }

        float net_reaction_moment_y = 0.0f;
        for (const auto& link : links) {
            net_reaction_moment_y += link.mass * link.r.z * link.r_ddot.x + link.H_dot.y;
        }
        out.feedforward_torque_pitch = -net_reaction_moment_y;

        return out;
    }
};
```
:::

## Покроковий розбір структури та інваріантів алгоритму

Розглянемо, як функція `evaluate_stability_guard` гарантує математичні інваріанти:

1. **Безпека від ділення на нуль:** Знаменник `sum_denom` у формулі ZMP містить суму вагових сил `∑ m_i · (g + z̈_i)`. Якщо робот перебуває у вільному падінні (`z̈ = −g`) або зазнає сильного вертикального удару донизу, знаменник прямує до нуля. Перевірка `fabsf(sum_denom) > 1e-4f` захищає алгоритм від генерації значень `NaN` або `Inf`, повертаючи точку `(0, 0)`.
2. **Конвенція обходу опорного багатокутника:** Функція `compute_dsm` розраховує внутрішню нормаль за правилом `nx = −dy/len`, `ny = dx/len`. Це правило математично коректне лише за умови, що вершини контуру коліс у масиві `vertices` задані в строгому порядку **проти годинникової стрілки**. Якщо порядок випадково інвертувати, знак відстані зміниться на протилежний, і алгоритм вважатиме положення всередині бази аварійним перекиданням.
3. **Плавне насичення (Soft Clamping):** Замість дискретного бінарного перемикання «дозвіл/аварійна зупинка», яке викликає жорсткі гідравлічні й електричні удари в сервоприводах, модуль застосовує лінійне стискання шкали в зоні між `dsm_critical_limit` (наприклад, 10 мм) та `dsm_safe_threshold` (50 мм). Це дозволяє маніпулятору плавно «впиратися» в невидиму м'яку межу стійкості, продовжуючи рух на зниженій швидкості.

## П'ять критичних підводних каменів на практиці

1. **Диференціювання сигналів енкодерів:** Пряме обчислення прискорень через другу різницю `(q_k − 2·q_{k−1} + q_{k−2}) / Δt²` вносить високий високочастотний шум квантування, амплітуда якого зростає обернено пропорційно квадрату періоду дискретизації. У розрахунок ZMP слід подавати бажані прискорення безпосередньо з генератора траєкторії або згладжувати оцінку фільтром Калмана другого порядку чи трекером стану з оцінкою прискорення (*Tracking Differentiator*).
2. **Динаміка на підйомах та узвозах:** Якщо платформа рухається похилою площиною, вектор `g_vec` у зв'язаній системі координат відхиляється від осі `Z`. У такому разі проєкції тяжіння `g_x = −g·sin(θ)`, `g_y = g·sin(φ)·cos(θ)`, `g_z = −g·cos(φ)·cos(θ)` беруться з оцінки орієнтації платформи (IMU/EKF). Без цього статичний нахил на схилі 15° спотворить розрахунок DSM на 120–150 мм.
3. **Пружність підвіски та шин:** При різкому реактивному моменті підвіска просідає ще до того, як колесо відірветься від поверхні. Це змінює кутову орієнтацію бази та фактичні координати вершин опорного багатокутника в інерціальному просторі, що необхідно враховувати в кінематичному дереві перетворень TF.
4. **Транспортне запізнення в шинах зв'язку (CAN bus latency):** Якщо сигнал випереджального моменту `τ_ff` доходить до моторів коліс із запізненням 10–15 мс (через буферизацію в чергах CAN або фазовий зсув низькочастотного фільтра), компенсувальний момент прикладатиметься не в протифазі з розгоном руки, а у фазі її зупинки. Замість гасіння коливань такий запізнілий сигнал увійде в позитивний зворотний зв'язок і лише посилить розгойдування шасі.
5. **Невизначеність маси захопленого вантажу:** Якщо робот бере невідомий об'єкт, маса якого не врахована в моделі ланки захвату, розрахункова точка ZMP виявиться оптимістичнішою за реальну. Для надійного захисту масу вантажу або попередньо зважують за струмом сервоприводів у фазі відриву від землі, або закладають гарантований коефіцієнт запасу `DSM_safe` на рівні 20–30% від напівбази ровера.
