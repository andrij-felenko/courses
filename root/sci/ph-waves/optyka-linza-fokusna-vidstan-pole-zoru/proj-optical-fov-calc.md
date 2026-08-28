# ⚙️ Модуль оптичних геометричних розрахунків для машинно-візуальних та пірометричних сенсорів

Оптичні розрахунки в системах комп'ютерного зору, промислової інспекції, тепловізійної діагностики та безконтактної пірометрії вимагають строгого математичного зв'язку між параметрами світлочутливої матриці, фокусною відстанню об'єктива, робочою дистанцією та кутовими полями огляду. Помилка у виборі фокусної відстані призводить або до обрізання країв інспекційного поля (недостатній кут FOV), або до падіння просторової роздільної здатності (недостатній IFOV для детекції дрібних дефектів).

Нижче наведено програмний модуль оптичної геометрії мовами C та C++, що виконує повний комплекс інженерних розрахунків:
1. Розрахунок кутів огляду FOV (горизонтальний, вертикальний, діагональний) для фокусування на нескінченність та на скінченну робочу відстань (з урахуванням лінзового висування та масштабу зображення).
2. Прямий підбір необхідної фокусної відстані `f` за заданими геометричними розмірами зони контролю та відстанню до об'єкта.
3. Обчислення миттєвого кутового поля зору пікселя (IFOV) та просторової роздільної здатності на місцевості (GSD).
4. Розрахунок оптичного показника візування (Distance-to-Spot ratio `D:S`) та фактичного діаметра плями для пірометричних інфрачервоних сенсорів.

## Алгоритмічна реалізація: C та C++20

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define RAD_TO_DEG(rad) ((rad) * (180.0 / M_PI))
#define DEG_TO_RAD(deg) ((deg) * (M_PI / 180.0))

/* Структура специфікації світлочутливої матриці сенсора */
typedef struct {
    double width_mm;          /* Фізична ширина світлочутливої зони (мм) */
    double height_mm;         /* Фізична висота світлочутливої зони (мм) */
    double pixel_pitch_um;    /* Фізичний розмір пікселя (мікрометри) */
    int res_x;                /* Кількість пікселів по горизонталі */
    int res_y;                /* Кількість пікселів по вертикалі */
} SensorSpec;

/* Результати кутового поля зору FOV */
typedef struct {
    double hfov_deg;          /* Горизонтальний кут поля зору (градуси) */
    double vfov_deg;          /* Вертикальний кут поля зору (градуси) */
    double dfov_deg;          /* Діагональний кут поля зору (градуси) */
    double ifov_mrad;         /* Миттєве кутове поле зору одного пікселя (мілірадіани) */
    double diag_mm;           /* Діагональ світлочутливої матриці (мм) */
    double crop_factor;       /* Кроп-фактор відносно Full Frame (36x24 мм) */
} OpticalFovResult;

/* Результат розрахунку фокусної відстані для цільової сцени */
typedef struct {
    double required_f_mm;     /* Необхідна фокусна відстань об'єктива (мм) */
    double magnification;     /* Оптичне лінійне збільшення системи */
    double sensor_distance_mm;/* Фактична відстань від задньої головної площини до сенсора */
    bool is_macro;            /* Ознака макрорежиму (збільшення M > 0.1) */
} FocalLengthResult;

/* Результат пірометричного розрахунку плями візування */
typedef struct {
    double spot_diameter_mm;  /* Діаметр плями вимірювання на заданій відстані (мм) */
    double ds_ratio;          /* Оптичний показник візування D:S */
    double ifov_deg;          /* Повний кут конуса візування сенсора (градуси) */
} PyrometerSpotResult;

/* Статус виконання обчислень */
typedef enum {
    OPTIC_OK = 0,
    OPTIC_ERR_INVALID_PARAM = -1,
    OPTIC_ERR_ZERO_DIVISION = -2,
    OPTIC_ERR_DISTANCE_TOO_SHORT = -3
} OpticStatus;

/* Обчислення кутів FOV та роздільної здатності сенсора */
OpticStatus calc_sensor_fov(const SensorSpec* sensor, double focal_length_mm, 
                            double working_distance_mm, OpticalFovResult* out_res) {
    if (!sensor || !out_res || focal_length_mm <= 0.0 || sensor->width_mm <= 0.0 || sensor->height_mm <= 0.0) {
        return OPTIC_ERR_INVALID_PARAM;
    }

    double diag_mm = sqrt(sensor->width_mm * sensor->width_mm + sensor->height_mm * sensor->height_mm);
    const double full_frame_diag_mm = 43.266615; /* sqrt(36^2 + 24^2) */
    out_res->diag_mm = diag_mm;
    out_res->crop_factor = full_frame_diag_mm / diag_mm;

    /* Розрахунок ефективної відстані до площини зображення d_i */
    double d_i_mm = focal_length_mm;
    if (working_distance_mm > 0.0) {
        if (working_distance_mm <= focal_length_mm) {
            return OPTIC_ERR_DISTANCE_TOO_SHORT;
        }
        /* Формула тонкої лінзи: 1/d_i = 1/f - 1/d_o */
        d_i_mm = (focal_length_mm * working_distance_mm) / (working_distance_mm - focal_length_mm);
    }

    /* FOV = 2 * arctan(dimension / (2 * d_i)) */
    out_res->hfov_deg = RAD_TO_DEG(2.0 * atan(sensor->width_mm / (2.0 * d_i_mm)));
    out_res->vfov_deg = RAD_TO_DEG(2.0 * atan(sensor->height_mm / (2.0 * d_i_mm)));
    out_res->dfov_deg = RAD_TO_DEG(2.0 * atan(diag_mm / (2.0 * d_i_mm)));

    /* IFOV = pixel_pitch / focal_length (у мілірадіанах) */
    if (sensor->pixel_pitch_um > 0.0) {
        out_res->ifov_mrad = (sensor->pixel_pitch_um / 1000.0) / focal_length_mm * 1000.0;
    } else if (sensor->res_x > 0) {
        double pitch_calc_um = (sensor->width_mm / (double)sensor->res_x) * 1000.0;
        out_res->ifov_mrad = (pitch_calc_um / 1000.0) / focal_length_mm * 1000.0;
    } else {
        out_res->ifov_mrad = 0.0;
    }

    return OPTIC_OK;
}

/* Підбір фокусної відстані за шириною поля огляду W та дистанцією WD */
OpticStatus calc_focal_length_for_scene(double field_width_mm, double working_distance_mm,
                                        double sensor_width_mm, FocalLengthResult* out_res) {
    if (!out_res || field_width_mm <= 0.0 || working_distance_mm <= 0.0 || sensor_width_mm <= 0.0) {
        return OPTIC_ERR_INVALID_PARAM;
    }

    /* Оптичне лінійне збільшення M = w_sensor / W_field */
    double m = sensor_width_mm / field_width_mm;
    out_res->magnification = m;
    out_res->is_macro = (m >= 0.1);

    /* Необхідна фокусна відстань з урахуванням кінцевої дистанції: f = WD * M / (1 + M) */
    out_res->required_f_mm = working_distance_mm * m / (1.0 + m);
    out_res->sensor_distance_mm = out_res->required_f_mm * (1.0 + m);

    return OPTIC_OK;
}

/* Розрахунок пірометричної плями візування D:S */
OpticStatus calc_pyrometer_spot(double ds_ratio, double aperture_diam_mm,
                                double distance_mm, PyrometerSpotResult* out_res) {
    if (!out_res || ds_ratio <= 0.0 || distance_mm < 0.0) {
        return OPTIC_ERR_INVALID_PARAM;
    }

    out_res->ds_ratio = ds_ratio;
    /* Діаметр плями S = Aperture + Distance / (D:S) */
    out_res->spot_diameter_mm = aperture_diam_mm + (distance_mm / ds_ratio);
    
    /* Еквівалентний кут візування (градуси) */
    double half_angle_rad = atan(1.0 / (2.0 * ds_ratio));
    out_res->ifov_deg = RAD_TO_DEG(2.0 * half_angle_rad);

    return OPTIC_OK;
}
```
```cpp
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <format>
#include <optional>

namespace optical {

enum class ErrorCode {
    InvalidParameter,
    ZeroDivision,
    DistanceTooShort
};

struct SensorSpec {
    double width_mm{0.0};
    double height_mm{0.0};
    double pixel_pitch_um{0.0};
    int res_x{0};
    int res_y{0};

    [[nodiscard]] constexpr double diagonal_mm() const noexcept {
        return std::hypot(width_mm, height_mm);
    }

    [[nodiscard]] constexpr double aspect_ratio() const noexcept {
        return height_mm > 0.0 ? width_mm / height_mm : 0.0;
    }
};

struct FovResult {
    double hfov_deg{0.0};
    double vfov_deg{0.0};
    double dfov_deg{0.0};
    double ifov_mrad{0.0};
    double crop_factor{0.0};
    double image_distance_mm{0.0};
};

struct LensSelectionResult {
    double required_focal_length_mm{0.0};
    double magnification{0.0};
    double sensor_distance_mm{0.0};
    bool is_macro_regime{false};
};

struct PyrometerResult {
    double spot_diameter_mm{0.0};
    double ds_ratio{0.0};
    double cone_angle_deg{0.0};
};

class OpticsCalculator {
public:
    static constexpr double FULL_FRAME_DIAG_MM = 43.266615; // sqrt(36^2 + 24^2)

    [[nodiscard]] static constexpr double rad_to_deg(double rad) noexcept {
        return rad * (180.0 / std::numbers::pi);
    }

    [[nodiscard]] static constexpr double deg_to_rad(double deg) noexcept {
        return deg * (std::numbers::pi / 180.0);
    }

    [[nodiscard]] static std::expected<FovResult, ErrorCode> calculate_fov(
        const SensorSpec& sensor,
        double focal_length_mm,
        double working_distance_mm = 0.0) noexcept 
    {
        if (focal_length_mm <= 0.0 || sensor.width_mm <= 0.0 || sensor.height_mm <= 0.0) {
            return std::unexpected(ErrorCode::InvalidParameter);
        }

        double diag = sensor.diagonal_mm();
        double d_i = focal_length_mm;

        if (working_distance_mm > 0.0) {
            if (working_distance_mm <= focal_length_mm) {
                return std::unexpected(ErrorCode::DistanceTooShort);
            }
            d_i = (focal_length_mm * working_distance_mm) / (working_distance_mm - focal_length_mm);
        }

        FovResult res{};
        res.image_distance_mm = d_i;
        res.crop_factor = FULL_FRAME_DIAG_MM / diag;
        res.hfov_deg = rad_to_deg(2.0 * std::atan(sensor.width_mm / (2.0 * d_i)));
        res.vfov_deg = rad_to_deg(2.0 * std::atan(sensor.height_mm / (2.0 * d_i)));
        res.dfov_deg = rad_to_deg(2.0 * std::atan(diag / (2.0 * d_i)));

        double pitch_um = sensor.pixel_pitch_um;
        if (pitch_um <= 0.0 && sensor.res_x > 0) {
            pitch_um = (sensor.width_mm / static_cast<double>(sensor.res_x)) * 1000.0;
        }

        if (pitch_um > 0.0) {
            res.ifov_mrad = (pitch_um / 1000.0) / focal_length_mm * 1000.0;
        }

        return res;
    }

    [[nodiscard]] static std::expected<LensSelectionResult, ErrorCode> select_focal_length(
        double field_width_mm,
        double working_distance_mm,
        double sensor_width_mm) noexcept
    {
        if (field_width_mm <= 0.0 || working_distance_mm <= 0.0 || sensor_width_mm <= 0.0) {
            return std::unexpected(ErrorCode::InvalidParameter);
        }

        double m = sensor_width_mm / field_width_mm;
        LensSelectionResult res{};
        res.magnification = m;
        res.is_macro_regime = (m >= 0.1);
        res.required_focal_length_mm = (working_distance_mm * m) / (1.0 + m);
        res.sensor_distance_mm = res.required_focal_length_mm * (1.0 + m);

        return res;
    }

    [[nodiscard]] static std::expected<PyrometerResult, ErrorCode> calculate_pyrometer_spot(
        double ds_ratio,
        double aperture_diam_mm,
        double distance_mm) noexcept
    {
        if (ds_ratio <= 0.0 || distance_mm < 0.0 || aperture_diam_mm < 0.0) {
            return std::unexpected(ErrorCode::InvalidParameter);
        }

        PyrometerResult res{};
        res.ds_ratio = ds_ratio;
        res.spot_diameter_mm = aperture_diam_mm + (distance_mm / ds_ratio);
        res.cone_angle_deg = rad_to_deg(2.0 * std::atan(1.0 / (2.0 * ds_ratio)));

        return res;
    }
};

} // namespace optical
```
:::

## Архітектура модуля та інтерпретація структур

Програмний модуль спроектовано для використання у вбудованих системах реального часу (STM32, ESP32, Linux-based SBC на зразок Raspberry Pi CM4 чи NVIDIA Jetson).

### Розділення обов'язків між функціями

1. **`SensorSpec`**: описує фізичну геометрію кремнієвої підкладки матриці. Якщо точний розмір пікселя `pixel_pitch_um` невідомий або дорівнює нулю, алгоритм автоматично вираховує крок сітки як відношення фізичної ширини сенсора до кількості пікселів `res_x`.
2. **`calc_sensor_fov` / `calculate_fov`**: виконує розрахунок тривимірного пірамідального кута зору. Приймає опціональну робочу дистанцію `working_distance_mm`. Якщо дистанція дорівнює нулю (`WD = 0`), обчислення здійснюються для фокусування на оптичну нескінченність (`d_i = f`). Якщо дистанція є додатною, розраховується точне висування лінзи `d_i` за формулою тонкої лінзи.
3. **`calc_focal_length_for_scene` / `select_focal_length`**: вирішує обернену задачу проектування. За відомими габаритами інспекційного вікна `field_width_mm` та дистанцією монтажу камери розраховує точне значення фокусної відстані `required_f_mm`, а також встановлює прапорець `is_macro`, якщо масштаб збільшення `M ≥ 0.1`, сигналізуючи про необхідність використання подовжувальних кілець (Extension Tubes) або макрооб'єктива.
4. **`calc_pyrometer_spot` / `calculate_pyrometer_spot`**: обчислює інтегральну пляму збору теплової енергії інфрачервоного пірометра з урахуванням вхідного діаметра лінзи.

## Фізичні пастки та граничні випадки обчислень

Під час проектування оптичних вимірювальних систем виникають чотири критичні фізичні ефекти, нехтування якими спотворює геометричні розрахунки:

### 1. Ефект дихання фокусу (Focus Breathing)
У спрощених формулах часто приймають відстань від лінзи до сенсора рівною номінальній фокусній відстані `d_i = f`. Це справедливо лише за умови фокусування на оптичну нескінченність (`d_o → ∞`). При макрозйомці або роботі на близьких дистанціях (робоча відстань `WD < 10 · f`) об'єктив висувається вперед на величину додаткового ходу `Δx = f · M`.

Фактична відстань до матриці зростає до `d_i = f · (1 + M)`. Оскільки поле зору обчислюється як `FOV = 2 · arctan(d / (2 · d_i))`, при наближенні до об'єкта кутове поле зору зменшується:

```
FOV_eff = 2 · arctan(d / (2 · f · (1 + M)))
```

Для макролінзи зі збільшенням `M = 1.0` (масштаб 1:1) відстань до сенсора подвоюється `d_i = 2·f`, а тангенс кута огляду падає рівно вдвічі порівняно з нескінченністю. Наведений вище код автоматично враховує збільшення `M` та коригує розрахунок `FOV` за формулою тонкої лінзи.

### 2. Дисторсія та нелінійність кутового перетворення
Канонічна формула `w = 2 · d_i · tan(FOV / 2)` базується на моделі прямолінійної (перспективної) проекції Гауса (Pinhole / Rectilinear lens). Реальні ширококутні об'єктиви (кути `FOV > 60°`) зазнають радіальної дисторсії: бочкоподібної (Barrel) або подушкоподібної (Pincushion).

При бочкоподібній дисторсії коефіцієнт третього порядку `k₁ < 0` стискає периферичні зони матриці, збільшуючи фактичне кутове поле зору на краях за рахунок геометричного стиснення пікселів. Тому для вимірювального комп'ютерного зору (Metrology) вимагається калібрування матриці камери (Camera Calibration) за поліномом Брауна-Конраді або застосування спеціалізованих телецентричних об'єктивів (Telecentric Lenses), де головні промені паралельні оптичній осі, а кут огляду `FOV = 0°` при постійному полі спостереження.

### 3. Телецентрична оптика проти ентоцентричної
У класичних ентоцентричних (перспективних) об'єктивах збільшення залежить від відстані до об'єкта: якщо деталь наближається або має значну товщину (тривимірний рельєф), її верхня площина здається більшою за нижню. Це створює перспективне спотворення (Perspective Error) та унеможливлює точний вимір діаметрів отворів на різній глибині.

У телецентричних об'єктивах (Telecentric Lenses) апертурна діафрагма розташована у фокальній площині. Завдяки цьому головні промені у просторі предметів (Object-space Telecentric) поширюються строго паралельно до головної оптичної осі. Кутове поле зору такої системи дорівнює нулю (`FOV = 0°`), а лінійне збільшення `M` залишається постійним при будь-яких поздовжніх коливаннях деталі в межах глибини різкості (DOF). У таких системах розрахунок фокусної відстані через `tan(FOV/2)` втрачає фізичний зміст, а розмір поля зору визначається виключно світловим діаметром передньої лінзи об'єктива: `W_field = w_sensor / M`.

### 4. Оптичний показник візування пірометра (D:S Ratio)
У безконтактних інфрачервоних пірометрах і термографічних детекторах виробники вказують оптичний показник `D:S` (наприклад, 50:1 або 12:1), де `D` — дистанція до об'єкта, а `S` — діаметр плями, з якої збирається 90% інфрачервоного теплового випромінювання.

Поширена інженерна помилка полягає у розрахунку плями за простою пропорцією `S = D / (D:S)`. Ця формула не враховує вхідну апертуру оптичної лінзи пірометра `d_aperture`. На нульовій відстані (`D = 0`) діаметр плями не дорівнює нулю, а строго дорівнює діаметру лінзи приладу. Точне рівняння плями має вигляд:

```
S(D) = d_aperture + D / (D:S)
```

Якщо розмір контрольованого об'єкта на платі (наприклад, мікросхеми QFN розміром 4×4 мм) є меншим за обчислений діаметр плями `S(D)`, у поле зору пірометра потрапляє холодна або гаряча друкована плата, що призводить до систематичної похибки вимірювання температури на десятки градусів.

### 5. Дисперсійний зсув фокуса в спектральних діапазонах
Оптичні матеріали мають різний [показник заломлення](root:ph-waves/refractive-index) на різних довжинах хвиль через явище [оптичної дисперсії](root:ph-waves/optical-dispersion). Якщо оптичний модуль налаштовано для видимого світла (`λ ≈ 550 нм`), при переході в ближній інфрачервоний діапазон (NIR, `λ = 850–940 нм` для нічної підсвітки) показник заломлення скла падає.

Згідно з формулою шліфувальника лінз, зменшення `n` збільшує фокусну відстань `f`. Без використання спеціальних IR-коригованих об'єктивів площина різкого зображення зміщується назад, спричиняючи дефокусування та розмиття контурів об'єктів при перемиканні камери в нічний режим.
