# ⚙️ Моніторинг і фільтрація RSSI/RSRP у коді

Алгоритми обробки показників сигналу в радіомодемах запобігають деструктивному ефекту «пінг-понгу» (декілька швидких перемикань між базовими станціями на секунду) та стабілізують оцінку якості каналу. Оцифровані рівні RSRP та RSSI схильні до швидких замирань внаслідок багатопроменевого поширення (Rayleigh fading). Для прийняття надійних рішень про зміну соти або адаптацію модуляції сирі вибірки піддають фільтрації та перевірці гістерезисом.

## Фізика замирань сигналу та математична потреба у фільтрації

У мобільних та бездротових мережах електромагнітна хвиля поширюється від базової станції до приймача багатьма шляхами — відбиваючись від стін будинків, асфальтного покриття, автотранспорту та дерев. На вхідній антені приймача сумуються десятки відбитих копій сигналу з різними фазовими зсувами та часовими затримками.

Цей процес спричиняє два фундаментальні типи флуктуацій сигналу у просторі та часі:
1. **Швидкі замирання (Fast Fading / Rayleigh Fading):** Інтерференція відбитих хвиль спричиняє появу інтерференційної картини у просторі з максимумами й глибиною замирань у вузлах через кожні півдовжини хвилі (близько 7–15 см для діапазонів 1.8–2.6 ГГц). Коли автомобіль або мобільний термінал рухається зі швидкістю 60–90 км/год, виміряний RSRP може змінюватися на `15 ... 20 dB` кілька разів за секунду з доплерівською частотою `f_d = v / λ`. Якщо між антенним комплексом базової станції та приймачем є пряма видимість (Line-of-Sight, LOS), замирання підпорядковуються розподілу Ріса (Rician fading), де присутній потужний постійний вектор. За відсутності прямої видимості (Non-Line-of-Sight, NLOS) амплітуда підпорядковується розподілу Релея (Rayleigh fading), де ймовірність глибокого провалу сигналу значно вища.
2. **Повільні замирання (Slow Fading / Log-normal Shadowing):** Викликані затіненням сигналу великими материальними перешкодами (будівлі, рельєф місцевості, залізобетонні мости). Потужність сигналу узагальнено підпорядковується логнормальному розподілу з просторовою кореляційною відстанню 20–100 метрів.

Якщо модулі керування мережевим стеком будуть реагувати на кожну швидку вибірку RSRP без попередньої фільтрації, система потрапить у стан хибного хендоверу. Пристрій почне постійно перемикати активне з'єднання між двома вежами, витрачаючи ресурси процесора, виснажуючи акумулятор та спричиняючи масові втрати мережевих пакетів.

### Доплерівське зміщення та час когерентності каналу

Максимальна доплерівська частота `f_d` залежить від швидкості руху пристрою `v`, швидкості світла `c` та несучої частоти `f_carrier`:

```text
f_d = (v / c) · f_carrier
```

Наприклад, при русі автомобіля зі швидкістю `v = 90 км/год = 25 м/с` на частоті `f_carrier = 2.1 ГГц` (`λ = 0.1428 м`):

```text
f_d = 25 / 0.1428 ≈ 175 Гц
```

Час когерентності каналу `T_c` (інтервал, протягом якого амплітуда сигналу залишається корельованою) обчислюється як:

```text
T_c ≈ 0.423 / f_d = 0.423 / 175 ≈ 2.4 мс
```

Це означає, що при русі авто кожні 2.4 мс радіоканал отримує абсолютно нове значення замирання. Завдання цифрового фільтра — усереднити ці коливання за часовий інтервал, що значно перевищує `T_c` (типово 1–2 секунди).

## Математична модель фільтрації за специфікацією 3GPP TS 36.331

У специфікаціях 3GPP LTE/5G (TS 36.331, розділ 5.5.3.2) висунуто чітку математичну формулу Layer 3 Filtering для згладжування вимірювань RSRP та RSRQ:

```text
F_n = (1 - a) · F_{n-1} + a · M_n
```

де:
- `F_n` — нове згладжене значення вимірювання;
- `F_{n-1}` — попереднє згладжене значення вимірювання;
- `M_n` — останнє фізичне вимірювання, отримане від фізичного рівня L1;
- `a = 1 / 2^(k / 4)` — коефіцієнт згладжування, де `k` — параметр `filterCoefficient`, що передається в повідомленні RRC Connection Reconfiguration.

### Таблиця відповідності коефіцієнтів 3GPP та значення α

Параметр `k` (поле `filterCoefficient`) набуває значень від 0 до 19:

| Коефіцієнт 3GPP `k` | Значення `a = 1 / 2^(k/4)` | Фізичний аналог `α` у фільтрі EMA | Постійна часу `τ` (при Δt=200мс) |
|---|---|---|---|
| `k = 0` (fc0) | `1 / 2⁰ = 1.000` | `1.00` (фільтрація вимкнена) | `0.0 с` |
| `k = 2` (fc2) | `1 / 2⁰⁵ = 0.707` | `0.71` | `0.08 с` |
| `k = 4` (fc4) | `1 / 2¹ = 0.500` | `0.50` | `0.20 с` |
| `k = 6` (fc6) | `1 / 2¹⁵ = 0.354` | `0.35` | `0.45 с` |
| `k = 8` (fc8) | `1 / 2² = 0.250` | `0.25` (стандартне значення) | `0.70 с` |
| `k = 12` (fc12) | `1 / 2³ = 0.125` | `0.125` | `1.45 с` |
| `k = 16` (fc16) | `1 / 2⁴ = 0.0625` | `0.0625` | `3.05 с` |

Значення `k = 4` використовується для швидкої реакції в умовах щільної міської забудови, тоді як `k = 8` або `k = 12` застосовують на автомагістралях для стабілізації оцінки соти.

## Процедура Handover у протокольному стеку

Фільтровані значення `F_n` передаються в модуль прийняття рішень протоколу RRC. Процедура переходу між базовими станціями включає такі кроки:

1. **Опитування та Layer 3 Filtering:** Фізичний рівень L1 кожні 5–10 мс знімає сирі вибірки `M_n` й передає їх на рівень L3, де застосовується формула `F_n`.
2. **Оцінка умов Event A3:** Модуль RRC перевіряє нерівність `RSRP_neighbor_filtered > RSRP_serving_filtered + Hysteresis`.
3. **Відлік Time-to-Trigger (TTT):** Якщо умова виконується протягом інтервалу `TTT` (наприклад, 480 мс), термінал формує повідомлення `RRCMeasurementReport` і відправляє його на поточну базову станцію.
4. **Обмін повідомленнями між базовими станціями:** Вихідна вежа (Source eNB) надсилає запит `Handover Request` на цільову вежу (Target eNB) через інтерфейс X2 або S1.
5. **Команда Handover Command:** Після виділення ресурсів цільовою вежею термінал отримує команду `RRCConnectionReconfiguration` із параметрами мобільності й виконує швидкий перехід (RACH procedure) на нову соту.

## Алгоритм гістерезису та Time-to-Trigger (TTT)

Навіть після згладжування сигналу фільтром EMA пристрій може перебувати на межі покриття двох сот `A` та `B`, де їхні середні рівні RSRP майже однакові (`RSRP_A ≈ RSRP_B`).

Для прийняття остаточного рішення про перехід застосовують кінцевий автомат зі станом **Time-to-Trigger (TTT)** та параметром **гістерезису (Hysteresis Margin)**.

### Умова запуску хендоверу (Event A3 у 3GPP LTE)

Хендовер на сусідню соту `B` ініціюється тоді й лише тоді, коли виконується нерівність:

```text
RSRP_B_filtered > RSRP_A_filtered + H_margin
```

де `H_margin` — гістерезисний запас (типово від `2.0 dB` до `4.0 dB`).

Після виконання цієї умови запускається таймер утримання `TTT`. Якщо протягом заданої кількості послідовних вибірок `N_samples` (або часу `T_ttt`, наприклад 480 мс) умова зберігається, приймається остаточне рішення про виконання хендоверу. Якщо під час відліку сигнал соти `B` знову впав нижче порогу, таймер скидається в нуль.

## Реалізація у коді: C та C++

У програмістських проектах вбудованих систем (embedded firmware) та системних демонах Linux реалізація обробки вимагає високої обчислювальної ефективності, відсутності фрагментації пам'яті та коректної обробки крайових випадків (наприклад, втрата сигналу чи відсутність вибірок).

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define MAX_NEIGHBORS 4
#define DEFAULT_ALPHA 0.25
#define HYSTERESIS_MARGIN_DB 3.0
#define TIME_TO_TRIGGER_SAMPLES 3
#define INVALID_SIGNAL_DBM -140.0

typedef struct {
    int cell_id;
    double raw_rsrp_dbm;
    double raw_rssi_dbm;
    double filtered_rsrp_dbm;
    double filtered_rssi_dbm;
    bool is_initialized;
} CellSignalMetric;

typedef struct {
    int active_cell_id;
    CellSignalMetric active_cell;
    CellSignalMetric neighbors[MAX_NEIGHBORS];
    size_t neighbor_count;
    
    // Стан алгоритму хендоверу
    int candidate_cell_id;
    int ttt_counter;
} SignalMonitor;

void signal_monitor_init(SignalMonitor *mon, int initial_cell_id) {
    mon->active_cell_id = initial_cell_id;
    mon->active_cell.cell_id = initial_cell_id;
    mon->active_cell.raw_rsrp_dbm = INVALID_SIGNAL_DBM;
    mon->active_cell.raw_rssi_dbm = INVALID_SIGNAL_DBM;
    mon->active_cell.filtered_rsrp_dbm = INVALID_SIGNAL_DBM;
    mon->active_cell.filtered_rssi_dbm = INVALID_SIGNAL_DBM;
    mon->active_cell.is_initialized = false;
    mon->neighbor_count = 0;
    mon->candidate_cell_id = -1;
    mon->ttt_counter = 0;
}

static double apply_3gpp_ema_filter(double previous, double current, double alpha, bool is_init) {
    if (!is_init || current <= INVALID_SIGNAL_DBM) {
        return current;
    }
    return alpha * current + (1.0 - alpha) * previous;
}

void signal_monitor_update_cell(CellSignalMetric *metric, double raw_rsrp, double raw_rssi, double alpha) {
    if (raw_rsrp <= INVALID_SIGNAL_DBM) {
        return; // Ігноруємо некоректні вибірки модема
    }
    
    metric->raw_rsrp_dbm = raw_rsrp;
    metric->raw_rssi_dbm = raw_rssi;
    
    metric->filtered_rsrp_dbm = apply_3gpp_ema_filter(metric->filtered_rsrp_dbm, raw_rsrp, alpha, metric->is_initialized);
    metric->filtered_rssi_dbm = apply_3gpp_ema_filter(metric->filtered_rssi_dbm, raw_rssi, alpha, metric->is_initialized);
    metric->is_initialized = true;
}

bool signal_monitor_process_sample(SignalMonitor *mon, double active_rsrp, double active_rssi) {
    signal_monitor_update_cell(&mon->active_cell, active_rsrp, active_rssi, DEFAULT_ALPHA);
    
    // Пошук кращої сусідньої соти з урахуванням гістерезису
    int best_candidate_id = -1;
    double max_neighbor_rsrp = mon->active_cell.filtered_rsrp_dbm + HYSTERESIS_MARGIN_DB;
    
    for (size_t i = 0; i < mon->neighbor_count; ++i) {
        if (mon->neighbors[i].is_initialized && 
            mon->neighbors[i].filtered_rsrp_dbm > max_neighbor_rsrp) {
            max_neighbor_rsrp = mon->neighbors[i].filtered_rsrp_dbm;
            best_candidate_id = mon->neighbors[i].cell_id;
        }
    }
    
    // Перевірка умови Time-to-Trigger (TTT)
    if (best_candidate_id != -1) {
        if (best_candidate_id == mon->candidate_cell_id) {
            mon->ttt_counter++;
        } else {
            mon->candidate_cell_id = best_candidate_id;
            mon->ttt_counter = 1;
        }
        
        if (mon->ttt_counter >= TIME_TO_TRIGGER_SAMPLES) {
            printf("[HANDOVER] Виконано перехід: сота %d -> %d (Новий RSRP: %.1f dBm)\n",
                   mon->active_cell_id, best_candidate_id, max_neighbor_rsrp);
            mon->active_cell_id = best_candidate_id;
            mon->candidate_cell_id = -1;
            mon->ttt_counter = 0;
            return true; // Перехід підтверджено
        }
    } else {
        mon->candidate_cell_id = -1;
        mon->ttt_counter = 0;
    }
    
    return false;
}
```
```cpp
#include <iostream>
#include <vector>
#include <optional>
#include <algorithm>
#include <span>

struct CellMetric {
    int cell_id{0};
    double raw_rsrp_dbm{-140.0};
    double raw_rssi_dbm{-140.0};
    double filtered_rsrp_dbm{-140.0};
    double filtered_rssi_dbm{-140.0};
    bool initialized{false};

    void update(double rsrp, double rssi, double alpha) noexcept {
        if (rsrp <= -140.0) {
            return; // Пропуск некоректних даних
        }
        raw_rsrp_dbm = rsrp;
        raw_rssi_dbm = rssi;
        if (!initialized) {
            filtered_rsrp_dbm = rsrp;
            filtered_rssi_dbm = rssi;
            initialized = true;
        } else {
            filtered_rsrp_dbm = alpha * rsrp + (1.0 - alpha) * filtered_rsrp_dbm;
            filtered_rssi_dbm = alpha * rssi + (1.0 - alpha) * filtered_rssi_dbm;
        }
    }
};

class SignalMonitor {
public:
    explicit SignalMonitor(int initial_cell_id, double alpha = 0.25, 
                          double hysteresis_db = 3.0, std::size_t ttt_samples = 3)
        : active_cell_id_(initial_cell_id), alpha_(alpha),
          hysteresis_margin_db_(hysteresis_db), time_to_trigger_samples_(ttt_samples) {
        active_cell_.cell_id = initial_cell_id;
    }

    void set_3gpp_filter_coefficient(int k_coeff) noexcept {
        // Конвертація параметра 3GPP filterCoefficient k у alpha = 1 / 2^(k/4)
        if (k_coeff <= 0) {
            alpha_ = 1.0;
        } else {
            alpha_ = 1.0 / std::pow(2.0, static_cast<double>(k_coeff) / 4.0);
        }
    }

    void update_neighbor(int cell_id, double rsrp, double rssi) {
        auto it = std::find_if(neighbors_.begin(), neighbors_.end(),
                               [cell_id](const CellMetric& m) { return m.cell_id == cell_id; });
        if (it != neighbors_.end()) {
            it->update(rsrp, rssi, alpha_);
        } else {
            CellMetric new_metric{.cell_id = cell_id};
            new_metric.update(rsrp, rssi, alpha_);
            neighbors_.push_back(new_metric);
        }
    }

    bool process_active_sample(double active_rsrp, double active_rssi) {
        active_cell_.update(active_rsrp, active_rssi, alpha_);

        std::optional<int> best_candidate_id;
        double highest_rsrp = active_cell_.filtered_rsrp_dbm + hysteresis_margin_db_;

        for (const auto& neighbor : neighbors_) {
            if (neighbor.initialized && neighbor.filtered_rsrp_dbm > highest_rsrp) {
                highest_rsrp = neighbor.filtered_rsrp_dbm;
                best_candidate_id = neighbor.cell_id;
            }
        }

        if (best_candidate_id.has_value()) {
            if (best_candidate_id == candidate_cell_id_) {
                ++ttt_counter_;
            } else {
                candidate_cell_id_ = best_candidate_id;
                ttt_counter_ = 1;
            }

            if (ttt_counter_ >= time_to_trigger_samples_) {
                std::cout << "[HANDOVER] Прийнято рішення: сота " << active_cell_id_ 
                          << " -> " << *best_candidate_id 
                          << " (Згладжений RSRP: " << highest_rsrp << " dBm)\n";
                active_cell_id_ = *best_candidate_id;
                candidate_cell_id_.reset();
                ttt_counter_ = 0;
                return true;
            }
        } else {
            candidate_cell_id_.reset();
            ttt_counter_ = 0;
        }

        return false;
    }

    [[nodiscard]] double get_active_rsrp() const noexcept {
        return active_cell_.filtered_rsrp_dbm;
    }

    [[nodiscard]] int get_active_cell_id() const noexcept {
        return active_cell_id_;
    }

private:
    int active_cell_id_;
    double alpha_;
    double hysteresis_margin_db_;
    std::size_t time_to_trigger_samples_;
    
    CellMetric active_cell_;
    std::vector<CellMetric> neighbors_;
    
    std::optional<int> candidate_cell_id_;
    std::size_t ttt_counter_{0};
};
```
:::

## Аналіз архітектурних рішень та крайових випадків

### 1. Ініціалізація та перша вибірка (Cold Start)

При старті пристрою значення `S[0]` фільтра EMA ще відсутнє. Якщо встановити початковий стан у нуль (`0.0`), це відповідатиме потужності `+30 dBm` (1 Ват), що викривить фільтрацію на десятки секунд. Тому в коді використовується прапорець `initialized`: перша ж валідна вибірка безпосередньо записується у `filtered_rsrp_dbm`, обминаючи вагову суму.

### 2. Скидання фільтра при виконанні Handover

Після прийняття рішення про хендовер на нову соту її історія у фільтрі повинна стати поточною активною метрикою. Програма переносить згладжені значення з елемента `neighbors` у `active_cell` та очищає лічильники TTT.

### 3. Логарифмічна проти Лінійної фільтрації

В даному коді фільтрація EMA виконується безпосередньо над логарифмічними величинами дБм (децибелах). Це відповідає стандарту 3GPP TS 36.331 для Layer 3 Filtering. З математичної точки зору усереднення у децибелах є **геометричним усередненням** лінійних потужностей. Це запобігає асиметричному викривленню середнього значення при появі поодиноких потужних пікових вибірок.

### 4. Оптимізація для мікроконтролерів без блоку FPU

У малопотужних мікроконтролерах без апаратного блоку обчислення плаваючої крапки (FPU, наприклад ARM Cortex-M0/M3) арифметику з плаваючою крапкою `double` замінюють на цілочисельну арифметику з фіксованою комою (Fixed-Point). Значення дБм зберігають у вигляді знакового 16-бітного цілого числа, помноженого на 100 (наприклад, `-9550` відповідає `-95.50 dBm`), а розрахунок EMA виконують бітовими зсувами:

```c
// Еквівалент α = 0.25 (1/4) у цілочисельній арифметиці фіксованої коми
int16_t filtered_q100 = previous_q100 + ((current_q100 - previous_q100) >> 2);
```

Це дозволяє розраховувати згладжування за 3-4 такти процесора без залучення бібліотек програмної емуляції плаваючої коми.

### 5. Обробка стрімкої втрати покриття (Radio Link Failure, RLF)

Якщо пристрій потрапляє в тунель або підземне укриття, RSRP може впасти з `-85 dBm` до `-135 dBm` за 100 мс. Фільтр EMA з малим `α` згладжує цей падіння протягом 2-3 секунд.

Для запобігання зависанню алгоритму в системі передбачено миттєвий скид станів: якщо сире значення `raw_rsrp` опускається нижче порогу `-130 dBm` дві вибірки поспіль, стан фільтрації форсовано переводиться у режим пошуку мережі (Out-of-Service / RLF), не чекаючи таймера TTT.

### 6. Адаптивна динаміка постійної часу фільтра залежно від швидкості руху

У просунутих алгоритмах мобільності параметри згладжування `α` коригуються динамічно на основі оцінки швидкості термінала.

При оцінці високої швидкості (High Mobility, рух потягом чи авто на 120 км/год) коефіцієнт `α` тимчасово підвищується до `0.50` (`k = 4`), щоб система встигала відстежувати швидкі зміни геологічного покриття сот. При стаціонарному розміщенні (Low Mobility / Pedestrian, швидкість до 3 км/год) `α` знижується до `0.125` (`k = 12`) для забезпечення максимальної стабільності сигналу та виключення хибних реакцій на дрібні флуктуації.

У коді C++ це реалізується викликом методу `set_3gpp_filter_coefficient(int k_coeff)`, який обчислює новий коефіцієнт ваги як `alpha = 1.0 / std::pow(2.0, k / 4.0)`.

### 7. Модульне тестування (Unit Testing Strategy)

Для перевірки коректності роботи алгоритму моніторингу в ізольованому середовищі розробляють набір модульних тестів (Unit Tests), які моделюють типові радіосценарії:
- **Тест 1 (Cold Start):** Перевірка запису першої ж вибірки в `filtered_rsrp_dbm` без перехідного процесу від нуля.
- **Тест 2 (Hysteresis Guard):** Подача вибірок сусідньої соти на `+2.0 dB` вище активної (при порозі `+3.0 dB`). Рішення про хендовер не повинно прийматися (`process_active_sample` повертає `false`).
- **Тест 3 (TTT Counter Expiry):** Подача вибірок сусідньої соти на `+4.0 dB` вище активної протягом 3 вибірок поспіль. На третій вибірці повертається `true`, а `active_cell_id` змінюється на ідентифікатор цільової соти.
- **Тест 4 (TTT Reset):** Подача вибірок на `+4.0 dB` протягом 2 вибірок, після чого третя вибірка падає нижче порогу. Лічильник TTT повинен скинутися у нуль.

Цей підхід гарантує високу надійність функціонування мережевого стека в реальних умовах ефіру.
