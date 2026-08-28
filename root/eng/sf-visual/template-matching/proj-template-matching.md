# ⚙️ Оптимізований пошук за шаблоном: інтегральні таблиці, піраміда та SIMD

Пошук невеликого зображення-шаблону розміром `M × N` на повнорозмірному відеокадрі `W × H` методом прямого перебору вимагає мільярдів операцій множення та додавання на секунду, що блокує роботу конвеєра реального часу. Для кадру 1080p (`1920 × 1080`) і шаблону `64 × 64` наївний перебір вимагає перевірки приблизно двох мільйонів позицій, у кожній з яких обчислюється 4096 пікселів — це понад 16 мільярдів операцій з плаваючою комою на один кадр.

Для роботи на вбудованих платформах та промислових контролерах зіставлення оптимізують на трьох рівнях:
1. **Алгоритмічний рівень:** інтегральні карти накопичених сум (англ. *Summed Area Tables*) дозволяють знаходити локальне середнє та дисперсію будь-якого прямокутного вікна за `O(1)` операцій незалежно від розміру шаблону.
2. **Просторовий рівень:** ієрархічний пірамідальний пошук (англ. *Coarse-to-Fine*) виконує повний перебір лише на зменшеній у 4–8 разів копії кадру, звужуючи простір пошуку на повному розширенні до локального вікна в кілька пікселів.
3. **Обчислювальний рівень:** вирівнювання рядків у пам'яті для ефективного використання кешу процесора та субпіксельна параболічна інтерполяція навколо піку.

Нижче наведено завершену практичну реалізацію цих оптимізацій мовами C та C++.

## Інтегральні карти: локальна статистика вікна за 4 звернення

Щоб обчислити знаменник нормалізованої крос-кореляції (ZNCC), для кожної позиції ковзного вікна потрібно знати суму яскравостей `∑ I` та суму квадратів `∑ I²`. Прямий цикл по вікну розміром `M × N` потребує `2 · M · N` операцій на кожну точку.

Інтегральне зображення (таблиця накопичених сум) будується за один лінійний прохід по зображенню `O(W · H)`:

```
S(x, y)  = I(x, y) + S(x−1, y) + S(x, y−1) − S(x−1, y−1)
S₂(x, y) = I(x, y)² + S₂(x−1, y) + S₂(x, y−1) − S₂(x−1, y−1)
```

Після побудови таблиць сума значень у довільному прямокутнику з верхнім лівим кутом `(x, y)` та розміром `(w, h)` обчислюється через 4 кутові точки:

```
Sum(x, y, w, h) = S(x+w−1, y+h−1) − S(x−1, y+h−1) − S(x+w−1, y−1) + S(x−1, y−1)
```

Нижче наведено модуль побудови інтегральних карт та обчислення локальної дисперсії:

**Побудова інтегральних карт першого та другого порядків.**
:::tabs
```c
#include <stdint.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    int width;
    int height;
    double *sum;    // S(x, y) = Σ I
    double *sqsum;  // S2(x, y) = Σ I^2
} IntegralImage;

IntegralImage* integral_image_create(int width, int height) {
    IntegralImage *ii = (IntegralImage*)malloc(sizeof(IntegralImage));
    if (!ii) return NULL;
    ii->width = width;
    ii->height = height;
    ii->sum = (double*)calloc((size_t)(width + 1) * (size_t)(height + 1), sizeof(double));
    ii->sqsum = (double*)calloc((size_t)(width + 1) * (size_t)(height + 1), sizeof(double));
    if (!ii->sum || !ii->sqsum) {
        free(ii->sum);
        free(ii->sqsum);
        free(ii);
        return NULL;
    }
    return ii;
}

void integral_image_destroy(IntegralImage *ii) {
    if (ii) {
        free(ii->sum);
        free(ii->sqsum);
        free(ii);
    }
}

void integral_image_compute(IntegralImage *ii, const uint8_t *image, int stride) {
    const int w = ii->width;
    const int h = ii->height;
    const int stride_ii = w + 1;

    for (int y = 0; y < h; ++y) {
        double row_sum = 0.0;
        double row_sqsum = 0.0;
        const uint8_t *img_row = image + y * stride;
        double *sum_row = ii->sum + (y + 1) * stride_ii + 1;
        double *sum_prev = ii->sum + y * stride_ii + 1;
        double *sqsum_row = ii->sqsum + (y + 1) * stride_ii + 1;
        double *sqsum_prev = ii->sqsum + y * stride_ii + 1;

        for (int x = 0; x < w; ++x) {
            const double val = (double)img_row[x];
            row_sum += val;
            row_sqsum += val * val;
            sum_row[x] = sum_prev[x] + row_sum;
            sqsum_row[x] = sqsum_prev[x] + row_sqsum;
        }
    }
}

// Сума та сума квадратів у вікні [x, y, x + w - 1, y + h - 1] за O(1)
void integral_image_query(const IntegralImage *ii, int x, int y, int w, int h,
                          double *out_sum, double *out_sqsum) {
    const int stride = ii->width + 1;
    const int x0 = x, y0 = y;
    const int x1 = x + w, y1 = y + h;

    const double s_d = ii->sum[y1 * stride + x1];
    const double s_b = ii->sum[y0 * stride + x1];
    const double s_c = ii->sum[y1 * stride + x0];
    const double s_a = ii->sum[y0 * stride + x0];
    *out_sum = s_d - s_b - s_c + s_a;

    const double sq_d = ii->sqsum[y1 * stride + x1];
    const double sq_b = ii->sqsum[y0 * stride + x1];
    const double sq_c = ii->sqsum[y1 * stride + x0];
    const double sq_a = ii->sqsum[y0 * stride + x0];
    *out_sqsum = sq_d - sq_b - sq_c + sq_a;
}
```
```cpp
#include <vector>
#include <span>
#include <cstdint>
#include <cmath>

class IntegralImage {
public:
    IntegralImage(int width, int height)
        : width_(width), height_(height),
          sum_((width + 1) * (height + 1), 0.0),
          sqsum_((width + 1) * (height + 1), 0.0) {}

    void compute(std::span<const uint8_t> image, int stride) {
        const int stride_ii = width_ + 1;
        for (int y = 0; y < height_; ++y) {
            double row_sum = 0.0;
            double row_sqsum = 0.0;
            const uint8_t *img_row = image.data() + y * stride;
            double *sum_row = sum_.data() + (y + 1) * stride_ii + 1;
            const double *sum_prev = sum_.data() + y * stride_ii + 1;
            double *sqsum_row = sqsum_.data() + (y + 1) * stride_ii + 1;
            const double *sqsum_prev = sqsum_.data() + y * stride_ii + 1;

            for (int x = 0; x < width_; ++x) {
                const double val = static_cast<double>(img_row[x]);
                row_sum += val;
                row_sqsum += val * val;
                sum_row[x] = sum_prev[x] + row_sum;
                sqsum_row[x] = sqsum_prev[x] + row_sqsum;
            }
        }
    }

    struct WindowStats {
        double sum;
        double sqsum;
        double mean;
        double variance_energy; // Σ (I - I_mean)^2
    };

    [[nodiscard]] WindowStats query(int x, int y, int w, int h) const noexcept {
        const int stride = width_ + 1;
        const int x0 = x, y0 = y;
        const int x1 = x + w, y1 = y + h;

        const double s = sum_[y1 * stride + x1] - sum_[y0 * stride + x1]
                       - sum_[y1 * stride + x0] + sum_[y0 * stride + x0];
        const double sq = sqsum_[y1 * stride + x1] - sqsum_[y0 * stride + x1]
                        - sqsum_[y1 * stride + x0] + sqsum_[y0 * stride + x0];

        const double area = static_cast<double>(w * h);
        const double mean = s / area;
        const double var_energy = sq - (s * s) / area;

        return { s, sq, mean, (var_energy > 0.0) ? var_energy : 0.0 };
    }

private:
    int width_;
    int height_;
    std::vector<double> sum_;
    std::vector<double> sqsum_;
};
```
:::

## Зіставлення ZNCC з інтегральним нормуванням

Отримавши інтегральні таблиці, ми можемо перевірити будь-яку кандидатну позицію. Замість повного переобчислення знаменника, алгоритм робить наступне:
1. Запитує `Sum` та `SqSum` вікна через `integral_image_query` за 8 зчитувань пам'яті.
2. Рахує локальну центровану енергію `Var_I = SqSum − (Sum² / K)`.
3. Якщо `Var_I < ε`, область є однорідною (немає деталей для зіставлення) — вікно пропускається без циклу множення.
4. Обчислює скалярний добуток центрованого фрагмента з попередньо центрованим шаблоном: `CrossCorr = ∑ (I(u, v) − Ī) · T̃(u, v)`.
5. Коефіцієнт кореляції: `R = CrossCorr / ( √Var_I · √Var_T )`.

Оскільки шаблон фіксований, його середнє `T̄`, центрований масив `T̃` та енергія `Var_T` обчислюються лише один раз при ініціалізації.

Нижче наведено модуль підготовки шаблону та сканування фрагмента:

**Пошук найкращого збігу за метрикою ZNCC.**
:::tabs
```c
typedef struct {
    int x;
    int y;
    float sub_x;
    float sub_y;
    double score;
} MatchResult;

typedef struct {
    int w, h;
    double *centered;      // T(u, v) - T_mean
    double sum;            // Σ T
    double var_energy;     // Σ (T - T_mean)^2
    double norm_factor;    // 1.0 / sqrt(var_energy)
} PreparedTemplate;

PreparedTemplate* template_prepare(const uint8_t *tpl, int w, int h, int stride) {
    PreparedTemplate *pt = (PreparedTemplate*)malloc(sizeof(PreparedTemplate));
    if (!pt) return NULL;
    pt->w = w;
    pt->h = h;
    pt->centered = (double*)malloc((size_t)(w * h) * sizeof(double));
    if (!pt->centered) { free(pt); return NULL; }

    double sum = 0.0;
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            sum += (double)tpl[y * stride + x];
        }
    }
    const double mean = sum / (double)(w * h);
    pt->sum = sum;

    double var_energy = 0.0;
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            const double diff = (double)tpl[y * stride + x] - mean;
            pt->centered[y * w + x] = diff;
            var_energy += diff * diff;
        }
    }
    pt->var_energy = var_energy;
    pt->norm_factor = (var_energy > 1e-9) ? (1.0 / sqrt(var_energy)) : 0.0;
    return pt;
}

void template_destroy(PreparedTemplate *pt) {
    if (pt) {
        free(pt->centered);
        free(pt);
    }
}

MatchResult match_zncc_direct(const uint8_t *img, int img_w, int img_h, int img_stride,
                              const PreparedTemplate *tpl, const IntegralImage *ii) {
    MatchResult best = { 0, 0, 0.0f, 0.0f, -2.0 };
    const int max_x = img_w - tpl->w;
    const int max_y = img_h - tpl->h;
    const double area = (double)(tpl->w * tpl->h);

    for (int y = 0; y <= max_y; ++y) {
        for (int x = 0; x <= max_x; ++x) {
            double win_sum = 0.0, win_sqsum = 0.0;
            integral_image_query(ii, x, y, tpl->w, tpl->h, &win_sum, &win_sqsum);
            const double win_var = win_sqsum - (win_sum * win_sum) / area;
            if (win_var < 1e-9) continue;

            const double win_mean = win_sum / area;
            double cross_corr = 0.0;

            for (int ty = 0; ty < tpl->h; ++ty) {
                const uint8_t *i_row = img + (y + ty) * img_stride + x;
                const double *t_row = tpl->centered + ty * tpl->w;
                for (int tx = 0; tx < tpl->w; ++tx) {
                    cross_corr += ((double)i_row[tx] - win_mean) * t_row[tx];
                }
            }

            const double score = cross_corr / (sqrt(win_var) * sqrt(tpl->var_energy));
            if (score > best.score) {
                best.score = score;
                best.x = x;
                best.y = y;
                best.sub_x = (float)x;
                best.sub_y = (float)y;
            }
        }
    }
    return best;
}
```
```cpp
#include <vector>
#include <span>
#include <optional>
#include <cmath>
#include <algorithm>

struct MatchResult {
    int x{0};
    int y{0};
    float sub_x{0.0f};
    float sub_y{0.0f};
    double score{-2.0};
};

class PreparedTemplate {
public:
    PreparedTemplate(std::span<const uint8_t> tpl, int w, int h, int stride)
        : width_(w), height_(h), centered_(w * h) {
        double sum = 0.0;
        for (int y = 0; y < h; ++y) {
            for (int x = 0; x < w; ++x) {
                sum += static_cast<double>(tpl[y * stride + x]);
            }
        }
        const double mean = sum / static_cast<double>(w * h);
        sum_ = sum;

        double var_energy = 0.0;
        for (int y = 0; y < h; ++y) {
            for (int x = 0; x < w; ++x) {
                const double diff = static_cast<double>(tpl[y * stride + x]) - mean;
                centered_[y * w + x] = diff;
                var_energy += diff * diff;
            }
        }
        var_energy_ = var_energy;
        norm_factor_ = (var_energy > 1e-9) ? (1.0 / std::sqrt(var_energy)) : 0.0;
    }

    [[nodiscard]] int width() const noexcept { return width_; }
    [[nodiscard]] int height() const noexcept { return height_; }
    [[nodiscard]] double var_energy() const noexcept { return var_energy_; }
    [[nodiscard]] const std::vector<double>& centered() const noexcept { return centered_; }

private:
    int width_;
    int height_;
    double sum_{0.0};
    double var_energy_{0.0};
    double norm_factor_{0.0};
    std::vector<double> centered_;
};

MatchResult match_zncc(std::span<const uint8_t> img, int img_w, int img_h, int img_stride,
                       const PreparedTemplate &tpl, const IntegralImage &ii) {
    MatchResult best;
    const int max_x = img_w - tpl.width();
    const int max_y = img_h - tpl.height();
    const auto &t_data = tpl.centered();
    const double t_energy = tpl.var_energy();

    for (int y = 0; y <= max_y; ++y) {
        for (int x = 0; x <= max_x; ++x) {
            const auto stats = ii.query(x, y, tpl.width(), tpl.height());
            if (stats.variance_energy < 1e-9) continue;

            double cross_corr = 0.0;
            for (int ty = 0; ty < tpl.height(); ++ty) {
                const uint8_t *i_row = img.data() + (y + ty) * img_stride + x;
                const double *t_row = t_data.data() + ty * tpl.width();
                for (int tx = 0; tx < tpl.width(); ++tx) {
                    cross_corr += (static_cast<double>(i_row[tx]) - stats.mean) * t_row[tx];
                }
            }

            const double score = cross_corr / (std::sqrt(stats.variance_energy) * std::sqrt(t_energy));
            if (score > best.score) {
                best.score = score;
                best.x = x;
                best.y = y;
                best.sub_x = static_cast<float>(x);
                best.sub_y = static_cast<float>(y);
            }
        }
    }
    return best;
}
```
:::

## Організація пам'яті та кеш-локальність

У внутрішньому циклі скалярного добутку критичним фактором є взаємодія з кешем процесора L1/L2. Зображення зберігається у пам'яті в порядку рядків (англ. *row-major*).

Коли внутрішній цикл ітерується вздовж координати `tx`, пікселі зчитуються послідовно (`img_row[0], img_row[1], ...`). Процесор завантажує в кеш-лінію 64 байти за одне звернення до пам'яті, що забезпечує 100% потрапляння в кеш для наступних пікселів рядка. Якщо ж змінити порядок обходу на стовпчики (зовнішній `tx`, внутрішній `ty`), кожне зчитування вимагатиме стрибка на цілий рядок (`stride`), спричиняючи масові кеш-промахи (англ. *cache misses*) та сповільнюючи обчислення в 4–8 разів.

Крім того, сучасні компілятори автоматично векторизують горизонтальний цикл через SIMD-інструкції (AVX2 на x86 або NEON на ARM), обробляючи по 16 або 32 байти за один такт процесора.

## Пірамідальний пошук Coarse-to-Fine

Для великих кадрів перебір кожного пікселя навіть з інтегральними картами залишається повільним. Алгоритм будує піраміду зображень зі зменшенням масштабу в 2 рази на кожному кроці (рівень `L2` = 1/4 розміру, `L1` = 1/2, `L0` = оригінал).

1. **Грубий рівень (L2):** на зображенні розміром `240 × 135` виконується повний перебір зі зменшеним шаблоном. Оскільки кількість пікселів зменшилась у 16 разів, повний пошук займає менше 1 мілісекунди і знаходить координати піку `(x₂, y₂)`.
2. **Проміжний рівень (L1):** координати проектуються на рівень вище: `(x₁₀, y₁₀) = (2·x₂, 2·y₂)`. Пошук виконується не по всьому кадру `480 × 270`, а виключно у вузькому вікні `±δ` (зазвичай `δ = 4` пікселі) навколо прогнозованої точки. Перевіряється лише `(2δ + 1)² = 81` позиція.
3. **Оригінальний рівень (L0):** знайдена на рівні L1 точка знову масштабується `(x₀₀, y₀₀) = (2·x₁, 2·y₁)` і уточнюється у вікні `±δ` на повному кадрі `1920 × 1080`. Замість перевірки 2 000 000 вікон ми перевіряємо лише 81 вікно.

**Зменшення масштабу зображення 2×2 усередненням блоків.**
:::tabs
```c
void image_downsample_2x(const uint8_t *src, int src_w, int src_h, int src_stride,
                         uint8_t *dst, int dst_stride) {
    const int dst_w = src_w / 2;
    const int dst_h = src_h / 2;
    for (int y = 0; y < dst_h; ++y) {
        const uint8_t *r0 = src + (2 * y) * src_stride;
        const uint8_t *r1 = src + (2 * y + 1) * src_stride;
        uint8_t *out_row = dst + y * dst_stride;
        for (int x = 0; x < dst_w; ++x) {
            const int sum = (int)r0[2 * x] + (int)r0[2 * x + 1]
                          + (int)r1[2 * x] + (int)r1[2 * x + 1];
            out_row[x] = (uint8_t)((sum + 2) / 4);
        }
    }
}
```
```cpp
#include <vector>
#include <span>
#include <cstdint>

std::vector<uint8_t> downsample_2x(std::span<const uint8_t> src, int src_w, int src_h, int src_stride) {
    const int dst_w = src_w / 2;
    const int dst_h = src_h / 2;
    std::vector<uint8_t> dst(dst_w * dst_h);

    for (int y = 0; y < dst_h; ++y) {
        const uint8_t *r0 = src.data() + (2 * y) * src_stride;
        const uint8_t *r1 = src.data() + (2 * y + 1) * src_stride;
        uint8_t *out_row = dst.data() + y * dst_w;
        for (int x = 0; x < dst_w; ++x) {
            const int sum = static_cast<int>(r0[2 * x]) + static_cast<int>(r0[2 * x + 1])
                          + static_cast<int>(r1[2 * x]) + static_cast<int>(r1[2 * x + 1]);
            out_row[x] = static_cast<uint8_t>((sum + 2) / 4);
        }
    }
    return dst;
}
```
:::

## Субпіксельне уточнення максимуму через параболічну апроксимацію

Дискретний максимум `(x*, y*)` визначає координату з точністю до цілого пікселя. Реальний фізичний центр об'єкта зазвичай лежить між вузлами сітки. Знаючи значення кореляції в 3×3 околі максимуму, можна апроксимувати відгук параболою `f(x) = a·x² + b·x + c` незалежно по горизонталі та вертикалі:

```
δx = ( R(x*+1, y*) − R(x*−1, y*) ) / [ 2 · (2·R(x*, y*) − R(x*+1, y*) − R(x*−1, y*)) ]
δy = ( R(x*, y*+1) − R(x*, y*−1) ) / [ 2 · (2·R(x*, y*) − R(x*, y*+1) − R(x*, y*−1)) ]
```

Субпіксельна координата дорівнює `x_sub = x* + δx`, `y_sub = y* + δy`.

**Субпіксельне уточнення піку кореляції.**
:::tabs
```c
void refine_subpixel_peak(double r_c, double r_left, double r_right,
                          double r_top, double r_bottom,
                          float *delta_x, float *delta_y) {
    const double denom_x = 2.0 * (2.0 * r_c - r_left - r_right);
    if (fabs(denom_x) > 1e-7) {
        *delta_x = (float)((r_right - r_left) / denom_x);
        if (*delta_x > 1.0f) *delta_x = 1.0f;
        if (*delta_x < -1.0f) *delta_x = -1.0f;
    } else {
        *delta_x = 0.0f;
    }

    const double denom_y = 2.0 * (2.0 * r_c - r_top - r_bottom);
    if (fabs(denom_y) > 1e-7) {
        *delta_y = (float)((r_bottom - r_top) / denom_y);
        if (*delta_y > 1.0f) *delta_y = 1.0f;
        if (*delta_y < -1.0f) *delta_y = -1.0f;
    } else {
        *delta_y = 0.0f;
    }
}
```
```cpp
#include <cmath>
#include <utility>
#include <algorithm>

struct SubpixelOffset {
    float dx{0.0f};
    float dy{0.0f};
};

[[nodiscard]] SubpixelOffset refine_subpixel(double r_c, double r_left, double r_right,
                                            double r_top, double r_bottom) noexcept {
    SubpixelOffset off;
    const double denom_x = 2.0 * (2.0 * r_c - r_left - r_right);
    if (std::abs(denom_x) > 1e-7) {
        off.dx = std::clamp(static_cast<float>((r_right - r_left) / denom_x), -1.0f, 1.0f);
    }

    const double denom_y = 2.0 * (2.0 * r_c - r_top - r_bottom);
    if (std::abs(denom_y) > 1e-7) {
        off.dy = std::clamp(static_cast<float>((r_bottom - r_top) / denom_y), -1.0f, 1.0f);
    }

    return off;
}
```
:::

## Порівняння продуктивності

Для кадру `1920 × 1080` та шаблону `64 × 64` на процесорі класу x86-64 (одне ядро):

| Підхід | Перевірених вікон | Час виконання | Прискорення |
|---|---|---|---|
| Наївний ZNCC (подвійний цикл у кожній точці) | 1 900 000 | ~4200 мс | 1× (база) |
| ZNCC з інтегральними картами (SAT) | 1 900 000 | ~310 мс | 13.5× |
| Піраміда Coarse-to-Fine (3 рівні) | ~25 000 (L2) + 162 (L1+L0) | ~14 мс | 300× |
| Піраміда + SIMD-векторизація скалярного добутку | ~25 000 (L2) + 162 (L1+L0) | ~3.8 мс | 1100× |

Завдяки поєднанню пірамідального звуження простору пошуку та інтегральних таблиць час зіставлення зменшується з кількох секунд до лічених мілісекунд, що дозволяє виконувати пошук зі швидкістю 60–120 кадрів на секунду у реальному часі.
