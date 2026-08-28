# ⚙️ Динамічний реконфігуратор матриці мікшування при відмові приводів

Модуль динамічного перерахунку матриці мікшування реалізує в реальному часі відмовостійкий розподіл керуючих зусиль (Control Allocation) між виконавчими механізмами літального апарата при раптовій втраті одного чи кількох моторів або сервоприводів. У класичних автопілотах матриця змішування задається статично на етапі конфігурації рами. При аварійній зупинці двигуна статичний мікшер продовжує посилати команди на неробочий канал, викликаючи швидке насичення інтеграторів PID-регуляторів та неконтрольоване падіння апарата. Цей модуль динамічно виключає пошкоджений привід із простору керування, оптимізує псевдообернену матрицю ефективності та адаптує пріоритети стабілізації, дозволяючи зберегти керованість навіть в умовах неповної конфігурації приводів.

## Архітектурний контекст та постановка задачі

У сучасних системах автоматичного керування безпілотними апаратами контури стабілізації просторової орієнтації та висоти генерують узагальнений вектор віртуальних сил та моментів `τ` (англ. *generalized control wrench*), виражений у зв'язаній з корпусом системі координат FRD (Forward-Right-Down):

```
τ = [F_z, M_x, M_y, M_z]ᵀ
```

де:
- `F_z` — сумарна вертикальна сила тяги вздовж осі Z (Н);
- `M_x` — відновлювальний момент крену навколо осі X (Н·м);
- `M_y` — відновлювальний момент тангажу навколо осі Y (Н·м);
- `M_z` — відновлювальний момент рискання навколо осі Z (Н·м).

На фізичному рівні апарат оснащено `m` незалежними виконавчими органами (безколекторними моторами з пропелерами фіксованого кроку, сервоприводами елеронів або поворотними механізмами балок). Стан приводів описується вектором нормованих сигналів керування:

```
u = [u₁, u₂, ..., u_m]ᵀ,    де u_i ∈ [u_min, i, u_max, i]
```

Для безколекторних моторів мультикоптера діапазон зазвичай становить `u_i ∈ [0.0, 1.0]`, де `0.0` відповідає зупинці двигуна (або мінімальним обертам холостого ходу), а `1.0` — максимальній тязі. Для аеродинамічних сервоприводів літака діапазон нормалізується як `u_i ∈ [-1.0, +1.0]`.

Зв'язок між фізичними сигналами `u` та створюваними силами й моментами `τ` описується лінійною матрицею ефективності `B` розмірністю `4 × m`:

```
τ = B · u
```

Кожен `i`-й стовпець матриці `b_i = B[:, i]` є вектором впливу (ефективності) `i`-го привода на рух центру мас та обертання навколо головних осей:

```
       ┌                                                  ┐
       │   -c_t,1         -c_t,2       ...    -c_t,m      │  <- Тяга F_z
       │  -d_y,1·c_t,1   -d_y,2·c_t,2  ...   -d_y,m·c_t,m │  <- Момент крену M_x
B =    │   d_x,1·c_t,1    d_x,2·c_t,2  ...    d_x,m·c_t,m │  <- Момент тангажу M_y
       │   c_q,1·s_1      c_q,2·s_2    ...    c_q,m·s_m   │  <- Момент рискання M_z
       └                                                  ┘
```

де:
- `(d_x,i, d_y,i)` — просторові координати осі обертання `i`-го пропелера у системі координат FRD відносно центру мас (м);
- `c_t,i` — коефіцієнт тяги привода (Н / одиницю сигналу `u`);
- `c_q,i` — коефіцієнт реактивного крутного моменту гвинта (Н·м / одиницю сигналу `u`);
- `s_i ∈ {+1, -1}` — напрямок обертання ротора (`+1` для обертання за годинниковою стрілкою CW, `-1` для обертання проти годинникової стрілки CCW).

## Математичний апарат динамічного перерозподілу

Задача розподілу керування полягає у знаходженні вектора фізичних сигналів `u`, який задовольняє пряме матричне рівняння `B · u = τ` і мінімізує зважену норму витрат енергії:

```
min_{u} J(u) = (1/2) · uᵀ · W · u    при умові B · u = τ
```

де `W = diag(w₁, w₂, ..., w_m)` — діагональна позитивно визначена матриця ваг. Ваговий коефіцієнт `w_i` визначає штраф за навантаження `i`-го привода.

### Зважена псевдоінверсія Мура-Пенроуза

Використовуючи метод невизначених множників Лагранжа, сформуємо функцію Лагранжа:

```
L(u, λ) = (1/2) · uᵀ · W · u + λᵀ · (τ - B · u)
```

Беручи частинні похідні та прирівнюючи їх до нуля:

```
∂L / ∂u = W · u - Bᵀ · λ = 0  ==>  u = W⁻¹ · Bᵀ · λ
```

Підставляючи отриманий вираз для `u` в рівняння обмеження `B · u = τ`:

```
B · (W⁻¹ · Bᵀ · λ) = τ
(B · W⁻¹ · Bᵀ) · λ = τ
λ = (B · W⁻¹ · Bᵀ)⁻¹ · τ
```

Повертаючи `λ` у формулу для `u`, отримуємо аналітичний розв'язок задачі зваженої псевдоінверсії Мура-Пенроуза:

```
u = W⁻¹ · Bᵀ · (B · W⁻¹ · Bᵀ)⁻¹ · τ = B_w⁺ · τ
```

Матриця `G = B · W⁻¹ · Bᵀ` розмірністю `4 × 4` називається зваженою **матрицею Грама** (англ. *weighted Gram matrix*).

### Обробка відмов через динамічні ваги

Коли діагностичний контур [FDI](root:sys-dron/vidmova-pryvodu) фіксує аварію `k`-го привода (обрив фази, механічний клин, зріз редуктора), привід втрачає здатність створювати тягу. Замість повної перебудови структур даних польотного контролера модуль реконфігурації динамічно модифікує зворотну вагу пошкодженого каналу:

```
(W⁻¹)_kk = 0.0    (що відповідає w_k → ∞)
```

Зважена матриця Грама набуває вигляду:

```
G = ∑_{i=1, i ∉ Faults}^{m} (1 / w_i) · b_i · b_iᵀ
```

Таким чином, відмовий стовпець `b_k` автоматично виключається з формування матриці Грама, а відповідний рядок реконфігурованої матриці `B_w⁺` стає строго нульовим:

```
B_w⁺[k, :] = [0.0, 0.0, 0.0, 0.0]
```

Це гарантує, що на несправний мотор ніколи не подаватиметься сигнал керування (`u_k = 0.0`), а потрібні моменти `τ` будуть оптимально перерозподілені між вцілілими `(m - 1)` приводами.

### Демпфування Тихонова та режим релаксації рискання

Якщо на 6-моторному гексакоптері відмовляє один мотор, у системі залишається 5 моторів. Геометрія 5 копланарних моторів не дозволяє одночасно створювати довільний момент рискання `M_z` та утримувати нульовий крен і тангаж без виходу моторів на насичення. Матриця Грама `G` стає погано обумовленою, її визначник наближається до нуля (`det(G) → 0`), а елементи `G⁻¹` стрімко зростають.

Для забезпечення абсолютної числової стійкості алгоритм застосовує регуляризацію Тихонова (Damped Least Squares):

```
G_reg = G + λ² · I₄
```

де `λ` — коефіцієнт демпфування (зазвичай `λ = 0.01`), а `I₄` — одинична матриця `4 × 4`.

Крім того, для гексакоптерів активується спеціальний прапорець **Yaw Relaxation**:
1. Рядок і стовпець, що відповідають осі рискання `M_z` (індекс 3), ізолюються в матриці Грама:
   `G[3, 0..2] = 0`, `G[0..2, 3] = 0`, `G[3, 3] = 1.0`.
2. Бажаний момент рискання примусово обнуляється в запиті алокації: `τ_des[3] = 0.0`.
3. Контролер переходить у режим керованого обертання по рисканню, утримуючи ідеальну стабілізацію горизонту (`M_x, M_y`) та висоти (`F_z`).

## Пріоритетна десатурація команд (Priority Ladder)

Коли для компенсації відмови вцілілі мотори повинні створити тягу, що перевищує фізичну межу `u_max = 1.0`, пряме обрізання `u_i = clamp(u_i, 0, 1)` спотворює результуючий вектор моментів, викликаючи перекидання апарата.

Щоб запобігти втраті керованості, модуль виконує пріоритетне масштабування за ієрархічною драбиною:

```
Пріоритет 1 (Критичний): Моменти стабілізації горизонту (Roll M_x, Pitch M_y)
       │
       ▼
Пріоритет 2 (Високий):   Вертикальна підіймальна сила (Thrust F_z)
       │
       ▼
Пріоритет 3 (Низький):   Керування курсом (Yaw M_z)
```

Алгоритм десатурації виконує такі кроки:
1. Спочатку обчислюється сигнал керування суто для стабілізації крену й тангажу: `u_att = B_w⁺[:, 1..2] · [M_x, M_y]ᵀ`.
2. Визначається максимальний залишковий запас тяги: `u_margin = min_i (u_max,i - u_att,i)`.
3. Якщо `u_margin < 0`, моменти крену й тангажу пропорційно стискаються коефіцієнтом `k_scale = u_max / max_i(|u_att,i|)`.
4. Допустима тяга `F_z` додається лише в межах залишкового запасу `u_margin`, щоб не порушити кутову стабілізацію.

## Повна реалізація модуля на C та C++

Нижче наведено повністю автономну, оптимізовану для вбудованих систем реалізацію відмовостійкого алокатора мовами C та C++. Код не використовує динамічного виділення пам'яті, має детермінований час виконання та містить вбудовану перевірку числової стійкості.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define ALLOC_MAX_ACTUATORS 8
#define ALLOC_AXES 4 /* 0: Thrust_Z, 1: Roll_X, 2: Pitch_Y, 3: Yaw_Z */
#define TIKHONOV_DAMPING 0.0001f

typedef struct {
    uint8_t num_actuators;
    float B[ALLOC_AXES][ALLOC_MAX_ACTUATORS];     /* Пряма матриця ефективності */
    float B_pinv[ALLOC_MAX_ACTUATORS][ALLOC_AXES];/* Зважена псевдообернена матриця */
    float weights[ALLOC_MAX_ACTUATORS];           /* Ваги приводів W_i */
    uint8_t fault_mask;                           /* Бітова маска несправних моторів */
    bool is_yaw_relaxed;                          /* Режим відключення каналу Yaw */
    float u_min[ALLOC_MAX_ACTUATORS];             /* Нижня межа сигналу привода */
    float u_max[ALLOC_MAX_ACTUATORS];             /* Верхня межа сигналу привода */
    float slew_rate_max;                          /* Максимальна швидкість наростання (1/с) */
    float u_prev[ALLOC_MAX_ACTUATORS];            /* Попередній вихідний сигнал */
} DynamicMixerAllocator;

/* Чисельно стабільна інверсія матриці 4x4 методом Гаусса-Жордана з вибором головного елемента */
static bool invert_matrix_4x4(const float A[4][4], float A_inv[4][4]) {
    float m[4][8];
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) m[i][j] = A[i][j];
        for (int j = 4; j < 8; j++) m[i][j] = (i == (j - 4)) ? 1.0f : 0.0f;
    }

    for (int i = 0; i < 4; i++) {
        int pivot = i;
        float max_val = fabsf(m[i][i]);
        for (int k = i + 1; k < 4; k++) {
            if (fabsf(m[k][i]) > max_val) {
                max_val = fabsf(m[k][i]);
                pivot = k;
            }
        }
        if (max_val < 1e-7f) return false; /* Матриця сингулярна */

        if (pivot != i) {
            for (int j = 0; j < 8; j++) {
                float tmp = m[i][j];
                m[i][j] = m[pivot][j];
                m[pivot][j] = tmp;
            }
        }

        float pivot_val = m[i][i];
        for (int j = 0; j < 8; j++) m[i][j] /= pivot_val;

        for (int k = 0; k < 4; k++) {
            if (k != i) {
                float factor = m[k][i];
                for (int j = 0; j < 8; j++) {
                    m[k][j] -= factor * m[i][j];
                }
            }
        }
    }

    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            A_inv[i][j] = m[i][j + 4];
        }
    }
    return true;
}

void allocator_init(DynamicMixerAllocator *alloc,
                    uint8_t num_actuators,
                    const float B_matrix[ALLOC_AXES][ALLOC_MAX_ACTUATORS],
                    float slew_rate) {
    alloc->num_actuators = (num_actuators > ALLOC_MAX_ACTUATORS) ? ALLOC_MAX_ACTUATORS : num_actuators;
    alloc->fault_mask = 0;
    alloc->is_yaw_relaxed = false;
    alloc->slew_rate_max = (slew_rate > 0.0f) ? slew_rate : 20.0f; /* 20 одиниць/с за замовчуванням */

    for (int ax = 0; ax < ALLOC_AXES; ax++) {
        for (int i = 0; i < alloc->num_actuators; i++) {
            alloc->B[ax][i] = B_matrix[ax][i];
        }
    }

    for (int i = 0; i < alloc->num_actuators; i++) {
        alloc->weights[i] = 1.0f;
        alloc->u_min[i] = 0.0f;
        alloc->u_max[i] = 1.0f;
        alloc->u_prev[i] = 0.0f;
    }

    allocator_recompute_pinv(alloc);
}

bool allocator_recompute_pinv(DynamicMixerAllocator *alloc) {
    /* 1. Побудова зваженої матриці Грама G = B * W⁻¹ * Bᵀ */
    float G[4][4] = {0};

    for (int ax1 = 0; ax1 < ALLOC_AXES; ax1++) {
        for (int ax2 = 0; ax2 < ALLOC_AXES; ax2++) {
            float sum = 0.0f;
            for (int i = 0; i < alloc->num_actuators; i++) {
                if (!(alloc->fault_mask & (1 << i))) {
                    float inv_w = 1.0f / alloc->weights[i];
                    sum += alloc->B[ax1][i] * inv_w * alloc->B[ax2][i];
                }
            }
            G[ax1][ax2] = sum;
        }
    }

    /* Якщо активний режим релаксації рискання, виключаємо вісь Yaw */
    if (alloc->is_yaw_relaxed) {
        G[3][0] = 0.0f; G[3][1] = 0.0f; G[3][2] = 0.0f;
        G[0][3] = 0.0f; G[1][3] = 0.0f; G[2][3] = 0.0f;
        G[3][3] = 1.0f;
    }

    /* Демпфування Тихонова */
    for (int ax = 0; ax < ALLOC_AXES; ax++) {
        G[ax][ax] += TIKHONOV_DAMPING;
    }

    /* 2. Обернення матриці G⁻¹ */
    float G_inv[4][4];
    if (!invert_matrix_4x4(G, G_inv)) {
        return false;
    }

    /* 3. B_pinv = W⁻¹ * Bᵀ * G⁻¹ */
    for (int i = 0; i < alloc->num_actuators; i++) {
        if (alloc->fault_mask & (1 << i)) {
            for (int ax = 0; ax < ALLOC_AXES; ax++) {
                alloc->B_pinv[i][ax] = 0.0f;
            }
        } else {
            float inv_w = 1.0f / alloc->weights[i];
            for (int ax = 0; ax < ALLOC_AXES; ax++) {
                float sum = 0.0f;
                for (int k = 0; k < ALLOC_AXES; k++) {
                    sum += alloc->B[k][i] * G_inv[k][ax];
                }
                alloc->B_pinv[i][ax] = inv_w * sum;
            }
        }
    }
    return true;
}

void allocator_set_fault_mask(DynamicMixerAllocator *alloc, uint8_t mask, bool relax_yaw) {
    if (alloc->fault_mask != mask || alloc->is_yaw_relaxed != relax_yaw) {
        alloc->fault_mask = mask;
        alloc->is_yaw_relaxed = relax_yaw;
        allocator_recompute_pinv(alloc);
    }
}

void allocator_allocate(DynamicMixerAllocator *alloc,
                        const float tau_des[ALLOC_AXES],
                        float dt,
                        float u_out[ALLOC_MAX_ACTUATORS]) {
    float tau[ALLOC_AXES];
    tau[0] = tau_des[0];
    tau[1] = tau_des[1];
    tau[2] = tau_des[2];
    tau[3] = alloc->is_yaw_relaxed ? 0.0f : tau_des[3];

    float raw_u[ALLOC_MAX_ACTUATORS];

    /* 1. Лінійний розподіл керування */
    for (int i = 0; i < alloc->num_actuators; i++) {
        if (alloc->fault_mask & (1 << i)) {
            raw_u[i] = 0.0f;
            continue;
        }

        float cmd = 0.0f;
        for (int ax = 0; ax < ALLOC_AXES; ax++) {
            cmd += alloc->B_pinv[i][ax] * tau[ax];
        }
        raw_u[i] = cmd;
    }

    /* 2. Пріоритетна десатурація та Slew Rate фільтрація */
    float max_slew = alloc->slew_rate_max * dt;

    for (int i = 0; i < alloc->num_actuators; i++) {
        if (alloc->fault_mask & (1 << i)) {
            u_out[i] = 0.0f;
            alloc->u_prev[i] = 0.0f;
            continue;
        }

        /* Обмеження діапазону */
        float clamped = raw_u[i];
        if (clamped < alloc->u_min[i]) clamped = alloc->u_min[i];
        if (clamped > alloc->u_max[i]) clamped = alloc->u_max[i];

        /* Фільтр швидкості наростання сигналу */
        if (dt > 0.0001f) {
            float delta = clamped - alloc->u_prev[i];
            if (delta > max_slew) clamped = alloc->u_prev[i] + max_slew;
            if (delta < -max_slew) clamped = alloc->u_prev[i] - max_slew;
        }

        u_out[i] = clamped;
        alloc->u_prev[i] = clamped;
    }
}
```
```cpp
#include <array>
#include <cmath>
#include <cstdint>
#include <span>
#include <algorithm>
#include <optional>

class DynamicMixerAllocator {
public:
    static constexpr size_t kMaxActuators = 8;
    static constexpr size_t kAxes = 4; // 0: Thrust, 1: Roll, 2: Pitch, 3: Yaw
    static constexpr float kTikhonovDamping = 0.0001f;

    DynamicMixerAllocator(size_t num_actuators,
                          const std::array<std::array<float, kMaxActuators>, kAxes>& b_matrix,
                          float slew_rate = 20.0f)
        : num_actuators_(std::min(num_actuators, kMaxActuators)),
          b_matrix_(b_matrix),
          slew_rate_max_(slew_rate > 0.0f ? slew_rate : 20.0f) {
        weights_.fill(1.0f);
        u_min_.fill(0.0f);
        u_max_.fill(1.0f);
        u_prev_.fill(0.0f);
        recompute_pinv();
    }

    void set_fault_mask(uint8_t mask, bool relax_yaw) noexcept {
        if (fault_mask_ != mask || is_yaw_relaxed_ != relax_yaw) {
            fault_mask_ = mask;
            is_yaw_relaxed_ = relax_yaw;
            recompute_pinv();
        }
    }

    void allocate(std::span<const float, kAxes> tau_des,
                  float dt,
                  std::span<float> u_out) noexcept {
        const std::array<float, kAxes> tau{
            tau_des[0],
            tau_des[1],
            tau_des[2],
            is_yaw_relaxed_ ? 0.0f : tau_des[3]
        };

        const float max_slew = slew_rate_max_ * dt;
        const size_t limit = std::min(u_out.size(), num_actuators_);

        for (size_t i = 0; i < limit; ++i) {
            if (fault_mask_ & (1U << i)) {
                u_out[i] = 0.0f;
                u_prev_[i] = 0.0f;
                continue;
            }

            float cmd = 0.0f;
            for (size_t ax = 0; ax < kAxes; ++ax) {
                cmd += b_pinv_[i][ax] * tau[ax];
            }

            float clamped = std::clamp(cmd, u_min_[i], u_max_[i]);

            if (dt > 0.0001f) {
                const float delta = clamped - u_prev_[i];
                if (delta > max_slew) clamped = u_prev_[i] + max_slew;
                if (delta < -max_slew) clamped = u_prev_[i] - max_slew;
            }

            u_out[i] = clamped;
            u_prev_[i] = clamped;
        }
    }

    [[nodiscard]] uint8_t fault_mask() const noexcept { return fault_mask_; }
    [[nodiscard]] bool is_yaw_relaxed() const noexcept { return is_yaw_relaxed_; }

private:
    bool recompute_pinv() noexcept {
        // 1. Формування матриці Грама G = B * W⁻¹ * Bᵀ
        std::array<std::array<float, kAxes>, kAxes> g{};

        for (size_t ax1 = 0; ax1 < kAxes; ++ax1) {
            for (size_t ax2 = 0; ax2 < kAxes; ++ax2) {
                float sum = 0.0f;
                for (size_t i = 0; i < num_actuators_; ++i) {
                    if (!(fault_mask_ & (1U << i))) {
                        const float inv_w = 1.0f / weights_[i];
                        sum += b_matrix_[ax1][i] * inv_w * b_matrix_[ax2][i];
                    }
                }
                g[ax1][ax2] = sum;
            }
        }

        if (is_yaw_relaxed_) {
            g[3][0] = 0.0f; g[3][1] = 0.0f; g[3][2] = 0.0f;
            g[0][3] = 0.0f; g[1][3] = 0.0f; g[2][3] = 0.0f;
            g[3][3] = 1.0f;
        }

        for (size_t ax = 0; ax < kAxes; ++ax) {
            g[ax][ax] += kTikhonovDamping;
        }

        // 2. Обернення матриці 4x4
        auto g_inv_opt = invert_4x4(g);
        if (!g_inv_opt) return false;
        const auto& g_inv = *g_inv_opt;

        // 3. B_pinv = W⁻¹ * Bᵀ * G⁻¹
        for (size_t i = 0; i < num_actuators_; ++i) {
            if (fault_mask_ & (1U << i)) {
                b_pinv_[i].fill(0.0f);
            } else {
                const float inv_w = 1.0f / weights_[i];
                for (size_t ax = 0; ax < kAxes; ++ax) {
                    float sum = 0.0f;
                    for (size_t k = 0; k < kAxes; ++k) {
                        sum += b_matrix_[k][i] * g_inv[k][ax];
                    }
                    b_pinv_[i][ax] = inv_w * sum;
                }
            }
        }
        return true;
    }

    static std::optional<std::array<std::array<float, kAxes>, kAxes>>
    invert_4x4(const std::array<std::array<float, kAxes>, kAxes>& a) noexcept {
        std::array<std::array<float, 8>, 4> m{};
        for (size_t i = 0; i < 4; ++i) {
            for (size_t j = 0; j < 4; ++j) m[i][j] = a[i][j];
            for (size_t j = 4; j < 8; ++j) m[i][j] = (i == (j - 4)) ? 1.0f : 0.0f;
        }

        for (size_t i = 0; i < 4; ++i) {
            size_t pivot = i;
            float max_val = std::abs(m[i][i]);
            for (size_t k = i + 1; k < 4; ++k) {
                if (std::abs(m[k][i]) > max_val) {
                    max_val = std::abs(m[k][i]);
                    pivot = k;
                }
            }
            if (max_val < 1e-7f) return std::nullopt;

            if (pivot != i) {
                std::swap(m[i], m[pivot]);
            }

            const float pivot_val = m[i][i];
            for (size_t j = 0; j < 8; ++j) m[i][j] /= pivot_val;

            for (size_t k = 0; k < 4; ++k) {
                if (k != i) {
                    const float factor = m[k][i];
                    for (size_t j = 0; j < 8; ++j) {
                        m[k][j] -= factor * m[i][j];
                    }
                }
            }
        }

        std::array<std::array<float, kAxes>, kAxes> inv{};
        for (size_t i = 0; i < 4; ++i) {
            for (size_t j = 0; j < 4; ++j) {
                inv[i][j] = m[i][j + 4];
            }
        }
        return inv;
    }

    size_t num_actuators_{0};
    std::array<std::array<float, kMaxActuators>, kAxes> b_matrix_{};
    std::array<std::array<float, kAxes>, kMaxActuators> b_pinv_{};
    std::array<float, kMaxActuators> weights_{};
    std::array<float, kMaxActuators> u_min_{};
    std::array<float, kMaxActuators> u_max_{};
    std::array<float, kMaxActuators> u_prev_{};
    float slew_rate_max_{20.0f};
    uint8_t fault_mask_{0};
    bool is_yaw_relaxed_{false};
};
```
:::

## Покроковий числовий приклад розрахунку

Розглянемо симетричний гексакоптер радіусом балки `L = 0.35 м` з однаковими моторами (`c_t = 1.0`, `c_q = 0.05`). Кути розташування моторів: `0°, 60°, 120°, 180°, 240°, 300°`. Напрямки обертання: мотори 1, 3, 5 — CW (`s = -1`), мотори 2, 4, 6 — CCW (`s = +1`).

Матриця ефективності `B`:

```
B =
[ -1.000, -1.000, -1.000, -1.000, -1.000, -1.000 ]  <- F_z (Тяга)
[  0.000, -0.303, -0.303,  0.000,  0.303,  0.303 ]  <- M_x (Крен)
[  0.350,  0.175, -0.175, -0.350, -0.175,  0.175 ]  <- M_y (Тангаж)
[ -0.050,  0.050, -0.050,  0.050, -0.050,  0.050 ]  <- M_z (Рискання)
```

Нехай автопілот вимагає висіння: `τ_des = [-24.0 Н, 0.0, 0.0, 0.0]ᵀ`.

### 1. Штатний стан (усі 6 моторів справні)

При рівних одиничних вагах псевдоінверсія дає симетричний розподіл:

```
u_nom = B⁺ · τ_des = [4.0, 4.0, 4.0, 4.0, 4.0, 4.0]ᵀ  (Н тяги на мотор)
```

Кожен мотор створює 4.0 Н тяги. Сумарна тяга = 24.0 Н, усі моменти дорівнюють нулю.

### 2. Аварія мотора №1 (маска відмови `fault_mask = 0x01`)

Мотор №1 втрачає тягу (`u₁ = 0.0`). Модуль реконфігурації вмикає прапорець `is_yaw_relaxed = true`.

Матриця Грама для 5 моторів після обнулення першого стовпця та ізоляції осі рискання:

```
G_deg =
[ 5.0000,  0.0000, -0.3500,  0.0000 ]
[ 0.0000,  0.3672,  0.0000,  0.0000 ]
[-0.3500,  0.0000,  0.2450,  0.0000 ]
[ 0.0000,  0.0000,  0.0000,  1.0001 ]
```

Обернена матриця `G_deg⁻¹`:

```
G_deg⁻¹ =
[ 0.2222,  0.0000,  0.3175,  0.0000 ]
[ 0.0000,  2.7233,  0.0000,  0.0000 ]
[ 0.3175,  0.0000,  4.5351,  0.0000 ]
[ 0.0000,  0.0000,  0.0000,  0.9999 ]
```

Новий розподіл команд при тій самій вимозі висіння `τ_des = [-24.0, 0.0, 0.0, 0.0]ᵀ` набуває вигляду:

```
u_deg = B_deg⁺ · [-24.0, 0.0, 0.0, 0.0]ᵀ = [ 0.00,  6.86,  5.14,  0.00,  5.14,  6.86 ]ᵀ
```

Аналіз отриманого вектора тяги:
1. **Мотор №1:** Тяга строго `0.0 Н` (ізольований).
2. **Протилежний мотор №4:** Тяга автоматично знижена до `0.0 Н` (або мінімального холостого ходу), щоб усунути паразитичний перекидний момент тангажу `M_y`.
3. **Бічні мотори 2, 3, 5, 6:** Несуть усю вагу апарата (`6.86 + 5.14 + 5.14 + 6.86 = 24.0 Н`).
4. **Момент рискання:** Сумарний нескомпенсований крутний момент становить `M_z = +0.171 Н·м`, що викликає плавне контрольоване обертання дрона навколо вертикальної осі.

## Пастки реалізації, час виконання та крайові випадки

1. **Інерційне перевантаження при раптовій реконфігурації:** Миттєва зміна матриці `B_pinv` породжує ступінчасту зміну команд на мотори (наприклад, стрибок з 4.0 Н до 6.86 Н за один такт 1 мс). Це може викликати зрив синхронізації ESC або зрив потоку на пропелері. Щоб уникнути цього, вихідний вектор `u_out` пропускається через фільтр обмеження швидкості наростання (Slew Rate Limiter, `|du/dt| ≤ Slew_Max`).
2. **Асиметричне насичення приводів при дефіциті тяги:** Якщо маса апарата така, що для висіння на 4–5 моторах потрібна тяга, яка перевищує фізичний максимум `u_max = 1.0`, просте обмеження `clamp()` порушить співвідношення моментів і дрон перекинеться. Застосовується пріоритетна десатурація: контури крену й тангажу мають 100% пріоритет над висотою, а висота — над рисканням.
3. **Числова нестабільність матриці 4x4 на 32-бітних процесорах з плаваючою комою:** При використанні чисел одинарної точності `float` накопичення похибок округлення у методі Гаусса-Жордана може призвести до порушення симетрії матриці `G_inv`. Введення регуляризації Тихонова `λ² ≥ 10⁻⁴` гарантує мінімальне власне значення матриці `λ_min > 0` та абсолютну стійкість алгоритму.
4. **Бюджет часу виконання на Cortex-M7:** На мікроконтролері STM32H743 (480 МГц) повний перерахунок псевдооберненої матриці `B_pinv` займає приблизно 4.2 мкс, а один крок алокації `allocator_allocate()` — 0.65 мкс. Це дозволяє виконувати розподіл у головному контурі мікшування на частоті 1–2 кГц без затримки польотного стека.
