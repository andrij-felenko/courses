# ⚙️ Алгоритм розпізнавання втрат на оптичній рефлектограмі (OTDR Trace)

Оптична часова рефлектометрія (*Optical Time-Domain Reflectometry*, OTDR) є головним методологічним інструментом вимірювання, діагностики та локалізації несправностей у волоконно-оптичних лініях зв'язку. Метод базується на зондуванні волокна короткими світловими імпульсами високої інтенсивності та безперервній реєстрації часової залежності потужності зворотного випромінювання.

Сигнал, що повертається до приймача рефлектометра, формується двома фундаментальними фізичними процесами:
1. **Неперервне релеївське зворотне розсіяння (*Rayleigh Backscattering*)**: Виникає на флуктуаціях густини та показника заломлення кварцового скла, зафіксованих у структурі волокна під час його витягування. Частка потужності, розсіяна назад у напрямку джерела, описується формулою:
   ```text
   P_b(s) = 0.5 · P₀ · W · v_g · α_s · S · exp(−2 · α · s)
   ```
   де `P₀` — пікова потужність зондувального імпульсу, `W` — тривалість імпульсу, `v_g` — групова швидкість світла у склі, `α_s` — коефіцієнт релеївського розсіяння, `S` — частка розсіяного світла, яка захоплюється апертурою ядра у зворотному напрямку, а `α` — повний коефіцієнт загасання волокна.
2. **Дискретні френелівські відбиття (*Fresnel Reflections*)**: Виникають на скачкоподібних межах розподілу середовищ із різними показниками заломлення (на відкритих торцях, механічних стиках та роз'ємних конекторах), створюючи вузькі високоінтенсивні піки потужності.

---

### Фізичні обмеження: мертві зони та тривалість імпульсу

Під час проектування алгоритмів аналізу OTDR-траси необхідно враховувати концепцію **мертвих зон** (*Dead Zones*):
- **Мертва зона по події (*Event Dead Zone*, EDZ)**: Мінімальна відстань від початку відбивного піка (наприклад, конектора), на якій рефлектометр здатний виявити наступну подійну сходинку. Вона визначається тривалістю зондувального імпульсу `W` та смугою пропускання фотоприймача. Для імпульсу тривалістю 3 нс мертва зона за подією становить близько 0.8–1.0 метра.
- **Мертва зона за загасанням (*Attenuation Dead Zone*, ADZ)**: Відстань від початку відбивного піка до точки, де хвіст насичення фотодетектора (лавинного фотодіода APD) спадає до рівня `±0.5 дБ` від лінії релеївського розсіяння. Вона визначає мінімальну відстань, на якій можна достовірно виміряти втрати наступного зварного шва.
- **Фізика насичення APD-детектора**: Коли потужне френелівське відбиття від відкритого конектора вдаряє у фотодіод, лавинне помноження носіїв розгону переходить у режим насичення. Фотодіоду потрібен час для розсмоктування впроваджених носіїв заряду, через що крива траси експоненціально «повзе» вниз, маскуючи найближчі зварні шви.

Парадокс OTDR полягає у виборі тривалості імпульсу `W`:
- **Короткий імпульс (3–10 нс)**: Забезпечує високу просторову роздільну здатність (малі мертві зони EDZ < 1 м), але має малу енергетику, що обмежує динамічний діапазон і дальність вимірювання (до 5–10 км).
- **Довгий імпульс (1–10 мкс)**: Забезпечує колосальний динамічний діапазон (до 40–45 дБ), дозволяючи вимірювати магістралі завдовжки понад 100 км, але створює величезні мертві зони (ADZ > 100–500 м), усередині яких маскуються проміжні зварні шви.

---

### Математична логіка аналізу та квантифікації подій

Вхідними даними алгоритму є табульований масив дискретних відліків `(distance_m, power_dBm)`, отриманий після первинного цифрового фільтрування та усереднення (зазвичай 2¹⁶–2²⁰ імпульсів для зняття високочастотного шуму).

Аналітична обробка траси складається з п'яти послідовних етапів:

#### 1. Обчислення фонового загасання волокна (`α_fiber`)
На лінійних ділянках між подіями потужність падає пропорційно відстані. Алгоритм застосовує метод найменших квадратів (*Linear Least Squares Regression*, LSA) на ковзному вікні шириною 50–200 метрів для знаходження нахилу лінії:
```text
α_fiber = −(P(L₂) − P(L₁)) / (L₂ − L₁)     [дБ/км]
```
Для стандартного одномодового волокна на довжині хвилі 1550 нм нормальне значення нахилу становить `α_fiber ≈ 0.18...0.22 дБ/км`.

#### 2. Детектування та вимірювання невідбивних сходинок (зварних швів)
Зварний шов описується локальним зниженням рівня релеївського розсіяння без відбивного піка. Для обчислення втрат алгоритм екстраполює лінійні апроксимації фону до події (`P_before`) та після події (`P_after`):
```text
Loss_splice = P_before − P_after     [дБ]
```
Якщо `Loss_splice > 0`, записується стандартний зварний шов (*Fusion Splice*).

#### 3. Обробка аномалії «Гейнер» (Gainer / Negative Loss)
Якщо зварюються два волокна з різними коефіцієнтами зворотного розсіяння `S₁ < S₂` (наприклад, волокно з підвищеним вмістом Германію зварюється зі стандартним волокном), рівень сигнального розсіяння у другому волокні виявляється вищим, ніж у першому. На трасі виникає від'ємна сходинка втрат (`Loss_splice < 0`), яка виглядає як «підйом» сигнальної кривої вгору.

Фізичного підсилення світла на пасивному склі не відбувається. Це оптична ілюзія. Для знаходження істинних втрат `Loss_true` алгоритм вимагає обробки двох рефлектограм, знятих з протилежних кінців кабелю (напрям А → Б та напрям Б → А):
```text
Loss_true = (Loss_A_to_B + Loss_B_to_A) / 2
```
Якщо при вимірюванні А → Б отримано `Loss_A_to_B = −0.15 дБ` (гейнер), а при вимірюванні Б → А отримано `Loss_B_to_A = +0.21 дБ`, то істинні втрати шва становлять:
```text
Loss_true = (−0.15 + 0.21) / 2 = +0.03 дБ
```

#### 4. Ідентифікація фантомних відбивань (Ghost Peaks)
При наявності двох highly-reflective конекторів на короткій відстані `L_conn` світловий імпульс може багаторазово перевідбиватися між ними туди й назад. Це створює на рефлектограмі фальшиві відбивні піки — «фантоми» (*Ghosts*), розташовані на відстані `2 · L_conn`, `3 · L_conn` і так далі.
Алгоритм розпізнає фантоми за двома ознаками:
- Відстань до фантомного піка є кратною відстані між реальними відбивними конекторами;
- Після фантомного піка відсутня сходинка падіння фонового загасання (`P_before == P_after`).

#### 5. Виявлення макровигинів волокна (Macrobends)
Для відрізнення зварного шва з високими втратами від макровигину волокна (де кабель затиснутий або зігнутий радіусом `R < 30 мм`) алгоритм порівнює рефлектограми, зняті на двох довжинах хвиль (1310 нм та 1550 нм):
- Якщо втрати на події однакові на 1310 нм та 1550 нм — це геометричний дефект зварного шва.
- Якщо втрати на 1550 нм помітно вищі (на 0.5–2.0 дБ більші), ніж на 1310 нм — це макровигин волокна, оскільки випромінювання з довшою хвилею слабше утримується в ядрі й витікає при згині.

---

### Практична реалізація алгоритму аналізу траси

Нижче наведено ідіоматичні реалізації алгоритму аналізу OTDR-траси мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

// Типи оптичних подій на трасі
typedef enum {
    EVENT_NONE = 0,
    EVENT_SPLICE_FUSION,
    EVENT_CONNECTOR,
    EVENT_GAINER,
    EVENT_FIBER_END
} otdr_event_type_t;

// Структура опису знайденої події
typedef struct {
    double distance_m;
    otdr_event_type_t type;
    double loss_db;
    double return_loss_db;
} otdr_event_t;

// Вхідний масив відліків траси
typedef struct {
    const double *distances_m;
    const double *powers_dbm;
    size_t count;
    double pulse_width_ns;
} otdr_trace_t;

// Функція аналізу траси рефлектометра
size_t analyze_otdr_trace(const otdr_trace_t *trace,
                         otdr_event_t *out_events,
                         size_t max_events,
                         double noise_floor_dbm) {
    if (!trace || !out_events || trace->count < 5) {
        return 0;
    }

    size_t event_count = 0;
    double backscatter_slope = 0.0002; // ~0.2 дБ/км

    for (size_t i = 2; i < trace->count - 2; ++i) {
        double dist = trace->distances_m[i];
        double p_prev = trace->powers_dbm[i - 1];
        double p_curr = trace->powers_dbm[i];
        double p_next = trace->powers_dbm[i + 1];

        // Перевірка на кінець волокна (сигнал впав до рівня шумів)
        if (p_curr <= noise_floor_dbm && p_prev > noise_floor_dbm) {
            if (event_count < max_events) {
                out_events[event_count++] = (otdr_event_t){
                    .distance_m = dist,
                    .type = EVENT_FIBER_END,
                    .loss_db = p_prev - noise_floor_dbm,
                    .return_loss_db = 0.0
                };
            }
            break;
        }

        // Перевірка на відбивний пік (конектор)
        if (p_curr > p_prev + 0.5 && p_curr > p_next + 0.5) {
            double p_after = trace->powers_dbm[i + 3];
            double loss = p_prev - p_after;
            double rl = p_curr - p_prev + 10.0 * log10(trace->pulse_width_ns);

            if (event_count < max_events) {
                out_events[event_count++] = (otdr_event_t){
                    .distance_m = dist,
                    .type = EVENT_CONNECTOR,
                    .loss_db = loss,
                    .return_loss_db = rl
                };
            }
            i += 3; // Пропускаємо мертву зону відбиття
            continue;
        }

        // Перевірка на невідбивну сходинку (зварний шов або гейнер)
        double step = p_prev - p_next - (trace->distances_m[i + 1] - trace->distances_m[i - 1]) * backscatter_slope;
        if (fabs(step) >= 0.03) { // Поріг чутливості 0.03 дБ
            otdr_event_type_t ev_type = (step > 0) ? EVENT_SPLICE_FUSION : EVENT_GAINER;

            if (event_count < max_events) {
                out_events[event_count++] = (otdr_event_t){
                    .distance_m = dist,
                    .type = ev_type,
                    .loss_db = step,
                    .return_loss_db = 0.0
                };
            }
            i += 2;
        }
    }

    return event_count;
}

int main(void) {
    // Тестовий профіль траси: 3000 м, зварка на 1000 м, конектор на 2000 м
    double dists[] = {0, 500, 999, 1000, 1001, 1500, 1999, 2000, 2001, 2005, 2500, 3000};
    double powers[] = {0.0, -0.1, -0.2, -0.25, -0.25, -0.35, -0.45, +12.0, -0.85, -0.86, -0.96, -110.0};
    size_t count = sizeof(dists) / sizeof(dists[0]);

    otdr_trace_t trace = {
        .distances_m = dists,
        .powers_dbm = powers,
        .count = count,
        .pulse_width_ns = 50.0
    };

    otdr_event_t events[10];
    size_t found = analyze_otdr_trace(&trace, events, 10, -100.0);

    printf("Знайдено оптичних подій: %zu\n", found);
    for (size_t i = 0; i < found; ++i) {
        const char *tname = "Невідомо";
        switch (events[i].type) {
            case EVENT_SPLICE_FUSION: tname = "Зварний шов"; break;
            case EVENT_CONNECTOR:     tname = "Конектор"; break;
            case EVENT_GAINER:        tname = "Гейнер (підйом)"; break;
            case EVENT_FIBER_END:     tname = "Кінець волокна"; break;
            default: break;
        }
        printf("Подія на %.1f м: тип=%s, втрати=%.3f дБ, RL=%.1f дБ\n",
               events[i].distance_m, tname, events[i].loss_db, events[i].return_loss_db);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <string_view>
#include <expected>

enum class OtdrEventType {
    SpliceFusion,
    Connector,
    Gainer,
    FiberEnd
};

struct OtdrEvent {
    double distance_m;
    OtdrEventType type;
    double loss_db;
    double return_loss_db;
};

struct OtdrTraceView {
    std::span<const double> distances_m;
    std::span<const double> powers_dbm;
    double pulse_width_ns;
};

enum class OtdrAnalysisError {
    InvalidTraceData,
    TraceTooShort
};

class OtdrAnalyzer {
public:
    static std::expected<std::vector<OtdrEvent>, OtdrAnalysisError>
    analyze(const OtdrTraceView& trace, double noise_floor_dbm = -100.0) {
        if (trace.distances_m.size() != trace.powers_dbm.size()) {
            return std::unexpected(OtdrAnalysisError::InvalidTraceData);
        }
        if (trace.distances_m.size() < 5) {
            return std::unexpected(OtdrAnalysisError::TraceTooShort);
        }

        std::vector<OtdrEvent> events;
        constexpr double backscatter_slope = 0.0002;

        const size_t n = trace.distances_m.size();
        for (size_t i = 2; i < n - 2; ++i) {
            const double dist = trace.distances_m[i];
            const double p_prev = trace.powers_dbm[i - 1];
            const double p_curr = trace.powers_dbm[i];
            const double p_next = trace.powers_dbm[i + 1];

            if (p_curr <= noise_floor_dbm && p_prev > noise_floor_dbm) {
                events.push_back(OtdrEvent{
                    .distance_m = dist,
                    .type = OtdrEventType::FiberEnd,
                    .loss_db = p_prev - noise_floor_dbm,
                    .return_loss_db = 0.0
                });
                break;
            }

            if (p_curr > p_prev + 0.5 && p_curr > p_next + 0.5) {
                const double p_after = trace.powers_dbm[i + 3];
                const double loss = p_prev - p_after;
                const double rl = p_curr - p_prev + 10.0 * std::log10(trace.pulse_width_ns);

                events.push_back(OtdrEvent{
                    .distance_m = dist,
                    .type = OtdrEventType::Connector,
                    .loss_db = loss,
                    .return_loss_db = rl
                });
                i += 3;
                continue;
            }

            const double step = p_prev - p_next - (trace.distances_m[i + 1] - trace.distances_m[i - 1]) * backscatter_slope;
            if (std::abs(step) >= 0.03) {
                events.push_back(OtdrEvent{
                    .distance_m = dist,
                    .type = (step > 0) ? OtdrEventType::SpliceFusion : OtdrEventType::Gainer,
                    .loss_db = step,
                    .return_loss_db = 0.0
                });
                i += 2;
            }
        }

        return events;
    }

    static std::string_view event_type_to_string(OtdrEventType type) noexcept {
        switch (type) {
            case OtdrEventType::SpliceFusion: return "Зварний шов";
            case OtdrEventType::Connector:    return "Конектор";
            case OtdrEventType::Gainer:       return "Гейнер (підйом)";
            case OtdrEventType::FiberEnd:     return "Кінець волокна";
        }
        return "Невідомо";
    }
};

int main() {
    const std::vector<double> dists = {0, 500, 999, 1000, 1001, 1500, 1999, 2000, 2001, 2005, 2500, 3000};
    const std::vector<double> powers = {0.0, -0.1, -0.2, -0.25, -0.25, -0.35, -0.45, +12.0, -0.85, -0.86, -0.96, -110.0};

    OtdrTraceView trace{
        .distances_m = dists,
        .powers_dbm = powers,
        .pulse_width_ns = 50.0
    };

    auto result = OtdrAnalyzer::analyze(trace);
    if (!result) {
        std::cerr << "Помилка аналізу OTDR-траси!\n";
        return 1;
    }

    std::cout << "Знайдено оптичних подій: " << result->size() << "\n";
    for (const auto& ev : *result) {
        std::cout << "Подія на " << ev.distance_m << " м: "
                  << "тип=" << OtdrAnalyzer::event_type_to_string(ev.type)
                  << ", втрати=" << ev.loss_db << " дБ"
                  << ", RL=" << ev.return_loss_db << " дБ\n";
    }

    return 0;
}
```
:::
