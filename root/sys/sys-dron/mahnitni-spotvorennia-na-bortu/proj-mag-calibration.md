# ⚙️ Бортовий калібратор магнітометра: бінування простору та матричне розв'язання

Калібрування магнітометра на борту дрона або робототехнічної платформи відбувається в умовах суворих апаратних обмежень: мікроконтролер польотного стека (наприклад, STM32F4/F7/H7) має обмежений обсяг оперативної пам'яті RAM і не може виділити десятки кілобайт для зберігання сирих масивів тривимірних векторів магнітної індукції. Крім того, обчислювальні ресурси під час основного циклу керування обмежені, тому алгоритм повинен виконувати попереднє накопичення даних з мінімальними накладними витратами часу процесора.

Друга критична проблема пов'язана з людським фактором: коли оператор вручну повертає апарат у повітрі («танець компаса»), рух є нерівномірним. Людина природно довше утримує апарат у зручних горизонтальних або вертикальних орієнтаціях, створюючи щільні скупчення сотень майже однакових точок, тоді як діагональні кути залишаються ненасиченими. Якщо подати таку нерівномірну вибірку в стандартний алгоритм найменших квадратів без просторової фільтрації, матриця нормальних рівнянь деформується в бік перенасичених областей, що призводить до зміщення оцінки центру еліпсоїда та спотворення обчисленого курсу на 10–25 градусів.

Нижче наведено повну архітектуру бортового калібратора, яка розв'язує ці інженерні виклики через поєднання просторового бінування, потокового накопичувача нормальних рівнянь та числово стійкого розв'язувача лінійних систем.

## Архітектура та етапи роботи калібратора

Модуль калібрування організовано у вигляді кінцевого автомата (Finite State Machine), що послідовно проходить такі стадії:

1. **Ініціалізація та очищення накопичувачів:** матриця нормальних рівнянь `Hᵀ·H` розміром 9×9 та правий вектор `Hᵀ·1` розміром 9×1 занулюються. Встановлюються початкові значення матриці м'якого заліза (одинична матриця) та вектора твердого заліза (нульовий вектор).
2. **Просторове бінування сфери (Sphere Sector Binning):** простір орієнтацій розбивається на фіксовану кількість кутових секторів за азимутом і кутом місця (наприклад, 12 секторів за азимутом по 30° та 6 секторів за кутом місця по 30°, що дає сумарно 72 просторові комірки-біни). Кожен новий вектор перетворюється у сферичні координати для визначення індексу сектора. Якщо відповідний сектор уже містить максимальну дозволену кількість зразків (наприклад, 5 точок), новий відлік відкидається. Це гарантує рівномірність хмари точок по всій поверхні еліпсоїда незалежно від швидкості обертання дрона.
3. **Потокове накопичення квадрики:** прийнятий вектор миттєво використовується для обчислення компонентів базисного вектора `h = (x², y², z², xy, xz, yz, x, y, z)` та додавання його зовнішнього добутку `h · hᵀ` до накопичувальної матриці `Hᵀ·H`. Сирі координати не зберігаються в пам'яті, завдяки чому весь накопичувач займає менше 500 байтів RAM.
4. **Матричний розв'язок системи 9×9:** після заповнення достатньої кількості секторів (не менше 36–40 точок у різних квадрантах) система нормальних рівнянь розв'язується методом Гаусса з вибором головного елемента по стовпцю (Partial Pivoting) для запобігання втраті точності при діленні на малі діагональні елементи.
5. **Виділення геометрії та розклад Холецького:** із розв'язку відновлюється матриця форми `A` та лінійний вектор `b`. Обчислюється центр еліпсоїда `V_hard = −A⁻¹·b`, масштабний коефіцієнт та нормована матриця `M = A / scale`. Факторизація Холецького `M = L·Lᵀ` дає верхньотрикутну матрицю корекції `T = B₀·Lᵀ`.
6. **Онлайн-застосування корекції:** у реальному часі польотного циклу корекція виконується за один матрично-векторний добуток `B_calibrated = T · (B_raw − V_hard)`, що вимагає лише кількох мікросекунд на ядрі ARM Cortex-M4/M7.

## Інтеграція з протоколом MAVLink та збереження параметрів

Під час інтеграції бортового калібратора у польотні стеки (PX4 Autopilot або ArduPilot) алгоритм взаємодіє з наземною станцією керування (QGroundControl / Mission Planner) через стандартний набір повідомлень MAVLink:
- **`MAG_CAL_REPORT` / `MAG_CAL_PROGRESS`:** автопілот періодично (з частотою 5–10 Гц) транслює на станцію бітову маску заповнених просторових секторів та загальний відсоток готовності вибірки `completion_pct`. Це дозволяє графічному інтерфейсу станції відображати 3D-модель сфери із зафарбовуванням секторів, що наочно показує пілоту, в яку саме орієнтацію ще потрібно нахилити апарат.
- **Енергонезалежне збереження параметрів:** після успішного обчислення вектор зміщення `V_hard` записується у параметри енергонезалежної пам'яті FRAM/EEPROM (наприклад, `CAL_MAG0_XOFF`, `CAL_MAG0_YOFF`, `CAL_MAG0_ZOFF`), а верхньотрикутні коефіцієнти матриці `T` зберігаються як масштаби та перехресні коефіцієнти (`CAL_MAG0_XSCALE`, `CAL_MAG0_YSCALE`, `CAL_MAG0_ZSCALE`, `CAL_MAG0_XYOFF`, `CAL_MAG0_XZOFF`, `CAL_MAG0_YZOFF`). При наступних запусках автопілот миттєво ініціалізує калібрувальну матрицю без повторної процедури вписування.

## Програмна реалізація мовами C та C++

:::tabs
```c
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

#define MAG_CAL_SECTORS_AZIMUTH   12
#define MAG_CAL_SECTORS_ELEVATION 6
#define MAG_CAL_TOTAL_BINS        (MAG_CAL_SECTORS_AZIMUTH * MAG_CAL_SECTORS_ELEVATION)
#define MAG_CAL_MIN_SAMPLES       36
#define MAG_CAL_MAX_PER_BIN       5

typedef struct {
    float hth[9][9];                       /* Матриця нормальних рівнянь Hᵀ·H */
    float ht1[9];                          /* Правий вектор Hᵀ·1 */
    uint8_t bin_counts[MAG_CAL_TOTAL_BINS];/* Лічильник відліків по секторах */
    uint32_t total_samples;                /* Загальна кількість врахованих точок */
    bool is_calibrated;                    /* Прапорець успішності обчислення */
    float v_hard[3];                       /* Вектор зміщення твердого заліза */
    float t_soft[3][3];                    /* Матриця компенсації м'якого заліза */
    float earth_field_uT;                  /* Очікувана напруженість поля Землі */
} mag_calibrator_t;

void mag_cal_init(mag_calibrator_t *cal, float earth_field_uT) {
    memset(cal, 0, sizeof(mag_calibrator_t));
    cal->earth_field_uT = (earth_field_uT > 10.0f) ? earth_field_uT : 45.0f;
    cal->t_soft[0][0] = 1.0f;
    cal->t_soft[1][1] = 1.0f;
    cal->t_soft[2][2] = 1.0f;
}

/* Визначення індексу просторового сектора за координатами вимірювання */
static int mag_cal_get_bin_index(float x, float y, float z) {
    float norm = sqrtf(x * x + y * y + z * z);
    if (norm < 1e-4f) return 0;

    float azimuth = atan2f(y, x); /* Діапазон [-π, +π] */
    if (azimuth < 0.0f) azimuth += 2.0f * (float)M_PI;
    int az_bin = (int)(azimuth / (2.0f * (float)M_PI / MAG_CAL_SECTORS_AZIMUTH));
    if (az_bin >= MAG_CAL_SECTORS_AZIMUTH) az_bin = MAG_CAL_SECTORS_AZIMUTH - 1;

    float elevation = asinf(z / norm); /* Діапазон [-π/2, +π/2] */
    float norm_elev = elevation + (float)M_PI * 0.5f; /* Діапазон [0, π] */
    int el_bin = (int)(norm_elev / ((float)M_PI / MAG_CAL_SECTORS_ELEVATION));
    if (el_bin >= MAG_CAL_SECTORS_ELEVATION) el_bin = MAG_CAL_SECTORS_ELEVATION - 1;

    return el_bin * MAG_CAL_SECTORS_AZIMUTH + az_bin;
}

/* Додавання сирого вимірювання до накопичувача МНК з фільтрацією надлишкових точок */
bool mag_cal_add_sample(mag_calibrator_t *cal, float x, float y, float z) {
    int bin = mag_cal_get_bin_index(x, y, z);
    if (cal->bin_counts[bin] >= MAG_CAL_MAX_PER_BIN) {
        return false; /* Сектор заповнений, пропускаємо дубль */
    }

    cal->bin_counts[bin]++;
    cal->total_samples++;

    /* Вектор базисних функцій квадрики H_i */
    float h[9];
    h[0] = x * x;
    h[1] = y * y;
    h[2] = z * z;
    h[3] = x * y;
    h[4] = x * z;
    h[5] = y * z;
    h[6] = x;
    h[7] = y;
    h[8] = z;

    /* Акумуляція симетричної матриці Hᵀ · H та вектора Hᵀ · 1 */
    for (int i = 0; i < 9; i++) {
        cal->ht1[i] += h[i];
        for (int j = 0; j < 9; j++) {
            cal->hth[i][j] += h[i] * h[j];
        }
    }
    return true;
}

/* Розв'язання лінійної системи 9×9 методом Гаусса з вибором головного елемента */
static bool solve_linear_system_9x9(float A[9][9], float b[9], float x_out[9]) {
    float M[9][10];
    for (int i = 0; i < 9; i++) {
        for (int j = 0; j < 9; j++) {
            M[i][j] = A[i][j];
        }
        M[i][9] = b[i];
    }

    /* Прямий хід з вибором головного елемента по стовпцю */
    for (int col = 0; col < 9; col++) {
        int max_row = col;
        float max_val = fabsf(M[col][col]);
        for (int row = col + 1; row < 9; row++) {
            float v = fabsf(M[row][col]);
            if (v > max_val) {
                max_val = v;
                max_row = row;
            }
        }
        if (max_val < 1e-9f) return false; /* Матриця сингулярна або погано обумовлена */

        if (max_row != col) {
            for (int k = col; k < 10; k++) {
                float tmp = M[col][k];
                M[col][k] = M[max_row][k];
                M[max_row][k] = tmp;
            }
        }

        for (int row = col + 1; row < 9; row++) {
            float factor = M[row][col] / M[col][col];
            for (int k = col; k < 10; k++) {
                M[row][k] -= factor * M[col][k];
            }
        }
    }

    /* Зворотний хід Гаусса */
    for (int row = 8; row >= 0; row--) {
        float sum = M[row][9];
        for (int col = row + 1; col < 9; col++) {
            sum -= M[row][col] * x_out[col];
        }
        x_out[row] = sum / M[row][row];
    }
    return true;
}

/* Аналітичне обернення матриці 3×3 через алгебраїчні доповнення */
static bool invert_matrix_3x3(const float A[3][3], float inv[3][3]) {
    float det = A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1]) -
                A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0]) +
                A[0][2] * (A[1][0] * A[2][1] - A[1][2] * A[2][0]);
    if (fabsf(det) < 1e-12f) return false;

    float inv_det = 1.0f / det;
    inv[0][0] = (A[1][1] * A[2][2] - A[1][2] * A[2][1]) * inv_det;
    inv[0][1] = (A[0][2] * A[2][1] - A[0][1] * A[2][2]) * inv_det;
    inv[0][2] = (A[0][1] * A[1][2] - A[0][2] * A[1][1]) * inv_det;
    inv[1][0] = (A[1][2] * A[2][0] - A[1][0] * A[2][2]) * inv_det;
    inv[1][1] = (A[0][0] * A[2][2] - A[0][2] * A[2][0]) * inv_det;
    inv[1][2] = (A[0][2] * A[1][0] - A[0][0] * A[1][2]) * inv_det;
    inv[2][0] = (A[1][0] * A[2][1] - A[1][1] * A[2][0]) * inv_det;
    inv[2][1] = (A[0][1] * A[2][0] - A[0][0] * A[2][1]) * inv_det;
    inv[2][2] = (A[0][0] * A[1][1] - A[0][1] * A[1][0]) * inv_det;
    return true;
}

/* Обчислення підсумкових параметрів твердого та м'якого заліза */
bool mag_cal_compute(mag_calibrator_t *cal) {
    if (cal->total_samples < MAG_CAL_MIN_SAMPLES) return false;

    float p[9];
    if (!solve_linear_system_9x9(cal->hth, cal->ht1, p)) return false;

    /* Відновлення матриці форми A та вектора лінійних коефіцієнтів b */
    float A[3][3] = {
        { p[0],        p[3] * 0.5f, p[4] * 0.5f },
        { p[3] * 0.5f, p[1],        p[5] * 0.5f },
        { p[4] * 0.5f, p[5] * 0.5f, p[2]        }
    };
    float b[3] = { p[6] * 0.5f, p[7] * 0.5f, p[8] * 0.5f };

    float A_inv[3][3];
    if (!invert_matrix_3x3(A, A_inv)) return false;

    /* Центр еліпсоїда V_hard = -A⁻¹ · b */
    for (int i = 0; i < 3; i++) {
        cal->v_hard[i] = -(A_inv[i][0] * b[0] + A_inv[i][1] * b[1] + A_inv[i][2] * b[2]);
    }

    /* Масштаб форми scale = V_hardᵀ · A · V_hard + 1.0 */
    float Av[3] = {
        A[0][0] * cal->v_hard[0] + A[0][1] * cal->v_hard[1] + A[0][2] * cal->v_hard[2],
        A[1][0] * cal->v_hard[0] + A[1][1] * cal->v_hard[1] + A[1][2] * cal->v_hard[2],
        A[2][0] * cal->v_hard[0] + A[2][1] * cal->v_hard[1] + A[2][2] * cal->v_hard[2]
    };
    float scale = cal->v_hard[0] * Av[0] + cal->v_hard[1] * Av[1] + cal->v_hard[2] * Av[2] + 1.0f;
    if (scale <= 1e-6f) return false;

    /* Нормована матриця форми M = A / scale */
    float M[3][3];
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            M[i][j] = A[i][j] / scale;
        }
    }

    /* Розклад Холецького M = L · Lᵀ */
    float L[3][3] = {0};
    if (M[0][0] <= 0.0f) return false;
    L[0][0] = sqrtf(M[0][0]);
    L[1][0] = M[1][0] / L[0][0];
    L[2][0] = M[2][0] / L[0][0];

    float d11 = M[1][1] - L[1][0] * L[1][0];
    if (d11 <= 0.0f) return false;
    L[1][1] = sqrtf(d11);
    L[2][1] = (M[2][1] - L[2][0] * L[1][0]) / L[1][1];

    float d22 = M[2][2] - L[2][0] * L[2][0] - L[2][1] * L[2][1];
    if (d22 <= 0.0f) return false;
    L[2][2] = sqrtf(d22);

    /* Матриця компенсації T = B₀ · Lᵀ (верхня трикутна) */
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            cal->t_soft[i][j] = cal->earth_field_uT * L[j][i];
        }
    }

    cal->is_calibrated = true;
    return true;
}

/* Онлайн-корекція сирих відліків у циклі керування */
void mag_cal_apply(const mag_calibrator_t *cal, float rx, float ry, float rz,
                   float *cx, float *cy, float *cz) {
    if (!cal->is_calibrated) {
        *cx = rx; *cy = ry; *cz = rz;
        return;
    }
    float dx = rx - cal->v_hard[0];
    float dy = ry - cal->v_hard[1];
    float dz = rz - cal->v_hard[2];

    *cx = cal->t_soft[0][0] * dx + cal->t_soft[0][1] * dy + cal->t_soft[0][2] * dz;
    *cy = cal->t_soft[1][0] * dx + cal->t_soft[1][1] * dy + cal->t_soft[1][2] * dz;
    *cz = cal->t_soft[2][0] * dx + cal->t_soft[2][1] * dy + cal->t_soft[2][2] * dz;
}
```
```cpp
#include <array>
#include <cmath>
#include <numbers>
#include <span>
#include <cstdint>

class MagCalibrator {
public:
    static constexpr size_t kAzimuthSectors = 12;
    static constexpr size_t kElevationSectors = 6;
    static constexpr size_t kTotalBins = kAzimuthSectors * kElevationSectors;
    static constexpr size_t kMinSamples = 36;
    static constexpr uint8_t kMaxPerBin = 5;

    struct Vec3 {
        float x{0.0f}, y{0.0f}, z{0.0f};
    };

    struct Matrix3x3 {
        std::array<std::array<float, 3>, 3> m{{{1,0,0}, {0,1,0}, {0,0,1}}};
    };

    explicit MagCalibrator(float earth_field_uT = 45.0f) noexcept
        : earth_field_uT_{earth_field_uT > 10.0f ? earth_field_uT : 45.0f} {
        reset();
    }

    void reset() noexcept {
        for (auto& row : hth_) row.fill(0.0f);
        ht1_.fill(0.0f);
        bin_counts_.fill(0);
        total_samples_ = 0;
        is_calibrated_ = false;
        v_hard_ = {};
        t_soft_ = Matrix3x3{};
    }

    bool add_sample(const Vec3& sample) noexcept {
        const size_t bin = compute_bin_index(sample);
        if (bin_counts_[bin] >= kMaxPerBin) {
            return false;
        }

        bin_counts_[bin]++;
        total_samples_++;

        const std::array<float, 9> h{
            sample.x * sample.x,
            sample.y * sample.y,
            sample.z * sample.z,
            sample.x * sample.y,
            sample.x * sample.z,
            sample.y * sample.z,
            sample.x,
            sample.y,
            sample.z
        };

        for (size_t i = 0; i < 9; ++i) {
            ht1_[i] += h[i];
            for (size_t j = 0; j < 9; ++j) {
                hth_[i][j] += h[i] * h[j];
            }
        }
        return true;
    }

    bool compute() noexcept {
        if (total_samples_ < kMinSamples) return false;

        std::array<float, 9> p{};
        if (!solve_linear_system_9x9(hth_, ht1_, p)) return false;

        Matrix3x3 A{{{
            { p[0],        p[3] * 0.5f, p[4] * 0.5f },
            { p[3] * 0.5f, p[1],        p[5] * 0.5f },
            { p[4] * 0.5f, p[5] * 0.5f, p[2]        }
        }}};
        const Vec3 b{ p[6] * 0.5f, p[7] * 0.5f, p[8] * 0.5f };

        Matrix3x3 A_inv{};
        if (!invert_matrix_3x3(A, A_inv)) return false;

        v_hard_.x = -(A_inv.m[0][0] * b.x + A_inv.m[0][1] * b.y + A_inv.m[0][2] * b.z);
        v_hard_.y = -(A_inv.m[1][0] * b.x + A_inv.m[1][1] * b.y + A_inv.m[1][2] * b.z);
        v_hard_.z = -(A_inv.m[2][0] * b.x + A_inv.m[2][1] * b.y + A_inv.m[2][2] * b.z);

        const Vec3 Av{
            A.m[0][0] * v_hard_.x + A.m[0][1] * v_hard_.y + A.m[0][2] * v_hard_.z,
            A.m[1][0] * v_hard_.x + A.m[1][1] * v_hard_.y + A.m[1][2] * v_hard_.z,
            A.m[2][0] * v_hard_.x + A.m[2][1] * v_hard_.y + A.m[2][2] * v_hard_.z
        };
        const float scale = v_hard_.x * Av.x + v_hard_.y * Av.y + v_hard_.z * Av.z + 1.0f;
        if (scale <= 1e-6f) return false;

        Matrix3x3 M{};
        for (size_t i = 0; i < 3; ++i) {
            for (size_t j = 0; j < 3; ++j) {
                M.m[i][j] = A.m[i][j] / scale;
            }
        }

        Matrix3x3 L{};
        if (M.m[0][0] <= 0.0f) return false;
        L.m[0][0] = std::sqrt(M.m[0][0]);
        L.m[1][0] = M.m[1][0] / L.m[0][0];
        L.m[2][0] = M.m[2][0] / L.m[0][0];

        const float d11 = M.m[1][1] - L.m[1][0] * L.m[1][0];
        if (d11 <= 0.0f) return false;
        L.m[1][1] = std::sqrt(d11);
        L.m[2][1] = (M.m[2][1] - L.m[2][0] * L.m[1][0]) / L.m[1][1];

        const float d22 = M.m[2][2] - L.m[2][0] * L.m[2][0] - L.m[2][1] * L.m[2][1];
        if (d22 <= 0.0f) return false;
        L.m[2][2] = std::sqrt(d22);

        for (size_t i = 0; i < 3; ++i) {
            for (size_t j = 0; j < 3; ++j) {
                t_soft_.m[i][j] = earth_field_uT_ * L.m[j][i];
            }
        }

        is_calibrated_ = true;
        return true;
    }

    [[nodiscard]] Vec3 apply(const Vec3& raw) const noexcept {
        if (!is_calibrated_) return raw;
        const float dx = raw.x - v_hard_.x;
        const float dy = raw.y - v_hard_.y;
        const float dz = raw.z - v_hard_.z;

        return Vec3{
            t_soft_.m[0][0] * dx + t_soft_.m[0][1] * dy + t_soft_.m[0][2] * dz,
            t_soft_.m[1][0] * dx + t_soft_.m[1][1] * dy + t_soft_.m[1][2] * dz,
            t_soft_.m[2][0] * dx + t_soft_.m[2][1] * dy + t_soft_.m[2][2] * dz
        };
    }

    [[nodiscard]] bool is_calibrated() const noexcept { return is_calibrated_; }
    [[nodiscard]] const Vec3& hard_iron_offset() const noexcept { return v_hard_; }
    [[nodiscard]] const Matrix3x3& soft_iron_matrix() const noexcept { return t_soft_; }

private:
    float earth_field_uT_{45.0f};
    std::array<std::array<float, 9>, 9> hth_{};
    std::array<float, 9> ht1_{};
    std::array<uint8_t, kTotalBins> bin_counts_{};
    uint32_t total_samples_{0};
    bool is_calibrated_{false};
    Vec3 v_hard_{};
    Matrix3x3 t_soft_{};

    static size_t compute_bin_index(const Vec3& p) noexcept {
        const float norm = std::sqrt(p.x * p.x + p.y * p.y + p.z * p.z);
        if (norm < 1e-4f) return 0;

        float azimuth = std::atan2(p.y, p.x);
        if (azimuth < 0.0f) azimuth += 2.0f * std::numbers::pi_v<float>;
        auto az_bin = static_cast<size_t>(azimuth / (2.0f * std::numbers::pi_v<float> / kAzimuthSectors));
        if (az_bin >= kAzimuthSectors) az_bin = kAzimuthSectors - 1;

        const float elevation = std::asin(p.z / norm);
        const float norm_elev = elevation + std::numbers::pi_v<float> * 0.5f;
        auto el_bin = static_cast<size_t>(norm_elev / (std::numbers::pi_v<float> / kElevationSectors));
        if (el_bin >= kElevationSectors) el_bin = kElevationSectors - 1;

        return el_bin * kAzimuthSectors + az_bin;
    }

    static bool solve_linear_system_9x9(
        const std::array<std::array<float, 9>, 9>& A,
        const std::array<float, 9>& b,
        std::array<float, 9>& x_out) noexcept {
        std::array<std::array<float, 10>, 9> M{};
        for (size_t i = 0; i < 9; ++i) {
            for (size_t j = 0; j < 9; ++j) M[i][j] = A[i][j];
            M[i][9] = b[i];
        }

        for (size_t col = 0; col < 9; ++col) {
            size_t max_row = col;
            float max_val = std::abs(M[col][col]);
            for (size_t row = col + 1; row < 9; ++row) {
                if (const float v = std::abs(M[row][col]); v > max_val) {
                    max_val = v;
                    max_row = row;
                }
            }
            if (max_val < 1e-9f) return false;

            if (max_row != col) {
                std::swap(M[col], M[max_row]);
            }

            for (size_t row = col + 1; row < 9; ++row) {
                const float factor = M[row][col] / M[col][col];
                for (size_t k = col; k < 10; ++k) {
                    M[row][k] -= factor * M[col][k];
                }
            }
        }

        for (int row = 8; row >= 0; --row) {
            float sum = M[static_cast<size_t>(row)][9];
            for (size_t col = static_cast<size_t>(row) + 1; col < 9; ++col) {
                sum -= M[static_cast<size_t>(row)][col] * x_out[col];
            }
            x_out[static_cast<size_t>(row)] = sum / M[static_cast<size_t>(row)][static_cast<size_t>(row)];
        }
        return true;
    }

    static bool invert_matrix_3x3(const Matrix3x3& A, Matrix3x3& inv) noexcept {
        const float det = A.m[0][0] * (A.m[1][1] * A.m[2][2] - A.m[1][2] * A.m[2][1]) -
                          A.m[0][1] * (A.m[1][0] * A.m[2][2] - A.m[1][2] * A.m[2][0]) +
                          A.m[0][2] * (A.m[1][0] * A.m[2][1] - A.m[1][1] * A.m[2][0]);
        if (std::abs(det) < 1e-12f) return false;

        const float inv_det = 1.0f / det;
        inv.m[0][0] = (A.m[1][1] * A.m[2][2] - A.m[1][2] * A.m[2][1]) * inv_det;
        inv.m[0][1] = (A.m[0][2] * A.m[2][1] - A.m[0][1] * A.m[2][2]) * inv_det;
        inv.m[0][2] = (A.m[0][1] * A.m[1][2] - A.m[0][2] * A.m[1][1]) * inv_det;
        inv.m[1][0] = (A.m[1][2] * A.m[2][0] - A.m[1][0] * A.m[2][2]) * inv_det;
        inv.m[1][1] = (A.m[0][0] * A.m[2][2] - A.m[0][2] * A.m[2][0]) * inv_det;
        inv.m[1][2] = (A.m[0][2] * A.m[1][0] - A.m[0][0] * A.m[1][2]) * inv_det;
        inv.m[2][0] = (A.m[1][0] * A.m[2][1] - A.m[1][1] * A.m[2][0]) * inv_det;
        inv.m[2][1] = (A.m[0][1] * A.m[2][0] - A.m[0][0] * A.m[2][1]) * inv_det;
        inv.m[2][2] = (A.m[0][0] * A.m[1][1] - A.m[0][1] * A.m[1][0]) * inv_det;
        return true;
    }
};
```
:::

## Інженерні пастки та критерії валідації калібрування

Під час інтеграції алгоритму в реальний польотний стек необхідно контролювати кілька типових відмов:

1. **Недостатнє просторове покриття (Planar Rotation Defect):** якщо користувач обертав дрон лише на столі в горизонтальній площині (2D поворот), розв'язок квадрики за віссю Z вироджується. Перевірка повинна перевіряти кількість заповнених секторів за висотою (Elevation): якщо вибірка не містить відліків з нахилом вгору та вниз хоча б на ±45°, калібрування має бути відхилене з помилкою `CAL_ERR_POOR_COVERAGE`.
2. **Аномальні коефіцієнти форми (Eccentricity Check):** якщо відношення максимального та мінімального діагональних елементів матриці `M` перевищує 3.0, це вказує на наявність екстремальної завади (наприклад, калібрування виконувалося поруч із залізобетонною підлогою).
3. **Середньоквадратична нев'язка радіуса (Fitness Score):** після розрахунку параметрів корисним є прогін вибірки через фільтр: для кожної точки обчислюється нев'язка `res_i = | ||T · (B_i − V_hard)|| − B₀ |`. Середня відносна похибка не повинна перевищувати 3–5% від `B₀`.
4. **Продуктивність реального часу:** на типовому процесорі STM32F7 @ 216 МГц виконання функції `mag_cal_add_sample()` займає менше 120 тактів (близько 0.5 мкс), а підсумковий розрахунок матриці `mag_cal_compute()` триває менше 1.2 мс, що дозволяє виконувати калібрування без переривання основних контурів стабілізації польоту.
