# ⚙️ Алгоритм вимірювання смуги 3 dB та 99% OBW за цифровим спектром

Ця практична вставка детально розбирає алгоритм обчислення смуги пропускання за рівнем половинної потужності (-3 дБ) та 99% зайнятої смуги (англ. *Occupied Bandwidth*, OBW) за допомогою дискретного аналізу спектральної щільності потужності (PSD).

Приклад розроблено у двох ідіоматичних варіантах — мовами C та C++20. Обидві реалізації містять дробову інтерполяцію між бінами БПФ для усунення дискретизаційної похибки сітки, а також обчислення кумулятивної інтегральної функції потужності для відповідності міжнародному стандарту ITU-R SM.443.

## 1. Навіщо потрібне автоматичне вимірювання смуги у коді

У сучасних системах цифрового радіозв'язку (SDR), спектроаналізаторах, автоматизованих комплексах радіоконтролю та кодеках вимірювання смуги виконується в режимі реального часу. Отримання точного значення смуги необхідно для вирішення наступних практичних завдань:

* **Контроль позасмугових випромінювань (ITU OBW):** Перевірка відповідності випромінювання передавача ліцензійним обмеженням ефіру (наприклад, визначення 99% зайнятої смуги для Wi-Fi або LTE каналу).
* **Автоматична переналастройка фільтрів (Adaptive Channel Filtering):** Налаштування цифрового FIR/IIR фільтра низьких частот у приймачі під реальну ширину спектра прийшовши сигналу для максимального придушення шумів.
* **Оцінка швидкості символів (Symbol Rate Estimation):** Визначення тактової частоти дискретизації модульованого сигналу без знання попередніх параметрів протоколу (сліпа ідентифікація сигналу).

## 2. Попередня обробка сигналу та усереднення за методом Уелча

Перед викликом процедури вимірювання смуги вхідний цифровий потік відліків `x[n]` АЦП проходе попередню спектральну обробку. Щоб зменшити дисперсію шумових флуктуацій і отримати стабільне оцінювання АЧХ, застосовують усереднення періодограм за методом Уелча (Welch's Method):

1. **Сегментація потоку:** Вхідний сигнал ділиться на `K` перекривних кадри довжиною `M` відліків кожен (з перекриттям 50% або 75%).
2. **Віконне зважування:** Кожен кадр множиться на віконну функцію `w[n]` (наприклад, вікно Ганна), щоб придушити розтікання спектра через розриви на межах кадру.
3. **Обчислення БПФ та усереднення:** Для кожного кадру обчислюється комплексне БПФ `X_k[i]`, після чого виконується усереднення квадратів модулів по всіх `K` кадрах:
   ```
   PSD[i] = (1 / (K · U · M)) · ∑_{k=1}^{K} |X_k[i]|^2
   ```
   Де `U = (1 / M) · ∑_{n=0}^{M-1} w[n]^2` — нормувальна потужність віконної функції.

Отриманий масив `PSD[i]` передається у функцію вимірювання смуги `estimate_bandwidth()`.

## 3. Математична структура алгоритму вимірювання

Алгоритм приймає на вхід масив дискретних значень спектральної щільності потужності `psd[i]` (де `i = 0..N-1`), стартову частоту `f_start` (Гц) та крок частотної сітки `df = f_s / N` (Гц/бін). Обчислення розбито на чотири логічні етапи.

### Етап 1: Знаходження піку та інтегрування повної потужності

На першому проході алгоритм обчислює загальну інтегральну потужність спектра `P_total` та шукає максимальне значення потужності `P_max` разом із його індексом `idx_max`:

```
P_total = ∑_{i=0}^{N-1} psd[i]
P_max = max(psd[i]),   idx_max = argmax(psd[i])
```

Якщо `P_max ≤ 0` або сумарна потужність дорівнює нулю, спектр вважається порожнім, і алгоритм повертає помилку.

### Етап 2: Пошук меж -3 дБ із лінійною інтерполяцією

Рівень половинної потужності відповідає значенням `P_3dB = P_max / 2.0` (що становить точно -3.01 дБ у логарифмічному масштабі). Якщо просто шукати найближчі біни БПФ, дискретність частотної сітки `df` створить систематичну похибку вимірювання до `±df / 2`.

Для досягнення суб-бінової точності алгоритм шукає сусідні біни `psd[i-1]` та `psd[i]`, між якими проходить пороговий рівень `P_3dB`, і виконує лінійну інтерполяцію:

```
frac = (P_3dB - psd[i-1]) / (psd[i] - psd[i-1])
idx_interp = (i - 1) + frac
f_3dB = f_start + idx_interp · df
```

Верхня межа теоретичної похибки вимірювання частоти при лінійній інтерполяції обмежена другою похідною спектральної кривої:

```
E_freq <= (df^2 / 8) · |d²(PSD) / df²|
```

Це дозволяє точно вимірювати смугу навіть при невеликій кількості бінів БПФ (наприклад, `N = 512` або `1024`).

### Етап 3: Обчислення 99% зайнятої смуги (OBW) за кумулятивною сумою

Згідно зі стандартом ITU-R SM.443, 99% зайнята смуга визначається частотними межами `[f_low_obw, f_high_obw]`, між якими зосереджено 99% сумарної потужності `P_total`.

Алгоритм обчислює кумулятивну суму елементів `cumsum[i]` і знаходить перші індекси, для яких виконуються умови:

* **Нижня границя (0.5% потужності):** перший індекс `i_low`, де `cumsum[i_low] ≥ 0.005 · P_total`.
* **Верхня границя (99.5% потужності):** перший індекс `i_high`, де `cumsum[i_high] ≥ 0.995 · P_total`.

Ширина зайнятої смуги становить `BW_99 = (i_high - i_low) · df`.

### Етап 4: Обробка крайніх випадків (Edge Cases)

Алгоритм коректно обробляє наступні крайові ситуації:
1. **Сигнал на межі сітки (DC або Nyquist):** якщо пік знаходиться на крайніх бінах, інтерполяція затискається в межах масиву без виходу за межі пам'яті.
2. **Багатопіковий або зашумлений спектр:** лінійна інтерполяція відстежує найперші точки спаду від головного максимуму, ураховуючи можливі шумні коливання baseline.

## 4. Код вимірювання смуги мовами C та C++

У наведених нижче вкладках подано реалізації алгоритму. Варіант на C розрахований на вбудовані системи та мікроконтролери із жорстким обмеженням пам'яті. Варіант на C++20 використовує сучасні концепції стандартної бібліотеки (`std::span`, `std::optional`, `std::accumulate`, `std::max_element`) без використання сирих вказівників.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Результати аналізу смуги пропускання */
typedef struct {
    double f_center;       /* Частота пикового максимуму (Гц) */
    double bw_3db;         /* Смуга за рівнем -3 дБ (Гц) */
    double bw_obw99;       /* 99% зайнята смуга ITU (Гц) */
    double f_low_3db;      /* Нижня частотна границя -3 дБ (Гц) */
    double f_high_3db;     /* Верхня частотна границя -3 дБ (Гц) */
    double f_low_obw;      /* Нижня границя 99% OBW (Гц) */
    double f_high_obw;     /* Верхня границя 99% OBW (Гц) */
} BandwidthResult;

/**
 * @brief Обчислює смугу -3 дБ та 99% OBW за масивом PSD.
 * @param psd Масив спектральної щільності потужності (лінійні одиниці Вт/Гц або V^2/Гц)
 * @param n Кількість відліків спектра (бінів БПФ)
 * @param f_start Початкова частота першого біна (Гц)
 * @param df Крок частотної сітки (Гц/бін)
 * @param res Вихідна структура для запису результатів
 * @return true у разі успішного розрахунку, false у разі помилки
 */
bool estimate_bandwidth(const double *psd, size_t n, double f_start, double df, BandwidthResult *res) {
    if (!psd || n < 3 || df <= 0.0 || !res) {
        return false;
    }

    /* 1. Знаходження максимуму та загальної інтегральної потужності */
    size_t idx_max = 0;
    double p_max = psd[0];
    double p_total = 0.0;

    for (size_t i = 0; i < n; i++) {
        p_total += psd[i];
        if (psd[i] > p_max) {
            p_max = psd[i];
            idx_max = i;
        }
    }

    if (p_max <= 1e-15 || p_total <= 1e-15) {
        return false; /* Спектр порожній або містить від'ємні значення */
    }

    res->f_center = f_start + (double)idx_max * df;
    double target_3db = p_max * 0.5; /* Рівень половинної потужності (-3.01 дБ) */

    /* 2. Пошук лівої границі -3 дБ з лінійною інтерполяцією */
    double idx_left_3db = (double)idx_max;
    for (size_t i = idx_max; i > 0; i--) {
        if (psd[i - 1] <= target_3db) {
            double p_lower = psd[i - 1];
            double p_upper = psd[i];
            double delta_p = p_upper - p_lower;
            double frac = (delta_p > 1e-12) ? (target_3db - p_lower) / delta_p : 0.0;
            idx_left_3db = (double)(i - 1) + frac;
            break;
        }
    }

    /* 3. Пошук правої границі -3 дБ з лінійною інтерполяцією */
    double idx_right_3db = (double)idx_max;
    for (size_t i = idx_max; i < n - 1; i++) {
        if (psd[i + 1] <= target_3db) {
            double p_left = psd[i];
            double p_right = psd[i + 1];
            double delta_p = p_right - p_left;
            double frac = (fabs(delta_p) > 1e-12) ? (target_3db - p_left) / delta_p : 0.0;
            idx_right_3db = (double)i + frac;
            break;
        }
    }

    res->f_low_3db = f_start + idx_left_3db * df;
    res->f_high_3db = f_start + idx_right_3db * df;
    res->bw_3db = res->f_high_3db - res->f_low_3db;

    /* 4. Пошук 99% OBW за кумулятивною інтегральною сумою */
    double lower_tail = p_total * 0.005; /* 0.5% нижнього хвоста */
    double upper_tail = p_total * 0.995; /* 99.5% повної енергії */

    double cumsum = 0.0;
    size_t idx_obw_low = 0;
    size_t idx_obw_high = n - 1;
    bool found_low = false;

    for (size_t i = 0; i < n; i++) {
        cumsum += psd[i];
        if (!found_low && cumsum >= lower_tail) {
            idx_obw_low = i;
            found_low = true;
        }
        if (cumsum >= upper_tail) {
            idx_obw_high = i;
            break;
        }
    }

    res->f_low_obw = f_start + (double)idx_obw_low * df;
    res->f_high_obw = f_start + (double)idx_obw_high * df;
    res->bw_obw99 = res->f_high_obw - res->f_low_obw;

    return true;
}

int main(void) {
    const size_t n = 512;
    double psd[512];
    double f_start = 100.0e6; /* 100 МГц несуча */
    double df = 1000.0;        /* 1 кГц на бін БПФ */

    /* Моделювання Гауссового радіосигналу з центром у 100.25 МГц */
    double center_bin = 250.0;
    double sigma_bin = 20.0;
    for (size_t i = 0; i < n; i++) {
        double diff = (double)i - center_bin;
        psd[i] = exp(-(diff * diff) / (2.0 * sigma_bin * sigma_bin));
    }

    BandwidthResult res;
    if (estimate_bandwidth(psd, n, f_start, df, &res)) {
        printf("=== Результати спектрального аналізу ===\n");
        printf("Пікова частота сигналу: %.3f МГц\n", res.f_center / 1e6);
        printf("Смуга за рівнем -3 дБ:  %.2f кГц (від %.3f до %.3f МГц)\n",
               res.bw_3db / 1e3, res.f_low_3db / 1e6, res.f_high_3db / 1e6);
        printf("Зайнята смуга 99%% OBW:  %.2f кГц (від %.3f до %.3f МГц)\n",
               res.bw_obw99 / 1e3, res.f_low_obw / 1e6, res.f_high_obw / 1e6);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>
#include <cmath>
#include <span>
#include <optional>
#include <iomanip>

struct BandwidthMetrics {
    double center_frequency_hz{0.0};
    double bw_3db_hz{0.0};
    double bw_obw99_hz{0.0};
    double f_low_3db_hz{0.0};
    double f_high_3db_hz{0.0};
    double f_low_obw_hz{0.0};
    double f_high_obw_hz{0.0};
};

class BandwidthEstimator {
public:
    [[nodiscard]] static std::optional<BandwidthMetrics> calculate(
        std::span<const double> psd,
        double start_frequency_hz,
        double bin_resolution_hz) noexcept
    {
        if (psd.size() < 3 || bin_resolution_hz <= 0.0) {
            return std::nullopt;
        }

        const auto max_it = std::max_element(psd.begin(), psd.end());
        const double p_max = *max_it;
        const auto max_idx = static_cast<size_t>(std::distance(psd.begin(), max_it));

        const double p_total = std::accumulate(psd.begin(), psd.end(), 0.0);
        if (p_max <= 1e-15 || p_total <= 1e-15) {
            return std::nullopt;
        }

        BandwidthMetrics metrics;
        metrics.center_frequency_hz = start_frequency_hz + static_cast<double>(max_idx) * bin_resolution_hz;

        // 1. Пошук і суб-бінова інтерполяція точок половинної потужності (-3 дБ)
        const double target_3db = p_max * 0.5;

        double left_idx = static_cast<double>(max_idx);
        for (size_t i = max_idx; i > 0; --i) {
            if (psd[i - 1] <= target_3db) {
                const double delta_p = psd[i] - psd[i - 1];
                const double frac = (delta_p > 1e-12) ? (target_3db - psd[i - 1]) / delta_p : 0.0;
                left_idx = static_cast<double>(i - 1) + frac;
                break;
            }
        }

        double right_idx = static_cast<double>(max_idx);
        for (size_t i = max_idx; i < psd.size() - 1; ++i) {
            if (psd[i + 1] <= target_3db) {
                const double delta_p = psd[i + 1] - psd[i];
                const double frac = (std::abs(delta_p) > 1e-12) ? (target_3db - psd[i]) / delta_p : 0.0;
                right_idx = static_cast<double>(i) + frac;
                break;
            }
        }

        metrics.f_low_3db_hz = start_frequency_hz + left_idx * bin_resolution_hz;
        metrics.f_high_3db_hz = start_frequency_hz + right_idx * bin_resolution_hz;
        metrics.bw_3db_hz = metrics.f_high_3db_hz - metrics.f_low_3db_hz;

        // 2. Кумулятивний пошук 99% OBW за стандартом ITU-R
        const double lower_threshold = p_total * 0.005;
        const double upper_threshold = p_total * 0.995;

        double running_sum = 0.0;
        size_t obw_low_idx = 0;
        size_t obw_high_idx = psd.size() - 1;
        bool low_found = false;

        for (size_t i = 0; i < psd.size(); ++i) {
            running_sum += psd[i];
            if (!low_found && running_sum >= lower_threshold) {
                obw_low_idx = i;
                low_found = true;
            }
            if (running_sum >= upper_threshold) {
                obw_high_idx = i;
                break;
            }
        }

        metrics.f_low_obw_hz = start_frequency_hz + static_cast<double>(obw_low_idx) * bin_resolution_hz;
        metrics.f_high_obw_hz = start_frequency_hz + static_cast<double>(obw_high_idx) * bin_resolution_hz;
        metrics.bw_obw99_hz = metrics.f_high_obw_hz - metrics.f_low_obw_hz;

        return metrics;
    }
};

int main() {
    constexpr size_t fft_bins = 512;
    std::vector<double> psd(fft_bins);
    constexpr double f_start = 100.0e6; // 100 МГц несуча
    constexpr double df = 1000.0;        // 1 кГц/бін

    constexpr double center_bin = 250.0;
    constexpr double sigma_bin = 20.0;
    for (size_t i = 0; i < fft_bins; ++i) {
        const double diff = static_cast<double>(i) - center_bin;
        psd[i] = std::exp(-(diff * diff) / (2.0 * sigma_bin * sigma_bin));
    }

    if (const auto metrics = BandwidthEstimator::calculate(psd, f_start, df)) {
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "=== Результати аналізу (C++20) ===\n";
        std::cout << "Пікова частота сигналу: " << metrics->center_frequency_hz / 1e6 << " МГц\n";
        std::cout << "Смуга за рівнем -3 дБ:  " << metrics->bw_3db_hz / 1e3 << " кГц (від "
                  << metrics->f_low_3db_hz / 1e6 << " до " << metrics->f_high_3db_hz / 1e6 << " МГц)\n";
        std::cout << "Зайнята смуга 99% OBW:  " << metrics->bw_obw99_hz / 1e3 << " кГц (від "
                  << metrics->f_low_obw_hz / 1e6 << " до " << metrics->f_high_obw_hz / 1e6 << " МГц)\n";
    }
    return 0;
}
```
:::
