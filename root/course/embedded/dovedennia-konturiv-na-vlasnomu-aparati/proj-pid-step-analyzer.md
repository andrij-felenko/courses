# ⚙️ Аналізатор перехідної характеристики та діагностика перетюну

Налаштування контурів стабілізації без точних числових метрик перетворюється на небезпечне вгадування: пілот бачить легке тремтіння променів або відчуває «ватність» у стіках, але не може визначити, чи перерегулювання становить допустимі 8%, чи аварійні 35%, і чи спричинений нагрів моторів високочастотним шумом D-терма, чи механічним дисбалансом. Цей інструмент створено для автоматизованого обчислення динамічних характеристик перехідного процесу за даними бортового логу: він виділяє окремі сходинки керування, обчислює час запізнення, час наростання, амплітуду перерегулювання та середньоквадратичний шум диференційного каналу, формуючи чіткі рекомендації для коригування коефіцієнтів.

## Метрики перехідного процесу в бортовому лозі

Коли автопілот або пілот подає різку зміну кутової швидкості (сходинку `SetPoint`), реакція системи описується класичною перехідною характеристикою замкненого контуру. Для об'єктивної оцінки контуру аналізатор обчислює п'ять базових параметрів:

1. **Транспортне запізнення** (`tau_us`): часовий інтервал від миті стрибка завдання до моменту, коли кутова швидкість гіроскопа досягає 5% від повної амплітуди сходинки. Ця величина відображає сумарну фазову затримку каскаду цифрових фільтрів, обчислювальний лаг таймерів мікроконтролера та час реакції силового ключа ESC й індуктивності обмоток мотора. Якщо запізнення перевищує 20–25 мс, замкнений контур втрачає запас стійкості за фазою і стає схильним до самозбудження при будь-якому збільшенні підсилення.
2. **Час наростання** (`rise_time_ms`): інтервал між досягненням 10% та 90% цільового значення кутової швидкості. Цей показник безпосередньо характеризує жорсткість та пропорційне підсилення контуру (`P`-gain). Що коротший час наростання, то швидше апарат підхоплює команду, проте надмірно малий час наростання (< 20 мс) вимагає екстремальних струмів і загрожує зривом синхронізації безколекторного мотора (десинхронізація ESC).
3. **Перерегулювання** (`overshoot_pct`): відсоткове перевищення амплітуди першого екстремуму над встановленим цільовим рівнем:
```
overshoot_pct = ((peak_value − target_value) / target_value) · 100%
```
Перерегулювання в межах 3–8% вважається оптимальним компромісом між швидкістю та стійкістю; перевищення 15–20% свідчить про гострий брак демпфування (`D`-gain) або надмірний коефіцієнт `P`.
4. **Час встановлення** (`settling_time_ms`): проміжок часу від початку маневру, після якого виміряна кутова швидкість остаточно входить у допустимий коридор стабілізації ±5% від цільового значення і більше не виходить за його межі.
5. **Високочастотний шум D-терма** (`d_noise_rms`): середньоквадратичне відхилення високочастотної складової сигналу D-терма на квазістаціонарній ділянці (плато сходинки), яке сигналізує про паразитичне високочастотне розсіювання енергії в міді статора:
```
d_noise_rms = √ ( (1/N) · Σ (d_out[i] − d_filtered[i])² )
```

## Алгоритм автоматичного детектування сходинки

У реальному польотному лозі сходинки керування не ізольовані: пілот безперервно маневрує, сигнал стіка містить тремтіння рук (RC noise), а на вихід гіроскопа накладається аеродинамічна турбулентність. Щоб надійно виокремити придатний для аналізу відрізок, аналізатор реалізує триетапну фільтрацію подій:

- **Детектор фронту за швидкістю наростання завдання:** фронт вважається сходинкою, якщо похідна сигналу завдання `|d(SetPoint)/dt|` перевищує поріг 600 deg/s², а сумарна зміна завдання `ΔSetPoint` становить не менше 40 deg/s протягом інтервалу не більше 30 мс. Повільні рухи стіка відкидаються, оскільки вони не збуджують власні резонанси системи й не дають інформації про перехідну характеристику.
- **Перевірка стабільності передісторії:** протягом 80 мс до початку сходинки кутова швидкість апарата має бути спокійною (відхилення `|SetPoint − Gyro| < 15 deg/s`), що гарантує відсутність перехідних процесів від попереднього маневру. Якщо апарат усе ще коливався після попереднього фліпу, поточний маневр не аналізується, щоб уникнути накладання коливань.
- **Перевірка утримання плато:** після завершення фронту завдання має залишатися незмінним протягом щонайменше 150 мс. Якщо пілот смикнув стік назад раніше, сходинка відкидається як неповна.

Крім того, алгоритм контролює валідність вимірювань: якщо в момент маневру зафіксовано кліпінг давача гіроскопа (виліт за межі діапазону ±2000 deg/s) або просідання напруги батареї нижче критичного порогу відсічки, така сходинка позначається як спотворена зовнішніми факторами.

## Оцінка високочастотного шуму та нагріву

Головна небезпека диференційного коефіцієнта полягає в тому, що D-терм може виглядати стабільним на графіку загального кута, але водночас генерувати приховану високочастотну потужність. Для кількісної оцінки цього ефекту аналізатор розраховує середньоквадратичну дисперсію скінченних різниць `d_term[i] - d_term[i-1]` на ділянці усталеного руху.

Якщо `d_noise_rms` перевищує поріг 35–40 одиниць за шкалою мікшера, це свідчить про те, що гармоніки обертання пропелерів пробиваються крізь цифровий фільтр низьких частот і потрапляють на вхід ESC. У такому стані мотори працюють як нагрівальні елементи, що вимагає негайного зниження коефіцієнта `K_d` або увімкнення динамічного режекторного фільтра (Dynamic RPM Notch Filter).

## Програмна реалізація аналізатора (C та C++)

Нижче наведено повний модуль потокового аналізу сходинок. Модуль приймає масиви часових відліків польотного логу, виявляє границі перехідного процесу, обчислює динамічні параметри та видає структурований діагностичний вердикт із конкретними вказівками щодо підстроювання коефіцієнтів.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_SAMPLES 1024

typedef struct {
    double setpoint;          // Амплітуда виявленої сходинки, deg/s
    double latency_ms;        // Час запізнення реакції (вихід на 5%), мс
    double rise_time_ms;      // Час наростання від 10% до 90%, мс
    double overshoot_pct;     // Величина перерегулювання, %
    double settling_time_ms;  // Час заспокоєння до коридору 5%, мс
    double d_noise_rms;       // Середньоквадратичний шум D-терма на плато
    int    oscillation_count; // Кількість перетинів коридору (дзвін)
    bool   is_valid_step;     // Ознака валідної та придатної до аналізу сходинки
} StepMetrics;

typedef enum {
    TUNE_PERFECT = 0,
    TUNE_P_TOO_LOW,
    TUNE_P_TOO_HIGH,
    TUNE_D_TOO_LOW,
    TUNE_D_TOO_HIGH_NOISE,
    TUNE_SYSTEM_LAGGY
} TuneDiagnostic;

// Перевірка спокою системи перед початком сходинки
static bool verify_pre_step_quiescence(const double *target, const double *actual, int start_idx) {
    if (start_idx < 10) return true;
    for (int i = start_idx - 10; i < start_idx; ++i) {
        if (fabs(target[i] - actual[i]) > 25.0) {
            return false;
        }
    }
    return true;
}

// Аналіз масиву відліків сходинки перехідного процесу
static StepMetrics analyze_step_response(const uint64_t *time_us,
                                        const double *target,
                                        const double *actual,
                                        const double *d_term,
                                        int n) {
    StepMetrics m = {0};
    if (n < 25 || n > MAX_SAMPLES) return m;

    double t0 = target[0];
    double t_final = target[n - 1];
    double step_amp = t_final - t0;

    // Сходинка має бути чіткою та енергійною (> 35 deg/s)
    if (fabs(step_amp) < 35.0) return m;
    if (!verify_pre_step_quiescence(target, actual, 5)) return m;

    m.setpoint = step_amp;
    m.is_valid_step = true;

    uint64_t t_start = time_us[0];
    uint64_t t_5pct = 0, t_10pct = 0, t_90pct = 0;
    double max_val = actual[0];
    int peak_idx = 0;

    double target_5  = t0 + 0.05 * step_amp;
    double target_10 = t0 + 0.10 * step_amp;
    double target_90 = t0 + 0.90 * step_amp;
    double band_low  = t_final - 0.05 * fabs(step_amp);
    double band_high = t_final + 0.05 * fabs(step_amp);

    for (int i = 1; i < n; ++i) {
        double val = actual[i];

        // Фіксація часу запізнення реакції (вихід на 5%)
        if (!t_5pct && ((step_amp > 0 && val >= target_5) || (step_amp < 0 && val <= target_5))) {
            t_5pct = time_us[i];
        }
        // Фіксація часових позначок наростання (10% та 90%)
        if (!t_10pct && ((step_amp > 0 && val >= target_10) || (step_amp < 0 && val <= target_10))) {
            t_10pct = time_us[i];
        }
        if (!t_90pct && ((step_amp > 0 && val >= target_90) || (step_amp < 0 && val <= target_90))) {
            t_90pct = time_us[i];
        }

        // Пошук абсолютного піка для визначення перерегулювання
        if (step_amp > 0) {
            if (val > max_val) { max_val = val; peak_idx = i; }
        } else {
            if (val < max_val) { max_val = val; peak_idx = i; }
        }
    }

    if (t_5pct > t_start) {
        m.latency_ms = (double)(t_5pct - t_start) / 1000.0;
    }
    if (t_90pct > t_10pct && t_10pct > 0) {
        m.rise_time_ms = (double)(t_90pct - t_10pct) / 1000.0;
    }

    // Обчислення відсотка перерегулювання
    if (step_amp > 0 && max_val > t_final) {
        m.overshoot_pct = ((max_val - t_final) / step_amp) * 100.0;
    } else if (step_amp < 0 && max_val < t_final) {
        m.overshoot_pct = ((t_final - max_val) / fabs(step_amp)) * 100.0;
    } else {
        m.overshoot_pct = 0.0;
    }

    // Час встановлення та підрахунок перетинів межі коридору 5%
    uint64_t t_settle = 0;
    int crossings = 0;
    for (int i = peak_idx; i < n; ++i) {
        if (actual[i] < band_low || actual[i] > band_high) {
            t_settle = time_us[i];
            crossings++;
        }
    }
    m.settling_time_ms = (t_settle > t_start) ? (double)(t_settle - t_start) / 1000.0 : m.rise_time_ms;
    m.oscillation_count = crossings;

    // Оцінка високочастотного шуму D-терма на плато сходинки
    double sum_sq = 0.0;
    int noise_samples = 0;
    int start_noise = n / 2;
    for (int i = start_noise + 1; i < n; ++i) {
        double delta = d_term[i] - d_term[i - 1];
        sum_sq += delta * delta;
        noise_samples++;
    }
    m.d_noise_rms = (noise_samples > 0) ? sqrt(sum_sq / noise_samples) : 0.0;

    return m;
}

// Генерація діагностичного висновку за виміряними метриками
static TuneDiagnostic evaluate_tuning(const StepMetrics *m) {
    if (!m->is_valid_step) return TUNE_PERFECT;

    if (m->latency_ms > 24.0) {
        return TUNE_SYSTEM_LAGGY; // Завеликий лаг фільтрів або слабка тяга
    }
    if (m->d_noise_rms > 35.0) {
        return TUNE_D_TOO_HIGH_NOISE; // Небезпека високочастотного перегріву моторів
    }
    if (m->overshoot_pct > 20.0 && m->rise_time_ms < 32.0) {
        return (m->oscillation_count > 4) ? TUNE_P_TOO_HIGH : TUNE_D_TOO_LOW;
    }
    if (m->rise_time_ms > 90.0 && m->overshoot_pct < 2.0) {
        return TUNE_P_TOO_LOW; // Млява реакція, брак пропорційного підсилення
    }
    return TUNE_PERFECT;
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <vector>
#include <span>
#include <optional>
#include <string_view>

struct StepMetrics {
    double setpoint{0.0};
    double latency_ms{0.0};
    double rise_time_ms{0.0};
    double overshoot_pct{0.0};
    double settling_time_ms{0.0};
    double d_noise_rms{0.0};
    int    oscillation_count{0};
};

enum class TuneDiagnostic {
    Perfect,
    PLow,
    PHigh,
    DLow,
    DHighNoise,
    SystemLaggy
};

class StepResponseAnalyzer {
public:
    static std::optional<StepMetrics> analyze(std::span<const uint64_t> time_us,
                                              std::span<const double> target,
                                              std::span<const double> actual,
                                              std::span<const double> d_term) {
        const size_t n = time_us.size();
        if (n < 25 || target.size() != n || actual.size() != n || d_term.size() != n) {
            return std::nullopt;
        }

        const double t0 = target.front();
        const double t_final = target.back();
        const double step_amp = t_final - t0;

        if (std::abs(step_amp) < 35.0) {
            return std::nullopt; // Амплітуда сходинки недостатня для достовірної оцінки
        }

        // Перевірка спокою до початку сходинки
        for (size_t i = 0; i < 5 && i < n; ++i) {
            if (std::abs(target[i] - actual[i]) > 25.0) {
                return std::nullopt;
            }
        }

        StepMetrics m;
        m.setpoint = step_amp;

        const uint64_t t_start = time_us.front();
        uint64_t t_5pct = 0, t_10pct = 0, t_90pct = 0;
        double max_val = actual.front();
        size_t peak_idx = 0;

        const double target_5  = t0 + 0.05 * step_amp;
        const double target_10 = t0 + 0.10 * step_amp;
        const double target_90 = t0 + 0.90 * step_amp;
        const double band_low  = t_final - 0.05 * std::abs(step_amp);
        const double band_high = t_final + 0.05 * std::abs(step_amp);

        for (size_t i = 1; i < n; ++i) {
            const double val = actual[i];

            if (!t_5pct && ((step_amp > 0 && val >= target_5) || (step_amp < 0 && val <= target_5))) {
                t_5pct = time_us[i];
            }
            if (!t_10pct && ((step_amp > 0 && val >= target_10) || (step_amp < 0 && val <= target_10))) {
                t_10pct = time_us[i];
            }
            if (!t_90pct && ((step_amp > 0 && val >= target_90) || (step_amp < 0 && val <= target_90))) {
                t_90pct = time_us[i];
            }

            if (step_amp > 0) {
                if (val > max_val) { max_val = val; peak_idx = i; }
            } else {
                if (val < max_val) { max_val = val; peak_idx = i; }
            }
        }

        if (t_5pct > t_start) m.latency_ms = static_cast<double>(t_5pct - t_start) / 1000.0;
        if (t_90pct > t_10pct && t_10pct > 0) m.rise_time_ms = static_cast<double>(t_90pct - t_10pct) / 1000.0;

        if (step_amp > 0 && max_val > t_final) {
            m.overshoot_pct = ((max_val - t_final) / step_amp) * 100.0;
        } else if (step_amp < 0 && max_val < t_final) {
            m.overshoot_pct = ((t_final - max_val) / std::abs(step_amp)) * 100.0;
        }

        uint64_t t_settle = 0;
        int crossings = 0;
        for (size_t i = peak_idx; i < n; ++i) {
            if (actual[i] < band_low || actual[i] > band_high) {
                t_settle = time_us[i];
                crossings++;
            }
        }
        m.settling_time_ms = (t_settle > t_start) ? static_cast<double>(t_settle - t_start) / 1000.0 : m.rise_time_ms;
        m.oscillation_count = crossings;

        // Розрахунок високочастотного шуму D-терма на плато
        double sum_sq = 0.0;
        size_t noise_samples = 0;
        const size_t start_noise = n / 2;
        for (size_t i = start_noise + 1; i < n; ++i) {
            const double delta = d_term[i] - d_term[i - 1];
            sum_sq += delta * delta;
            noise_samples++;
        }
        m.d_noise_rms = (noise_samples > 0) ? std::sqrt(sum_sq / static_cast<double>(noise_samples)) : 0.0;

        return m;
    }

    static TuneDiagnostic evaluate(const StepMetrics &m) {
        if (m.latency_ms > 24.0) return TuneDiagnostic::SystemLaggy;
        if (m.d_noise_rms > 35.0) return TuneDiagnostic::DHighNoise;
        if (m.overshoot_pct > 20.0 && m.rise_time_ms < 32.0) {
            return (m.oscillation_count > 4) ? TuneDiagnostic::PHigh : TuneDiagnostic::DLow;
        }
        if (m.rise_time_ms > 90.0 && m.overshoot_pct < 2.0) {
            return TuneDiagnostic::PLow;
        }
        return TuneDiagnostic::Perfect;
    }

    static std::string_view recommendation(TuneDiagnostic diag) {
        switch (diag) {
            case TuneDiagnostic::Perfect:
                return "Контур ідеально збалансовано: мінімальний лаг, перерегулювання в межах 5-10%, чистий D-терм.";
            case TuneDiagnostic::PLow:
                return "Збільшити P на 15-20%: контур занадто повільно виходить на сходинку, бракує жорсткості.";
            case TuneDiagnostic::PHigh:
                return "Зменшити P на 15%: зафіксовано затяжні низькочастотні коливання (дзвін) навколо цільового значення.";
            case TuneDiagnostic::DLow:
                return "Збільшити D на 10-15%: наростання швидке, але спостерігається надмірний одиничний відскок (overshoot).";
            case TuneDiagnostic::DHighNoise:
                return "Зменшити D на 20% або активувати Dynamic Notch: критичний рівень ВЧ шуму, загроза перегріву моторів.";
            case TuneDiagnostic::SystemLaggy:
                return "Перевірити фільтри або демпфери IMU: затримка > 24 мс свідчить про надмірний фазовий лаг у системі.";
        }
        return "";
    }
};
```
:::

## Інтерпретація діагностичних метрик

Під час аналізу перехідних характеристик тестового польоту інженер спирається на наведені нижче контрольні пороги, відкалібровані для типових квадрокоптерів класу 5–10 дюймів із живленням 4S–6S:

| Метрика | Норма (Healthy) | Замале підсилення (Undertuned) | Надмірне підсилення (Overtuned) |
|---|---|---|---|
| Затримка `tau_us` | 8–16 мс | > 24 мс (мляві мотори або надмірна фільтрація) | — |
| Час наростання `t_rise` | 30–60 мс | > 90 мс (нестача `P`, ватне керування) | < 20 мс (ризик самозбудження при просіданні АКБ) |
| Перерегулювання `M_p` | 3–10% | 0% (передемпфована, повільна реакція) | > 22% (дзвін, propwash, зрив траєкторії) |
| Шум `d_noise_rms` | < 15.0 | — | > 35.0 (паразитне нагрівання обмоток статора) |

Якщо час запізнення `tau_us` стабільно перевищує 24 мс, подальше нарощування коефіцієнтів `P` та `D` є контрпродуктивним: будь-яка спроба зробити контур жорсткішим викличе нестійкість через втрату фазового запасу. У такій ситуації насамперед оптимізують смугу низькочастотних фільтрів гіроскопа або переходять на швидший протокол ESC (наприклад, DShot600 замість класичного PWM або OneShot).
