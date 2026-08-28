# ⚙️ Конвеєр усунення дисторсії та проекції камери

У системах комп'ютерного зору корекція геометрії зображення ділиться на дві принципово різні інженерні задачі:
1. **Точкова корекція (Sparse Point Undistortion)** — перетворення одиничних координат знайдених ключових точок (детектори кутів, маркери ArUco, центри зірок) із сирих пікселів кадру в нормовані промені погляду.
2. **Щільна ректифікація кадру (Dense Image Undistortion / Remap)** — розпрямлення всього растрового зображення для подальшого виводу на екран оператора, побудови панорам чи передачі в згорткові нейромережі.

Тут реалізовано повний цикл алгоритмів: пряму перспективну проекцію з дисторсією Брауна–Конраді, чисельну інверсію дисторсії для окремих точок (метод фіксованої точки) та побудову карт попередньо обчисленого зворотного відображення (Remap LUT) із субпіксельною білінійною інтерполяцією.

## 1. Структури даних камери та коефіцієнтів дисторсії

Збережемо внутрішні параметри K (f_x, f_y, c_x, c_y) та п'ять коефіцієнтів моделі Брауна–Конраді (k_1, k_2, p_1, p_2, k_3) у компактні структури:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

// Внутрішні параметри камери
typedef struct {
    double fx;      // фокусна відстань за віссю X (у пікселях)
    double fy;      // фокусна відстань за віссю Y (у пікселях)
    double cx;      // координата X головної точки (оптичного центру)
    double cy;      // координата Y головної точки (оптичного центру)
} CameraIntrinsics;

// Коефіцієнти дисторсії Брауна–Конраді
typedef struct {
    double k1, k2, k3;  // радіальна дисторсія
    double p1, p2;      // тангенціальна дисторсія
} DistortionCoeffs;

// Двовимірна точка
typedef struct {
    double x, y;
} Point2D;

// Тривимірна точка
typedef struct {
    double x, y, z;
} Point3D;
```
```cpp
#include <cstdint>
#include <cmath>
#include <vector>
#include <span>
#include <array>
#include <memory>
#include <algorithm>

namespace vision {

// Внутрішні параметри камери
struct CameraIntrinsics {
    double fx{0.0};     // фокусна відстань за віссю X (у пікселях)
    double fy{0.0};     // фокусна відстань за віссю Y (у пікселях)
    double cx{0.0};     // координата X головної точки
    double cy{0.0};     // координата Y головної точки
};

// Коефіцієнти дисторсії Брауна–Конраді
struct DistortionCoeffs {
    double k1{0.0};     // радіальний коефіцієнт 1
    double k2{0.0};     // радіальний коефіцієнт 2
    double k3{0.0};     // радіальний коефіцієнт 3
    double p1{0.0};     // тангенціальний коефіцієнт 1
    double p2{0.0};     // тангенціальний коефіцієнт 2
};

struct Point2D {
    double x{0.0};
    double y{0.0};
};

struct Point3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};
};

} // namespace vision
```
:::

## 2. Пряма проекція: від 3D точки до спотвореного пікселя

Прямий шлях повністю аналітичний і складається з чотирьох послідовних геометричних етапів:
1. **Перехід до нормованої площини:** точка P_c = (X_c, Y_c, Z_c) у системі координат камери ділиться на глибину Z_c. Якщо Z_c ≤ 0, точка лежить позаду оптичного центру і не може бути спроектована на сенсор.
2. **Обчислення радіального коефіцієнта масштабу:** розраховується квадрат радіуса r² = x² + y² та парні степені r⁴, r⁶. Радіальний множник масштабу дорівнює L(r) = 1 + k_1 r² + k_2 r⁴ + k_3 r⁶.
3. **Обчислення тангенціального зміщення:** зміщення через непаралельність лінз обчислюється як dx = 2 p_1 x y + p_2 (r² + 2 x²) та dy = p_1 (r² + 2 y²) + 2 p_2 x y.
4. **Перехід у піксельні координати:** спотворені нормовані координати масштабуються фокусними відстанями f_x, f_y та зміщуються головною точкою (c_x, c_y).

:::tabs
```c
// Пряма проекція 3D точки простору на сенсор камери
bool project_point(const Point3D *pt_cam,
                   const CameraIntrinsics *K,
                   const DistortionCoeffs *D,
                   Point2D *out_pixel) {
    if (pt_cam->z <= 1e-6) {
        return false; // точка позаду або в площині оптичного центру
    }

    // 1. Нормовані координати
    double x = pt_cam->x / pt_cam->z;
    double y = pt_cam->y / pt_cam->z;

    // 2. Радіальна відстань
    double r2 = x * x + y * y;
    double r4 = r2 * r2;
    double r6 = r4 * r2;

    // 3. Радіальний і тангенціальний зсув
    double radial = 1.0 + D->k1 * r2 + D->k2 * r4 + D->k3 * r6;
    double dx_tangential = 2.0 * D->p1 * x * y + D->p2 * (r2 + 2.0 * x * x);
    double dy_tangential = D->p1 * (r2 + 2.0 * y * y) + 2.0 * D->p2 * x * y;

    double x_distorted = x * radial + dx_tangential;
    double y_distorted = y * radial + dy_tangential;

    // 4. Переведення в пікселі
    out_pixel->x = K->fx * x_distorted + K->cx;
    out_pixel->y = K->fy * y_distorted + K->cy;
    return true;
}
```
```cpp
namespace vision {

// Пряма проекція 3D точки камери на сенсор
[[nodiscard]] constexpr bool project_point(const Point3D& pt_cam,
                                           const CameraIntrinsics& K,
                                           const DistortionCoeffs& D,
                                           Point2D& out_pixel) noexcept {
    if (pt_cam.z <= 1e-6) {
        return false;
    }

    const double x = pt_cam.x / pt_cam.z;
    const double y = pt_cam.y / pt_cam.z;

    const double r2 = x * x + y * y;
    const double r4 = r2 * r2;
    const double r6 = r4 * r2;

    const double radial = 1.0 + D.k1 * r2 + D.k2 * r4 + D.k3 * r6;
    const double dx_tangential = 2.0 * D.p1 * x * y + D.p2 * (r2 + 2.0 * x * x);
    const double dy_tangential = D.p1 * (r2 + 2.0 * y * y) + 2.0 * D.p2 * x * y;

    const double x_dist = x * radial + dx_tangential;
    const double y_dist = y * radial + dy_tangential;

    out_pixel.x = K.fx * x_dist + K.cx;
    out_pixel.y = K.fy * y_dist + K.cy;
    return true;
}

} // namespace vision
```
:::

## 3. Точкове розпрямлення: ітеративна інверсія моделі

Оскільки многочлен Брауна–Конраді має степінь 6 за радіусом (r⁶) або степінь 7 за координатами, аналітичного виразу для прямого знаходження ідеальних координат (x_n, y_n) зі спотворених (x_d, y_d) не існує. 

Для одиничних точок застосовують метод ітерацій фіксованої точки (Fixed-Point Iteration). За початкове наближення беруть спотворені координати x^(0) = x_d, y^(0) = y_d. На кожному кроці розраховують поточний коефіцієнт деформації та уточнюють координати діленням на отриманий радіальний масштаб.

Через те що коефіцієнти дисторсії в реальних об'єктивах є малими (|k_1| < 1, |p_1| < 0.01), оператор відображення є стискаючим (Contraction Mapping). Метод збігається експоненційно: кожна ітерація зменшує залишок похибки приблизно на порядок. П'ять ітерацій забезпечують субпіксельну точність до 10⁻⁹ пікселя, що повністю задовольняє вимоги прецизійної фотограмметрії.

:::tabs
```c
// Інверсія дисторсії для одиничного пікселя
Point2D undistort_point(const Point2D *distorted_pixel,
                        const CameraIntrinsics *K,
                        const DistortionCoeffs *D) {
    // 1. Початкове наближення в нормованих координатах
    double x_d = (distorted_pixel->x - K->cx) / K->fx;
    double y_d = (distorted_pixel->y - K->cy) / K->fy;

    double x = x_d;
    double y = y_d;

    // 2. Ітерації фіксованої точки
    for (int iter = 0; iter < 5; ++iter) {
        double r2 = x * x + y * y;
        double r4 = r2 * r2;
        double r6 = r4 * r2;

        double radial = 1.0 + D->k1 * r2 + D->k2 * r4 + D->k3 * r6;
        double dx_tan = 2.0 * D->p1 * x * y + D->p2 * (r2 + 2.0 * x * x);
        double dy_tan = D->p1 * (r2 + 2.0 * y * y) + 2.0 * D->p2 * x * y;

        // Поправка кроку
        x = (x_d - dx_tan) / radial;
        y = (y_d - dy_tan) / radial;
    }

    Point2D normalized_undistorted = { x, y };
    return normalized_undistorted;
}
```
```cpp
namespace vision {

// Ітеративне розпрямлення однієї точки
[[nodiscard]] Point2D undistort_point(const Point2D& dist_pixel,
                                      const CameraIntrinsics& K,
                                      const DistortionCoeffs& D,
                                      int max_iters = 5) noexcept {
    const double x_d = (dist_pixel.x - K.cx) / K.fx;
    const double y_d = (dist_pixel.y - K.cy) / K.fy;

    double x = x_d;
    double y = y_d;

    for (int i = 0; i < max_iters; ++i) {
        const double r2 = x * x + y * y;
        const double r4 = r2 * r2;
        const double r6 = r4 * r2;

        const double radial = 1.0 + D.k1 * r2 + D.k2 * r4 + D.k3 * r6;
        const double dx_tan = 2.0 * D.p1 * x * y + D.p2 * (r2 + 2.0 * x * x);
        const double dy_tan = D.p1 * (r2 + 2.0 * y * y) + 2.0 * D.p2 * x * y;

        x = (x_d - dx_tan) / radial;
        y = (y_d - dy_tan) / radial;
    }

    return Point2D{x, y};
}

} // namespace vision
```
:::

## 4. Генерація карт ректифікації Remap LUT

Для повного кадру розраховувати формули поліномів на кожному пікселі в реальному часі відеопотоку надто дорого. Для кадру Full HD (1920×1080) це вимагало б понад 2 мільйони обчислень степенів поліномів на кожен кадр (60 разів на секунду = 120 мільйонів нелінійних обчислень на секунду).

Вирішальна оптимізація полягає у **попередньому обчисленні карт відображення (Remap Look-Up Tables)**. Карти map_x[v, u] та map_y[v, u] генеруються **один раз** при старті системи через зворотне відображення (Inverse Mapping):
- Для кожного пікселя цільового розпрямленого зображення (u_dst, v_dst) обчислюються його ідеальні координати x = (u_dst - c_x)/f_x, y = (v_dst - c_y)/f_y.
- До цих координат застосовується **пряма аналітична формула дисторсії Брауна**.
- Отримані спотворені координати перетворюються на дійсні субпіксельні числа (u_src, v_src) і записуються в пам'ять масивів.

Розмір двох масивів `float` для Full HD кадру становить 1920 × 1080 × 4 байти × 2 = 16.6 МБ, що легко поміщається в оперативній пам'яті будь-якого вбудованого мікрокомп'ютера.

:::tabs
```c
// Таблиця попередньо обчислених координат
typedef struct {
    int width;
    int height;
    float *map_x; // розмір width * height
    float *map_y; // розмір width * height
} UndistortMap;

UndistortMap* create_undistort_map(int width, int height,
                                   const CameraIntrinsics *K_src,
                                   const DistortionCoeffs *D,
                                   const CameraIntrinsics *K_dst) {
    UndistortMap *map = (UndistortMap*)malloc(sizeof(UndistortMap));
    if (!map) return NULL;

    map->width = width;
    map->height = height;
    map->map_x = (float*)malloc(sizeof(float) * width * height);
    map->map_y = (float*)malloc(sizeof(float) * width * height);

    if (!map->map_x || !map->map_y) {
        free(map->map_x);
        free(map->map_y);
        free(map);
        return NULL;
    }

    // Для кожного вихідного пікселя (u_dst, v_dst) рахуємо, де він лежить у сирому кадрі
    for (int v_dst = 0; v_dst < height; ++v_dst) {
        for (int u_dst = 0; u_dst < width; ++u_dst) {
            // 1. Нормовані координати в новому зображенні
            double x = (u_dst - K_dst->cx) / K_dst->fx;
            double y = (v_dst - K_dst->cy) / K_dst->fy;

            // 2. Пряме застосування моделі дисторсії Брауна
            double r2 = x * x + y * y;
            double r4 = r2 * r2;
            double r6 = r4 * r2;

            double radial = 1.0 + D->k1 * r2 + D->k2 * r4 + D->k3 * r6;
            double dx_tan = 2.0 * D->p1 * x * y + D->p2 * (r2 + 2.0 * x * x);
            double dy_tan = D->p1 * (r2 + 2.0 * y * y) + 2.0 * D->p2 * x * y;

            double x_d = x * radial + dx_tan;
            double y_d = y * radial + dy_tan;

            // 3. Переведення у пікселі вихідного сирого кадру
            float u_src = (float)(K_src->fx * x_d + K_src->cx);
            float v_src = (float)(K_src->fy * y_d + K_src->cy);

            int idx = v_dst * width + u_dst;
            map->map_x[idx] = u_src;
            map->map_y[idx] = v_src;
        }
    }
    return map;
}

void free_undistort_map(UndistortMap *map) {
    if (map) {
        free(map->map_x);
        free(map->map_y);
        free(map);
    }
}
```
```cpp
namespace vision {

class ImageRemapper {
public:
    ImageRemapper(int width, int height,
                  const CameraIntrinsics& K_src,
                  const DistortionCoeffs& D,
                  const CameraIntrinsics& K_dst)
        : width_(width), height_(height),
          map_x_(width * height), map_y_(width * height) {
        build_lut(K_src, D, K_dst);
    }

    [[nodiscard]] int width() const noexcept { return width_; }
    [[nodiscard]] int height() const noexcept { return height_; }
    [[nodiscard]] std::span<const float> map_x() const noexcept { return map_x_; }
    [[nodiscard]] std::span<const float> map_y() const noexcept { return map_y_; }

private:
    int width_{0};
    int height_{0};
    std::vector<float> map_x_;
    std::vector<float> map_y_;

    void build_lut(const CameraIntrinsics& K_src,
                   const DistortionCoeffs& D,
                   const CameraIntrinsics& K_dst) {
        for (int v_dst = 0; v_dst < height_; ++v_dst) {
            for (int u_dst = 0; u_dst < width_; ++u_dst) {
                const double x = (u_dst - K_dst.cx) / K_dst.fx;
                const double y = (v_dst - K_dst.cy) / K_dst.fy;

                const double r2 = x * x + y * y;
                const double r4 = r2 * r2;
                const double r6 = r4 * r2;

                const double radial = 1.0 + D.k1 * r2 + D.k2 * r4 + D.k3 * r6;
                const double dx_tan = 2.0 * D.p1 * x * y + D.p2 * (r2 + 2.0 * x * x);
                const double dy_tan = D.p1 * (r2 + 2.0 * y * y) + 2.0 * D.p2 * x * y;

                const double x_d = x * radial + dx_tan;
                const double y_d = y * radial + dy_tan;

                const auto u_src = static_cast<float>(K_src.fx * x_d + K_src.cx);
                const auto v_src = static_cast<float>(K_src.fy * y_d + K_src.cy);

                const int idx = v_dst * width_ + u_dst;
                map_x_[idx] = u_src;
                map_y_[idx] = v_src;
            }
        }
    }
};

} // namespace vision
```
:::

## 5. Швидка білінійна ректифікація кадру

Операція застосування карти (Remap) виконує вибірку текстури:
1. За цілочисельними індексами (u_dst, v_dst) з таблиць зчитуються дійсні координати (sx, sy).
2. Обчислюється цілочисельний базовий піксель x_0 = floor(sx), y_0 = floor(sy) та його сусіди x_1 = x_0 + 1, y_1 = y_0 + 1.
3. Розраховуються дробові частки wx_1 = sx - x_0, wy_1 = sy - y_0 та їхні доповнення wx_0 = 1 - wx_1, wy_0 = 1 - wy_1.
4. Чотири пікселі вхідного зображення зважуються білінійною сумою:
   ```
   val = (p00·wx_0 + p01·wx_1)·wy_0 + (p10·wx_0 + p11·wx_1)·wy_1
   ```
5. Якщо координати (sx, sy) виходять за межі вхідного кадру, піксель заповнюється нулем (чорним кольором).

:::tabs
```c
// Ректифікація 8-бітного одноканального (сірого) кадру
void remap_bilinear_gray(const uint8_t *src_img,
                         int width, int height,
                         const UndistortMap *map,
                         uint8_t *dst_img) {
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            int idx = y * width + x;
            float sx = map->map_x[idx];
            float sy = map->map_y[idx];

            int x0 = (int)floorf(sx);
            int y0 = (int)floorf(sy);
            int x1 = x0 + 1;
            int y1 = y0 + 1;

            // Перевірка меж вхідного зображення
            if (x0 >= 0 && x1 < width && y0 >= 0 && y1 < height) {
                float wx1 = sx - (float)x0;
                float wx0 = 1.0f - wx1;
                float wy1 = sy - (float)y0;
                float wy0 = 1.0f - wy1;

                float p00 = (float)src_img[y0 * width + x0];
                float p01 = (float)src_img[y0 * width + x1];
                float p10 = (float)src_img[y1 * width + x0];
                float p11 = (float)src_img[y1 * width + x1];

                float val = (p00 * wx0 + p01 * wx1) * wy0 +
                            (p10 * wx0 + p11 * wx1) * wy1;

                dst_img[idx] = (uint8_t)(val + 0.5f);
            } else {
                dst_img[idx] = 0; // чорне тло за межами сенсора
            }
        }
    }
}
```
```cpp
namespace vision {

// Білінійна ректифікація кадру
void remap_bilinear_gray(std::span<const uint8_t> src_img,
                         int width, int height,
                         const ImageRemapper& remapper,
                         std::span<uint8_t> dst_img) {
    const auto map_x = remapper.map_x();
    const auto map_y = remapper.map_y();

    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            const int idx = y * width + x;
            const float sx = map_x[idx];
            const float sy = map_y[idx];

            const int x0 = static_cast<int>(std::floor(sx));
            const int y0 = static_cast<int>(std::floor(sy));
            const int x1 = x0 + 1;
            const int y1 = y0 + 1;

            if (x0 >= 0 && x1 < width && y0 >= 0 && y1 < height) {
                const float wx1 = sx - static_cast<float>(x0);
                const float wx0 = 1.0f - wx1;
                const float wy1 = sy - static_cast<float>(y0);
                const float wy0 = 1.0f - wy1;

                const float p00 = static_cast<float>(src_img[y0 * width + x0]);
                const float p01 = static_cast<float>(src_img[y0 * width + x1]);
                const float p10 = static_cast<float>(src_img[y1 * width + x0]);
                const float p11 = static_cast<float>(src_img[y1 * width + x1]);

                const float val = (p00 * wx0 + p01 * wx1) * wy0 +
                                  (p10 * wx0 + p11 * wx1) * wy1;

                dst_img[idx] = static_cast<uint8_t>(std::clamp(val + 0.5f, 0.0f, 255.0f));
            } else {
                dst_img[idx] = 0;
            }
        }
    }
}

} // namespace vision
```
:::

## 6. Підводні камені та пастки реалізації

1. **Неправильний вибір нової матриці камери K_dst:** Якщо для ректифікованого зображення взяти ту саму матрицю K_dst = K_src, бочкоподібна дисторсія після розпрямлення розширить краї зображення за межі кадру, відтявши частину поля зору (FOV). Щоб зберегти всі пікселі або прибрати чорні поля, використовують масштабування K_dst (параметр alpha в cv::getOptimalNewCameraMatrix): при alpha = 0 всі пікселі вихідного кадру валідні (чорні поля обрізані), при alpha = 1 зберігається все поле зору з чорними кутами.
2. **Низька швидкість розрахунку ділення на вбудованих платформах:** У циклах remap обчислення float ділення та виклики `floorf` замінюють на таблиці з фіксованою точкою Q8.8 або Q11.5. У форматі Q8.8 ціла частина числа отримується звичайним бітовим зсувом `sx >> 8`, а дробова частка для ваги — побітовим «І» `sx & 0xFF`, що дозволяє векторній інструкції SIMD (ARM NEON / AVX2) обробляти по 16 пікселів за такт.
3. **Крайові ефекти та захист пам'яті:** При білінійній вибірці на межі кадру x_1 = width спроба зчитати сусідній піксель викликає вихід за межі виділеної пам'яті (Buffer Overflow). Перевірка `x1 < width` та `y1 < height` є критично важливою для стабільності програми.
4. **Кеш-промахи (Cache Misses) при сильних деформаціях:** Для об'єктивів «риб'яче око» з кутом зору понад 150° вектор вибірки (sx, sy) на краях кадру швидко змінюється від рядка до рядка, спричиняючи нелокальні звернення до пам'яті вхідного зображення. Для оптимізації зображення розбивають на невеликі тайли (наприклад, 32×32 пікселі), які поміщаються в L1-кеш процесора.
