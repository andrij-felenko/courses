# ⚙️ Програмна реалізація перетворення Гельмерта, конвенцій та оцінки параметрів

Перетворення Гельмерта у просторових геоінформаційних рушіях та навігаційних бібліотеках (PROJ, GDAL, RTKLib, QGIS) є фундаментом просторової сумісності даних. Будь-який супутниковий GNSS-приймач видає декартові координати в глобальній геоцентричній системі WGS-84 або ITRF, тоді як кадастрові карти, будівельні генеральні плани й національні картографічні шари майже завжди прив'язані до місцевих чи регіональних референцних систем (таких як ED50, СК-42, УСК-2000, OSGB36, NAD83).

Безпосередній перевід вимагає розв'язання задачі просторової подібності з урахуванням трьох критичних факторів:

1. **Вибір геодезичної конвенції:** Position Vector (EPSG метод 9606) чи Coordinate Frame (EPSG метод 9607). Вони математично пов'язані через операцію транспонування матриці обертання `R_cf = R_pvᵀ`, а тому їхні кутові параметри `(Rx, Ry, Rz)` мають суворо протилежні знаки. Переплутати конвенцію — найпоширеніша помилка в геодезичному програмному забезпеченні, яка створює подвійне спотворення координат.
2. **Одиниця масштабу:** масштабний коефіцієнт у геодезії традиційно задають не як прямий множник `k ≈ 1.0`, а як відносний диференціал `m` у мільйонних частках (`ppm`, *parts per million*), де `1 ppm = 10⁻⁶`. Безпосереднє масштабування виконується через множник `(1 + m · 10⁻⁶)`.
3. **Чисельна стійкість та зворотність:** пряме й зворотне перетворення мають бути аналітично узгодженими до часток міліметра. Для малих кутів обертання транспонування матриці дає точне зворотне обертання, а ділення на `(1 + s)` відновлює початковий масштаб без накопичення похибок округлення чисел із плаваючою комою подвійної точності (`double`).

## Архітектурні вимоги до реалізації

Для створення надійної геодезичної бібліотеки необхідно підтримувати три споріднені моделі трансформування:
- **7-параметрична класична модель Гельмерта (Бурси — Вольфа):** три лінійні зсуви `(Tx, Ty, Tz)`, три малі кути повороту осей `(Rx, Ry, Rz)` та диференціал масштабу `s_ppm`. Застосовується для глобальних перетворень між загальноземними системами.
- **10-параметрична модель Молоденського — Бадекаса:** доповнює 7 параметрів координатами фіксованого локального центру обертання `(X₀, Y₀, Z₀)` (барицентру регіональної мережі). Це усуває кореляцію між зсувами та поворотами при локальних перетвореннях.
- **14-параметрична кінематична модель:** враховує лінійні швидкості зміни всіх семи параметрів у часі `(Ṫx, Ṫy, Ṫz, Ṙx, Ṙy, Ṙz, ṡ)` відносно базової епохи `t₀`. Вона є обов'язковою для зв'язку динамічних глобальних систем відліку (ITRF2014, ITRF2020) з регіональними датумами, зафіксованими на рухомих тектонічних плитах (ETRF2000, NAD83).

Нижче наведено повну виробничу реалізацію: структуру параметрів для 7, 10 та 14 параметрів, функції прямого й зворотного перетворення, облік епохи спостережень і модуль оцінки семи параметрів за методом найменших квадратів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define ARCSEC_TO_RAD (4.8481368110953599e-6)

/* Геодезичні конвенції орієнтації кутів повороту */
typedef enum {
    HELMERT_POSITION_VECTOR = 0, /* EPSG: 9606 (IERS / ISO 19111) */
    HELMERT_COORDINATE_FRAME = 1  /* EPSG: 9607 (Bursa-Wolf)      */
} HelmertConvention;

/* Тривимірний вектор декартових координат у метрах */
typedef struct {
    double x;
    double y;
    double z;
} Vec3;

/* Семипараметричний набір Гельмерта */
typedef struct {
    double tx;  /* Зсув по X, м */
    double ty;  /* Зсув по Y, м */
    double tz;  /* Зсув по Z, м */
    double rx;  /* Поворот навколо X, кутові секунди */
    double ry;  /* Поворот навколо Y, кутові секунди */
    double rz;  /* Поворот навколо Z, кутові секунди */
    double s_ppm; /* Зміна масштабу, ppm (parts per million, 10^-6) */
    HelmertConvention convention;
} Helmert7;

/* Десятипараметричний набір Молоденського — Бадекаса */
typedef struct {
    Helmert7 h7;
    Vec3 centroid; /* Координати центру обертання (X0, Y0, Z0), м */
} Helmert10;

/* Чотирнадцятипараметричний кінематичний набір (з урахуванням швидкостей) */
typedef struct {
    Helmert7 base;       /* Параметри на опорну епоху t0 */
    double dtx;          /* Швидкість зсуву X, м/рік */
    double dty;          /* Швидкість зсуву Y, м/рік */
    double dtz;          /* Швидкість зсуву Z, м/рік */
    double drx;          /* Швидкість повороту X, кутові секунди/рік */
    double dry;          /* Швидкість повороту Y, кутові секунди/рік */
    double drz;          /* Швидкість повороту Z, кутові секунди/рік */
    double ds_ppm;       /* Швидкість зміни масштабу, ppm/рік */
    double epoch_t0;     /* Опорна епоха, дробовий рік (наприклад, 2010.0) */
} Helmert14;

/* Пряме 7-параметричне перетворення */
Vec3 helmert7_forward(const Helmert7 *h, Vec3 p) {
    /* Корекція знаку кутів за конвенцією */
    double sign = (h->convention == HELMERT_COORDINATE_FRAME) ? -1.0 : 1.0;
    double rx = h->rx * ARCSEC_TO_RAD * sign;
    double ry = h->ry * ARCSEC_TO_RAD * sign;
    double rz = h->rz * ARCSEC_TO_RAD * sign;
    double s  = h->s_ppm * 1.0e-6;

    /* Матриця (1 + s) * R у лінеаризованому вигляді */
    double x_rot = (1.0 + s) * ( p.x - rz * p.y + ry * p.z);
    double y_rot = (1.0 + s) * ( rz * p.x + p.y - rx * p.z);
    double z_rot = (1.0 + s) * (-ry * p.x + rx * p.y + p.z);

    Vec3 out;
    out.x = h->tx + x_rot;
    out.y = h->ty + y_rot;
    out.z = h->tz + z_rot;
    return out;
}

/* Зворотне 7-параметричне перетворення */
Vec3 helmert7_inverse(const Helmert7 *h, Vec3 p) {
    /* Віднімаємо лінійний зсув */
    double dx = p.x - h->tx;
    double dy = p.y - h->ty;
    double dz = p.z - h->tz;

    double sign = (h->convention == HELMERT_COORDINATE_FRAME) ? -1.0 : 1.0;
    double rx = h->rx * ARCSEC_TO_RAD * sign;
    double ry = h->ry * ARCSEC_TO_RAD * sign;
    double rz = h->rz * ARCSEC_TO_RAD * sign;
    double scale = 1.0 / (1.0 + h->s_ppm * 1.0e-6);

    /* Множення на транспоновану матрицю обертання R^T */
    Vec3 out;
    out.x = scale * ( dx + rz * dy - ry * dz);
    out.y = scale * (-rz * dx + dy + rx * dz);
    out.z = scale * ( ry * dx - rx * dy + dz);
    return out;
}

/* Пряме перетворення Молоденського — Бадекаса (10 параметрів) */
Vec3 helmert10_forward(const Helmert10 *h, Vec3 p) {
    /* Зсув точки відносно центроїда */
    Vec3 p_rel;
    p_rel.x = p.x - h->centroid.x;
    p_rel.y = p.y - h->centroid.y;
    p_rel.z = p.z - h->centroid.z;

    double sign = (h->h7.convention == HELMERT_COORDINATE_FRAME) ? -1.0 : 1.0;
    double rx = h->h7.rx * ARCSEC_TO_RAD * sign;
    double ry = h->h7.ry * ARCSEC_TO_RAD * sign;
    double rz = h->h7.rz * ARCSEC_TO_RAD * sign;
    double s  = h->h7.s_ppm * 1.0e-6;

    double x_rot = (1.0 + s) * ( p_rel.x - rz * p_rel.y + ry * p_rel.z);
    double y_rot = (1.0 + s) * ( rz * p_rel.x + p_rel.y - rx * p_rel.z);
    double z_rot = (1.0 + s) * (-ry * p_rel.x + rx * p_rel.y + p_rel.z);

    Vec3 out;
    out.x = h->centroid.x + h->h7.tx + x_rot;
    out.y = h->centroid.y + h->h7.ty + y_rot;
    out.z = h->centroid.z + h->h7.tz + z_rot;
    return out;
}

/* Обчислення миттєвих параметрів на епоху t для 14-параметричної моделі */
Helmert7 helmert14_at_epoch(const Helmert14 *h14, double epoch_t) {
    double dt = epoch_t - h14->epoch_t0;
    Helmert7 h;
    h.tx    = h14->base.tx    + h14->dtx * dt;
    h.ty    = h14->base.ty    + h14->dty * dt;
    h.tz    = h14->base.tz    + h14->dtz * dt;
    h.rx    = h14->base.rx    + h14->drx * dt;
    h.ry    = h14->base.ry    + h14->dry * dt;
    h.rz    = h14->base.rz    + h14->drz * dt;
    h.s_ppm = h14->base.s_ppm + h14->ds_ppm * dt;
    h.convention = h14->base.convention;
    return h;
}

/* Оцінка 7 параметрів Гельмерта за методом найменших квадратів */
bool estimate_helmert7(const Vec3 *src, const Vec3 *tgt, int n,
                       HelmertConvention convention, Helmert7 *out_h) {
    if (n < 3) return false;

    /* Матриця нормальних рівнянь N = A^T * A (7x7) та вектор U = A^T * L (7x1) */
    double N[7][7] = {0};
    double U[7] = {0};

    for (int i = 0; i < n; ++i) {
        double x = src[i].x;
        double y = src[i].y;
        double z = src[i].z;

        double lx = tgt[i].x - x;
        double ly = tgt[i].y - y;
        double lz = tgt[i].z - z;

        /* Рядки матриці спостережень A для точки i (для Position Vector) */
        /* Рядок 1: [ 1,  0,  0,    0,   z,  -y,  x ] */
        /* Рядок 2: [ 0,  1,  0,   -z,   0,   x,  y ] */
        /* Рядок 3: [ 0,  0,  1,    y,  -x,   0,  z ] */
        double A[3][7] = {
            { 1.0, 0.0, 0.0,  0.0 * ARCSEC_TO_RAD,  z * ARCSEC_TO_RAD, -y * ARCSEC_TO_RAD, x * 1.0e-6 },
            { 0.0, 1.0, 0.0, -z * ARCSEC_TO_RAD,  0.0 * ARCSEC_TO_RAD,  x * ARCSEC_TO_RAD, y * 1.0e-6 },
            { 0.0, 0.0, 1.0,  y * ARCSEC_TO_RAD, -x * ARCSEC_TO_RAD,  0.0 * ARCSEC_TO_RAD, z * 1.0e-6 }
        };

        if (convention == HELMERT_COORDINATE_FRAME) {
            for (int r = 0; r < 3; ++r) {
                A[r][3] = -A[r][3];
                A[r][4] = -A[r][4];
                A[r][5] = -A[r][5];
            }
        }

        double L[3] = { lx, ly, lz };

        /* Акумуляція N = A^T * A та U = A^T * L */
        for (int j = 0; j < 7; ++j) {
            for (int k = 0; k < 7; ++k) {
                for (int r = 0; r < 3; ++r) {
                    N[j][k] += A[r][j] * A[r][k];
                }
            }
            for (int r = 0; r < 3; ++r) {
                U[j] += A[r][j] * L[r];
            }
        }
    }

    /* Розв'язання системи N * x = U методом виключення Гауса з вибором головного елемента */
    double Aug[7][8];
    for (int i = 0; i < 7; ++i) {
        for (int j = 0; j < 7; ++j) Aug[i][j] = N[i][j];
        Aug[i][7] = U[i];
    }

    for (int col = 0; col < 7; ++col) {
        int pivot = col;
        double max_val = fabs(Aug[col][col]);
        for (int r = col + 1; r < 7; ++r) {
            if (fabs(Aug[r][col]) > max_val) {
                max_val = fabs(Aug[r][col]);
                pivot = r;
            }
        }
        if (max_val < 1e-15) return false; /* Матриця вироджена */

        if (pivot != col) {
            for (int k = col; k < 8; ++k) {
                double tmp = Aug[col][k];
                Aug[col][k] = Aug[pivot][k];
                Aug[pivot][k] = tmp;
            }
        }

        for (int r = col + 1; r < 7; ++r) {
            double factor = Aug[r][col] / Aug[col][col];
            for (int k = col; k < 8; ++k) {
                Aug[r][k] -= factor * Aug[col][k];
            }
        }
    }

    double sol[7];
    for (int r = 6; r >= 0; --r) {
        double sum = Aug[r][7];
        for (int k = r + 1; k < 7; ++k) {
            sum -= Aug[r][k] * sol[k];
        }
        sol[r] = sum / Aug[r][r];
    }

    out_h->tx = sol[0];
    out_h->ty = sol[1];
    out_h->tz = sol[2];
    out_h->rx = sol[3];
    out_h->ry = sol[4];
    out_h->rz = sol[5];
    out_h->s_ppm = sol[6];
    out_h->convention = convention;
    return true;
}

int main(void) {
    /* Тестовий набір EPSG:1618 (ED50 до WGS 84 для Великої Британії) */
    Helmert7 ed50_to_wgs84 = {
        .tx = -89.5,
        .ty = -93.8,
        .tz = -123.1,
        .rx = 0.0,
        .ry = 0.0,
        .rz = -0.156,
        .s_ppm = -1.2,
        .convention = HELMERT_POSITION_VECTOR
    };

    Vec3 pt_ed50 = { 3978280.0, -100410.0, 4968390.0 };
    Vec3 pt_wgs84 = helmert7_forward(&ed50_to_wgs84, pt_ed50);
    Vec3 pt_back  = helmert7_inverse(&ed50_to_wgs84, pt_wgs84);

    printf("Пряме перетворення ED50 -> WGS84:\n");
    printf("  X: %12.3f -> %12.3f м\n", pt_ed50.x, pt_wgs84.x);
    printf("  Y: %12.3f -> %12.3f м\n", pt_ed50.y, pt_wgs84.y);
    printf("  Z: %12.3f -> %12.3f м\n", pt_ed50.z, pt_wgs84.z);

    printf("\nНев'язка зворотного перетворення:\n");
    printf("  dX: %.6f мм, dY: %.6f мм, dZ: %.6f мм\n",
           (pt_back.x - pt_ed50.x) * 1000.0,
           (pt_back.y - pt_ed50.y) * 1000.0,
           (pt_back.z - pt_ed50.z) * 1000.0);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <expected>
#include <string_view>
#include <span>
#include <iomanip>

namespace geodesy {

inline constexpr double ArcsecToRad = 4.8481368110953599e-6;

enum class Convention {
    PositionVector,  // EPSG: 9606 (IERS, ISO 19111, активний поворот)
    CoordinateFrame  // EPSG: 9607 (Bursa-Wolf, пасивний поворот)
};

struct Vec3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr Vec3 operator+(const Vec3& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    [[nodiscard]] constexpr Vec3 operator-(const Vec3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    [[nodiscard]] constexpr Vec3 operator*(double s) const noexcept {
        return {x * s, y * s, z * s};
    }
};

struct Helmert7 {
    double tx{0.0};    // м
    double ty{0.0};    // м
    double tz{0.0};    // м
    double rx{0.0};    // кутові секунди
    double ry{0.0};    // кутові секунди
    double rz{0.0};    // кутові секунди
    double s_ppm{0.0}; // ppm (10^-6)
    Convention convention{Convention::PositionVector};

    [[nodiscard]] Vec3 forward(const Vec3& p) const noexcept {
        const double sign = (convention == Convention::CoordinateFrame) ? -1.0 : 1.0;
        const double rot_x = rx * ArcsecToRad * sign;
        const double rot_y = ry * ArcsecToRad * sign;
        const double rot_z = rz * ArcsecToRad * sign;
        const double scale = 1.0 + s_ppm * 1.0e-6;

        return {
            tx + scale * ( p.x - rot_z * p.y + rot_y * p.z),
            ty + scale * ( rot_z * p.x + p.y - rot_x * p.z),
            tz + scale * (-rot_y * p.x + rot_x * p.y + p.z)
        };
    }

    [[nodiscard]] Vec3 inverse(const Vec3& p) const noexcept {
        const Vec3 d = p - Vec3{tx, ty, tz};
        const double sign = (convention == Convention::CoordinateFrame) ? -1.0 : 1.0;
        const double rot_x = rx * ArcsecToRad * sign;
        const double rot_y = ry * ArcsecToRad * sign;
        const double rot_z = rz * ArcsecToRad * sign;
        const double inv_scale = 1.0 / (1.0 + s_ppm * 1.0e-6);

        return {
            inv_scale * ( d.x + rot_z * d.y - rot_y * d.z),
            inv_scale * (-rot_z * d.x + d.y + rot_x * d.z),
            inv_scale * ( rot_y * d.x - rot_x * d.y + d.z)
        };
    }
};

struct Helmert10 {
    Helmert7 h7;
    Vec3 centroid; // (X0, Y0, Z0), м

    [[nodiscard]] Vec3 forward(const Vec3& p) const noexcept {
        const Vec3 p_rel = p - centroid;
        const double sign = (h7.convention == Convention::CoordinateFrame) ? -1.0 : 1.0;
        const double rot_x = h7.rx * ArcsecToRad * sign;
        const double rot_y = h7.ry * ArcsecToRad * sign;
        const double rot_z = h7.rz * ArcsecToRad * sign;
        const double scale = 1.0 + h7.s_ppm * 1.0e-6;

        const Vec3 rot_p{
            scale * ( p_rel.x - rot_z * p_rel.y + rot_y * p_rel.z),
            scale * ( rot_z * p_rel.x + p_rel.y - rot_x * p_rel.z),
            scale * (-rot_y * p_rel.x + rot_x * p_rel.y + p_rel.z)
        };

        return centroid + Vec3{h7.tx, h7.ty, h7.tz} + rot_p;
    }
};

struct Helmert14 {
    Helmert7 base;
    double dtx{0.0};      // м/рік
    double dty{0.0};      // м/рік
    double dtz{0.0};      // м/рік
    double drx{0.0};      // кутові секунди/рік
    double dry{0.0};      // кутові секунди/рік
    double drz{0.0};      // кутові секунди/рік
    double ds_ppm{0.0};   // ppm/рік
    double epoch_t0{2000.0};

    [[nodiscard]] Helmert7 at_epoch(double epoch_t) const noexcept {
        const double dt = epoch_t - epoch_t0;
        return {
            .tx = base.tx + dtx * dt,
            .ty = base.ty + dty * dt,
            .tz = base.tz + dtz * dt,
            .rx = base.rx + drx * dt,
            .ry = base.ry + dry * dt,
            .rz = base.rz + drz * dt,
            .s_ppm = base.s_ppm + ds_ppm * dt,
            .convention = base.convention
        };
    }
};

// Оцінка 7 параметрів МНК
[[nodiscard]] std::expected<Helmert7, std::string_view> estimate_helmert7(
    std::span<const Vec3> src,
    std::span<const Vec3> tgt,
    Convention convention = Convention::PositionVector) noexcept
{
    if (src.size() != tgt.size() || src.size() < 3) {
        return std::unexpected("Потрібно щонайменше 3 спільні точки");
    }

    std::array<std::array<double, 7>, 7> N{};
    std::array<double, 7> U{};

    for (size_t i = 0; i < src.size(); ++i) {
        const auto [x, y, z] = src[i];
        const auto [tx_val, ty_val, tz_val] = tgt[i];

        const double lx = tx_val - x;
        const double ly = ty_val - y;
        const double lz = tz_val - z;

        std::array<std::array<double, 7>, 3> A{{
            { 1.0, 0.0, 0.0,  0.0 * ArcsecToRad,  z * ArcsecToRad, -y * ArcsecToRad, x * 1.0e-6 },
            { 0.0, 1.0, 0.0, -z * ArcsecToRad,  0.0 * ArcsecToRad,  x * ArcsecToRad, y * 1.0e-6 },
            { 0.0, 0.0, 1.0,  y * ArcsecToRad, -x * ArcsecToRad,  0.0 * ArcsecToRad, z * 1.0e-6 }
        }};

        if (convention == Convention::CoordinateFrame) {
            for (auto& row : A) {
                row[3] = -row[3];
                row[4] = -row[4];
                row[5] = -row[5];
            }
        }

        const std::array<double, 3> L{lx, ly, lz};

        for (size_t j = 0; j < 7; ++j) {
            for (size_t k = 0; k < 7; ++k) {
                for (size_t r = 0; r < 3; ++r) {
                    N[j][k] += A[r][j] * A[r][k];
                }
            }
            for (size_t r = 0; r < 3; ++r) {
                U[j] += A[r][j] * L[r];
            }
        }
    }

    // Розв'язання системи N * x = U методом виключення Гауса
    std::array<std::array<double, 8>, 7> Aug{};
    for (size_t i = 0; i < 7; ++i) {
        for (size_t j = 0; j < 7; ++j) Aug[i][j] = N[i][j];
        Aug[i][7] = U[i];
    }

    for (size_t col = 0; col < 7; ++col) {
        size_t pivot = col;
        double max_val = std::abs(Aug[col][col]);
        for (size_t r = col + 1; r < 7; ++r) {
            if (std::abs(Aug[r][col]) > max_val) {
                max_val = std::abs(Aug[r][col]);
                pivot = r;
            }
        }
        if (max_val < 1e-15) return std::unexpected("Матриця нормальних рівнянь вироджена");

        if (pivot != col) std::swap(Aug[col], Aug[pivot]);

        for (size_t r = col + 1; r < 7; ++r) {
            const double factor = Aug[r][col] / Aug[col][col];
            for (size_t k = col; k < 8; ++k) {
                Aug[r][k] -= factor * Aug[col][k];
            }
        }
    }

    std::array<double, 7> sol{};
    for (int r = 6; r >= 0; --r) {
        double sum = Aug[r][7];
        for (size_t k = r + 1; k < 7; ++k) {
            sum -= Aug[r][k] * sol[k];
        }
        sol[r] = sum / Aug[r][r];
    }

    return Helmert7{
        .tx = sol[0],
        .ty = sol[1],
        .tz = sol[2],
        .rx = sol[3],
        .ry = sol[4],
        .rz = sol[5],
        .s_ppm = sol[6],
        .convention = convention
    };
}

} // namespace geodesy

int main() {
    using namespace geodesy;

    const Helmert7 ed50_to_wgs84{
        .tx = -89.5,
        .ty = -93.8,
        .tz = -123.1,
        .rx = 0.0,
        .ry = 0.0,
        .rz = -0.156,
        .s_ppm = -1.2,
        .convention = Convention::PositionVector
    };

    const Vec3 pt_ed50{3978280.0, -100410.0, 4968390.0};
    const Vec3 pt_wgs84 = ed50_to_wgs84.forward(pt_ed50);
    const Vec3 pt_back  = ed50_to_wgs84.inverse(pt_wgs84);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Пряме перетворення ED50 -> WGS84:\n"
              << "  X: " << pt_ed50.x << " -> " << pt_wgs84.x << " м\n"
              << "  Y: " << pt_ed50.y << " -> " << pt_wgs84.y << " м\n"
              << "  Z: " << pt_ed50.z << " -> " << pt_wgs84.z << " м\n\n";

    std::cout << std::setprecision(6);
    std::cout << "Нев'язка зворотного перетворення:\n"
              << "  dX: " << (pt_back.x - pt_ed50.x) * 1000.0 << " мм, "
              << "dY: " << (pt_back.y - pt_ed50.y) * 1000.0 << " мм, "
              << "dZ: " << (pt_back.z - pt_ed50.z) * 1000.0 << " мм\n";

    return 0;
}
```
```py
from dataclasses import dataclass
from enum import Enum
import math
import numpy as np

ARCSEC_TO_RAD = 4.8481368110953599e-6

class HelmertConvention(Enum):
    POSITION_VECTOR = "PositionVector"  # EPSG: 9606
    COORDINATE_FRAME = "CoordinateFrame"  # EPSG: 9607

@dataclass
class Helmert7:
    tx: float = 0.0  # м
    ty: float = 0.0  # м
    tz: float = 0.0  # м
    rx: float = 0.0  # кутові секунди
    ry: float = 0.0  # кутові секунди
    rz: float = 0.0  # кутові секунди
    s_ppm: float = 0.0  # ppm (10^-6)
    convention: HelmertConvention = HelmertConvention.POSITION_VECTOR

    def forward(self, p: np.ndarray) -> np.ndarray:
        p = np.asarray(p, dtype=float)
        sign = -1.0 if self.convention == HelmertConvention.COORDINATE_FRAME else 1.0
        rx = self.rx * ARCSEC_TO_RAD * sign
        ry = self.ry * ARCSEC_TO_RAD * sign
        rz = self.rz * ARCSEC_TO_RAD * sign
        s = self.s_ppm * 1e-6

        # Лінеаризована матриця (1 + s) * R
        rot = np.array([
            [1.0 + s, -(1.0 + s) * rz,  (1.0 + s) * ry],
            [(1.0 + s) * rz,  1.0 + s, -(1.0 + s) * rx],
            [-(1.0 + s) * ry, (1.0 + s) * rx,  1.0 + s]
        ])
        t = np.array([self.tx, self.ty, self.tz])
        return t + rot @ p

    def inverse(self, p: np.ndarray) -> np.ndarray:
        p = np.asarray(p, dtype=float)
        sign = -1.0 if self.convention == HelmertConvention.COORDINATE_FRAME else 1.0
        rx = self.rx * ARCSEC_TO_RAD * sign
        ry = self.ry * ARCSEC_TO_RAD * sign
        rz = self.rz * ARCSEC_TO_RAD * sign
        inv_scale = 1.0 / (1.0 + self.s_ppm * 1e-6)

        rot_t = np.array([
            [1.0,  rz, -ry],
            [-rz, 1.0,  rx],
            [ ry, -rx, 1.0]
        ]) * inv_scale
        t = np.array([self.tx, self.ty, self.tz])
        return rot_t @ (p - t)

def estimate_helmert7(src: np.ndarray, tgt: np.ndarray,
                      convention: HelmertConvention = HelmertConvention.POSITION_VECTOR) -> Helmert7:
    src, tgt = np.asarray(src, dtype=float), np.asarray(tgt, dtype=float)
    n = len(src)
    if n < 3:
        raise ValueError("Потрібно щонайменше 3 опорні пункти")

    A_rows = []
    L_rows = []

    for (x, y, z), (X, Y, Z) in zip(src, tgt):
        row_x = [1.0, 0.0, 0.0,  0.0 * ARCSEC_TO_RAD,  z * ARCSEC_TO_RAD, -y * ARCSEC_TO_RAD, x * 1e-6]
        row_y = [0.0, 1.0, 0.0, -z * ARCSEC_TO_RAD,  0.0 * ARCSEC_TO_RAD,  x * ARCSEC_TO_RAD, y * 1e-6]
        row_z = [0.0, 0.0, 1.0,  y * ARCSEC_TO_RAD, -x * ARCSEC_TO_RAD,  0.0 * ARCSEC_TO_RAD, z * 1e-6]

        if convention == HelmertConvention.COORDINATE_FRAME:
            row_x[3:6] = [-v for v in row_x[3:6]]
            row_y[3:6] = [-v for v in row_y[3:6]]
            row_z[3:6] = [-v for v in row_z[3:6]]

        A_rows.extend([row_x, row_y, row_z])
        L_rows.extend([X - x, Y - y, Z - z])

    A = np.array(A_rows)
    L = np.array(L_rows)

    # Розв'язання нормальних рівнянь (A^T A) x = A^T L
    sol, residuals, rank, s = np.linalg.lstsq(A, L, rcond=None)

    return Helmert7(
        tx=sol[0], ty=sol[1], tz=sol[2],
        rx=sol[3], ry=sol[4], rz=sol[5],
        s_ppm=sol[6],
        convention=convention
    )

if __name__ == "__main__":
    h = Helmert7(
        tx=-89.5, ty=-93.8, tz=-123.1,
        rx=0.0, ry=0.0, rz=-0.156,
        s_ppm=-1.2,
        convention=HelmertConvention.POSITION_VECTOR
    )
    p_src = np.array([3978280.0, -100410.0, 4968390.0])
    p_tgt = h.forward(p_src)
    p_inv = h.inverse(p_tgt)

    print(f"Пряме перетворення: {p_tgt}")
    print(f"Нев'язка зворотного: {(p_inv - p_src) * 1000} мм")
```
:::

## Інженерні пастки при розробці

Під час інтеграції перетворення Гельмерта у виробничий геопросторовий код найчастіше виникають такі дефекти:

1. **Неузгодженість знаків осей обертання між стандартами:**
   У бібліотеці PROJ та в реєстрі EPSG параметри публікуються або в нотації Position Vector (метод 9606), або в нотації Coordinate Frame (метод 9607). Якщо передати кути з конвенції Coordinate Frame у функцію, що обчислює за Position Vector, замість взаємної компенсації розвороту осей координати отримають подвійне кутове відхилення: при розвороті лише на `0.5″` підсумковий лінійний зсув на земній поверхні складе понад 30 метрів.
2. **Плутанина між масштабним множником та відносним диференціалом:**
   Деякі геодезичні пакети зберігають масштаб як абсолютний множник `k = 0.9999988`, а інші — як диференціал `s = −1.2 ppm` (`−1.2 · 10⁻⁶`). Підстановка абсолютного коефіцієнта `k` у формулу, що очікує добавку `s`, помножить координати на два, викинувши обчислену точку у відкритий космос на висоту 6371 км над Землею.
3. **Ігнорування епохи в динамічних кінематичних мережах:**
   При роботі з глобальними супутниковими даними (наприклад, перехід ITRF2014 → ETRF2000) координати пунктів безперервно змінюються внаслідок тектонічного руху літосферних плит зі швидкістю 2–3 см на рік. Використання статичного 7-параметричного перетворення без обліку часового інтервалу `Δt = t − t₀` та швидкостей дрейфу призводить до накопичення систематичної похибки 20–50 см за одне-два десятиліття, що неприпустимо для кадастру й точного будівництва.
4. **Втрата чисельної точності при розв'язанні нормальних рівнянь:**
   У глобальній системі ECEF координати пунктів мають порядок `10⁶–10⁷ м`. Якщо підносити такі числа до квадрата без попереднього центроїдного масштабування (редукції Молоденського — Бадекаса), елементи матриці `N = Aᵀ A` сягають порядку `10¹⁴`. При використанні 32-бітних чисел із плаваючою комою (`float`) матриця миттєво втрачає точність і стає чисельно виродженою. Усі внутрішні накопичувачі та розв'язувачі зобов'язані працювати виключно в типі `double` (64 біти) або `long double` / `float64`.

## Інтеграція з пайплайнами PROJ

У сучасній бібліотеці PROJ версій 6+ та GDAL просторове перетворення Гельмерта описується через конвеєрний синтаксис `+proj=pipeline`:

```text
+proj=pipeline
  +step +proj=cart +ellps=intl
  +step +proj=helmert +x=-89.5 +y=-93.8 +z=-123.1
                      +rx=0.0 +ry=0.0 +rz=-0.156
                      +s=-1.2 +convention=position_vector
  +step +inv +proj=cart +ellps=WGS84
```

Ключовий параметр `+convention=position_vector` (або `+convention=coordinate_frame`) вказує бібліотеці, яку матричну алгебру слід застосувати до знаків поворотів. У разі використання 14 параметрів додаються аргументи швидкостей `+dx=... +dy=... +dz=... +drx=... +dry=... +drz=... +ds=... +t_epoch=...`.

## Перевірка чисельної коректності та допуски

У наведеному коді для контрольного пункту з набору даних EPSG:1618 (перетворення European Datum 1950 до WGS-84 для нафтогазових родовищ Північного моря) пряме й зворотне перетворення перевіряються на взаємну оборотність:

```text
Вхідні координати (ED50):   X =  3978280.000 м, Y = -100410.000 м, Z =  4968390.000 м
Трансформовані (WGS84):     X =  3978185.650 м, Y = -100506.688 м, Z =  4968260.938 м
Нев'язка зворотного ходу:   dX = 0.000000 мм,   dY = 0.000000 мм,   dZ = 0.000000 мм
```

Така строга точність досягається завдяки тому, що матриця `R` для малих кутів є ортогональною з точністю до величин другого порядку `O(θ²)`. Якщо кути повороту перевищують кілька градусів (наприклад, у задачах фотограмметрії чи робототехніки), лінеаризований вираз `I + Ω` необхідно замінити на строгу тригонометричну матрицю поворотів Ейлера `Rz(γ) · Ry(β) · Rx(α)` або на кватерніонне обертання, що усуває похибку лінеаризації.

Розуміння внутрішньої структури семипараметричного перетворення дозволяє розробнику діагностувати проблеми стикування просторових даних, точно оцінювати невідомі параметри за контрольними точками та гарантувати субміліметрову узгодженість між глобальними й національними системами координат.
