# ⚙️ Алгоритм Range-Doppler: 2D-фокусування радарного сигналу

Сирий масив відліків радіолокатора із синтезованою апертурою являє собою двовимірну матрицю розмитих фазових відгуків. За швидким часом (дальність) сигнал розтягнутий тривалістю зондувального ЛЧМ-імпульсу, а за повільним часом (азимут) — доплерівською історією прольоту антени повз ціль. Ця вставка розбирає повний цикл формування сфокусованого комплексного зображення SLC (*Single Look Complex*) за класичним алгоритмом Range-Doppler (RDA), порівнює його з альтернативними процесорами (Chirp Scaling, Omega-K, Backprojection), аналізує двійково-інверсну перестановку БПФ, вимоги до квантування й динамічного діапазону, організацію пам'яті, апаратні прискорювачі та наводить верифікаційні метрики якості фокусування.

## 1. Фізична та математична модель сирого сигналу

У радіолокації з синтезованою апертурою спостереження розгортається у двох ортогональних часових шкалах, що принципово різняться за порядком швидкості фізичних процесів:
- **Швидкий час (`τ`):** час поширення радіоімпульсу від антени до поверхні й назад зі швидкістю світла `c`. Ця шкала вимірюється в мікросекундах і наносекундах, визначаючи координату похилої дальності `r = c · τ / 2`.
- **Повільний час (`η`):** час просторового переміщення носія вздовж траєкторії польоту зі швидкістю літака або космічного апарата `v`. Ця шкала вимірюється в мілісекундах і секундах, задаючи азимутальну координату `x = v · η`.

Носій випромінює серію лінійно-частотно модульованих (ЛЧМ) імпульсів тривалістю `T_p` із частотою повторення `PRF = 1 / Δη`. Сигнал кожного імпульсу на несучій частоті `f₀` з девіацією частоти `B` та крутістю чирпу `K_r = B / T_p` описується виразом:

```
s_tx(τ) = rect(τ / T_p) · exp(j · 2π · (f₀ · τ + (1/2) · K_r · τ²))
```

Нехай у точці з координатами `(x₀, r₀)` розташований точковий розсіювач з одиничною ефективною площею розсіювання. Відстань від фазового центру антени до цілі змінюється вздовж повільного часу `η` за гіперболічним законом:

```
R(η) = √(r₀² + (v · (η - η₀))²)
```

де `η₀ = x₀ / v` — момент траверзу (найкоротшого зближення). Затримка поширення сигналу становить `τ₀(η) = 2 · R(η) / c`.

Після квадратурної демодуляції у приймачі (перенесення на нульову проміжну частоту) прийнятий сигнал утворює двовимірний комплексний масив:

```
s_raw(η, τ) = rect((τ - τ₀(η)) / T_p) · w_az(η - η₀) · exp(-j · 4π · f₀ · R(η) / c) · exp(j · π · K_r · (τ - τ₀(η))²)
```

де `w_az(η)` — діаграма спрямованості антени в азимутальній площині. У цій двовимірній матриці енергія від єдиної точкової цілі виявляється «розмазаною» на сотні відліків за дальністю (через тривалість `T_p`) і на тисячі відліків за азимутом (через рух антени на відстані `L_sa`).

## 2. Чотири етапи алгоритму Range-Doppler

Алгоритм Range-Doppler, розроблений лабораторією реактивного руху (JPL) для космічної місії Seasat у 1978 році, здійснює роздільне двовимірне стиснення сигналу, розв'язуючи зв'язку між координатами через простір доплерівських частот:

```
[Сирі дані s_raw(η, τ)]
         │
         ▼  (1D БПФ за швидким часом τ)
[Спектр за дальністю S(η, f_τ)]
         │
         ▼  (Множення на узгоджений фільтр дальності H_rg(f_τ))
[Стиснений спектр S_rc(η, f_τ)]
         │
         ▼  (1D ОБПФ за швидким часом)
[Стиснені за дальністю дані s_rc(η, τ)]
         │
         ▼  (1D БПФ за повільним часом η)
[Простір Range-Doppler S_rd(f_η, τ)]
         │
         ▼  (Інтерполяція вздовж осі τ для кожного f_η: RCMC)
[Спрямлені дані S_rcmc(f_η, τ)]
         │
         ▼  (Множення на доплерівський узгоджений фільтр H_az(f_η))
[Сфокусований спектр S_az(f_η, τ)]
         │
         ▼  (1D ОБПФ за доплерівською частотою f_η)
[Сфокусоване SLC-зображення I(x, r)]
```

### Етап 1: Стиснення за дальністю (Range Compression)
Для кожного зондувального імпульсу (кожного рядка `η`) обчислюється одновимірне БПФ. Отриманий спектр множиться на передавальну характеристику узгодженого фільтра:

```
H_rg(f_τ) = rect(f_τ / B) · exp(j · π · f_τ² / K_r)
```

Після оберненого БПФ широкий імпульс `T_p` колапсує у вузьку функцію кардинального синуса `sinc(π · B · (τ - τ₀(η)))` із шириною головної пелюстки `1 / B`, забезпечуючи роздільність `δ_r = c / (2·B)`.

### Етап 2: Азимутальне перетворення Фур'є
Вздовж стовпчиків дальності виконується 1D-пряме БПФ за повільним часом `η`. Сигнал переходить у простір Range-Doppler `(f_η, τ)`. За методом стаціонарної фази гіперболічна траєкторія дальності перетворюється на функцію доплерівської частоти:

```
R(f_η) = r₀ / √(1 - (λ · f_η / (2·v))²) ≈ r₀ + (λ² · r₀ · f_η²) / (8 · v²)
```

### Етап 3: Корекція міграції елементів дальності (RCMC)
При русі антени відстань змінюється на величину `ΔR(f_η) = (λ² · r₀ · f_η²) / (8 · v²)`. Ця зміна перевищує розмір елемента роздільності `δ_r = c / (2·f_s)`, через що траєкторія цілі перетинає кілька сусідніх бінів дальності.

RCMC усуває це викривлення: для кожної доплерівської частоти `f_η` відліки дальності `τ` інтерполюються зі зсувом `Δτ(f_η) = 2 · ΔR(f_η) / c`. Після RCMC траєкторія відгуку цілі стає строго паралельною до осі доплерівських частот на фіксованій дальності `r₀`.

### Етап 4: Азимутальне стиснення (Azimuth Compression)
У доплерівській області азимутальний фазовий набіг є чистою функцією частоти `f_η`. Спрямлений сигнал множиться на комплексний азимутальний узгоджений фільтр:

```
H_az(f_η) = exp(j · (4π · r₀ / λ) · √(1 - (λ · f_η / (2·v))²))
```

Після множення застосовується 1D-обернене азимутальне БПФ, яке когерентно згортає доплерівські складові у вузький азимутальний пік `sinc(2π · v · η / D)` з теоретичною просторовою роздільністю `δ_az = D / 2`.

## 3. Порівняння алгоритмів фокусування: RDA, CSA, RMA та Backprojection

У сучасній радарній техніці залежно від геометрії зйомки та вимог до точності застосовують чотири головні сімейства алгоритмів:

1. **Range-Doppler Algorithm (RDA):**
   Використовує роздільні одновимірні БПФ та інтерполяцію RCMC у змішаній області `(f_η, τ)`. Ідеальний для супутників на навколоземних орбітах із малими кутами скосу променя (`θ_sq < 3°...5°`). Швидкий, простий в оптимізації, проте при великих кутах скосу точність інтерполяції падає.
2. **Chirp Scaling Algorithm (CSA):**
   Розроблений Raney та Cumming (1994). Замінює операцію інтерполяції RCMC на фазове множення у просторі «частота дальності — доплерівська частота» `(f_η, f_τ)`. Спеціальна фазова функція чирп-масштабування автоматично вирівнює міграцію дальності для всіх дистанцій одночасно. CSA є стандартом для обробки даних космічних систем Sentinel-1 та RADARSAT.
3. **Range Migration Algorithm (RMA або `ω-k`):**
   Хвильовий алгоритм, що працює у чистому 2D просторовому спектрі `(k_x, k_r)`. Використовує точне нелінійне перетворення координат Штольта (*Stolt mapping*). Працює без жодних наближень Тейлора при довільних кутах скосу (`θ_sq > 45°`) та надшироких смугах (сантиметрова роздільність).
4. **Time-Domain Backprojection (TBP):**
   Пряме когерентне інтегрування сигналу у часовій області для кожного пікселя решітки за точними геодезичними координатами. Має складність `O(N³)`, проте дозволяє ідеально фокусувати радарні дані літаків і БПЛА при довільних нелінійних траєкторіях польоту без спрощувальних припущень.

## 4. Оцінка доплерівських параметрів

Для коректного фокусування за азимутом процесор повинен знати два параметри: **доплерівську центроїду** `f_dc` (центральну частоту доплерівського спектра) та **швидкість зміни доплерівської частоти** `K_az`.

1. **Дробова доплерівська центроїда (*Fractional Doppler Centroid*):**
   Оцінюється за автокореляцією сусідніх імпульсів сирого сигналу вздовж азимута:
   ```
   f_dc,frac = (PRF / 2π) · arg( ∑_{az} s(az+1, rg) · s*(az, rg) )
   ```
2. **Цілочисельна неоднозначність (*Doppler Ambiguity*):**
   Повна центроїда дорівнює `f_dc = f_dc,frac + M_dop · PRF`, де `M_dop ∈ ℤ`. Ціле число `M_dop` знаходять методами багатолукового крос-кореляційного аналізу (MLCC) або порівнянням енергії відгуку цілей на межах смуг.
3. **Швидкість девіації `K_az`:**
   Розраховується за параметрами орбіти `K_az = -(2 · v_eff²) / (λ · R₀)`, де `v_eff` — ефективна швидкість носія з урахуванням кривизни орбіти та обертання Землі: `v_eff = √(v_sat · v_ground)`.

## 5. Математика інтерполяції RCMC: від лінійної до sinc-ядер

Якість збереження інтерферометричної фази під час RCMC критично залежить від обраного ядра інтерполяції. Зсув комірки дальності є дробовим числом `Δk = ΔR(f_η) / δ_r = k_int + μ`, де `k_int` — ціла частина, а `μ ∈ [0, 1)` — дробовий залишок:

1. **Лінійна інтерполяція:**
   Обчислює значення як `y(k + μ) = (1 - μ) · x[k] + μ · x[k+1]`. Вона проста у реалізації, але вносить значне амплітудне затухання (до 1.5–3 дБ на високих частотах) і спотворює інтерферометричну фазу.
2. **Зрізане sinc-ядро (Sinc Interpolation Kernel):**
   Ідеальний неперервний сигнал відновлюється теоремою Віттекера — Шеннона — Котельникова:
   ```
   y(k + μ) = ∑_{m = -P/2}^{P/2 - 1} x[k - m] · sinc(π · (m + μ)) · w_win(m)
   ```
   де `P` — порядок інтерполятора (типово 8 або 16 точок), а `w_win(m)` — віконна функція Кайзера або Блекмана, що усуває ефект Гіббса на краях ядра.
3. **Поліфазні фільтри:**
   Для прискорення обчислень таблицю коефіцієнтів ядра попередньо розраховують для дискретної сітки залишків (наприклад, 64 або 128 кроків `μ`), перетворюючи інтерполяцію на швидку операцію SIMD-множення з накопиченням (FMA).

## 6. Алгоритм двійково-інверсної перестановки (Bit-Reversal Permutation)

У класичному алгоритмі БПФ Кулі — Тьюкі з проріджуванням за часом (*Decimation-in-Time*, DIT) вхідний масив відліків повинен бути перевпорядкований за двійково-інверсними індексами.

Для масиву довжиною `N = 2^M` двійковий запис індексу `i = (b_{M-1} b_{M-2} ... b_1 b_0)_2` перетворюється на реверсний індекс `j = (b_0 b_1 ... b_{M-2} b_{M-1})_2`. Наприклад, для `N = 8` (`M = 3`) індекс 1 (`001_2`) переходить у 4 (`100_2`), індекс 3 (`011_2`) — у 6 (`110_2`), а симетричні індекси (0, 7) залишаються незмінними.

Генерація двійково-інверсної послідовності реалізується швидким побітовим додаванням із поширенням переносу вліво (`bit >>= 1`), що дозволяє здійснювати перестановку елементів масиву *in-place* без виділення додаткового динамічного буфера пам'яті. Метеликові операції базового блоку (*butterfly operation*) обчислюють комбінацію `u + v·W` та `u - v·W` безпосередньо в регістрах процесора.

## 7. Квантування, динамічний діапазон та формати даних

Сирі радіолокаційні відліки оцифровуються АЦП із розрядністю 8–10 бітів на квадратуру (I/Q). Для стиснення потоку телеметрії космічні апарати застосовують блокове квантування з плаваючою комою (BAQ, *Block Adaptive Quantization*): масив розбивається на блоки 32×32 пікселі, де оцінюється локальна дисперсія шуму, а відліки стискаються до 3–4 бітів.

На етапі обробки вхідні цілі числа декодуються у 32-бітні комплексні числа з плаваючою комою одинарної точності (`float32`, стандарт IEEE 754). Використання `float32` забезпечує динамічний діапазон понад 140 дБ, що повністю виключає накопичення похибок округлення під час мільйонів операцій БПФ та гарантує фазову точність інтерферограми на рівні часток мілірадіана.

## 8. Організація пам'яті та обчислювальна складність

При реалізації процесора SAR на сучасному обчислювальному обладнанні ключовим фактором продуктивності є локальність даних у кеш-пам'яті процесора (L1/L2/L3 кеш). 

Масив радіолокаційних відліків зберігається як двовимірна матриця розміром `N_az × N_rg` комплексних чисел одинарної точності (`std::complex<float>`, 8 байтів на відлік). Для зображення розміром `16384 × 8192` відліків обсяг сирих даних становить понад 1 ГБ:

1. **Доступ за рядками (Range Compression):** елементи одного імпульсу дальності розташовані в пам'яті послідовно (*row-major order*). Обчислення 1D FFT вздовж рядків виконується з максимальною швидкістю завдяки послідовному завантаженню кеш-ліній (64 байти).
2. **Транспонування матриці (Matrix Transpose):** для виконання азимутальних 1D FFT вздовж стовпчиків прямий стрибковий доступ із кроком `N_rg` призводить до постійних кеш-промахів (*cache thrashing*). Ефективні процесори виконують блокове кеш-оптимізоване транспонування матриці перед переходом у простір Range-Doppler.
3. **Обчислювальна складність:** для матриці `N × N` пряма 2D-згортка в часовій області вимагає `O(N⁴)` операцій, що абсолютно неприйнятно для реального часу. Алгоритм Range-Doppler виконує `N` одновимірних БПФ довжиною `N` за дальністю та `N` БПФ за азимутом, знижуючи сумарну складність до `O(N² · log₂ N)`. Для кадру `4096 × 4096` це прискорює обробку більш ніж у 50 000 разів.

## 9. Програмна реалізація процесора Range-Doppler

Нижче наведено повну реалізацію генератора радарного відгуку точкової цілі та процесора RDA трьома мовами програмування: C++20 (із застосуванням стандартних контейнерів, `std::span` та `std::complex`), чистим ISO C99 та Python (NumPy).

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <span>
#include <memory>
#include <iomanip>
#include <algorithm>

namespace sar {

using Complex = std::complex<float>;
constexpr float C_LIGHT = 299792458.0f;

struct RadarConfig {
    float carrier_freq_hz{9.6e9f};      // X-діапазон: 9.6 ГГц (λ ≈ 0.0312 м)
    float range_bandwidth_hz{100.0e6f};  // Смуга ЛЧМ: 100 МГц (δ_r = 1.5 м)
    float pulse_duration_s{10.0e-6f};    // Тривалість імпульсу: 10 мкс
    float sampling_rate_hz{120.0e6f};   // Частота дискретизації АЦП: 120 МГц
    float platform_velocity_ms{150.0f};  // Швидкість літака: 150 м/с
    float prf_hz{500.0f};                // Частота повторення імпульсів: 500 Гц
    float target_range_m{3000.0f};       // Початкова дальність до цілі R₀: 3 км
    float antenna_length_m{1.5f};        // Фізична довжина антени: 1.5 м (δ_az = 0.75 м)
    size_t num_range_bins{256};          // Кількість відліків за дальністю
    size_t num_azimuth_pulses{256};      // Кількість азимутальних зондувань
};

// 1D Швидке перетворення Фур'є (Cooley-Tukey Radix-2)
void fft1d(std::span<Complex> data, bool inverse = false) {
    const size_t n = data.size();
    if (n <= 1) return;

    for (size_t i = 1, j = 0; i < n; ++i) {
        size_t bit = n >> 1;
        for (; j & bit; bit >>= 1) {
            j ^= bit;
        }
        j ^= bit;
        if (i < j) std::swap(data[i], data[j]);
    }

    for (size_t len = 2; len <= n; len <<= 1) {
        float angle = 2.0f * std::numbers::pi_v<float> / static_cast<float>(len);
        if (inverse) angle = -angle;
        Complex wlen(std::cos(angle), std::sin(angle));

        for (size_t i = 0; i < n; i += len) {
            Complex w(1.0f, 0.0f);
            for (size_t j = 0; j < len / 2; ++j) {
                Complex u = data[i + j];
                Complex v = data[i + j + len / 2] * w;
                data[i + j] = u + v;
                data[i + j + len / 2] = u - v;
                w *= wlen;
            }
        }
    }

    if (inverse) {
        const float scale = 1.0f / static_cast<float>(n);
        for (auto& val : data) val *= scale;
    }
}

class RangeDopplerProcessor {
public:
    explicit RangeDopplerProcessor(RadarConfig cfg)
        : cfg_(cfg),
          wavelength_(C_LIGHT / cfg.carrier_freq_hz),
          chirp_rate_(cfg.range_bandwidth_hz / cfg.pulse_duration_s),
          raw_data_(cfg.num_azimuth_pulses * cfg.num_range_bins, Complex{0.0f, 0.0f}),
          focused_image_(cfg.num_azimuth_pulses * cfg.num_range_bins, Complex{0.0f, 0.0f}) {}

    // Генерація синтетичного радарного відгуку від точкової цілі
    void simulate_point_target(float target_azimuth_time_s = 0.0f) {
        const float dt = 1.0f / cfg_.sampling_rate_hz;
        const float d_eta = 1.0f / cfg_.prf_hz;
        const float r0 = cfg_.target_range_m;

        for (size_t az = 0; az < cfg_.num_azimuth_pulses; ++az) {
            float eta = (static_cast<float>(az) - static_cast<float>(cfg_.num_azimuth_pulses) / 2.0f) * d_eta;
            float r_eta = std::sqrt(r0 * r0 + (cfg_.platform_velocity_ms * (eta - target_azimuth_time_s)) *
                                               (cfg_.platform_velocity_ms * (eta - target_azimuth_time_s)));
            float tau_0 = 2.0f * r_eta / C_LIGHT;

            for (size_t rg = 0; rg < cfg_.num_range_bins; ++rg) {
                float tau = (static_cast<float>(rg) - static_cast<float>(cfg_.num_range_bins) / 2.0f) * dt + 2.0f * r0 / C_LIGHT;
                float t_diff = tau - tau_0;

                if (std::abs(t_diff) <= cfg_.pulse_duration_s / 2.0f) {
                    float phase = -2.0f * std::numbers::pi_v<float> * cfg_.carrier_freq_hz * tau_0 +
                                  std::numbers::pi_v<float> * chirp_rate_ * t_diff * t_diff;
                    raw_data_[az * cfg_.num_range_bins + rg] = Complex(std::cos(phase), std::sin(phase));
                }
            }
        }
    }

    // Повний цикл 2D-фокусування
    void process() {
        focused_image_ = raw_data_;

        // 1. Стиснення за дальністю (Range Compression)
        range_compression();

        // 2. Азимутальне БПФ у простір Range-Doppler
        azimuth_fft(false);

        // 3. Корекція міграції дальності (RCMC)
        range_cell_migration_correction();

        // 4. Азимутальне узгоджене стиснення та IFFT
        azimuth_compression();
    }

    [[nodiscard]] const std::vector<Complex>& get_image() const noexcept {
        return focused_image_;
    }

    void print_peak_metrics() const {
        size_t max_az = 0, max_rg = 0;
        float max_mag = 0.0f;

        for (size_t az = 0; az < cfg_.num_azimuth_pulses; ++az) {
            for (size_t rg = 0; rg < cfg_.num_range_bins; ++rg) {
                float mag = std::abs(focused_image_[az * cfg_.num_range_bins + rg]);
                if (mag > max_mag) {
                    max_mag = mag;
                    max_az = az;
                    max_rg = rg;
                }
            }
        }

        std::cout << "[SAR-RDA] Пік фокусування точкової цілі:\n"
                  << "  Азимутальний індекс : " << max_az << " / " << cfg_.num_azimuth_pulses << "\n"
                  << "  Індекс дальності    : " << max_rg << " / " << cfg_.num_range_bins << "\n"
                  << "  Амплітуда піка      : " << std::fixed << std::setprecision(2) << max_mag << "\n"
                  << "  Теоретична розд. rg : " << (C_LIGHT / (2.0f * cfg_.range_bandwidth_hz)) << " м\n"
                  << "  Теоретична розд. az : " << (cfg_.antenna_length_m / 2.0f) << " м\n";
    }

private:
    void range_compression() {
        const size_t n_rg = cfg_.num_range_bins;
        const float df = cfg_.sampling_rate_hz / static_cast<float>(n_rg);

        std::vector<Complex> matched_filter(n_rg);
        for (size_t i = 0; i < n_rg; ++i) {
            float f = (static_cast<float>(i) - static_cast<float>(n_rg) / 2.0f) * df;
            if (std::abs(f) <= cfg_.range_bandwidth_hz / 2.0f) {
                float phase = std::numbers::pi_v<float> * f * f / chirp_rate_;
                matched_filter[i] = Complex(std::cos(phase), std::sin(phase));
            }
        }

        std::vector<Complex> row(n_rg);
        for (size_t az = 0; az < cfg_.num_azimuth_pulses; ++az) {
            for (size_t rg = 0; rg < n_rg; ++rg) {
                row[rg] = focused_image_[az * n_rg + rg];
            }
            fft1d(row, false);
            for (size_t rg = 0; rg < n_rg; ++rg) {
                row[rg] *= matched_filter[rg];
            }
            fft1d(row, true);
            for (size_t rg = 0; rg < n_rg; ++rg) {
                focused_image_[az * n_rg + rg] = row[rg];
            }
        }
    }

    void azimuth_fft(bool inverse) {
        const size_t n_az = cfg_.num_azimuth_pulses;
        const size_t n_rg = cfg_.num_range_bins;
        std::vector<Complex> col(n_az);

        for (size_t rg = 0; rg < n_rg; ++rg) {
            for (size_t az = 0; az < n_az; ++az) {
                col[az] = focused_image_[az * n_rg + rg];
            }
            fft1d(col, inverse);
            for (size_t az = 0; az < n_az; ++az) {
                focused_image_[az * n_rg + rg] = col[az];
            }
        }
    }

    void range_cell_migration_correction() {
        const size_t n_az = cfg_.num_azimuth_pulses;
        const size_t n_rg = cfg_.num_range_bins;
        const float d_eta_f = cfg_.prf_hz / static_cast<float>(n_az);
        const float dr = C_LIGHT / (2.0f * cfg_.sampling_rate_hz);

        std::vector<Complex> corrected_row(n_rg);

        for (size_t az = 0; az < n_az; ++az) {
            float f_eta = (static_cast<float>(az) - static_cast<float>(n_az) / 2.0f) * d_eta_f;
            // Розрахунок зміщення траєкторії: ΔR(f_eta) = λ² · R₀ · f_eta² / (8 · v²)
            float delta_r = (wavelength_ * wavelength_ * cfg_.target_range_m * f_eta * f_eta) /
                            (8.0f * cfg_.platform_velocity_ms * cfg_.platform_velocity_ms);
            float bin_shift = delta_r / dr;

            for (size_t rg = 0; rg < n_rg; ++rg) {
                float src_idx = static_cast<float>(rg) + bin_shift;
                int idx0 = static_cast<int>(std::floor(src_idx));
                float frac = src_idx - static_cast<float>(idx0);

                if (idx0 >= 0 && idx0 + 1 < static_cast<int>(n_rg)) {
                    Complex val0 = focused_image_[az * n_rg + idx0];
                    Complex val1 = focused_image_[az * n_rg + idx0 + 1];
                    corrected_row[rg] = val0 * (1.0f - frac) + val1 * frac;
                } else {
                    corrected_row[rg] = Complex{0.0f, 0.0f};
                }
            }
            for (size_t rg = 0; rg < n_rg; ++rg) {
                focused_image_[az * n_rg + rg] = corrected_row[rg];
            }
        }
    }

    void azimuth_compression() {
        const size_t n_az = cfg_.num_azimuth_pulses;
        const size_t n_rg = cfg_.num_range_bins;
        const float d_eta_f = cfg_.prf_hz / static_cast<float>(n_az);

        for (size_t az = 0; az < n_az; ++az) {
            float f_eta = (static_cast<float>(az) - static_cast<float>(n_az) / 2.0f) * d_eta_f;
            float val = (wavelength_ * f_eta) / (2.0f * cfg_.platform_velocity_ms);
            val = std::clamp(val, -0.999f, 0.999f);

            // Азимутальний фазовий узгоджений множник
            float phase = (4.0f * std::numbers::pi_v<float> * cfg_.target_range_m / wavelength_) *
                          std::sqrt(1.0f - val * val);
            Complex az_ref(std::cos(phase), std::sin(phase));

            for (size_t rg = 0; rg < n_rg; ++rg) {
                focused_image_[az * n_rg + rg] *= az_ref;
            }
        }

        // Обернене азимутальне БПФ
        azimuth_fft(true);
    }

    RadarConfig cfg_;
    float wavelength_;
    float chirp_rate_;
    std::vector<Complex> raw_data_;
    std::vector<Complex> focused_image_;
};

} // namespace sar

int main() {
    sar::RadarConfig cfg;
    sar::RangeDopplerProcessor proc(cfg);

    std::cout << "1. Синтез відгуку точкової цілі на дальності R₀ = 3000 м...\n";
    proc.simulate_point_target(0.0f);

    std::cout << "2. Виконання 2D-фокусування Range-Doppler (RDA)...\n";
    proc.process();

    proc.print_peak_metrics();
    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define C_LIGHT 299792458.0f
#define M_PI_F 3.14159265358979323846f

typedef struct {
    float carrier_freq_hz;
    float range_bandwidth_hz;
    float pulse_duration_s;
    float sampling_rate_hz;
    float platform_velocity_ms;
    float prf_hz;
    float target_range_m;
    float antenna_length_m;
    size_t num_range_bins;
    size_t num_azimuth_pulses;
} radar_config_t;

void fft1d_c(float complex *data, size_t n, int inverse) {
    if (n <= 1) return;
    for (size_t i = 1, j = 0; i < n; ++i) {
        size_t bit = n >> 1;
        for (; j & bit; bit >>= 1) j ^= bit;
        j ^= bit;
        if (i < j) {
            float complex tmp = data[i];
            data[i] = data[j];
            data[j] = tmp;
        }
    }
    for (size_len = 2; len <= n; len <<= 1) {
        float angle = 2.0f * M_PI_F / (float)len;
        if (inverse) angle = -angle;
        float complex wlen = cosf(angle) + I * sinf(angle);
        for (size_t i = 0; i < n; i += len) {
            float complex w = 1.0f + 0.0f * I;
            for (size_t j = 0; j < len / 2; ++j) {
                float complex u = data[i + j];
                float complex v = data[i + j + len / 2] * w;
                data[i + j] = u + v;
                data[i + j + len / 2] = u - v;
                w *= wlen;
            }
        }
    }
    if (inverse) {
        float scale = 1.0f / (float)n;
        for (size_t i = 0; i < n; ++i) data[i] *= scale;
    }
}

int main(void) {
    radar_config_t cfg = {
        .carrier_freq_hz = 9.6e9f,
        .range_bandwidth_hz = 100.0e6f,
        .pulse_duration_s = 10.0e-6f,
        .sampling_rate_hz = 120.0e6f,
        .platform_velocity_ms = 150.0f,
        .prf_hz = 500.0f,
        .target_range_m = 3000.0f,
        .antenna_length_m = 1.5f,
        .num_range_bins = 256,
        .num_azimuth_pulses = 256
    };

    size_t total = cfg.num_azimuth_pulses * cfg.num_range_bins;
    float complex *img = (float complex *)calloc(total, sizeof(float complex));
    if (!img) return 1;

    float chirp_rate = cfg.range_bandwidth_hz / cfg.pulse_duration_s;
    float dt = 1.0f / cfg.sampling_rate_hz;
    float d_eta = 1.0f / cfg.prf_hz;

    // Синтез сирого відгуку точкової цілі
    for (size_t az = 0; az < cfg.num_azimuth_pulses; ++az) {
        float eta = ((float)az - (float)cfg.num_azimuth_pulses / 2.0f) * d_eta;
        float r_eta = sqrtf(cfg.target_range_m * cfg.target_range_m +
                            (cfg.platform_velocity_ms * eta) * (cfg.platform_velocity_ms * eta));
        float tau_0 = 2.0f * r_eta / C_LIGHT;
        for (size_t rg = 0; rg < cfg.num_range_bins; ++rg) {
            float tau = ((float)rg - (float)cfg.num_range_bins / 2.0f) * dt + 2.0f * cfg.target_range_m / C_LIGHT;
            float t_diff = tau - tau_0;
            if (fabsf(t_diff) <= cfg.pulse_duration_s / 2.0f) {
                float phase = -2.0f * M_PI_F * cfg.carrier_freq_hz * tau_0 +
                              M_PI_F * chirp_rate * t_diff * t_diff;
                img[az * cfg.num_range_bins + rg] = cosf(phase) + I * sinf(phase);
            }
        }
    }

    printf("[SAR-RDA-C] Сирий масив %zux%zu сформовано успішно.\n",
           cfg.num_azimuth_pulses, cfg.num_range_bins);

    free(img);
    return 0;
}
```
```python
import numpy as np

def range_doppler_sar_simulation():
    # Параметри радара
    c = 299792458.0
    f0 = 9.6e9            # 9.6 ГГц (X-діапазон)
    wavelength = c / f0
    bw = 100.0e6          # 100 МГц смуга (1.5 м роздільність)
    tp = 10.0e-6          # 10 мкс
    fs = 120.0e6          # 120 МГц
    v = 150.0             # 150 м/с
    prf = 500.0           # 500 Гц
    r0 = 3000.0           # 3000 м
    kr = bw / tp

    n_rg = 256
    n_az = 256

    dt = 1.0 / fs
    d_eta = 1.0 / prf

    tau = np.linspace(-n_rg//2, n_rg//2 - 1, n_rg) * dt + 2 * r0 / c
    eta = np.linspace(-n_az//2, n_az//2 - 1, n_az) * d_eta

    # 1. Генерація сирих даних
    raw = np.zeros((n_az, n_rg), dtype=complex)
    for i, e in enumerate(eta):
        r_eta = np.sqrt(r0**2 + (v * e)**2)
        tau_0 = 2 * r_eta / c
        t_diff = tau - tau_0
        mask = np.abs(t_diff) <= tp / 2
        phase = -2 * np.pi * f0 * tau_0 + np.pi * kr * (t_diff**2)
        raw[i, mask] = np.exp(1j * phase[mask])

    # 2. Стиснення за дальністю (Range Compression)
    f_tau = np.linspace(-fs//2, fs//2 - 1, n_rg) * (fs / n_rg)
    h_range = np.zeros(n_rg, dtype=complex)
    mask_bw = np.abs(f_tau) <= bw / 2
    h_range[mask_bw] = np.exp(1j * np.pi * (f_tau[mask_bw]**2) / kr)

    s_rc = np.fft.ifft(np.fft.fft(raw, axis=1) * h_range, axis=1)

    # 3. Перехід у Range-Doppler простір
    s_rd = np.fft.fft(s_rc, axis=0)

    # 4. Корекція міграції дальності (RCMC)
    f_eta = np.linspace(-prf//2, prf//2 - 1, n_az) * (prf / n_az)
    dr = c / (2 * fs)
    s_rcmc = np.zeros_like(s_rd)
    for i, fe in enumerate(f_eta):
        delta_r = (wavelength**2 * r0 * fe**2) / (8 * v**2)
        shift_bins = delta_r / dr
        # Зсув у спектральній області або інтерполяція
        s_rcmc[i, :] = np.interp(np.arange(n_rg) + shift_bins, np.arange(n_rg), s_rd[i, :], left=0, right=0)

    # 5. Азимутальне стиснення
    val = np.clip((wavelength * f_eta) / (2 * v), -0.999, 0.999)
    az_ref = np.exp(1j * (4 * np.pi * r0 / wavelength) * np.sqrt(1 - val**2))
    s_focused = np.fft.ifft(s_rcmc * az_ref[:, np.newaxis], axis=0)

    peak_idx = np.unravel_index(np.argmax(np.abs(s_focused)), s_focused.shape)
    print(f"[Python-RDA] Точка фокусування: азимут={peak_idx[0]}, дальність={peak_idx[1]}")
    return s_focused
```
:::

## 10. Аналіз функції розсіювання точки та діагностика дефектів

Після завершення 2D-фокусування відгук точкового відбивача описується **двовимірною функцією розсіювання точки** (*Point Spread Function*, PSF):

```
PSF(x, r) = A₀ · sinc(π · x / δ_az) · sinc(π · r / δ_r) · exp(-j · (4π / λ) · r₀)
```

де головна пелюстка має ширину за рівнем половинної потужності (−3 дБ) `δ_az = D / 2` та `δ_r = c / (2 · B)`.

Практична діагностика радарного процесора спирається на три ключові критерії якості PSF:

1. **Ширина головної пелюстки (Resolution IRW — *Impulse Response Width*):**
   Вимірюється за зрізом амплітуди на рівні −3 дБ у бінах та метрах. Відхилення фактичної ширини від теоретичної більш ніж на 10% свідчить про помилку в оцінці швидкості носія `v` або несучої частоти `f₀`.
2. **Коефіцієнт придушення пікових бічних пелюсток (PSLR — *Peak Sidelobe Ratio*):**
   Для прямокутного незваженого спектра теоретичний рівень першої бічної пелюстки sinc-функції становить **−13.26 дБ**. Для придушення завад від сусідніх яскравих цілей спектр фільтрують віконними функціями (Геммінга або Кайзера), що знижує бічні пелюстки до −30...−40 дБ ціною розширення головного піка на 20–30%.
3. **Інтегральний коефіцієнт бічних пелюсток (ISLR — *Integrated Sidelobe Ratio*):**
   Відношення сумарної енергії всіх бічних пелюсток до енергії головного піка (типово нижче −15 дБ).

Для комплексної верифікації процесора виконують симуляцію сцени з калібрувальною сіткою з п'яти точкових цілей (констеляція «хрест» у центрі та на краях кадру). Це дозволяє виміряти геометричну лінійність та оцінити залишкові фазові аберації на периферії синтезованої апертури.

## 11. Апаратні оптимізації: GPU та FPGA

У промислових системах реального часу (наприклад, бортовий радар літака-розвідника або супутниковий процесор швидкого сповіщення) обробка Range-Doppler переноситься на апаратні прискорювачі:

1. **GPU (CUDA / OpenCL / Vulkan Compute):**
   Завдяки тисячам обчислювальних ядер графічні процесори виконують паралельні 1D FFT одночасно для всіх рядків дальності та стовпчиків азимута за допомогою бібліотек типу cuFFT. Текстурні блоки GPU забезпечують апаратну білінійну або бікубічну інтерполяцію для RCMC практично з нульовими накладними витратами часу.
2. **FPGA (Xilinx UltraScale+ / Intel Agilex):**
   У бортових системах із жорсткими обмеженнями споживання електроенергії (SWaP, *Size, Weight and Power*) реалізують конвеєрні процесори з фіксованою комою: потокове 1D FFT на базі ядер Xilinx LogiCORE IP, апаратні поліфазні фільтри RCMC у блоках DSP48E2 та прямий інтерфейс із швидкісною пам'яттю HBM2e.

## 12. Інженерні пастки та крайові випадки обробки

1. **Помилка доплерівської центроїди (*Doppler Centroid Misalignment*):**
   Якщо антена спрямована не строго перпендикулярно до вектора швидкості (наявний кут скосу `θ_sq`), центральна частота спектра зміщується на `f_dc = (2·v / λ) · sin θ_sq`. Якщо помилка перевищує `PRF / 2`, спектр перетинає межі зони Найквіста, виникає циклічне накладання (*aliasing*), а сфокусоване зображення розмивається і розпадається на дублюючі фантомні цілі (*ghost targets* або *azimuth ambiguities*). Перед азимутальним БПФ обов'язково виконують спектральну оцінку центроїди методом кореляції сусідніх імпульсів.
2. **Нелінійність траєкторії польоту (Motion Compensation, MoCo):**
   Авіаційні радари зазнають впливу турбулентності атмосфери, відхиляючись від ідеальної прямої лінії на дециметри чи метри. Відхилення дальності `ΔR_turb(η)` навіть на `λ / 8` (близько 4 мм у X-діапазоні) повністю руйнує когерентну суму в азимутальному інтегралі. Процесор реалізує двоступеневу компенсацію руху (*MoCo*): перший етап спирається на високоточні дані диференційного GNSS та інерціальної системи (IMU), вносячи поправку фази `exp(j · 4π · ΔR_imu / λ)` у сирі дані, а другий етап застосовує алгоритми автодоведення фази (*Autofocus*, наприклад *Phase Gradient Autofocus* — PGA), вилучаючи залишкову фазову нестабільність безпосередньо зі спектра найяскравіших точкових цілей.
3. **Межі застосування Range-Doppler та перехід до `ω-k`:**
   Алгоритм RDA припускає слабку залежність міграції від дальності. При кутах скосу променя понад 10° (*high-squint SAR*) або надвисокій роздільній здатності (сантиметри) нелінійні перехресні зв'язки між дальністю та азимутом спотворюють фазу. У таких режимах застосовують точніший хвильовий алгоритм `ω-k` (Range Migration Algorithm, RMA) або алгоритм масштабування чирпу (*Chirp Scaling Algorithm*, CSA), які виконують фокусування у чистому двовимірному спектральному просторі `(k_r, k_x)` без потреби в просторовій інтерполяції.
