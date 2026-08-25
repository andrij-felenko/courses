# ⚙️ Програмна реалізація просторових MIMO-детекторів (ZF, MMSE, ML)

<preknowlist>
- [Канал AWGN](topic:math-information/awgn-channel) — генерація комплексного гаусового шуму.
- [Статистика завмирань](topic:com-medium/fading-statistics) — моделювання релеївських коефіцієнтів передачі.
</preknowlist>

У системах бездротового зв'язку з просторовим мультиплексуванням передавач одночасно транслює `N_t` незалежних символів даних у спільній смузі частот. На стороні приймача кожна з `N_r` антен фіксує лінійну суперпозицію всіх випромінених хвиль, спотворену випадковим релеївським середовищем і змішану з тепловим шумом:

```
y = H·x + n
```

Задача MIMO-детектора полягає у відновленні вихідного дискретного інформаційного вектора `x = [x₁, x₂, …, x_{N_t}]ᵀ` за прийнятим вектором `y` та відомою матрицею каналу `H`.

Геометрично матриця `H` деформує ортогональну решітку сигнального сузір'я: масштабує осі, повертає їх у комплексному просторі та зменшує кути між сигнальними напрямками. Якщо стовпці матриці `H` виявляються близькими до лінійної залежності, точки сузір'я зближуються, що створює важкі перехресні завади (Inter-Stream Interference).

Нижче наведено теоретичний аналіз, архітектурні особливості, розширення за допомогою зниження ґратки (Lattice Reduction), конвеєрну апаратну реалізацію та повну програмну симуляцію трьох базових класів просторових детекторів для системи `2 × 2` з модуляцією QPSK: лінійного Zero-Forcing, регуляризованого MMSE та оптимального нелінійного Maximum Likelihood.

---

### 1. Теоретичний огляд та математичні основи алгоритмів

#### 1. Детектор Zero-Forcing (ZF)
Детектор Zero-Forcing прагне повністю усунути взаємні просторові завади між потоками шляхом множення прийнятого вектора на псевдообернену матрицю Мура–Пенроуза `W_ZF = (Hᴴ·H)⁻¹ · Hᴴ`.

При застосуванні фільтра вектор оцінок набуває вигляду:
```
x̂_ZF = W_ZF · y = (Hᴴ·H)⁻¹ · Hᴴ · (H·x + n) = x + (Hᴴ·H)⁻¹ · Hᴴ · n = x + n_ZF
```
Міжпотокова інтерференція зникає, проте дисперсія шумової складової для `i`-го просторового потоку дорівнює:
```
Var(n_{ZF,i}) = N₀ · [(Hᴴ·H)⁻¹]_{ii}
```
Якщо матриця каналу має високе число обумовленості `cond(H) = σ_max / σ_min ≫ 1` (стовпці матриці `H` близькі до лінійної залежності), діагональні елементи `[(Hᴴ·H)⁻¹]_{ii}` зростають на кілька порядків. Детектор Zero-Forcing спричиняє катастрофічне посилення шуму (Noise Enhancement). Порядок просторового рознесення детектора ZF становить лише `d = N_r − N_t + 1` (для конфігурації 2×2 `d = 2 − 2 + 1 = 1`).

#### 2. Лінійний детектор MMSE (Minimum Mean Square Error)
Детектор MMSE оптимізує лінійний просторовий фільтр `W_MMSE`, мінімізуючи повну середньоквадратичну похибку між переданим і відновленим векторами:
```
min_W  E[ ||W·y − x||² ]
```
Розв'язок задачі Вінера–Хопфа дає регуляризовану матрицю фільтрації:
```
W_MMSE = (Hᴴ·H + (σ_n² / σ_x²) · I_{N_t})⁻¹ · Hᴴ
```
де `σ_n² / σ_x² = 1 / SNR_lin` при одиничній енергії символів сузір'я. Регуляризаційний коефіцієнт обмежує знизу власні значення матриці `Hᴴ·H + α·I`, запобігаючи неконтрольованому зростанню дисперсії шуму. За низьких SNR детектор діє як узгоджений фільтр (Matched Filter), а за високих SNR асимптотично переходить у Zero-Forcing.

#### 3. Детектор максимальної правдоподібності (Maximum Likelihood, ML)
Детектор ML відмовляється від лінійного матричного обернення на користь дискретної оптимізації. Він перевіряє всі можливі комбінації векторів сигнального сузір'я `s ∈ Q^{N_t}` і обирає вектор, що мінімізує квадратичну евклідову нев'язку:
```
ŝ_ML = arg min_{s ∈ Q^{N_t}}  ||y − H·s||²
```
Детектор ML забезпечує мінімальну можливу ймовірність помилки та досягає повного порядку просторового рознесення `d = N_r = 2`. Його недоліком є експоненційна обчислювальна складність `O(|Q|^{N_t})`, яка для високих порядків модуляції та великої кількості антен стає неприйнятною для апаратної реалізації в реальному часі.

---

### 2. Програмна реалізація симулятора на Python та C++

Нижче наведено повністю працездатні еквівалентні реалізації Монте-Карло симуляції радіолінії MIMO 2×2 з релеївським каналом, детекторами ZF, MMSE та ML мовами Python та C++.

:::tabs
```python
import cmath
import math
import random

# Нормовані точки сузір'я QPSK з одиничною середньою енергією E_s = 1
INV_SQRT2 = 1.0 / math.sqrt(2.0)
QPSK_CONSTELLATION = [
    complex( INV_SQRT2,  INV_SQRT2),  # Символ 0 (біти 00)
    complex(-INV_SQRT2,  INV_SQRT2),  # Символ 1 (біти 01)
    complex( INV_SQRT2, -INV_SQRT2),  # Символ 2 (біти 10)
    complex(-INV_SQRT2, -INV_SQRT2),  # Символ 3 (біти 11)
]

def hard_slice_qpsk(val: complex) -> complex:
    """Поточкове порогове квантування у найближчу точку сузір'я QPSK."""
    re = INV_SQRT2 if val.real >= 0.0 else -INV_SQRT2
    im = INV_SQRT2 if val.imag >= 0.0 else -INV_SQRT2
    return complex(re, im)

def mat2x2_inv(a: complex, b: complex, c: complex, d: complex):
    """Аналітичне обернення комплексної матриці 2x2: [[a, b], [c, d]]."""
    det = a * d - b * c
    if abs(det) < 1e-12:
        det = complex(1e-12, 0.0)  # Захист від ділення на нуль
    inv_det = 1.0 / det
    return d * inv_det, -b * inv_det, -c * inv_det, a * inv_det

def detect_zf_2x2(H: list, y: list) -> list:
    """Zero-Forcing детектор: x̂ = (Hᴴ·H)⁻¹ · Hᴴ · y."""
    h11, h12 = H[0][0], H[0][1]
    h21, h22 = H[1][0], H[1][1]

    # Обчислення матриці Грама G = Hᴴ · H
    g11 = h11.conjugate() * h11 + h21.conjugate() * h21
    g12 = h11.conjugate() * h12 + h21.conjugate() * h22
    g21 = h12.conjugate() * h11 + h22.conjugate() * h21
    g22 = h12.conjugate() * h12 + h22.conjugate() * h22

    ig11, ig12, ig21, ig22 = mat2x2_inv(g11, g12, g21, g22)

    # Узгоджена просторова фільтрація y_mf = Hᴴ · y
    y1, y2 = y[0], y[1]
    ymf1 = h11.conjugate() * y1 + h21.conjugate() * y2
    ymf2 = h12.conjugate() * y1 + h22.conjugate() * y2

    # Оцінка переданих символів
    x1_est = ig11 * ymf1 + ig12 * ymf2
    x2_est = ig21 * ymf1 + ig22 * ymf2

    return [hard_slice_qpsk(x1_est), hard_slice_qpsk(x2_est)]

def detect_mmse_2x2(H: list, y: list, snr_lin: float) -> list:
    """Linear MMSE детектор: x̂ = (Hᴴ·H + (1/SNR)·I)⁻¹ · Hᴴ · y."""
    h11, h12 = H[0][0], H[0][1]
    h21, h22 = H[1][0], H[1][1]

    alpha = 1.0 / max(snr_lin, 1e-4)

    # Регуляризована матриця (Hᴴ·H + α·I)
    g11 = (h11.conjugate() * h11 + h21.conjugate() * h21) + alpha
    g12 = h11.conjugate() * h12 + h21.conjugate() * h22
    g21 = h12.conjugate() * h11 + h22.conjugate() * h21
    g22 = (h12.conjugate() * h12 + h22.conjugate() * h22) + alpha

    ig11, ig12, ig21, ig22 = mat2x2_inv(g11, g12, g21, g22)

    y1, y2 = y[0], y[1]
    ymf1 = h11.conjugate() * y1 + h21.conjugate() * y2
    ymf2 = h12.conjugate() * y1 + h22.conjugate() * y2

    x1_est = ig11 * ymf1 + ig12 * ymf2
    x2_est = ig21 * ymf1 + ig22 * ymf2

    return [hard_slice_qpsk(x1_est), hard_slice_qpsk(x2_est)]

def detect_ml_2x2(H: list, y: list) -> list:
    """Maximum Likelihood: повний перебір векторів сузір'я s ∈ Q²."""
    h11, h12 = H[0][0], H[0][1]
    h21, h22 = H[1][0], H[1][1]
    y1, y2 = y[0], y[1]

    best_dist = float("inf")
    best_s = [QPSK_CONSTELLATION[0], QPSK_CONSTELLATION[0]]

    for s1 in QPSK_CONSTELLATION:
        for s2 in QPSK_CONSTELLATION:
            # Очікуваний вектор безшумного відгуку r = H · s
            r1 = h11 * s1 + h12 * s2
            r2 = h21 * s1 + h22 * s2

            dist = abs(y1 - r1)**2 + abs(y2 - r2)**2
            if dist < best_dist:
                best_dist = dist
                best_s = [s1, s2]

    return best_s

def run_simulation(num_packets=10000, snr_db=14.0):
    """Монте-Карло симуляція 2x2 MIMO системи з релеївським каналом."""
    snr_lin = 10.0 ** (snr_db / 10.0)
    sigma_noise = math.sqrt(1.0 / (2.0 * snr_lin))

    err_zf = 0
    err_mmse = 0
    err_ml = 0
    total_symbols = num_packets * 2

    for _ in range(num_packets):
        tx_syms = [random.choice(QPSK_CONSTELLATION), random.choice(QPSK_CONSTELLATION)]

        # Релеївський канал H (комплексні гаусові відліки CN(0, 1))
        H = [
            [complex(random.gauss(0, 0.7071), random.gauss(0, 0.7071)),
             complex(random.gauss(0, 0.7071), random.gauss(0, 0.7071))],
            [complex(random.gauss(0, 0.7071), random.gauss(0, 0.7071)),
             complex(random.gauss(0, 0.7071), random.gauss(0, 0.7071))]
        ]

        n1 = complex(random.gauss(0, sigma_noise), random.gauss(0, sigma_noise))
        n2 = complex(random.gauss(0, sigma_noise), random.gauss(0, sigma_noise))

        y1 = H[0][0] * tx_syms[0] + H[0][1] * tx_syms[1] + n1
        y2 = H[1][0] * tx_syms[0] + H[1][1] * tx_syms[1] + n2
        y = [y1, y2]

        hat_zf = detect_zf_2x2(H, y)
        hat_mmse = detect_mmse_2x2(H, y, snr_lin)
        hat_ml = detect_ml_2x2(H, y)

        for i in range(2):
            if abs(hat_zf[i] - tx_syms[i]) > 1e-4:
                err_zf += 1
            if abs(hat_mmse[i] - tx_syms[i]) > 1e-4:
                err_mmse += 1
            if abs(hat_ml[i] - tx_syms[i]) > 1e-4:
                err_ml += 1

    return {
        "SER_ZF": err_zf / total_symbols,
        "SER_MMSE": err_mmse / total_symbols,
        "SER_ML": err_ml / total_symbols,
    }

if __name__ == "__main__":
    res = run_simulation(num_packets=5000, snr_db=14.0)
    print(f"Результати при SNR = 14 дБ:")
    print(f"  Zero-Forcing SER: {res['SER_ZF']:.4e}")
    print(f"  MMSE SER:         {res['SER_MMSE']:.4e}")
    print(f"  Max-Likelihood:   {res['SER_ML']:.4e}")
```
```cpp
#include <iostream>
#include <complex>
#include <vector>
#include <array>
#include <random>
#include <cmath>
#include <limits>

using cdouble = std::complex<double>;

constexpr double INV_SQRT2 = 0.7071067811865475;

const std::array<cdouble, 4> QPSK_CONSTELLATION = {
    cdouble( INV_SQRT2,  INV_SQRT2),
    cdouble(-INV_SQRT2,  INV_SQRT2),
    cdouble( INV_SQRT2, -INV_SQRT2),
    cdouble(-INV_SQRT2, -INV_SQRT2)
};

cdouble hard_slice_qpsk(cdouble val) noexcept {
    double re = (val.real() >= 0.0) ? INV_SQRT2 : -INV_SQRT2;
    double im = (val.imag() >= 0.0) ? INV_SQRT2 : -INV_SQRT2;
    return cdouble(re, im);
}

// Аналітичне обернення комплексної матриці 2x2
std::array<cdouble, 4> mat2x2_inv(cdouble a, cdouble b, cdouble c, cdouble d) noexcept {
    cdouble det = a * d - b * c;
    if (std::abs(det) < 1e-12) {
        det = cdouble(1e-12, 0.0);
    }
    cdouble inv_det = cdouble(1.0, 0.0) / det;
    return { d * inv_det, -b * inv_det, -c * inv_det, a * inv_det };
}

// Zero-Forcing детектор
std::array<cdouble, 2> detect_zf(const std::array<std::array<cdouble, 2>, 2>& H,
                                 const std::array<cdouble, 2>& y) noexcept {
    cdouble h11 = H[0][0], h12 = H[0][1];
    cdouble h21 = H[1][0], h22 = H[1][1];

    cdouble g11 = std::conj(h11) * h11 + std::conj(h21) * h21;
    cdouble g12 = std::conj(h11) * h12 + std::conj(h21) * h22;
    cdouble g21 = std::conj(h12) * h11 + std::conj(h22) * h21;
    cdouble g22 = std::conj(h12) * h12 + std::conj(h22) * h22;

    auto [ig11, ig12, ig21, ig22] = mat2x2_inv(g11, g12, g21, g22);

    cdouble ymf1 = std::conj(h11) * y[0] + std::conj(h21) * y[1];
    cdouble ymf2 = std::conj(h12) * y[0] + std::conj(h22) * y[1];

    cdouble x1_est = ig11 * ymf1 + ig12 * ymf2;
    cdouble x2_est = ig21 * ymf1 + ig22 * ymf2;

    return { hard_slice_qpsk(x1_est), hard_slice_qpsk(x2_est) };
}

// MMSE детектор
std::array<cdouble, 2> detect_mmse(const std::array<std::array<cdouble, 2>, 2>& H,
                                   const std::array<cdouble, 2>& y,
                                   double snr_lin) noexcept {
    cdouble h11 = H[0][0], h12 = H[0][1];
    cdouble h21 = H[1][0], h22 = H[1][1];

    double alpha = 1.0 / std::max(snr_lin, 1e-4);

    cdouble g11 = (std::conj(h11) * h11 + std::conj(h21) * h21) + alpha;
    cdouble g12 = std::conj(h11) * h12 + std::conj(h21) * h22;
    cdouble g21 = std::conj(h12) * h11 + std::conj(h22) * h21;
    cdouble g22 = (std::conj(h12) * h12 + std::conj(h22) * h22) + alpha;

    auto [ig11, ig12, ig21, ig22] = mat2x2_inv(g11, g12, g21, g22);

    cdouble ymf1 = std::conj(h11) * y[0] + std::conj(h21) * y[1];
    cdouble ymf2 = std::conj(h12) * y[0] + std::conj(h22) * y[1];

    cdouble x1_est = ig11 * ymf1 + ig12 * ymf2;
    cdouble x2_est = ig21 * ymf1 + ig22 * ymf2;

    return { hard_slice_qpsk(x1_est), hard_slice_qpsk(x2_est) };
}

// Maximum Likelihood (ML) детектор
std::array<cdouble, 2> detect_ml(const std::array<std::array<cdouble, 2>, 2>& H,
                                 const std::array<cdouble, 2>& y) noexcept {
    cdouble h11 = H[0][0], h12 = H[0][1];
    cdouble h21 = H[1][0], h22 = H[1][1];

    double best_dist = std::numeric_limits<double>::infinity();
    std::array<cdouble, 2> best_s = { QPSK_CONSTELLATION[0], QPSK_CONSTELLATION[0] };

    for (const auto& s1 : QPSK_CONSTELLATION) {
        for (const auto& s2 : QPSK_CONSTELLATION) {
            cdouble r1 = h11 * s1 + h12 * s2;
            cdouble r2 = h21 * s1 + h22 * s2;

            double dist = std::norm(y[0] - r1) + std::norm(y[1] - r2);
            if (dist < best_dist) {
                best_dist = dist;
                best_s = { s1, s2 };
            }
        }
    }
    return best_s;
}

int main() {
    std::mt19937 rng(42);
    std::normal_distribution<double> dist_norm(0.0, INV_SQRT2);
    std::uniform_int_distribution<int> dist_sym(0, 3);

    const int num_packets = 10000;
    const double snr_db = 14.0;
    const double snr_lin = std::pow(10.0, snr_db / 10.0);
    const double sigma_noise = std::sqrt(1.0 / (2.0 * snr_lin));
    std::normal_distribution<double> dist_noise(0.0, sigma_noise);

    int err_zf = 0, err_mmse = 0, err_ml = 0;

    for (int p = 0; p < num_packets; ++p) {
        std::array<cdouble, 2> tx_syms = {
            QPSK_CONSTELLATION[dist_sym(rng)],
            QPSK_CONSTELLATION[dist_sym(rng)]
        };

        std::array<std::array<cdouble, 2>, 2> H = {{
            { cdouble(dist_norm(rng), dist_norm(rng)), cdouble(dist_norm(rng), dist_norm(rng)) },
            { cdouble(dist_norm(rng), dist_norm(rng)), cdouble(dist_norm(rng), dist_norm(rng)) }
        }};

        cdouble n1(dist_noise(rng), dist_noise(rng));
        cdouble n2(dist_noise(rng), dist_noise(rng));

        std::array<cdouble, 2> y = {
            H[0][0] * tx_syms[0] + H[0][1] * tx_syms[1] + n1,
            H[1][0] * tx_syms[0] + H[1][1] * tx_syms[1] + n2
        };

        auto hat_zf = detect_zf(H, y);
        auto hat_mmse = detect_mmse(H, y, snr_lin);
        auto hat_ml = detect_ml(H, y);

        for (int i = 0; i < 2; ++i) {
            if (std::abs(hat_zf[i] - tx_syms[i]) > 1e-4) ++err_zf;
            if (std::abs(hat_mmse[i] - tx_syms[i]) > 1e-4) ++err_mmse;
            if (std::abs(hat_ml[i] - tx_syms[i]) > 1e-4) ++err_ml;
        }
    }

    const double total_syms = num_packets * 2.0;
    std::cout << "Результати 2x2 MIMO симуляції (SNR = " << snr_db << " dB):\n";
    std::cout << "  ZF SER:   " << (err_zf / total_syms) << "\n";
    std::cout << "  MMSE SER: " << (err_mmse / total_syms) << "\n";
    std::cout << "  ML SER:   " << (err_ml / total_syms) << "\n";

    return 0;
}
```
:::

---

### 3. Детальний інженерний аналіз та порівняння результатів

#### Число обумовленості матриці каналу та геометрія помилок
Якість просторової детекції лінійними детекторами критично залежить від числа обумовленості матриці каналу:
```
cond(H) = σ_max(H) / σ_min(H)
```
1. **Сприятливий радіоканал (`cond(H) ≈ 1`):** Стовпці матриці `H` є майже ортогональними. Матриця Грама `Hᴴ·H` є майже діагональною, тому обернення не підсилює шум. У цих умовах лінійні детектори ZF та MMSE демонструють завадостійкість, дуже близьку до оптимального детектора Maximum Likelihood, витрачаючи в рази менше обчислювальних ресурсів.
2. **Вироджений радіоканал (`cond(H) ≫ 1`):** Стовпці матриці `H` майже колінеарні (наприклад, за відсутності розсіювачів або за малої відстані між антенами). Матриця Грама стає майже сингулярною, через що діагональні елементи її обернення стрімко зростають:
```
[(Hᴴ·H)⁻¹]_{11} = 1 / (σ_min²) ≫ 1
```
У результаті вихідний шум детектора ZF багаторазово перекриває корисний сигнал, призводячи до помилок детекції навіть при вхідному SNR понад 20–30 дБ. Детектор MMSE за рахунок коефіцієнта регуляризації `α` стримує цей ефект, обмежуючи максимальну дисперсію шуму.

#### М'яке детектування (Soft-Output Demapping) та обчислення LLR
У сучасних цифрових стандартах зв'язку (LTE-Advanced, 5G NR, Wi-Fi 6/7) MIMO-детектор працює не ізольовано, а в парі з канальним декодером (LDPC або Polar коди). Детектор генерує не жорсткі двійкові рішення (`0` або `1`), а м'які оцінки у вигляді логарифмічного відношення правдоподібності (Log-Likelihood Ratio, LLR) для кожного канального біта:
```
LLR(b_k) = ln( P(b_k = 1 | y, H) / P(b_k = 0 | y, H) )
```
Для детектора MMSE наближений розрахунок LLR здійснюється через модель еквівалентного скалярного каналу:
```
LLR(b_{k,i}) ≈ (4 · Re(x̂_{MMSE,i}) · μ_i) / ( (1 − μ_i) · σ_x² )
```
де `μ_i = [W_MMSE · H]_{ii}` — ефективний коефіцієнт передачі для `i`-го просторового потоку.

#### Сфера-декодування (Sphere Decoding) як компроміс складності
Для систем високого порядку (наприклад, 4×4 з модуляцією 256-QAM, де кількість векторних комбінацій складає `256⁴ ≈ 4.29 × 10⁹`), прямий перебір ML неможливо реалізувати апаратно в реальному часі.

Сфера-декодер факторизує канальну матрицю за допомогою QR-розкладу `H = Q · R` (де `Q` — унітарна матриця, `R` — верхньотрикутна матриця):
```
||y − H·s||² = ||Qᴴ·y − R·s||² = ||y' − R·s||² ≤ r_sphere²
```
Оскільки матриця `R` є верхньотрикутною, багатовимірна задача зводиться до обходу дерева рішень за алгоритмом зворотного підставлення (алгоритми Шнорра–Ейхнера та Фінка–Поста):
```
∑_{i=1}^{N_t} | y'_i − ∑_{j=i}^{N_t} R_ij · s_j |² ≤ r_sphere²
```
Якщо на проміжному кроці часткова відстань перевищує заданий радіус гіперсфери `r_sphere`, вся гілка дерева негайно відтинається (tree pruning). Це знижує обчислювальну складність алгоритму до субполіноміальної `O(N_t³)` за високих SNR, зберігаючи завадостійкість ідеального детектора Maximum Likelihood.

---

### 4. Зниження ґратки (Lattice Reduction, LLL) та редукція просторових каналів

Геометрично сигнальне сузір'я MIMO утворює багатовимірну точкову ґратку (Lattice) `Λ(H) = { H · s,  s ∈ ℤ[j]^{N_t} }`. Якщо стовпці матриці `H` утворюють гострі кути між собою (погано обумовлений базис), області прийняття рішень Вороного стають сильно витягнутими паралелепіпедами. Просте порогове квантування за осями координат (ZF/MMSE slicing) призводить до грубих помилок через зрізання кутів сусідніх комірок.

Алгоритм Ленстри–Ленстри–Ловаса (LLL Lattice Reduction) знаходить унімодулярну матрицю перетворення `T` із цілими гаусовими коефіцієнтами (`det(T) = ±1` або `±j`), таку що нова зведена матриця каналу:

```
H̃ = H · T
```

має стовпці, максимально близькі до взаємної ортогональності та найменшої можливої довжини.

Приймач фільтрує сигнал через редуковану матрицю `H̃`:

```
z̃ = (H̃ᴴ·H̃)⁻¹ · H̃ᴴ · y = T⁻¹ · x + ñ
```

Оскільки стовпці `H̃` майже ортогональні, посилення шуму стає мінімальним. Після стандартного порогового округлення оцінки `ẑ = round(z̃)` початковий інформаційний вектор відновлюється безпомилково через зворотне унімодулярне відображення:

```
x̂ = T · ẑ
```

Детектор LR-aided ZF/MMSE досягає повного порядку просторового рознесення `d = N_r`, як у детектора Maximum Likelihood, маючи поліноміальну обчислювальну складність.

---

### 5. Конвеєрна апаратна реалізація на FPGA/ASIC

Для практичного розгортання MIMO-детектора в базових станціях 5G NR розробляють конвеєрні систолічні масиви:

1. **Блок QR-декомпозиції на алгоритмі CORDIC:**
   - Замість обчислення тригонометричних функцій і квадратних коренів матричний розклад `H = Q · R` виконується послідовністю фіксованих мікроповоротів CORDIC (Coordinate Rotation Digital Computer), що використовують лише операції зсуву та додавання.
2. **Арифметика з фіксованою комою (Fixed-Point Arithmetic):**
   - Комплексні коефіцієнти квантуються у форматі `Q4.12` (16 біт: 1 знаковий, 3 цілих, 12 дробових).
   - Для запобігання переповненню під час обчислення матриці Грама `Hᴴ·H` застосовують динамічне масштабування блоків експонент (Block Floating Point).
3. **Конвеєризація зворотного підставлення:**
   - Обчислення гілок сфера-декодера або лінійних оцінок ділиться на `N_t` послідовних конвеєрних тактів, забезпечуючи пропускну здатність обробки понад 1 мільярд просторових векторів на секунду при тактовій частоті FPGA 500 МГц.
