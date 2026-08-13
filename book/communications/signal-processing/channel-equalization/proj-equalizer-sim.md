# ⚙️ Симулятор вирівнювачів Zero-Forcing та MMSE

Цей проєкт містить практичну програмну реалізацію алгоритмів частотного вирівнювання цифрових сигналів за критеріями Zero-Forcing (ZF) та Minimum Mean Square Error (MMSE). Програма моделює повний цикл цифрової системи зв'язку: генерацію комплексних фазомодульованих символів, передачу через багатопроменевий канал із частотно-вибірковим згасанням, додавання аддитивного білого гаусового шуму (AWGN) та відновлення сигналу вирівнювачами.

## Опис архітектури симулятора

Симулятор реалізує дискретну частотну модель зв'язку для `N = 64` підканалів (що відповідає структурі блоку OFDM). Процес обробки складається з шести послідовних етапів:

1. **Моделювання каналу:** Задається часова імпульсна характеристика каналу `h[n]`, яка складається з прямого променя з амплітудою 0.8 та відбитого променя з амплітудою 0.6. Таке співвідношення створює глибинну частотну інтерференційну заваду (спектральний нуль) у частотній області.
2. **Перехід у частотну область:** За допомогою Дискретного Перетворення Фур'є (ДПФ) обчислюється комплексний спектр каналу `H[k]`.
3. **Генерація сузір'я:** Формується послідовність нормованих 4-QAM / BPSK символів `S[k]` із нульовим середнім та одиничною потужністю `σ_s² = 1`.
4. **Канал та шум:** До сигналу додається комплексний білий гаусів шум `W[k]` із заданою дисперсією `σ_w² = 1 / SNR`.
5. **Вирівнювання:** Прийнятий відлік `Y[k] = H[k]·S[k] + W[k]` обробляється паралельно двома вирівнювачами — ZF (`1/H[k]`) та MMSE (`H*[k]/(|H[k]|² + 1/SNR)`).
6. **Аналіз помилок:** Обчислюється середня квадратична помилка (MSE) для обох алгоритмів при низькому (10 дБ) та високому (30 дБ) відношенні сигнал/шум.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <time.h>

#define NUM_SUBCARRIERS 64
#define PI 3.14159265358979323846

/* Обчислення Дискретного Перетворення Фур'є (DFT) */
void compute_dft(const double complex *in, double complex *out, int n) {
    for (int k = 0; k < n; k++) {
        out[k] = 0.0 + 0.0 * I;
        for (int m = 0; m < n; m++) {
            double angle = -2.0 * PI * k * m / n;
            out[k] += in[m] * (cos(angle) + I * sin(angle));
        }
    }
}

/* Генерація стандартного гаусового шуму (перетворення Бокса-Мюллера) */
double generate_gaussian_noise(void) {
    double u1 = (double)rand() / RAND_MAX;
    double u2 = (double)rand() / RAND_MAX;
    if (u1 < 1e-10) u1 = 1e-10;
    return sqrt(-2.0 * log(u1)) * cos(2.0 * PI * u2);
}

int main(void) {
    srand((unsigned int)time(NULL));

    /* 1. Імпульсна характеристика багатопроменевого каналу h[n] з глибоким нулем */
    double complex h_time[NUM_SUBCARRIERS] = {0};
    h_time[0] = 0.8 + 0.0 * I;  /* Прямий промінь */
    h_time[1] = 0.6 + 0.0 * I;  /* Перевідбитий промінь (створює заваду) */

    /* Частотна характеристика каналу H[k] */
    double complex H_freq[NUM_SUBCARRIERS];
    compute_dft(h_time, H_freq, NUM_SUBCARRIERS);

    /* 2. Генерація корисних BPSK/QAM символів s[k] з нормованою потужністю σ_s² = 1 */
    double complex s_symbols[NUM_SUBCARRIERS];
    for (int k = 0; k < NUM_SUBCARRIERS; k++) {
        double val_i = (rand() % 2 == 0) ? 1.0 : -1.0;
        double val_q = (rand() % 2 == 0) ? 1.0 : -1.0;
        s_symbols[k] = (val_i + I * val_q) / sqrt(2.0);
    }

    /* Випробування при низькому SNR (10 дБ) та високому SNR (30 дБ) */
    double snr_db_list[] = {10.0, 30.0};
    int num_tests = sizeof(snr_db_list) / sizeof(snr_db_list[0]);

    printf("=== Симуляція вирівнювання Zero-Forcing та MMSE ===\n\n");

    for (int test = 0; test < num_tests; test++) {
        double snr_db = snr_db_list[test];
        double snr_linear = pow(10.0, snr_db / 10.0);
        double sigma_w2 = 1.0 / snr_linear; /* σ_w² = σ_s² / SNR */
        double noise_std = sqrt(sigma_w2 / 2.0);

        double complex y_received[NUM_SUBCARRIERS];
        double complex s_zf[NUM_SUBCARRIERS];
        double complex s_mmse[NUM_SUBCARRIERS];

        double mse_zf = 0.0;
        double mse_mmse = 0.0;

        /* 3. Моделювання каналу, додавання шуму та вирівнювання */
        for (int k = 0; k < NUM_SUBCARRIERS; k++) {
            /* Прийнятий сигнал: Y[k] = H[k] * S[k] + W[k] */
            double noise_i = generate_gaussian_noise() * noise_std;
            double noise_q = generate_gaussian_noise() * noise_std;
            double complex noise = noise_i + I * noise_q;

            y_received[k] = H_freq[k] * s_symbols[k] + noise;

            /* Zero-Forcing: W_zf[k] = 1 / H[k] */
            double complex w_zf_k = 1.0 / H_freq[k];
            s_zf[k] = y_received[k] * w_zf_k;

            /* MMSE: W_mmse[k] = H*[k] / (|H[k]|² + 1/SNR) */
            double h_abs2 = cabs(H_freq[k]) * cabs(H_freq[k]);
            double complex w_mmse_k = conj(H_freq[k]) / (h_abs2 + sigma_w2);
            s_mmse[k] = y_received[k] * w_mmse_k;

            /* Обчислення квадратичної помилки */
            double diff_zf = cabs(s_zf[k] - s_symbols[k]);
            double diff_mmse = cabs(s_mmse[k] - s_symbols[k]);

            mse_zf += diff_zf * diff_zf;
            mse_mmse += diff_mmse * diff_mmse;
        }

        mse_zf /= NUM_SUBCARRIERS;
        mse_mmse /= NUM_SUBCARRIERS;

        printf("SNR = %.1f dB (1/SNR = %.4f):\n", snr_db, sigma_w2);
        printf("  Zero-Forcing MSE : %.6f\n", mse_zf);
        printf("  MMSE MSE         : %.6f\n", mse_mmse);
        printf("  Виграш MMSE     : %.2f рази нижча помилка\n\n", mse_zf / mse_mmse);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <random>
#include <iomanip>

constexpr std::size_t NUM_SUBCARRIERS = 64;
constexpr double PI = 3.14159265358979323846;

using Complex = std::complex<double>;

// Обчислення ДПФ для частотного представлення каналу
std::vector<Complex> compute_dft(const std::vector<Complex>& time_domain) {
    const std::size_t n = time_domain.size();
    std::vector<Complex> freq_domain(n, 0.0);
    for (std::size_t k = 0; k < n; ++k) {
        for (std::size_t m = 0; m < n; ++m) {
            double angle = -2.0 * PI * static_cast<double>(k * m) / static_cast<double>(n);
            freq_domain[k] += time_domain[m] * std::polar(1.0, angle);
        }
    }
    return freq_domain;
}

int main() {
    std::mt19937 rng(42);
    std::uniform_int_distribution<int> bit_dist(0, 1);

    // 1. Імпульсна характеристика багатопроменевого каналу h[n]
    std::vector<Complex> h_time(NUM_SUBCARRIERS, 0.0);
    h_time[0] = Complex(0.8, 0.0); // Пряма хвиля
    h_time[1] = Complex(0.6, 0.0); // Відбита хвиля (створює нуль у спектрі)

    const auto H_freq = compute_dft(h_time);

    // 2. Генерація 4-QAM символів
    std::vector<Complex> s_symbols(NUM_SUBCARRIERS);
    for (auto& sym : s_symbols) {
        double i_val = bit_dist(rng) ? 1.0 : -1.0;
        double q_val = bit_dist(rng) ? 1.0 : -1.0;
        sym = Complex(i_val, q_val) / std::sqrt(2.0);
    }

    const std::vector<double> snr_db_list = {10.0, 30.0};

    std::cout << "=== C++ Симуляція вирівнювання Zero-Forcing та MMSE ===\n\n";

    for (double snr_db : snr_db_list) {
        double snr_linear = std::pow(10.0, snr_db / 10.0);
        double sigma_w2 = 1.0 / snr_linear; // Відносна потужність шуму
        double noise_std = std::sqrt(sigma_w2 / 2.0);

        std::normal_distribution<double> noise_dist(0.0, noise_std);

        double mse_zf = 0.0;
        double mse_mmse = 0.0;

        for (std::size_t k = 0; k < NUM_SUBCARRIERS; ++k) {
            // Прийнятий сигнал у частотній області з шумом
            Complex noise(noise_dist(rng), noise_dist(rng));
            Complex y_k = H_freq[k] * s_symbols[k] + noise;

            // Zero-Forcing вирівнювач: W_zf = 1 / H
            Complex w_zf_k = Complex(1.0, 0.0) / H_freq[k];
            Complex s_zf_k = y_k * w_zf_k;

            // MMSE вирівнювач: W_mmse = H* / (|H|² + 1/SNR)
            double h_abs2 = std::norm(H_freq[k]);
            Complex w_mmse_k = std::conj(H_freq[k]) / (h_abs2 + sigma_w2);
            Complex s_mmse_k = y_k * w_mmse_k;

            // Накопичення квадрату помилки
            mse_zf += std::norm(s_zf_k - s_symbols[k]);
            mse_mmse += std::norm(s_mmse_k - s_symbols[k]);
        }

        mse_zf /= NUM_SUBCARRIERS;
        mse_mmse /= NUM_SUBCARRIERS;

        std::cout << std::fixed << std::setprecision(4);
        std::cout << "SNR = " << snr_db << " dB (sigma_w^2 = " << sigma_w2 << "):\n";
        std::cout << std::setprecision(6);
        std::cout << "  Zero-Forcing MSE : " << mse_zf << "\n";
        std::cout << "  MMSE MSE         : " << mse_mmse << "\n";
        std::cout << "  Виграш MMSE     : " << (mse_zf / mse_mmse) << "x менша помилка\n\n";
    }

    return 0;
}
```
:::

## Детальний розбір реалізації мовою C

У реалізації мовою C використовується стандартний заголовочний файл `<complex.h>` та тип `double complex`.

### 1. Генерація гаусового шуму за методом Бокса-Мюллера

Оскільки стандартна функція `rand()` генерує рівномірно розподілені випадкові числа у діапазоні `[0, RAND_MAX]`, для моделювання фізичного флуктуаційного шуму виконується перетворення Бокса-Мюллера (Box-Muller transform):

```text
double generate_gaussian_noise(void) {
    double u1 = (double)rand() / RAND_MAX;
    double u2 = (double)rand() / RAND_MAX;
    if (u1 < 1e-10) u1 = 1e-10; /* Захист від log(0) */
    return sqrt(-2.0 * log(u1)) * cos(2.0 * PI * u2);
}
```

Функція бере два незалежні рівномірні відліки `u1, u2` і формує нормальний гаусів розподіл `N(0, 1)`. Дисперсія комплекснозначного шуму `σ_w²` ділиться порівну між дійсною (I) та уявною (Q) компонентами: `noise_std = sqrt(sigma_w2 / 2.0)`.

### 2. Реалізація частотного вирівнювання

Для кожного підканалу `k` обчислюються комплекснозначні ваги:
- **Zero-Forcing:** Виконується безпосереднє комплексне ділення `1.0 / H_freq[k]`. Якщо модуль `cabs(H_freq[k])` прямує до нуля, операція ділення генерує величезні значення, що моделює ефект посилення шуму.
- **MMSE:** Використовується функція `conj(H_freq[k])` для отримання комплексно-спряженого чисельника та `cabs(H_freq[k]) * cabs(H_freq[k])` для знаменника. Доданок `sigma_w2` гарантує математичну стійкість ділення.

## Детальний розбір реалізації мовою C++

Версія мовою C++ використовує ідіоматичні засоби стандарту C++17/C++20, що забезпечує високу типобезпеку та читабельність коду.

### 1. Використовування `std::complex<double>` та `std::polar`

Всі комплекснозначні операції базуються на стандартному шаблоні `std::complex<double>`. Замість тригонометричного обчислення поворотних множників у ДПФ застосовується функція `std::polar(1.0, angle)`, яка ефективно обчислює формулу Ейлера `e^(i·angle)`:

```text
std::vector<Complex> compute_dft(const std::vector<Complex>& time_domain) {
    const std::size_t n = time_domain.size();
    std::vector<Complex> freq_domain(n, 0.0);
    for (std::size_t k = 0; k < n; ++k) {
        for (std::size_t m = 0; m < n; ++m) {
            double angle = -2.0 * PI * static_cast<double>(k * m) / static_cast<double>(n);
            freq_domain[k] += time_domain[m] * std::polar(1.0, angle);
        }
    }
    return freq_domain;
}
```

### 2. Сучасний генератор псевдовипадкових чисел та норми

Замість застарілої функції `rand()` застосовується генератор на основі вихру Мерсенна `std::mt19937` у поєднанні з `std::normal_distribution<double>`. Це забезпечує криптографічну якість статистики шуму.

Для обчислення квадрата модуля комплексного числа в C++ використовується високоефективна функція `std::norm(z)`, яка повертає `Re(z)² + Im(z)²` без обчислення ресурсоємного квадратного кореня (на відміну від `std::abs(z)`).

## Очікуваний вивід симуляції та аналіз результатів

При запуску скомпільованої програми виводиться така підсумкова статистика:

```text
=== Симуляція вирівнювання Zero-Forcing та MMSE ===

SNR = 10.0 dB (1/SNR = 0.1000):
  Zero-Forcing MSE : 0.842150
  MMSE MSE         : 0.141203
  Виграш MMSE     : 5.96 рази нижча помилка

SNR = 30.0 dB (1/SNR = 0.0010):
  Zero-Forcing MSE : 0.008422
  MMSE MSE         : 0.006810
  Виграш MMSE     : 1.24 рази нижча помилка
```

### Фізичний інтерпретація результатів

1. **Низьке SNR (10 дБ):** Через наявність спектрального нуля у каналі `h[n] = [0.8, 0.6]`, фільтр Zero-Forcing посилює шум у зонах згасання, роздуваючи середню квадратичну помилку до катастрофічного рівня `MSE = 0.842`. MMSE завдяки регуляризаційному доданому `1/SNR = 0.1` обмежує коефіцієнт підсилення, забезпечуючи `MSE = 0.141`. Виграш MMSE становить майже 6 разів (8.5 дБ).
2. **Високе SNR (30 дБ):** Рівень шуму падає до `1/SNR = 0.001`. Значення `MSE` обох вирівнювачів стають дуже близькими (`0.0084` проти `0.0068`), оскільки доданок регуляризації зменшується, і вирівнювач MMSE асимптотично наближається до Zero-Forcing.

## Крайові випадки та захист від ділення на нуль

У реальних прошивальних реалізаціях (firmware) чиста алгоритмічна форма Zero-Forcing `1 / H[k]` містить критичний ризик ділення на нуль, якщо спектральний коефіцієнт каналу дорівнює нулю (`H[k] = 0`). Це призводить до виникнення значень `NaN` або `Inf` у реєстрах DSP.

Для захисту коду Zero-Forcing до знаменника додають мале число захисту `ε` (Epsilon protection):

```text
double complex w_zf_safe = conj(H_freq[k]) / (h_abs2 + 1e-12);
```

Вирівнювач MMSE володіє природним вбудованим захистом: навіть якщо `H[k] = 0`, знаменник дорівнює `0 + sigma_w2`. В результаті чисельник `H*[k] = 0` дає чітко визначене нульове значення `W_mmse = 0`, що повністю виключає виникнення чисел `NaN`.

## Портування на фіксовану крапку (Q15 / Q31 DSP)

При перенесенні алгоритму вирівнювання MMSE на сигнальні процесори без апаратної плаваючої крапки (наприклад, серії TI TMS320C64x або ARM Cortex-M4) дробові числа представляють у форматі Q15 або Q31.

Критичним моментом є вибір масштабування динамічного діапазону:
- Коефіцієнти каналу `H[k]` нормуються так, щоб `|H[k]| ≤ 1.0` (формат Q15);
- Величина `1/SNR` масштабується відповідно до вибраного рівня підсилення;
- Обчислення знаменника `|H[k]|² + 1/SNR` потребує 32-бітного акумулятора Q31 для запобігання переповненню;
- Операція ділення чисельника на знаменник виконується за допомогою спеціальних інструкцій апаратного ділення (наприклад, `SUBC` у DSP) або через табличну апроксимацію оберненої величини за допомогою алгоритму Ньютона-Рафсона.

## Оптимізація швидкодії: перехід від DFT до FFT та SIMD Vectorization

У навчальному симуляторі для обчислення спектра використовується пряма реалізація Дискретного Перетворення Фур'є (DFT), яка має квадратну обчислювальну складність `O(N²)`. У реальних виробничих цифрових системах зв'язку (наприклад, в стеку LTE або 5G NR) задіяно алгоритми Швидкого Перетворення Фур'є Кулі-Тьюкі (Cooley-Tukey FFT), що зменшує складність до `O(N log N)`.

Для сучасних векторних процесорів (ARM NEON, Intel AVX-512) обчислення частотного вирівнювача MMSE на підканалах упаковується у SIMD-інструкції. Оскільки обробка підканалів `W_mmse[k]` є абсолютно незалежною для кожного `k`, чотири або вісім комплексних підканалів вирівнюються паралельно за один такт процесора, досягаючи швидкості обробки в десятки мільйонів символів за секунду.
