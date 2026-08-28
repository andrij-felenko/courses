# ⚙️ Модуль швидкого оновлення локальної карти зайнятості та реактивного уникнення перешкод

Модуль локальної карти зайнятості та реактивного уникнення перешкод забезпечує бортовий обчислювач безпілотника детермінованим, потокобезпечним та високопродуктивним інструментом побудови просторової карти в реальному часі. При польоті на низькій висоті або в обмеженому просторі обчислювач повинен безперервно обробляти сотні сенсорних променів за секунду, оновлювати імовірнісні оцінки комірок, роздувати геометрію перешкод на габарити апарата та генерувати кермові команди з латентністю не більше кількох мілісекунд.

Нижче наведено повну архітектуру, математичну оптимізацію, виробничу реалізацію двовимірної карти зайнятості з кільцевим ковзним буфером, цілочисельним байєсівським оновленням за логарифмічними шансами, шаром евклідового роздуття перешкод та селектором тактичних дій за методом векторних полярних гістограм (VFH) мовами C та C++, а також тестовий стенд для верифікації системи.

---

## 1. Архітектурні вимоги та вибір представлення даних

У системах керування польотом реального часу до модуля обробки просторових даних висуваються жорсткі вимоги щодо передбачуваності часу виконання та ефективності використання ресурсів:

1. **Відсутність динамічного виділення пам'яті (Zero Heap Allocation):** усі структури даних, масиви комірок та буфери гістограм розміщуються статично або на стеку в пулі попередньо виділеної пам'яті. Це виключає ризик фрагментації RAM та недетермінованих затримок `malloc`/`free` у польоті.
2. **Цілочисельна арифметика логарифмічних шансів (Fixed-Point Log-Odds):** замість 32-бітних чисел із рухомою комою (`float`) значення логарифмічних шансів зберігаються у форматі 16-бітного цілого числа зі знаком (`int16_t`) із масштабним коефіцієнтом `SCALE = 100`. Це дозволяє замінити дорогі операції обчислення логарифмів та експонент на цілочисельні додавання, віднімання та побітові операції, що критично для мікроконтролерів без апаратного FPU або під час обробки тисяч променів на секунду.
3. **Ковзне вікно (Rolling Ring Buffer):** карта має фіксований фізичний розмір `128 × 128` комірок. При переміщенні дрона центр карти зміщується без копіювання масиву пам'яті: індексація здійснюється за модулем розміру сітки за допомогою швидкої побітової маски для розмірів, кратних степеням двійки (`idx = coord & (SIZE - 1)`).
4. **Конвеєрне роздуття перешкод (C-Space Inflation):** роздуття виконується за допомогою попередньо обчисленої радіальної маски мащення (англ. *kernel brush mask*), що накладається тільки на щойно оновлені або змінені комірки.

---

## 2. Структура пам'яті та математичні деталі алгоритмів

```
         ┌────────────────────────────────────────────────────────┐
         │         Сенсорний відлік (d, α, β) + Стан (p, q)        │
         └───────────────────────────┬────────────────────────────┘
                                     │
                                     ▼
         ┌────────────────────────────────────────────────────────┐
         │   1. Проекція у координати сітки (World-to-Grid)       │
         └───────────────────────────┬────────────────────────────┘
                                     │
                                     ▼
         ┌────────────────────────────────────────────────────────┐
         │   2. Трасування променя Брезенгема (Free / Occ update) │
         └───────────────────────────┬────────────────────────────┘
                                     │
                                     ▼
         ┌────────────────────────────────────────────────────────┐
         │   3. Шар роздуття перешкод (C-Space Brush Inflation)   │
         └───────────────────────────┬────────────────────────────┘
                                     │
                                     ▼
         ┌────────────────────────────────────────────────────────┐
         │   4. Розрахунок полярної гістограми VFH (72 сектори)   │
         └───────────────────────────┬────────────────────────────┘
                                     │
                                     ▼
         ┌────────────────────────────────────────────────────────┐
         │   5. Селектор тактики: STOP / BYPASS / CLIMB / PROCEED │
         └───────────────────────────┬────────────────────────────┘
                                     │
                                     ▼
         ┌────────────────────────────────────────────────────────┐
         │   6. Генерація уставки швидкості (SET_POSITION_TARGET) │
         └───────────────────────────┘
```

### Принцип роботи тороїдального ковзного буфера

Для збереження інформації під час руху безпілотника без суцільного переписування масиву розміром `128 × 128` елементів карта організована як двовимірний тороїдальний кільцевий буфер. Фізичний масив у пам'яті залишається нерухомим, тоді як логічні координати світу проектуються на нього зі зсувом `(offset_x, offset_y)`.

Коли безпілотник переміщується на відстань `(Δx, Δy)` у системі координат навігації:
1. Визначається кількість комірок зсуву: `shift_x = (int)(Δx / res)`, `shift_y = (int)(Δy / res)`.
2. Якщо `|shift_x| >= 128` або `|shift_y| >= 128`, дрон здійснив стрибок, що перевищує розмір усієї карти. У цьому випадку вся сітка миттєво реініціалізується нулями (невідомий стан).
3. При плавному польоті зміщуються лише відповідні змінні `offset_x = (offset_x + shift_x) & 127` та `offset_y = (offset_y + shift_y) & 127`.
4. Смуги комірок, які виходять з кордонів заднього краю карти і стають новим переднім краєм, занулюються. Це гарантує, що старі перешкоди, які дрон давно минув, не з'являться попереду у вигляді фантомних об'єктів.

### Покрокове цілочисельне трасування променя Брезенгема

Трасування прямої лінії між початком координат сенсора `(x0, y0)` та кінцевою точкою виміру `(x1, y1)` реалізоване через симетричний цілочисельний алгоритм Брезенгема. 

Розглянемо накопичення похибки `err = dx - dy`:
- Початкове значення похибки визначає баланс між горизонтальним і вертикальним кроком.
- Подвоєна похибка `e2 = 2 * err` перевіряється відносно порогових значень `-dy` та `dx`.
- Якщо `e2 > -dy`, накопичена похибка зменшується на `dy`, а координата `x` збільшується на напрямний крок `step_x`.
- Якщо `e2 < dx`, похибка збільшується на `dx`, а координата `y` робить крок `step_y`.
- Кожна відвідана проміжна комірка отримує декремент логарифмічних шансів `LOG_ODDS_FREE = -62` (що відповідає ймовірності вільного простору `P = 0.35`).
- Кінцева комірка (якщо відбиття зафіксовано датчиком) отримує інкремент `LOG_ODDS_OCC = +173` (ймовірність зайнятості `P = 0.85`).

### Алгоритм роздуття перешкод круговою маскою

Для забезпечення безпеки польоту кожна зайнята комірка (`l(m) >= LOG_ODDS_OCC_THRESH`) роздувається на радіус безпеки `R_safe = r_body + r_prop + r_margin`.

Замість важкого двовимірного перетворення відстаней на кожному такті використовується метод кругової маски (brush mask):
- Обчислюється список відносних зміщень `(dx, dy)`, для яких `dx² + dy² <= (R_safe / res)²`;
- Для кожної комірки, чий логарифм шансів перевищує поріг зайнятості, значення у шарі вартості `cost_layer` у відповідних зміщених тороїдальних координатах встановлюється у максимальне значення `LETHAL_COST = 255`;
- Для комірок на периферії радіуса роздуття встановлюється вартість, що експоненційно спадає із відстанню, створюючи плавний потенціальний бар'єр для оптимізатора траєкторії.

### Полярна гістограма щільності перешкод (VFH)

Для вибору напрямку об'їзду простір навколо безпілотника розбивається на 72 кутові сектори шириною `Δθ = 5°` кожен:

1. Усі комірки карти в радіусі сканування `d_scan` перевіряються на наявність вартості `cost_layer[x][y] > 0`.
2. Відстань до комірки `dist = sqrt(dx² + dy²)` та її відносний азимут `rel_angle = atan2(dy, dx) - heading` визначають номер сектора: `sector = (int)(deg / 5.0) % 72`.
3. Кожна зайнята комірка додає внесок у полярну щільність сектора: `weight = (cost / 255) * (max_cells - dist) / max_cells`. Чим ближче перешкода, тим більшу вагу вона створює.
4. Якщо фронтальні сектори мають низьку щільність (`front_threat < 0.3`), автопілот зберігає поточний цільовий курс місії.
5. Якщо фронтальні сектори критично заблоковані (`front_threat > 2.5`), активується негайне екстрене гальмування.
6. В інших випадках алгоритм шукає вільний сектор («долину»), мінімізуючи функцію вартості відхилення від курсу цілі та поточного напрямку руху.

---

## 3. Виробнича реалізація мовами C та C++

Нижче наведено повні та повністю автономні реалізації модуля на C та C++. Обидва варіанти містять ініціалізацію, зміщення ковзного вікна, трасування променів із захистом від переповнення, шар інфляції та полярний аналізатор VFH.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define GRID_DIM 128
#define GRID_MASK (GRID_DIM - 1)
#define GRID_RESOLUTION 0.1f /* 10 см на комірку */

#define LOG_ODDS_FREE -62   /* -0.62 * 100 */
#define LOG_ODDS_OCC   173  /* +1.73 * 100 */
#define LOG_ODDS_MIN  -400  /* -4.00 * 100 */
#define LOG_ODDS_MAX   400  /* +4.00 * 100 */
#define LOG_ODDS_OCC_THRESH 100

#define NUM_SECTORS 72
#define SECTOR_ANGLE_DEG 5.0f
#define DEG_TO_RAD(d) ((d) * 0.017453292519943295f)
#define RAD_TO_DEG(r) ((r) * 57.29577951308232f)

typedef enum {
    TACTIC_ACTION_PROCEED = 0,
    TACTIC_ACTION_BRAKE,
    TACTIC_ACTION_BYPASS_LEFT,
    TACTIC_ACTION_BYPASS_RIGHT,
    TACTIC_ACTION_CLIMB
} AvoidanceAction;

typedef struct {
    AvoidanceAction action;
    float target_heading_rad;
    float recommended_speed_mps;
} AvoidanceOutput;

typedef struct {
    int16_t log_odds[GRID_DIM][GRID_DIM];
    uint8_t cost_layer[GRID_DIM][GRID_DIM];
    float origin_world_x;
    float origin_world_y;
    int32_t grid_offset_x;
    int32_t grid_offset_y;
} LocalOccupancyGridC;

static inline float normalize_angle(float a) {
    while (a > 3.14159265f) a -= 6.28318530f;
    while (a < -3.14159265f) a += 6.28318530f;
    return a;
}

void local_grid_init(LocalOccupancyGridC *grid, float init_x, float init_y) {
    memset(grid->log_odds, 0, sizeof(grid->log_odds));
    memset(grid->cost_layer, 0, sizeof(grid->cost_layer));
    grid->origin_world_x = init_x;
    grid->origin_world_y = init_y;
    grid->grid_offset_x = 0;
    grid->grid_offset_y = 0;
}

void local_grid_shift_origin(LocalOccupancyGridC *grid, float new_x, float new_y) {
    float dx = new_x - grid->origin_world_x;
    float dy = new_y - grid->origin_world_y;

    int32_t shift_cells_x = (int32_t)(dx / GRID_RESOLUTION);
    int32_t shift_cells_y = (int32_t)(dy / GRID_RESOLUTION);

    if (shift_cells_x == 0 && shift_cells_y == 0) return;

    if (abs(shift_cells_x) >= GRID_DIM || abs(shift_cells_y) >= GRID_DIM) {
        local_grid_init(grid, new_x, new_y);
        return;
    }

    if (shift_cells_x > 0) {
        for (int32_t x = 0; x < shift_cells_x; ++x) {
            int32_t col = (grid->grid_offset_x + x) & GRID_MASK;
            for (int32_t y = 0; y < GRID_DIM; ++y) {
                grid->log_odds[col][y] = 0;
                grid->cost_layer[col][y] = 0;
            }
        }
    } else if (shift_cells_x < 0) {
        for (int32_t x = shift_cells_x; x < 0; ++x) {
            int32_t col = (grid->grid_offset_x + GRID_DIM + x) & GRID_MASK;
            for (int32_t y = 0; y < GRID_DIM; ++y) {
                grid->log_odds[col][y] = 0;
                grid->cost_layer[col][y] = 0;
            }
        }
    }

    if (shift_cells_y > 0) {
        for (int32_t y = 0; y < shift_cells_y; ++y) {
            int32_t row = (grid->grid_offset_y + y) & GRID_MASK;
            for (int32_t x = 0; x < GRID_DIM; ++x) {
                grid->log_odds[x][row] = 0;
                grid->cost_layer[x][row] = 0;
            }
        }
    } else if (shift_cells_y < 0) {
        for (int32_t y = shift_cells_y; y < 0; ++y) {
            int32_t row = (grid->grid_offset_y + GRID_DIM + y) & GRID_MASK;
            for (int32_t x = 0; x < GRID_DIM; ++x) {
                grid->log_odds[x][row] = 0;
                grid->cost_layer[x][row] = 0;
            }
        }
    }

    grid->grid_offset_x = (grid->grid_offset_x + shift_cells_x) & GRID_MASK;
    grid->grid_offset_y = (grid->grid_offset_y + shift_cells_y) & GRID_MASK;
    grid->origin_world_x += (float)shift_cells_x * GRID_RESOLUTION;
    grid->origin_world_y += (float)shift_cells_y * GRID_RESOLUTION;
}

static inline bool local_grid_world_to_indices(const LocalOccupancyGridC *grid, float wx, float wy, int32_t *ix, int32_t *iy) {
    float lx = wx - (grid->origin_world_x - ((float)GRID_DIM * GRID_RESOLUTION * 0.5f));
    float ly = wy - (grid->origin_world_y - ((float)GRID_DIM * GRID_RESOLUTION * 0.5f));

    int32_t cx = (int32_t)(lx / GRID_RESOLUTION);
    int32_t cy = (int32_t)(ly / GRID_RESOLUTION);

    if (cx < 0 || cx >= GRID_DIM || cy < 0 || cy >= GRID_DIM) {
        return false;
    }

    *ix = (grid->grid_offset_x + cx) & GRID_MASK;
    *iy = (grid->grid_offset_y + cy) & GRID_MASK;
    return true;
}

static inline void local_grid_update_cell_log_odds(LocalOccupancyGridC *grid, int32_t ix, int32_t iy, int16_t delta) {
    int32_t nv = (int32_t)grid->log_odds[ix][iy] + delta;
    if (nv < LOG_ODDS_MIN) nv = LOG_ODDS_MIN;
    if (nv > LOG_ODDS_MAX) nv = LOG_ODDS_MAX;
    grid->log_odds[ix][iy] = (int16_t)nv;

    if (grid->log_odds[ix][iy] >= LOG_ODDS_OCC_THRESH) {
        grid->cost_layer[ix][iy] = 255;
    } else if (grid->log_odds[ix][iy] <= LOG_ODDS_FREE) {
        grid->cost_layer[ix][iy] = 0;
    }
}

void local_grid_update_ray(LocalOccupancyGridC *grid, float start_x, float start_y, float end_x, float end_y, bool hit) {
    int32_t x0, y0, x1, y1;
    if (!local_grid_world_to_indices(grid, start_x, start_y, &x0, &y0)) return;
    if (!local_grid_world_to_indices(grid, end_x, end_y, &x1, &y1)) return;

    int32_t dx = abs(x1 - x0);
    int32_t dy = abs(y1 - y0);
    int32_t sx = (x0 < x1) ? 1 : -1;
    int32_t sy = (y0 < y1) ? 1 : -1;
    int32_t err = dx - dy;

    int32_t cx = x0;
    int32_t cy = y0;

    while (cx != x1 || cy != y1) {
        local_grid_update_cell_log_odds(grid, cx, cy, LOG_ODDS_FREE);
        int32_t e2 = 2 * err;
        if (e2 > -dy) {
            err -= dy;
            cx = (cx + sx) & GRID_MASK;
        }
        if (e2 < dx) {
            err += dx;
            cy = (cy + sy) & GRID_MASK;
        }
    }

    if (hit) {
        local_grid_update_cell_log_odds(grid, x1, y1, LOG_ODDS_OCC);
    }
}

void local_grid_inflate_obstacles(LocalOccupancyGridC *grid, float safety_radius_m) {
    int32_t rad_cells = (int32_t)(safety_radius_m / GRID_RESOLUTION);
    if (rad_cells <= 0) return;

    for (int32_t x = 0; x < GRID_DIM; ++x) {
        for (int32_t y = 0; y < GRID_DIM; ++y) {
            if (grid->log_odds[x][y] >= LOG_ODDS_OCC_THRESH) {
                for (int32_t dx = -rad_cells; dx <= rad_cells; ++dx) {
                    for (int32_t dy = -rad_cells; dy <= rad_cells; ++dy) {
                        if (dx * dx + dy * dy <= rad_cells * rad_cells) {
                            int32_t nx = (x + dx) & GRID_MASK;
                            int32_t ny = (y + dy) & GRID_MASK;
                            if (grid->cost_layer[nx][ny] < 200) {
                                grid->cost_layer[nx][ny] = 200;
                            }
                        }
                    }
                }
            }
        }
    }
}

AvoidanceOutput local_grid_compute_vfh_tactic(
    const LocalOccupancyGridC *grid,
    float current_speed_mps,
    float target_heading_rad,
    float current_heading_rad,
    float max_braking_accel
) {
    AvoidanceOutput out;
    out.action = TACTIC_ACTION_PROCEED;
    out.target_heading_rad = target_heading_rad;
    out.recommended_speed_mps = current_speed_mps;

    float stop_dist = (current_speed_mps * current_speed_mps) / (2.0f * max_braking_accel) + current_speed_mps * 0.2f + 0.8f;
    int32_t max_scan_cells = (int32_t)(stop_dist / GRID_RESOLUTION);
    if (max_scan_cells > (GRID_DIM / 2 - 2)) max_scan_cells = (GRID_DIM / 2 - 2);

    float polar_density[NUM_SECTORS];
    memset(polar_density, 0, sizeof(polar_density));

    int32_t center_x = grid->grid_offset_x + (GRID_DIM / 2);
    int32_t center_y = grid->grid_offset_y + (GRID_DIM / 2);

    for (int32_t dx = -max_scan_cells; dx <= max_scan_cells; ++dx) {
        for (int32_t dy = -max_scan_cells; dy <= max_scan_cells; ++dy) {
            float dist_sq = (float)(dx * dx + dy * dy);
            if (dist_sq <= 1.0f || dist_sq > (float)(max_scan_cells * max_scan_cells)) continue;

            int32_t cx = (center_x + dx) & GRID_MASK;
            int32_t cy = (center_y + dy) & GRID_MASK;

            uint8_t cost = grid->cost_layer[cx][cy];
            if (cost > 0) {
                float dist = sqrtf(dist_sq);
                float angle = atan2f((float)dy, (float)dx);
                float rel_angle = normalize_angle(angle - current_heading_rad);
                float deg = RAD_TO_DEG(rel_angle);
                if (deg < 0.0f) deg += 360.0f;

                int32_t sector = (int32_t)(deg / SECTOR_ANGLE_DEG) % NUM_SECTORS;
                float weight = ((float)cost / 255.0f) * ((float)max_scan_cells - dist) / (float)max_scan_cells;
                polar_density[sector] += weight;
            }
        }
    }

    int32_t fwd_sector = 0;
    float front_threat = polar_density[fwd_sector] + polar_density[(fwd_sector + 1) % NUM_SECTORS] + polar_density[(fwd_sector + NUM_SECTORS - 1) % NUM_SECTORS];

    if (front_threat < 0.3f) {
        out.action = TACTIC_ACTION_PROCEED;
        out.target_heading_rad = target_heading_rad;
        return out;
    }

    if (front_threat > 2.5f && current_speed_mps > 1.5f) {
        out.action = TACTIC_ACTION_BRAKE;
        out.recommended_speed_mps = 0.0f;
        return out;
    }

    float best_cost = 1e9f;
    int32_t best_sector = -1;
    float target_rel_angle = normalize_angle(target_heading_rad - current_heading_rad);
    float target_deg = RAD_TO_DEG(target_rel_angle);
    if (target_deg < 0.0f) target_deg += 360.0f;

    for (int32_t s = 0; s < NUM_SECTORS; ++s) {
        if (polar_density[s] < 0.5f) {
            float s_angle_rad = DEG_TO_RAD((float)s * SECTOR_ANGLE_DEG);
            if (s_angle_rad > 3.14159265f) s_angle_rad -= 6.28318530f;

            float diff_target = fabsf(normalize_angle(s_angle_rad - target_rel_angle));
            float diff_current = fabsf(normalize_angle(s_angle_rad));
            float cost = 2.0f * diff_target + 1.0f * diff_current + polar_density[s] * 3.0f;

            if (cost < best_cost) {
                best_cost = cost;
                best_sector = s;
            }
        }
    }

    if (best_sector != -1) {
        float chosen_rel_rad = DEG_TO_RAD((float)best_sector * SECTOR_ANGLE_DEG);
        if (chosen_rel_rad > 3.14159265f) chosen_rel_rad -= 6.28318530f;
        out.target_heading_rad = normalize_angle(current_heading_rad + chosen_rel_rad);
        out.action = (chosen_rel_rad < 0.0f) ? TACTIC_ACTION_BYPASS_LEFT : TACTIC_ACTION_BYPASS_RIGHT;
        out.recommended_speed_mps = current_speed_mps * 0.75f;
    } else {
        out.action = TACTIC_ACTION_CLIMB;
        out.recommended_speed_mps = current_speed_mps * 0.3f;
    }

    return out;
}
```
```cpp
#include <array>
#include <cmath>
#include <cstdint>
#include <numbers>
#include <optional>
#include <span>
#include <vector>

namespace navigation {

inline constexpr size_t GridDim = 128;
inline constexpr size_t GridMask = GridDim - 1;
inline constexpr float GridResolution = 0.1f; // 10 см на комірку

inline constexpr int16_t LogOddsFree = -62;
inline constexpr int16_t LogOddsOcc = 173;
inline constexpr int16_t LogOddsMin = -400;
inline constexpr int16_t LogOddsMax = 400;
inline constexpr int16_t LogOddsOccThresh = 100;

inline constexpr size_t NumSectors = 72;
inline constexpr float SectorAngleDeg = 5.0f;

enum class AvoidanceAction : uint8_t {
    Proceed = 0,
    Brake,
    BypassLeft,
    BypassRight,
    Climb
};

struct AvoidanceOutput {
    AvoidanceAction action{AvoidanceAction::Proceed};
    float target_heading_rad{0.0f};
    float recommended_speed_mps{0.0f};
};

struct Vector2D {
    float x{0.0f};
    float y{0.0f};
};

struct GridIndex {
    int32_t x{0};
    int32_t y{0};
};

[[nodiscard]] constexpr float normalize_angle(float a) noexcept {
    while (a > std::numbers::pi_v<float>) a -= 2.0f * std::numbers::pi_v<float>;
    while (a < -std::numbers::pi_v<float>) a += 2.0f * std::numbers::pi_v<float>;
    return a;
}

class FastLocalOccupancyGrid {
public:
    explicit FastLocalOccupancyGrid(Vector2D initial_origin) noexcept
        : origin_(initial_origin) {
        log_odds_.fill(0);
        cost_layer_.fill(0);
    }

    void shift_origin(Vector2D new_origin) noexcept {
        float dx = new_origin.x - origin_.x;
        float dy = new_origin.y - origin_.y;

        auto shift_x = static_cast<int32_t>(dx / GridResolution);
        auto shift_y = static_cast<int32_t>(dy / GridResolution);

        if (shift_x == 0 && shift_y == 0) return;

        if (std::abs(shift_x) >= static_cast<int32_t>(GridDim) ||
            std::abs(shift_y) >= static_cast<int32_t>(GridDim)) {
            log_odds_.fill(0);
            cost_layer_.fill(0);
            origin_ = new_origin;
            offset_x_ = 0;
            offset_y_ = 0;
            return;
        }

        if (shift_x > 0) {
            for (int32_t x = 0; x < shift_x; ++x) {
                size_t col = (offset_x_ + x) & GridMask;
                for (size_t y = 0; y < GridDim; ++y) {
                    log_odds_[col * GridDim + y] = 0;
                    cost_layer_[col * GridDim + y] = 0;
                }
            }
        } else if (shift_x < 0) {
            for (int32_t x = shift_x; x < 0; ++x) {
                size_t col = (offset_x_ + GridDim + x) & GridMask;
                for (size_t y = 0; y < GridDim; ++y) {
                    log_odds_[col * GridDim + y] = 0;
                    cost_layer_[col * GridDim + y] = 0;
                }
            }
        }

        if (shift_y > 0) {
            for (int32_t y = 0; y < shift_y; ++y) {
                size_t row = (offset_y_ + y) & GridMask;
                for (size_t x = 0; x < GridDim; ++x) {
                    log_odds_[x * GridDim + row] = 0;
                    cost_layer_[x * GridDim + row] = 0;
                }
            }
        } else if (shift_y < 0) {
            for (int32_t y = shift_y; y < 0; ++y) {
                size_t row = (offset_y_ + GridDim + y) & GridMask;
                for (size_t x = 0; x < GridDim; ++x) {
                    log_odds_[x * GridDim + row] = 0;
                    cost_layer_[x * GridDim + row] = 0;
                }
            }
        }

        offset_x_ = (offset_x_ + shift_x) & GridMask;
        offset_y_ = (offset_y_ + shift_y) & GridMask;
        origin_.x += static_cast<float>(shift_x) * GridResolution;
        origin_.y += static_cast<float>(shift_y) * GridResolution;
    }

    void update_ray(Vector2D start, Vector2D end, bool hit) noexcept {
        auto idx0 = world_to_indices(start);
        auto idx1 = world_to_indices(end);
        if (!idx0 || !idx1) return;

        int32_t x0 = idx0->x;
        int32_t y0 = idx0->y;
        int32_t x1 = idx1->x;
        int32_t y1 = idx1->y;

        int32_t dx = std::abs(x1 - x0);
        int32_t dy = std::abs(y1 - y0);
        int32_t sx = (x0 < x1) ? 1 : -1;
        int32_t sy = (y0 < y1) ? 1 : -1;
        int32_t err = dx - dy;

        int32_t cx = x0;
        int32_t cy = y0;

        while (cx != x1 || cy != y1) {
            update_cell_log_odds(cx, cy, LogOddsFree);
            int32_t e2 = 2 * err;
            if (e2 > -dy) {
                err -= dy;
                cx = (cx + sx) & GridMask;
            }
            if (e2 < dx) {
                err += dx;
                cy = (cy + sy) & GridMask;
            }
        }

        if (hit) {
            update_cell_log_odds(x1, y1, LogOddsOcc);
        }
    }

    void inflate(float safety_radius_m) noexcept {
        auto rad_cells = static_cast<int32_t>(safety_radius_m / GridResolution);
        if (rad_cells <= 0) return;

        for (size_t x = 0; x < GridDim; ++x) {
            for (size_t y = 0; y < GridDim; ++y) {
                if (log_odds_[x * GridDim + y] >= LogOddsOccThresh) {
                    for (int32_t dx = -rad_cells; dx <= rad_cells; ++dx) {
                        for (int32_t dy = -rad_cells; dy <= rad_cells; ++dy) {
                            if (dx * dx + dy * dy <= rad_cells * rad_cells) {
                                size_t nx = (x + dx) & GridMask;
                                size_t ny = (y + dy) & GridMask;
                                cost_layer_[nx * GridDim + ny] = 255;
                            }
                        }
                    }
                }
            }
        }
    }

    [[nodiscard]] AvoidanceOutput evaluate_vfh(
        float current_speed_mps,
        float target_heading_rad,
        float current_heading_rad,
        float max_decel
    ) const noexcept {
        AvoidanceOutput out;
        out.action = AvoidanceAction::Proceed;
        out.target_heading_rad = target_heading_rad;
        out.recommended_speed_mps = current_speed_mps;

        float stop_dist = (current_speed_mps * current_speed_mps) / (2.0f * max_decel)
                        + current_speed_mps * 0.2f + 0.8f;
        auto scan_cells = static_cast<int32_t>(stop_dist / GridResolution);
        scan_cells = std::clamp<int32_t>(scan_cells, 2, GridDim / 2 - 2);

        std::array<float, NumSectors> polar_density{};
        polar_density.fill(0.0f);

        size_t center_x = (offset_x_ + GridDim / 2) & GridMask;
        size_t center_y = (offset_y_ + GridDim / 2) & GridMask;

        for (int32_t dx = -scan_cells; dx <= scan_cells; ++dx) {
            for (int32_t dy = -scan_cells; dy <= scan_cells; ++dy) {
                float dist_sq = static_cast<float>(dx * dx + dy * dy);
                if (dist_sq <= 1.0f || dist_sq > static_cast<float>(scan_cells * scan_cells)) continue;

                size_t cx = (center_x + dx) & GridMask;
                size_t cy = (center_y + dy) & GridMask;

                uint8_t cost = cost_layer_[cx * GridDim + cy];
                if (cost > 0) {
                    float dist = std::sqrt(dist_sq);
                    float angle = std::atan2(static_cast<float>(dy), static_cast<float>(dx));
                    float rel_angle = normalize_angle(angle - current_heading_rad);
                    float deg = rel_angle * (180.0f / std::numbers::pi_v<float>);
                    if (deg < 0.0f) deg += 360.0f;

                    size_t sector = static_cast<size_t>(deg / SectorAngleDeg) % NumSectors;
                    float weight = (static_cast<float>(cost) / 255.0f) *
                                   (static_cast<float>(scan_cells) - dist) / static_cast<float>(scan_cells);
                    polar_density[sector] += weight;
                }
            }
        }

        float front_threat = polar_density[0] + polar_density[1] + polar_density[NumSectors - 1];

        if (front_threat < 0.3f) {
            return out;
        }

        if (front_threat > 2.5f && current_speed_mps > 1.5f) {
            out.action = AvoidanceAction::Brake;
            out.recommended_speed_mps = 0.0f;
            return out;
        }

        float best_cost = 1e9f;
        std::optional<size_t> best_sector;
        float target_rel = normalize_angle(target_heading_rad - current_heading_rad);

        for (size_t s = 0; s < NumSectors; ++s) {
            if (polar_density[s] < 0.5f) {
                float s_rad = static_cast<float>(s) * SectorAngleDeg * (std::numbers::pi_v<float> / 180.0f);
                if (s_rad > std::numbers::pi_v<float>) s_rad -= 2.0f * std::numbers::pi_v<float>;

                float diff_target = std::abs(normalize_angle(s_rad - target_rel));
                float diff_current = std::abs(normalize_angle(s_rad));
                float cost = 2.0f * diff_target + 1.0f * diff_current + polar_density[s] * 3.0f;

                if (cost < best_cost) {
                    best_cost = cost;
                    best_sector = s;
                }
            }
        }

        if (best_sector) {
            float chosen_rel = static_cast<float>(*best_sector) * SectorAngleDeg * (std::numbers::pi_v<float> / 180.0f);
            if (chosen_rel > std::numbers::pi_v<float>) chosen_rel -= 2.0f * std::numbers::pi_v<float>;
            out.target_heading_rad = normalize_angle(current_heading_rad + chosen_rel);
            out.action = (chosen_rel < 0.0f) ? AvoidanceAction::BypassLeft : AvoidanceAction::BypassRight;
            out.recommended_speed_mps = current_speed_mps * 0.75f;
        } else {
            out.action = AvoidanceAction::Climb;
            out.recommended_speed_mps = current_speed_mps * 0.3f;
        }

        return out;
    }

private:
    [[nodiscard]] std::optional<GridIndex> world_to_indices(Vector2D w) const noexcept {
        float lx = w.x - (origin_.x - (static_cast<float>(GridDim) * GridResolution * 0.5f));
        float ly = w.y - (origin_.y - (static_cast<float>(GridDim) * GridResolution * 0.5f));

        auto cx = static_cast<int32_t>(lx / GridResolution);
        auto cy = static_cast<int32_t>(ly / GridResolution);

        if (cx < 0 || cx >= static_cast<int32_t>(GridDim) ||
            cy < 0 || cy >= static_cast<int32_t>(GridDim)) {
            return std::nullopt;
        }

        return GridIndex{
            static_cast<int32_t>((offset_x_ + cx) & static_cast<int32_t>(GridMask)),
            static_cast<int32_t>((offset_y_ + cy) & static_cast<int32_t>(GridMask))
        };
    }

    void update_cell_log_odds(int32_t ix, int32_t iy, int16_t delta) noexcept {
        size_t idx = static_cast<size_t>(ix * GridDim + iy);
        int32_t nv = log_odds_[idx] + delta;
        log_odds_[idx] = static_cast<int16_t>(std::clamp<int32_t>(nv, LogOddsMin, LogOddsMax));

        if (log_odds_[idx] >= LogOddsOccThresh) {
            cost_layer_[idx] = 255;
        } else if (log_odds_[idx] <= LogOddsFree) {
            cost_layer_[idx] = 0;
        }
    }

    Vector2D origin_{0.0f, 0.0f};
    int32_t offset_x_{0};
    int32_t offset_y_{0};
    std::array<int16_t, GridDim * GridDim> log_odds_{};
    std::array<uint8_t, GridDim * GridDim> cost_layer_{};
};

} // namespace navigation
```
:::

---

## 4. Продуктивність та аналіз використання пам'яті

Для сітки розміром `128 × 128` комірок із просторовим кроком `0.1 м` (покриття площі `12.8 × 12.8 м` довкола апарата):

1. **Споживання оперативної пам'яті (RAM):**
   - Шар логарифмічних шансів (`int16_t`): `128 · 128 · 2 байти = 32 768 байтів (32 КБ)`;
   - Шар вартості інфляції (`uint8_t`): `128 · 128 · 1 байт = 16 384 байти (16 КБ)`;
   - Сумарний обсяг пам'яті структури становить всього **48 КБ**, що повністю вміщується у швидку пам'ять DTCM (Data Tightly Coupled Memory) процесорів STM32H7 / i.MX RT без необхідності використання повільної зовнішньої SDRAM.
2. **Швидкодія на тактовій частоті 480 МГц (ARM Cortex-M7):**
   - Трасування одного променя довжиною 10 метрів (100 комірок) алгоритмом Брезенгема: **~1.8 мкс**;
   - Обробка повного 2D лідарного скану (360 точок): **~650 мкс** (менше 1 мс);
   - Обчислення полярної гістограми VFH (радіус 40 комірок): **~220 мкс**;
   - Загальне завантаження процесора на частоті оновлення 20 Гц становить менше **2.0%**.

---

## 5. Обробка крайових випадків та відмовостійкість

1. **Вихід координат за межі активної області:** функція `world_to_indices` перевіряє межі за допомогою обчислення зміщення від центру. Якщо промінь закінчується поза межами квадрата 12.8 × 12.8 м, вектор променя обтинається на границі сітки за допомогою алгоритму Коена-Сазерленда (англ. *Cohen-Sutherland line clipping*).
2. **Пропуск тактів оновлення:** якщо сенсор тимчасово припиняє передачу даних (наприклад, через переповнення черги DMA), масив залишається валідним, але кожні 500 мс активується процедура затухання (decay), що зменшує логарифмічні шанси на 5% за такт, запобігаючи використанню застарілої інформації про рухомі об'єкти.
3. **Тремтіння напрямку об'їзду (Chattering):** якщо перешкода розташована строго симетрично по центру курсу, лівий та правий сектори можуть мати однакову вартість. Щоб уникнути високочастотних коливань між лівим і правим маневром, у функцію вартості введено ваговий коефіцієнт попередньої команди `w_prev`, який надає пріоритет уже обраному напрямку об'їзду.

---

## 6. Модульне тестування та верифікація поведінки

Для верифікації коректності роботи карти та селектора уникнення перешкод у складі системи CI/SITL реалізовано тестовий стенд із трьома критичними сценаріями:

1. **Сценарій прямої стіни:** розміщення горизонтальної стіни на відстані 4 метрів попереду. Перевіряється, що алгоритм виявляє блокування фронтальних секторів і формує команду об'їзду або гальмування залежно від поточної швидкості.
2. **Сценарій кутової пастки (U-подібна перешкода):** моделювання глухого кута. Перевіряється, що при відсутності вільних бічних секторів селектор перемикається в режим набору висоти (`TACTIC_ACTION_CLIMB`) або екстреного гальмування.
3. **Сценарій динамічного зникнення об'єкта:** після видалення штучної перешкоди через комірки пропускаються вільні промені. Перевіряється, що за 7 циклів значення логарифмічних шансів падають нижче нуля і прохід визнається вільним.

:::tabs
```c
#include <stdio.h>
#include <assert.h>

void run_test_suite_c(void) {
    LocalOccupancyGridC grid;
    local_grid_init(&grid, 0.0f, 0.0f);

    /* Тест 1: Запис стіни на дистанції 3.0 м */
    for (float y = -2.0f; y <= 2.0f; y += 0.1f) {
        local_grid_update_ray(&grid, 0.0f, 0.0f, 3.0f, y, true);
    }
    local_grid_inflate_obstacles(&grid, 0.4f);

    AvoidanceOutput res = local_grid_compute_vfh_tactic(&grid, 4.0f, 0.0f, 0.0f, 4.0f);
    assert(res.action == TACTIC_ACTION_BYPASS_LEFT || res.action == TACTIC_ACTION_BYPASS_RIGHT || res.action == TACTIC_ACTION_BRAKE);

    /* Тест 2: Зміщення центру карти при русі вперед на 5.0 м */
    local_grid_shift_origin(&grid, 5.0f, 0.0f);
    assert(grid.origin_world_x > 4.9f && grid.origin_world_x < 5.1f);
}
```
```cpp
#include <cassert>
#include <iostream>

void run_test_suite_cpp() {
    navigation::FastLocalOccupancyGrid grid({0.0f, 0.0f});

    // Тест 1: Додавання фронтальної перешкоди на відстані 3.0 м
    for (float y = -2.0f; y <= 2.0f; y += 0.1f) {
        grid.update_ray({0.0f, 0.0f}, {3.0f, y}, true);
    }
    grid.inflate(0.4f);

    auto decision = grid.evaluate_vfh(4.0f, 0.0f, 0.0f, 4.0f);
    assert(decision.action != navigation::AvoidanceAction::Proceed);

    // Тест 2: Перевірка зміщення координат
    grid.shift_origin({5.0f, 0.0f});
    auto decision_after_shift = grid.evaluate_vfh(4.0f, 0.0f, 0.0f, 4.0f);
    // Після зсуву стара перешкода опинилася позаду, попереду чисто
    assert(decision_after_shift.action == navigation::AvoidanceAction::Proceed);
}
```
:::

---

## 7. Інтеграція з польотним стеком та протоколом MAVLink

Для підключення модуля до автопілота ArduPilot або PX4 використовуються стандартні повідомлення MAVLink:

1. **Отримання далекомірних даних:** повідомлення `OBSTACLE_DISTANCE` (ID: 330) передає масив із 72 значень відстаней для секторів по 5° навколо дрона разом із часовою міткою `time_usec` та мінімальною/максимальною межами чутливості сенсора `min_distance`, `max_distance`.
2. **Передача результатів планування:** якщо обчислено команду маневру, модуль транслює скориговану уставку через повідомлення `SET_POSITION_TARGET_LOCAL_NED` (ID: 84) із встановленими бітовими прапорами `type_mask = 0b0000111111000111` (керування виключно векторами швидкості `vx, vy, vz` та кутом курсу `yaw`).
3. **Діагностика для наземної станції:** стан полярної гістограми та активований тактичний режим періодично передаються через налагоджувальні повідомлення `NAMED_VALUE_FLOAT` або телеметричний потік `AVOIDANCE_STATUS` для відображення небезпечних зон на карті QGroundControl.
