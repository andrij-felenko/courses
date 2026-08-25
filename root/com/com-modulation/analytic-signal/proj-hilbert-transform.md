# ⚙️ Обчислення аналітичного сигналу в C та C++

У цифрових системах обробки сигналів аналітичний сигнал обчислюють двома основними способами залежно від архітектури обчислювача та вимог до системної затримки:
1. **Спектральний метод Марпла (FFT-based Hilbert transform)** — застосовується при кадровій або пакетній обробці блоків даних (off-line або frame-based DSP). Забезпечує найвищу точність, ідеальне пригнічення від'ємних частот та відсутність фазових спотворень у смузі пропускання.
2. **Часовий КІХ-фільтр Гільберта (FIR Hilbert transformer)** — застосовується для потокової обробки відліків у реальному часі (real-time DSP на мікроконтролерах STM32/ESP32 та сигнальних процесорах). Забезпечує фіксовану групову затримку та низьку обчислювальну складність за рахунок нульових коефіцієнтів.

У цій вставці подано детальний опис обох математичних підходів, розбір обчислювальних нюансів, аналіз чисельної точності та закончені, готові до використання реалізації мовами C (C99) та C++ (C++23).

---

## 1. Спектральний алгоритм Марпла (FFT)

Спектральний метод обчислення дискретного аналітичного сигналу було розроблено Саймоном Марплом (S. Lawrence Marple Jr.) у 1999 році. Алгоритм приймає на вхід масив дійснозначних відліків `x[n]` довжиною `N` і повертає комплексний масив `z[n] = x[n] + j · x̂[n]`.

### Математичні кроки алгоритму

1. **Пряме перетворення Фур'є**:
   Обчислюється дискретне перетворення Фур'є дійснозначного вектора `x[n]`:
   ```
   X[k] = FFT{ x[n] },   k = 0, 1, ..., N-1
   ```
2. **Формування спектральної маски Гільберта `H[k]`**:
   Спектр `X[k]` множиться на комплексний вектор вагових коефіцієнтів `H[k]`:
   ```
          ┌ 1,        при k = 0 (постійна складова залишається без змін)
          │ 2,        при 1 ≤ k < N/2 (додатні частоти подвоюються)
   H[k] = ├ 1,        при k = N/2 (частота Найквіста для парного N)
          └ 0,        при N/2 < k < N (від'ємні частоти обнуляються)
   ```
   *Чому подвоюються додатні частоти*: оскільки дійснозначний сигнал має симетричний спектр `X[k] = X*[N-k]`, вилучення від'ємних частот зменшує загальну енергію сигналу удвічі. Множення додатних частот на `2` гарантує, що енергія аналітичного сигналу `z[n]` точно дорівнюватиме енергії вихідного сигналу `x[n]`.
   *Чому не змінюються DC та Nyquist*: постійна складова (`k = 0`) та частота Найквіста (`k = N/2`) не мають дзеркальних пар у спектрі, тому їхні коефіцієнти залишаються рівними `1`.
3. **Спектральне множення**:
   ```
   Z[k] = X[k] · H[k]
   ```
4. **Зворотне перетворення Фур'є**:
   ```
   z[n] = IFFT{ Z[k] }
   ```
   У результаті дійсна частина `Re(z[n])` з високою точністю збігається з вихідним сигналом `x[n]`, а уявна частина `Im(z[n])` являє собою його перетворення Гільберта `x̂[n]`.

### Чисельні нюанси та точність спектрального методу

При реалізації алгоритму Марпла з використанням арифметики з плаваючою точкою (float32 або float64) необхідно враховувати такі інженерні нюанси:
- **Точність подвійної точності (float64)**: використання типів `double` або `std::complex<double>` забезпечує пригнічення від'ємних частот на рівні `-300 дБ`, що обмежується лише накопиченою помилкою округлення арифметики IEEE 754.
- **Накладання крайових ефектів**: якщо вхідний кадр `x[n]` не є строго періодичним (значення `x[0] ≠ x[N-1]`), розрив на межі каду викликає розмивання спектра (spectral leakage). Для усунення цього явища перед ШВФ застосовують вікна Т'юкі або Хенна.
- **Розмір кадру N**: класичний Radix-2 FFT вимагає, щоб `N` було степенем 2 (`256, 512, 1024, 2048`). Якщо довжина сигналу не є степенем 2, застосовують доповнення нулями (zero-padding).

---

## 2. Реалізація спектрального методу в C та C++

У наведених нижче прикладах реалізовано повністю автономний алгоритм ШВФ (Cooley-Tukey Radix-2 FFT) та спектральний метод Марпла.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* 
 * Автономна реалізація Radix-2 Cooley-Tukey FFT з двома напрямками (пряме / зворотне).
 * Вхідний масив buf переставляється за алгоритмом Bit-reversal.
 */
static void fft_radix2(double complex *buf, size_t n, int inverse) {
    if (n <= 1) return;

    /* 1. Перестановка бітів (Bit-reversal permutation) */
    size_t j = 0;
    for (size_t i = 0; i < n; i++) {
        if (i < j) {
            double complex tmp = buf[i];
            buf[i] = buf[j];
            buf[j] = tmp;
        }
        size_t m = n >> 1;
        while (m >= 1 && j >= m) {
            j -= m;
            m >>= 1;
        }
        j += m;
    }

    /* 2. Обчислення каскадів метеликів (Butterfly computation) */
    for (size_t len = 2; len <= n; len <<= 1) {
        double angle = (inverse ? 2.0 : -2.0) * M_PI / (double)len;
        double complex wlen = cexp(I * angle);

        for (size_t i = 0; i < n; i += len) {
            double complex w = 1.0 + 0.0 * I;
            for (size_t k = 0; k < len / 2; k++) {
                double complex u = buf[i + k];
                double complex v = buf[i + k + len / 2] * w;
                buf[i + k] = u + v;
                buf[i + k + len / 2] = u - v;
                w *= wlen;
            }
        }
    }

    /* 3. Нормування для зворотного IFFT */
    if (inverse) {
        for (size_t i = 0; i < n; i++) {
            buf[i] /= (double)n;
        }
    }
}

/* 
 * Головна функція обчислення аналітичного сигналу за алгоритмом Марпла в C.
 * Приймає дійснозначний вхідний масив input та повертає комплексний вихідний масив output.
 * Розмір n має бути степенем 2.
 */
int compute_analytic_signal_c(const double *input, double complex *output, size_t n) {
    if (!input || !output || n == 0 || (n & (n - 1)) != 0) {
        return -1; /* Помилка: неправильний розмір або NULL вказівник */
    }

    /* Копіювання дійснозначного сигналу в комплексний масив */
    for (size_t i = 0; i < n; i++) {
        output[i] = input[i] + 0.0 * I;
    }

    /* Крок 1: Пряме швидке перетворення Фур'є */
    fft_radix2(output, n, 0);

    /* Крок 2: Модифікація спектра за ваговим масивом H[k] */
    output[0] *= 1.0; /* Постійна складова (DC) */

    size_t half = n / 2;
    for (size_t k = 1; k < half; k++) {
        output[k] *= 2.0; /* Додатні частоти подвоюються */
    }

    output[half] *= 1.0; /* Частота Найквіста */

    for (size_t k = half + 1; k < n; k++) {
        output[k] = 0.0 + 0.0 * I; /* Від'ємні частоти обнуляються */
    }

    /* Крок 3: Зворотне швидке перетворення Фур'є (IFFT) */
    fft_radix2(output, n, 1);

    return 0;
}

int main(void) {
    const size_t N = 16;
    double signal[16];
    double complex analytic[16];

    /* Генерація тестового сигналу: cos(2*pi*2*i/N) */
    for (size_t i = 0; i < N; i++) {
        signal[i] = cos(2.0 * M_PI * 2.0 * (double)i / (double)N);
    }

    if (compute_analytic_signal_c(signal, analytic, N) == 0) {
        printf("Index \t Real (x) \t Imag (x_hat) \t Envelope (A)\n");
        printf("-----------------------------------------------------\n");
        for (size_t i = 0; i < N; i++) {
            double re = creal(analytic[i]);
            double im = cimag(analytic[i]);
            double env = cabs(analytic[i]);
            printf("%2zu \t %+.4f \t %+.4f \t %.4f\n", i, re, im, env);
        }
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <complex>
#include <numbers>
#include <cmath>
#include <span>
#include <expected>
#include <iomanip>

enum class SignalError {
    InvalidSize,
    NullPointer
};

class AnalyticSignalCalculator {
public:
    using Complex = std::complex<double>;

    // Перевірка чи є розмір буфера степенем двійки
    static constexpr bool is_power_of_two(std::size_t n) noexcept {
        return n > 0 && (n & (n - 1)) == 0;
    }

    // Спектральний алгоритм Марпла обчислення аналітичного сигналу
    static std::expected<std::vector<Complex>, SignalError> 
    compute(std::span<const double> input) {
        const std::size_t n = input.size();
        if (!is_power_of_two(n)) {
            return std::unexpected(SignalError::InvalidSize);
        }

        std::vector<Complex> z(n);
        for (std::size_t i = 0; i < n; ++i) {
            z[i] = Complex(input[i], 0.0);
        }

        // 1. Пряме ШВФ
        fft_radix2(z, false);

        // 2. Модифікація спектра H[k]
        const std::size_t half = n / 2;
        for (std::size_t k = 1; k < half; ++k) {
            z[k] *= 2.0; // Подвоєння додатних частот
        }
        for (std::size_t k = half + 1; k < n; ++k) {
            z[k] = Complex(0.0, 0.0); // Обнулення від'ємних частот
        }

        // 3. Зворотне ШВФ
        fft_radix2(z, true);

        return z;
    }

private:
    static void fft_radix2(std::span<Complex> buf, bool inverse) {
        const std::size_t n = buf.size();

        // Перестановка бітів (Bit-reversal)
        std::size_t j = 0;
        for (std::size_t i = 0; i < n; ++i) {
            if (i < j) {
                std::swap(buf[i], buf[j]);
            }
            std::size_t m = n >> 1;
            while (m >= 1 && j >= m) {
                j -= m;
                m >>= 1;
            }
            j += m;
        }

        // Обчислення каскадів метеликів
        for (std::size_t len = 2; len <= n; len <<= 1) {
            const double angle = (inverse ? 2.0 : -2.0) * std::numbers::pi / static_cast<double>(len);
            const Complex wlen = std::polar(1.0, angle);

            for (std::size_t i = 0; i < n; i += len) {
                Complex w(1.0, 0.0);
                for (std::size_t k = 0; k < len / 2; ++k) {
                    Complex u = buf[i + k];
                    Complex v = buf[i + k + len / 2] * w;
                    buf[i + k] = u + v;
                    buf[i + k + len / 2] = u - v;
                    w *= wlen;
                }
            }
        }

        if (inverse) {
            const double inv_n = 1.0 / static_cast<double>(n);
            for (auto& val : buf) {
                val *= inv_n;
            }
        }
    }
};

int main() {
    constexpr std::size_t N = 16;
    std::vector<double> signal(N);

    for (std::size_t i = 0; i < N; ++i) {
        signal[i] = std::cos(2.0 * std::numbers::pi * 2.0 * static_cast<double>(i) / static_cast<double>(N));
    }

    auto result = AnalyticSignalCalculator::compute(signal);
    if (result) {
        std::cout << std::fixed << std::setprecision(4);
        std::cout << "Index\tReal (x)\tImag (x_hat)\tEnvelope (A)\n";
        std::cout << "-----------------------------------------------------\n";
        for (std::size_t i = 0; i < N; ++i) {
            const auto& z = (*result)[i];
            std::cout << i << "\t" 
                      << (z.real() >= 0 ? " " : "") << z.real() << "\t"
                      << (z.imag() >= 0 ? " " : "") << z.imag() << "\t"
                      << std::abs(z) << "\n";
        }
    } else {
        std::cerr << "Помилка обчислення аналітичного сигналу!\n";
    }

    return 0;
}
```
:::

---

## 3. Часовий КІХ-фільтр Гільберта (FIR Filter)

У потокових системах обробки сигналів реального часу (наприклад, у цифрових радіоприймачах SDR або медичних УЗД-сканерах) використання кадрового ШВФ є недопустимим через занадто велику обчислювальну затримку (latency). У таких архітектурах застосовують **непарні антисиметричні КІХ-фільтри Гільберта** (Type III FIR Filter).

### Синтез та властивості КІХ-фільтра

Імпульсна характеристика ідеального фільтра Гільберта `h[n] = 2 / (π n)` для непарних `n` є нескінченною. Для створення причинного цифрового фільтра скінченної довжини `M = 2L + 1` застосовують віконну обрізку:

```
         ┌ (2 / (π · n)) · w[n],  для непарних n (при -L ≤ n ≤ L, n ≠ 0)
h[n] =  ├ 
         └ 0,                     для парних n (включаючи n = 0)
```

де `w[n]` — симетрична віконна функція (Хеммінга, Кайзера або Блекмана).

**Ключові обчислювальні переваги КІХ-фільтра Гільберта**:
1. **Зниження обчислень на 50%**: завдяки тому, що кожен парний коефіцієнт `h[n]` строго дорівнює 0, половина операцій множення з додаванням (MAC) у циклі згортки просто пропускається.
2. **Точна та постійна групова затримка**: КІХ-фільтр непарної довжини `M` створює строго постійну групову затримку `τ = (M - 1) / 2` відліків на всіх частотах.
3. **Формування квадратурної пари (I/Q)**: щоб отримати точну квадратурну пару `(I[n], Q[n])` на виході, дійсну частину сигналу `x[n]` просто пропускають через лінію затримки на `τ` відліків (`I[n] = x[n - τ]`), а уявну частину `Q[n]` отримують з виходу КІХ-фільтра.

### Оптимізація віконних функцій для КІХ-фільтра

Для оптимізації характеристик КІХ-фільтра Гільберта вибір віконної функції має вирішальне значення:
- **Вікно Хеммінга**: забезпечує рівень пригнічення бокових пелюсток близько `-43 дБ`. Підходить для загальних задач радіозв'язку з невисоким динамічним діапазоном.
- **Вікно Кайзера**: дає змогу гнучко регулювати рівень пригнічення бокових пелюсток (від `-50 дБ` до `-100 дБ`) шляхом вибору параметра `β`. Збільшення `β` покращує пригнічення завад, але розширює перехідну смугу біля частот `0` та `f_s/2`.
- **Алгоритм Паркса — Макклеллана (Parks-McClellan / Remez)**: дає змогу синтезувати рівнохвильовий (equiripple) КІХ-фільтр Гільберта з мінімальною довжиною імпульсної характеристики при заданому рівня пульсацій у смузі пропускання.

---

## 4. Реалізація КІХ-фільтра Гільберта в C та C++

Наведені нижче класи реалізують потоковий КІХ-фільтр Гільберта з кільцевим буфером (circular buffer), що дозволяє обробляти вхідні відліки поодинці з мінімальними накладними витратами.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура потокового КІХ-фільтра Гільберта */
typedef struct {
    double *taps;        /* Масив коефіцієнтів фільтра */
    double *delay_line;  /* Кільцевий буфер для вхідних відліків */
    size_t length;        /* Загальна довжина фільтра M (непарне число) */
    size_t head;          /* Поточна позиція запису в кільцевому буфері */
    size_t delay;         /* Гропова затримка (M - 1) / 2 */
} fir_hilbert_t;

/* Створення та ініціалізація КІХ-фільтра Гільберта з вікном Хеммінга */
fir_hilbert_t* fir_hilbert_create(size_t num_taps) {
    if (num_taps % 2 == 0) num_taps++; /* Гарантуємо непарну довжину */

    fir_hilbert_t *filter = (fir_hilbert_t*)malloc(sizeof(fir_hilbert_t));
    if (!filter) return NULL;

    filter->length = num_taps;
    filter->delay = (num_taps - 1) / 2;
    filter->head = 0;

    filter->taps = (double*)calloc(num_taps, sizeof(double));
    filter->delay_line = (double*)calloc(num_taps, sizeof(double));

    if (!filter->taps || !filter->delay_line) {
        free(filter->taps);
        free(filter->delay_line);
        free(filter);
        return NULL;
    }

    /* Обчислення коефіцієнтів фільтра з вікном Хеммінга */
    int half = (int)filter->delay;
    for (int i = -half; i <= half; i++) {
        size_t idx = (size_t)(i + half);
        if (i % 2 != 0) {
            /* Віконна функція Хеммінга */
            double w = 0.54 + 0.46 * cos(M_PI * (double)i / (double)half);
            filter->taps[idx] = (2.0 / (M_PI * (double)i)) * w;
        } else {
            filter->taps[idx] = 0.0; /* Парні коефіцієнти строго 0 */
        }
    }

    return filter;
}

void fir_hilbert_free(fir_hilbert_t *filter) {
    if (filter) {
        free(filter->taps);
        free(filter->delay_line);
        free(filter);
    }
}

/* Обробка одного відліку сигналу в реальному часі */
void fir_hilbert_process(fir_hilbert_t *filter, double sample_in, double *i_out, double *q_out) {
    /* Запис нового відліку в кільцевий буфер */
    filter->delay_line[filter->head] = sample_in;

    /* 1. Обчислення Q(t) через дискретну згортку */
    double q_acc = 0.0;
    size_t idx = filter->head;

    for (size_t k = 0; k < filter->length; k++) {
        q_acc += filter->taps[k] * filter->delay_line[idx];
        if (idx == 0) {
            idx = filter->length - 1;
        } else {
            idx--;
        }
    }

    /* 2. Отримання I(t) з лінії затримки для компенсації фазового зсуву */
    size_t delayed_idx = (filter->head + filter->length - filter->delay) % filter->length;
    *i_out = filter->delay_line[delayed_idx];
    *q_out = q_acc;

    /* Зсув вказівника кільцевого буфера */
    filter->head = (filter->head + 1) % filter->length;
}

int main(void) {
    fir_hilbert_t *hilbert = fir_hilbert_create(31);
    if (!hilbert) return 1;

    printf("Sample \t Input \t\t I (Delayed) \t Q (Hilbert) \t Envelope\n");
    printf("----------------------------------------------------------------\n");

    for (int n = 0; n < 40; n++) {
        double in = cos(2.0 * M_PI * 0.1 * n);
        double i_val, q_val;
        fir_hilbert_process(hilbert, in, &i_val, &q_val);
        double env = sqrt(i_val * i_val + q_val * q_val);

        if (n >= 15) { /* Пропускаємо заповнення лінії затримки фільтра */
            printf("%2d \t %+.4f \t %+.4f \t %+.4f \t %.4f\n", n, in, i_val, q_val, env);
        }
    }

    fir_hilbert_free(hilbert);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <memory>
#include <iomanip>

class FirHilbertFilter {
public:
    struct QuadraturePair {
        double real_i; // Дійсна частина (In-phase, з узгодженою затримкою)
        double imag_q; // Уявна частина (Quadrature, з виходу Гільберта)

        [[nodiscard]] double envelope() const noexcept {
            return std::hypot(real_i, imag_q);
        }

        [[nodiscard]] double phase() const noexcept {
            return std::atan2(imag_q, real_i);
        }
    };

    explicit FirHilbertFilter(std::size_t num_taps) {
        if (num_taps % 2 == 0) ++num_taps; // Гарантуємо непарну довжину
        length_ = num_taps;
        delay_ = (num_taps - 1) / 2;
        delay_line_.assign(length_, 0.0);
        taps_.assign(length_, 0.0);

        // Обчислення коефіцієнтів з вікном Хеммінга
        const int half = static_cast<int>(delay_);
        for (int i = -half; i <= half; ++i) {
            const std::size_t idx = static_cast<std::size_t>(i + half);
            if (i % 2 != 0) {
                const double w = 0.54 + 0.46 * std::cos(std::numbers::pi * static_cast<double>(i) / static_cast<double>(half));
                taps_[idx] = (2.0 / (std::numbers::pi * static_cast<double>(i))) * w;
            } else {
                taps_[idx] = 0.0;
            }
        }
    }

    // Обробка одного відліку потоку в реальному часі
    QuadraturePair process(double sample_in) noexcept {
        delay_line_[head_] = sample_in;

        double q_acc = 0.0;
        std::size_t idx = head_;

        for (std::size_t k = 0; k < length_; ++k) {
            q_acc += taps_[k] * delay_line_[idx];
            if (idx == 0) {
                idx = length_ - 1;
            } else {
                --idx;
            }
        }

        const std::size_t delayed_idx = (head_ + length_ - delay_) % length_;
        const double i_val = delay_line_[delayed_idx];

        head_ = (head_ + 1) % length_;

        return QuadraturePair{.real_i = i_val, .imag_q = q_acc};
    }

    void reset() noexcept {
        std::fill(delay_line_.begin(), delay_line_.end(), 0.0);
        head_ = 0;
    }

private:
    std::vector<double> taps_;
    std::vector<double> delay_line_;
    std::size_t length_{31};
    std::size_t delay_{15};
    std::size_t head_{0};
};

int main() {
    FirHilbertFilter filter(31);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Sample\tInput\t\tI (Delayed)\tQ (Hilbert)\tEnvelope\n";
    std::cout << "----------------------------------------------------------------\n";

    for (int n = 0; n < 40; ++n) {
        const double in = std::cos(2.0 * std::numbers::pi * 0.1 * static_cast<double>(n));
        const auto pair = filter.process(in);

        if (n >= 15) { // Пропускаємо початкове заповнення фільтра
            std::cout << n << "\t" 
                      << (in >= 0 ? " " : "") << in << "\t"
                      << (pair.real_i >= 0 ? " " : "") << pair.real_i << "\t"
                      << (pair.imag_q >= 0 ? " " : "") << pair.imag_q << "\t"
                      << pair.envelope() << "\n";
        }
    }

    return 0;
}
```
:::

---

## 5. Порівняння підходів та вибір архітектури

При виборі між спектральним методом Марпла (FFT) та часовим КІХ-фільтром Гільберта керуються інженерними вимогами системи:

| Критерій | Спектральний метод (FFT / Марпл) | Часовий КІХ-фільтр (FIR) |
|---|---|---|
| **Режим обробки** | Кадровий / Пакетний (Off-line / Frame DSP) | Потоковий у реальному часі (Sample-by-sample DSP) |
| **Системна затримка** | Затримка повного кадру `N` відліків | Фіксована затримка `(M-1)/2` відліків |
| **Пригнічення від'ємних частот** | Точне (обнулення коефіцієнтів) | Залежить від довжини фільтра `M` та вікна |
| **Обчисливальна складність** | `O(N log N)` на кадр | `M / 2` множень на відлік (завдяки 0-коефіцієнтам) |
| **Вимоги до пам'яті** | Буфер для повного кадру `N` комплексних чисел | Малий кільцевий буфер розміру `M` відліків |
| **Крайові ефекти** | Ефект Гіббса на межах кадру (вимагає вікон) | Перехідний процес тривалістю `(M-1)/2` відліків на старті |
