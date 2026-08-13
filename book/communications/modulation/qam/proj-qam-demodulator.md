# ⚙️ Реалізація модулятора та soft/hard демодулятора QAM

У сучасних цифрових системах передачі даних (Wi-Fi 6/7, 4G LTE, 5G NR, DVB-C) сузір'я QAM використовується для пакування потоку бітів у комплексні відліки синфазного (`I`) та квадратурного (`Q`) каналів. На стороні передавача потік бітів розбивається на блоки по `k = log₂ M` бітів, кожен з яких мапується у відповідний стан сузір'я. На стороні приймача відбувається зворотна операція — демодуляція, яка може виконуватися у двох кардинально різних режимах: жорсткому (*hard decision*) та м'якому (*soft decision*).

### Математичні принципи демодуляції QAM

Під час жорсткого демодулювання приймач вимірює прийнятий символ `y = I_rec + j·Q_rec` і знаходить точку сузір'я `s_hat = (a_i, b_i)`, яка розташована на найменшій евклідовій відстані від `y`. Оскільки для квадратних сузір'їв `M`-QAM сітка точок розпадається на дві незалежні `√M`-PAM модуляції по осях `I` та `Q`, прийняття рішення спрощується до порівняння координат із фіксованими порогами без обчислення квадратних коренів чи двовимірних відстаней.

Проте сучасні завадостійкі коди (LDPC, турбокоди, виколоті згорткові коди) потребують не просто жорсткого рішення «0» чи «1», а м'яких ймовірнісних оцінок надійності кожного біта. Для цього обчислюється логарифм відношення правдоподібностей (LLR):

```
LLR(b_i) = ln [ P(b_i = 1 | y) / P(b_i = 0 | y) ]
```

Для квадратного сузір'я 16-QAM з кодуванням Грея точне обчислення LLR вимагає підсумовування експонент за всіма точками сузір'я. Застосовуючи логарифмічне наближення Max-Log (`ln(e^A + e^B) ≈ max(A, B)`), складні трансцендентні обчислення перетворюються на прості кусочно-лінійні функції від координат `y_I` та `y_Q`.

Припустімо, що точки сузір'я 16-QAM мають нормовані амплітуди `{-3d, -d, +d, +3d}`, де `d = 1 / √10` забезпечує середню потужність сигналу `E_avg = 1.0`. Наближення Max-Log знаходить найближчу точку сузір'я серед усіх станів, де біт `b_i = 1`, та віднімає відстань до найближчої точки, де `b_i = 0`. В результаті трансцендентна байєсова формула згортається у шматочно-лінійні рівняння без виклику виснажливих функцій `exp()` чи `log()`.

Нормована відстань між рівнями 16-QAM становить `d = 2 / √10`. Оцінки LLR для чотирьох бітів символу `(b₀, b₁, b₂, b₃)` підпорядковуються наступним графічним лініям прийняття рішень:
- Біт `b₀` (знак `I`): LLR вимірюється пропорційно величині `y_I`. Якщо `y_I > 0`, біт швидше за все дорівнює 1, а за значення `y_I < 0` від'ємний знак вказує на логічний 0.
- Біт `b₁` (амплітуда `I`): LLR вимірює відстань від центральних точок до внутрішніх порогів `±d`. Значення пропорційне `d - |y_I|`.
- Біт `b₂` (знак `Q`): LLR вимірюється пропорційно величині `y_Q`.
- Біт `b₃` (амплітуда `Q`): LLR пропорційне `d - |y_Q|`.

### Апаратна обробка та квантування LLR

У практичних цифрових приймачах на базі DSP чи FPGA м'які оцінки LLR квантуються у цілочисельні 8-бітні значення зі знаком (`int8_t`). Для цього аналогово-цифровий перетворювач (ADC) та блок автоматичного регулювання посилення (AGC) підтримують нормовану середньоквадратичну амплітуду сигналу на сталому рівні `A_rms = 1.0`. Алгоритм цифрового AGC відстежує середню потужність блоку прийнятих символів `P_meas = (1 / N) · ∑ (y_I,k² + y_Q,k²)` та коригує масштабувальний множник `g_agc = 1 / √P_meas`.

Якщо коефіцієнт підсилення AGC відхиляється від оптимуму або якщо амплітуда сигналу "пливе" через згасання в каналі, лінійні межі `d - |y_I|` зсуваються відносно фіксованих цілочисельних сіток квантувача. Це призводить до нелінійного стискання діапазону LLR та суттєвого погіршення ефективності декодера LDPC (до 2.5 дБ втрати SNR).

### Архітектура програмного модему

Реалізований нижче програмний модуль моделює повний цикл обробки сигналу в цифровому модемі:
1. **Генерація псевдовипадкового потоку бітів** та їх групування по `k = 4` біти для 16-QAM.
2. **2D Грей-мапування:** конвертація двох бітів у координату `I` та двох бітів у координату `Q` за правилом `{00 → -3, 01 → -1, 11 → +1, 10 → +3}` з нормуванням на `√10`.
3. **Симуляція AWGN каналу:** накладання гаусового шуму з нормованою дисперсією `σ² = N_0 / 2` за методом Бокса–Мюллера для заданого рівня `E_b / N_0`.
4. **Демодуляція:** паралельне виконання жорсткого слайсера та м'якого Max-Log LLR демодулятора.
5. **Оцінка BER (Monte Carlo):** підрахунок бітових помилок для визначення надійності зв'язку за різних рівнів шуму.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define M_PI_VAL 3.14159265358979323846

/* Структура комплексного символу I/Q */
typedef struct {
    double i;
    double q;
} qam_symbol_t;

/* Генератор шуму Бокса-Мюллера */
static double generate_gaussian_noise(double sigma) {
    double u1 = (double)rand() / (RAND_MAX + 1.0);
    double u2 = (double)rand() / (RAND_MAX + 1.0);
    if (u1 < 1e-12) u1 = 1e-12;
    return sigma * sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI_VAL * u2);
}

/* 1D Грей мапування для 2 бітів -> 4-PAM {-3, -1, +1, +3} */
static double gray_map_2bit(uint8_t bits_2bit) {
    switch (bits_2bit & 0x03) {
        case 0: return -3.0; /* 00 */
        case 1: return -1.0; /* 01 */
        case 3: return  1.0; /* 11 */
        case 2: return  3.0; /* 10 */
        default: return 0.0;
    }
}

/* 1D Грей демодулювання для 4-PAM */
static uint8_t gray_demap_2bit(double val) {
    if (val < -2.0)     return 0; /* 00 */
    else if (val < 0.0) return 1; /* 01 */
    else if (val < 2.0) return 3; /* 11 */
    else                return 2; /* 10 */
}

/* Модулятор 16-QAM: упаковує масив бітів у масив комплексних символів */
void mod_16qam(const uint8_t *bits, size_t num_bits, qam_symbol_t *symbols) {
    const double norm = 1.0 / sqrt(10.0); /* E_avg = 1.0 */
    size_t num_symbols = num_bits / 4;
    
    for (size_t k = 0; k < num_symbols; k++) {
        uint8_t b_i = (bits[4 * k + 0] << 1) | bits[4 * k + 1];
        uint8_t b_q = (bits[4 * k + 2] << 1) | bits[4 * k + 3];
        
        symbols[k].i = gray_map_2bit(b_i) * norm;
        symbols[k].q = gray_map_2bit(b_q) * norm;
    }
}

/* Жорсткий демодулятор 16-QAM */
void demap_16qam_hard(const qam_symbol_t *symbols, size_t num_symbols, uint8_t *bits_out) {
    const double scale = sqrt(10.0);
    
    for (size_t k = 0; k < num_symbols; k++) {
        double val_i = symbols[k].i * scale;
        double val_q = symbols[k].q * scale;
        
        uint8_t b_i = gray_demap_2bit(val_i);
        uint8_t b_q = gray_demap_2bit(val_q);
        
        bits_out[4 * k + 0] = (b_i >> 1) & 0x01;
        bits_out[4 * k + 1] = (b_i >> 0) & 0x01;
        bits_out[4 * k + 2] = (b_q >> 1) & 0x01;
        bits_out[4 * k + 3] = (b_q >> 0) & 0x01;
    }
}

/* М'який демодулятор 16-QAM (Max-Log LLR) */
void demap_16qam_soft(const qam_symbol_t *symbols, size_t num_symbols, double n0, double *llrs_out) {
    const double norm = 1.0 / sqrt(10.0);
    const double d = 2.0 * norm;
    const double factor = 2.0 * d / (n0 / 2.0); /* 4d / N0 */

    for (size_t k = 0; k < num_symbols; k++) {
        double yi = symbols[k].i;
        double yq = symbols[k].q;
        
        /* LLR для бітів I */
        llrs_out[4 * k + 0] = factor * yi;
        llrs_out[4 * k + 1] = factor * (d - fabs(yi));
        
        /* LLR для бітів Q */
        llrs_out[4 * k + 2] = factor * yq;
        llrs_out[4 * k + 3] = factor * (d - fabs(yq));
    }
}

int main(void) {
    const size_t num_bits = 40000;
    const size_t num_symbols = num_bits / 4;
    
    uint8_t *tx_bits = (uint8_t *)malloc(num_bits * sizeof(uint8_t));
    uint8_t *rx_bits = (uint8_t *)malloc(num_bits * sizeof(uint8_t));
    qam_symbol_t *tx_syms = (qam_symbol_t *)malloc(num_symbols * sizeof(qam_symbol_t));
    qam_symbol_t *rx_syms = (qam_symbol_t *)malloc(num_symbols * sizeof(qam_symbol_t));
    double *llrs = (double *)malloc(num_bits * sizeof(double));

    for (size_t i = 0; i < num_bits; i++) {
        tx_bits[i] = rand() % 2;
    }

    mod_16qam(tx_bits, num_bits, tx_syms);

    printf("=== Симуляція 16-QAM модему (Monte Carlo) ===\n");
    printf("Eb/N0 (дБ) | BER (Hard)  | BER (Soft Sign)\n");
    printf("-------------------------------------------\n");

    for (double ebn0_db = 0.0; ebn0_db <= 12.0; ebn0_db += 2.0) {
        double ebn0_lin = pow(10.0, ebn0_db / 10.0);
        double k = 4.0; /* 16-QAM */
        double esn0_lin = k * ebn0_lin;
        double n0 = 1.0 / esn0_lin;
        double sigma = sqrt(n0 / 2.0);

        /* Додавання AWGN */
        for (size_t i = 0; i < num_symbols; i++) {
            rx_syms[i].i = tx_syms[i].i + generate_gaussian_noise(sigma);
            rx_syms[i].q = tx_syms[i].q + generate_gaussian_noise(sigma);
        }

        /* Жорстка та м'яка демодуляція */
        demap_16qam_hard(rx_syms, num_symbols, rx_bits);
        demap_16qam_soft(rx_syms, num_symbols, n0, llrs);

        size_t hard_errors = 0;
        size_t soft_errors = 0;
        for (size_t i = 0; i < num_bits; i++) {
            if (rx_bits[i] != tx_bits[i]) hard_errors++;
            uint8_t soft_bit = (llrs[i] >= 0.0) ? 1 : 0;
            if (soft_bit != tx_bits[i]) soft_errors++;
        }

        printf(" %4.1f дБ   | %1.5f     | %1.5f\n",
               ebn0_db, (double)hard_errors / num_bits, (double)soft_errors / num_bits);
    }

    free(tx_bits); free(rx_bits); free(tx_syms); free(rx_syms); free(llrs);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <complex>
#include <random>
#include <cmath>
#include <iomanip>
#include <span>

class QamModem16 {
public:
    using Complex = std::complex<double>;

    explicit QamModem16()
        : norm_(1.0 / std::sqrt(10.0)) {}

    [[nodiscard]] std::vector<Complex> modulate(std::span<const uint8_t> bits) const {
        if (bits.size() % 4 != 0) {
            throw std::invalid_argument("Кількість бітів має бути кратна 4 для 16-QAM");
        }
        size_t num_symbols = bits.size() / 4;
        std::vector<Complex> symbols(num_symbols);

        for (size_t k = 0; k < num_symbols; ++k) {
            uint8_t b_i = (bits[4 * k + 0] << 1) | bits[4 * k + 1];
            uint8_t b_q = (bits[4 * k + 2] << 1) | bits[4 * k + 3];

            double i_val = grayMap2Bit(b_i) * norm_;
            double q_val = grayMap2Bit(b_q) * norm_;
            symbols[k] = {i_val, q_val};
        }
        return symbols;
    }

    [[nodiscard]] std::vector<uint8_t> demapHard(std::span<const Complex> symbols) const {
        double scale = std::sqrt(10.0);
        std::vector<uint8_t> bits(symbols.size() * 4);

        for (size_t k = 0; k < symbols.size(); ++k) {
            double val_i = symbols[k].real() * scale;
            double val_q = symbols[k].imag() * scale;

            uint8_t b_i = grayDemap2Bit(val_i);
            uint8_t b_q = grayDemap2Bit(val_q);

            bits[4 * k + 0] = (b_i >> 1) & 0x01;
            bits[4 * k + 1] = (b_i >> 0) & 0x01;
            bits[4 * k + 2] = (b_q >> 1) & 0x01;
            bits[4 * k + 3] = (b_q >> 0) & 0x01;
        }
        return bits;
    }

    [[nodiscard]] std::vector<double> demapSoftMaxLog(std::span<const Complex> symbols, double n0) const {
        double d = 2.0 * norm_;
        double factor = 2.0 * d / (n0 / 2.0);
        std::vector<double> llrs(symbols.size() * 4);

        for (size_t k = 0; k < symbols.size(); ++k) {
            double yi = symbols[k].real();
            double yq = symbols[k].imag();

            llrs[4 * k + 0] = factor * yi;
            llrs[4 * k + 1] = factor * (d - std::abs(yi));
            llrs[4 * k + 2] = factor * yq;
            llrs[4 * k + 3] = factor * (d - std::abs(yq));
        }
        return llrs;
    }

private:
    double norm_;

    static double grayMap2Bit(uint8_t b) {
        switch (b & 0x03) {
            case 0: return -3.0;
            case 1: return -1.0;
            case 3: return  1.0;
            case 2: return  3.0;
            default: return 0.0;
        }
    }

    static uint8_t grayDemap2Bit(double v) {
        if (v < -2.0)      return 0;
        else if (v < 0.0)  return 1;
        else if (v < 2.0)  return 3;
        else               return 2;
    }
};

int main() {
    constexpr size_t num_bits = 40000;
    std::mt19937 rng(42);
    std::uniform_int_distribution<int> bit_dist(0, 1);

    std::vector<uint8_t> tx_bits(num_bits);
    for (auto &b : tx_bits) b = static_cast<uint8_t>(bit_dist(rng));

    QamModem16 modem;
    auto tx_symbols = modem.modulate(tx_bits);

    std::cout << "=== C++17 16-QAM Modem Simulation ===\n";
    std::cout << std::fixed << std::setprecision(5);
    std::cout << "Eb/N0 (dB) | BER (Hard)  | BER (Soft Sign)\n";
    std::cout << "-------------------------------------------\n";

    for (double ebn0_db = 0.0; ebn0_db <= 12.0; ebn0_db += 2.0) {
        double ebn0_lin = std::pow(10.0, ebn0_db / 10.0);
        double esn0_lin = 4.0 * ebn0_lin;
        double n0 = 1.0 / esn0_lin;
        double sigma = std::sqrt(n0 / 2.0);

        std::normal_distribution<double> noise_dist(0.0, sigma);
        std::vector<std::complex<double>> rx_symbols(tx_symbols.size());

        for (size_t i = 0; i < tx_symbols.size(); ++i) {
            rx_symbols[i] = tx_symbols[i] + std::complex<double>(noise_dist(rng), noise_dist(rng));
        }

        auto rx_bits = modem.demapHard(rx_symbols);
        auto llrs = modem.demapSoftMaxLog(rx_symbols, n0);

        size_t hard_errors = 0;
        size_t soft_errors = 0;
        for (size_t i = 0; i < num_bits; ++i) {
            if (rx_bits[i] != tx_bits[i]) hard_errors++;
            uint8_t soft_bit = (llrs[i] >= 0.0) ? 1 : 0;
            if (soft_bit != tx_bits[i]) soft_errors++;
        }

        std::cout << " " << std::setw(4) << std::setprecision(1) << ebn0_db
                  << " dB   | " << std::setprecision(5) << static_cast<double>(hard_errors) / num_bits
                  << "     | " << static_cast<double>(soft_errors) / num_bits << "\n";
    }

    return 0;
}
```
:::

### Пастки реалізації та практичні нюанси

1. **Нормування коефіцієнтів LLR для апаратного декодування:**
   У практичних системних рішеннях на DSP чи FPGA логарифмічні відношення LLR квантуються у 6-бітні або 8-бітні цілі числа зі знаком (`int8_t`). Якщо автоматичне регулювання посилення (AGC) працює невірно і середня амплітуда сигналу відхиляється від нормованої одиниці, множник `factor = 4d / N_0` спотворює пропорції LLR, спричиняючи деградацію завадостійкого декодера LDPC на 1.5–3 дБ.

2. **Залежність від еквалайзера у каналах із багатопроменевістю:**
   У реальних каналах зв'язку з мультиплексним поширенням хвилин сузір'я 16-QAM зазнає суттєвої міжсимвольної інтерференції (ISI), що зміщує точки у сусідні квадранти. Спроба демодулювати сигнал без попереднього вирівнювання тракту за допомогою цифрового адаптивного еквалайзера (наприклад, LMS чи RLS) призводить до суцільних помилок декодування незалежно від високої потужності передавача.
