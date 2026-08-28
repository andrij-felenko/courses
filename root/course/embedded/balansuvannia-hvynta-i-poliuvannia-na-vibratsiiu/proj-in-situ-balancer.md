# ⚙️ Програма динамічного балансування мотора на стенді

Динамічне балансування ротора безпосередньо на стенді або промені дрона (In-Situ Dynamic Balancing) — це процес, що перетворює пару синхронізованих у часі сирих сигналів (віброприскорення з акселерометра та імпульси нульової фази від оптичного тахометра) на точні координати коригувального тягарця: його масу в міліграмах і кут установки в градусах. Нижче розібрано повну інженерну реалізацію такого вимірювального конвеєра на мовах C та C++, готову до роботи як на вбудованому мікроконтролері (STM32 / ESP32), так і на стендовому ПК.

### Архітектура вимірювального тракту стенда

Стенд динамічного балансування складається з трьох ключових апаратних вузлів:
1. **Датчик вібрації**: аналоговий або цифровий MEMS-акселерометр із частотою опитування 4–10 кГц, жорстко закріплений на моторній опорі перпендикулярно до осі вала.
2. **Фазовий маркер**: оптичний відбивний датчик (ІЧ-оптопара) або датчик Холла, який фіксує білу смужку на дзвоні мотора та видає короткий логічний імпульс (Rising Edge) рівно один раз за оберт ротора.
3. **Обчислювальний модуль**: процесор, що синхронізує вибірки вібрації з моментами спрацьовування фазового маркера.

```
┌─────────────────┐       Миттєве прискорення a(t)
│  Акселерометр   ├──────────────────────────────────────┐
└─────────────────┘                                      │
                                                         ▼
┌─────────────────┐   Імпульс нульової фази 0°   ┌──────────────────────────────┐   Параметри тягарця:
│ Оптичний маркер ├─────────────────────────────►│ Синхронний фазовий детектор  ├──► Маса:  104.1 мг
└─────────────────┘   (T_rev -> RPM)             │ Квадратурне інтегрування     │   Кут:   32.0 град
                                                 └──────────────────────────────┘
```

Головна перевага спеціалізованого фазового детектора над універсальним швидким перетворенням Фур'є (ШПФ) при стендовому балансуванні — **вибіркова фільтрація та нульовий витік спектра**. Повне ШПФ розкладає сигнал на сотні частотних бінів, вимагаючи великого буфера пам'яті й фіксованої сітки частот `f_s / N`. Синхронний фазовий детектор обчислює інтеграл Фур'є рівно для однієї частоти обертання вала `f_r`, синхронізованої з оптичним датчиком:

```
Re(V) = (2/T) · ∫ a(t) · cos(2π · f_r · t) · w(t) dt
Im(V) = (2/T) · ∫ a(t) · sin(2π · f_r · t) · w(t) dt
```

де `w(t)` — віконна функція Ганна, яка усуває крайові стрибки на границях вибірки. Таке квадратурне множення повністю пригнічує гармоніки комутації ESC, високочастотний писк ШІМ та шум підшипників, виділяючи чисту синусоїду дисбалансу `1× RPM`.

### Нормалізація амплітуди та вікно Ганна

Пряме застосування вікна Ганна `w[i] = 0.5 · (1 − cos(2π·i / (N − 1)))` зменшує сумарну енергію сигналу, оскільки краї буфера притискаються до нуля. Когерентний коефіцієнт підсилення (англ. *coherent gain*) для вікна Ганна дорівнює `0.5`, тобто амплітуда розрахованої синусоїди падає вдвічі порівняно зі справжнім фізичним сигналом.

Для відновлення істинної амплітуди віброприскорення дискретна сума множиться на коригувальний коефіцієнт масштабування:
```
scale = 2 / (Coherent_Gain · N) = 2 / (0.5 · N) = 4 / N
```
Завдяки цьому коефіцієнту `4 / N` порахований модуль комплексного вектора `|V_0|` точно дорівнює амплітудному значенню прискорення в м/с² або `g`, незалежно від розміру буфера `N`.

### Часовий джиттер та фазова точність

Точність визначення кута дисбалансу `θ_c` прямо залежить від стабільності часових міток оптичного маркера.

Припустимо, мотор обертається зі швидкістю 20 000 об/хв (`f_r = 333.3` Гц). Період одного повного оберту становить:
```
T_rev = 1 / 333.3 Гц = 3.0 мс = 3000 мкс
```
Один градус повороту ротора відповідає часовому інтервалу:
```
Δt_1deg = 3000 мкс / 360° ≈ 8.33 мкс
```

Якщо обробка переривання GPIO оптичного датчика в операційній системі або мікроконтролері має часовий джиттер (невизначеність затримки виклику ISR) величиною `10 мкс`, фазова похибка визначення вектора становитиме:
```
Похибка фази = 10 мкс / 8.33 мкс/град ≈ 1.2°
```
Похибка в 1.2° є цілком допустимою для динамічного балансування (вона забезпечує залишковий дисбаланс менше 2–3%). Проте якщо використовувати опитування датчика через неблокуючий polling у повільному головному циклі з періодом 1 мс, фазова помилка сягне `1000 / 8.33 = 120°`, що повністю зруйнує векторний розрахунок. Тому захоплення мітки тахометра **завжди виконується апаратним таймером** (Input Capture) або швидким апаратним перериванням із найвищим пріоритетом.

### Числова стабільність та захист від ділення на нуль

У вбудованих обчисленнях одинарної точності (`float32`) різниця двох близьких векторів `ΔV = V_1 − V_0` може втрачати точність, якщо пробний вантаж викликав надто слабкий відгук або випадково відлетів під дією відцентрової сили під час розгону.

Програма обов'язково перевіряє модуль приросту вібрації: якщо `|ΔV| < 10⁻⁶` м/с², алгоритм не намагається обчислювати дріб `Uc = −V0 / S`, оскільки знаменник прямує до нуля, а результуюча маса прямувала б до нескінченності. Замість аварійної зупинки чи генерації значень `NaN` (Not-a-Number), функція повертає ознаку помилки калібрування, сигналізуючи оператору про необхідність збільшити масу пробного тягарця або перевірити надійність його кріплення на роторі.

### Покроковий протокол роботи зі стендом

Програма реалізує стандартний двопрогінний алгоритм коефіцієнтів впливу:
1. **Крок 1 (Базовий замір).** Мотор розкручується до стабільних робочих обертів (наприклад, 12 000 об/хв). Програма накопичує буфер із 1024–2048 вибірок, обчислює базовий вектор вібрації `V_0` та виводить його модуль і фазу.
2. **Крок 2 (Калібрувальний замір).** Мотор зупиняють. На ротор у точці нульової фазової мітки (`θ_t = 0°`) наклеюють пробний вантаж відомої маси `m_t` (наприклад, 100 мг пластиліну чи алюмінієвого скотчу). Мотор повторно запускають на тій самій швидкості. Програма вимірює новий вектор `V_1`.
3. **Крок 3 (Векторний розрахунок).** Програма обчислює вектор відгуку `ΔV = V_1 − V_0`. Якщо `|ΔV|` перевищує поріг чутливості, модуль розраховує комплексний коефіцієнт передачі `S = ΔV / U_t` та формує вихідну команду для оператора.
4. **Крок 4 (Фіксація постійного вантажу).** Оператор знімає тимчасовий пробний вантаж і закріплює постійний балансувальний вантаж розрахованої маси `m_c` під вказаним кутом `θ_c`.
5. **Крок 5 (Контрольний прогін).** Контрольний замір підтверджує залишковий рівень вібрацій (зазвичай спостерігається падіння амплітуди на 85–95%).

### Реалізація на C та C++

Нижче наведено повний вихідний код програми. Версія на C орієнтована на ефективне вбудоване виконання без динамічного виділення пам'яті в гарячому циклі. Версія на C++20 використовує строгу типізацію, контейнери `std::vector`, представлення `std::span`, стандартні комплексні типи `std::complex` та безпечну обробку помилок через `std::optional`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define M_PI_F 3.14159265358979323846f

typedef struct {
    float real;
    float imag;
} ComplexVec;

typedef struct {
    float mass_mg;
    float angle_deg;
    float residual_amp;
} BalanceResult;

static inline ComplexVec complex_make(float r, float i) {
    ComplexVec v = { .real = r, .imag = i };
    return v;
}

static inline ComplexVec complex_sub(ComplexVec a, ComplexVec b) {
    return complex_make(a.real - b.real, a.imag - b.imag);
}

static inline ComplexVec complex_div(ComplexVec a, ComplexVec b) {
    float denom = b.real * b.real + b.imag * b.imag;
    if (denom < 1e-12f) return complex_make(0.0f, 0.0f);
    return complex_make((a.real * b.real + a.imag * b.imag) / denom,
                        (a.imag * b.real - a.real * b.imag) / denom);
}

static inline float complex_mag(ComplexVec v) {
    return sqrtf(v.real * v.real + v.imag * v.imag);
}

static inline float complex_arg_deg(ComplexVec v) {
    float deg = atan2f(v.imag, v.real) * (180.0f / M_PI_F);
    if (deg < 0.0f) deg += 360.0f;
    return deg;
}

// Виділення амплітуди й фази гармоніки 1x RPM синхронним фазовим детектором
ComplexVec extract_1x_vector(const float *samples, size_t num_samples, 
                             float sample_rate, float rpm_freq) {
    float sum_cos = 0.0f;
    float sum_sin = 0.0f;
    float dt = 1.0f / sample_rate;
    float omega = 2.0f * M_PI_F * rpm_freq;

    for (size_t i = 0; i < num_samples; i++) {
        float t = (float)i * dt;
        float phase = omega * t;
        // Вікно Ганна для усунення крайових стрибків
        float w = 0.5f * (1.0f - cosf(2.0f * M_PI_F * (float)i / (float)(num_samples - 1)));
        float val = samples[i] * w;

        sum_cos += val * cosf(phase);
        sum_sin += val * sinf(phase);
    }

    // Нормалізація амплітуди з урахуванням втрат вікна Ганна (множник 4/N)
    float scale = 4.0f / (float)num_samples;
    return complex_make(sum_cos * scale, sum_sin * scale);
}

// Розрахунок параметрів коригувального вантажу
BalanceResult calculate_correction(ComplexVec v0, ComplexVec v1, 
                                   float trial_mass_mg, float trial_angle_deg) {
    BalanceResult res;
    ComplexVec delta_v = complex_sub(v1, v0);
    float delta_mag = complex_mag(delta_v);

    if (delta_mag < 1e-6f) {
        // Пробний вантаж не спричинив змін — недостатня маса або механічне заклинювання
        res.mass_mg = 0.0f;
        res.angle_deg = 0.0f;
        res.residual_amp = complex_mag(v0);
        return res;
    }

    // Вектор дисбалансу пробного вантажу
    float rad_t = trial_angle_deg * (M_PI_F / 180.0f);
    ComplexVec ut = complex_make(trial_mass_mg * cosf(rad_t), trial_mass_mg * sinf(rad_t));

    // Коефіцієнт впливу S = delta_V / Ut
    ComplexVec sens = complex_div(delta_v, ut);

    // Коригувальний дисбаланс Uc = -V0 / S
    ComplexVec neg_v0 = complex_make(-v0.real, -v0.imag);
    ComplexVec uc = complex_div(neg_v0, sens);

    res.mass_mg = complex_mag(uc);
    res.angle_deg = complex_arg_deg(uc);
    res.residual_amp = 0.0f; // Теоретичний ідеальний залишок

    return res;
}

int main(void) {
    const float fs = 8000.0f;      // Частота дискретизації АЦП: 8 кГц
    const float f_rpm = 200.0f;    // 12000 RPM = 200 Гц
    const size_t n = 2048;         // Розмір вибірки аналізу
    float samples_run0[2048];
    float samples_run1[2048];

    // Моделювання сирого сигналу для базового пуску: V0 = 12.0 м/с² під 40°
    for (size_t i = 0; i < n; i++) {
        float t = (float)i / fs;
        float p0 = 2.0f * M_PI_F * f_rpm * t + 40.0f * (M_PI_F / 180.0f);
        samples_run0[i] = 12.0f * cosf(p0) + 1.2f * sinf(2.0f * M_PI_F * 600.0f * t);
    }

    // Моделювання для пуску з пробним вантажем 100 мг на 0°: V1 = 6.5 м/с² під 110°
    for (size_t i = 0; i < n; i++) {
        float t = (float)i / fs;
        float p1 = 2.0f * M_PI_F * f_rpm * t + 110.0f * (M_PI_F / 180.0f);
        samples_run1[i] = 6.5f * cosf(p1) + 1.1f * sinf(2.0f * M_PI_F * 600.0f * t);
    }

    ComplexVec v0 = extract_1x_vector(samples_run0, n, fs, f_rpm);
    ComplexVec v1 = extract_1x_vector(samples_run1, n, fs, f_rpm);

    printf("Базовий вектор V0:    |V0| = %6.2f m/s^2, phi = %5.1f deg\n",
           complex_mag(v0), complex_arg_deg(v0));
    printf("Вектор з вантажем V1: |V1| = %6.2f m/s^2, phi = %5.1f deg\n",
           complex_mag(v1), complex_arg_deg(v1));

    BalanceResult sol = calculate_correction(v0, v1, 100.0f, 0.0f);

    printf("\n=== РЕЗУЛЬТАТ ДИНАМІЧНОГО БАЛАНСУВАННЯ ===\n");
    printf("1. Зніміть пробний вантаж (100.0 мг на 0.0 deg).\n");
    printf("2. Встановіть балансувальний вантаж:\n");
    printf("   -> Маса тягарця:  %6.1f мг\n", sol.mass_mg);
    printf("   -> Кут установки: %6.1f градусів від мітки\n", sol.angle_deg);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <span>
#include <optional>
#include <iomanip>

struct BalanceCorrection {
    float mass_mg;
    float angle_deg;
};

class InSituDynamicBalancer {
public:
    explicit InSituDynamicBalancer(float sample_rate_hz)
        : sample_rate_{sample_rate_hz} {}

    // Виділення вектора 1x RPM синхронним квадратурним інтегруванням
    [[nodiscard]] std::complex<float> extractHarmonicVector(
        std::span<const float> samples, float rotation_freq_hz) const {
        
        if (samples.empty() || rotation_freq_hz <= 0.0f) {
            return {0.0f, 0.0f};
        }

        const float dt = 1.0f / sample_rate_;
        const float omega = 2.0f * std::numbers::pi_v<float> * rotation_freq_hz;
        const size_t n = samples.size();

        float sum_cos = 0.0f;
        float sum_sin = 0.0f;

        for (size_t i = 0; i < n; ++i) {
            const float t = static_cast<float>(i) * dt;
            const float phase = omega * t;
            // Вікно Ганна
            const float window = 0.5f * (1.0f - std::cos(2.0f * std::numbers::pi_v<float> * static_cast<float>(i) / static_cast<float>(n - 1)));
            const float val = samples[i] * window;

            sum_cos += val * std::cos(phase);
            sum_sin += val * std::sin(phase);
        }

        const float scale = 4.0f / static_cast<float>(n);
        return {sum_cos * scale, sum_sin * scale};
    }

    // Векторний розрахунок компенсації
    [[nodiscard]] std::optional<BalanceCorrection> computeCorrection(
        std::complex<float> base_vec_v0,
        std::complex<float> trial_vec_v1,
        float trial_mass_mg,
        float trial_angle_deg) const {

        const auto delta_v = trial_vec_v1 - base_vec_v0;
        if (std::abs(delta_v) < 1e-6f) {
            return std::nullopt; // Відсутній вимірний відгук
        }

        const float rad_t = trial_angle_deg * (std::numbers::pi_v<float> / 180.0f);
        const std::complex<float> u_trial = std::polar(trial_mass_mg, rad_t);

        // Чутливість системи S = delta_V / U_trial
        const auto sensitivity = delta_v / u_trial;

        // Коригувальний дисбаланс U_corr = -V0 / S
        const auto u_corr = -base_vec_v0 / sensitivity;

        float angle_deg = std::arg(u_corr) * (180.0f / std::numbers::pi_v<float>);
        if (angle_deg < 0.0f) {
            angle_deg += 360.0f;
        }

        return BalanceCorrection{
            .mass_mg = std::abs(u_corr),
            .angle_deg = angle_deg
        };
    }

private:
    float sample_rate_;
};

int main() {
    constexpr float sample_rate = 8000.0f;
    constexpr float rpm_freq = 200.0f; // 12000 RPM
    constexpr size_t num_samples = 2048;

    std::vector<float> run0(num_samples);
    std::vector<float> run1(num_samples);

    // Моделювання базового прогону (12 м/с², 40 град)
    for (size_t i = 0; i < num_samples; ++i) {
        float t = static_cast<float>(i) / sample_rate;
        float phase0 = 2.0f * std::numbers::pi_v<float> * rpm_freq * t + 40.0f * (std::numbers::pi_v<float> / 180.0f);
        run0[i] = 12.0f * std::cos(phase0) + 1.2f * std::sin(2.0f * std::numbers::pi_v<float> * 600.0f * t);
    }

    // Моделювання прогону з пробним вантажем 100 мг на 0 град (6.5 м/с², 110 град)
    for (size_t i = 0; i < num_samples; ++i) {
        float t = static_cast<float>(i) / sample_rate;
        float phase1 = 2.0f * std::numbers::pi_v<float> * rpm_freq * t + 110.0f * (std::numbers::pi_v<float> / 180.0f);
        run1[i] = 6.5f * std::cos(phase1) + 1.1f * std::sin(2.0f * std::numbers::pi_v<float> * 600.0f * t);
    }

    InSituDynamicBalancer balancer(sample_rate);
    auto v0 = balancer.extractHarmonicVector(run0, rpm_freq);
    auto v1 = balancer.extractHarmonicVector(run1, rpm_freq);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Базовий вектор V0:    |" << std::abs(v0) << "| m/s^2, кут: "
              << (std::arg(v0) * 180.0f / std::numbers::pi_v<float>) << " deg\n";
    std::cout << "Вектор з вантажем V1: |" << std::abs(v1) << "| m/s^2, кут: "
              << (std::arg(v1) * 180.0f / std::numbers::pi_v<float>) << " deg\n";

    if (auto result = balancer.computeCorrection(v0, v1, 100.0f, 0.0f)) {
        std::cout << "\n=== РЕЗУЛЬТАТ БАЛАНСУВАННЯ ===\n";
        std::cout << "1. Зніміть пробний вантаж.\n";
        std::cout << "2. Закріпіть постійний вантаж:\n";
        std::cout << "   -> Маса: " << result->mass_mg << " мг\n";
        std::cout << "   -> Кут:  " << result->angle_deg << " градусів\n";
    } else {
        std::cerr << "Помилка розрахунку: відгук системи нижче рівня шуму.\n";
    }

    return 0;
}
```
:::
