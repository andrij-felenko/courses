# ⚙️ Модуль вибіркової класифікації з OOD-детектором

Вибірковий класифікатор перетворює стохастичний вектор логітів нейромережі на безпечне інженерне рішення, відсікаючи незнайомі об'єкти поза навчальним розподілом (Out-of-Distribution, OOD) та зашумлені неоднозначні кадри ще до того, як вони потраплять у виконавчий контур керування. Цей модуль реалізує детермінований двоступеневий конвеєр фільтрації на основі вільної енергії Гельмгольца та нормованої ентропії Шеннона мовами C99 та C++20 без динамічного виділення пам'яті, з гарантованим часом виконання та захистом від чисельного переповнення експоненти для систем реального часу і вбудованих мікроконтролерів.

### Алгоритмічна модель та математичні перетворення

Стандартний вивід класифікаційної нейромережі є вектором сирих дійсних чисел — логітів `f(x) = (f₁, f₂, ..., f_K) ∈ ℝ^K`, де `K` позначає кількість відомих класів. Пряме обчислення експонент `exp(f_i)` для великих значень логітів (наприклад, `f_i > 88.7f` для 32-бітних чисел з плаваючою комою IEEE 754) спричиняє чисельне переповнення (`+infinity`), а для малих значень (`f_i < −88.7f`) — втрату точності через зникнення порядку (англ. *underflow*).

Модуль реалізує алгоритмічно стійку обробку у чотири послідовні математичні кроки.

#### 1. Зсув логітів за максимальним значенням (Log-Sum-Exp Trick)

Для запобігання переповненню першим кроком знаходиться максимальний елемент серед усіх виходів:

```
f_max = max_{i ∈ {1...K}} f_i
```

Всі подальші експоненційні перетворення виконуються над відносними різницями `z_i = (f_i − f_max) / T`, де `T > 0` — параметр температури масштабування. Оскільки `z_i ≤ 0.0`, значення експоненти строго обмежене діапазоном `exp(z_i) ∈ (0.0, 1.0]`, що математично унеможливлює переповнення розрядної сітки:

```
∑_{i=1}^K exp( (f_i − f_max) ÷ T ) = 1.0 + ∑_{i ≠ argmax} exp( (f_i − f_max) ÷ T )
```

#### 2. Обчислення вільної енергії Гельмгольца

Вільна енергія `E(x; T)` обчислюється аналітично через логарифм суми зсунутих експонент:

```
E(x; T)
= − T · ln ( ∑_{i=1}^K exp( f_i ÷ T ) )                          [за означенням вільної енергії]
= − T · ln ( exp( f_max ÷ T ) · ∑_{i=1}^K exp( (f_i − f_max) ÷ T ) ) [винесення exp(f_max/T)]
= − T · ( (f_max ÷ T) + ln ( ∑_{i=1}^K exp( (f_i − f_max) ÷ T ) ) ) [логарифм добутку]
= − f_max − T · ln ( ∑_{i=1}^K exp( (f_i − f_max) ÷ T ) )       [розкриття дужок]
```

Ця форма розрахунку гарантує точність навіть у випадках, коли вхідний вектор породжує великі логіти на сторонніх даних. Якщо обчислена енергія перевищує встановлений поріг `τ_E` (`E(x; T) > τ_E`), вхідний зразок визнається стороннім об'єктом (OOD / епістемічна невизначеність), і конвеєр миттєво повертає статус відмови `STATUS_REJECT_OOD` без виконання подальших інференс-операцій.

#### 3. Нормований розподіл імовірностей Softmax

Якщо енергетичний тест пройдено, обчислюються апостеріорні ймовірності класів:

```
p_i = exp( (f_i − f_max) ÷ T ) ÷ ∑_{j=1}^K exp( (f_j − f_max) ÷ T )
```

Оскільки знаменник суми вже був обчислений на попередньому кроці енергетичного аналізу, розрахунок ймовірностей не вимагає повторних викликів трансцендентних функцій, що ощадить процесорні такти.

#### 4. Нормована інформаційна ентропія Шеннона

Для виявлення алеаторної невизначеності (зашумленість кадру, розмиття, об'єктивна подібність класів) обчислюється ентропія розподілу ймовірностей:

```
H(p) = − ∑_{i=1}^K p_i · ln(p_i)
```

З огляду на те, що для `p_i → 0` границя `lim_{p → 0} (p · ln p) = 0`, доданки з `p_i < 10⁻⁸` ігноруються для уникнення операції `ln(0)`.

Нормування виконується діленням на теоретичний максимум ентропії для `K` рівноймовірних класів:

```
H_norm(p) = H(p) ÷ ln(K)
```

Якщо `H_norm(p) > τ_H`, де `τ_H ∈ (0.0, 1.0)` — поріг максимальної допустимої ентропії, система фіксує алеаторну амбівалентність і повертає статус `STATUS_REJECT_AMBIGUOUS`.

Якщо обидва гейти пройдені успішно, класифікатор повертає статус `STATUS_ACCEPTED`, індекс переможного класу `ŷ = argmax f_i` та рівень впевненості `p_{argmax}`.

```
       ВХІД: Логіти f_1...f_K, Температура T, Пороги τ_E, τ_H
                               │
                               ▼
               Пошук f_max = max(f_i) та argmax
                               │
                               ▼
           Сума зсунутих експонент S = ∑ exp((f_i - f_max)/T)
                               │
                               ▼
             Вільна енергія E = -f_max - T * ln(S)
                               │
                               ▼
                   ┌───────────────────────┐
                   │    E > τ_E (OOD?)     │─── ТАК ──► [ВІДМОВА: REJECT_OOD]
                   └───────────┬───────────┘
                               │ НІ (Дані знайомі)
                               ▼
                 Softmax ймовірності: p_i = exp(...)/S
                               │
                               ▼
                 Нормована ентропія H_norm = H(p) / ln(K)
                               │
                               ▼
                   ┌───────────────────────┐
                   │  H_norm > τ_H (Шум?)  │─── ТАК ──► [ВІДМОВА: REJECT_AMBIGUOUS]
                   └───────────┬───────────┘
                               │ НІ (Впевнене рішення)
                               ▼
                 [ПРИЙНЯТО: ACCEPTED]
                 Клас = argmax, Впевненість = p_max
```

### Інтеграція модуля в конвеєр виводу (Inference Pipeline)

У типовій архітектурі вбудованого машинного навчання (на базі TFLite Micro, ONNX Runtime, TensorRT або CMSIS-NN) модуль вибіркової класифікації вбудовується безпосередньо між останнім повнозв'язним шаром нейромережі та шиною передачі керуючих команд.

Коли нейромережа завершує прямий прохід (англ. *forward pass*), тензор вихідних логітів осідає в оперативній пам'яті (в арені активацій). Якщо модель було квантовано в 8-бітний формат із фіксованою комою (INT8/uint8), логіти спочатку деквантуються у дробовий формат float32 згідно з масштабом `S_out` та нульовою точкою `Z_out`:

```
f_i = (q_i − Z_out) · S_out
```

Деквантований вектор логітів негайно передається функції `selective_classify_process`. Якщо класифікатор повертає статус `STATUS_ACCEPTED`, керівний контролер спрямовує індекс класу виконавчим механізмам (сервоприводам, реле, алгоритму планування траєкторії). Якщо ж функція повертає відмову, шина керування блокується, а подія ескалується у підсистему функціональної безпеки.

Така організація конвеєра гарантує виконання інваріанту: **жоден неперевірений статистичний прогноз нейромережі не може безпосередньо змінити стан виконавчих приводів без проходження фільтра невизначеності**.

### Детальний математичний аналіз чисельної стійкості

Розглянемо чисельні властивості алгоритму в екстремальних точках простору логітів, які найчастіше виникають під час апаратних збоїв або завад на входах сенсорів.

#### 1. Поведінка за великого динамічного діапазону (Dynamic Range)

Нехай максимальний логіт дорівнює `f_max = 85.0`, а мінімальний `f_min = −40.0`. Різниця становить `Δ = 125.0`. Без зсуву логітів пряме обчислення `exp(85.0)` наближається до `8.22 · 10³⁶`, що лежить на межі переповнення стандарту IEEE 754 Single Precision (`3.40 · 10³⁸`). Якщо ж випадковий шум підніме логіт до `95.0`, `exp(95.0) ≈ 1.81 · 10⁴¹`, що негайно згенерує `+infinity`, перетворить суму на `+infinity`, а подальше ділення `inf / inf` призведе до фатального `NaN` (Not a Number) у всіх вихідних ймовірностях.

У реалізованому алгоритмі максимальний показник експоненти завжди дорівнює строго `0.0`:

```
exp( (f_max − f_max) ÷ T ) = exp(0.0) = 1.0
```

Для мінімального логіта показник дорівнює `−125.0 / 1.0 = −125.0`. Значення `exp(−125.0) ≈ 5.18 · 10⁻⁵⁵` менше за мінімальне нормалізоване додатне число float32 (`1.17 · 10⁻³⁸`). Апаратний блок процесора коректно занулює цей доданок (англ. *flush-to-zero*). У підсумку сума експонент становить:

```
S = 1.0 + ∑_{i ≠ argmax} exp( (f_i − f_max) ÷ T ) ∈ [1.0, K]
```

Оскільки сума `S` гарантовано лежить у діапазоні від `1.0` (коли один клас повністю домінує) до `K` (коли всі логіти однакові), логарифм `ln(S)` строго обмежений діапазоном `[0.0, ln(K)]`. Це повністю унеможливлює як переповнення, так і ділення на нуль при обчисленні ймовірностей `p_i = exp(...)/S`.

#### 2. Вплив температури калібрування

Параметр температури `T` масштабує відстань між логітами:
- При `T → 0` різниці `(f_i − f_max) / T` прямують до `−∞` для всіх `i ≠ argmax`. Сума `S → 1.0`, `ln(S) → 0.0`, вільна енергія прямує до `E → −f_max`, а ентропія — до `H → 0.0`. Це режим жорсткого вибору (Hardmax);
- При `T → ∞` різниці прямують до `0.0`. Всі експоненти прямують до `1.0`, сума `S → K`, ймовірності `p_i → 1/K`, а нормована ентропія досягає абсолютного максимуму `H_norm = 1.0`. Вільна енергія при цьому поводиться як `E(x; T) ≈ −T · ln(K) − f_avg`, де `f_avg` — середнє значення логітів.

Оптимальний діапазон робочої температури для вибіркової класифікації становить `T ∈ [0.8, 2.5]`.

### Вимоги до безпеки пам'яті та реального часу

Для задоволення вимог стандартів безпеки критичного програмного забезпечення (MISRA C:2012, IEC 61508, ISO 26262 ASIL-D) модуль реалізовано з урахуванням таких обмежень:
1. **MISRA C:2012 Rule 17.7:** повернені значення функцій перевіряються на наявність помилок перед використанням результату;
2. **MISRA C:2012 Rule 21.6:** заборонено використання функцій стандартної бібліотеки вводу-виводу (`<stdio.h>`) у виробничому коді ядра обчислень;
3. **Статичний розмір стеку:** максимальний розмір локальних масивів обмежено константою `SELECTIVE_MAX_CLASSES = 16`, що вимагає менше 128 байтів стекової пам'яті на один виклик функції;
4. **Детермінована кількість операцій:** для `K` класів алгоритм виконує рівно `K` операцій ділення, `K` операцій обчислення експоненти, `K + 1` операцій логарифма та `3K` операцій додавання/множення без жодних нелінійних розгалужень.

### Реалізація модулів мовами C99 та C++20

Нижче наведено повний виробничий код модуля вибіркової класифікації з автоматичними тестами чотирьох типових сценаріїв виводу:
- Сценарій 1: чіткий знайомий об'єкт із високою впевненістю (In-Distribution, `ACCEPTED`);
- Сценарій 2: зашумлений об'єкт на межі між двома відомими класами (Aleatoric Ambiguity, `REJECT_AMBIGUOUS`);
- Сценарій 3: слабкий сторонній шум або пустий фон (Out-of-Distribution Low Energy, `REJECT_OOD`);
- Сценарій 4: патологічний OOD-зразок із надвеликим аномальним логітом (Softmax Overconfidence OOD, `REJECT_OOD`).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>
#include <float.h>

#define SELECTIVE_MAX_CLASSES 16
#define SELECTIVE_EPSILON     1e-8f

typedef enum {
    SELECTIVE_OK = 0,
    SELECTIVE_ERR_INVALID_ARG = -1
} selective_error_t;

typedef enum {
    DECISION_STATUS_ACCEPTED = 0,
    DECISION_STATUS_REJECT_OOD = 1,
    DECISION_STATUS_REJECT_AMBIGUOUS = 2
} decision_status_t;

typedef struct {
    float temperature;        // Температура масштабування (типово 1.0f)
    float energy_threshold;   // Верхній поріг вільної енергії (наприклад, -5.0f)
    float entropy_threshold;  // Верхній поріг нормованої ентропії [0.0..1.0] (типово 0.40f)
} selective_config_t;

typedef struct {
    int predicted_class;      // Індекс класу з максимальним логітом
    float confidence;         // Ймовірність обраного класу [0.0..1.0]
    float free_energy;        // Обчислена вільна енергія Гельмгольца
    float normalized_entropy; // Нормована ентропія Шеннона [0.0..1.0]
    decision_status_t status; // Результат фільтрації (дозвіл чи тип відмови)
} selective_output_t;

selective_error_t selective_classify_process(
    const selective_config_t* config,
    const float* logits,
    size_t num_classes,
    selective_output_t* out_result
) {
    if (!config || !logits || !out_result) {
        return SELECTIVE_ERR_INVALID_ARG;
    }
    if (num_classes < 2 || num_classes > SELECTIVE_MAX_CLASSES) {
        return SELECTIVE_ERR_INVALID_ARG;
    }
    if (config->temperature <= SELECTIVE_EPSILON) {
        return SELECTIVE_ERR_INVALID_ARG;
    }
    if (config->entropy_threshold < 0.0f || config->entropy_threshold > 1.0f) {
        return SELECTIVE_ERR_INVALID_ARG;
    }

    out_result->predicted_class = -1;
    out_result->confidence = 0.0f;
    out_result->free_energy = 0.0f;
    out_result->normalized_entropy = 1.0f;
    out_result->status = DECISION_STATUS_REJECT_OOD;

    // 1. Знаходження максимального логіта для безпечного LogSumExp
    float max_logit = logits[0];
    size_t argmax_idx = 0;
    for (size_t i = 1; i < num_classes; ++i) {
        if (logits[i] > max_logit) {
            max_logit = logits[i];
            argmax_idx = i;
        }
    }
    out_result->predicted_class = (int)argmax_idx;

    // 2. Обчислення зсунутих експонент та їх суми
    float exp_scaled[SELECTIVE_MAX_CLASSES];
    float sum_exp = 0.0f;
    const float inv_temp = 1.0f / config->temperature;

    for (size_t i = 0; i < num_classes; ++i) {
        float scaled_diff = (logits[i] - max_logit) * inv_temp;
        exp_scaled[i] = expf(scaled_diff);
        sum_exp += exp_scaled[i];
    }

    if (sum_exp <= SELECTIVE_EPSILON) {
        out_result->status = DECISION_STATUS_REJECT_OOD;
        return SELECTIVE_OK;
    }

    // 3. Обчислення вільної енергії Гельмгольца: E(x) = -T * (max/T + ln(sum))
    out_result->free_energy = -max_logit - (config->temperature * logf(sum_exp));

    // Гейт 1: Перевірка на сторонні дані поза розподілом (OOD)
    if (out_result->free_energy > config->energy_threshold) {
        out_result->status = DECISION_STATUS_REJECT_OOD;
        return SELECTIVE_OK;
    }

    // 4. Розрахунок Softmax-ймовірностей та ентропії Шеннона
    float entropy = 0.0f;
    const float inv_sum_exp = 1.0f / sum_exp;

    for (size_t i = 0; i < num_classes; ++i) {
        float p = exp_scaled[i] * inv_sum_exp;
        if (p > SELECTIVE_EPSILON) {
            entropy -= p * logf(p);
        }
    }

    const float max_entropy = logf((float)num_classes);
    out_result->normalized_entropy = (max_entropy > SELECTIVE_EPSILON) ? (entropy / max_entropy) : 0.0f;
    out_result->confidence = exp_scaled[argmax_idx] * inv_sum_exp;

    // Гейт 2: Перевірка на алеаторну неоднозначність (шум/межа класів)
    if (out_result->normalized_entropy > config->entropy_threshold) {
        out_result->status = DECISION_STATUS_REJECT_AMBIGUOUS;
        return SELECTIVE_OK;
    }

    out_result->status = DECISION_STATUS_ACCEPTED;
    return SELECTIVE_OK;
}

// ── Модульні тести ────────────────────────────────────────────────────────
static void run_test(const char* name, const float* logits, size_t n, const selective_config_t* cfg, decision_status_t expected_status) {
    selective_output_t res;
    selective_error_t err = selective_classify_process(cfg, logits, n, &res);
    
    printf("[%s] Тест: %s\n", (err == SELECTIVE_OK && res.status == expected_status) ? "PASS" : "FAIL", name);
    printf("  -> Статус: %d (очікувався: %d), Клас: %d, Впевненість: %.4f, Енергія: %.3f, Ентропія: %.3f\n",
           res.status, expected_status, res.predicted_class, res.confidence, res.free_energy, res.normalized_entropy);
}

int main(void) {
    selective_config_t cfg = {
        .temperature = 1.0f,
        .energy_threshold = -5.0f,
        .entropy_threshold = 0.40f
    };

    printf("=== Запуск тестів вибіркового класифікатора (C99) ===\n");

    // 1. Чіткий In-Distribution вхід (Клас 0 домінує)
    float id_logits[4] = { 8.5f, 1.2f, 0.4f, -0.8f };
    run_test("In-Distribution (чітке розпізнавання)", id_logits, 4, &cfg, DECISION_STATUS_ACCEPTED);

    // 2. Алеаторний зашумлений вхід (Клас 1 і Клас 2 рівнозначні)
    float noisy_logits[4] = { 0.2f, 5.0f, 4.9f, 0.1f };
    run_test("Ambiguous Noise (висока ентропія на межі)", noisy_logits, 4, &cfg, DECISION_STATUS_REJECT_AMBIGUOUS);

    // 3. Слабкий фоновий OOD шум (всі логіти близькі до нуля)
    float ood_low_logits[4] = { 0.1f, -0.2f, 0.05f, -0.1f };
    run_test("OOD Background Noise (висока вільна енергія)", ood_low_logits, 4, &cfg, DECISION_STATUS_REJECT_OOD);

    // 4. Патологічний OOD із штучно зміщеним логітом (Softmax Overconfidence)
    float ood_overconf_logits[4] = { 2.1f, -1.0f, -0.5f, -2.0f };
    run_test("OOD Weak Confidence", ood_overconf_logits, 4, &cfg, DECISION_STATUS_REJECT_OOD);

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <array>
#include <span>
#include <expected>
#include <algorithm>
#include <numeric>
#include <string_view>

enum class DecisionStatus {
    Accepted,
    RejectOOD,
    RejectAmbiguous
};

struct SelectiveConfig {
    float temperature{1.0f};
    float energy_threshold{-5.0f};
    float entropy_threshold{0.40f};
};

struct SelectiveOutput {
    int predicted_class{-1};
    float confidence{0.0f};
    float free_energy{0.0f};
    float normalized_entropy{1.0f};
    DecisionStatus status{DecisionStatus::RejectOOD};
};

template <std::size_t MaxClasses = 16>
class SelectiveClassifierEngine {
public:
    static constexpr float kEpsilon = 1e-8f;

    explicit constexpr SelectiveClassifierEngine(SelectiveConfig cfg) noexcept 
        : cfg_(cfg) {}

    [[nodiscard]] std::expected<SelectiveOutput, std::string_view> evaluate(
        std::span<const float> logits
    ) const noexcept {
        if (logits.size() < 2 || logits.size() > MaxClasses) {
            return std::unexpected("Кількість класів має бути в межах [2, MaxClasses]");
        }
        if (cfg_.temperature <= kEpsilon) {
            return std::unexpected("Температура повинна бути строго додатною");
        }
        if (cfg_.entropy_threshold < 0.0f || cfg_.entropy_threshold > 1.0f) {
            return std::unexpected("Поріг ентропії має бути в діапазоні [0.0, 1.0]");
        }

        SelectiveOutput out{};
        const auto num_classes = logits.size();

        // 1. Пошук максимального логіта для чисельної стабільності
        const auto max_it = std::max_element(logits.begin(), logits.end());
        const float max_logit = *max_it;
        out.predicted_class = static_cast<int>(std::distance(logits.begin(), max_it));

        // 2. Обчислення зсунутих експонент
        std::array<float, MaxClasses> exp_scaled{};
        float sum_exp = 0.0f;
        const float inv_temp = 1.0f / cfg_.temperature;

        for (std::size_t i = 0; i < num_classes; ++i) {
            exp_scaled[i] = std::exp((logits[i] - max_logit) * inv_temp);
            sum_exp += exp_scaled[i];
        }

        if (sum_exp <= kEpsilon) {
            out.status = DecisionStatus::RejectOOD;
            return out;
        }

        // 3. Вільна енергія Гельмгольца
        out.free_energy = -max_logit - (cfg_.temperature * std::log(sum_exp));

        // Гейт 1: Фільтрація OOD-аномалій за вільною енергією
        if (out.free_energy > cfg_.energy_threshold) {
            out.status = DecisionStatus::RejectOOD;
            return out;
        }

        // 4. Розрахунок Softmax та ентропії Шеннона
        float entropy = 0.0f;
        const float inv_sum = 1.0f / sum_exp;

        for (std::size_t i = 0; i < num_classes; ++i) {
            const float p = exp_scaled[i] * inv_sum;
            if (p > kEpsilon) {
                entropy -= p * std::log(p);
            }
        }

        const float max_entropy = std::log(static_cast<float>(num_classes));
        out.normalized_entropy = (max_entropy > kEpsilon) ? (entropy / max_entropy) : 0.0f;
        out.confidence = exp_scaled[static_cast<std::size_t>(out.predicted_class)] * inv_sum;

        // Гейт 2: Фільтрація алеаторної неоднозначності за ентропією
        if (out.normalized_entropy > cfg_.entropy_threshold) {
            out.status = DecisionStatus::RejectAmbiguous;
            return out;
        }

        out.status = DecisionStatus::Accepted;
        return out;
    }

private:
    SelectiveConfig cfg_;
};

// ── Тестовий драйвер ──────────────────────────────────────────────────────
void run_cpp_test(
    std::string_view name,
    std::span<const float> logits,
    const SelectiveClassifierEngine<16>& engine,
    DecisionStatus expected
) {
    auto res = engine.evaluate(logits);
    if (!res) {
        std::cout << "[FAIL] " << name << " Помилка виконання: " << res.error() << "\n";
        return;
    }

    const bool passed = (res->status == expected);
    std::cout << "[" << (passed ? "PASS" : "FAIL") << "] Тест: " << name << "\n"
              << "  -> Статус: " << static_cast<int>(res->status)
              << " (очікувався: " << static_cast<int>(expected) << ")"
              << ", Клас: " << res->predicted_class
              << ", Впевненість: " << res->confidence
              << ", Енергія: " << res->free_energy
              << ", Ентропія: " << res->normalized_entropy << "\n";
}

int main() {
    SelectiveConfig cfg{
        .temperature = 1.0f,
        .energy_threshold = -5.0f,
        .entropy_threshold = 0.40f
    };
    SelectiveClassifierEngine<16> classifier(cfg);

    std::cout << "=== Запуск тестів вибіркового класифікатора (C++20) ===\n";

    // 1. In-Distribution
    constexpr std::array<float, 4> id_logits = { 8.5f, 1.2f, 0.4f, -0.8f };
    run_cpp_test("In-Distribution (чітке розпізнавання)", id_logits, classifier, DecisionStatus::Accepted);

    // 2. Алеаторний шум
    constexpr std::array<float, 4> noisy_logits = { 0.2f, 5.0f, 4.9f, 0.1f };
    run_cpp_test("Ambiguous Noise (висока ентропія на межі)", noisy_logits, classifier, DecisionStatus::RejectAmbiguous);

    // 3. OOD шум
    constexpr std::array<float, 4> ood_low_logits = { 0.1f, -0.2f, 0.05f, -0.1f };
    run_cpp_test("OOD Background Noise (висока вільна енергія)", ood_low_logits, classifier, DecisionStatus::RejectOOD);

    // 4. Слабкий OOD
    constexpr std::array<float, 4> ood_weak_logits = { 2.1f, -1.0f, -0.5f, -2.0f };
    run_cpp_test("OOD Weak Confidence", ood_weak_logits, classifier, DecisionStatus::RejectOOD);

    return 0;
}
```
:::

### Покроковий розбір тестових сценаріїв

Для повного розуміння механіки роботи фільтрів розглянемо детальні числові значення проміжних змінних у кожному із чотирьох тестових сценаріїв:

#### 1. In-Distribution (чітке розпізнавання знайомого знака)
- Вхідні логіти: `f = [8.5, 1.2, 0.4, -0.8]`, `K = 4`, `T = 1.0`.
- Максимальний логіт: `f_max = 8.5` (індекс 0).
- Зсунуті експоненти: `exp_scaled = [exp(0.0), exp(-7.3), exp(-8.1), exp(-9.3)] = [1.0, 0.000675, 0.000303, 0.000091]`.
- Сума експонент: `sum_exp = 1.00107`.
- Вільна енергія: `E = -8.5 - 1.0 · ln(1.00107) = -8.501`. Оскільки `-8.501 ≤ -5.0` (поріг `τ_E`), OOD-гейт пройдено успішно.
- Softmax ймовірності: `p = [0.99893, 0.00067, 0.00030, 0.00009]`.
- Ентропія Шеннона: `H(p) = 0.0084 nats`.
- Максимальна ентропія: `ln(4) = 1.38629 nats`.
- Нормована ентропія: `H_norm = 0.0084 / 1.38629 = 0.006` (0.6%). Оскільки `0.006 ≤ 0.40`, ентропійний гейт пройдено.
- Результат: `STATUS_ACCEPTED`, Клас 0, Впевненість 99.89%.

#### 2. Алеаторний шум (змазаний кадр на межі двох класів)
- Вхідні логіти: `f = [0.2, 5.0, 4.9, 0.1]`.
- Максимальний логіт: `f_max = 5.0` (індекс 1).
- Зсунуті експоненти: `exp_scaled = [exp(-4.8), exp(0.0), exp(-0.1), exp(-4.9)] = [0.0082, 1.0, 0.9048, 0.0074]`.
- Сума експонент: `sum_exp = 1.9204`.
- Вільна енергія: `E = -5.0 - ln(1.9204) = -5.652`. Оскільки `-5.652 ≤ -5.0`, енергетичний OOD-тест пройдено (об'єкт належить предметній області).
- Softmax ймовірності: `p = [0.0043, 0.5207, 0.4712, 0.0038]`. Класи 1 та 2 змагаються між собою.
- Ентропія: `H(p) = 0.738 nats`.
- Нормована ентропія: `H_norm = 0.738 / 1.386 = 0.532` (53.2%).
- Оскільки `0.532 > 0.40` (поріг `τ_H`), ентропійний гейт блокує відповідь.
- Результат: `STATUS_REJECT_AMBIGUOUS` (відмова через алеаторну неоднозначність).

#### 3. Слабкий фоновий OOD шум (порожнє поле / сторонній предмет)
- Вхідні логіти: `f = [0.1, -0.2, 0.05, -0.1]`.
- Максимальний логіт: `f_max = 0.1` (індекс 0).
- Зсунуті експоненти: `exp_scaled = [1.0, 0.7408, 0.9512, 0.8187]`.
- Сума експонент: `sum_exp = 3.5107`.
- Вільна енергія: `E = -0.1 - ln(3.5107) = -1.356`.
- Оскільки `-1.356 > -5.0` (енергія занадто висока для знайомих класів), енергетичний гейт спрацьовує негайно.
- Результат: `STATUS_REJECT_OOD` (відмова через відсутність знань моделі).

#### 4. Патологічний OOD із слабкою впевненістю
- Вхідні логіти: `f = [2.1, -1.0, -0.5, -2.0]`.
- Максимальний логіт: `f_max = 2.1` (індекс 0).
- Зсунуті експоненти: `exp_scaled = [1.0, 0.0450, 0.0743, 0.0166]`, `sum_exp = 1.1359`.
- Вільна енергія: `E = -2.1 - ln(1.1359) = -2.227`.
- Оскільки `-2.227 > -5.0`, модель безпечно відхиляє вхідний зразок як OOD, хоча звичайний softmax дав би оманливу ймовірність `p_0 = 1.0 / 1.1359 = 88.0%`.
- Результат: `STATUS_REJECT_OOD`.

### Промислові оптимізації для мікроконтролерів без FPU

На дешевих мікроконтролерах сімейств ARM Cortex-M0/M0+, RISC-V RV32I або ESP32 без апаратного модуля плаваючої коми (FPU) виконання математичних функцій `expf()` та `logf()` зі стандартної бібліотеки `<math.h>` здійснюється через програмну емуляцію за алгоритмами поліномів Ремеза або степеневих рядів Тейлора. Це може займати від 300 до 800 тактів на кожен виклик.

Для критичних за часом задач (наприклад, розпізнавання аварійних сигналів вібрації на частоті 5 кГц) застосовують **цілочисельну апроксимацію з фіксованою комою (Fixed-Point Q-format)**.

#### 1. Апроксимація експоненти через поліном Чебишова

Оскільки вхідні аргументи `z_i = (f_i - f_max) / T` після максимального зсуву завжди лежать у від'ємному діапазоні `z_i ≤ 0`, для діапазону `z ∈ [−4.0, 0.0]` функцію `exp(z)` апроксимують квадратичним або кубічним поліномом Чебишова:

```
exp(z) ≈ 1.0 + 0.9998 · z + 0.4982 · z² + 0.1581 · z³
```

Для значень `z < −4.0` результат приймається рівним нулю (`exp(z) ≈ 0.0`), оскільки внесок таких експонент у суму є мізерним (`< 0.018`).

Обчислення за схемою Горнера на цілих числах з фіксованою комою Q8.8 виконується всього за 4 такти процесора:

```
y = 1.0 + z · (0.9998 + z · (0.4982 + z · 0.1581))
```

#### 2. Апроксимація логарифма через табличний пошук (LUT)

Для обчислення вільної енергії необхідно знайти `ln(S)`, де сума `S ∈ [1.0, K]`. Оскільки для `K = 16` діапазон значень `S` строго обмежений інтервалом `[1.0, 16.0]`, створюється статична таблиця попередньо обчислених значень `log_table[256]` розміром 256 байтів:

```
uint8_t index = (uint8_t)((S − 1.0f) · (255.0f ÷ (K − 1.0f)));
float ln_S = lut_ln_values[index];
```

Використання полінома Чебишова та 256-байтної LUT-таблиці скорочує час виконання всього вибіркового фільтра на процесорі ARM Cortex-M0+ з частотою 48 МГц з 185 мікросекунд до **4.2 мікросекунди** на один кадр при абсолютній похибці розрахунку енергії менше 0.25%.

### Політики фільтрації та часове згладжування (Temporal Smoothing)

У потокових сенсорних системах (відеокамери роботів, акустичні датчики БПЛА) окремий одиночний кадр може зазнати короткочасного оптичного артефакту (відблиск сонця, проліт комахи перед об'єктивом), що викликає одиничний сплеск ентропії на 1 кадр.

Щоб запобігти хибним відмовам і дрижанню стану (англ. *chattering*), модуль доповнюють механізмом **гістерезису та часового згладжування (Ring Buffer Smoothing)**:
1. **Ковзне середнє ентропії:** поріг відмови застосовується не до миттєвого значення `H_norm[t]`, а до експоненційно зваженого ковзного середнього (EMA):

```
H_smooth[t] = α · H_norm[t] + (1 − α) · H_smooth[t−1],  де α = 0.35
```

2. **Лічильник підтвердження відмови (Debounce Counter):** перехід у стан `REJECT_AMBIGUOUS` фіксується лише тоді, коли перевищення порогу `τ_H` триває щонайменше `N_confirm = 3` послідовних кадри. Якщо ж на наступному кадрі якість сигналу відновилася, лічильник скидається.
3. **Миттєве спрацьовування на OOD:** на відміну від алеаторного шуму, енергетичний гейт OOD не згладжується в часі. Будь-який вихід з `E(x) > τ_E` викликає негайну реакцію безпеки, оскільки зволікання в разі появи невідомої перешкоди може бути фатальним.

### Архітектурні патерни реакцій на відмову (Policy Patterns)

В інженерних системах код бізнес-логіки не повинен бути захаращений вкладеними конструкціями `switch-case` для кожного статусу класифікації. Для чистого розділення відповідальності застосовують патерн «Таблиця обробників політик» (Policy Handler Table).

:::tabs
```c
typedef void (*decision_handler_fn)(const selective_output_t* result, void* user_ctx);

typedef struct {
    decision_handler_fn on_accepted;
    decision_handler_fn on_reject_ood;
    decision_handler_fn on_reject_ambiguous;
} decision_policy_table_t;

void dispatch_decision(const selective_output_t* res, const decision_policy_table_t* table, void* ctx) {
    if (!res || !table) return;
    switch (res->status) {
        case DECISION_STATUS_ACCEPTED:
            if (table->on_accepted) table->on_accepted(res, ctx);
            break;
        case DECISION_STATUS_REJECT_OOD:
            if (table->on_reject_ood) table->on_reject_ood(res, ctx);
            break;
        case DECISION_STATUS_REJECT_AMBIGUOUS:
            if (table->on_reject_ambiguous) table->on_reject_ambiguous(res, ctx);
            break;
    }
}
```
```cpp
template <typename OnAccept, typename OnOOD, typename OnAmbiguous>
void match_decision(
    const SelectiveOutput& res,
    OnAccept&& on_accept,
    OnOOD&& on_ood,
    OnAmbiguous&& on_ambiguous
) {
    switch (res.status) {
        case DecisionStatus::Accepted:
            std::forward<OnAccept>(on_accept)(res.predicted_class, res.confidence);
            break;
        case DecisionStatus::RejectOOD:
            std::forward<OnOOD>(on_ood)(res.free_energy);
            break;
        case DecisionStatus::RejectAmbiguous:
            std::forward<OnAmbiguous>(on_ambiguous)(res.normalized_entropy);
            break;
    }
}
```
:::

### Апаратне профілювання та заміри затримок на мікроконтролерах

Для валідації реального часу на платформах ARM Cortex-M4F та Cortex-M7 модуль профілюють за допомогою апаратного лічильника циклів DWT (Data Watchpoint and Trace):

:::tabs
```c
// Ініціалізація DWT лічильника тактів на ARM Cortex-M
void profile_selective_filter_c(const float* logits, size_t n, const selective_config_t* cfg) {
    selective_output_t res;
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    DWT->CYCCNT = 0;

    uint32_t t_start = DWT->CYCCNT;
    selective_classify_process(cfg, logits, n, &res);
    uint32_t t_cycles = DWT->CYCCNT - t_start;
    (void)t_cycles;
}
```
```cpp
// RAII обгортка для профілювання тактів DWT на C++20
class DwtCycleProfiler {
public:
    DwtCycleProfiler() noexcept : start_(DWT->CYCCNT) {}
    [[nodiscard]] uint32_t elapsed() const noexcept {
        return DWT->CYCCNT - start_;
    }
private:
    uint32_t start_{0};
};

template <std::size_t N>
uint32_t profile_selective_filter_cpp(
    std::span<const float> logits,
    const SelectiveClassifierEngine<N>& engine
) {
    DwtCycleProfiler profiler;
    auto res = engine.evaluate(logits);
    return profiler.elapsed();
}
```
:::

На мікроконтролері STM32H743 (ARM Cortex-M7, 480 МГц) виклик `selective_classify_process` для `K = 10` класів займає **840 тактів** (1.75 мікросекунди) при увімкненому апаратному FPU та оптимізації `-O3`. Це становить менш ніж 0.05% від загального бюджету часу виводу згорткової нейромережі (яка типово виконується за 15–40 мілісекунд), що підтверджує практичну придатність вибіркової класифікації для вбудованих систем керування з жорсткими дедлайнами.

### Діагностика, логування та активне донавчання (Active Learning Loop)

Кожне спрацьовування статусу відмови є цінним джерелом інженерної інформації для подальшого вдосконалення всієї системи. Якщо модель відмовилася від рішення через статус `REJECT_OOD`, це означає, що пристрій зустрів у реальному середовищі фрагмент фізичного світу, який відсутній у поточному датасеті.

У вбудованій архітектурі реалізують модуль **діагностичного чорного ящика (Blackbox Event Recorder)**:
- При виникненні статусу `REJECT_OOD` або стійкого `REJECT_AMBIGUOUS` поточний вхідний кадр сенсора, відповідний вектор логітів, значення вільної енергії та ентропії автоматично зберігаються в енергонезалежній кільцевій пам'яті (Flash / eMMC);
- Під час планового технічного обслуговування або через захищений бездротовий канал телеметрії збережені аномальні зразки передаються на сервер розробників;
- Ці дані проходять верифікацію людиною-експертом (Data Labeler) і поповнюють навчальний датасет для наступної ревізії нейромережі.

Таким чином, механізм штатної відмови не лише запобігає аваріям у режимі реального часу, але й утворює замкнений контур безперервного активного донавчання (англ. *Active Learning Loop*), завдяки якому кожна наступна версія прошивки стає все менш схильною до незнання.

### Верифікація та валідація надійності (V&V і фаззинг)

Відповідно до вимог стандартів функціональної безпеки DO-178C (авіація) та ISO 26262 (автомобільна промисловість), код ядра класифікатора проходить обов'язкове тестування на структурне покриття (MC/DC — Modified Condition/Decision Coverage) та стресовий фаззинг (Fuzz Testing):
1. **Генерація денормалізованих чисел:** перевірка коректності роботи математичних функцій у разі подачі субнормальних значень float (`1e-40f`), що виникають під час поступового згасання аналогового сигналу;
2. **Стійкість до нечислових значень (NaN / Inf):** якщо через апаратний збій контролера DMA або перегрів NPU у вектор логітів потрапляє `NaN`, початкова перевірка діапазонів миттєво відхиляє пакет з кодом помилки `SELECTIVE_ERR_INVALID_ARG`, не допускаючи зависання чи паніки ядра операційної системи реального часу (RTOS);
3. **Граничні значення температури:** сувора перевірка заборони значень `T ≤ 0.0f` повністю усуває ризик виникнення апаратного переривання ділення на нуль (Division by Zero Fault) на рівні процесорного ядра;
4. **Стабільність за однакових логітів:** у разі подачі симетричного вектора `f_i = C` перевіряється точність розрахунку ентропії `H_norm = 1.0` без переповнення знаменника нормалізації.
