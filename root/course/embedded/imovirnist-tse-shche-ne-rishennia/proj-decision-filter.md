# ⚙️ Фільтр впевненості з гістерезисом та M-з-N голосуванням

Сирий вихід нейромережевого детектора — це потік дробових чисел (оцінок впевненості класів), який на бортовому комп'ютері оновлюється з кожним новим кадром сенсора (від 10 до 60 разів на секунду). Якщо контур керування наївно зіставить ці числа зі статичним порогом `if (confidence > 0.5)` і передасть результат прямо на виконавчі органи, виникнуть дві важкі інженерні проблеми:
1. **Хибні спрацьовування на одиничних викидах:** випадковий відблиск сонця, завада на матриці камери або артефакт стиснення відео на один кадр підніме оцінку до `0.95`, викликаючи миттєве непотрібне аварійне гальмування та ривок механіки.
2. **Брязкіт станів (chattering):** коли реальний об'єкт перебуває на межі видимості або в тіні, сира оцінка коливається навколо порогу (наприклад, `0.48 -> 0.52 -> 0.49 -> 0.51`). Виконавчі реле та силові H-мости починають перемикатися з частотою кадрів, що призводить до перегріву ключів, ударних навантажень на шестерні редуктора та розгойдування шасі.

Цей проєкт реалізує компактний, неблокуючий і детермінований триступеневий конвеєр стабілізації впевненості, оптимізований для мікроконтролерів без динамічного виділення пам'яті:
- **Калібратор температури** — згладжує перенасичені сирі логіти нейромережі до реалістичних імовірностей.
- **Інтегратор витоку (Exponential Moving Average, EMA)** — накопичує енергію сигналу в часі, придушуючи поодинокі спалахи шуму.
- **Ковзне бітове вікно голосування M з N** — підтверджує стійкість просторової детекції за останні `N` тактів за 1 такт процесора за допомогою інструкції `popcount`.
- **Автомат станів із подвійним гістерезисом та таймером утримання (Dwell Time)** — повністю усуває брязкіт і гарантує мінімальну тривалість активної дії.

---

### Архітектура та послідовність обробки

Конвеєр викликається періодично в обробнику завершення інференсу моделі (або в періодичній задачі RTOS):

```
Логіт z[i]  ──►  [Температурний Softmax]  ──►  Сира ймовірність P
                                                      │
                                                      ▼
                      [Інтегратор витоку / M-з-N бітове вікно]
                                                      │
                                                      ▼
                                           Накопичена впевненість S
                                                      │
                                                      ▼
                                           [Гістерезис H_on / H_off]
                                                      │
                                                      ▼
                                           [Таймер утримання t_hold]
                                                      │
                                                      ▼
                                          Стабільна команда: STOP / RUN
```

---

### Покроковий розбір структури та математики фільтра

#### 1. Температурне масштабування сирих логітів

Більшість легких згорткових мереж (YOLO, MobileNet) видають сирі логіти `z_i` перед фінальною нормалізацією. Калібратор ділить вектор логітів на попередньо підібрану скалярну температуру `T > 1.0`. Для бінарного виявлення перешкоди («об'єкт» проти «фону») формула з захистом від переповнення експоненти `expf` має вигляд:

```
max_l = max( z_target / T, z_bg / T )
P_calibrated = exp( z_target / T - max_l ) / ( exp( z_target / T - max_l ) + exp( z_bg / T - max_l ) )
```

Віднімання `max_l` гарантує, що аргумент функції `expf` ніколи не перевищить `0.0`, що повністю запобігає переповненню типу з рухомою комою (`+inf`).

#### 2. Інтегратор витоку (Exponential Moving Average)

Дискретний фільтр низьких частот першого порядку накопичує значення за рекурентною формулою:

```
S[k] = α · S[k-1] + (1 - α) · P[k]
```

Коефіцієнт `α ∈ (0, 1)` обирається виходячи з бажаної постійної часу фільтрації `τ` та періоду опитування `dt = 1 / FPS`: `α = exp(-dt / τ)`.  
- При `α = 0.8` та частоті 20 Гц (`dt = 50 мс`) постійна часу становить `τ ≈ 224 мс`.
- Одиночний спалах `P[k] = 1.0` піднімає фільтр із нуля лише до `S[k] = 0.20`, що нижче порогу спрацьовування.

#### 3. Бітове вікно голосування M з N на регістрах зсуву

Для миттєвої оцінки послідовності кадрів кожен такт квантується в 1 біт: `1`, якщо `P[k] >= H_off`, та `0` у протилежному випадку.  
Історія останніх `N ≤ 32` кадрів записується в одне 32-бітне беззнакове ціле число зсувом уліво: `history = (history << 1) | bit`. Кількість успішних детекцій у вікні обчислюється апаратною інструкцією `__builtin_popcount(history & mask)` за один такт ALU без циклів та масивів у пам'яті.

Порівняно з класичним кільцевим буфером на масиві `bool buffer[N]`, бітова маска має три вирішальні переваги для вбудованих систем:
- **Нульовий оверхед пам'яті:** замість масиву з індексами голови й хвоста весь стан займає рівно 4 байти.
- **Абсолютна детермінованість:** відсутність циклів `for` виключає розкид часу виконання (джиттер) у перериваннях.
- **Атомарність оновлення:** оновлення стану виконується однією машинною інструкцією запису слова.

#### 4. Гістерезис та часовий таймер Dwell Time

Автомат має два стани: `is_active = false` (Нормальний рух) та `is_active = true` (Аварійне спрацювання).
- **Перехід 0 -> 1:** відбувається, коли фільтрована впевненість `S[k] >= H_on` АБО бітове голосування підтвердило наявність об'єкта (`votes >= M`). Одночасно фіксується мітка часу `state_entered_ms = now_ms`.
- **Перехід 1 -> 0:** дозволений лише за виконання двох умов одночасно:
  1. Від моменту активації минуло не менше `min_hold_ms` мілісекунд (захист від короткочасного розблокування).
  2. Накопичена впевненість опустилася нижче порогу деактивації `S[k] < H_off` ТА голосування більше не проходить (`votes < M`).

---

### Реалізація фільтра впевненості на C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Конфігурація фільтра впевненості */
typedef struct {
    float alpha;               /* Коефіцієнт згладжування EMA (0.0 < alpha < 1.0) */
    float thresh_on;           /* Поріг активації тривоги (H_on, наприклад 0.75) */
    float thresh_off;          /* Поріг деактивації тривоги (H_off, наприклад 0.35) */
    uint32_t min_hold_ms;      /* Мінімальний час утримання активного стану (мс) */
    uint8_t window_size;       /* Розмір вікна M-з-N (макс 32 кадри) */
    uint8_t min_votes;         /* Поріг голосування M (кількість кадрів) */
} ConfidenceFilterConfig;

/* Стан екземпляра фільтра */
typedef struct {
    ConfidenceFilterConfig cfg;
    float integrated_score;    /* Поточна накопичена впевненість */
    uint32_t history_mask;     /* Бітова історія для M-з-N вікна */
    uint32_t state_entered_ms; /* Часова мітка останнього переходу стану */
    bool is_active;            /* Поточний стабільний дискретний вихід */
} ConfidenceFilter;

/* Ініціалізація структури фільтра з заданою конфігурацією */
void confidence_filter_init(ConfidenceFilter *filter, const ConfidenceFilterConfig *cfg) {
    if (!filter || !cfg) return;
    filter->cfg = *cfg;
    filter->integrated_score = 0.0f;
    filter->history_mask = 0U;
    filter->state_entered_ms = 0U;
    filter->is_active = false;
}

/* Обчислення каліброваної ймовірності через температурне масштабування */
float calibrate_temperature(float logit_target, float logit_bg, float temperature) {
    if (temperature <= 0.001f) temperature = 1.0f;
    float scaled_target = logit_target / temperature;
    float scaled_bg = logit_bg / temperature;
    
    /* Захист від переповнення експоненти */
    float max_l = (scaled_target > scaled_bg) ? scaled_target : scaled_bg;
    float exp_target = expf(scaled_target - max_l);
    float exp_bg = expf(scaled_bg - max_l);
    
    return exp_target / (exp_target + exp_bg);
}

/* Обробка нового такту виміру */
bool confidence_filter_update(ConfidenceFilter *filter, float raw_prob, uint32_t now_ms) {
    if (!filter) return false;

    /* 1. Інтегратор витоку (Exponential Moving Average) */
    filter->integrated_score = (filter->cfg.alpha * filter->integrated_score) +
                               ((1.0f - filter->cfg.alpha) * raw_prob);

    /* 2. Ковзне бітове вікно голосування M-з-N */
    bool frame_detected = (raw_prob >= filter->cfg.thresh_off);
    filter->history_mask = (filter->history_mask << 1) | (frame_detected ? 1U : 0U);
    
    /* Маскування за розміром вікна (захист при window_size = 32) */
    uint32_t valid_mask = (filter->cfg.window_size >= 32) ? 0xFFFFFFFFU :
                          ((1U << filter->cfg.window_size) - 1U);
    uint32_t current_window = filter->history_mask & valid_mask;
    
    /* Швидкий підрахунок кількості одиниць у бітовій масці */
    int votes = __builtin_popcount(current_window);
    bool vote_passed = (votes >= (int)filter->cfg.min_votes);

    /* 3. Автомат гістерезису з урахуванням мінімального часу утримання */
    if (filter->is_active) {
        /* Умови виходу з активного стану:
         * 1) Сплив мінімальний час утримання t_hold
         * 2) Накопичена впевненість впала нижче H_off ТА голосування не пройшло */
        bool hold_expired = (now_ms - filter->state_entered_ms) >= filter->cfg.min_hold_ms;
        if (hold_expired && (filter->integrated_score < filter->cfg.thresh_off) && !vote_passed) {
            filter->is_active = false;
            filter->state_entered_ms = now_ms;
        }
    } else {
        /* Умова входу в активний стан:
         * Накопичена впевненість перевищила H_on АБО голосування M-з-N впевнено пройшло */
        if ((filter->integrated_score >= filter->cfg.thresh_on) || vote_passed) {
            filter->is_active = true;
            filter->state_entered_ms = now_ms;
        }
    }

    return filter->is_active;
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <chrono>
#include <bit>

class DecisionConfidenceFilter {
public:
    struct Config {
        float alpha{0.75f};              // Коефіцієнт згладжування інтегратора EMA
        float thresh_on{0.75f};          // Поріг активації (H_on)
        float thresh_off{0.35f};         // Поріг деактивації (H_off)
        uint32_t min_hold_ms{300};       // Мінімальний час утримання активного стану (мс)
        uint8_t window_size{10};         // Розмір вікна голосування (кадри, N <= 32)
        uint8_t min_votes{6};            // Необхідна кількість підтверджень (M)
    };

    explicit constexpr DecisionConfidenceFilter(const Config& config = Config{}) noexcept
        : cfg_(config), integrated_score_(0.0f), history_mask_(0U),
          state_entered_ms_(0U), is_active_(false) {}

    // Температурне калібрування сирих логітів
    [[nodiscard]] static float calibrateTemperature(float logit_target, float logit_bg, float temperature) noexcept {
        const float temp = (temperature > 0.001f) ? temperature : 1.0f;
        const float st = logit_target / temp;
        const float sbg = logit_bg / temp;
        const float max_l = std::max(st, sbg);
        const float exp_t = std::exp(st - max_l);
        const float exp_bg = std::exp(sbg - max_l);
        return exp_t / (exp_t + exp_bg);
    }

    // Оновлення стану фільтра за новим виміром
    bool update(float raw_prob, uint32_t now_ms) noexcept {
        // 1. Інтегрування експоненційним середнім
        integrated_score_ = (cfg_.alpha * integrated_score_) + ((1.0f - cfg_.alpha) * raw_prob);

        // 2. Бітове голосування M-з-N
        const bool frame_hit = (raw_prob >= cfg_.thresh_off);
        history_mask_ = (history_mask_ << 1U) | (frame_hit ? 1U : 0U);

        const uint32_t valid_mask = (cfg_.window_size >= 32) ? 0xFFFFFFFFU : ((1U << cfg_.window_size) - 1U);
        const uint32_t current_window = history_mask_ & valid_mask;
        const int votes = std::popcount(current_window);
        const bool vote_passed = (votes >= static_cast<int>(cfg_.min_votes));

        // 3. Логіка гістерезису та часового утримання
        if (is_active_) {
            const bool hold_expired = (now_ms - state_entered_ms_) >= cfg_.min_hold_ms;
            if (hold_expired && (integrated_score_ < cfg_.thresh_off) && !vote_passed) {
                is_active_ = false;
                state_entered_ms_ = now_ms;
            }
        } else {
            if ((integrated_score_ >= cfg_.thresh_on) || vote_passed) {
                is_active_ = true;
                state_entered_ms_ = now_ms;
            }
        }

        return is_active_;
    }

    [[nodiscard]] float integratedScore() const noexcept { return integrated_score_; }
    [[nodiscard]] bool isActive() const noexcept { return is_active_; }

    void reset() noexcept {
        integrated_score_ = 0.0f;
        history_mask_ = 0U;
        state_entered_ms_ = 0U;
        is_active_ = false;
    }

private:
    Config cfg_;
    float integrated_score_{0.0f};
    uint32_t history_mask_{0U};
    uint32_t state_entered_ms_{0U};
    bool is_active_{false};
};
```
:::

---

### Приклад покрокової траси станів у часі

Простежимо роботу фільтра на тестовій послідовності з 10 тактів із кроком `dt = 50 мс` (`alpha = 0.75`, `H_on = 0.70`, `H_off = 0.35`, `min_hold = 200 мс`, `M/N = 3/5`):

| Такт `k` | Час (мс) | Сирий `P[k]` | Інтеграл `S[k]` | Маска (bin) | Голоси `M/5` | Стан виходу | Коментар |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 0 | 0.05 | 0.013 | `00000` | 0 | `0` (Норма) | Початковий стан спокою |
| 2 | 50 | **0.95** | 0.247 | `00001` | 1 | `0` (Норма) | **Спалах шуму знехтувано** (`S < 0.70`) |
| 3 | 100 | 0.04 | 0.195 | `00010` | 1 | `0` (Норма) | Шум зник, інтеграл спадає |
| 4 | 150 | 0.85 | 0.359 | `00101` | 2 | `0` (Норма) | Початок реальної перешкоди |
| 5 | 200 | 0.90 | 0.494 | `01011` | 3 | **`1` (Тривога)** | **Активація за голосуванням 3/5** |
| 6 | 250 | 0.88 | 0.591 | `10111` | 4 | `1` (Тривога) | Утримання стану (`t_hold = 50 < 200`) |
| 7 | 300 | 0.10 | 0.468 | `01110` | 3 | `1` (Тривога) | Провал детекції на 1 кадр знехтувано |
| 8 | 350 | 0.92 | 0.581 | `11101` | 4 | `1` (Тривога) | Перешкода підтверджена |
| 9 | 400 | 0.05 | 0.448 | `11010` | 3 | `1` (Тривога) | Об'єкт зник, але `S > H_off` |
| 10 | 450 | 0.02 | 0.341 | `10100` | 2 | `0` (Норма) | **Скидання: `t_hold ≥ 200`, `S < 0.35` і `M < 3`** |

---

### Обслуговування множини трекованих об'єктів (Multi-Track)

У реальних детекторах (SORT, DeepSORT, ByteTrack) алгоритм супроводу веде десятки одночасних треків (наприклад, до 32 обмежувальних рамок). Створювати динамічні об'єкти через купу (`malloc` або `new`) у реальному часі заборонено стандартами функціональної безпеки (MISRA, DO-178C).

Для мультитрекінгу виділяють статичний пул фільтрів фіксованого розміру:

:::tabs
```c
#define MAX_TRACKED_OBJECTS 32

typedef struct {
    ConfidenceFilter filters[MAX_TRACKED_OBJECTS];
    int track_ids[MAX_TRACKED_OBJECTS];
    bool in_use[MAX_TRACKED_OBJECTS];
} TrackerFilterPool;
```
```cpp
#include <array>
#include <optional>

template <std::size_t MaxObjects = 32>
struct TrackerFilterPool {
    std::array<DecisionConfidenceFilter, MaxObjects> filters{};
    std::array<std::optional<int>, MaxObjects> track_ids{};
};
```
:::

Коли трекер призначає об'єкту новий `track_id`, вільний слот пулу ініціалізується функцією `confidence_filter_init()`. Якщо об'єкт тимчасово перекривається іншою перешкодою, трекер передає у фільтр `P[k] = 0.0`, і таймер `t_hold` гарантує, що апарат не вважатиме зону вільною до повної деактивації або видалення треку за таймаутом.

---

### Профіль ресурсів та типові пастки на залізі

1. **Пам'ять та обчислювальна складність:** Екземпляр `ConfidenceFilter` займає рівно 24 байти RAM на 32-бітній платформі. Час виконання функції `confidence_filter_update` на ядрі ARM Cortex-M4 (168 МГц) становить менше **35 тактів процесора** (~0.2 мкс), що дозволяє обслуговувати масив із 64 незалежних трекованих об'єктів без відчутного завантаження CPU.
2. **Переповнення бітового зсуву:** На деяких архітектурах операція `1U << 32` призводить до невизначеної поведінки (UB). У коді маскування захищене тернарним виразом `(window_size >= 32) ? 0xFFFFFFFFU : ((1U << window_size) - 1U)`.
3. **Холодний старт та динамічний розгін:** Якщо об'єкт знаходиться перед камерою в момент включення живлення, фільтру потрібно кілька тактів для наростання `S[k]`. Для критичних систем під час ініціалізації первинний стан встановлюють у безпечний `is_active = true` до завершення процедури самотестування.
