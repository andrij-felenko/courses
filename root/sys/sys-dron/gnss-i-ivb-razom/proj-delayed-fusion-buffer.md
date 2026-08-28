# ⚙️ Кільцевий буфер часового узгодження та ретроспективне злиття в EKF

Супутникові приймачі передають пакети навігаційних даних (PVT) через послідовний інтерфейс UART або шину SPI з істотною затримкою обробки та передачі: від моменту, коли радіохвиля досягла антени, до моменту розбору байтів у польотному контролері минає від 150 до 250 мілісекунд. Якщо подати такий запізнілий вимір у розширений фільтр Калмана безпосередньо до поточного стану апарата, фільтр сприйме зсув у часі за просторову помилку, що на швидкості 20 м/с створить фіктивну нев'язку в 3–5 метрів і призведе до розгойдування швидкості або аварійного розходження фільтра.

Щоб точно врахувати затримку, навігаційний стек зберігає історію вибірок IMU та станів фільтра в кільцевому буфері (Ring Buffer). Коли надходить затримане супутникове вимірювання, алгоритм знаходить точний історичний стан на момент виміру, обчислює інновацію, перевіряє її за критерієм Махаланобіса та поширює розраховану поправку вперед у часі до поточного такту.

## Природа асинхронності та апаратні затримки

У реальній бортовій системі час ділиться на дві нерівні шкали: високочастотну синхронну шкалу внутрішнього таймера мікроконтролера та зовнішню шкалу супутникового часу GNSS.

1. **Апаратний тракт затримки GNSS:**
   - **Затримка радіотракту та кореляції:** обробка цифрових вибірок сигналів у кореляторах приймача та інтегрування на інтервалі коду займає 20–40 мс.
   - **Обчислення навігаційного розв'язку (PVT Task):** розв'язання нелінійної системи рівнянь методом найменших квадратів або внутрішнім фільтром супутникового модуля потребує 40–80 мс залежно від завантаження його мікроконтролера та кількості видимих супутників.
   - **Формування та передача пакетів:** передача бінарного UBX-пакета повідомлення `NAV-PVT` довжиною 92 байти на стандартній швидкості UART 115200 бод займає `(92 · 10) / 115200 ≈ 8.0` мс. При швидкості 38400 бод цей час зростає до 24 мс.
   - **Буферизація в драйвері польотного контролера:** отримання байтів через DMA, перевірка контрольної суми CRC та публікація повідомлення в системну шину публікацій (uORB у PX4 або AP_HAL у ArduPilot) додають ще 5–15 мс.

У підсумку сумарне запізнення `Δt_delay` становить від 120 до 250 мс. Якщо літак виконує розгін із прискоренням 5 м/с², за час затримки 200 мс його швидкість змінюється на `Δv = 5 · 0.2 = 1.0` м/с, а координата зміщується на `Δp = 0.5 · 5 · (0.2)² = 0.1` м додатково до лінійного пробігу `v · Δt = 4.0` м. Без компенсації затримки фільтр спробує компенсувати цей пробіг зміною оцінки зміщення нуля акселерометра, що призведе до фальшивого калібрування давача.

2. **Синхронізація через апаратний строб PPS (Pulse Per Second):**
   Для усунення невизначеності моменту вимірювання сучасні навігаційні модулі видають апаратний імпульс PPS, передній фронт якого з точністю до 15–30 наносекунд збігається з початком секунди супутникового часу UTC. Польотний контролер захоплює цей фронт апаратним таймером (Input Capture Timer) і жорстко прив'язує лічильник мікросекунд мікроконтролера до шкали GNSS. Кожен наступний навігаційний пакет містить мітку часу тижня (Time of Week, TOW), що дозволяє точно визначити, якому саме моменту в минулому відповідає отриманий блок координат.

## Архітектура кільцевого буфера

Кільцевий буфер вибірок організовано як фіксований масив структур `nav_state_t` розміром `N = 256` елементів (ступінь двійки для швидкого бітового маскування індексів замість операції ділення з остачею). При частоті інтегрування IMU 250 Гц кожен слот буфера відповідає кванту часу `Δt = 4` мс, що забезпечує глибину пам'яті:

```
T_buffer = 256 · 0.004 = 1.024 секунди
```

Цього часового вікна більш ніж достатньо для компенсації будь-яких реалістичних затримок передачі пакетів від GNSS (150–250 мс), барометра (20–40 мс) або далекомірів (30–60 мс).

У буфер записуються:
- Мітка монотонного системного часу в мілісекундах `timestamp_ms`;
- Інтегровані координати у локальній навігаційній системі `pos (x, y, z)`;
- Лінійна швидкість `vel (vx, vy, vz)`;
- Орієнтація у вигляді унітарного кватерніона `q (w, x, y, z)`;
- Поточні оцінки зміщень нуля гіроскопів та акселерометрів `gyro_bias`, `accel_bias`.

## Реалізація кільцевого буфера та ретроспективного злиття

Нижче наведено закінчений модуль узгодження затримок та ретроспективної корекції для навігаційного фільтра польотного контролера.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

#define BUFFER_SIZE 256
#define BUFFER_MASK (BUFFER_SIZE - 1)

typedef struct {
    float x, y, z;
} vec3_t;

typedef struct {
    float w, x, y, z;
} quat_t;

/* Знімок навігаційного стану на певний момент часу */
typedef struct {
    uint32_t timestamp_ms;
    vec3_t pos;           /* NED координати (метри) */
    vec3_t vel;           /* NED швидкість (м/с) */
    quat_t q;             /* Орієнтація Body -> NED */
    vec3_t gyro_bias;     /* Зміщення гіроскопа (рад/с) */
    vec3_t accel_bias;    /* Зміщення акселерометра (м/с²) */
} nav_state_t;

/* Кільцевий буфер історичних станів */
typedef struct {
    nav_state_t buffer[BUFFER_SIZE];
    uint32_t head;
    uint32_t count;
} state_ring_buffer_t;

void ring_buffer_init(state_ring_buffer_t *rb) {
    memset(rb, 0, sizeof(state_ring_buffer_t));
}

void ring_buffer_push(state_ring_buffer_t *rb, const nav_state_t *state) {
    rb->buffer[rb->head & BUFFER_MASK] = *state;
    rb->head++;
    if (rb->count < BUFFER_SIZE) {
        rb->count++;
    }
}

/* Пошук найближчого стану в буфері за часовою міткою */
bool ring_buffer_find(const state_ring_buffer_t *rb, uint32_t target_time_ms, nav_state_t *out_state) {
    if (rb->count == 0) return false;

    uint32_t oldest_idx = (rb->head >= rb->count) ? (rb->head - rb->count) : 0;
    uint32_t oldest_time = rb->buffer[oldest_idx & BUFFER_MASK].timestamp_ms;
    uint32_t newest_time = rb->buffer[(rb->head - 1) & BUFFER_MASK].timestamp_ms;

    /* Перевірка виходу за межі буфера */
    if (target_time_ms < oldest_time || target_time_ms > newest_time) {
        return false;
    }

    /* Лінійний пошук від найновішого до найстарішого запису */
    for (uint32_t i = 1; i <= rb->count; ++i) {
        uint32_t idx = (rb->head - i) & BUFFER_MASK;
        if (rb->buffer[idx].timestamp_ms <= target_time_ms) {
            *out_state = rb->buffer[idx];
            return true;
        }
    }
    return false;
}

/* Обчислення інновації та перевірка за Махаланобісом (Gating) */
bool evaluate_gnss_innovation(
    const nav_state_t *historical_state,
    const vec3_t *gnss_pos,
    float pos_noise_var,
    float state_var,
    vec3_t *out_innovation,
    float *out_gain
) {
    /* Інновація: y = z - H * x_hist */
    out_innovation->x = gnss_pos->x - historical_state->pos.x;
    out_innovation->y = gnss_pos->y - historical_state->pos.y;
    out_innovation->z = gnss_pos->z - historical_state->pos.z;

    /* Коваріація інновації: S = P + R */
    float S = state_var + pos_noise_var;
    if (S <= 1e-6f) return false;

    /* Квадрат відстані Махаланобіса d² = yᵀ · S⁻¹ · y */
    float d2 = (out_innovation->x * out_innovation->x +
                out_innovation->y * out_innovation->y +
                out_innovation->z * out_innovation->z) / S;

    /* Поріг відсікання викидів: χ² для 3 ступенів вільності (99% = 11.34) */
    const float GATE_THRESHOLD = 11.34f;
    if (d2 > GATE_THRESHOLD) {
        return false; /* Викид (наприклад, перевідбиття сигналу або стрибок псевдодальності) */
    }

    /* Підсилення Калмана K = P / S */
    *out_gain = state_var / S;
    return true;
}

/* Ретроспективне оновлення поточного стану (Error-State Feedback) */
void apply_delayed_correction(
    nav_state_t *current_state,
    const vec3_t *innovation,
    float gain
) {
    /* Поправка положення та швидкості інжектується в поточний стан */
    current_state->pos.x += gain * innovation->x;
    current_state->pos.y += gain * innovation->y;
    current_state->pos.z += gain * innovation->z;

    /* Поправка швидкості через крос-коваріацію */
    float vel_gain = gain * 0.45f;
    current_state->vel.x += vel_gain * innovation->x;
    current_state->vel.y += vel_gain * innovation->y;
    current_state->vel.z += vel_gain * innovation->z;
}
```
```cpp
#include <array>
#include <cstdint>
#include <cmath>
#include <optional>
#include <span>

struct Vector3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr Vector3 operator+(const Vector3& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    [[nodiscard]] constexpr Vector3 operator-(const Vector3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    [[nodiscard]] constexpr Vector3 operator*(float s) const noexcept {
        return {x * s, y * s, z * s};
    }
    [[nodiscard]] constexpr float squared_norm() const noexcept {
        return x * x + y * y + z * z;
    }
};

struct Quaternion {
    float w{1.0f};
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct NavState {
    uint32_t timestamp_ms{0};
    Vector3 pos{};
    Vector3 vel{};
    Quaternion q{};
    Vector3 gyro_bias{};
    Vector3 accel_bias{};
};

template <size_t Capacity = 256>
class StateHistoryBuffer {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of two");
public:
    constexpr StateHistoryBuffer() noexcept = default;

    void push(const NavState& state) noexcept {
        buffer_[head_ & (Capacity - 1)] = state;
        ++head_;
        if (count_ < Capacity) {
            ++count_;
        }
    }

    [[nodiscard]] std::optional<NavState> find_at(uint32_t target_time_ms) const noexcept {
        if (count_ == 0) return std::nullopt;

        const uint32_t oldest_idx = (head_ >= count_) ? (head_ - count_) : 0;
        const uint32_t oldest_time = buffer_[oldest_idx & (Capacity - 1)].timestamp_ms;
        const uint32_t newest_time = buffer_[(head_ - 1) & (Capacity - 1)].timestamp_ms;

        if (target_time_ms < oldest_time || target_time_ms > newest_time) {
            return std::nullopt;
        }

        for (size_t i = 1; i <= count_; ++i) {
            const size_t idx = (head_ - i) & (Capacity - 1);
            if (buffer_[idx].timestamp_ms <= target_time_ms) {
                return buffer_[idx];
            }
        }
        return std::nullopt;
    }

    [[nodiscard]] constexpr size_t size() const noexcept { return count_; }
    void clear() noexcept { head_ = 0; count_ = 0; }

private:
    std::array<NavState, Capacity> buffer_{};
    size_t head_{0};
    size_t count_{0};
};

class DelayedMeasurementFusion {
public:
    struct FusionResult {
        Vector3 innovation;
        float kalman_gain;
    };

    static constexpr float GateThresholdChi2_3DOF = 11.34f; /* 99% довірчий інтервал */

    [[nodiscard]] static std::optional<FusionResult> evaluate_gnss(
        const NavState& historical_state,
        const Vector3& gnss_pos,
        float pos_noise_var,
        float state_var
    ) noexcept {
        const Vector3 innovation = gnss_pos - historical_state.pos;
        const float S = state_var + pos_noise_var;

        if (S <= 1e-6f) return std::nullopt;

        const float mahalanobis_d2 = innovation.squared_norm() / S;
        if (mahalanobis_d2 > GateThresholdChi2_3DOF) {
            return std::nullopt; /* Відкидаємо аномальне вимірювання */
        }

        const float kalman_gain = state_var / S;
        return FusionResult{innovation, kalman_gain};
    }

    static void apply_feedback(NavState& current_state, const FusionResult& res) noexcept {
        current_state.pos = current_state.pos + res.innovation * res.kalman_gain;
        current_state.vel = current_state.vel + res.innovation * (res.kalman_gain * 0.45f);
    }
};
```
:::

## Покроковий аналіз роботи та крайові випадки

Щоб чітко уявити дію алгоритму, простежмо числовий приклад обробки затриманого пакета:

1. **Нормальний режим польоту:**
   - Дрон рухається на північ зі швидкістю 15 м/с.
   - Поточний системний час `t_now = 12450` мс.
   - Через UART надходить пакет `NAV-PVT` із міткою часу `t_meas = 12250` мс (затримка `200` мс).
   - Поточна інтегрована позиція дрона `p_now = [300.0, 0.0, -50.0]ᵀ` м.
   - Пошук у буфері повертає історичний стан на момент `12250` мс: `p_hist = [297.0, 0.0, -50.0]ᵀ` м.
   - Супутниковий приймач повідомляє координату `z_gnss = [297.1, 0.0, -50.0]ᵀ` м.
   - Справжня інновація становить `y = 297.1 − 297.0 = +0.1` м.
   - Якщо б фільтр порівнював з поточним станом, інновація склала б `297.1 − 300.0 = −2.9` м, викликавши катастрофічне хибне гальмування!

2. **Крайовий випадок: інтерполяція між вибірками (Sub-sample Interpolation):**
   Якщо мітка вимірювання `t_meas` потрапляє між двома записами буфера `t_k` та `t_{k+1}` (наприклад, `12251` мс при кроках `12248` та `12252` мс), точне значення історичного стану знаходиться лінійною інтерполяцією для координат та швидкостей:

   ```
   α = (t_meas − t_k) / (t_{k+1} − t_k)
   p_interp = p_k + α · (p_{k+1} − p_k)
   v_interp = v_k + α · (v_{k+1} − v_k)
   ```

   Для орієнтації замість простого додавання застосовується сферична лінійна інтерполяція кватерніонів (SLERP) або нормалізована лінійна інтерполяція (NLERP), що запобігає спотворенню довжини кватерніона.

3. **Крайовий випадок: переповнення буфера при тривалому затіненні (Buffer Overflow):**
   Якщо внаслідок глибокого маневру або перешкод зв'язок з GNSS переривається більше ніж на 1024 мс, найстаріші записи у кільцевому буфері перезаписуються свіжими даними. Коли після паузи нарешті надходить перший пакет, функція `ring_buffer_find` повертає `false`, оскільки `t_meas < oldest_time`. У цій ситуації фільтр не виконує некоректну екстраполяцію по застарілих даних, а безпечно відкидає перший запізнілий пакет і чекає наступного регулярного відліку.

4. **Захист від багатопроменевості та стрибків псевдодальності (Multipath Glitch):**
   При польоті поруч зі стінами будівель або металевими ангарами відбитий супутниковий сигнал може створити раптовий стрибок координати на 15–30 метрів. Обчислене значення відстані Махаланобіса `d² = yᵀ · S⁻¹ · y` миттєво перевищує довірчий поріг `γ² = 11.34`. Алгоритм маркує вимірювання як викид (Outlier) і блокує інжекцію похибки, захищаючи навігаційний контур автопілота від збурень.
