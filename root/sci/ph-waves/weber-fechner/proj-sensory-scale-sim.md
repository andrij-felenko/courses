# ⚙️ Моделювання сенсорної адаптації та шкал сприйняття

Ця вставка містить практичні програмні моделі обчислення логарифмічного відчуття за законом Вебера–Фехнера, генерацію послідовних ступенів ледве помітної відмінності (JND), нелінійне компандування аудіосигналів, гамма-корекцію зображень у форматі sRGB та порівняльний аналіз динамічного стиснення діапазону сигналів мовами C, C++ та Python.

## 1. Архітектурні задачі та алгоритмічні принципи

При розробці цифрових систем обробки сигналів, звукових двигунів, графічних рендерерів та медичного вимірювального обладнання виникає фундаментальна задача перетворення фізичних величин (амплітуди звукового тиску, світлового потоку, механічного тиску) у суб'єктивно рівномірні координати сприйняття або стиснення динамічного діапазону перед передачею через обмежені аналого-цифрові канали.

У цій практичній моделі ми розробляємо чотири взаємопов'язані алгоритмічні модулі:

### Модуль 1: Обчислювач Вебера–Фехнера та Стівенса з чисельною стабілізацією
Пряме обчислення виразу `S = k · ln(I / I₀)` за допомогою стандартної функції `log(x)` стає чисельно нестабільним, коли інтенсивність стимулу `I` знаходиться дуже близько до абсолютно порогу чутливості `I₀`. У такому випадку відношення `I / I₀` прямує до `1.0`, а значення `I / I₀ - 1` втрачає молодші розряди мантиси через обмеження плаваючої коми.

Для усунення цього ефекту алгоритм переписує аргумент у формі відносного перевищення порогу `x = (I - I₀) / I₀` і використовує спеціалізовану математичну функцію `log1p(x) = ln(1 + x)`. Це гарантує збереження повної точності розрядів навіть при відносних приростах порядку `10⁻¹⁵`. Паралельно реалізовано обчислення степенного закону Стівенса `S = k · (I - I₀)ⁿ` для порівняння двох шкал.

### Модуль 2: Генератор послідовних ступенів JND (Just-Noticeable Difference)
Для тестування психофізичних порогів або побудови дискретних шкал регулювання (наприклад, кроків підсилювача звуку чи зсуву яскравості дисплея) необхідно згенерувати послідовність стимулів, у якій кожен наступний рівень відрізняється від попереднього на одну ледве помітну відмінність.

За законом Вебера `ΔI / I = k_W`, отже наступне значення стимулу дорівнює `I_{n+1} = I_n + ΔI = I_n · (1 + k_W)`. Послідовність стимулів утворює геометричну прогресію у фізичному просторі. У логарифмічному просторі сприйняття ці кроки розташовані на абсолютно однаковій відстані один від одного. Алгоритм будує цей масив із захистом від виходу за межі виділеного буфера.

### Модуль 3: Гамма-перетворення sRGB (OETF та EOTF)
Людське око значно чутливіше до відносних змін яскравості у темних ділянках зображення, ніж у світлих. Якби значення кольору зберігалися в кодових числах від 0 до 255 лінійно, 8-бітний кодер демонстрував би виражений бандинг (смугастість) у тінях.

Передавальна функція оптоелектронного перетворення (OETF) sRGB нелінійно мапує лінійну яскравість `L ∈ [0, 1]` у кодове значення sRGB. Вона складається з лінійної ділянки поблизу нуля (для пригнічення шуму) та степенної ділянки з показником `1/2.4 ≈ 0.42` (що дуже близько до степенного закону Стівенса для яскравості `n ≈ 0.33`):

- Якщо `L ≤ 0.0031308`: `V_sRGB = 12.92 · L`
- Якщо `L > 0.0031308`: `V_sRGB = 1.055 · L^(1/2.4) - 0.055`

### Модуль 4: Компресор динамічного діапазону (DRC)
У цифровій обробці звуку компресор вимірює огинаючу сигналу в логарифмічній шкалі децибел `L_dB = 20 · log10(|x| / A_ref)`. Якщо рівень сигналу перевищує заданий поріг `Threshold_dB`, компресор зменшує приріст сигналу в `Ratio` разів, реалізуючи дробове стиснення Вебера–Фехнера в реальному часі.

## 2. Реалізація у коді

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Модель Вебера-Фехнера та Стівенса */
typedef struct {
    double i_zero;     /* Абсолютний поріг чутливості I0 */
    double k_weber;    /* Константа Вебера kW (ΔI / I) */
    double k_scale;    /* Масштабний коефіцієнт k */
    double stevens_n;  /* Показник степеня Стівенса n */
} SensoryModel;

/* Захищене обчислення логарифмічного відчуття за Вебером-Фехнером */
double calculate_weber_fechner(const SensoryModel *model, double intensity) {
    if (!model || intensity <= model->i_zero) {
        return 0.0;
    }
    /* Використовуємо log1p для підвищення точності поблизу порогу I0 */
    double delta_ratio = (intensity - model->i_zero) / model->i_zero;
    return model->k_scale * log1p(delta_ratio);
}

/* Обчислення відчуття за степенним законом Стівенса */
double calculate_stevens(const SensoryModel *model, double intensity) {
    if (!model || intensity <= model->i_zero) {
        return 0.0;
    }
    double delta = intensity - model->i_zero;
    return model->k_scale * pow(delta, model->stevens_n);
}

/* Генерація сітки JND ступенів у заданому діапазоні */
int generate_jnd_steps(const SensoryModel *model, double i_max, double *out_buffer, int max_size) {
    if (!model || !out_buffer || model->k_weber <= 0.0) {
        return -1;
    }

    double current_i = model->i_zero;
    int count = 0;

    while (current_i <= i_max && count < max_size) {
        out_buffer[count++] = current_i;
        current_i *= (1.0 + model->k_weber);
    }

    return count;
}

/* Перетворення лінійного світла у 8-бітний sRGB піксель (OETF) */
unsigned char linear_to_srgb_8bit(double linear_val) {
    if (linear_val <= 0.0) return 0;
    if (linear_val >= 1.0) return 255;

    double srgb;
    if (linear_val <= 0.0031308) {
        srgb = 12.92 * linear_val;
    } else {
        srgb = 1.055 * pow(linear_val, 1.0 / 2.4) - 0.055;
    }

    return (unsigned char)(srgb * 255.0 + 0.5);
}

int main(void) {
    SensoryModel vision_model = {
        .i_zero = 1.0e-5,
        .k_weber = 0.01,
        .k_scale = 10.0,
        .stevens_n = 0.33
    };

    printf("=== Моделювання сенсорних шкал (C) ===\n");
    double test_intensities[] = { 1.0e-5, 1.0e-4, 1.0e-3, 1.0e-2, 1.0 };
    size_t num_tests = sizeof(test_intensities) / sizeof(test_intensities[0]);

    for (size_t i = 0; i < num_tests; ++i) {
        double I = test_intensities[i];
        double S_wf = calculate_weber_fechner(&vision_model, I);
        double S_st = calculate_stevens(&vision_model, I);
        printf("I = %10.5f | S_Fechner = %8.4f | S_Stevens = %8.4f\n", I, S_wf, S_st);
    }

    double jnd_buffer[200];
    int steps = generate_jnd_steps(&vision_model, 1.0e-4, jnd_buffer, 200);
    printf("Згенеровано %d JND-ступенів від I0 до 1.0e-4\n", steps);

    printf("\nsRGB квантування яскравості:\n");
    double lum_values[] = { 0.001, 0.01, 0.1, 0.5, 1.0 };
    for (size_t i = 0; i < 5; ++i) {
        unsigned char p = linear_to_srgb_8bit(lum_values[i]);
        printf("Лінійна яскравість = %5.3f -> sRGB 8-bit = %3u\n", lum_values[i], p);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <span>
#include <expected>
#include <iomanip>
#include <algorithm>

class SensoryScaleCalculator {
public:
    struct Params {
        double i_zero{1.0e-5};   // Абсолютний поріг чутливості
        double k_weber{0.01};    // Відносний поріг Вебера
        double k_scale{10.0};    // Масштабний коефіцієнт
        double stevens_n{0.33};  // Показник степеня Стівенса
    };

    enum class Error {
        InvalidIntensity,
        InvalidWeberFraction,
        BufferTooSmall
    };

    explicit SensoryScaleCalculator(Params params) : params_(params) {}

    [[nodiscard]] double calculateFechner(double intensity) const noexcept {
        if (intensity <= params_.i_zero) {
            return 0.0;
        }
        double delta_ratio = (intensity - params_.i_zero) / params_.i_zero;
        return params_.k_scale * std::log1p(delta_ratio);
    }

    [[nodiscard]] double calculateStevens(double intensity) const noexcept {
        if (intensity <= params_.i_zero) {
            return 0.0;
        }
        return params_.k_scale * std::pow(intensity - params_.i_zero, params_.stevens_n);
    }

    [[nodiscard]] std::expected<std::vector<double>, Error> generateJndSteps(double max_intensity) const {
        if (params_.k_weber <= 0.0) {
            return std::unexpected(Error::InvalidWeberFraction);
        }
        if (max_intensity < params_.i_zero) {
            return std::unexpected(Error::InvalidIntensity);
        }

        std::vector<double> steps;
        double current_i = params_.i_zero;

        while (current_i <= max_intensity) {
            steps.push_back(current_i);
            current_i *= (1.0 + params_.k_weber);
        }

        return steps;
    }

    [[nodiscard]] static uint8_t linearToSrgb8Bit(double linear_val) noexcept {
        if (linear_val <= 0.0) return 0;
        if (linear_val >= 1.0) return 255;

        double srgb = (linear_val <= 0.0031308) 
            ? (12.92 * linear_val) 
            : (1.055 * std::pow(linear_val, 1.0 / 2.4) - 0.055);

        return static_cast<uint8_t>(std::clamp(srgb * 255.0 + 0.5, 0.0, 255.0));
    }

private:
    Params params_;
};

int main() {
    SensoryScaleCalculator::Params vision_params{
        .i_zero = 1.0e-5,
        .k_weber = 0.01,
        .k_scale = 10.0,
        .stevens_n = 0.33
    };

    SensoryScaleCalculator calc(vision_params);

    std::cout << "=== Моделювання сенсорних шкал (C++) ===\n";
    const std::vector<double> test_intensities{1.0e-5, 1.0e-4, 1.0e-3, 1.0e-2, 1.0};

    for (double I : test_intensities) {
        double S_f = calc.calculateFechner(I);
        double S_s = calc.calculateStevens(I);
        std::cout << "I = " << std::setw(10) << std::fixed << std::setprecision(5) << I 
                  << " | S_Fechner = " << std::setw(8) << std::setprecision(4) << S_f
                  << " | S_Stevens = " << std::setw(8) << std::setprecision(4) << S_s << "\n";
    }

    auto steps_res = calc.generateJndSteps(1.0e-4);
    if (steps_res) {
        std::cout << "Згенеровано " << steps_res->size() << " JND-ступенів\n";
    }

    std::cout << "\nsRGB квантування яскравості:\n";
    const std::vector<double> luminances{0.001, 0.01, 0.1, 0.5, 1.0};
    for (double lum : luminances) {
        uint8_t px = SensoryScaleCalculator::linearToSrgb8Bit(lum);
        std::cout << "Лінійна = " << std::setw(5) << std::setprecision(3) << lum 
                  << " -> sRGB 8-bit = " << static_cast<int>(px) << "\n";
    }

    return 0;
}
```
```py
import math

class SensoryScaleCalculator:
    def __init__(self, i_zero: float = 1e-5, k_weber: float = 0.01, k_scale: float = 10.0, stevens_n: float = 0.33):
        self.i_zero = i_zero
        self.k_weber = k_weber
        self.k_scale = k_scale
        self.stevens_n = stevens_n

    def calculate_fechner(self, intensity: float) -> float:
        if intensity <= self.i_zero:
            return 0.0
        delta_ratio = (intensity - self.i_zero) / self.i_zero
        return self.k_scale * math.log1p(delta_ratio)

    def calculate_stevens(self, intensity: float) -> float:
        if intensity <= self.i_zero:
            return 0.0
        return self.k_scale * math.pow(intensity - self.i_zero, self.stevens_n)

    def generate_jnd_steps(self, max_intensity: float) -> list[float]:
        if self.k_weber <= 0:
            raise ValueError("Weber fraction must be positive")
        steps = []
        current_i = self.i_zero
        while current_i <= max_intensity:
            steps.append(current_i)
            current_i *= (1.0 + self.k_weber)
        return steps

    @staticmethod
    def linear_to_srgb_8bit(linear_val: float) -> int:
        if linear_val <= 0.0:
            return 0
        if linear_val >= 1.0:
            return 255
        if linear_val <= 0.0031308:
            srgb = 12.92 * linear_val
        else:
            srgb = 1.055 * math.pow(linear_val, 1.0 / 2.4) - 0.055
        return int(min(max(srgb * 255.0 + 0.5, 0.0), 255.0))

if __name__ == "__main__":
    calc = SensoryScaleCalculator(i_zero=1e-5, k_weber=0.01, k_scale=10.0, stevens_n=0.33)
    print("=== Моделювання сенсорних шкал (Python) ===")
    
    test_values = [1e-5, 1e-4, 1e-3, 1e-2, 1.0]
    for val in test_values:
        sf = calc.calculate_fechner(val)
        ss = calc.calculate_stevens(val)
        print(f"I = {val:10.5f} | S_Fechner = {sf:8.4f} | S_Stevens = {ss:8.4f}")

    jnd_steps = calc.generate_jnd_steps(1e-4)
    print(f"Згенеровано {len(jnd_steps)} JND-ступенів")

    print("\nsRGB квантування яскравості:")
    for lum in [0.001, 0.01, 0.1, 0.5, 1.0]:
        px = SensoryScaleCalculator.linear_to_srgb_8bit(lum)
        print(f"Лінійна = {lum:5.3f} -> sRGB 8-bit = {px:3d}")
```
:::

## 3. Аналіз розходжень та інженерні висновки

Аналіз роботи представлених програмних модулів демонструє кілька важливих біофізичних та обчислювальних закономірностей:

### 1. Ефект чисельної розбіжності при малих інтенсивностях
При зміні інтенсивності від `10⁻⁵` до `10⁻⁴` логарифмічне відчуття Фехнера зростає від `0.0` до `23.02`, демонструючи високу чутливість алгоритму до появи первинного сигналу над абсолютним порогом. У той самий час степенна функція Стівенса з `n = 0.33` дає значно плавніше зростання. Для систем комп'ютерного зору це означає, що логарифмічні LUT-таблиці є ефективнішими для виявлення слабких контрастів у тінях, тоді як степенні функції краще зберігають глобальний тональний баланс сценічного освітлення.

### 2. Квантування sRGB та контрастна чутливість
Результати обчислення функції `linear_to_srgb_8bit` показують, що лінійна яскравість `0.001` (всього 0.1% від максимуму) відображається у значення 8-бітного пікселя `p = 3`, а яскравість `0.01` (1%) — у `p = 25`. Це означає, що 10% усіх доступних кодових рівнів (від 0 до 25) виділено на кодування найнижчого 1% фізичної яскравості. Це повністю відповідає закону Вебера–Фехнера і запобігає виникненню видимих смуг квантування в тінях без збільшення розрядності кодера.

### 3. Оптимізація обчислювальної складності у реальному часі
У високопродуктивних обробниках аудіо або відео реального часу прямий виклик функцій `std::log()` або `std::pow()` на кожен піксель чи аудіосемпл є занадто дорогим. Для прискорення обчислень застосовують наближення за допомогою таблиць пошуку (Look-Up Tables, LUT) з інтерполяцією або апаратні інструкції швидкого наближення логарифма (наприклад, витягання експоненти з форматів `IEEE 754 float`). Оскільки геометрична прогресія JND перетворюється на арифметичну прогресію під час логарифмування, таблиці пошуку будуються з рівномірним кроком по логарифмічній осі.

### 4. Векторизація SIMD та кеш-пам'ять
Для потокової обробки відео у форматах 4K та 8K обчислення передавальних функцій EOTF/OETF виконують векторазовано за допомогою SIMD-інструкцій (AVX2, AVX-512 у x86 або NEON в ARM). Замість обчислення дробових степеней `pow(x, 1/2.4)` для кожного пікселя окремо, алгоритми завантажують попередньо обчислені 16-бітні LUT-таблиці розміром 65536 елементів у L1-кеш процесора (розмір таблиці 128 КБ). Це знижує обчислювальне навантаження з 40–50 тактів процесора на піксель до 1–2 тактів читання з кешу.

### 5. Обробка крайових випадків у реальних системах
Під час реалізації сенсорних алгоритмів у вбудованих системах (мікроконтролери, DSP) слід враховувати три основні крайові випадки:
- **Нульовий або від'ємний вхідний сигнал (`I ≤ 0`):** Фізичні сенсори під дією шуму або зсуву нуля можуть видавати від'ємні значення. Алгоритм зобов'язаний відсікати їх на рівні `I₀` перед логарифмуванням, інакше програма згенерує помилку `NaN` або `-INFINITY`.
- **Переповнення при великих `I`:** При значних стимулах вираз `(1 + k_W)^N` під час генерації JND-сітки може швидко перевищити діапазон `double`. У коді передбачено строгий контроль ліміту `i_max` та перевірку розміру масиву.
- **Динамічна адаптація порогу `I₀`:** У реальних рецепторах поріг чутливості `I₀` не є статичною константою — він повільно підлаштовується під середнє значення стимулу за останні кілька секунд (темнова та світлова адаптація). У високоточних моделях `I₀` реалізують як вихід низькочастотного фільтра першого порядку (IIR-фільтр).
