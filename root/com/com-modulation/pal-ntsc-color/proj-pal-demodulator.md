# ⚙️ Моделювання фазового маятника PAL та 1H лінії затримки мовами C та C++

Практичне розуміння переваг стандарту PAL над NTSC забезпечується програмним моделюванням повного тракту квадратурної модуляції, внеском фазової завади в канал зв'язку та цифровою демодуляцією за допомогою алгоритму 1H-лінії затримки.

### Повний обчислювальний тракт цифрової обробки відеосигналу

У системі цифрової обробки аналогового відео (DSP) композитний сигнал колірності `C(t)` дискретизується високошвидкісним аналогово-цифровим перетворювачем (АЦП / ADC). Для стандарту PAL з частотою колірної піднесучої `f[sc] = 4.43361875 МГц` оптимальною частотою дискретизації є `f[s] = 40 МГц`, що гарантує відсутність накладання спектрів (аліасингу) та забезпечує високу точність відновлення фази.

Математична симуляція моделює розгортку двох послідовних відеорядків (`N` та `N+1`). Кожен рядок складається з `1000` цифрових відліків яскравості `Y` та двох колірно-різницевих сигналів `U` та `V`.

Алгоритм виконує п'ять послідовних обчислювальних етапів:

1. **Генерація та нормування компонентів YUV.**
   Початкові кольори пікселів задаються у просторі `RGB` з діапазоном `[0.0, 1.0]`. Для дотримання вектору колірності здійснюється конвертація за фундаментальною матрицею EBU:
```
Y =  0.299·R + 0.587·G + 0.114·B         [сигнал яскравості]
U = -0.147·R - 0.289·G + 0.436·B         [колірне відхилення синього, 0.492·(B - Y)]
V =  0.615·R - 0.515·G - 0.100·B         [колірне відхилення червоного, 0.877·(R - Y)]
```

2. **Квадратурна модуляція піднесучої (QAM) та фазовий маятник.**
   Для кожного часового відліку `t = i / f[s]` обчислюється миттєве значення колірного сигналу піднесучої `C(t)`.
   - У системі NTSC фаза компоненти `V` залишається постійною для всіх рядків:
```
C_NTSC(t) = U·sin(2·π·f[sc]·t) + V·cos(2·π·f[sc]·t)
```
   - У системі PAL фаза компоненти `V` перевертається на `180°` на кожному другому рядку (інверсія знака перед `cos`):
```
C_N(t)   = U·sin(2·π·f[sc]·t) + V·cos(2·π·f[sc]·t)    [рядок N: пряма фаза +V]
C_N1(t)  = U·sin(2·π·f[sc]·t) - V·cos(2·π·f[sc]·t)    [рядок N+1: інверсна фаза -V]
```

3. **Моделювання спотворень у каналі зв'язку (Phase Noise / Differential Phase).**
   Під час поширення через радіоефір або довготривалий коаксіальний кабель високочастотна піднесуча зазнає фазового зсуву `Δφ` через зсув гетеродина або нелінійність підсилювачів. Симуляція додає сталий фазовий зсув `Δφ = +15°` до вхідних масивів відліків обох рядків:
```
C_rx(t) = C(t + Δφ / ω)                  [внесення фазового зсуву Δφ]
```

4. **Програмний декодер PAL на основі 1H буфера та матричних суматорів.**
   Для виділення компонентів `U` та `V` використовується кільцевий буфер пам'яті ОЗП розміром `1000` елементів, який виконує роль ультразвукової лінії затримки на один рядок (`64.0 мкс`).
   - **Сумування рядків:**
```
S_U[i] = 0.5 · (C_N[i] + C_N1[i])         [взаємне скасування V, виділення 2U·sin]
```
   - **Віднімання рядків:**
```
D_V[i] = 0.5 · (C_N[i] - C_N1[i])         [взаємне скасування U, виділення 2V·cos]
```
   Отримані розділені масиви надходять на квадратурні синхронні демодулятори, де множаться на опорні синусоїди `sin(2·π·f[sc]·t)` та `cos(2·π·f[sc]·t)` відповідно, з подальшим усредненням (цифровий ФНЧ-інтегратор).

5. **Зворотне матрицювання та аналіз похибки.**
   Відновлені значення `Y`, `U`, `V` перераховуються у вихідний простір `RGB`. Симуляція порівнює результат роботи прямих демодуляторів NTSC (де фазовий зсув `+15°` спотворює колір тону) та декодера PAL із лінією затримки (де фазовий зсув лише злегка зменшує насиченість на `cos(15°) ≈ 0.966`, повністю зберігаючи тон).

### Власні пастки та крайові випадки обробки

При реалізації цифрового декодера PAL необхідно враховувати три інженерні пастки:

1. **Зсув фази вибірок АЦП.**
   Якщо частота дискретизації `f[s]` не кратна точній частоті піднесучої `f[sc]`, фаза дискретизатора відносно синусоїди спалаху зміщується від рядка до рядка. Для уникнення накопичення фазової помилки в коді використовується точне числове накопичення кута `omega * t` з подвійною точністю (`double`).

2. **Дерегулювання тригера фазового маятника.**
   У реальних декодерах електронний ключ інверсії `V` може включитися в протифазі (інвертувати рядок `N` замість `N+1`). Симуляція в коді компенсує це суворим чергуванням знаків при відніманні рядків.

3. **Обмеження динамічного діапазону (Color Clipping).**
   Після демодуляції спотвореного сигналу значення `RGB` можуть вийти за межі допустимого діапазону `[0.0, 1.0]`. У коді застосовується захисне відсікання (`std::clamp` у C++ та умовні перевірки у C).

### Організація пам'яті та керування ресурсами у C та C++

Важливою відмінністю між двома мовними реалізаціями є підхід до виділення пам'яті під буфери відеорядків:

- **Реалізація мовою C.** Застосовує динамічне виділення пам'яті функцією `malloc()` у купі (heap). Обов'язковим інваріантом надійного коду є перевірка покажчика на `NULL` та звільнення пам'яті викликом `free()` перед виходом з функції `main()`. Для збереження сумісності з мікроконтролерними обчисленнями функції матицювання оголошено як `static inline`.
- **Реалізація мовою C++20.** Застосовує контейнер `std::vector<double>`, який забезпечує автоматичне керування ресурсами за принципом RAII (*Resource Acquisition Is Initialization*). Опрацювання масивів усередині методів декодування здійснюється через заголовок `std::span<const double>`, що уникає копіювання даних та гарантує захист від виходу за межі масиву без додаткових витрат продуктивності.

### Покроковий розбір коду симуляції

Код симулятора побудований за модульною схемою:

- **Структури `RgbColor` та `YuvColor`.** Утримують нормовані плаваючі значення компонентів.
- **Класи/функції матрицювання.** Здійснюють конвертацію між колірними просторами за коефіцієнтами стандарту EBU.
- **Генератор сигналів рядків.** Синтезує відліки з дискретизацією `40 МГц` та вносить фазовий зсув `phase_error_deg`.
- **Модуль демодуляції NTSC.** Помножує сигнал прямого рядка на синфазні та квадратурні синусоїди, обчислюючи інтегральне середнє за період рядка.
- **Модуль декодувальника PAL.** Виконує сумування та віднімання відліків двох рядків перед синхронним демодулюванням, показуючи точне відновлення вихідного відтінку.

### Реалізація симулятора мовами C та C++

Нижче подано паралельні працездатні реалізації моделі. Симуляція приймає тестовий тоновий вектор колірності шкіри (рожево-бежевий відтінок) і демонструє реконструйовані значення кольору RGB для NTSC та PAL при фазовому зсуві `+15°`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define SAMPLES_PER_LINE 1000
#define F_SUBCARRIER     4433618.75   /* Частота піднесучої PAL (Гц) */
#define SAMPLING_FREQ    40000000.0   /* Частота дискретизації 40 МГц */

typedef struct {
    double r, g, b;
} rgb_color_t;

typedef struct {
    double y, u, v;
} yuv_color_t;

/* Матрицювання RGB -> YUV */
static yuv_color_t rgb_to_yuv(rgb_color_t c) {
    yuv_color_t out;
    out.y =  0.299 * c.r + 0.587 * c.g + 0.114 * c.b;
    out.u = -0.147 * c.r - 0.289 * c.g + 0.436 * c.b; /* 0.492 * (B - Y) */
    out.v =  0.615 * c.r - 0.515 * c.g - 0.100 * c.b; /* 0.877 * (R - Y) */
    return out;
}

/* Зворотне матрицювання YUV -> RGB з обмеженням [0.0, 1.0] */
static rgb_color_t yuv_to_rgb(yuv_color_t c) {
    rgb_color_t out;
    double r = c.y + 1.140 * c.v;
    double b = c.y + 2.032 * c.u;
    double g = c.y - 0.395 * c.u - 0.581 * c.v;
    
    out.r = (r < 0.0) ? 0.0 : (r > 1.0) ? 1.0 : r;
    out.g = (g < 0.0) ? 0.0 : (g > 1.0) ? 1.0 : g;
    out.b = (b < 0.0) ? 0.0 : (b > 1.0) ? 1.0 : b;
    return out;
}

/* Моделювання демодуляції PAL та NTSC при наявності фазової помилки */
int main(void) {
    /* Вхідний тестовий колір (відтінок шкіри): R=0.85, G=0.60, B=0.50 */
    rgb_color_t orig_rgb = {0.85, 0.60, 0.50};
    yuv_color_t orig_yuv = rgb_to_yuv(orig_rgb);
    
    double phase_error_deg = 15.0;
    double phase_error_rad = phase_error_deg * M_PI / 180.0;
    
    double *line_N_chroma   = (double*)malloc(sizeof(double) * SAMPLES_PER_LINE);
    double *line_N1_chroma  = (double*)malloc(sizeof(double) * SAMPLES_PER_LINE);
    
    if (!line_N_chroma || !line_N1_chroma) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }

    double dt = 1.0 / SAMPLING_FREQ;
    double omega = 2.0 * M_PI * F_SUBCARRIER;

    /* 1. Модуляція та внесення фазової завади phase_error_rad */
    for (int i = 0; i < SAMPLES_PER_LINE; ++i) {
        double t = i * dt;
        /* Рядок N: +V компонента з фазовим зсувом */
        line_N_chroma[i]  = orig_yuv.u * sin(omega * t + phase_error_rad) +
                            orig_yuv.v * cos(omega * t + phase_error_rad);
        /* Рядок N+1: -V компонента у PAL (фазовий маятник) */
        line_N1_chroma[i] = orig_yuv.u * sin(omega * t + phase_error_rad) -
                            orig_yuv.v * cos(omega * t + phase_error_rad);
    }

    /* 2. Демодуляція NTSC (без лінії затримки, береться тільки один рядок N) */
    double ntsc_u_acc = 0.0, ntsc_v_acc = 0.0;
    for (int i = 0; i < SAMPLES_PER_LINE; ++i) {
        double t = i * dt;
        ntsc_u_acc += line_N_chroma[i] * 2.0 * sin(omega * t);
        ntsc_v_acc += line_N_chroma[i] * 2.0 * cos(omega * t);
    }
    yuv_color_t ntsc_yuv = {
        .y = orig_yuv.y,
        .u = ntsc_u_acc / SAMPLES_PER_LINE,
        .v = ntsc_v_acc / SAMPLES_PER_LINE
    };
    rgb_color_t ntsc_rgb = yuv_to_rgb(ntsc_yuv);

    /* 3. Демодуляція PAL з 1H лінією затримки (сумування та віднімання N та N+1) */
    double pal_u_acc = 0.0, pal_v_acc = 0.0;
    for (int i = 0; i < SAMPLES_PER_LINE; ++i) {
        double t = i * dt;
        /* Сумування двох рядків виділяє 2U, віднімання виділяє 2V */
        double u_signal = 0.5 * (line_N_chroma[i] + line_N1_chroma[i]);
        double v_signal = 0.5 * (line_N_chroma[i] - line_N1_chroma[i]);
        
        pal_u_acc += u_signal * 2.0 * sin(omega * t);
        pal_v_acc += v_signal * 2.0 * cos(omega * t);
    }
    yuv_color_t pal_yuv = {
        .y = orig_yuv.y,
        .u = pal_u_acc / SAMPLES_PER_LINE,
        .v = pal_v_acc / SAMPLES_PER_LINE
    };
    rgb_color_t pal_rgb = yuv_to_rgb(pal_yuv);

    /* 4. Вивід результатів порівняння */
    printf("=== СИМУЛЯЦІЯ ДЕМОДУЛЯЦІЇ (Фазова помилка каналу = %.1f deg) ===\n", phase_error_deg);
    printf("Оригінал RGB:   R=%.3f, G=%.3f, B=%.3f\n", orig_rgb.r, orig_rgb.g, orig_rgb.b);
    printf("NTSC декодер:   R=%.3f, G=%.3f, B=%.3f  [СПОРТВОРЕННЯ ТОНУ!]\n", ntsc_rgb.r, ntsc_rgb.g, ntsc_rgb.b);
    printf("PAL 1H декодер: R=%.3f, G=%.3f, B=%.3f  [ТОЧНИЙ КОЛІР!]\n", pal_rgb.r, pal_rgb.g, pal_rgb.b);

    free(line_N_chroma);
    free(line_N1_chroma);
    return 0;
}
```

```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <numbers>
#include <span>

namespace pal_sim {

struct RgbColor {
    double r{0.0};
    double g{0.0};
    double b{0.0};
};

struct YuvColor {
    double y{0.0};
    double u{0.0};
    double v{0.0};
};

class ColorConverter {
public:
    [[nodiscard]] static constexpr YuvColor to_yuv(const RgbColor& rgb) noexcept {
        return {
            .y =  0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b,
            .u = -0.147 * rgb.r - 0.289 * rgb.g + 0.436 * rgb.b,
            .v =  0.615 * rgb.r - 0.515 * rgb.g - 0.100 * rgb.b
        };
    }

    [[nodiscard]] static constexpr RgbColor to_rgb(const YuvColor& yuv) noexcept {
        const double r = std::clamp(yuv.y + 1.140 * yuv.v, 0.0, 1.0);
        const double b = std::clamp(yuv.y + 2.032 * yuv.u, 0.0, 1.0);
        const double g = std::clamp(yuv.y - 0.395 * yuv.u - 0.581 * yuv.v, 0.0, 1.0);
        return {.r = r, .g = g, .b = b};
    }
};

class PalDecoderSimulator {
private:
    static constexpr std::size_t kSamplesPerLine = 1000;
    static constexpr double kSubcarrierFreq = 4433618.75;
    static constexpr double kSamplingFreq   = 40000000.0;

public:
    void run_simulation(RgbColor target_color, double phase_error_deg) const {
        const double phase_error_rad = phase_error_deg * std::numbers::pi / 180.0;
        const YuvColor orig_yuv = ColorConverter::to_yuv(target_color);

        std::vector<double> line_N(kSamplesPerLine);
        std::vector<double> line_N1(kSamplesPerLine);

        const double dt = 1.0 / kSamplingFreq;
        const double omega = 2.0 * std::numbers::pi * kSubcarrierFreq;

        // Синтез двох рядків PAL з фазовим маятником та помилкою каналу
        for (std::size_t i = 0; i < kSamplesPerLine; ++i) {
            const double t = static_cast<double>(i) * dt;
            line_N[i]  = orig_yuv.u * std::sin(omega * t + phase_error_rad) +
                         orig_yuv.v * std::cos(omega * t + phase_error_rad);
            line_N1[i] = orig_yuv.u * std::sin(omega * t + phase_error_rad) -
                         orig_yuv.v * std::cos(omega * t + phase_error_rad);
        }

        // Демодуляція NTSC (без компенсації)
        const RgbColor ntsc_rgb = demodulate_ntsc(line_N, orig_yuv.y, omega, dt);

        // Демодуляція PAL (із 1H ультразвуковою лінією затримки)
        const RgbColor pal_rgb = demodulate_pal(line_N, line_N1, orig_yuv.y, omega, dt);

        print_results(target_color, ntsc_rgb, pal_rgb, phase_error_deg);
    }

private:
    [[nodiscard]] RgbColor demodulate_ntsc(std::span<const double> line, double luma,
                                            double omega, double dt) const {
        double u_acc = 0.0;
        double v_acc = 0.0;
        for (std::size_t i = 0; i < line.size(); ++i) {
            const double t = static_cast<double>(i) * dt;
            u_acc += line[i] * 2.0 * std::sin(omega * t);
            v_acc += line[i] * 2.0 * std::cos(omega * t);
        }
        const YuvColor yuv{
            .y = luma,
            .u = u_acc / static_cast<double>(line.size()),
            .v = v_acc / static_cast<double>(line.size())
        };
        return ColorConverter::to_rgb(yuv);
    }

    [[nodiscard]] RgbColor demodulate_pal(std::span<const double> line_N,
                                           std::span<const double> line_N1,
                                           double luma, double omega, double dt) const {
        double u_acc = 0.0;
        double v_acc = 0.0;
        for (std::size_t i = 0; i < line_N.size(); ++i) {
            const double t = static_cast<double>(i) * dt;
            // Ультразвукова лінія затримки 1H + матричний суматор/віднімач
            const double u_sig = 0.5 * (line_N[i] + line_N1[i]);
            const double v_sig = 0.5 * (line_N[i] - line_N1[i]);

            u_acc += u_sig * 2.0 * std::sin(omega * t);
            v_acc += v_sig * 2.0 * std::cos(omega * t);
        }
        const YuvColor yuv{
            .y = luma,
            .u = u_acc / static_cast<double>(line_N.size()),
            .v = v_acc / static_cast<double>(line_N.size())
        };
        return ColorConverter::to_rgb(yuv);
    }

    void print_results(const RgbColor& orig, const RgbColor& ntsc,
                        const RgbColor& pal, double phase_error_deg) const {
        std::cout << "=== C++20 СИМУЛЯЦІЯ ДЕМОДУЛЯЦІЇ (Фазова помилка = "
                  << phase_error_deg << " deg) ===\n"
                  << "Оригінал RGB:   R=" << orig.r << ", G=" << orig.g << ", B=" << orig.b << "\n"
                  << "NTSC декодер:   R=" << ntsc.r << ", G=" << ntsc.g << ", B=" << ntsc.b
                  << "  [СПОРТВОРЕННЯ ТОНУ!]\n"
                  << "PAL 1H декодер: R=" << pal.r << ", G=" << pal.g << ", B=" << pal.b
                  << "  [ТОЧНИЙ КОЛІР!]\n";
    }
};

} // namespace pal_sim

int main() {
    const pal_sim::PalDecoderSimulator simulator;
    /* Тестовий відтінок шкіри */
    simulator.run_simulation({.r = 0.85, .g = 0.60, .b = 0.50}, 15.0);
    return 0;
}
```
:::
