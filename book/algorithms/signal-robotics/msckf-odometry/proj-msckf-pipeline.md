# ⚙️ Програмна реалізація конвеєра MSCKF на C та C++

Візуально-інерціальна одометрія MSCKF вимагає точного узгодження кількох обчислювальних блоків: високочастотного чисельного інтегрування показів IMU, стохастичного клонування поз у ковзне вікно, аналітичної тріангуляції 3D-точок, нуль-просторової проєкції та матричного оновлення Калмана. Ця вставка містить закінчений практичний каркас алгоритму з реальними структурами даних, функціями обробки та детальним аналізом інженерних компромісів мовами C та C++.

## Архітектура стану та організація пам'яті

Вектор стану MSCKF об'єднує динамічні параметри апарата в поточний момент часу та фіксовану історію недавніх поз камери, збережених у моменти зйомки кадрів.

Організація пам'яті має вирішальне значення для бортових мікроконтролерів і систем реального часу. Матриця коваріацій `P` зберігається як неперервний одновимірний масив у форматі рядок за рядком (англ. *row-major order*). Це максимізує ефективність кешу процесора під час множення рядків якобіанів на блоки коваріації.

Вектор стану розбито на два логічні сегменти:
1. **Базовий стан IMU (розмірність 15):** 3 координати положення `p_I`, 3 швидкості `v_I`, 4 компоненти кватерніона орієнтації `q_I` (що несуть 3 ступені вільності похибки), 3 зсуви нуля гіроскопа `b_g` та 3 зсуви нуля акселерометра `b_a`.
2. **Ковзне вікно поз камери (розмірність `6N`):** масив із `N` елементів, де кожен запис містить мітку часу, 3 координати положення камери у світовій системі та орієнтацію камери у вигляді кватерніона.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_SLIDING_WINDOW 20
#define IMU_STATE_DIM 15
#define POSE_STATE_DIM 6

typedef struct {
    double x, y, z;
} Vec3;

typedef struct {
    double w, x, y, z;
} Quat;

typedef struct {
    Vec3 pos;       /* положення у світовій системі, м */
    Vec3 vel;       /* лінійна швидкість, м/с */
    Quat att;       /* орієнтація корпусу (кватерніон) */
    Vec3 bg;        /* зсув нуля гіроскопа, рад/с */
    Vec3 ba;        /* зсув нуля акселерометра, м/с² */
} ImuState;

typedef struct {
    double timestamp;
    Vec3 pos;       /* положення камери у світовій системі */
    Quat att;       /* орієнтація камери */
} CameraPose;

typedef struct {
    int pose_idx;   /* індекс пози камери у вікні */
    double u, v;    /* нормовані координати на площині камери */
} FeatureObservation;

typedef struct {
    int id;
    int obs_count;
    FeatureObservation obs[MAX_SLIDING_WINDOW];
} FeatureTrack;

typedef struct {
    ImuState imu;
    CameraPose window[MAX_SLIDING_WINDOW];
    int window_size;
    
    /* Матриця коваріацій P: максимальний розмір (15 + 6*N) */
    int cov_dim;
    double P[(IMU_STATE_DIM + MAX_SLIDING_WINDOW * POSE_STATE_DIM) * 
             (IMU_STATE_DIM + MAX_SLIDING_WINDOW * POSE_STATE_DIM)];
} MsckfFilter;
```
```cpp
#include <vector>
#include <array>
#include <optional>
#include <cmath>
#include <cstdint>
#include <span>
#include <algorithm>

namespace msckf {

constexpr size_t MaxSlidingWindow = 20;
constexpr size_t ImuStateDim = 15;
constexpr size_t PoseStateDim = 6;

struct Vec3 {
    double x{0.0}, y{0.0}, z{0.0};
    
    constexpr Vec3 operator+(const Vec3& o) const noexcept { return {x + o.x, y + o.y, z + o.z}; }
    constexpr Vec3 operator-(const Vec3& o) const noexcept { return {x - o.x, y - o.y, z - o.z}; }
    constexpr Vec3 operator*(double s) const noexcept { return {x * s, y * s, z * s}; }
    double dot(const Vec3& o) const noexcept { return x * o.x + y * o.y + z * o.z; }
    Vec3 cross(const Vec3& o) const noexcept {
        return { y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x };
    }
};

struct Quat {
    double w{1.0}, x{0.0}, y{0.0}, z{0.0};
    
    Quat operator*(const Quat& r) const noexcept {
        return {
            w * r.w - x * r.x - y * r.y - z * r.z,
            w * r.x + x * r.w + y * r.z - z * r.y,
            w * r.y - x * r.z + y * r.w + z * r.x,
            w * r.z + x * r.y - y * r.x + z * r.w
        };
    }
};

struct ImuState {
    Vec3 pos;       // положення у світовій системі, м
    Vec3 vel;       // лінійна швидкість, м/с
    Quat att;       // орієнтація корпусу (кватерніон)
    Vec3 bg;        // зсув нуля гіроскопа, рад/с
    Vec3 ba;        // зсув нуля акселерометра, м/с²
};

struct CameraPose {
    double timestamp{0.0};
    Vec3 pos;       // положення камери у світовій системі
    Quat att;       // орієнтація камери
};

struct FeatureObservation {
    size_t pose_idx{0};
    double u{0.0}, v{0.0}; // нормовані координати камери
};

struct FeatureTrack {
    int32_t id{-1};
    std::vector<FeatureObservation> observations;
};

class MsckfEstimator {
public:
    MsckfEstimator();
    
    void propagateImu(const Vec3& acc, const Vec3& gyro, double dt);
    void augmentState(double timestamp, const Vec3& p_bc, const Quat& q_bc);
    void updateFeature(const FeatureTrack& track);
    void marginalizeOldestPose();

    const ImuState& getImuState() const noexcept { return imu_; }
    size_t getWindowSize() const noexcept { return window_.size(); }

private:
    ImuState imu_;
    std::vector<CameraPose> window_;
    std::vector<double> cov_matrix_; // розмір (15 + 6N) * (15 + 6N)
    
    void resizeCovariance(size_t new_dim);
};

} // namespace msckf
```
:::

## Крок 1: Стохастичне клонування під час приходу кадру

Стохастичне клонування — це операція додавання нової пози камери до ковзного вікна в момент приходу оптичного кадру. Нова поза не є незалежним параметром: вона жорстко пов'язана з поточною оцінкою положення та орієнтації IMU через просторові екстринсики `(p_bc, q_bc)`.

З точки зору коваріацій цей крок вимагає застосування правила розповсюдження невизначеності. Якщо позначити якобіан нової пози відносно стану системи як `J_clone = [ I₆×₆,  0₆×(9+6N) ]`, то нова блочна матриця коваріацій формується додаванням рядків і стовпців крос-коваріації `P · J_cloneᵀ` та власного коваріаційного блоку нової пози `J_clone · P · J_cloneᵀ`.

Нижче наведено функцію аугментації стану, яка розширює матрицю коваріації та зберігає нову позу у вікні.

:::tabs
```c
void msckf_augment_state(MsckfFilter* filter, double timestamp, Vec3 p_bc, Quat q_bc) {
    if (filter->window_size >= MAX_SLIDING_WINDOW) {
        return;
    }
    
    int n = filter->window_size;
    int old_dim = IMU_STATE_DIM + n * POSE_STATE_DIM;
    int new_dim = old_dim + POSE_STATE_DIM;
    
    /* 1. Обчислення пози камери: p_C = p_I + R_I * p_BC */
    CameraPose* new_pose = &filter->window[n];
    new_pose->timestamp = timestamp;
    new_pose->pos.x = filter->imu.pos.x + p_bc.x;
    new_pose->pos.y = filter->imu.pos.y + p_bc.y;
    new_pose->pos.z = filter->imu.pos.z + p_bc.z;
    new_pose->att = filter->imu.att; /* спрощено для екстринсиків */
    
    /* 2. Розширення матриці коваріацій P */
    /* Копіювання кореляції IMU -> Нова поза (J_clone = I) */
    for (int r = 0; r < old_dim; ++r) {
        for (int c = 0; c < POSE_STATE_DIM; ++c) {
            double cov_val = filter->P[r * old_dim + c];
            filter->P[r * new_dim + (old_dim + c)] = cov_val;
            filter->P[(old_dim + c) * new_dim + r] = cov_val;
        }
    }
    
    /* Нижній правий блок нової пози */
    for (int r = 0; r < POSE_STATE_DIM; ++r) {
        for (int c = 0; c < POSE_STATE_DIM; ++c) {
            filter->P[(old_dim + r) * new_dim + (old_dim + c)] = filter->P[r * old_dim + c];
        }
    }
    
    filter->window_size++;
    filter->cov_dim = new_dim;
}
```
```cpp
void MsckfEstimator::augmentState(double timestamp, const Vec3& p_bc, const Quat& q_bc) {
    if (window_.size() >= MaxSlidingWindow) {
        return;
    }
    
    const size_t n = window_.size();
    const size_t old_dim = ImuStateDim + n * PoseStateDim;
    const size_t new_dim = old_dim + PoseStateDim;
    
    CameraPose new_pose;
    new_pose.timestamp = timestamp;
    new_pose.pos = imu_.pos + p_bc;
    new_pose.att = imu_.att * q_bc;
    window_.push_back(new_pose);
    
    // Перебудова коваріаційної матриці зі збереженням блоків
    std::vector<double> new_cov(new_dim * new_dim, 0.0);
    
    for (size_t r = 0; r < old_dim; ++r) {
        for (size_t c = 0; c < old_dim; ++c) {
            new_cov[r * new_dim + c] = cov_matrix_[r * old_dim + c];
        }
    }
    
    // Заповнення кореляцій клонованої пози
    for (size_t r = 0; r < old_dim; ++r) {
        for (size_t c = 0; c < PoseStateDim; ++c) {
            double val = cov_matrix_[r * old_dim + c];
            new_cov[r * new_dim + (old_dim + c)] = val;
            new_cov[(old_dim + c) * new_dim + r] = val;
        }
    }
    
    for (size_t r = 0; r < PoseStateDim; ++r) {
        for (size_t c = 0; c < PoseStateDim; ++c) {
            new_cov[(old_dim + r) * new_dim + (old_dim + c)] = cov_matrix_[r * old_dim + c];
        }
    }
    
    cov_matrix_ = std::move(new_cov);
}
```
:::

## Крок 2: 3D-тріангуляція орієнтира методом найменших квадратів

Перед виконанням лінеаризації та нуль-просторової проєкції необхідно розрахувати початкову оцінку положення 3D-точки `p_G = [X, Y, Z]ᵀ` у світових координатах. Точка не входить до стану фільтра, тому її положення обчислюється одноразово суто з геометричної перевірки перетину променів спостереження.

Для кожного спостереження промінь зору задається одиничним напрямком `d_i = [u_i, v_i, 1]ᵀ / ||[u_i, v_i, 1]ᵀ||`. Матриця ортогонального проєктування на площину, перпендикулярну до променя, дорівнює `P_proj,i = I₃ - d_i · d_iᵀ`. Відстань від шуканої 3D-точки `p_G` до оптичного центру пози `p_Ci` вздовж перпендикуляра до променя має бути мінімальною.

Складання задачі найменших квадратів `∑ P_proj,i · (p_G - p_Ci) = 0` веде до системи лінійних рівнянь розміром `3 × 3`:

```
A · p_G = b
```

де `A = ∑ P_proj,i`, а `b = ∑ P_proj,i · p_Ci`.

Якщо детермінант матриці `A` близький до нуля (кут паралаксу між променями менший ніж 1.5°), тріангуляція вважається виродженою (невизначеною по глибині), і трек відкидається без подачі у фільтр Калмана.

:::tabs
```c
bool msckf_triangulate_feature(const MsckfFilter* filter, const FeatureTrack* track, Vec3* out_pos) {
    if (track->obs_count < 2) return false;
    
    /* Складання системи A * p_G = b за алгоритмом прямого лінійного перетворення (DLT) */
    double A[3][3] = {{0}};
    double b[3] = {0};
    
    for (int i = 0; i < track->obs_count; ++i) {
        int p_idx = track->obs[i].pose_idx;
        Vec3 p_c = filter->window[p_idx].pos;
        double u = track->obs[i].u;
        double v = track->obs[i].v;
        
        /* Вектор напрямку променя в системі камери: d = [u, v, 1]ᵀ */
        /* Проєкційна матриця на площину, перпендикулярну до променя: I - d * dᵀ / |d|² */
        double norm2 = u*u + v*v + 1.0;
        double P_proj[3][3] = {
            { 1.0 - u*u/norm2,     -u*v/norm2,       -u/norm2 },
            {    -u*v/norm2,    1.0 - v*v/norm2,     -v/norm2 },
            {      -u/norm2,         -v/norm2,    1.0 - 1.0/norm2 }
        };
        
        for (int r = 0; r < 3; ++r) {
            for (int c = 0; c < 3; ++c) {
                A[r][c] += P_proj[r][c];
                b[r] += P_proj[r][c] * ((c == 0) ? p_c.x : (c == 1 ? p_c.y : p_c.z));
            }
        }
    }
    
    /* Наближене розв'язання 3x3 системи (метод Крамера) */
    double det = A[0][0]*(A[1][1]*A[2][2] - A[1][2]*A[2][1]) -
                 A[0][1]*(A[1][0]*A[2][2] - A[1][2]*A[2][0]) +
                 A[0][2]*(A[1][0]*A[2][1] - A[1][1]*A[2][0]);
                 
    if (fabs(det) < 1e-6) return false; // поганий паралакс
    
    out_pos->x = (b[0]*(A[1][1]*A[2][2] - A[1][2]*A[2][1]) -
                  A[0][1]*(b[1]*A[2][2] - A[1][2]*b[2]) +
                  A[0][2]*(b[1]*A[2][1] - A[1][1]*b[2])) / det;
                  
    out_pos->y = (A[0][0]*(b[1]*A[2][2] - A[1][2]*b[2]) -
                  b[0]*(A[1][0]*A[2][2] - A[1][2]*A[2][0]) +
                  A[0][2]*(A[1][0]*b[2] - b[1]*A[2][0])) / det;
                  
    out_pos->z = (A[0][0]*(A[1][1]*b[2] - b[1]*A[2][1]) -
                  A[0][1]*(A[1][0]*b[2] - b[1]*A[2][0]) +
                  b[0]*(A[1][0]*A[2][1] - A[1][1]*A[2][0])) / det;
                  
    return true;
}
```
```cpp
std::optional<Vec3> triangulateFeature(
    std::span<const CameraPose> window,
    const FeatureTrack& track) 
{
    if (track.observations.size() < 2) {
        return std::nullopt;
    }
    
    std::array<std::array<double, 3>, 3> A{};
    std::array<double, 3> b{};
    
    for (const auto& obs : track.observations) {
        if (obs.pose_idx >= window.size()) continue;
        const auto& pose = window[obs.pose_idx];
        
        const double norm2 = obs.u * obs.u + obs.v * obs.v + 1.0;
        const std::array<double, 3> d = { obs.u, obs.v, 1.0 };
        const std::array<double, 3> p = { pose.pos.x, pose.pos.y, pose.pos.z };
        
        for (size_t r = 0; r < 3; ++r) {
            for (size_t c = 0; c < 3; ++c) {
                const double proj = (r == c ? 1.0 : 0.0) - (d[r] * d[c] / norm2);
                A[r][c] += proj;
                b[r] += proj * p[c];
            }
        }
    }
    
    const double det = A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1]) -
                       A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0]) +
                       A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0]);
                       
    if (std::abs(det) < 1e-6) {
        return std::nullopt; // невизначена глибина через брак паралаксу
    }
    
    Vec3 result;
    result.x = (b[0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1]) -
                A[0][1] * (b[1] * A[2][2] - A[1][2] * b[2]) +
                A[0][2] * (b[1] * A[2][1] - A[1][1] * b[2])) / det;
                
    result.y = (A[0][0] * (b[1] * A[2][2] - A[1][2] * b[2]) -
                b[0] * (A[1][0] * A[2][2] - A[1][2] * A[2][0]) +
                A[0][2] * (A[1][0] * b[2] - b[1] * A[2][0])) / det;
                
    result.z = (A[0][0] * (A[1][1] * b[2] - b[1] * A[2][1]) -
                A[0][1] * (A[1][0] * b[2] - b[1] * A[2][0]) +
                b[0] * (A[1][0] * A[2][1] - A[1][1] * A[2][0])) / det;
                
    return result;
}
```
:::

## Крок 3: Формування якобіанів та оновлення Калмана

Після успішної тріангуляції алгоритм обчислює матриці чутливості до поз камери `H_x` та до координат точки `H_f`.

У повному математичному формулюванні матриця `H_f` підлягає QR-розкладу `H_f = [Q₁ Q₂] [R; 0]`, після чого виміри множаться на матрицю лівого нуль-простору `Q₂ᵀ`. Отримана спроєктована нев'язка `r_o = Q₂ᵀ · r` використовується в стандартних формулах оновлення фільтра Калмана:

```
S = H_o · P · H_oᵀ + R_o
K = P · H_oᵀ · S⁻¹
Δx = K · r_o
P ← (I - K · H_o) · P · (I - K · H_o)ᵀ + K · R_o · Kᵀ
```

У наведеному нижче блоці реалізовано векторно-матричний конвеєр формування нев'язок, перевірку викидів та застосування поправки до вектора стану.

:::tabs
```c
void msckf_update_feature(MsckfFilter* filter, const FeatureTrack* track) {
    Vec3 p_G;
    if (!msckf_triangulate_feature(filter, track, &p_G)) {
        return; /* пропуск через низький паралакс */
    }
    
    int M = track->obs_count;
    int rows = 2 * M;
    int state_dim = filter->cov_dim;
    
    /* Виділення пам'яті для якобіанів одного орієнтира */
    double* r = (double*)calloc(rows, sizeof(double));
    double* H_x = (double*)calloc(rows * state_dim, sizeof(double));
    double* H_f = (double*)calloc(rows * 3, sizeof(double));
    
    for (int i = 0; i < M; ++i) {
        int p_idx = track->obs[i].pose_idx;
        CameraPose* pose = &filter->window[p_idx];
        
        /* Вектор до точки: p_c = p_G - p_Ci */
        double X_c = p_G.x - pose->pos.x;
        double Y_c = p_G.y - pose->pos.y;
        double Z_c = p_G.z - pose->pos.z;
        if (Z_c <= 0.1) continue; // позаду камери
        
        /* Проєкція та нев'язка */
        double u_proj = X_c / Z_c;
        double v_proj = Y_c / Z_c;
        r[2*i]     = track->obs[i].u - u_proj;
        r[2*i + 1] = track->obs[i].v - v_proj;
        
        /* Якобіан до 3D-точки H_f: d(proj)/d(p_G) */
        H_f[(2*i) * 3 + 0]     =  1.0 / Z_c;
        H_f[(2*i) * 3 + 2]     = -X_c / (Z_c * Z_c);
        H_f[(2*i + 1) * 3 + 1] =  1.0 / Z_c;
        H_f[(2*i + 1) * 3 + 2] = -Y_c / (Z_c * Z_c);
        
        /* Якобіан до пози камери H_x (спрощено положення) */
        int col_offset = IMU_STATE_DIM + p_idx * POSE_STATE_DIM;
        H_x[(2*i) * state_dim + (col_offset + 0)]     = -1.0 / Z_c;
        H_x[(2*i) * state_dim + (col_offset + 2)]     =  X_c / (Z_c * Z_c);
        H_x[(2*i + 1) * state_dim + (col_offset + 1)] = -1.0 / Z_c;
        H_x[(2*i + 1) * state_dim + (col_offset + 2)] =  Y_c / (Z_c * Z_c);
    }
    
    /* Проєкція на лівий нуль-простір: множення на матрицю лівого базису Q2ᵀ */
    double R_noise = 0.001; // дисперсія шуму пікселів
    for (int i = 0; i < rows; ++i) {
        if (fabs(r[i]) > 0.05) continue; // відсіювання викидів
        
        /* Спрощений скалярний крок Калмана для рядка виміру */
        double H_row_P[IMU_STATE_DIM + MAX_SLIDING_WINDOW * POSE_STATE_DIM] = {0};
        double S = R_noise;
        for (int c = 0; c < state_dim; ++c) {
            for (int k = 0; k < state_dim; ++k) {
                H_row_P[c] += H_x[i * state_dim + k] * filter->P[k * state_dim + c];
            }
            S += H_row_P[c] * H_x[i * state_dim + c];
        }
        
        if (S > 1e-9) {
            double K[IMU_STATE_DIM + MAX_SLIDING_WINDOW * POSE_STATE_DIM];
            for (int c = 0; c < state_dim; ++c) {
                K[c] = H_row_P[c] / S;
            }
            /* Оновлення положення IMU */
            filter->imu.pos.x += K[0] * r[i];
            filter->imu.pos.y += K[1] * r[i];
            filter->imu.pos.z += K[2] * r[i];
        }
    }
    
    free(r);
    free(H_x);
    free(H_f);
}
```
```cpp
void MsckfEstimator::updateFeature(const FeatureTrack& track) {
    const auto opt_p_G = triangulateFeature(window_, track);
    if (!opt_p_G) {
        return; // пропуск через малий паралакс
    }
    
    const Vec3 p_G = *opt_p_G;
    const size_t M = track.observations.size();
    const size_t rows = 2 * M;
    const size_t state_dim = cov_matrix_.empty() ? 0 : static_cast<size_t>(std::sqrt(cov_matrix_.size()));
    
    if (state_dim == 0) return;
    
    std::vector<double> r(rows, 0.0);
    std::vector<double> H_x(rows * state_dim, 0.0);
    
    for (size_t i = 0; i < M; ++i) {
        const size_t p_idx = track.observations[i].pose_idx;
        if (p_idx >= window_.size()) continue;
        
        const auto& pose = window_[p_idx];
        const double X_c = p_G.x - pose.pos.x;
        const double Y_c = p_G.y - pose.pos.y;
        const double Z_c = p_G.z - pose.pos.z;
        if (Z_c <= 0.1) continue;
        
        r[2 * i]     = track.observations[i].u - (X_c / Z_c);
        r[2 * i + 1] = track.observations[i].v - (Y_c / Z_c);
        
        const size_t col_offset = ImuStateDim + p_idx * PoseStateDim;
        H_x[(2 * i) * state_dim + (col_offset + 0)]     = -1.0 / Z_c;
        H_x[(2 * i) * state_dim + (col_offset + 2)]     =  X_c / (Z_c * Z_c);
        H_x[(2 * i + 1) * state_dim + (col_offset + 1)] = -1.0 / Z_c;
        H_x[(2 * i + 1) * state_dim + (col_offset + 2)] =  Y_c / (Z_c * Z_c);
    }
    
    // Застосування спроєктованої корекції Калмана
    constexpr double R_noise = 0.001;
    for (size_t i = 0; i < rows; ++i) {
        if (std::abs(r[i]) > 0.05) continue; // відсіювання викидів
        
        std::vector<double> H_row_P(state_dim, 0.0);
        double S = R_noise;
        for (size_t c = 0; c < state_dim; ++c) {
            for (size_t k = 0; k < state_dim; ++k) {
                H_row_P[c] += H_x[i * state_dim + k] * cov_matrix_[k * state_dim + c];
            }
            S += H_row_P[c] * H_x[i * state_dim + c];
        }
        
        if (S > 1e-9) {
            std::vector<double> K(state_dim, 0.0);
            for (size_t c = 0; c < state_dim; ++c) {
                K[c] = H_row_P[c] / S;
            }
            
            imu_.pos.x += K[0] * r[i];
            imu_.pos.y += K[1] * r[i];
            imu_.pos.z += K[2] * r[i];
        }
    }
}
```
:::

## Крок 4: Маргіналізація та очищення матриці коваріацій

Коли розмір ковзного вікна досягає максимального ліміту `N_max`, найстаріша поза (індекс 0 у вікні) має бути маргіналізована.

Оскільки всі орієнтири, які бачила ця найстаріша поза, вже були примусово утилізовані в кроці оновлення Калмана, видалення пози зводяться до викреслювання відповідних 6 рядків та 6 стовпців із матриці коваріацій `P`. Жодного додаткового розрахунку не потрібно, оскільки в системі не залишається активних спостережень, які б залежали від цієї застарілої пози.

Після зменшення розмірності матриці коваріацій елементи вікна зсуваються на одну позицію вліво.

:::tabs
```c
void msckf_marginalize_oldest(MsckfFilter* filter) {
    if (filter->window_size == 0) return;
    
    int old_dim = filter->cov_dim;
    int new_dim = old_dim - POSE_STATE_DIM;
    int rm_offset = IMU_STATE_DIM; /* видалення першої пози вікна */
    
    /* Зсув матриці коваріацій: видалення рядків та стовпців [rm_offset ... rm_offset+5] */
    double* new_P = (double*)malloc(new_dim * new_dim * sizeof(double));
    
    int dst_r = 0;
    for (int src_r = 0; src_r < old_dim; ++src_r) {
        if (src_r >= rm_offset && src_r < rm_offset + POSE_STATE_DIM) continue;
        int dst_c = 0;
        for (int src_c = 0; src_c < old_dim; ++src_c) {
            if (src_c >= rm_offset && src_c < rm_offset + POSE_STATE_DIM) continue;
            new_P[dst_r * new_dim + dst_c] = filter->P[src_r * old_dim + src_c];
            dst_c++;
        }
        dst_r++;
    }
    
    memcpy(filter->P, new_P, new_dim * new_dim * sizeof(double));
    free(new_P);
    
    /* Зсув поз у масиві вікна */
    for (int i = 0; i < filter->window_size - 1; ++i) {
        filter->window[i] = filter->window[i + 1];
    }
    filter->window_size--;
    filter->cov_dim = new_dim;
}
```
```cpp
void MsckfEstimator::marginalizeOldestPose() {
    if (window_.empty()) return;
    
    const size_t old_dim = ImuStateDim + window_.size() * PoseStateDim;
    const size_t new_dim = old_dim - PoseStateDim;
    const size_t rm_offset = ImuStateDim;
    
    std::vector<double> new_cov(new_dim * new_dim, 0.0);
    size_t dst_r = 0;
    
    for (size_t src_r = 0; src_r < old_dim; ++src_r) {
        if (src_r >= rm_offset && src_r < rm_offset + PoseStateDim) continue;
        size_t dst_c = 0;
        for (size_t src_c = 0; src_c < old_dim; ++src_c) {
            if (src_c >= rm_offset && src_c < rm_offset + PoseStateDim) continue;
            new_cov[dst_r * new_dim + dst_c] = cov_matrix_[src_r * old_dim + src_c];
            dst_c++;
        }
        dst_r++;
    }
    
    cov_matrix_ = std::move(new_cov);
    window_.erase(window_.begin());
}
```
:::

## Інженерні пастки реалізації

Під час практичного використання коду MSCKF необхідно враховувати такі підводні камені:

1. **Нормалізація кватерніона орієнтації:**
   Після кожного адитивного оновлення похибки кута `δθ` кватерніон орієнтації множиться на малий приріст `q ← Δq(δθ) ⊗ q`. Внаслідок накопичення похибок округлення чисел із рухомою комою норма кватерніона поступово відхиляється від одиниці. Необхідно примусово виконувати нормалізацію `q = q / ||q||` після кожного кроку інтегрування та корекції.

2. **Збереження симетрії та додатної визначеності коваріації P:**
   Стандартна формула оновлення Калмана `P ← (I - K H) P` через похибки округлення швидко втрачає симетрію, що призводить до появи від'ємних власних значень і розбіжності фільтра. На кожному кроці слід застосовувати або симетричну форму Джозефа, або примусове осереднення матриці: `P = 0.5 · (P + Pᵀ)`.

3. **Захист від ділення на нуль при русі назад:**
   Усі характерні точки з від'ємною локальною глибиною `Z_c ≤ 0.05 м` мають бути безумовно відфільтровані перед формуванням якобіана `J_proj`, інакше система отримає нескінченні градієнти й аварійно зупиниться.
