# ⚙️ Алгоритми компенсації постійної складової (DCOC) та калібрування I/Q

Цей практичний проєкт демонструє реалізацію двох цифрових алгоритмів обробки сигналів для Zero-IF приймачів мовами C та C++: рекурсивного фільтра усунення постійної складової (DCOC) та ортогоналізації Ґрама-Шмідта для компенсації I/Q дисбалансу.

### Принцип роботи цифрових адаптивних алгоритмів

У приймачах прямого перетворення (Zero-IF) цифрова обробка базової смуги в цифровому сигнальному процесорі (DSP) або FPGA розпочинається одразу після оцифрування аналогово-цифровими перетворювачами (АЦП) віток I та Q. Оцифровані відліки містять дві основні систематичні завади, викликані недосконалістю аналогового ВЧ-переднього кінця:

1. **Динамічну постійну складову (DC Offset)**: виникає через самозмішування гетеродина (LO self-mixing) та температурний дрейф аналогових підсилювачів. Вона зсуває середнє значення відліків від нуля, що краде динамічний діапазон АЦП та створює потужний паразитний пік на 0 Гц.
2. **I/Q Дисбаланс**: викликається фазовою `θ` та амплітудною `ε` асиметрією аналогових змішувачів і квадратурного гетеродина. Це призводить до витікання дзеркального каналу у корисний спектр та викривлення сигнального сузір'я.

Для усунення цих завад у реальному часі застосовується послідовний цифровий тракт компенсації:

1. **Фільтр DCOC (Dynamic DC Offset Cancellation)**: Рекурсивний цифровий фільтр високих частот із низькою частотою зрізу (порядку 0.1% від частоти дискретизації). Він постійно оцінює ковзне середнє значення сигналу `mean[n]` та віднімає його від поточного відліку:

```
mean[n] = (1 − α) · mean[n−1] + α · x[n]
y[n]    = x[n] − mean[n]
```

де `α` — коефіцієнт адаптації (наприклад, `α = 2^-10 ≈ 0.00097`), що задає постійну часу усереднення.

2. **Компенсатор Ґрама-Шмідта (Gram-Schmidt IQ Balancer)**: Алгоритм сліпої ортогоналізації. Вважаючи канал `I` еталонним (`I_corr = I_in`), він оцінює ковзне взаємне кореляційне значення між каналами `I` та `Q` для обчислення фазового коефіцієнта `C_phase`, а також відношення потужностей для обчислення амплітудного коефіцієнта `C_gain`:

```
I_corr[n] = I_in[n]
Q_corr[n] = (Q_in[n] − C_phase · I_in[n]) · C_gain
```

### Фізичний механізм адаптації фільтра DCOC

Рекурсивний фільтр вилучення постійної складової DCOC є цифровим аналогом простішого аналогового RC-фільтра високих частот. Головне завдання цифрового алгоритму полягає у відокремленні повільного зміщення постійного рівня від швидкозмінних компонентів корисного модульованого сигналу.

Коефіцієнт адаптації `α` (альфа) визначає смугу зрізу цифрового ФВЧ. Для вибору коефіцієнта `α` скористаємося зв'язком між постійною часу усереднення `τ` та частотою дискретизації `f_s`:

```
α = 1 / (f_s · τ)
```

Якщо частота дискретизації АЦП становить `f_s = 20 МГц`, а потрібна смуга зрізу DCOC не повинна перевищувати `f_cut = 10 кГц` (щоб не спотворювати центр OFDM-сигналу), то постійна часу `τ = 1 / (2 · π · f_cut) ≈ 15.9 мкс`. Відповідно, оптимальний коефіцієнт адаптації обирають як степень двійки для прискорення обчислень у фіксованій крапці:

```
α = 2^-9 ≈ 0.001953
```

За такої настройки фільтр DCOC повністю відслідковує та пригнічує низькочастотний температурний дрейф аналогових підсилювачів та повільні зміни напруги самозмішування гетеродина при переминанні частот синтезатора.

### Адаптивний метод ортогоналізації Ґрама-Шмідта

Метод Ґрама-Шмідта базується на лінійній алгебрі геометричного простору сигналів. Вважаючи синфазну векторну координату `I[n]` базисним вектором, ми проектуємо квадратурний вектор `Q[n]` на базис `I[n]`. Величина ортогональної проекції визначається математичним сподіванням взаємного добутку `E{I · Q}`.

Якщо квадратурні вітки ідеально ортогональні (фазовий кут точно 90 градусів) та симетричні за потужністю, то математичне сподівання добутку незалежних випадкових процесів дорівнює нулю:

```
E{ I[n] · Q[n] } = 0
```

Якщо ж між каналами існує фазова похибка `θ`, взаємний добуток `I[n] · Q[n]` стає відмінним від нуля. Адаптивний алгоритм обчислює три ковзні рекурсивні оцінки статистичних моментів першого та другого порядків:

```
p_I[n]  = (1 − μ) · p_I[n−1]  + μ · I[n]²
p_Q[n]  = (1 − μ) · p_Q[n−1]  + μ · Q[n]²
p_IQ[n] = (1 − μ) · p_IQ[n−1] + μ · (I[n] · Q[n])
```

де `μ` (мю) — швидкість адаптації оцінювача (типово `μ = 0.0005`).

На основі цих ковзних статистичних оцінок у реальному часі обчислюються поточні коефіцієнти корекції матриці ортогоналізації:
- **Коефіцієнт фазової корекції**: `C_phase = p_IQ / p_I`. Цей коефіцієнт визначає, яка саме частина синфазного сигналу `I[n]` протікає у квадратурний канал `Q[n]`. Віднімаючи добуток `C_phase · I[n]` від `Q[n]`, ми відновлюємо точну геометричну ортогональність у 90 градусів.
- **Коефіцієнт амплітудної корекції**: `C_gain = sqrt(p_I / p_Q)`. Цей коефіцієнт масштабує амплітуду квадратурного каналу, вирівнюючи середньоквадратичні потужності обох віток.

### Програмна реалізація алгоритмів

Нижче наведено повну робочу реалізацію цифрового тракту компенсації DCOC та I/Q калібрування мовами C та C++. Реалізація мовою C пропонує низькорівневі процедури з явним керуванням пам'яттю для вбудованих систем, тоді як версія на C++20 використовує об'єктно-орієнтовану концепцію, безпечні за пам'яттю обгортки `std::span` та математичний тип `std::complex<float>`.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Структура стану фільтра DCOC */
typedef struct {
    float mean_i;
    float mean_q;
    float alpha;
} dcoc_filter_t;

/* Структура стану компенсатора IQ дисбалансу */
typedef struct {
    float p_i;       /* Потужність I каналу */
    float p_q;       /* Потужність Q каналу */
    float p_iq;      /* Взаємна кореляція I та Q */
    float mu;        /* Швидкість адаптації LMS */
    float c_phase;   /* Коефіцієнт фазової корекції */
    float c_gain;    /* Коефіцієнт амплітудної корекції */
} iq_calibrator_t;

/* Ініціалізація DCOC */
void dcoc_init(dcoc_filter_t *dcoc, float alpha) {
    dcoc->mean_i = 0.0f;
    dcoc->mean_q = 0.0f;
    dcoc->alpha = alpha;
}

/* Обробка буфера фільтром DCOC */
void dcoc_process(dcoc_filter_t *dcoc, float *i_buf, float *q_buf, size_t count) {
    const float alpha = dcoc->alpha;
    const float one_minus_alpha = 1.0f - alpha;

    for (size_t n = 0; n < count; ++n) {
        dcoc->mean_i = one_minus_alpha * dcoc->mean_i + alpha * i_buf[n];
        dcoc->mean_q = one_minus_alpha * dcoc->mean_q + alpha * q_buf[n];

        i_buf[n] -= dcoc->mean_i;
        q_buf[n] -= dcoc->mean_q;
    }
}

/* Ініціалізація IQ компенсатора */
void iq_calibrator_init(iq_calibrator_t *iq, float mu) {
    iq->p_i = 1.0f;
    iq->p_q = 1.0f;
    iq->p_iq = 0.0f;
    iq->mu = mu;
    iq->c_phase = 0.0f;
    iq->c_gain = 1.0f;
}

/* Адаптивне калібрування IQ дисбалансу за методом Ґрама-Шмідта */
void iq_calibrator_process(iq_calibrator_t *iq, float *i_buf, float *q_buf, size_t count) {
    const float mu = iq->mu;

    for (size_t n = 0; n < count; ++n) {
        const float i_in = i_buf[n];
        const float q_in = q_buf[n];

        /* Оновлення статистики адаптації */
        iq->p_i  = (1.0f - mu) * iq->p_i  + mu * (i_in * i_in);
        iq->p_q  = (1.0f - mu) * iq->p_q  + mu * (q_in * q_in);
        iq->p_iq = (1.0f - mu) * iq->p_iq + mu * (i_in * q_in);

        /* Обчислення коефіцієнтів компенсації */
        if (iq->p_i > 1e-9f && iq->p_q > 1e-9f) {
            iq->c_phase = iq->p_iq / iq->p_i;
            iq->c_gain  = sqrtf(iq->p_i / iq->p_q);
        }

        /* Застосування ортогоналізації Ґрама-Шмідта */
        const float i_out = i_in;
        const float q_out = (q_in - iq->c_phase * i_in) * iq->c_gain;

        i_buf[n] = i_out;
        q_buf[n] = q_out;
    }
}
```

@tab C++
```cpp
#include <complex>
#include <span>
#include <vector>
#include <cmath>
#include <algorithm>

namespace zero_if {

// Адаптивний рекурсивний фільтр вилучення постійної складової (DCOC)
class DcocFilter {
public:
    explicit constexpr DcocFilter(float alpha = 0.001f) noexcept 
        : alpha_{alpha} {}

    // Обробка комплексної послідовності IQ відліків за допомогою std::span
    void process(std::span<std::complex<float>> samples) noexcept {
        const float one_minus_alpha = 1.0f - alpha_;

        for (auto& sample : samples) {
            mean_i_ = one_minus_alpha * mean_i_ + alpha_ * sample.real();
            mean_q_ = one_minus_alpha * mean_q_ + alpha_ * sample.imag();

            sample = {sample.real() - mean_i_, sample.imag() - mean_q_};
        }
    }

    [[nodiscard]] constexpr std::complex<float> current_offset() const noexcept {
        return {mean_i_, mean_q_};
    }

    void reset() noexcept {
        mean_i_ = 0.0f;
        mean_q_ = 0.0f;
    }

private:
    float alpha_;
    float mean_i_{0.0f};
    float mean_q_{0.0f};
};

// Адаптивний компенсатор IQ дисбалансу на базі ортогоналізації Ґрама-Шмідта
class IqCalibrator {
public:
    explicit constexpr IqCalibrator(float adaptation_rate = 0.0005f) noexcept
        : mu_{adaptation_rate} {}

    void process(std::span<std::complex<float>> samples) noexcept {
        for (auto& sample : samples) {
            const float i_in = sample.real();
            const float q_in = sample.imag();

            // Оновлення ковзних оцінок потужностей та взаємної кореляції
            p_i_  = (1.0f - mu_) * p_i_  + mu_ * (i_in * i_in);
            p_q_  = (1.0f - mu_) * p_q_  + mu_ * (q_in * q_in);
            p_iq_ = (1.0f - mu_) * p_iq_ + mu_ * (i_in * q_in);

            if (p_i_ > 1e-9f && p_q_ > 1e-9f) {
                c_phase_ = p_iq_ / p_i_;
                c_gain_  = std::sqrt(p_i_ / p_q_);
            }

            // Корекція фазового та амплітудного розбалансу
            const float i_corr = i_in;
            const float q_corr = (q_in - c_phase_ * i_in) * c_gain_;

            sample = {i_corr, q_corr};
        }
    }

    [[nodiscard]] std::pair<float, float> current_coefficients() const noexcept {
        return {c_phase_, c_gain_};
    }

private:
    float mu_;
    float p_i_{1.0f};
    float p_q_{1.0f};
    float p_iq_{0.0f};
    float c_phase_{0.0f};
    float c_gain_{1.0f};
};

// Повний тракт базової обробки Zero-IF
class ZeroIfBasebandProcessor {
public:
    explicit ZeroIfBasebandProcessor(float dcoc_alpha = 0.001f, float iq_mu = 0.0005f)
        : dcoc_{dcoc_alpha}, iq_calib_{iq_mu} {}

    void process_frame(std::span<std::complex<float>> buffer) noexcept {
        dcoc_.process(buffer);
        iq_calib_.process(buffer);
    }

private:
    DcocFilter dcoc_;
    IqCalibrator iq_calib_;
};

} // namespace zero_if
```
:::

### Оптимізація обчислень у фіксованій крапці (Fixed-Point DSP)

У багатьох недорогих мікроконтролерах без розширення двійкової арифметики з плаваючою крапкою (FPU) обчислення дробових типів `float` виконуються через програмну емуляцію. Це споживає десятки тактів процесора на кожну математичну операцію. Для забезпечення роботи реального часу на високих частотах дискретизації (наприклад, 10–20 МГц) алгоритми DCOC та IQ калібрування переводять у формат фіксованої крапки **Q15** або **Q31**.

У форматі **Q15** 16-бітна цілочисельна змінна `int16_t` представляє дробове число у діапазоні від `-1.0` до `+0.999969` із кроком `1 / 32768`. Операція ділення та множення на коефіцієнт `α = 2^-k` замінюється надшвидкою арифметичною операцією побітового зсуву праворуч (`>> k`).

:::tabs
@tab C
```c
#include <stdint.h>

/* Стан фільтра DCOC Q15 */
typedef struct {
    int32_t acc_i;
    int32_t acc_q;
    uint8_t shift_k;
} dcoc_q15_t;

void dcoc_q15_init(dcoc_q15_t *dcoc, uint8_t shift_k) {
    dcoc->acc_i = 0;
    dcoc->acc_q = 0;
    dcoc->shift_k = shift_k;
}

/* Кроковий обчислювач DCOC у форматі Q15 */
void dcoc_q15_process(dcoc_q15_t *dcoc, int16_t *i_buf, int16_t *q_buf, size_t count) {
    const uint8_t k = dcoc->shift_k;

    for (size_t n = 0; n < count; ++n) {
        dcoc->acc_i += (int32_t)i_buf[n] - (dcoc->acc_i >> k);
        dcoc->acc_q += (int32_t)q_buf[n] - (dcoc->acc_q >> k);

        i_buf[n] -= (int16_t)(dcoc->acc_i >> k);
        q_buf[n] -= (int16_t)(dcoc->acc_q >> k);
    }
}
```

@tab C++
```cpp
#include <cstdint>
#include <span>
#include <complex>

namespace zero_if {

// Q15 фіксований фільтр DCOC для вбудованих мікроконтролерів без FPU
template <uint8_t ShiftK = 9>
class FixedDcocFilterQ15 {
public:
    constexpr FixedDcocFilterQ15() noexcept = default;

    void process(std::span<std::complex<int16_t>> samples) noexcept {
        for (auto& sample : samples) {
            acc_i_ += static_cast<int32_t>(sample.real()) - (acc_i_ >> ShiftK);
            acc_q_ += static_cast<int32_t>(sample.imag()) - (acc_q_ >> ShiftK);

            const auto mean_i = static_cast<int16_t>(acc_i_ >> ShiftK);
            const auto mean_q = static_cast<int16_t>(acc_q_ >> ShiftK);

            sample = {static_cast<int16_t>(sample.real() - mean_i),
                      static_cast<int16_t>(sample.imag() - mean_q)};
        }
    }

private:
    int32_t acc_i_{0};
    int32_t acc_q_{0};
};

} // namespace zero_if
```
:::

Використання 32-бітного акумулятора `acc_i` є обов'язковим для запобігання накопиченню помилок квантування та округлення низьких розрядів, які можуть викликати паразитні самозбудження фільтра DCOC.

### Інтеграція алгоритмів у сучасні радіочипи (AD9361/RTL-SDR)

У промислових інтегральних SDR-трансиверах (таких як Analog Devices AD9361 або AD9371) описані цифро-аналогові алгоритми підтримуються на апаратному рівні за допомогою вбудованих реконфігурованих цифрових блоків.

Конфігурація цифрового тракту реалізується через набір внутрішніх регістрів:
- **Регістр контролю DCOC (0x012)**: перемикає режими між автономним відслідковуванням (*Manual/Automatic Tracking*) та режимом швидкого перезахоплення (*Fast Attack*).
- **Регістри оцінки IQ дисбалансу (0x0A0 - 0x0A5)**: зберігають обчислені матричні коефіцієнти компенсації фазової та амплітудної асиметрії для передачі у вбудований цифровий помножувач.

Завдяки суміщенню аналогових диференціальних підсилювачів та апаратних цифрових DSP-коректорів сучасні Zero-IF трансивери забезпечують приглушення дзеркального каналу на рівні понад `65 дБ` та підтримують динамічний діапазон за DC offset у межах `80 дБ`.
