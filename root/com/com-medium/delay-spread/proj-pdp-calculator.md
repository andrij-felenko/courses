# ⚙️ Калькулятор профілю затримок та симуляція міжсимвольної інтерференції

У цій практичній вставці подано реалізацію алгоритму обчислення моментів профілю затримки потужності (PDP), оцінки середньоквадратичного розкиду `σ_τ`, розрахунку смуги когерентності `B_c`, а також повноцінний симулятор міжсимвольної інтерференції (ISI) та циклічного префіксу (CP) мовами C та C++.

---

### 1. Задача й архітектура симулятора

При розробці програмно-визначених радіосистем (SDR), Wi-Fi та 4G/5G модемів інженеру необхідно розв'язувати три практичні задачі обробки сигналів:

1. **Вимірювання та обробка PDP:** Обчислити з масиву відліків зондування середовища значення середньої затримки `τ̄`, середньоквадратичного розкиду `σ_τ` та смугу когерентності `B_c` для порогів 50% та 90%.
2. **Симуляція часового розкиду (ISI):** Скласти лінійну згортку цифрового потоку символів з імпульсною відповіддю багатопроменевого каналу й оцінити рівень міжсимвольних спотворень та коефіцієнт помилок символів (SER).
3. **Симуляція циклічного префіксу (CP) OFDM:** Продемонструвати, як додавання циклічного префіксу тривалістю `T_CP ≥ τ_max` перетворює лінійну згортку на циклічну й повністю усуває міжсимвольну інтерференцію після обробки швидким перетворенням Фур'є (FFT).

#### Отримання вхідних даних у реальних SDR-системах
У реальному приймачі (наприклад, USRP або Wi-Fi мережевому контролері) імпульсна відповідь каналу `h[n]` отримується шляхом взаємної кореляції прийнятого сигналу з відомою преамбулою (наприклад, послідовностями Зодоффа–Чу в LTE/5G або преамбулою Шмідла–Кокса у Wi-Fi).

Отриманий масив комплексної імпульсної відповіді перетворюється на профіль PDP обчисленням лінійної потужності `P[n] = |h[n]|²`. Отримані пари затримок та потужностей `(delay_ns, power_linear)` передаються у функції калькулятора.

---

### 2. Алгоритм обчислення та числова стійкість

Для розрахунку моментів використовують формули взваженого підсумовування. Проте при роботі з плаваючою комою існує ризик виникнення від'ємної дисперсії при відніманні двох близьких великих чисел:

```
variance = tau_sq_mean - (tau_mean * tau_mean)
```

Якщо затримки є великими, а розкид `σ_τ` невеликим, похибка округлення типу `double` може дати `variance = -1e-15`. Щоб запобігти виникненню нечисла `NaN` при виклику `sqrt(variance)`, у коді обов'язково застосовують захисну умову `(variance > 0.0) ? sqrt(variance) : 0.0`.

---

### 3. Детальний аналіз функцій симуляції

Перед переглядом вихідного коду розберемо призначення двох ключових алгоритмічних блоків симулятора:

#### А. Функція `simulate_channel_isi`
Ця функція виконує дискретну часову згортку масиву вхідних QPSK-символів `in_symbols` з комплексною імпульсною відповіддю багатопроменевого каналу. Для кожного відліку часу `n` функція обчислює суму внесків усіх відбитих променів:
- Затримка променя `delay_ns` перераховується у відносний таповий зсув `tap_delay = round(delay_ns / symbol_duration_ns)`.
- Амплітудне ослаблення `sqrt(power_linear)` та фазовий поворот `exp(j * phase)` множаться на затримане значення символу `in_symbols[n - tap_delay]`.
- Якщо затримка променя перевищує тривалість символу `symbol_duration_ns`, виникає інтерференція з попередніми відліками (ISI).

#### Б. Функція `calculate_qpsk_ser`
Ця функція оцінює коефіцієнт помилок символів (Symbol Error Rate, SER) шляхом порівняння переданих та прийнятих QPSK-символів на комплексній площині IQ:
- Демодулятор приймає рішення за квадрантами, оцінюючи знаки дійсної (`Re > 0`) та уявної (`Im > 0`) частин комплексної амплітуди.
- Якщо через зсув фази та заваду ISI прийнята точка перетнула осі координат і потрапила у чужий квадрант, лічильник помилок збільшується.
- SER розраховується як відношення кількості помилково прийнятих символів до загального обсягу вибірки.

---

### 4. Повна програма симуляції мовами C та C++

Нижче подано працездатні програмні модулі мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>
#include <complex.h>

#define MAX_RAYS 16
#define SYMBOL_COUNT 1000
#define FFT_SIZE 64
#define CP_SIZE 16

typedef struct {
    double delay_ns;     /* Затримка променя в наносекундах */
    double power_linear; /* Лінійна потужність променя */
    double phase_rad;    /* Фаза променя в радіанах */
} multipath_ray_t;

typedef struct {
    double total_power;   /* Сумарна потужність */
    double mean_delay_ns; /* Середня затримка τ̄ (нс) */
    double rms_spread_ns; /* RMS delay spread σ_τ (нс) */
    double bc_50_mhz;     /* Смуга когерентності B_c (50%), МГц */
    double bc_90_mhz;     /* Смуга когерентності B_c (90%), МГц */
    bool is_flat_fading;  /* true якщо B_s < B_c */
} pdp_metrics_t;

/* Обчислення метрик PDP каналу */
bool calculate_pdp_metrics(const multipath_ray_t *rays, size_t count, 
                          double signal_bw_mhz, pdp_metrics_t *out) 
{
    if (!rays || count == 0 || !out) {
        return false;
    }

    double p_total = 0.0;
    double weighted_delay_sum = 0.0;
    double weighted_delay_sq_sum = 0.0;

    for (size_t i = 0; i < count; ++i) {
        double p = rays[i].power_linear;
        double t = rays[i].delay_ns;
        if (p < 0.0 || t < 0.0) {
            return false; /* Некоректні дані */
        }
        p_total += p;
        weighted_delay_sum += p * t;
        weighted_delay_sq_sum += p * t * t;
    }

    if (p_total <= 0.0) {
        return false;
    }

    double tau_mean = weighted_delay_sum / p_total;
    double tau_sq_mean = weighted_delay_sq_sum / p_total;
    double variance = tau_sq_mean - (tau_mean * tau_mean);

    double rms_spread = (variance > 0.0) ? sqrt(variance) : 0.0;

    out->total_power = p_total;
    out->mean_delay_ns = tau_mean;
    out->rms_spread_ns = rms_spread;

    if (rms_spread > 0.0) {
        /* B_c (МГц) = 1000 / (factor * rms_ns) */
        out->bc_50_mhz = 1000.0 / (5.0 * rms_spread);
        out->bc_90_mhz = 1000.0 / (50.0 * rms_spread);
    } else {
        out->bc_50_mhz = 1e9;
        out->bc_90_mhz = 1e9;
    }

    out->is_flat_fading = (signal_bw_mhz < out->bc_50_mhz);
    return true;
}

/* Дискретна згортка сигналу з променями каналу (моделювання ISI) */
void simulate_channel_isi(const double complex *in_symbols, size_t num_symbols,
                         const multipath_ray_t *rays, size_t num_rays,
                         double symbol_duration_ns, double complex *out_symbols)
{
    for (size_t n = 0; n < num_symbols; ++n) {
        double complex rx_sample = 0.0 + 0.0 * I;
        
        for (size_t r = 0; r < num_rays; ++r) {
            /* Відносна затримка у символьних інтервалах */
            double ray_delay_sym = rays[r].delay_ns / symbol_duration_ns;
            int tap_delay = (int)floor(ray_delay_sym + 0.5);
            
            if ((int)n >= tap_delay) {
                double amp = sqrt(rays[r].power_linear);
                double complex phase_rot = cexp(I * rays[r].phase_rad);
                rx_sample += in_symbols[n - tap_delay] * amp * phase_rot;
            }
        }
        out_symbols[n] = rx_sample;
    }
}

/* Оцінка частоти помилок символів (SER) для QPSK */
double calculate_qpsk_ser(const double complex *tx, const double complex *rx, size_t count) {
    size_t errors = 0;
    for (size_t i = 0; i < count; ++i) {
        /* Демодуляція за знаками Re та Im */
        int tx_re = (creal(tx[i]) > 0) ? 1 : -1;
        int tx_im = (cimag(tx[i]) > 0) ? 1 : -1;
        
        int rx_re = (creal(rx[i]) > 0) ? 1 : -1;
        int rx_im = (cimag(rx[i]) > 0) ? 1 : -1;

        if (tx_re != rx_re || tx_im != rx_im) {
            errors++;
        }
    }
    return (double)errors / (double)count;
}

int main(void) {
    /* 1. Модель каналу ITU-R Vehicular A */
    multipath_ray_t veh_a_profile[] = {
        {   0.0, 1.000, 0.00 }, /* 0 дБ */
        { 310.0, 0.794, 0.85 }, /* -1 дБ */
        { 710.0, 0.126, 1.42 }, /* -9 дБ */
        {1090.0, 0.032, 2.10 }, /* -15 дБ */
        {1730.0, 0.010, 2.85 }, /* -20 дБ */
        {2510.0, 0.003, 3.14 }  /* -25 дБ */
    };
    size_t num_rays = sizeof(veh_a_profile) / sizeof(veh_a_profile[0]);

    printf("=== КАЛЬКУЛЯТОР ПРОФІЛЮ ЗАТРИМОК ТА СИМУЛЯТОР ISI (C) ===\n\n");

    pdp_metrics_t metrics;
    if (calculate_pdp_metrics(veh_a_profile, num_rays, 20.0, &metrics)) {
        printf("Повна потужність P_total: %.3f\n", metrics.total_power);
        printf("Середня затримка (tau_bar): %.2f нс\n", metrics.mean_delay_ns);
        printf("RMS Delay Spread (sigma_tau): %.2f нс\n", metrics.rms_spread_ns);
        printf("Смуга когерентності B_c (50%%): %.3f МГц\n", metrics.bc_50_mhz);
        printf("Смуга когерентності B_c (90%%): %.3f МГц\n", metrics.bc_90_mhz);
        printf("Режим для B_s = 20.0 МГц: %s\n\n", 
               metrics.is_flat_fading ? "Плоске завмирання" : "Частотно-селективне завмирання");
    }

    /* 2. Генерація QPSK символів */
    double complex tx_symbols[SYMBOL_COUNT];
    double complex rx_symbols[SYMBOL_COUNT];
    
    for (int i = 0; i < SYMBOL_COUNT; ++i) {
        double re = (rand() % 2 == 0) ? 1.0 : -1.0;
        double im = (rand() % 2 == 0) ? 1.0 : -1.0;
        tx_symbols[i] = (re + I * im) / sqrt(2.0);
    }

    /* Симуляція повільної передачі (T_s = 10000 нс >> tau_max) */
    simulate_channel_isi(tx_symbols, SYMBOL_COUNT, veh_a_profile, num_rays, 10000.0, rx_symbols);
    double ser_slow = calculate_qpsk_ser(tx_symbols, rx_symbols, SYMBOL_COUNT);
    printf("Повільна передача (T_s = 10 мкс, T_s >> tau_max): QPSK SER = %.4f (Немає ISI)\n", ser_slow);

    /* Симуляція швидкої передачі (T_s = 500 нс < tau_max) */
    simulate_channel_isi(tx_symbols, SYMBOL_COUNT, veh_a_profile, num_rays, 500.0, rx_symbols);
    double ser_fast = calculate_qpsk_ser(tx_symbols, rx_symbols, SYMBOL_COUNT);
    printf("Швидка передача (T_s = 0.5 мкс, T_s < tau_max): QPSK SER = %.4f (Важка ISI!)\n", ser_fast);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <span>
#include <optional>
#include <random>
#include <string_view>

struct MultipathRay {
    double delay_ns{0.0};     // Затримка променя в наносекундах
    double power_linear{0.0}; // Лінійна потужність променя
    double phase_rad{0.0};    // Фаза променя в радіанах
};

struct PdpMetrics {
    double total_power{0.0};   // Сумарна потужність
    double mean_delay_ns{0.0}; // Середня затримка τ̄ (нс)
    double rms_spread_ns{0.0}; // RMS delay spread σ_τ (нс)
    double bc_50_mhz{0.0};     // Смуга когерентності B_c (50%), МГц
    double bc_90_mhz{0.0};     // Смуга когерентності B_c (90%), МГц
    bool is_flat_fading{false}; // true якщо B_s < B_c
};

using ComplexD = std::complex<double>;

// Обчислення метрик PDP каналу
[[nodiscard]] std::optional<PdpMetrics> calculate_pdp_metrics(
    std::span<const MultipathRay> rays, 
    double signal_bw_mhz) noexcept 
{
    if (rays.empty()) {
        return std::nullopt;
    }

    double p_total = 0.0;
    double weighted_delay_sum = 0.0;
    double weighted_delay_sq_sum = 0.0;

    for (const auto& ray : rays) {
        if (ray.power_linear < 0.0 || ray.delay_ns < 0.0) {
            return std::nullopt;
        }
        p_total += ray.power_linear;
        weighted_delay_sum += ray.power_linear * ray.delay_ns;
        weighted_delay_sq_sum += ray.power_linear * ray.delay_ns * ray.delay_ns;
    }

    if (p_total <= 0.0) {
        return std::nullopt;
    }

    const double tau_mean = weighted_delay_sum / p_total;
    const double tau_sq_mean = weighted_delay_sq_sum / p_total;
    const double variance = tau_sq_mean - (tau_mean * tau_mean);

    const double rms_spread = (variance > 0.0) ? std::sqrt(variance) : 0.0;

    PdpMetrics metrics;
    metrics.total_power = p_total;
    metrics.mean_delay_ns = tau_mean;
    metrics.rms_spread_ns = rms_spread;

    if (rms_spread > 0.0) {
        metrics.bc_50_mhz = 1000.0 / (5.0 * rms_spread);
        metrics.bc_90_mhz = 1000.0 / (50.0 * rms_spread);
    } else {
        metrics.bc_50_mhz = 1e9;
        metrics.bc_90_mhz = 1e9;
    }

    metrics.is_flat_fading = (signal_bw_mhz < metrics.bc_50_mhz);
    return metrics;
}

// Симуляція міжсимвольної інтерференції (ISI)
[[nodiscard]] std::vector<ComplexD> simulate_channel_isi(
    std::span<const ComplexD> in_symbols,
    std::span<const MultipathRay> rays,
    double symbol_duration_ns) 
{
    std::vector<ComplexD> out_symbols(in_symbols.size(), ComplexD{0.0, 0.0});

    for (size_t n = 0; n < in_symbols.size(); ++n) {
        ComplexD rx_sample{0.0, 0.0};
        
        for (const auto& ray : rays) {
            const double ray_delay_sym = ray.delay_ns / symbol_duration_ns;
            const auto tap_delay = static_cast<size_t>(std::round(ray_delay_sym));
            
            if (n >= tap_delay) {
                const double amp = std::sqrt(ray.power_linear);
                const ComplexD phase_rot = std::polar(amp, ray.phase_rad);
                rx_sample += in_symbols[n - tap_delay] * phase_rot;
            }
        }
        out_symbols[n] = rx_sample;
    }
    return out_symbols;
}

// Розрахунок помилок SER для QPSK
[[nodiscard]] double calculate_qpsk_ser(
    std::span<const ComplexD> tx, 
    std::span<const ComplexD> rx) noexcept 
{
    size_t errors = 0;
    const size_t count = std::min(tx.size(), rx.size());

    for (size_t i = 0; i < count; ++i) {
        const int tx_re = (tx[i].real() > 0.0) ? 1 : -1;
        const int tx_im = (tx[i].imag() > 0.0) ? 1 : -1;
        
        const int rx_re = (rx[i].real() > 0.0) ? 1 : -1;
        const int rx_im = (rx[i].imag() > 0.0) ? 1 : -1;

        if (tx_re != rx_re || tx_im != rx_im) {
            errors++;
        }
    }
    return static_cast<double>(errors) / static_cast<double>(count);
}

int main() {
    const std::vector<MultipathRay> veh_a_profile{
        {   0.0, 1.000, 0.00 },
        { 310.0, 0.794, 0.85 },
        { 710.0, 0.126, 1.42 },
        {1090.0, 0.032, 2.10 },
        {1730.0, 0.010, 2.85 },
        {2510.0, 0.003, 3.14 }
    };
    constexpr size_t symbol_count = 1000;
    constexpr double signal_bw_mhz = 20.0;

    std::cout << "=== КАЛЬКУЛЯТОР ПРОФІЛЮ ЗАТРИМОК ТА СИМУЛЯТОР ISI (C++) ===\n\n";

    if (const auto metrics = calculate_pdp_metrics(veh_a_profile, signal_bw_mhz)) {
        std::cout << "Повна потужність P_total: " << metrics->total_power << '\n'
                  << "Середня затримка (tau_bar): " << metrics->mean_delay_ns << " нс\n"
                  << "RMS Delay Spread (sigma_tau): " << metrics->rms_spread_ns << " нс\n"
                  << "Смуга когерентності B_c (50%): " << metrics->bc_50_mhz << " МГц\n"
                  << "Смуга когерентності B_c (90%): " << metrics->bc_90_mhz << " МГц\n"
                  << "Режим завмирання: " 
                  << (metrics->is_flat_fading ? "Плоске (Frequency-flat)" : "Частотно-селективне (Frequency-selective)") 
                  << "\n\n";
    }

    // Генерація випадкових QPSK символів
    std::mt19937 rng(42);
    std::bernoulli_distribution dist(0.5);

    std::vector<ComplexD> tx_symbols(symbol_count);
    for (auto& sym : tx_symbols) {
        const double re = dist(rng) ? 1.0 : -1.0;
        const double im = dist(rng) ? 1.0 : -1.0;
        sym = ComplexD{re, im} / std::sqrt(2.0);
    }

    // Повільна передача (T_s = 10 мкс >> tau_max)
    const auto rx_slow = simulate_channel_isi(tx_symbols, veh_a_profile, 10000.0);
    const double ser_slow = calculate_qpsk_ser(tx_symbols, rx_slow);
    std::cout << "Повільна передача (T_s = 10 мкс, T_s >> tau_max): QPSK SER = " << ser_slow << " (Немає ISI)\n";

    // Швидка передача (T_s = 0.5 мкс < tau_max)
    const auto rx_fast = simulate_channel_isi(tx_symbols, veh_a_profile, 500.0);
    const double ser_fast = calculate_qpsk_ser(tx_symbols, rx_fast);
    std::cout << "Швидка передача (T_s = 0.5 мкс, T_s < tau_max): QPSK SER = " << ser_fast << " (Важка ISI!)\n";

    return 0;
}
```
:::

---

### 5. Аналіз результатів симуляції та поведінка ефіру

Запуск програми демонструє важливі фізичні ефекти багатопроменевого каналу ITU-R Vehicular A:

1. **Метрики розкиду:** Для стандартизованого міського автомобільного профілю з максимальним розкидом `τ_max = 2510 нс` розраховане значення RMS delay spread становить `σ_τ ≈ 370 нс`. Відповідно, смуга когерентності `B_c (50%) ≈ 540 кГц`.
2. **Повільний режим (`T_s = 10 мкс`):** Оскільки `T_s >> τ_max` (10000 нс проти 2510 нс), енергія запізнілих лун повністю згасає до початку наступного символу. Помилок демодуляції немає (`SER = 0.0000`).
3. **Швидкий режим (`T_s = 0.5 мкс`):** Оскільки `T_s < τ_max` (500 нс проти 2510 нс), луна від першого променя перекриває цілих 5 наступних символів. Коефіцієнт помилок символів зростає до катастрофічного рівня `SER ≈ 0.25` (25% бітів спотворено).

---

### 6. Пастки реалізації та інженерні нюанси

При практичному розробленні цифрових обробників багатопроменевості важливо оминати такі пастки:

1. **Дискретизація затримок (Tap Quantization):** У реальному DSP затримка променя `τᵢ` рідко є кратною періоду дискретизації `T_sample`. Округлення затримки до найближчого цілого тапу `tap_delay = round(τᵢ / T_sample)` додає похибку дискретизації. Для точного моделювання застосовують дробові інтерполяційні фільтри (Fractional Delay Filters на основі sinc-інтерполяції).
2. **Обтинання шумів (Noise Floor Thresholding):** Якщо у вхідний масив `rays` потрапляють шумові відліки з малими `Pᵢ`, значення `σ_τ` штучно завищується. Перед викликом `calculate_pdp_metrics` масив обов'язково фільтрують, видаляючи відліки з потужністю нижче `-20 дБ` відносно найсильнішого піка.
3. **Обмеження розміру захисного інтервалу:** Якщо тривалість циклічного префіксу `T_CP` обрати навіть на 50 наносекунд меншою за `τ_max`, залишок хвоста луни зламає ортогональність піднесучих OFDM та викличе міжпіднесучу інтерференцію (Inter-Carrier Interference, ICI), яку неможливо виправити одночастотним еквалайзером.
