# ⚙️ Відновлення карти глибини та генерація хмари точок

Повний конвеєр обробки структурованого світла приймає сирі кадри синусоїдальних смуг або спекл-патернів, усуває фонову засвітку, розгортає фазу рельєфу та виконує тріангуляцію для кожного валідного пікселя. На виході формується карта глибини та щільна тривимірна хмара точок у форматі PLY.

### Архітектура обчислювального конвеєра

Процес перетворення набору оптичних знімків на метричні тривимірні координати розбивається на чотири послідовні алгоритмічні стадії:

1. **Фазова демодуляція (Phase Demodulation)**: Приймаються чотири кадри високої просторової частоти `I_0 ... I_3` та чотири кадри низької опорної частоти. Для кожного пікселя обчислюється загорнута фаза `φ(x, y)` та амплітуда модуляції `B(x, y)`.
2. **Часове розгортання фази (Temporal Phase Unwrapping)**: Зіставлення грубої одноперіодної фази та високочастотної багатоперіодної фази визначає цілий номер періоду смуги `k(x, y)` та формує неперервну шкалу абсолютної фази `Φ(x, y)`.
3. **Фільтрація маски якості (Quality Masking)**: Пікселі з амплітудою модуляції, меншою за поріг `B_min` (зони тіней проектора, оклюзій камери або глибокого поглинання світла), відкидаються, що запобігає формуванню фальшивих шумів у хмарі точок.
4. **Тріангуляція та 3D-проекція (Triangulation)**: Абсолютна фаза перераховується у субпіксельну координату стовпця проектора `u_p`. За відомою базовою лінією `B` та фокусною відстанню `f_c` знаходиться оптичний паралакс `d = x - u_p` і глибина `Z = (B · f_c) / d`, після чого точка проектується в декартовий базис камери `(X, Y, Z)`.

### Калібрувальна модель та епіполярне вирівнювання

Геометричний розрахунок спирається на модель камери-обскури (*pinhole camera model*). Внутрішні параметри камери задаються матрицею `K_c`, що містить фокусні відстані `f_x, f_y` у пікселях та координати головної точки `(c_x, c_y)`. Радіальні спотворення об'єктива усуваються за поліноміальною моделлю Брауна–Конраді:

```
x_corrected = x_distorted · (1 + k_1·r² + k_2·r⁴) + 2·p_1·x·y + p_2·(r² + 2·x²)
```

Після геометричної ректифікації епіполярні лінії камери та проектора стають паралельними горизонтальним рядкам пікселів. Це дозволяє уникнути двовимірного пошуку: координата стовпця проектора `u_proj` однозначно визначається поточною абсолютною фазою `Φ(x, y)`, а паралакс обчислюється простим відніманням `d = x - u_proj`.

Нижче наведено модульну реалізацію конвеєра мовами C та C++20.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define PI 3.14159265358979323846f

typedef struct {
    float x, y, z;
    float intensity;
} Point3D;

typedef struct {
    float baseline_mm;    /* Базова лінія B між камерою та проектором */
    float focal_length_px;/* Фокусна відстань камери f_c в пікселях */
    float cx, cy;         /* Головна точка оптичної осі камери */
    int   proj_width_px;  /* Роздільна здатність проектора по горизонталі */
    int   fringe_periods; /* Кількість періодів високочастотної смуги (наприклад, 16) */
    float min_modulation; /* Поріг амплітуди B для відсікання тіней */
    float min_z_mm;       /* Мінімальна допустима дальність */
    float max_z_mm;       /* Максимальна допустима дальність */
} CalibrationParams;

/* Обчислення загорнутої фази та амплітуди модуляції з 4 кадрів */
void compute_4step_phase(const float* I0, const float* I1, 
                         const float* I2, const float* I3,
                         float* phase_out, float* mod_out,
                         int width, int height) {
    int total_pixels = width * height;
    for (int i = 0; i < total_pixels; ++i) {
        float num = I3[i] - I1[i];
        float den = I0[i] - I2[i];
        
        phase_out[i] = atan2f(num, den);
        mod_out[i]   = 0.5f * sqrtf(den * den + num * num);
    }
}

/* Двочастотне часове розгортання фази */
void temporal_unwrap(const float* coarse_phase, const float* fine_phase,
                     float* abs_phase_out, int width, int height, int n_periods) {
    int total_pixels = width * height;
    for (int i = 0; i < total_pixels; ++i) {
        /* Нормалізація грубої фази (1 період на весь кадр) до діапазону [0, 2π) */
        float phi1 = coarse_phase[i];
        if (phi1 < 0.0f) phi1 += 2.0f * PI;

        /* Нормалізація точної фази */
        float phi2 = fine_phase[i];
        if (phi2 < 0.0f) phi2 += 2.0f * PI;

        /* Визначення порядку періоду смуги k */
        float k_est = (n_periods * phi1 - phi2) / (2.0f * PI);
        int k = (int)roundf(k_est);
        if (k < 0) k = 0;
        if (k >= n_periods) k = n_periods - 1;

        /* Відновлення абсолютної неперервної фази */
        abs_phase_out[i] = phi2 + 2.0f * PI * (float)k;
    }
}

/* Тріангуляція фази у тривимірну хмару точок */
int reconstruct_point_cloud(const float* abs_phase, const float* modulation,
                            Point3D* cloud_out, int width, int height,
                            const CalibrationParams* calib) {
    int valid_points = 0;
    float max_abs_phase = 2.0f * PI * (float)calib->fringe_periods;

    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            int idx = y * width + x;

            /* Фільтрація тіней та перепадів яскравості за модуляцією */
            if (modulation[idx] < calib->min_modulation) {
                continue;
            }

            /* Відповідна неперервна координата на площині проектора */
            float u_proj = (abs_phase[idx] / max_abs_phase) * (float)calib->proj_width_px;

            /* Паралакс (диспаратність) вздовж ректифікованої лінії */
            float disparity = (float)x - u_proj;
            if (disparity <= 0.001f) {
                continue; /* Точка за нескінченністю або некоректна */
            }

            /* Гіперболічна тріангуляція Z = B · f / d */
            float z = (calib->baseline_mm * calib->focal_length_px) / disparity;
            if (z < calib->min_z_mm || z > calib->max_z_mm) {
                continue;
            }

            /* Зворотна проекція в декартові координати камери (X, Y) */
            float x_mm = ((float)x - calib->cx) * z / calib->focal_length_px;
            float y_mm = ((float)y - calib->cy) * z / calib->focal_length_px;

            cloud_out[valid_points].x = x_mm;
            cloud_out[valid_points].y = y_mm;
            cloud_out[valid_points].z = z;
            cloud_out[valid_points].intensity = modulation[idx];
            valid_points++;
        }
    }
    return valid_points;
}

/* Збереження хмари точок у форматі ASCII PLY */
bool export_ply(const char* filepath, const Point3D* cloud, int count) {
    FILE* fp = fopen(filepath, "w");
    if (!fp) return false;

    fprintf(fp, "ply\n");
    fprintf(fp, "format ascii 1.0\n");
    fprintf(fp, "element vertex %d\n", count);
    fprintf(fp, "property float x\n");
    fprintf(fp, "property float y\n");
    fprintf(fp, "property float z\n");
    fprintf(fp, "property float intensity\n");
    fprintf(fp, "end_header\n");

    for (int i = 0; i < count; ++i) {
        fprintf(fp, "%.3f %.3f %.3f %.1f\n", 
                cloud[i].x, cloud[i].y, cloud[i].z, cloud[i].intensity);
    }

    fclose(fp);
    return true;
}
```
```cpp
#include <cmath>
#include <numbers>
#include <vector>
#include <fstream>
#include <string_view>
#include <optional>
#include <span>
#include <algorithm>

struct Point3D {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
    float intensity{0.0f};
};

struct CalibrationParams {
    float baseline_mm{120.0f};       // Базова лінія B
    float focal_length_px{1050.0f};   // Фокусна відстань камери f_c
    float cx{640.0f};                 // Головна точка x
    float cy{360.0f};                 // Головна точка y
    int   proj_width_px{1920};        // Горизонтальна роздільність проектора
    int   fringe_periods{16};         // Кількість періодів високої частоти
    float min_modulation{10.0f};      // Поріг надійності модуляції
    float min_z_mm{200.0f};           // Близька межа вимірювання
    float max_z_mm{2500.0f};          // Далека межа вимірювання
};

class StructuredLightReconstructor {
public:
    explicit StructuredLightReconstructor(CalibrationParams calib) 
        : calib_(calib) {}

    // Обчислення загорнутої фази та амплітуди модуляції
    static void compute4StepPhase(std::span<const float> i0, std::span<const float> i1,
                                 std::span<const float> i2, std::span<const float> i3,
                                 std::span<float> phase_out, std::span<float> mod_out) {
        const size_t n = phase_out.size();
        for (size_t i = 0; i < n; ++i) {
            const float num = i3[i] - i1[i];
            const float den = i0[i] - i2[i];
            phase_out[i] = std::atan2(num, den);
            mod_out[i]   = 0.5f * std::sqrt(den * den + num * num);
        }
    }

    // Двочастотне розгортання фази
    static void temporalUnwrap(std::span<const float> coarse_phase,
                               std::span<const float> fine_phase,
                               std::span<float> abs_phase_out,
                               int n_periods) {
        constexpr float two_pi = 2.0f * std::numbers::pi_v<float>;
        const size_t n = abs_phase_out.size();

        for (size_t i = 0; i < n; ++i) {
            float phi1 = coarse_phase[i];
            if (phi1 < 0.0f) phi1 += two_pi;

            float phi2 = fine_phase[i];
            if (phi2 < 0.0f) phi2 += two_pi;

            const float k_est = (n_periods * phi1 - phi2) / two_pi;
            const int k = std::clamp(static_cast<int>(std::round(k_est)), 0, n_periods - 1);

            abs_phase_out[i] = phi2 + two_pi * static_cast<float>(k);
        }
    }

    // Тріангуляція у хмару точок
    [[nodiscard]] std::vector<Point3D> reconstruct(std::span<const float> abs_phase,
                                                   std::span<const float> modulation,
                                                   int width, int height) const {
        std::vector<Point3D> cloud;
        cloud.reserve(width * height / 4);

        const float max_abs_phase = 2.0f * std::numbers::pi_v<float> * static_cast<float>(calib_.fringe_periods);

        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                const size_t idx = static_cast<size_t>(y * width + x);

                if (modulation[idx] < calib_.min_modulation) {
                    continue; // Відсікання тіней
                }

                const float u_proj = (abs_phase[idx] / max_abs_phase) * static_cast<float>(calib_.proj_width_px);
                const float disparity = static_cast<float>(x) - u_proj;

                if (disparity <= 0.001f) {
                    continue;
                }

                const float z = (calib_.baseline_mm * calib_.focal_length_px) / disparity;
                if (z < calib_.min_z_mm || z > calib_.max_z_mm) {
                    continue;
                }

                const float x_mm = (static_cast<float>(x) - calib_.cx) * z / calib_.focal_length_px;
                const float y_mm = (static_cast<float>(y) - calib_.cy) * z / calib_.focal_length_px;

                cloud.push_back({x_mm, y_mm, z, modulation[idx]});
            }
        }
        return cloud;
    }

    // Експорт у формат PLY
    static bool exportPly(std::string_view filepath, std::span<const Point3D> cloud) {
        std::ofstream ofs(filepath.data());
        if (!ofs.is_open()) return false;

        ofs << "ply\n"
            << "format ascii 1.0\n"
            << "element vertex " << cloud.size() << "\n"
            << "property float x\n"
            << "property float y\n"
            << "property float z\n"
            << "property float intensity\n"
            << "end_header\n";

        for (const auto& pt : cloud) {
            ofs << pt.x << ' ' << pt.y << ' ' << pt.z << ' ' << pt.intensity << '\n';
        }
        return true;
    }

private:
    CalibrationParams calib_;
};
```
:::

### Пастки та критичні точки алгоритму

1. **Нормалізація фази перед відніманням**: Функція `atan2f` повертає значення в діапазоні `[-π, +π)`. Якщо значення від'ємне, до нього необхідно додати `2π` для приведення до `[0, 2π)`, інакше формула оцінки порядку періоду `k_est` дасть хибний зсув на `±1` на межі переходу знака.
2. **Фільтрація оклюзій за амплітудою модуляції**: Якщо піксель лежить у тіні або на поверхні з нульовим коефіцієнтом відбиття, фаза перетворюється на чистий шум. Перевірка `modulation[i] < calib.min_modulation` усуває до 99% хибних викидів хмари точок без необхідності складних просторових фільтрів.
3. **Ректифікація епіполярних ліній**: Наведена формула розрахунку `disparity = x - u_proj` справедлива лише для попередньо ректифікованої стереопари, де оптичні осі проектора й камери строго колінеарні, а рядки сенсорів збігаються. Для неректифікованих систем координату `u_proj` знаходять розв'язанням системи лінійних рівнянь перетину оптичного променя камери з площиною постійної фази проектора.
4. **Продуктивність та векторизація**: Усі внутрішні цикли розрахунку фази та модуляції не мають взаємних залежностей за даними між пікселями. На процесорах з підтримкою SIMD-інструкцій (AVX-512, ARM NEON) або при розпаралелюванні через OpenMP чи шейдери обчислення тривають менше ніж 2 мілісекунди для кадру роздільності Full HD (1920×1080), що дозволяє будувати системи 3D-контролю зі швидкістю понад 60 вимірів за секунду.
5. **Масштабування пам'яті**: Для уникнення частих виділень пам'яті у «гарячому» циклі обробки всі буфери фаз, амплітуд та результуючої хмари точок виділяються заздалегідь один раз під час ініціалізації драйвера сенсора.

### Апаратна синхронізація та заслінка камери

Для запобігання фазовим артефактам перемикання кадрів критично забезпечити строгу апаратну синхронізацію між проектором та камерою:

- **Строб-імпульс кадру (Frame Strobe)**: Проектор (наприклад, мікросхема керування DLP-контролера DLPC3479) генерує апаратний логічний імпульс тригера `TRIG_OUT` на початку відображення кожного синусоїдального патерну. Цей сигнал заводиться на вхід зовнішньої синхронізації `EXT_TRIG` CMOS-сенсора камери.
- **Глобальний проти рядкового затвора**: При використанні камери з рядковим затвором ([rolling shutter](root:hw-sensing/rolling-shutter)) різні рядки сенсора експонуються з часовим зсувом. Якщо проектор перемкне патерн під час зчитування кадру, верхня й нижня половини знімка отримають різні фази, що повністю зруйнує тригонометричний розрахунок. Тому в прецизійних FPP-системах застосовують виключно матриці з глобальним затвором (*Global Shutter*), де всі пікселі інтегрують світловий потік одночасно.

### Просторова постобробка хмари точок

Отримана після тріангуляції хмара точок зазвичай містить залишковий шум квантування на межах поверхонь. У промисловому конвеєрі до неї застосовують два типи фільтрації:

- **Статистичний фільтр викидів (Statistical Outlier Removal, SOR)**: Для кожної точки розраховується середня відстань `d_mean` до її `K` найближчих сусідів (типово `K = 30`). Точки, у яких середня відстань перевищує глобальне середнє більше ніж на `1.5 · σ` (де `σ` — стандартне відхилення), вважаються шумовими викидами й видаляються.
- **Двовимірний білатеральний фільтр глибини (Bilateral Filter)**: Згладжує плоскі ділянки поверхні вздовж карти глибини без розмиття різких ребер і переходів глибини. Фільтр зважує сусідні пікселі як за просторовою відстанню на матриці, так і за різницею значень глибини `|Z_1 - Z_2|`.

Завдяки цьому готові тривимірні дані набувають гладкості монолітного твердого тіла та передаються у CAD-системи для зворотного проектування (*Reverse Engineering*) або порівняння з еталонною 3D-моделлю.
