# 📋 Інтерфейс специфікації IGRF та обчислення геомагнітного поля

Міжнародна геомагнітна еталонна модель (International Geomagnetic Reference Field, **IGRF**) є фундаментальним стандартом кількісного опису головного (ядерного) магнітного поля Землі. Модель розробляється та затверджується Міжнародною асоціацією геомагнетизму та аерономії (IAGA) на основі координованих даних супутникових місій (Oersted, CHAMP, Swarm) та мережі наземних геомагнітних обсерваторій.

Кожні 5 років опубліковується нове покоління коефіцієнтів IGRF, яке включає набір коефіцієнтів Гаусса для фіксованої епохи та коефіцієнти секулярного ходу (вікового дрейфу) на наступну 5-річну перспективу. Модель IGRF є базовим стандартом для аеронавігації, буріння орієнтованих свердловин, коригування супутникових орбіт, калібрування компасних датчиків у мобільних пристроях та дослідження фізики іоносфери й магнітосфери.

Нижче наведено математичну специфікацію моделі Гаусса, формати коефіцієнтів, структури даних та уніфікований програмний інтерфейс (API) мовами C та C++ для обчислення компонентів геомагнітного поля у довільній точці навколоземного простору.

## 1. Специфікація математичної моделі Гаусса

Поза джерелами струму (в атмосфері та на поверхні Землі, де густина електричних струмів `J = 0` та `∇ × B = 0`) вектор магнітної індукції описується як градієнт скалярного магнітного потенціалу `V`:

```
B = -∇V
```

Скалярний потенціал `V` розкладається в ряд за сферичними гармоніками у геоцентричній сферичній системі координат `(r, θ, φ)` (де `r` — геоцентрична відстань від центра Землі, `θ` — сферична коширота `90° - широта`, `φ` — довгота):

```
V(r, θ, φ) = a · ∑ₙ₌₁ᴺ (a / r)ⁿ⁺¹ ∑ₘ₌₀ⁿ [ gₙᵐ(t) · cos(m·φ) + hₙᵐ(t) · sin(m·φ) ] · Pₙᵐ(cos θ)
```

де:
- `a = 6371.2 км` — еталонний радіус Землі (значення сферичного радіуса у геомагнетизмі);
- `N = 13` — максимальний порядок гармонічного розкладу (для актуальної моделі IGRF-13 та IGRF-14);
- `gₙᵐ(t)`, `hₙᵐ(t)` — коефіцієнти Гаусса (вимірюються в нанотеслах, нТл), які є функціями часу `t` та лінійно інтерполюються між епохами;
- `Pₙᵐ(cos θ)` — приєднані поліноми Лежандра ступеня `n` та порядку `m`, квазінормалізовані за методом Шмідта.

Компоненти вектора магнітної індукції у геоцентричній сферичній системі координат обчислюються як відповідні часткові похідні потенціалу `V`:

```
B_r = -∂V / ∂r = ∑ₙ (n+1) · (a/r)ⁿ⁺² ∑ₘ [ gₙᵐ cos(mφ) + hₙᵐ sin(mφ) ] Pₙᵐ(cos θ)
B_θ = -(1/r) · ∂V / ∂θ = -∑ₙ (a/r)ⁿ⁺² ∑ₘ [ gₙᵐ cos(mφ) + hₙᵐ sin(mφ) ] (dPₙᵐ/dθ)
B_φ = -(1 / (r·sin θ)) · ∂V / ∂φ = (1/sin θ) · ∑ₙ (a/r)ⁿ⁺² ∑ₘ m · [ gₙᵐ sin(mφ) - hₙᵐ cos(mφ) ] Pₙᵐ(cos θ)
```

Для врахування часової динаміки геомагнітного поля між 5-річними епохами коефіцієнти Гаусса обчислюються за допомогою лінійної інтерполяції з урахуванням швидкостей секулярного ходу `dgₙᵐ/dt` та `dhₙᵐ/dt`:

```
gₙᵐ(t) = gₙᵐ(t₀) + (t - t₀) · (dgₙᵐ / dt)
hₙᵐ(t) = hₙᵐ(t₀) + (t - t₀) · (dhₙᵐ / dt)
```

де `t₀` — базова епоха моделі (наприклад, 2020.0 або 2025.0), а `t` — цільовий рік розрахунку.

## 2. Перетворення геодезичних координат та геомагнітні компоненти

Земля не є ідеальною сферою, а описується референц-еліпсоїдом WGS84 з екваторіальним радіусом `a_e = 6378.137 км` та стисненням `f = 1 / 298.257223563`. Тому геодезичні координати спостерігача (широта `φ_gd`, довгота `λ`, висота над рівнем моря `h_ell`) спочатку перераховуються у сферичні геоцентричні координати `(r, θ, φ)`:

```
p = (N_rad + h_ell) · cos(φ_gd)
Z_center = (N_rad · (1 - e²) + h_ell) · sin(φ_gd)
r = √(p² + Z_center²)
cos(θ) = Z_center / r
```

де `N_rad = a_e / √(1 - e² · sin²(φ_gd))` — радіус кривини вертикала, `e² = 2f - f²` — квадрат першого ексцентриситету.

Після обчислення сферичних геоцентричних компонент вектора індукції `(B_r, B_θ, B_φ)` виконується зворотний поворот вектора на кут відхилення геодезичної нормалі від геоцентричного радіуса-вектора `ψ = φ_gd - (90° - θ)`:

- `X` (Північна компонента): `X = -B_θ · cos(ψ) - B_r · sin(ψ)`;
- `Y` (Східна компонента): `Y = B_φ`;
- `Z` (Вертикальна компонента вниз): `Z = B_θ · sin(ψ) - B_r · cos(ψ)`;
- `H` (Горизонтальна напруженість): `H = √(X² + Y²)`;
- `F` (Повний модуль магнітної індукції): `F = √(X² + Y² + Z²) = √(H² + Z²)`;
- `D` (Магнітна деклінація / схилення): `D = arctan2(Y, X)` (кут між географічним та магнітним північними полюсами);
- `I` (Магнітна інклінація / нахил): `I = arctan2(Z, H)` (кут між вектором індукції та горизонтальною площиною).

## 3. Специфікація текстового файлу коефіцієнтів Гаусса

Стандартні коефіцієнти моделі розповсюджуються IAGA у вигляді текстового табличного файлу (наприклад, `IGRF13.COF` або `igrf13coeffs.txt`). Кожен рядок описує один коефіцієнт для серії епох:

```
gh  n  m   1900.0   1905.0  ...   2020.0   2025.0-30
g   1  0  -31543.0 -31464.0 ...  -29404.8      6.7
g   1  1   -2297.0  -2298.0 ...   -1450.9      9.3
h   1  1    5922.0   5909.0 ...    4652.5    -25.9
```

Правила парсингу та валідації файлу коефіцієнтів:
- Перші рядки містять заголовки епох із кроком 5 років.
- Символ `g` або `h` у першій колонці позначає тип коефіцієнта Гаусса.
- Друга та третя колонки визначають ступінь `n` (`1 ≤ n ≤ 13`) та порядок `m` (`0 ≤ m ≤ n`).
- Останній стовпчик (наприклад `2025.0-30`) містить річний секулярний хід у нТл/рік для прогнозу на наступні 5 років.

## 4. Програмний інтерфейс (API) обчислення IGRF

:::tabs
```c
/* igrf_model.h - C API специфікації геомагнітної моделі IGRF */
#ifndef IGRF_MODEL_H
#define IGRF_MODEL_H

#ifdef __cplusplus
extern "C" {
#endif

#define IGRF_MAX_DEGREE 13
#define IGRF_NUM_COEFFS (((IGRF_MAX_DEGREE + 1) * (IGRF_MAX_DEGREE + 2)) / 2)

/* Геодезичні координати спостерігача (WGS84) */
typedef struct {
    double latitude_deg;   /* Географічна широта [-90.0 .. +90.0] */
    double longitude_deg;  /* Географічна долгота [-180.0 .. +180.0] */
    double altitude_km;    /* Висота над рівнем моря WGS84 (км) */
    double epoch_year;     /* Епоха (наприклад, 2025.5) */
} GeodeticCoord;

/* Результуючий геомагнітний вектор */
typedef struct {
    double X_nT;  /* Північна компонента (нТл) */
    double Y_nT;  /* Східна компонента (нТл) */
    double Z_nT;  /* Вертикальна компонента вниз (нТл) */
    double H_nT;  /* Горизонтальна напруженість (нТл) */
    double F_nT;  /* Повний модуль магнітного поля (нТл) */
    double D_deg; /* Деклінація (градуси, схід > 0) */
    double I_deg; /* Інклінація (градуси, вниз > 0) */
} MagneticVector;

/* Структура коефіцієнтів Гаусса для конкретної епохи */
typedef struct {
    double epoch;
    double g[IGRF_MAX_DEGREE + 1][IGRF_MAX_DEGREE + 1];
    double h[IGRF_MAX_DEGREE + 1][IGRF_MAX_DEGREE + 1];
} IGRFCoefficients;

/**
 * Обчислення геомагнітного вектора за координатами WGS84.
 * @param coord Координати та епоха спостерігача
 * @param coeffs Завантажені коефіцієнти Гаусса
 * @param result Вихідний вектор магнітного поля
 * @return 0 при успіху, від'ємний код при помилці
 */
int igrf_calculate(const GeodeticCoord* coord, const IGRFCoefficients* coeffs, MagneticVector* result);

#ifdef __cplusplus
}
#endif

#endif /* IGRF_MODEL_H */
```
```cpp
// igrf_model.hpp - Ідіоматичний C++ API геомагнітної моделі IGRF
#ifndef IGRF_MODEL_HPP
#define IGRF_MODEL_HPP

#include <cmath>
#include <vector>
#include <array>
#include <string>
#include <string_view>
#include <expected>
#include <system_error>

namespace geodynamo::igrf {

constexpr std::size_t MaxDegree = 13;
constexpr double EarthRadiusKm = 6371.2;

struct GeodeticCoord {
    double latitude_deg{0.0};
    double longitude_deg{0.0};
    double altitude_km{0.0};
    double epoch_year{2025.0};
};

struct MagneticVector {
    double X_nT{0.0};
    double Y_nT{0.0};
    double Z_nT{0.0};
    double H_nT{0.0};
    double F_nT{0.0};
    double D_deg{0.0};
    double I_deg{0.0};
};

enum class IGRFError {
    InvalidLatitude,
    InvalidLongitude,
    InvalidEpoch,
    FileNotFound,
    ParseError
};

class IGRFModel {
public:
    using Matrix = std::array<std::array<double, MaxDegree + 1>, MaxDegree + 1>;

    IGRFModel() = default;

    // Завантаження коефіцієнтів з текстового файлу IGRF.COF / igrf13.f
    [[nodiscard]] static std::expected<IGRFModel, IGRFError> load_from_file(std::string_view filepath);

    // Встановлення коефіцієнтів напряму
    void set_coefficients(double epoch, const Matrix& g, const Matrix& h) noexcept {
        epoch_ = epoch;
        g_ = g;
        h_ = h;
    }

    // Обчислення геомагнітного вектора
    [[nodiscard]] std::expected<MagneticVector, IGRFError> evaluate(const GeodeticCoord& coord) const noexcept;

private:
    double epoch_{2025.0};
    Matrix g_{};
    Matrix h_{};

    // Нормалізовані приєднані поліноми Лежандра та їхні похідні
    void compute_legendre(double costheta, double sintheta, 
                          std::array<std::array<double, MaxDegree + 1>, MaxDegree + 1>& P,
                          std::array<std::array<double, MaxDegree + 1>, MaxDegree + 1>& dP) const noexcept;
};

} // namespace geodynamo::igrf

#endif // IGRF_MODEL_HPP
```
:::

## 5. Приклад обчислення магнітного поля у C та C++

:::tabs
```c
/* main_igrf.c - Реалізація та демо-обчислення геомагнітного поля у Київській області */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "igrf_model.h"

int igrf_calculate(const GeodeticCoord* coord, const IGRFCoefficients* coeffs, MagneticVector* result) {
    if (!coord || !coeffs || !result) return -1;
    if (coord->latitude_deg < -90.0 || coord->latitude_deg > 90.0) return -2;

    /* Спрощений дипольний розрахунок для головних коефіцієнтів g10, g11, h11 */
    double g10 = coeffs->g[1][0]; /* ~ -29400 нТл */
    double g11 = coeffs->g[1][1]; /* ~ -1450 нТл */
    double h11 = coeffs->h[1][1]; /* ~ 4650 нТл */

    double lat_rad = coord->latitude_deg * (M_PI / 180.0);
    double lon_rad = coord->longitude_deg * (M_PI / 180.0);
    double r = 6371.2 + coord->altitude_km;
    double r_ratio = 6371.2 / r;
    double r_factor = r_ratio * r_ratio * r_ratio;

    double colat = (90.0 - coord->latitude_deg) * (M_PI / 180.0);

    /* Радіальна та меридіональна компоненти диполя */
    double Br = 2.0 * r_factor * (g10 * cos(colat) + (g11 * cos(lon_rad) + h11 * sin(lon_rad)) * sin(colat));
    double Bt = -r_factor * (-g10 * sin(colat) + (g11 * cos(lon_rad) + h11 * sin(lon_rad)) * cos(colat));
    double Bp = (r_factor / sin(colat)) * (-g11 * sin(lon_rad) + h11 * cos(lon_rad)) * sin(colat);

    /* Перетворення до географічної системи X (Північ), Y (Схід), Z (Вниз) */
    result->X_nT = -Bt;
    result->Y_nT = Bp;
    result->Z_nT = -Br;

    result->H_nT = sqrt(result->X_nT * result->X_nT + result->Y_nT * result->Y_nT);
    result->F_nT = sqrt(result->H_nT * result->H_nT + result->Z_nT * result->Z_nT);
    result->D_deg = atan2(result->Y_nT, result->X_nT) * (180.0 / M_PI);
    result->I_deg = atan2(result->Z_nT, result->H_nT) * (180.0 / M_PI);

    return 0;
}

int main(void) {
    GeodeticCoord kiev = {
        .latitude_deg = 50.4501,
        .longitude_deg = 30.5234,
        .altitude_km = 0.18,
        .epoch_year = 2025.0
    };

    IGRFCoefficients coeffs = { .epoch = 2025.0 };
    coeffs.g[1][0] = -29400.0;
    coeffs.g[1][1] = -1450.0;
    coeffs.h[1][1] = 4650.0;

    MagneticVector mag;
    if (igrf_calculate(&kiev, &coeffs, &mag) == 0) {
        printf("--- Геомагнітні компоненти у Києві (2025.0) ---\n");
        printf("Північна компонента (X):  %.1f нТл\n", mag.X_nT);
        printf("Східна компонента (Y):    %.1f нТл\n", mag.Y_nT);
        printf("Вертикальна компонента(Z):%.1f нТл\n", mag.Z_nT);
        printf("Горизонтальна напруга(H): %.1f нТл\n", mag.H_nT);
        printf("Повна індукція (F):       %.1f нТл\n", mag.F_nT);
        printf("Магнітна деклінація (D):  %.2f°\n", mag.D_deg);
        printf("Магнітна інклінація (I):  %.2f°\n", mag.I_deg);
    }
    return 0;
}
```
```cpp
// main_igrf.cpp - C++ реалізація з еталонними викликами та перевіркою меж
#include <iostream>
#include <iomanip>
#include "igrf_model.hpp"

namespace geodynamo::igrf {

std::expected<MagneticVector, IGRFError> IGRFModel::evaluate(const GeodeticCoord& coord) const noexcept {
    if (coord.latitude_deg < -90.0 || coord.latitude_deg > 90.0) {
        return std::unexpected(IGRFError::InvalidLatitude);
    }
    if (coord.longitude_deg < -180.0 || coord.longitude_deg > 180.0) {
        return std::unexpected(IGRFError::InvalidLongitude);
    }

    const double lat_rad = coord.latitude_deg * (std::numbers::pi / 180.0);
    const double lon_rad = coord.longitude_deg * (std::numbers::pi / 180.0);
    const double colat = (90.0 - coord.latitude_deg) * (std::numbers::pi / 180.0);

    const double r = EarthRadiusKm + coord.altitude_km;
    const double r_ratio = EarthRadiusKm / r;
    const double r_factor = r_ratio * r_ratio * r_ratio;

    const double g10 = g_[1][0];
    const double g11 = g_[1][1];
    const double h11 = h_[1][1];

    const double Br = 2.0 * r_factor * (g10 * std::cos(colat) + (g11 * std::cos(lon_rad) + h11 * std::sin(lon_rad)) * std::sin(colat));
    const double Bt = -r_factor * (-g10 * std::sin(colat) + (g11 * std::cos(lon_rad) + h11 * std::sin(lon_rad)) * std::cos(colat));
    const double Bp = (r_factor / std::sin(colat)) * (-g11 * std::sin(lon_rad) + h11 * std::cos(lon_rad)) * std::sin(colat);

    MagneticVector res;
    res.X_nT = -Bt;
    res.Y_nT = Bp;
    res.Z_nT = -Br;
    res.H_nT = std::hypot(res.X_nT, res.Y_nT);
    res.F_nT = std::hypot(res.H_nT, res.Z_nT);
    res.D_deg = std::atan2(res.Y_nT, res.X_nT) * (180.0 / std::numbers::pi);
    res.I_deg = std::atan2(res.Z_nT, res.H_nT) * (180.0 / std::numbers::pi);

    return res;
}

} // namespace geodynamo::igrf

int main() {
    using namespace geodynamo::igrf;

    IGRFModel model;
    IGRFModel::Matrix g{}, h{};
    g[1][0] = -29400.0;
    g[1][1] = -1450.0;
    h[1][1] = 4650.0;
    model.set_coefficients(2025.0, g, h);

    GeodeticCoord coord{.latitude_deg = 50.4501, .longitude_deg = 30.5234, .altitude_km = 0.18, .epoch_year = 2025.0};

    auto result = model.evaluate(coord);
    if (result) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "--- C++ IGRF Результат (Київ 2025.0) ---\n";
        std::cout << "X (Північ): " << result->X_nT << " нТл\n";
        std::cout << "Y (Схід):   " << result->Y_nT << " нТл\n";
        std::cout << "Z (Вниз):   " << result->Z_nT << " нТл\n";
        std::cout << "H (Гориз):  " << result->H_nT << " нТл\n";
        std::cout << "F (Повне):  " << result->F_nT << " нТл\n";
        std::cout << "D (Деклін): " << result->D_deg << "°\n";
        std::cout << "I (Інклін): " << result->I_deg << "°\n";
    } else {
        std::cerr << "Помилка обчислення моделі IGRF!\n";
    }
    return 0;
}
```
:::

## 6. Границі застосовності та інженерні обмеження

При розробці автономних навігаційних систем, геофізичного обладнання та алгоритмів орієнтації космічних апаратів слід чітко розрізняти сфери застосовності моделі IGRF та її природні обмеження:

1. **Відсікання корового магнітного поля**: Стандарт IGRF обмежено максимальним ступенем розкладу `N = 13`. Це свідомий вибір розробників: гармоніки до `N = 13` описують дипольне та недипольне поле, що ґенерується струмами рідкого ядра Землі. Починаючи з `N = 14`, амплітуда ядерного поля стає меншою за намагніченість кристалічних порід земної кори (феромагнітних мінералів на кшталт магнетиту та титаномагнетиту). Корове поле має локальний характер (аномалії шириною від десятків метрів до сотень кілометрів) і вимагає регіональних геомагнітних карт або локальних магнітометричних зйомок.
2. **Зовнішні варіації та космічна погода**: Модель IGRF обчислює квазістаціонарне магнітне поле земного походження і не враховує варіації, породжені струмовими системами іоносфери та магнітосфери (кільцевий струм, струми у хвості магнітосфери). Під час потужних геомагнітних бур інтенсивність зовнішніх полів може викликати флуктуації деклінації на кілька градусів за кілька годин, що створює тимчасові похибки для чисто компасної навігації.
3. **Часовий крок та дрейф коефіцієнтів**: Лінійна інтерполяція коефіцієнтів Гаусса `gₙᵐ(t)` між 5-річними епохами є наближенням. У областях із прискореним секулярним ходом (наприклад, у районі Південно-Атлантичної магнітної аномалії або при стрімкому русі північного магнітного полюса в бік Сибіру зі швидкістю до 55 км/рік) відхилення лінійної інтерполяції від реального поля може досягати десятків нТл на рік.
4. **Полярні області та нестійкість деклінації**: На геомагнітних полюсах вертикальна компонента `Z` прямує до максимуму, а горизонтальна компонента `H = √(X² + Y²)` прямує до нуля. Оскільки деклінація `D = arctan2(Y, X)` визначається через частку компонент, поблизу магнітних полюсів найменша шумова похибка вимірювача призводить до хаотичного обертання розрахованого значення деклінації `D`. У високоширотній навігації замість деклінації оперують сітковою деклінацією (Grid Declination) відносно полярних сіток проекцій.
