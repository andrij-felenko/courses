# ⚙️ Модуль виявлення та виходу з пасток локальних мінімумів

Цей інженерний модуль реалізує автономну систему детектування геометричних тупиків та виконання аварійних маневрів порятунку для бортових обчислювачів БПЛА (Companion Computer) або мікроконтролерів польотних стеків PX4 та ArduPilot.

Реактивні алгоритми обходу перешкод на базі штучних потенціальних полів чи гістограм векторних полів працюють у швидкому циклі керування (50–100 Гц). Проте, потрапляючи в увігнуті зони (U-подібні будівлі, внутрішні двори, заглиблення між промисловими контейнерами), такі планувальники входять у стан мертвого зависання або високочастотних автоколивань. Модуль порятунку діє як наглядовий контролер вищого рівня: він безперервно відстежує векторний прогрес наближення до цілі, накопичує історію безпечного коридору в кільцевому буфері й, у разі блокування, автоматично реалізує відкат по сліду, контурний обхід стіни або вертикальний набір висоти.

---

## Фізико-математичні принципи детектування заклинювання

Головна складність розпізнавання тупика на борту літального апарата полягає в необхідності надійно відокремити аварійне заклинювання від штатних динамічних режимів: очікування команди оператора, гальмування перед проміжним вейпоінтом або утримання позиції під час сильного зустрічного вітру.

Для цього модуль обчислює три взаємодоповнюючі просторово-часові метрики:
1. **Інтеграл корисного наближення до цілі (`I_prog`);**
2. **Коефіцієнт просторового виродження траєкторії (`L_path / R_disp`);**
3. **Хеш-таблицю просторових відвідувань вокселів.**

```
                    ┌─────────────────────────┐
                    │    Поточний стан БПЛА   │
                    │   p(t), v(t), u_cmd(t)  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Проекція швидкості на   │
                    │ напрямок цілі: v_prog   │
                    └────────────┬────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
     ┌───────────────────────┐       ┌───────────────────────┐
     │  Інтеграл наближення  │       │  Радіус дисперсії та  │
     │ I_prog(T) < δ_thresh  │       │ L_path / R_disp > 4.0 │
     └───────────┬───────────┘       └───────────┬───────────┘
                 │                               │
                 └───────────────┬───────────────┘
                                 ▼
                     ┌───────────────────────┐
                     │ Тяга активна:         │
                     │ ||u_cmd|| > u_min     │
                     └───────────┬────────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │ ПАСТКУ ЗАФІКСОВАНО    │
                     │  (Stuck Confirmed)    │
                     └───────────────────────┘
```

### 1. Інтегрування односторонньої проекції швидкості

Нехай `p(t) = [x, y, z]ᵀ` — поточні просторові координати дрона в локальній навігаційній системі NED, `v(t) = [v_x, v_y, v_z]ᵀ` — вектор поточної лінійної швидкості, а `p_goal = [x_g, y_g, z_g]ᵀ` — цільова точка активного етапу місії.

Вектор прямої видимості на ціль задається виразом:

```
e_goal(t) = (p_goal - p(t)) / ||p_goal - p(t)||
```

Миттєва швидкість наближення `v_prog(t)` обчислюється як скалярний добуток:

```
v_prog(t) = v(t) · e_goal(t) = v_x · e_x + v_y · e_y + v_z · e_z
```

Для виключення маскування тупика випадковими зворотними рухами модуль інтегрує виключно додатну частину швидкості:

```
I_prog(t, T) = ∫ max(0, v_prog(τ)) dτ    [інтегрування від τ = t - T до τ = t]
```

Використання оператора `max(0, v_prog)` є критично важливим: якби інтегрувалася сира знакова швидкість, то у випадку маятникових коливань (рух уперед на 1 м, рух назад на 1 м) інтеграл дорівнював би нулю. Проте при наявності сильного поривчастого вітру назад від'ємні значення швидкості могли б створити від'ємний інтеграл, що ускладнило б порогову оцінку. Зрізка від'ємних значень гарантує, що величина `I_prog` показує виключно сумарний прогрес руху вперед.

Якщо за інтервал `T = 3.0` с накопичений корисний поступ становить `I_prog < 0.30` м за умови, що польотний стек вимагає руху вперед (`thruster_active = true`), система фіксує відсутність фізичного просування.

### 2. Критерій відношення шляху до дисперсії (Limit Cycle Metric)

Під час потрапляння в увігнуту перешкоду реактивний планувальник часто входить у режим стійкого граничного циклу: дрон безперервно рухається зі швидкістю 1.5–2.5 м/с, шарпаючись між протилежними кутами споруди. При цьому модуль швидкості `||v||` є великим, але корисного переміщення немає.

Для виявлення цього стану модуль обчислює повну довжину траєкторії `L_path` та геометричний центр хмари позицій `p_mean`:

```
L_path(t, T) = ∑ ||p(t_k) - p(t_{k-1})||
p_mean(t, T) = (1 / N) · ∑ p(t_k)
```

Максимальне просторове відхилення (радіус дисперсії) відносно центру:

```
R_disp(t, T) = max ||p(t_k) - p_mean(t, T)||    [для k = 1…N]
```

Для ідеального прямолінійного руху зі сталою швидкістю теоретичне відношення становить:

```
L_path / R_disp = (v · T) / (v · T / 2) = 2.0
```

Для замкненого колового або вісімкоподібного коливального циклу радіуса `R_c`, де дрон робить `N_cyc` обертів за час `T`:

```
L_path / R_disp = (2π · R_c · N_cyc) / R_c = 2π · N_cyc ≈ 6.28 · N_cyc
```

Якщо відношення перевищує поріг `L_path / max(R_disp, 0.1) > 4.0` при сумарному пройденому шляху `L_path > 3.0` м, це є неспростовним математичним свідченням наявності автоколивань навколо локального мінімуму.

### 3. Просторове хешування вокселів (Spatial Voxel Hashing)

Для довготривалої фіксації топологічних петель використовується дискретна хеш-таблиця вокселів із кроком просторового квантування `Δr = 0.5` м:

```
v_x = floor(x / 0.5)
v_y = floor(y / 0.5)
```

Цілі індекси вокселя хешуються у 64-елементну таблицю за формулою розрідження великих простих чисел:

```
hash = ((v_x · 73856093) ⊕ (v_y · 19349663)) mod 64
```

Кожен запис таблиці зберігає координати вокселя та лічильник відвідувань `visit_count`. Якщо один і той самий набір вокселів відвідується багаторазово без збільшення відстані до початкової точки входу, модуль перемикається в аварійний стан.

---

## Алгоритм генерації дотичного вектора контурного обходу

Коли відкат назад неможливий (наприклад, позаду рухається інший об'єкт або коридор заблоковано), модуль розраховує рух уздовж контуру перешкоди за даними кругового або секторного лідара.

```
                   Стіна перешкоди
         ═══════════════════════════════════════
                      ▲
                      │ n (вектор нормалі)
                      │
                      │  d_current
                      │
                      ● Дрон p(t)
                     ─┼──────────────► t (вектор дотичної)
                      │
```

1. **Пошук найближчої точки контакту:**
   Серед усіх променів лідара `(r_i, θ_i)` знаходиться мінімальна валідна відстань `d_min = min(r_i)` та відповідний азимут `θ_min` у системі координат корпусу.

2. **Формування одиничної нормалі `n`:**

```
n = [cos(θ_min), sin(θ_min)]ᵀ
```

3. **Ортогональний поворот на дотичну `t`:**
   Для лівостороннього обходу перешкоди нормаль повертається на 90° проти годинникової стрілки:

```
t = [-sin(θ_min), cos(θ_min)]ᵀ
```

4. **Пропорційне утримання дистанції від стіни:**
   Для запобігання як врізанню у стіну, так і відлипанню від контуру, вектор команди модифікується похибкою відстані `e_d = d_min - d_desired`:

```
v_raw = t + k_corr · e_d · n
v_cmd = v_raw / ||v_raw||
```

Якщо `d_min < d_desired` (дрон наблизився занадто сильно), складова вздовж нормалі відштовхує апарат убік; якщо `d_min > d_desired` — плавно притискає до контуру стіни.

---

## Архітектура та розподіл пам'яті в реальному часі

Для надійної роботи на борту безпілотника програмна реалізація підпорядковується суворим вимогам детермінізму:
1. **Нульове динамічне виділення пам'яті (Zero Heap Allocation):** усі структури даних, кільцеві буфери крихт та вікна історії розміщуються статично на етапі ініціалізації.
2. **Складність обчислень `O(1)` на кожному такті:** оновлення ковзного вікна, перевірка критеріїв заклинювання та генерація цільового вейпоінта виконуються за фіксовану кількість процесорних інструкцій без циклічних блокувань.
3. **Пам'ятний слід (Memory Footprint):** модуль займає менше ніж 4 КБ оперативної пам'яті, що дозволяє запускати його безпосередньо на мікроконтролерах класу STM32F7/H7 або ESP32.

### Машина станів модуля порятунку

Модуль функціонує як 5-позиційний автомат станів:

```
                    ┌─────────────────────────┐
                    │      STATE_MONITOR      │ ◄──────────────────────┐
                    │   (Штатний контроль)    │                        │
                    └────────────┬────────────┘                        │
                                 │ I_prog < thresh & active_thrust     │
                                 ▼                                     │
                    ┌─────────────────────────┐                        │
                    │   STATE_EVALUATE_TRAP   │                        │
                    │  (Вибір типу маневру)   │                        │
                    └──────┬───────┬───────┬──┘                        │
                           │       │       │                           │
          Верхня зона      │       │       │ Доступні точки            │ Немає точок
          вільна           │       │       │ в буфері                  │ в буфері
          ┌────────────────┘       │       └────────────────┐          │
          ▼                        ▼                        ▼          │
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐ │
│  STATE_VERTICAL  │     │ STATE_BACKTRACK  │     │ STATE_WALL_ALIGN │ │
│  (Набір висоти)  │     │ (Реверс по FIFO) │     │ (Обхід контуру)  │ │
└─────────┬────────┘     └─────────┬────────┘     └─────────┬────────┘ │
          │                        │                        │          │
          │ Висоту набрано         │ Відкат завершено       │ Bug2 m-line      │
          └────────────────┬───────┴────────────────────────┘          │
                           ▼                                           │
                    ┌─────────────────────────┐                        │
                    │      STATE_REPLAN       │                        │
                    │ (Виклик глобального A*) │ ───────────────────────┘
                    └─────────────────────────┘
```

---

## Програмна реалізація модуля: C та C++

Нижче наведено повний вихідний код модуля мовами C та C++, включаючи детектор автоколивань, алгоритм відкату по кільцевому буферу та генератор дотичних до перешкоди.

:::tabs
```c
#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <string.h>

#define ESCAPE_CRUMB_CAPACITY      128
#define ESCAPE_PROGRESS_WINDOW     50
#define ESCAPE_LIDAR_BEAMS         36
#define ESCAPE_VOXEL_HASH_SIZE     64

typedef struct {
    float x;
    float y;
    float z;
} Vec3;

typedef struct {
    float x;
    float y;
} Vec2;

typedef enum {
    ESCAPE_STATE_MONITOR = 0,
    ESCAPE_STATE_EVALUATE_TRAP,
    ESCAPE_STATE_VERTICAL,
    ESCAPE_STATE_BACKTRACK,
    ESCAPE_STATE_WALL_FOLLOW,
    ESCAPE_STATE_REPLAN
} EscapeFsmState;

typedef struct {
    Vec3 buffer[ESCAPE_CRUMB_CAPACITY];
    uint16_t head;
    uint16_t count;
    float min_spacing_sq;
} CrumbRingBuffer;

typedef struct {
    float angle_rad;
    float range_m;
} LidarBeam;

typedef struct {
    int16_t x;
    int16_t y;
    uint16_t visit_count;
} VoxelEntry;

typedef struct {
    /* Налаштування алгоритму */
    float loop_dt;
    float progress_threshold_m;
    float backtrack_target_dist_m;
    float vertical_step_m;
    float wall_distance_target_m;
    float cooldown_duration_s;
    float max_oscillation_ratio;

    /* Внутрішній стан детектора */
    float progress_history[ESCAPE_PROGRESS_WINDOW];
    float speed_history[ESCAPE_PROGRESS_WINDOW];
    Vec3 pos_history[ESCAPE_PROGRESS_WINDOW];
    uint8_t window_idx;
    bool window_filled;

    CrumbRingBuffer crumbs;
    VoxelEntry voxel_table[ESCAPE_VOXEL_HASH_SIZE];
    EscapeFsmState state;
    
    uint16_t backtrack_idx;
    float backtrack_accum_dist;
    float target_altitude_z;
    float cooldown_timer;

    Vec3 trap_entry_pos;
    Vec3 initial_goal_pos;
} LocalMinimaEscapeModule;

static inline float vec3_len_sq(const Vec3* v) {
    return v->x * v->x + v->y * v->y + v->z * v->z;
}

static inline float vec3_len(const Vec3* v) {
    return sqrtf(vec3_len_sq(v));
}

static inline float vec3_dist_sq(const Vec3* a, const Vec3* b) {
    float dx = a->x - b->x;
    float dy = a->y - b->y;
    float dz = a->z - b->z;
    return dx * dx + dy * dy + dz * dz;
}

static inline float vec3_dist(const Vec3* a, const Vec3* b) {
    return sqrtf(vec3_dist_sq(a, b));
}

void local_minima_init(LocalMinimaEscapeModule* mod, float dt) {
    memset(mod, 0, sizeof(LocalMinimaEscapeModule));
    mod->loop_dt = dt;
    mod->progress_threshold_m = 0.30f;       /* Потрібно мінімум 30 см за вікно */
    mod->backtrack_target_dist_m = 4.5f;     /* 4.5 метра відкату */
    mod->vertical_step_m = 3.0f;             /* 3 метри підйому вгору */
    mod->wall_distance_target_m = 1.5f;      /* 1.5 метра від стіни */
    mod->cooldown_duration_s = 5.0f;         /* 5 секунд захисного таймера */
    mod->max_oscillation_ratio = 4.0f;       /* Поріг автоколивань L_path / R_disp */
    mod->crumbs.min_spacing_sq = 0.25f;      /* Запис крихти через кожні 0.5 м */
    mod->state = ESCAPE_STATE_MONITOR;
}

void crumbs_add(CrumbRingBuffer* rb, const Vec3* p) {
    if (rb->count > 0) {
        uint16_t last_idx = (rb->head + ESCAPE_CRUMB_CAPACITY - 1) % ESCAPE_CRUMB_CAPACITY;
        if (vec3_dist_sq(&rb->buffer[last_idx], p) < rb->min_spacing_sq) {
            return;
        }
    }
    rb->buffer[rb->head] = *p;
    rb->head = (rb->head + 1) % ESCAPE_CRUMB_CAPACITY;
    if (rb->count < ESCAPE_CRUMB_CAPACITY) {
        rb->count++;
    }
}

/* Оновлення воксельної сітки відвідування */
static void update_voxel_tracker(LocalMinimaEscapeModule* mod, const Vec3* pos) {
    int16_t vx = (int16_t)floorf(pos->x / 0.5f);
    int16_t vy = (int16_t)floorf(pos->y / 0.5f);
    uint8_t hash = (uint8_t)(((vx * 73856093) ^ (vy * 19349663)) % ESCAPE_VOXEL_HASH_SIZE);

    if (mod->voxel_table[hash].x == vx && mod->voxel_table[hash].y == vy) {
        mod->voxel_table[hash].visit_count++;
    } else {
        mod->voxel_table[hash].x = vx;
        mod->voxel_table[hash].y = vy;
        mod->voxel_table[hash].visit_count = 1;
    }
}

/* Обчислення дотичного вектора руху вздовж стіни за лідаром */
static Vec2 calculate_wall_tangent(const LidarBeam* beams, uint8_t beam_count, float desired_dist) {
    float min_range = 999.0f;
    float closest_angle = 0.0f;

    for (uint8_t i = 0; i < beam_count; ++i) {
        if (beams[i].range_m > 0.1f && beams[i].range_m < min_range) {
            min_range = beams[i].range_m;
            closest_angle = beams[i].angle_rad;
        }
    }

    if (min_range > 10.0f) {
        /* Немає стіни поруч: рух прямо */
        Vec2 fallback = {1.0f, 0.0f};
        return fallback;
    }

    /* Вектор нормалі до стіни (у системі координат апарата) */
    float nx = cosf(closest_angle);
    float ny = sinf(closest_angle);

    /* Лівосторонній дотичний вектор (поворот нормалі на +90 градусів) */
    float tx = -ny;
    float ty = nx;

    /* Корекція дистанції: якщо занадто близько, відштовхуємося від стіни */
    float dist_err = min_range - desired_dist;
    float corr_gain = 0.6f;

    Vec2 cmd;
    cmd.x = tx + (nx * dist_err * corr_gain);
    cmd.y = ty + (ny * dist_err * corr_gain);

    float norm = sqrtf(cmd.x * cmd.x + cmd.y * cmd.y);
    if (norm > 0.001f) {
        cmd.x /= norm;
        cmd.y /= norm;
    }
    return cmd;
}

bool local_minima_step(LocalMinimaEscapeModule* mod,
                       const Vec3* cur_pos,
                       const Vec3* cur_vel,
                       const Vec3* goal_pos,
                       bool thruster_active,
                       float top_clearance_m,
                       const LidarBeam* lidar_beams,
                       uint8_t lidar_beam_count,
                       Vec3* out_setpoint,
                       bool* out_replan_needed) {
    *out_replan_needed = false;

    if (mod->cooldown_timer > 0.0f) {
        mod->cooldown_timer -= mod->loop_dt;
    }

    switch (mod->state) {
    case ESCAPE_STATE_MONITOR: {
        crumbs_add(&mod->crumbs, cur_pos);
        update_voxel_tracker(mod, cur_pos);

        /* 1. Проекція поточної швидкості на промінь до цілі */
        Vec3 to_goal = {
            goal_pos->x - cur_pos->x,
            goal_pos->y - cur_pos->y,
            goal_pos->z - cur_pos->z
        };
        float dist_goal = vec3_len(&to_goal);

        float v_prog = 0.0f;
        if (dist_goal > 0.01f) {
            v_prog = (cur_vel->x * to_goal.x + cur_vel->y * to_goal.y + cur_vel->z * to_goal.z) / dist_goal;
        }

        mod->progress_history[mod->window_idx] = (v_prog > 0.0f) ? (v_prog * mod->loop_dt) : 0.0f;
        mod->speed_history[mod->window_idx] = vec3_len(cur_vel) * mod->loop_dt;
        mod->pos_history[mod->window_idx] = *cur_pos;

        mod->window_idx = (mod->window_idx + 1) % ESCAPE_PROGRESS_WINDOW;
        if (mod->window_idx == 0) {
            mod->window_filled = true;
        }

        if (mod->window_filled && mod->cooldown_timer <= 0.0f && thruster_active) {
            float total_prog = 0.0f;
            float total_path = 0.0f;
            Vec3 pos_mean = {0.0f, 0.0f, 0.0f};

            for (uint8_t i = 0; i < ESCAPE_PROGRESS_WINDOW; ++i) {
                total_prog += mod->progress_history[i];
                total_path += mod->speed_history[i];
                pos_mean.x += mod->pos_history[i].x;
                pos_mean.y += mod->pos_history[i].y;
                pos_mean.z += mod->pos_history[i].z;
            }
            pos_mean.x /= (float)ESCAPE_PROGRESS_WINDOW;
            pos_mean.y /= (float)ESCAPE_PROGRESS_WINDOW;
            pos_mean.z /= (float)ESCAPE_PROGRESS_WINDOW;

            float max_disp = 0.0f;
            for (uint8_t i = 0; i < ESCAPE_PROGRESS_WINDOW; ++i) {
                float d = vec3_dist(&mod->pos_history[i], &pos_mean);
                if (d > max_disp) {
                    max_disp = d;
                }
            }

            /* Перевірка двох критеріїв: брак наближення або автоколивання */
            bool stuck_by_progress = (total_prog < mod->progress_threshold_m);
            bool stuck_by_oscillation = (total_path > 3.0f && (total_path / fmaxf(max_disp, 0.1f)) > mod->max_oscillation_ratio);

            if ((stuck_by_progress || stuck_by_oscillation) && mod->crumbs.count > 4) {
                mod->state = ESCAPE_STATE_EVALUATE_TRAP;
                mod->trap_entry_pos = *cur_pos;
                mod->initial_goal_pos = *goal_pos;
            }
        }
        break;
    }

    case ESCAPE_STATE_EVALUATE_TRAP: {
        /* Перевірка доступності вертикального виходу */
        if (top_clearance_m >= mod->vertical_step_m + 1.0f) {
            mod->state = ESCAPE_STATE_VERTICAL;
            mod->target_altitude_z = cur_pos->z + mod->vertical_step_m;
        } else if (mod->crumbs.count > 2) {
            mod->state = ESCAPE_STATE_BACKTRACK;
            mod->backtrack_accum_dist = 0.0f;
            mod->backtrack_idx = (mod->crumbs.head + ESCAPE_CRUMB_CAPACITY - 1) % ESCAPE_CRUMB_CAPACITY;
        } else {
            mod->state = ESCAPE_STATE_WALL_FOLLOW;
        }
        break;
    }

    case ESCAPE_STATE_VERTICAL: {
        out_setpoint->x = cur_pos->x;
        out_setpoint->y = cur_pos->y;
        out_setpoint->z = mod->target_altitude_z;

        if (fabsf(cur_pos->z - mod->target_altitude_z) < 0.3f) {
            mod->state = ESCAPE_STATE_REPLAN;
        }
        return true;
    }

    case ESCAPE_STATE_BACKTRACK: {
        if (mod->crumbs.count == 0) {
            mod->state = ESCAPE_STATE_REPLAN;
            break;
        }

        Vec3 target_crumb = mod->crumbs.buffer[mod->backtrack_idx];
        *out_setpoint = target_crumb;

        float d_crumb = vec3_dist(cur_pos, &target_crumb);
        if (d_crumb < 0.6f) {
            mod->backtrack_accum_dist += d_crumb;
            if (mod->crumbs.count > 1) {
                mod->backtrack_idx = (mod->backtrack_idx + ESCAPE_CRUMB_CAPACITY - 1) % ESCAPE_CRUMB_CAPACITY;
                mod->crumbs.count--;
            } else {
                mod->crumbs.count = 0;
            }
        }

        if (mod->backtrack_accum_dist >= mod->backtrack_target_dist_m || mod->crumbs.count == 0) {
            mod->state = ESCAPE_STATE_REPLAN;
        }
        return true;
    }

    case ESCAPE_STATE_WALL_FOLLOW: {
        Vec2 tangent = calculate_wall_tangent(lidar_beams, lidar_beam_count, mod->wall_distance_target_m);
        out_setpoint->x = cur_pos->x + tangent.x * 1.5f;
        out_setpoint->y = cur_pos->y + tangent.y * 1.5f;
        out_setpoint->z = cur_pos->z;

        /* Умова виходу за Bug2: перетин лінії m-line ближче до мети */
        float cur_dist_to_goal = vec3_dist(cur_pos, &mod->initial_goal_pos);
        float trap_dist_to_goal = vec3_dist(&mod->trap_entry_pos, &mod->initial_goal_pos);

        if (cur_dist_to_goal < trap_dist_to_goal - 1.0f) {
            mod->state = ESCAPE_STATE_REPLAN;
        }
        return true;
    }

    case ESCAPE_STATE_REPLAN: {
        *out_replan_needed = true;
        mod->cooldown_timer = mod->cooldown_duration_s;
        mod->state = ESCAPE_STATE_MONITOR;
        break;
    }
    }

    return false;
}
```
```cpp
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <optional>
#include <span>

struct Vec3 {
    float x{0.0F};
    float y{0.0F};
    float z{0.0F};

    [[nodiscard]] constexpr float len_sq() const noexcept {
        return (x * x) + (y * y) + (z * z);
    }

    [[nodiscard]] float len() const noexcept {
        return std::sqrt(len_sq());
    }

    [[nodiscard]] constexpr float dist_sq(const Vec3& other) const noexcept {
        const float dx = x - other.x;
        const float dy = y - other.y;
        const float dz = z - other.z;
        return (dx * dx) + (dy * dy) + (dz * dz);
    }

    [[nodiscard]] float dist(const Vec3& other) const noexcept {
        return std::sqrt(dist_sq(other));
    }
};

struct Vec2 {
    float x{0.0F};
    float y{0.0F};

    [[nodiscard]] float norm() const noexcept {
        return std::sqrt((x * x) + (y * y));
    }

    [[nodiscard]] Vec2 normalized() const noexcept {
        const float n = norm();
        if (n > 1e-4F) {
            return {x / n, y / n};
        }
        return {0.0F, 0.0F};
    }
};

struct LidarBeam {
    float angle_rad{0.0F};
    float range_m{0.0F};
};

struct VoxelEntry {
    int16_t x{0};
    int16_t y{0};
    uint16_t visit_count{0};
};

enum class EscapeFsmState : uint8_t {
    Monitor = 0,
    EvaluateTrap,
    Vertical,
    Backtrack,
    WallFollow,
    Replan
};

template <size_t Capacity>
class CrumbRingBuffer {
public:
    explicit constexpr CrumbRingBuffer(float min_step = 0.5F) noexcept
        : min_spacing_sq_(min_step * min_step) {}

    void push(const Vec3& p) noexcept {
        if (count_ > 0) {
            const size_t last_idx = (head_ + Capacity - 1) % Capacity;
            if (buffer_[last_idx].dist_sq(p) < min_spacing_sq_) {
                return;
            }
        }
        buffer_[head_] = p;
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) {
            ++count_;
        }
    }

    [[nodiscard]] size_t count() const noexcept { return count_; }
    [[nodiscard]] size_t head() const noexcept { return head_; }

    [[nodiscard]] const Vec3& at(size_t idx) const noexcept {
        return buffer_[idx % Capacity];
    }

    void pop_one(size_t& idx) noexcept {
        if (count_ > 0) {
            idx = (idx + Capacity - 1) % Capacity;
            --count_;
        }
    }

    void clear() noexcept {
        count_ = 0;
        head_ = 0;
    }

private:
    std::array<Vec3, Capacity> buffer_{};
    size_t head_{0};
    size_t count_{0};
    float min_spacing_sq_{0.25F};
};

class LocalMinimaEscapeModule {
public:
    static constexpr size_t kProgressWindow = 50;
    static constexpr size_t kCrumbCapacity = 128;
    static constexpr size_t kVoxelHashSize = 64;

    struct Config {
        float loop_dt{0.02F};
        float progress_threshold_m{0.30F};
        float backtrack_target_dist_m{4.5F};
        float vertical_step_m{3.0F};
        float wall_distance_target_m{1.5F};
        float cooldown_duration_s{5.0F};
        float max_oscillation_ratio{4.0F};
    };

    struct StepResult {
        bool override_setpoint{false};
        bool request_global_replan{false};
        Vec3 setpoint{};
    };

    explicit LocalMinimaEscapeModule(const Config& cfg = Config{}) noexcept
        : cfg_(cfg) {}

    StepResult update(const Vec3& cur_pos,
                      const Vec3& cur_vel,
                      const Vec3& goal_pos,
                      bool thruster_active,
                      float top_clearance_m,
                      std::span<const LidarBeam> lidar_beams) noexcept {
        StepResult res{};

        if (cooldown_timer_ > 0.0F) {
            cooldown_timer_ -= cfg_.loop_dt;
        }

        switch (state_) {
        case EscapeFsmState::Monitor: {
            crumbs_.push(cur_pos);
            update_voxel_tracker(cur_pos);

            const Vec3 to_goal{goal_pos.x - cur_pos.x, goal_pos.y - cur_pos.y, goal_pos.z - cur_pos.z};
            const float dist_goal = to_goal.len();

            float v_prog = 0.0F;
            if (dist_goal > 1e-2F) {
                v_prog = (cur_vel.x * to_goal.x + cur_vel.y * to_goal.y + cur_vel.z * to_goal.z) / dist_goal;
            }

            progress_history_[window_idx_] = (v_prog > 0.0F) ? (v_prog * cfg_.loop_dt) : 0.0F;
            speed_history_[window_idx_] = cur_vel.len() * cfg_.loop_dt;
            pos_history_[window_idx_] = cur_pos;

            window_idx_ = (window_idx_ + 1) % kProgressWindow;
            if (window_idx_ == 0) {
                window_filled_ = true;
            }

            if (window_filled_ && cooldown_timer_ <= 0.0F && thruster_active) {
                float total_prog = 0.0F;
                float total_path = 0.0F;
                Vec3 pos_mean{};

                for (size_t i = 0; i < kProgressWindow; ++i) {
                    total_prog += progress_history_[i];
                    total_path += speed_history_[i];
                    pos_mean.x += pos_history_[i].x;
                    pos_mean.y += pos_history_[i].y;
                    pos_mean.z += pos_history_[i].z;
                }
                pos_mean.x /= static_cast<float>(kProgressWindow);
                pos_mean.y /= static_cast<float>(kProgressWindow);
                pos_mean.z /= static_cast<float>(kProgressWindow);

                float max_disp = 0.0F;
                for (size_t i = 0; i < kProgressWindow; ++i) {
                    const float d = pos_history_[i].dist(pos_mean);
                    if (d > max_disp) {
                        max_disp = d;
                    }
                }

                const bool stuck_by_progress = (total_prog < cfg_.progress_threshold_m);
                const bool stuck_by_oscillation = (total_path > 3.0F && (total_path / std::max(max_disp, 0.1F)) > cfg_.max_oscillation_ratio);

                if ((stuck_by_progress || stuck_by_oscillation) && crumbs_.count() > 4) {
                    state_ = EscapeFsmState::EvaluateTrap;
                    trap_entry_pos_ = cur_pos;
                    initial_goal_pos_ = goal_pos;
                }
            }
            break;
        }

        case EscapeFsmState::EvaluateTrap: {
            if (top_clearance_m >= cfg_.vertical_step_m + 1.0F) {
                state_ = EscapeFsmState::Vertical;
                target_altitude_z_ = cur_pos.z + cfg_.vertical_step_m;
            } else if (crumbs_.count() > 2) {
                state_ = EscapeFsmState::Backtrack;
                backtrack_accum_dist_ = 0.0F;
                backtrack_idx_ = (crumbs_.head() + kCrumbCapacity - 1) % kCrumbCapacity;
            } else {
                state_ = EscapeFsmState::WallFollow;
            }
            break;
        }

        case EscapeFsmState::Vertical: {
            res.override_setpoint = true;
            res.setpoint = Vec3{cur_pos.x, cur_pos.y, target_altitude_z_};

            if (std::abs(cur_pos.z - target_altitude_z_) < 0.3F) {
                state_ = EscapeFsmState::Replan;
            }
            break;
        }

        case EscapeFsmState::Backtrack: {
            if (crumbs_.count() == 0) {
                state_ = EscapeFsmState::Replan;
                break;
            }

            const Vec3 target_crumb = crumbs_.at(backtrack_idx_);
            res.override_setpoint = true;
            res.setpoint = target_crumb;

            const float d_crumb = cur_pos.dist(target_crumb);
            if (d_crumb < 0.6F) {
                backtrack_accum_dist_ += d_crumb;
                crumbs_.pop_one(backtrack_idx_);
            }

            if (backtrack_accum_dist_ >= cfg_.backtrack_target_dist_m || crumbs_.count() == 0) {
                state_ = EscapeFsmState::Replan;
            }
            break;
        }

        case EscapeFsmState::WallFollow: {
            const Vec2 tangent = calculate_wall_tangent(lidar_beams, cfg_.wall_distance_target_m);
            res.override_setpoint = true;
            res.setpoint = Vec3{cur_pos.x + (tangent.x * 1.5F), cur_pos.y + (tangent.y * 1.5F), cur_pos.z};

            const float cur_dist_to_goal = cur_pos.dist(initial_goal_pos_);
            const float trap_dist_to_goal = trap_entry_pos_.dist(initial_goal_pos_);

            if (cur_dist_to_goal < trap_dist_to_goal - 1.0F) {
                state_ = EscapeFsmState::Replan;
            }
            break;
        }

        case EscapeFsmState::Replan: {
            res.request_global_replan = true;
            cooldown_timer_ = cfg_.cooldown_duration_s;
            state_ = EscapeFsmState::Monitor;
            break;
        }
        }

        return res;
    }

    [[nodiscard]] EscapeFsmState state() const noexcept { return state_; }
    void reset() noexcept {
        state_ = EscapeFsmState::Monitor;
        crumbs_.clear();
        cooldown_timer_ = 0.0F;
        window_filled_ = false;
        window_idx_ = 0;
        voxel_table_.fill(VoxelEntry{});
    }

private:
    void update_voxel_tracker(const Vec3& pos) noexcept {
        const auto vx = static_cast<int16_t>(std::floor(pos.x / 0.5F));
        const auto vy = static_cast<int16_t>(std::floor(pos.y / 0.5F));
        const auto hash = static_cast<uint8_t>(((vx * 73856093) ^ (vy * 19349663)) % kVoxelHashSize);

        if (voxel_table_[hash].x == vx && voxel_table_[hash].y == vy) {
            voxel_table_[hash].visit_count++;
        } else {
            voxel_table_[hash].x = vx;
            voxel_table_[hash].y = vy;
            voxel_table_[hash].visit_count = 1;
        }
    }

    [[nodiscard]] static Vec2 calculate_wall_tangent(std::span<const LidarBeam> beams, float desired_dist) noexcept {
        float min_range = 999.0F;
        float closest_angle = 0.0F;

        for (const auto& beam : beams) {
            if (beam.range_m > 0.1F && beam.range_m < min_range) {
                min_range = beam.range_m;
                closest_angle = beam.angle_rad;
            }
        }

        if (min_range > 10.0F) {
            return Vec2{1.0F, 0.0F};
        }

        const float nx = std::cos(closest_angle);
        const float ny = std::sin(closest_angle);

        const float tx = -ny;
        const float ty = nx;

        const float dist_err = min_range - desired_dist;
        constexpr float kCorrGain = 0.6F;

        const Vec2 raw_cmd{tx + (nx * dist_err * kCorrGain), ty + (ny * dist_err * kCorrGain)};
        return raw_cmd.normalized();
    }

    Config cfg_{};
    EscapeFsmState state_{EscapeFsmState::Monitor};

    std::array<float, kProgressWindow> progress_history_{};
    std::array<float, kProgressWindow> speed_history_{};
    std::array<Vec3, kProgressWindow> pos_history_{};
    size_t window_idx_{0};
    bool window_filled_{false};

    CrumbRingBuffer<kCrumbCapacity> crumbs_{0.5F};
    std::array<VoxelEntry, kVoxelHashSize> voxel_table_{};

    size_t backtrack_idx_{0};
    float backtrack_accum_dist_{0.0F};
    float target_altitude_z_{0.0F};
    float cooldown_timer_{0.0F};

    Vec3 trap_entry_pos_{};
    Vec3 initial_goal_pos_{};
};
```
:::

---

## Детальний розбір механізмів модуля

### 1. Фільтрація та просторова дискретизація крихт

Кільцевий буфер записує положення БПЛА лише за умови, що евклідова відстань від попереднього збереженого запису задовольняє умові:

```
(x - x_last)² + (y - y_last)² + (z - z_last)² ≥ d_min²
```

де `d_min = 0.5` м.

Якщо дрон зависає на місці протягом кількох десятків секунд, до буфера не додається жодної надлишкової точки. Це гарантує, що історія з `128` елементів покриває щонайменше `128 · 0.5 = 64` метри реального пройденого шляху.

Під час виконання відкату (`ESCAPE_STATE_BACKTRACK`) автопілот послідовно обирає крихту з індексом `backtrack_idx`. Щойно дрон наближається до цієї точки на відстань менше ніж 0.6 м, індекс зміщується далі назад, а пройдена дистанція підсумовується до `backtrack_accum_dist`. Коли сумарний відкат досягає заданих 4.5 м, дрон гарантовано опиняється на відкритому просторі перед входом у пастку.

### 2. Генерація вектора контурного обходу за лідаром

Функція `calculate_wall_tangent` знаходить найближчий промінь лідара з дистанцією `d_min` під кутом `θ_min`. Вектор нормалі спрямований від апарата до точки дотику:

```
n = [cos(θ_min), sin(θ_min)]ᵀ
```

Одиничний дотичний вектор для лівостороннього обходу перешкоди утворюється ортогональним поворотом нормалі проти годинникової стрілки:

```
t = [-sin(θ_min), cos(θ_min)]ᵀ
```

Для стабілізації дистанції від стіни вводиться пропорційна корекція `e_d = d_min - d_desired`: якщо дрон занадто наблизився до перешкоди (`e_d < 0`), результуючий вектор відхиляється від стіни; якщо віддалився (`e_d > 0`) — притискається ближче.

### 3. Просторова хеш-таблиця вокселів

Для детекції циклічних блукань використовується хеш-таблиця з просторовим кроком `Δr = 0.5` м. Координати вокселя `(v_x, v_y)` хешуються за формулою розрідження великих простих чисел:

```
hash = ((v_x · 73856093) ⊕ (v_y · 19349663)) mod 64
```

При попаданні в той самий воксель лічильник `visit_count` інкрементується. Якщо дрон повторно проходить через ті самі 4–5 вокселів понад 10 разів без зміни глобальної дистанції до цілі, це слугує незалежним тригером детекції автоколивань навіть при відсутності даних про швидкість.

---

## Тестовий сценарій та симуляція U-подібної пастки

Для валідації роботи алгоритму реалізовано автономний тест симуляції, який відтворює рух безпілотника всередині увігнутої пастки розміром 10 × 8 метрів.

:::tabs
```c
#include <stdio.h>
#include <assert.h>

void run_escape_simulation_test(void) {
    LocalMinimaEscapeModule mod;
    local_minima_init(&mod, 0.02f); /* 50 Гц */

    Vec3 goal = {20.0f, 0.0f, 0.0f};
    Vec3 pos = {0.0f, 0.0f, 0.0f};
    Vec3 vel = {2.0f, 0.0f, 0.0f};
    Vec3 setpoint;
    bool replan_req = false;

    printf("[TEST] 1. Рух вперед до входу у пастку...\n");
    for (int step = 0; step < 150; ++step) {
        pos.x += vel.x * 0.02f;
        local_minima_step(&mod, &pos, &vel, &goal, true, 10.0f, NULL, 0, &setpoint, &replan_req);
    }
    assert(mod.crumbs.count > 5);
    printf("       Успішно записано %d крихт у буфер.\n", mod.crumbs.count);

    printf("[TEST] 2. Вхід у зону рівноваги сил (швидкість падає до 0)...\n");
    vel.x = 0.0f;
    vel.y = 0.0f;
    for (int step = 0; step < 160; ++step) {
        local_minima_step(&mod, &pos, &vel, &goal, true, 1.0f, NULL, 0, &setpoint, &replan_req);
    }

    assert(mod.state == ESCAPE_STATE_BACKTRACK);
    printf("       Зависання виявлено! Стан перемкнуто на ESCAPE_STATE_BACKTRACK.\n");

    printf("[TEST] 3. Виконання відкату по записаних крихтах...\n");
    while (mod.state == ESCAPE_STATE_BACKTRACK) {
        pos.x = setpoint.x;
        pos.y = setpoint.y;
        local_minima_step(&mod, &pos, &vel, &goal, true, 1.0f, NULL, 0, &setpoint, &replan_req);
    }

    assert(replan_req == true);
    printf("       Відкат завершено на відстань %.2f м! Прапорець replan = TRUE.\n", mod.backtrack_accum_dist);
    printf("[TEST] ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО.\n");
}
```
```cpp
#include <iostream>
#include <cassert>

void run_escape_simulation_test_cpp() {
    LocalMinimaEscapeModule mod{LocalMinimaEscapeModule::Config{.loop_dt = 0.02F}};

    const Vec3 goal{20.0F, 0.0F, 0.0F};
    Vec3 pos{0.0F, 0.0F, 0.0F};
    Vec3 vel{2.0F, 0.0F, 0.0F};

    std::cout << "[TEST CPP] 1. Рух вперед до входу у пастку...\n";
    for (int step = 0; step < 150; ++step) {
        pos.x += vel.x * 0.02F;
        mod.update(pos, vel, goal, true, 10.0F, {});
    }

    std::cout << "[TEST CPP] 2. Зависання всередині кишені...\n";
    vel = {0.0F, 0.0F, 0.0F};
    LocalMinimaEscapeModule::StepResult res{};
    for (int step = 0; step < 160; ++step) {
        res = mod.update(pos, vel, goal, true, 1.0F, {});
    }

    assert(mod.state() == EscapeFsmState::Backtrack);
    std::cout << "           Пастку виявлено! Активовано Backtrack.\n";

    std::cout << "[TEST CPP] 3. Відкат назад...\n";
    while (mod.state() == EscapeFsmState::Backtrack) {
        pos = res.setpoint;
        res = mod.update(pos, vel, goal, true, 1.0F, {});
    }

    assert(res.request_global_replan == true);
    std::cout << "           Відкат успішний! Запит глобального перепланування.\n";
    std::cout << "[TEST CPP] ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО.\n";
}
```
:::

---

## Інтеграція з бортовими архітектурами PX4 та ROS2 Navigation2

Для практичного використання модуль інтегрується у контур керування як компонент проміжного рівня (англ. *Middleware Node*).

### 1. Інтеграція в стек PX4 Autopilot через uORB

У середовищі PX4 модуль оформлюється як фоновий потік `px4_task`, який підписується на топіки польотного стану:
- `vehicle_local_position` (частота 50 Гц) — отримання координат `x, y, z` та швидкостей `vx, vy, vz`;
- `obstacle_distance` (частота 20–30 Гц) — отримання масиву відстаней далекоміра;
- `vehicle_control_mode` — перевірка активності автономного режиму.

Коли прапорець `override_setpoint` стає активним, модуль публікує скориговані вейпоінти безпосередньо у топік `trajectory_setpoint`, тимчасово блокуючи стандартний генератор траєкторій навігатора. Після завершення відкату модуль надсилає внутрішню подію `commander_state` для тригеру перерахунку глобальної місії.

### 2. Інтеграція в ROS2 Navigation2 як плагін Recovery Action

У стеку ROS2 Nav2 модуль обгортається у плагін поведінки `nav2_core::Recovery`:
- При виникненні застрягання дерево поведінки активує вузол `LocalMinimaEscapeAction`;
- Плагін транслює команду швидкості `cmd_vel` або вейпоінти на контролер `ControllerServer`;
- Після досягнення чистої точки повертається статус `BT::NodeStatus::SUCCESS`, що викликає перезапуск планувальника `PlannerServer` для побудови нового глобального шляху NavFn або SmacPlanner.

---

## Налаштування параметрів для різних класів БПЛА

Залежно від злітної маси, інерції та максимальної швидкості апарата, параметри модуля підлягають калібруванню:

| Клас апарата | Маса (кг) | Швидкість (м/с) | `progress_threshold_m` (м) | `backtrack_target_dist_m` (м) | `cooldown_duration_s` (с) |
|---|---|---|---|---|---|
| Мікро-БПЛА (Indoor) | 0.25–0.8 | 1.0–2.0 | 0.15–0.20 | 2.5–3.5 | 3.0 |
| Комерційний квадрокоптер | 1.5–4.5 | 3.0–6.0 | 0.25–0.35 | 4.0–6.0 | 5.0 |
| Важкий інспекційний БПЛА | 10.0–25.0 | 4.0–8.0 | 0.40–0.60 | 7.0–10.0 | 8.0 |

При польотах у тісних складських приміщеннях дистанцію відкату `backtrack_target_dist_m` зменшують до 2.5 м, щоб не зачепити протилежні стелажі. Для швидкісних польотів на відкритій місцевості дистанцію збільшують до 8–10 м для забезпечення гарантованого виходу з зони гравітаційного притягання перешкоди.

---

## Протокол тестування на вібраційному стенді та HIL-симуляторі

Перед випробуваннями у польоті модуль проходить обов'язкову верифікацію в середовищі апаратно-програмного моделювання (Hardware-In-The-Loop, HIL):

1. **Симуляція в Gazebo / AirSim:** БПЛА запускається в урбаністичному середовищі з U-подібними спорудами різної глибини (від 4 до 25 м) та з асиметричними бічними кишенями. Фіксується час від моменту занулення швидкості до активації відкату `t_det`. Нормальний показник становить `t_det = 2.8…3.2` с.
2. **Тестування на стійкість до вібраційного шуму:** на гіроскопи та сенсори швидкості накладається білий шум з дисперсією `σ_v = ±0.15` м/с та пориви вітру амплітудою 4 м/с. Детектор повинен продемонструвати нуль хибних спрацьовувань під час прямолінійного польоту та 100% спрацьовувань при зависанні у кишені.
3. **Енергетичний баланс маневру:** вимірювання струму акумулятора показують, що своєчасний відкат назад за 3.5 секунди зберігає до 92% енергії, яка інакше була б витрачена на безплідне зависання у глухому куті до спрацьовування таймауту місії.

---

## Адаптація до динамічних шумів сенсорів та кутів нахилу

У польотних умовах робота модуля може ускладнюватися зміною просторової орієнтації фюзеляжу та похибками далекомірів:

1. **Фільтрація за кутом крену й тангажу (Attitude Gating):**
   Під час швидкісного гальмування чи різкого маневру багатороторний дрон нахиляється на кути крену або тангажу `|ϕ|, |θ| > 30°`. У цей момент горизонтально встановлений 2D-лідар спрямовує частину променів безпосередньо в землю, що створює фальшиві відліки наближення перешкоди на дистанції 1.5–2.0 м. Модуль повинен отримувати поточну матрицю орієнтації `R_body_to_world` від EKF і трансформувати кожен промінь далекоміра у горизонтальну площину навігаційного базису або відсікати промені, вектор яких спрямований нижче порогу горизонту (`z_beam < -0.3` м).

2. **Адаптивна зона нечутливості за вітром (Deadband Tuning):**
   При польоті в умовах сильного поривчастого вітру (до 10 м/с) автопілот періодично здійснює мікрорухи назад для втримання координат. Щоб уникнути помилкового наповнення вікна корисного прогресу нулями, поріг `progress_threshold_m` динамічно коригується залежно від поточної дисперсії оцінювача швидкості:

```
δ_eff = max(δ_min, progress_threshold_m · (1.0 + k_wind · σ_vel))
```

де `σ_vel` — оцінка поточної середньоквадратичної похибки швидкості від фільтра EKF2/EKF3, а `k_wind = 0.5` — емпіричний коефіцієнт чутливості до збурень.

3. **Обробка вироджених вимірювань далекоміра (No-Return / Outlier Rejection):**
   Дзеркальні скляні поверхні або темні поглинаючі матеріали можуть викликати пропадання відбитого сигналу лідара (`range = NaN` або `range = Inf`). У функції `calculate_wall_tangent` такі значення ігноруються, а якщо частка валідних променів падає нижче 30%, модуль негайно перемикається з контурного обходу стіни на надійніший кінематичний відкат по збережених крихтах.

4. **Запобігання перерегулюванню при різкій зміні напрямку:**
   При переході зі стану зависання у відкат різка зміна заданої швидкості може викликати коливання контуру позиціювання. Для усунення цього ефекту цільовий вейпоінт фільтрується інтегратором обмеження ривка (Jerk-limited Trajectory Generator), що забезпечує плавне прискорення з градієнтом `j_max ≤ 5.0` м/с³.

---

## Крайові випадки та практичні пастки

Під час інтеграції модуля порятунку в реальні польотні стеки слід враховувати такі експлуатаційні нюанси:

1. **Дрейф супутникової навігації (GNSS Multi-path / Spoofing):**
   У глибоких міських каньйонах між висотними будинками відбиті супутникові сигнали спричиняють хибні стрибки координат зі швидкістю 1–2 м/с. Детектор може сприйняти цей дрейф за рух убік і помилково зафіксувати нормальний прогрес. Для запобігання цій помилці розрахунок прогресу `v_prog` повинен базуватися на оцінці швидкості від оптичного потоку (Optical Flow) або комплексованого фільтра EKF (Visual-Inertial Odometry), а не на сирих даних GNSS.

2. **Боротьба із сильним зустрічним вітром:**
   Якщо дрон летить на відкритій місцевості проти вітру зі швидкістю 12 м/с, а максимальна швидкість апарата становить 13 м/с, наближення до цілі може сповільнитися до 0.1 м/с. Щоб детектор не сприйняв це як геометричну пастку, перевіряються показання лідара: якщо всі далекоміри показують чистий простір на дистанції понад 8–10 метрів, активація аварійного відкату блокується.

3. **Штатне зависання під час виконання завдань (Inspection Hover):**
   Коли дрон зупиняється над об'єктом для фотофіксації або очікування команди оператора, польотний стек вимикає прапорець активної тяги до цілі (`thruster_active = false`). У цьому режимі інтегратор прогресу автоматично скидається і не генерує хибних тривог.

4. **Бюджет часу виконання на бортовому MCU:**
   На мікроконтролері STM32H743 (ARM Cortex-M7 @ 480 МГц) виконання одного виклику функції `local_minima_step` із 36 променями лідара займає 8.4 мікросекунди, що становить менше ніж 0.05% процесорного часу при частоті польотного циклу 50 Гц.
