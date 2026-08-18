# ⚙️ Автоматизований аудит евристик та матриця прийняття рішень

Ця практична вставка демонструє реалізацію алгоритмічного двигуна оцінки архітектурних рішень (Architectural Decision Evaluator), який автоматизує застосування п'яти головних евристик (зворотність, бюджет інновацій, YAGNI, вимірюваність, pre-mortem).

Автоматизована оцінка дозволяє інтегрувати чек-лісти прийняття рішень безпосередньо у CI/CD пайплайни або інструменти генерації ADR (Architecture Decision Records). Замість того, щоб покладатися на емоційні суперечки під час рев'ю, команда надає структурований вектор параметрів пропозиції, а двигун обчислює підсумкову категорію рішення та Prescribed Action (негайне делегування, створення прототипу, проведення сесії Pre-Mortem чи скликання колегії архітекторів).

```
ВХІДНІ ПАРАМЕТРИ РІШЕННЯ (Decision Vector)
├── Reversibility Score (0.0 .. 1.0) ──> Оцінка складності відкату назад
├── Innovation Tokens Needed (0 .. 3)  ──> Кількість інноваційних жетонів
├── Has Measurement Data (bool)       ──> Наявність виміряних профілів/метрик
├── PreMortem Risk Severity (1 .. 5)   ──> Максимальна важкість розрахованого ризику
└── Public API Boundary Impact (bool)  ──> Чи зачіпає рішення зовнішній контракт
            ↓
  [ ДВИГУН ОЦІНКИ ЕВРИСТИК ]
            ↓
РЕКОМЕНДОВАНИЙ МАРШРУТ (Prescribed Action)
├── FAST_TRACK_DELEGATE       (Реалізувати негайно без бюрократії)
├── TIMEBOXED_SPIKE_2DAYS     (Виділити 2 дні на прототипування)
├── PRE_MORTEM_WORKSHOP_REQUIRED (Обов'язкова 30-хв сесія Pre-Mortem)
└── ARCH_REVIEW_BOARD_GATE    (Повний аналіз RFC та колегія архітекторів)
```

### 1. Математична модель та принципи оцінки векторів

Формалізація архітектурних рішень вимагає перетворення суб'єктивних оцінок інженерів на вимірювані коефіцієнти. Двигун оперує векторним простором `V = (R, T, M, S, P)`, де кожен компонент описує фундаментальну грань ризику та складності.

* `R ∈ [0.0, 1.0]` — коефіцієнт зворотності (*reversibility score*). Значення `1.0` означає миттєвий відкат без зупинки системи та втрати даних (наприклад, перемикання прапорця фічі); значення `0.0` відповідає незворотній зміні формату зберігання на диску або деструктивній міграції схем.
* `T ∈ {0, 1, 2, 3}` — кількість інноваційних жетонів (*innovation tokens*), які вимагає дана технологія.
* `M ∈ {0, 1}` — прапорець наявності об'єктивних вимірювальних даних (*measurement data*).
* `S ∈ {1, 2, 3, 4, 5}` — максимальна важкість потенційного провалу (*risk severity*), отримана під час попереднього аналізу ризиків.
* `P ∈ {0, 1}` — прапорець впливу на публічну межу API або міжсервісний контракт.

Функція обчислення індексу односторонніх дверей (`I_door`) агрегує ці параметри за такою формулою:

```
I_door = (1.0 - R) · 0.5 + P · 0.3 + T · 0.1
```

Градація результатів визначає організаційний маршрут проходження рішення:
1. `I_door ≥ 0.6` або `S ≥ 4`: Рішення кваліфікується як **One-Way Door**. Деплой блокується до проведення вичерпного RFC та схвалення на Architecture Review Board.
2. `0.3 ≤ I_door < 0.6` або `S = 3`: Рішення вимагає обов'язкової 30-хвилинної сесії Pre-Mortem з участю суміжних команд.
3. `R < 0.7` або `T > 0`: Вимагається проведення таймбоксового спайку (Spike) тривалістю не більше 2 днів для покупки інформації та зниження невизначеності.
4. `I_door < 0.3` та `S ≤ 2`: Рішення є **Two-Way Door**. Надається зелене світло для миттєвої реалізації розробником без додаткових погоджень.

Окремим загороджувальним фільтром виступає правило **Measure First**: якщо прапорець `is_performance_optimization` дорівнює `true`, але `has_measurement_data` дорівнює `false`, двигун автоматично примушує до дії `MEASURE_FIRST_REJECT` (відмова в оптимізації до надання бечмарків).

### 2. Програмна реалізація двигуна аудиту

Нижче наведено ідіоматичні реалізації двигуна оцінки трьома мовами програмування. Кожна реалізація дотримується суворих інженерних гайдлайнів відповідної екосистеми.

У версії C++20 використовується `std::expected` для безпечної обробки обчислювальних помилок без використання винятків, а також `std::string_view` для ефективної передачі текстових описових полів без паразитного виділення динамічної пам'яті. У C-версії застосовується сувора безнадійна техніка перевірки покажчиків та передача результату через вихідний параметр із поверненням числового коду помилки. У TypeScript-версії реалізовано патерн *Discriminated Unions* для гарантії вичерпної обробки всіх можливих маршрутів рішення на етапі компіляції.

:::tabs
```cpp
#include <iostream>
#include <string_view>
#include <expected>
#include <vector>
#include <cstdint>

// Ідіоматичний C++20: строгі типи, std::expected для обробки помилок, std::string_view

enum class DecisionRoute {
    FastTrackDelegate,
    TimeboxedSpike,
    PreMortemWorkshop,
    ArchReviewBoard,
    RejectedNoMetrics
};

struct DecisionVector {
    std::string_view title;
    float reversibility_score;       // 0.0 (важко відкотити) .. 1.0 (легко)
    std::uint8_t innovation_tokens;  // 0 .. 3
    bool has_measurement_data;       // чи є метрики
    std::uint8_t risk_severity;      // 1 .. 5
    bool touches_public_api;         // чи міняє публічний контракт
    bool is_performance_optimization; // чи це оптимізація продуктивності
};

struct EvaluationResult {
    DecisionRoute route;
    float one_way_index;
    std::string_view rationale;
};

enum class EvaluatorError {
    TokenBudgetExceeded,
    InvalidReversibilityScore,
    InvalidRiskSeverity
};

class DecisionEvaluator {
private:
    static constexpr std::uint8_t MAX_TOTAL_TOKENS = 3;
    std::uint8_t current_project_tokens_{1}; // Поточні жетони проєкту

public:
    explicit DecisionEvaluator(std::uint8_t current_tokens) 
        : current_project_tokens_(current_tokens) {}

    [[nodiscard]] std::expected<EvaluationResult, EvaluatorError> 
    evaluate(const DecisionVector& vec) const noexcept {
        if (vec.reversibility_score < 0.0f || vec.reversibility_score > 1.0f) {
            return std::unexpected(EvaluatorError::InvalidReversibilityScore);
        }
        if (vec.risk_severity < 1 || vec.risk_severity > 5) {
            return std::unexpected(EvaluatorError::InvalidRiskSeverity);
        }

        // Перевірка бюджету інноваційних жетонів (Boring Technology Heuristic)
        if (current_project_tokens_ + vec.innovation_tokens > MAX_TOTAL_TOKENS) {
            return std::unexpected(EvaluatorError::TokenBudgetExceeded);
        }

        // Евристика: Measure First
        if (vec.is_performance_optimization && !vec.has_measurement_data) {
            return EvaluationResult{
                .route = DecisionRoute::RejectedNoMetrics,
                .one_way_index = 0.0f,
                .rationale = "Відхилено: оптимізація продуктивності заборонена без метрик і профілювання"
            };
        }

        // Обчислення індексу односторонніх дверей (One-Way Door Index)
        const float public_impact = vec.touches_public_api ? 0.3f : 0.0f;
        const float token_impact = static_cast<float>(vec.innovation_tokens) * 0.1f;
        const float one_way_index = (1.0f - vec.reversibility_score) * 0.5f + public_impact + token_impact;

        // Покрокова фільтрація маршруту
        if (one_way_index >= 0.6f || vec.risk_severity >= 4) {
            return EvaluationResult{
                .route = DecisionRoute::ArchReviewBoard,
                .one_way_index = one_way_index,
                .rationale = "One-Way Door: Високий ризик або незворотність. Потрібен RFC та Arch Review Board."
            };
        }

        if (vec.risk_severity == 3 || (one_way_index >= 0.3f && !vec.has_measurement_data)) {
            return EvaluationResult{
                .route = DecisionRoute::PreMortemWorkshop,
                .one_way_index = one_way_index,
                .rationale = "Помірний ризик / невизначеність. Обов'язкова 30-хв сесія Pre-Mortem."
            };
        }

        if (vec.reversibility_score < 0.7f || vec.innovation_tokens > 0) {
            return EvaluationResult{
                .route = DecisionRoute::TimeboxedSpike,
                .one_way_index = one_way_index,
                .rationale = "Необхідно купити інформацію: Timeboxed спайк на 2 дні."
            };
        }

        return EvaluationResult{
            .route = DecisionRoute::FastTrackDelegate,
            .one_way_index = one_way_index,
            .rationale = "Two-Way Door: Висока зворотність. Делегувати розробнику негайно."
        };
    }
};

int main() {
    DecisionEvaluator evaluator(/*current_tokens=*/1);

    DecisionVector prop1{
        .title = "Додати новий кастомний брокер повідомлень",
        .reversibility_score = 0.2f,
        .innovation_tokens = 2,
        .has_measurement_data = false,
        .risk_severity = 4,
        .touches_public_api = true,
        .is_performance_optimization = false
    };

    auto res = evaluator.evaluate(prop1);
    if (res) {
        std::cout << "Рішення: " << res->rationale 
                  << " [One-Way Index: " << res->one_way_index << "]\n";
    } else {
        std::cout << "Помилка оцінки рішення (код " << static_cast<int>(res.error()) << ")\n";
    }

    return 0;
}
```
```c
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

// Ідіоматичний C11: чіткі межі пам'яті, явні коди помилок, відсутність динамічного виділення

typedef enum {
    DECISION_ROUTE_FAST_TRACK = 0,
    DECISION_ROUTE_TIMEBOXED_SPIKE,
    DECISION_ROUTE_PRE_MORTEM,
    DECISION_ROUTE_ARCH_REVIEW,
    DECISION_ROUTE_REJECTED_NO_METRICS
} decision_route_t;

typedef enum {
    EVAL_OK = 0,
    EVAL_ERR_TOKEN_BUDGET_EXCEEDED,
    EVAL_ERR_INVALID_REVERSIBILITY,
    EVAL_ERR_INVALID_RISK
} eval_error_t;

typedef struct {
    const char* title;
    float reversibility_score;       // 0.0 .. 1.0
    uint8_t innovation_tokens;       // 0 .. 3
    bool has_measurement_data;
    uint8_t risk_severity;           // 1 .. 5
    bool touches_public_api;
    bool is_performance_optimization;
} decision_vector_t;

typedef struct {
    decision_route_t route;
    float one_way_index;
    const char* rationale;
} evaluation_result_t;

eval_error_t evaluate_decision(const decision_vector_t* vec, 
                                uint8_t current_project_tokens, 
                                evaluation_result_t* out_result) {
    if (!vec || !out_result) return EVAL_ERR_INVALID_REVERSIBILITY;

    if (vec->reversibility_score < 0.0f || vec->reversibility_score > 1.0f) {
        return EVAL_ERR_INVALID_REVERSIBILITY;
    }
    if (vec->risk_severity < 1 || vec->risk_severity > 5) {
        return EVAL_ERR_INVALID_RISK;
    }
    if (current_project_tokens + vec->innovation_tokens > 3) {
        return EVAL_ERR_TOKEN_BUDGET_EXCEEDED;
    }

    // Евристика: Measure First
    if (vec->is_performance_optimization && !vec->has_measurement_data) {
        out_result->route = DECISION_ROUTE_REJECTED_NO_METRICS;
        out_result->one_way_index = 0.0f;
        out_result->rationale = "Відхилено: оптимізація продуктивності заборонена без метрик";
        return EVAL_OK;
    }

    float public_impact = vec->touches_public_api ? 0.3f : 0.0f;
    float token_impact = (float)vec->innovation_tokens * 0.1f;
    float one_way_index = (1.0f - vec->reversibility_score) * 0.5f + public_impact + token_impact;

    out_result->one_way_index = one_way_index;

    if (one_way_index >= 0.6f || vec->risk_severity >= 4) {
        out_result->route = DECISION_ROUTE_ARCH_REVIEW;
        out_result->rationale = "One-Way Door: Високий ризик. Потрібен Arch Review Board.";
    } else if (vec->risk_severity == 3 || (one_way_index >= 0.3f && !vec->has_measurement_data)) {
        out_result->route = DECISION_ROUTE_PRE_MORTEM;
        out_result->rationale = "Помірний ризик. Обов'язкова сесія Pre-Mortem.";
    } else if (vec->reversibility_score < 0.7f || vec->innovation_tokens > 0) {
        out_result->route = DECISION_ROUTE_TIMEBOXED_SPIKE;
        out_result->rationale = "Купити інформацію: Timeboxed спайк на 2 дні.";
    } else {
        out_result->route = DECISION_ROUTE_FAST_TRACK;
        out_result->rationale = "Two-Way Door: Висока зворотність. Делегувати розробнику.";
    }

    return EVAL_OK;
}

int main(void) {
    decision_vector_t prop = {
        .title = "Рефакторинг внутрішнього сервісу авторизації",
        .reversibility_score = 0.85f,
        .innovation_tokens = 0,
        .has_measurement_data = true,
        .risk_severity = 2,
        .touches_public_api = false,
        .is_performance_optimization = false
    };

    evaluation_result_t res;
    eval_error_t err = evaluate_decision(&prop, 1, &res);

    if (err == EVAL_OK) {
        printf("Маршрут рішення: %s (Індекс: %.2f)\n", res.rationale, res.one_way_index);
    } else {
        printf("Помилка оцінки: %d\n", err);
    }

    return 0;
}
```
```ts
// Ідіоматичний TypeScript: дискриміновані об'єднання, суворе типування

export type DecisionRoute = 
  | { kind: 'FAST_TRACK_DELEGATE'; rationale: string }
  | { kind: 'TIMEBOXED_SPIKE'; spikeDays: number; rationale: string }
  | { kind: 'PRE_MORTEM_WORKSHOP'; rationale: string }
  | { kind: 'ARCH_REVIEW_BOARD'; rationale: string }
  | { kind: 'REJECTED_NO_METRICS'; rationale: string };

export interface DecisionVector {
  readonly title: string;
  readonly reversibilityScore: number; // 0.0 .. 1.0
  readonly innovationTokens: number;  // 0 .. 3
  readonly hasMeasurementData: boolean;
  readonly riskSeverity: number;      // 1 .. 5
  readonly touchesPublicApi: boolean;
  readonly isPerformanceOptimization: boolean;
}

export class DecisionEvaluator {
  private static readonly MAX_TOKENS = 3;

  constructor(private readonly currentProjectTokens: number = 1) {}

  public evaluate(vec: DecisionVector): DecisionRoute {
    if (this.currentProjectTokens + vec.innovationTokens > DecisionEvaluator.MAX_TOKENS) {
      throw new Error(`Перевищено бюджет інноваційних жетонів! Лишилося: ${DecisionEvaluator.MAX_TOKENS - this.currentProjectTokens}`);
    }

    // Евристика: Measure First
    if (vec.isPerformanceOptimization && !vec.hasMeasurementData) {
      return {
        kind: 'REJECTED_NO_METRICS',
        rationale: 'Відхилено: оптимізація продуктивності заборонена без надання профілів і метрик.'
      };
    }

    const publicImpact = vec.touchesPublicApi ? 0.3 : 0.0;
    const tokenImpact = vec.innovationTokens * 0.1;
    const oneWayIndex = (1.0 - vec.reversibilityScore) * 0.5 + publicImpact + tokenImpact;

    if (oneWayIndex >= 0.6 || vec.riskSeverity >= 4) {
      return {
        kind: 'ARCH_REVIEW_BOARD',
        rationale: `One-Way Door (Індекс: ${oneWayIndex.toFixed(2)}). Потрібна повноцінна захист RFC на Arch Review Board.`
      };
    }

    if (vec.riskSeverity === 3 || (oneWayIndex >= 0.3 && !vec.hasMeasurementData)) {
      return {
        kind: 'PRE_MORTEM_WORKSHOP',
        rationale: 'Помірний ризик/невизначеність. Обов’язкова 30-хвилинна сесія Pre-Mortem.'
      };
    }

    if (vec.reversibilityScore < 0.7 || vec.innovationTokens > 0) {
      return {
        kind: 'TIMEBOXED_SPIKE',
        spikeDays: 2,
        rationale: 'Необхідно купити інформацію: Timeboxed спайк на 2 дні.'
      };
    }

    return {
      kind: 'FAST_TRACK_DELEGATE',
      rationale: 'Two-Way Door: Висока зворотність. Делегувати розробнику без бюрократії.'
    };
  }
}
```
:::

### 3. Аналіз обробки граничних випадків та нетипових станів

Алгоритмічна оцінка повинна бути стійкою до некоректних або маніпулятивних вхідних даних, коли інженери намагаються штучно завищити коефіцієнт зворотності ради проходження фаст-треку. Розглянемо ключові захисні механізми двигуна:

#### Захист від маніпуляції зворотністю (Reversibility Guard)
Якщо прапорець `touches_public_api` дорівнює `true`, двигун встановлює нижню межу індексу односторонніх дверей `I_door` на рівні не менше `0.3`, навіть якщо розробник вказав `reversibility_score = 1.0`. Це унеможливлює проведення змін публічних контрактів без принаймні асинхронного рев'ю або сесії Pre-Mortem.

#### Валідація ліміту жетонів інновацій (Token Overflow Protection)
Спроба передати `innovation_tokens > 3` викликає виняток або повертає код помилки `EVAL_ERR_TOKEN_BUDGET_EXCEEDED` ще до початку обчислення геометрії дверей. Це блокує можливість одночасного впровадження кількох експериментальних систем в один сервіс.

#### Суворе правило відсутності метрик (Measure First Hard Gate)
Якщо зміна позначена як оптимізація продуктивності, двигун ігнорує високий коефіцієнт зворотності чи низький рівень ризику і повертає `REJECTED_NO_METRICS`. Це гарантує, що жоден PR з передчасною оптимізацією не потрапить у майстер-гілку без надання бенчмарків.

### 4. Трасування оцінки на реальних інженерних кейсах

Для перевірки стійкості математичної моделі розглянемо три сценарії з практики розбудови платформи Digital Homes:

#### Сценарій A: Впровадження експериментальної баз даних TimeSeries під обробку телеметрії
Архітектор висуває пропозицію замінити стандартне сховище PostgreSQL на нову розподілену TimeSeries БД для обробки подій з 500,000 сенсорів.
* `reversibility_score` = 0.15 (зміна формату зберігання та запитів є важкозворотною);
* `innovation_tokens` = 2 (нова система вимагає освоєння нової мови запитів та операційного інструментарію);
* `touches_public_api` = true;
* `risk_severity` = 5.

*Обчислення двигуна:*

```
I_door = (1.0 - 0.15) · 0.5 + 0.3 + 2 · 0.1 = 0.425 + 0.3 + 0.2 = 0.925
```

*Результат:* Оскільки `I_door = 0.925 ≥ 0.6`, двигун присвоює маршрут `ARCH_REVIEW_BOARD`. Деплой блокується до написання повноцінного RFC, проведення сесії Pre-Mortem та колегіального затвердження.

#### Сценарій B: Локальний рефакторинг алгоритму сортування в модулі кінематики
Розробник пропонує замінити стандартне сортування на узгоджений алгоритм усередині ізольованого модуля обробки сигналів тривоги.
* `reversibility_score` = 0.95 (зміна повністю прихована за інтерфейсом модуля);
* `innovation_tokens` = 0 (використовується стандартна бібліотека);
* `touches_public_api` = false;
* `risk_severity` = 1.

*Обчислення двигуна:*

```
I_door = (1.0 - 0.95) · 0.5 + 0.0 + 0.0 = 0.025
```

*Результат:* `I_door = 0.025 < 0.3`, маршрут `FAST_TRACK_DELEGATE`. Рішення схвалюється автоматично без бюрократії та погоджень.

#### Сценарій C: «Оптимізація» серіалізації JSON без надання профілів
Інженер надсилає пул-реквест зі складною саморобною схемою бінарної серіалізації замість JSON, аргументуючи це тим, що «це прискорить роботу системи».
* `is_performance_optimization` = true;
* `has_measurement_data` = false.

*Результат:* Двигун миттєво повертає статус `REJECTED_NO_METRICS`. Пул-реквест відхиляється на етапі CI з вимогою надати порівняльні бенчмарки та flamegraph профілювання.

### 5. Інтеграція в CI/CD та процес генерації ADR

Автоматизований аудит евристик найефективніше працює при підключенні до гіт-хуків або GitHub Actions. Коли розробник створює новий файл ADR (`docs/adr/ADR-0042.md`), linter запускає алгоритм перевірки вектора:

1. Парсер зчитує метадані з YAML-заголовка ADR (`reversibility`, `tokens`, `metrics_attached`).
2. Оцінювач валідує відповідність обраної процедури погодження рекомендаціям двигуна.
3. Якщо розробник намагається провести рішення з `I_door ≥ 0.6` через фаст-трек без посилання на схвалений RFC, CI повертає помилку з описом невиконаного правила.

Такий підхід перетворює архітектурну культуру з набору декларативних побажань на сувору, алгоритмічно контрольовану дисципліну розробки, де кожне незворотне рішення проходить перевірку об'єктивними критеріями зворотності та ризику.
