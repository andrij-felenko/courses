# ⚙️ Алгоритм обробки TDR-рефлектограми та обчислення профілю імпедансу

Цифрова обробка сигналів (DSP) у часовій рефлектометрії полягає у перетворенні сирого дигресованого масиву напруги `V[i]`, зчитаного зі стробоскопічного змішувача або аналогово-цифрового перетворювача (АЦП), у фізично зрозумілий профіль локального імпедансу лінії `Z(x)` та точну локалізацію дефектів у метрах або міліметрах.

Нижче детально описано архітектуру обробки TDR-даних, математичний апарат фільтрації, процедуру деконволюції та практичні реалізації алгоритму аналізу мовами C та C++.

---

### Архітектура цифрового конвеєра обробки TDR-сигналу

Обробка рефлектограми у реальному часі розгортається у конвеєр із шести послідовних етапів:

```
[Сирий масив V[i]] → [1. Фільтрація шуму] → [2. Детектування фронту t₀] → 
→ [3. Розрахунок Gamma[i]] → [4. Інверсія Z[i]] → [5. Пошук і класифікація подій]
```

#### 1. Фільтрація шумів та згладжування (Noise Reduction)
Вхідний масив відліків напруги зі стробоскопічного осцилографа піддається впливу теплового шуму приймача та джиттеру генератора перепаду. Для запобігання хибним спрацьовуванням детектора піків застосовується ковзне середнє (Moving Average) або фільтр Савицького — Голея (Savitzky-Golay filter).

Фільтр Савицького — Голея є відносно складнішим, ніж ковзне середнє, але він має важливу перевагу: він згладжує тепловий шум, не розмиваючи гострі піки фронтів індуктивностей та ємностей.

Для ковзного середнього з вікном розміром `2M + 1` згладжене значення відліку `V_smooth[i]` обчислюється як:

```
V_smooth[i] = (1 / (2M + 1)) · ∑_{k=-M}^{M} V[i + k]
```

#### 2. Оцінка базової лінії та детектування фронту $t_0$
Перші відліки масиву відповідають ділянці лінії до надходження падаючого перепаду. Алгоритм усереднює перші N відліків для визначення рівня постійного зсуву базової лінії `V_base`.

Точка відліку часу `t₀` (момент виходу перепаду з зонда в досліджувану лінію) визначається за методом перетину 50%-вого рівня падаючого перепаду `V_thresh`:

```
V_inc = V_max - V_base
V_thresh = V_base + 0.5 · V_inc
```

Для підвищення просторової точності застосовується субдискретна лінійна інтерполяція між сусідніми відліками `k` та `k+1`, між якими сигнал перетинає поріг `V_thresh`:

```
t₀ = t[k] + dt · (V_thresh - V[k]) / (V[k+1] - V[k])
```

Завдяки субдискретній інтерполяції точність фіксації точки `t₀` зростає в кілька разів порівняно з простим вибором найближчого цілого відліку `k`.

#### 3. Масштабування координати відстані та коефіцієнта відбиття
Для кожного відліку `i`, що відповідає часовій затримці `t[i] > t₀`, розраховується просторова координата `x[i]` з урахуванням швидкості поширення хвилі в діелектрику `v = c / √(ε_r)`:

```
x[i] = (c · (t[i] - t₀)) / (2 · √(ε_r))
```

Коефіцієнт відбиття `Γ[i]` обчислюється шляхом нормалізації амплітуди:

```
Γ[i] = (V[i] - (V_base + V_inc)) / V_inc
```

Значення `Γ[i]` програмно обмежуються діапазоном `[-0.999, +0.999]` для запобігання діленню на нуль або отриманню від'ємних значень опору.

#### 4. Обчислення профілю імпедансу $Z(x)$
Значення хвильового опору в кожній точці лінії розраховуються за формулою інверсії:

```
Z[i] = Z₀ · (1 + Γ[i]) / (1 - Γ[i])
```

#### 5. Детектування та класифікація дефектів (Event Detection & Fault Classifier)
Аналізатор виконує пошук локальних екстремумів `Γ[i]` шляхом відстеження знака першої похідної `dΓ/dt`. Виявлені події класифікуються за таблицею порогів:

| Значення коефіцієнта відбиття | Тип виявленого дефекту | Фізична причина |
| :--- | :--- | :--- |
| `Γ > +0.85` | Обрив (Open Circuit) | Механічний розрив центральної жили, знятий роз'єм |
| `Γ < -0.85` | Коротке замикання (Short Circuit) | Пробій діелектрика, замикання екрана на жилу |
| `+0.15 < Γ ≤ +0.85` | Високоомна неоднорідність | Звуження доріжки, перехід на кабель 75 Ом, тріщина |
| `-0.85 ≤ Γ < -0.15` | Низькоомна неоднорідність | Потовщення доріжки, розчавлений кабель, волога |
| Гострий позитивний пік | Послідовна індуктивність `L` | Індуктивність розварювального дротика чи виводу BGA |
| Гострий негативний провал | Паралельна ємність `C` | Ємність перехідного отвору (Via) або контактного майданчика |

---

### Деконволюція та програмне загострення фронту (Deconvolution)

У реальних TDR-системах виміряний сигнал є результат згортки (Convolution) істинного відгуку лінії `V_true(t)` з імпульсною характеристикою вимірювального тракту `h_sys(t)`, що охоплює скінченний фронт наростання генератора, смугу осцилографа та згасання з'єднувального кабелю:

```
V_meas(t) = V_true(t) * h_sys(t)
```

Для відновлення початкової просторової роздільної здатності алгоритм виконує **математичну деконволюцію** у частотній області за допомогою Швидкого Перетворення Фур'є (FFT).

1. Перехід у частотну область: `V_meas(f) = FFT(V_meas(t))` та `H_sys(f) = FFT(h_sys(t))`.
2. Застосування регуляризації Тихонова для запобігання діленню на нуль у високочастотних шумах:

```
V_true(f) = (V_meas(f) · H_sys*(f)) / (|H_sys(f)|² + λ)
```

де `λ` — коефіцієнт регуляризації (Regularization parameter), а `H_sys*` — комплексно-спряжена величина.
3. Повернення у часову область через зворотне перетворення: `V_true(t) = IFFT(V_true(f))`.

Ця операція дозволяє програмно «звузити» еквівалентний фронт перепаду напруги з 30 пікосекунд до 10 пікосекунд, підвищуючи просторову роздільну здатність плати майже утричі.

---

### Процедура компенсації опорної площини (Deskew Calibration)

Перед проведенням автоматизованого аналізу плати алгоритм вимагає вимірювання опорної рефлектограми калібрувального стандарту (Short або Open), підключеного безпосередньо до торця вимірювального зонда.

* **Етап 1:** Запис опорної траси `V_ref[i]` калібрувального обриву.
* **Етап 2:** Автоматичне знаходження точки `t_ref`, що відповідає торцю зонда.
* **Етап 3:** Математичне віднімання часового зсуву `t_ref` від усього подальшого масиву вимірювань (`t₀ = t_ref`). Це дає змогу встановити точну нульову просторову координату `x = 0.0 м` на контактному майданчику досліджуваного приладу.

---

### Практична реалізація мовами C та C++

Нижче наведено робочі реалізації конвеєра аналізу TDR-рефлектограми.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#define C_SPEED 299792458.0  /* Швидкість світла у м/с */

typedef enum {
    FAULT_NONE = 0,
    FAULT_SHORT,
    FAULT_OPEN,
    FAULT_HIGH_IMPEDANCE,
    FAULT_LOW_IMPEDANCE,
    FAULT_CAPACITIVE_DIP,
    FAULT_INDUCTIVE_PEAK
} FaultType;

typedef struct {
    double distance_m;
    double time_ns;
    double gamma;
    double impedance_ohm;
    FaultType type;
} TdrEvent;

/*
 * Згладжування масиву сигналів ковзним середнім (вікно 2M+1)
 */
void filter_moving_average(const double* in_buf, double* out_buf, int len, int window_half) {
    for (int i = 0; i < len; ++i) {
        double sum = 0.0;
        int count = 0;
        for (int k = -window_half; k <= window_half; ++k) {
            int idx = i + k;
            if (idx >= 0 && idx < len) {
                sum += in_buf[idx];
                count++;
            }
        }
        out_buf[i] = sum / count;
    }
}

/*
 * Головна функція аналізу TDR-сигналу
 */
int analyze_tdr_trace(const double* raw_voltage, int num_samples, double dt_sec,
                      double z0_ohm, double er_relative,
                      double* out_distance, double* out_impedance,
                      TdrEvent* out_events, int max_events, int* out_event_count) {
    if (!raw_voltage || num_samples < 20 || dt_sec <= 0.0 || z0_ohm <= 0.0 || er_relative < 1.0) {
        return -1;
    }

    /* Фільтрація шуму */
    double* smooth_v = (double*)malloc(num_samples * sizeof(double));
    if (!smooth_v) return -2;
    filter_moving_average(raw_voltage, smooth_v, num_samples, 2);

    /* 1. Обчислення базової лінії V_base (перші 10 відліків) */
    double v_base = 0.0;
    for (int i = 0; i < 10; ++i) {
        v_base += smooth_v[i];
    }
    v_base /= 10.0;

    /* 2. Пошук амплітуди падаючого перепаду V_inc */
    double v_max = smooth_v[0];
    for (int i = 1; i < num_samples; ++i) {
        if (smooth_v[i] > v_max) v_max = smooth_v[i];
    }
    double v_inc = v_max - v_base;
    if (v_inc < 1e-4) {
        free(smooth_v);
        return -3; /* Перепад не виявлено */
    }

    /* 3. Детектування точки фронту t0 (перетин 50% V_inc із субдискретною інтерполяцією) */
    double v_thresh = v_base + 0.5 * v_inc;
    double t0_sample_idx = -1.0;

    for (int i = 0; i < num_samples - 1; ++i) {
        if (smooth_v[i] <= v_thresh && smooth_v[i+1] > v_thresh) {
            double dy = smooth_v[i+1] - smooth_v[i];
            double fraction = (dy > 1e-9) ? ((v_thresh - smooth_v[i]) / dy) : 0.0;
            t0_sample_idx = i + fraction;
            break;
        }
    }

    if (t0_sample_idx < 0.0) {
        free(smooth_v);
        return -4;
    }

    /* 4. Швидкість поширення хвилі */
    double v_prop = C_SPEED / sqrt(er_relative);

    /* 5. Розрахунок профілю відстані та імпедансу */
    for (int i = 0; i < num_samples; ++i) {
        double dt = (i - t0_sample_idx) * dt_sec;
        out_distance[i] = (dt > 0.0) ? (v_prop * dt / 2.0) : 0.0;

        double gamma = (smooth_v[i] - (v_base + v_inc)) / v_inc;
        if (gamma > 0.999) gamma = 0.999;
        if (gamma < -0.999) gamma = -0.999;

        out_impedance[i] = z0_ohm * (1.0 + gamma) / (1.0 - gamma);
    }

    /* 6. Пошук неоднорідностей (Event Detection) */
    int event_cnt = 0;
    int start_search = (int)t0_sample_idx + 5;

    for (int i = start_search; i < num_samples - 1; ++i) {
        double gamma = (smooth_v[i] - (v_base + v_inc)) / v_inc;

        /* Перевірка на суттєве відхилення (пороги) */
        if (fabs(gamma) > 0.12) {
            /* Пошук локального екстремуму */
            if ((smooth_v[i] >= smooth_v[i-1] && smooth_v[i] >= smooth_v[i+1]) ||
                (smooth_v[i] <= smooth_v[i-1] && smooth_v[i] <= smooth_v[i+1])) {

                if (event_cnt < max_events) {
                    out_events[event_cnt].distance_m = out_distance[i];
                    out_events[event_cnt].time_ns = (i - t0_sample_idx) * dt_sec * 1e9;
                    out_events[event_cnt].gamma = gamma;
                    out_events[event_cnt].impedance_ohm = out_impedance[i];

                    if (gamma > 0.85) out_events[event_cnt].type = FAULT_OPEN;
                    else if (gamma < -0.85) out_events[event_cnt].type = FAULT_SHORT;
                    else if (gamma > 0.15) out_events[event_cnt].type = FAULT_HIGH_IMPEDANCE;
                    else if (gamma < -0.15) out_events[event_cnt].type = FAULT_LOW_IMPEDANCE;
                    else out_events[event_cnt].type = FAULT_NONE;

                    event_cnt++;
                    i += 3; /* Пропуск сусідніх відліків для виключення дублювання */
                }
            }
        }
    }

    if (out_event_count) *out_event_count = event_cnt;
    free(smooth_v);
    return 0;
}
```
```cpp
#include <vector>
#include <cmath>
#include <optional>
#include <stdexcept>
#include <string_view>
#include <algorithm>
#include <span>
#include <numeric>

enum class FaultType {
    None,
    ShortCircuit,
    OpenCircuit,
    HighImpedance,
    LowImpedance,
    CapacitiveDip,
    InductivePeak
};

struct TdrEvent {
    double distance_m{0.0};
    double time_ns{0.0};
    double gamma{0.0};
    double impedance_ohm{0.0};
    FaultType type{FaultType::None};
};

struct TdrAnalysisResult {
    std::vector<double> distances_m;
    std::vector<double> impedances_ohm;
    std::vector<TdrEvent> detected_events;
};

class TdrAnalyzer {
public:
    static constexpr double SpeedOfLight = 299792458.0;

    static TdrAnalysisResult process(std::span<const double> raw_voltage,
                                     double dt_sec,
                                     double z0_ohm = 50.0,
                                     double er_relative = 2.25) {
        if (raw_voltage.size() < 20) {
            throw std::invalid_argument("Масив відліків занадто малий для аналізу (мінімум 20)");
        }
        if (dt_sec <= 0.0 || z0_ohm <= 0.0 || er_relative < 1.0) {
            throw std::invalid_argument("Некоректні фізичні параметри лінії");
        }

        // 1. Фільтрація шуму ковзним середнім (вікно = 5 відліків)
        std::vector<double> v_smooth(raw_voltage.size());
        for (size_t i = 0; i < raw_voltage.size(); ++i) {
            double sum = 0.0;
            size_t count = 0;
            for (int k = -2; k <= 2; ++k) {
                ssize_t idx = static_cast<ssize_t>(i) + k;
                if (idx >= 0 && idx < static_cast<ssize_t>(raw_voltage.size())) {
                    sum += raw_voltage[idx];
                    count++;
                }
            }
            v_smooth[i] = sum / static_cast<double>(count);
        }

        // 2. Оцінка рівня базової лінії V_base
        const double v_base = std::accumulate(v_smooth.begin(), v_smooth.begin() + 10, 0.0) / 10.0;

        // 3. Пошук максимуму перепаду
        const double v_max = *std::max_element(v_smooth.begin(), v_smooth.end());
        const double v_inc = v_max - v_base;
        if (v_inc < 1e-4) {
            throw std::runtime_error("Падаючий перепад напруги не виявлено у масиві");
        }

        // 4. Детектування фронту t0 із субдискретною інтерполяцією
        const double v_thresh = v_base + 0.5 * v_inc;
        double t0_idx = -1.0;

        for (size_t i = 0; i < v_smooth.size() - 1; ++i) {
            if (v_smooth[i] <= v_thresh && v_smooth[i + 1] > v_thresh) {
                const double dy = v_smooth[i + 1] - v_smooth[i];
                const double fraction = (dy > 1e-9) ? ((v_thresh - v_smooth[i]) / dy) : 0.0;
                t0_idx = static_cast<double>(i) + fraction;
                break;
            }
        }

        if (t0_idx < 0.0) {
            throw std::runtime_error("Фронт наростання перепаду не перетинає рівень 50%");
        }

        TdrAnalysisResult result;
        result.distances_m.resize(v_smooth.size());
        result.impedances_ohm.resize(v_smooth.size());

        const double v_prop = SpeedOfLight / std::sqrt(er_relative);

        // 5. Розрахунок профілю відстаней та опорів
        for (size_t i = 0; i < v_smooth.size(); ++i) {
            const double dt = (static_cast<double>(i) - t0_idx) * dt_sec;
            result.distances_m[i] = (dt > 0.0) ? (v_prop * dt / 2.0) : 0.0;

            double gamma = (v_smooth[i] - (v_base + v_inc)) / v_inc;
            gamma = std::clamp(gamma, -0.999, 0.999);

            result.impedances_ohm[i] = z0_ohm * (1.0 + gamma) / (1.0 - gamma);
        }

        // 6. Виявлення подій (Event Detector)
        const size_t start_idx = static_cast<size_t>(t0_idx) + 5;
        for (size_t i = start_idx; i < v_smooth.size() - 1; ++i) {
            const double gamma = (v_smooth[i] - (v_base + v_inc)) / v_inc;

            if (std::abs(gamma) > 0.12) {
                // Перевірка умови локального екстремуму
                if ((v_smooth[i] >= v_smooth[i - 1] && v_smooth[i] >= v_smooth[i + 1]) ||
                    (v_smooth[i] <= v_smooth[i - 1] && v_smooth[i] <= v_smooth[i + 1])) {

                    TdrEvent ev;
                    ev.distance_m = result.distances_m[i];
                    ev.time_ns = (static_cast<double>(i) - t0_idx) * dt_sec * 1e9;
                    ev.gamma = gamma;
                    ev.impedance_ohm = result.impedances_ohm[i];

                    if (gamma > 0.85) ev.type = FaultType::OpenCircuit;
                    else if (gamma < -0.85) ev.type = FaultType::ShortCircuit;
                    else if (gamma > 0.15) ev.type = FaultType::HighImpedance;
                    else if (gamma < -0.15) ev.type = FaultType::LowImpedance;

                    result.detected_events.push_back(ev);
                    i += 3; // Антидребезговий зсув
                }
            }
        }

        return result;
    }
};
```
:::

---

### Особливості граничних випадків та неідеальностей

При практичному розгортанні алгоритму обробки на вимірювальному обладнанні слід ураховувати такі інженерні нюанси:

1. **Дисперсія діелектрика плати:** У склотекстоліті FR-4 діелектрична проникність знижується з ростом частоти (від `ε_r ≈ 4.3` на 100 МГц до `ε_r ≈ 3.8` на 10 ГГц). Це призводить до того, що високочастотні складові фронту біжать швидше за низькочастотний «хвіст», розмиваючи відбитий пік на далеких відстанях.
2. **Згасання у міді (Скін-ефект):** На частотах понад 1 ГГц глибина пронікнення струму у мідну доріжку стає меншою за 2 мікрометри. Високочастотні складові згасають пропорційно `√f`, що округлює гострі індуктивні та ємнісні піки.
3. **Множинні відбиття:** Якщо лінія містить кілька дефектів підряд, відбиття від першого дефекту повертається до другого, створюючи хибні «фантомні» піки. Для їх усунення в прецизійних аналізаторах застосовують алгоритми знімання шарів (Layer Peeling) або обчислення рефлектограми у частотній області через `S`-параметри.
