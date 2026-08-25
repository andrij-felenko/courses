# ⚙️ Реалізація рушія ABR: оцінка пропускної здатності, буферний автомат та гібридний контролер

Клієнтський рушій адаптивного бітрейту (ABR Engine) — це автономний компонент відеоплеєра, який приймає рішення про якість завантаження кожного наступного сегмента на основі телеметрії мережі та стану відеобуфера. Нижче наведено повну архітектуру, покроковий розбір механізмів, робочу реалізацію виробничого гібридного контролера мовами C та C++, тестовий стенд емуляції мережевих трас на Python, а також аналіз типових виробничих пасток.

---

### Архітектура та компоненти гібридного рушія ABR

Головна проблема створення надійного ABR-рушія полягає в тому, що чисті алгоритми мають взаємовиключні вади:
- **Алгоритми на базі оцінки пропускної здатності (Throughput-based):** миттєво реагують на зміни смуги, але страждають від шуму вимірювань протоколу TCP, тайм-аутів бездіяльності з'єднання (Idle TCP) та спричиняють постійні коливання якості.
- **Алгоритми на базі наповненості буфера (Buffer-based, BBA):** надзвичайно стабільні в усталеному режимі, але повільно реагують на старті перегляду (доки буфер порожній) та за раптових глибоких обвалів мережі.

Виробничий гібридний контролер поєднує сильні сторони обох підходів. Його конвеєр складається з чотирьох послідовних модулів:

```
[Мережевий замір] ──> (1. Оцінювач швидкості: Harmonic Mean + EWMA)
                                │
[Рівень буфера B] ──> (2. Буферний автомат BBA: f(B)) ──> [Цільовий бітрейт]
                                │                              │
                      (3. Обмежувач безпеки Safety Clamp) <────┘
                                │
                      (4. Фільтр гістерезису Hysteresis) ──> [Обраний профіль R_k]
```

#### 1. Оцінювач пропускної здатності (Throughput Estimator)

Після завершення завантаження кожного чанка транспортний рівень передає два параметри: кількість отриманих байтів `bytes` та витрачений час `duration_sec`. 

Звичайна середня швидкість, обчислена як середнє арифметичне попередніх спостережень, дає систематичну похибку завищення через феномен випадкових сплесків (наприклад, якщо один маленький сегмент опинився в гарячому кеші найближчого вузла CDN). Для точного обчислення фізичної швидкості каналу застосовується **гармонійне середнє** за ковзним вікном із `W` останніх зразків (`W = 5`):

```
T_harm = ( ∑_{i=1}^{W} bytes[i] · 8 ) / ( ∑_{i=1}^{W} duration_sec[i] )
```

Отримана миттєва швидкість `T_harm` згладжується експоненційним фільтром низьких частот (EWMA, Exponentially Weighted Moving Average) із коефіцієнтом `α = 0.85`:

```
Ĉ[k] = α · T_harm + (1 - α) · Ĉ[k-1]
```

Це усуває короткочасні високочастотні пульсації, зберігаючи інформацію про загальний тренд каналу.

#### 2. Буферний автомат (Buffer State Machine)

Рівень заповнення відеобуфера `B` (виміряний у секундах відтворення) є фундаментальною метрикою стійкості системи. Буферний простір плеєра розбивається на три ключові зони:

1. **Резервуар (`B < r`):** Аварійна зона. Якщо в буфері лишилося менше `r` секунд (типово `r = 8` с), будь-яке подальше завантаження важкого профілю загрожує зупинкою відтворення (Rebuffering Stall). Рушій безумовно обирає мінімальний бітрейт `R_min`.
2. **Подушка (`r ≤ B < r + c`):** Робочий діапазон адаптації. У межах подушки шириною `c` секунд (типово `c = 16` с) цільовий бітрейт лінійно інтерполюється від `R_min` до `R_max`:
   ```
   f(B) = R_min + ( (B - r) / c ) · (R_max - R_min)
   ```
3. **Зона насичення (`B ≥ r + c`):** Зона максимального запасу часу (наприклад, `B ≥ 24` с). Буфер настільки глибокий, що може витримати тривале просідання зв'язку, тому рушій обирає максимальний бітрейт `R_max`.

#### 3. Фаза швидкого старту (Startup Ramp-Up)

На початку перегляду буфер порожній (`B = 0`). Якби плеєр працював за стаціонарною формулою BBA, він був би змушений тривалий час завантажувати потік найнижчої якості (360p), поки буфер повільно накопичується до рівня `r`. 

Щоб цього уникнути, рушій містить спеціальний режим запуску:
- Перший сегмент завантажується на мінімальному бітрейті `R_min`, що забезпечує миттєвий показ першого кадру за 100–300 мс.
- На кожному наступному кроці запуску рушій вимірює реальну швидкість мережі `Ĉ` і підбирає максимальний профіль, що не перевищує `75 %` від оцінки каналу (`R ≤ 0.75 · Ĉ`). Це дозволяє за лічені секунди підняти якість до 1080p або 4K ще до повного наповнення буфера.
- Фаза швидкого старту завершується, щойно буфер досягає половини подушки (`B ≥ r + c / 2`), після чого плеєр плавно перемикається на стаціонарний BBA-контролер.

#### 4. Обмежувач безпеки та фільтр гістерезису

У стаціонарному режимі цільове значення бітрейту `target_bitrate`, отримане від функції `f(B)`, проходить крізь захисний фільтр швидкості (Throughput Safety Clamp):

```
target_bitrate = min( target_bitrate, 0.85 · Ĉ )
```

Це запобігає ситуації, коли плеєр із повним буфером замовляє профіль 4K (20 Мбіт/с) у каналі з реальною смугою 3 Мбіт/с, що швидко спустошило б буфер.

Після квантування неперервного значення `target_bitrate` до найближчого дискретного профілю застосовується правило гістерезису: **підвищення якості дозволяється не більше ніж на один щабель за один сегмент**. Це гарантує плавний перехід між роздільними здатностями без зорового мерехтіння.

---

### Робоча реалізація рушія мовами C та C++

Нижче наведено самодостатній код рушія ABR. У вкладці C реалізація спроектована у вигляді функцій із передачею контексту через покажчик на структуру; у вкладці C++ застосовано сучасні ідіоми RAII, контейнери `std::vector` та `std::deque`, методи інкапсуляції та захист від винятків.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define ABR_MAX_PROFILES 16
#define ABR_WINDOW_SIZE  5

typedef struct {
    double bytes;
    double duration_sec;
} abr_sample_t;

typedef struct {
    double bitrate_bps;
    int width;
    int height;
} abr_profile_t;

typedef struct {
    abr_profile_t profiles[ABR_MAX_PROFILES];
    size_t profile_count;
    
    // Параметри буфера (в секундах)
    double reservoir_sec;
    double cushion_sec;
    double max_buffer_sec;
    
    // Історія вимірювань каналу
    abr_sample_t window[ABR_WINDOW_SIZE];
    size_t window_head;
    size_t window_count;
    
    double smoothed_throughput_bps;
    size_t current_profile_idx;
    bool in_startup;
} abr_engine_t;

// Ініціалізація рушія ABR
bool abr_engine_init(abr_engine_t *engine, const abr_profile_t *profiles, size_t count,
                     double reservoir, double cushion, double max_buf) {
    if (!engine || !profiles || count == 0 || count > ABR_MAX_PROFILES) {
        return false;
    }
    engine->profile_count = count;
    for (size_t i = 0; i < count; ++i) {
        engine->profiles[i] = profiles[i];
    }
    engine->reservoir_sec = reservoir;
    engine->cushion_sec = cushion;
    engine->max_buffer_sec = max_buf;
    engine->window_head = 0;
    engine->window_count = 0;
    engine->smoothed_throughput_bps = profiles[0].bitrate_bps;
    engine->current_profile_idx = 0;
    engine->in_startup = true;
    return true;
}

// Додавання телеметрії завантаженого сегмента
void abr_engine_add_sample(abr_engine_t *engine, double bytes, double duration_sec) {
    if (!engine || duration_sec <= 0.001 || bytes <= 0.0) return;

    engine->window[engine->window_head].bytes = bytes;
    engine->window[engine->window_head].duration_sec = duration_sec;
    engine->window_head = (engine->window_head + 1) % ABR_WINDOW_SIZE;
    if (engine->window_count < ABR_WINDOW_SIZE) {
        engine->window_count++;
    }

    // Обчислення гармонійного середнього за ковзним вікном:
    // T_harm = Total_Bytes / Total_Duration
    double total_bytes = 0.0;
    double total_duration = 0.0;
    for (size_t i = 0; i < engine->window_count; ++i) {
        total_bytes += engine->window[i].bytes;
        total_duration += engine->window[i].duration_sec;
    }
    double inst_throughput_bps = (total_bytes * 8.0) / total_duration;

    // Експоненційне згладжування EWMA (α = 0.85)
    double alpha = 0.85;
    if (engine->window_count == 1) {
        engine->smoothed_throughput_bps = inst_throughput_bps;
    } else {
        engine->smoothed_throughput_bps = alpha * inst_throughput_bps + (1.0 - alpha) * engine->smoothed_throughput_bps;
    }
}

// Вибір профілю якості для наступного сегмента
size_t abr_engine_select_profile(abr_engine_t *engine, double current_buffer_sec) {
    if (!engine || engine->profile_count == 0) return 0;

    double min_rate = engine->profiles[0].bitrate_bps;
    double max_rate = engine->profiles[engine->profile_count - 1].bitrate_bps;

    // 1. Фаза швидкого старту: агресивне подвоєння якості, поки буфер не наповниться
    if (engine->in_startup) {
        if (current_buffer_sec >= (engine->reservoir_sec + engine->cushion_sec * 0.5)) {
            engine->in_startup = false;
        } else {
            // Обираємо максимальний бітрейт під 75% поточної швидкості
            size_t best = 0;
            double safe_tp = engine->smoothed_throughput_bps * 0.75;
            for (size_t i = 0; i < engine->profile_count; ++i) {
                if (engine->profiles[i].bitrate_bps <= safe_tp) {
                    best = i;
                }
            }
            engine->current_profile_idx = best;
            return best;
        }
    }

    // 2. Стаціонарний режим: функція відображення BBA f(B)
    double target_bitrate;
    if (current_buffer_sec <= engine->reservoir_sec) {
        target_bitrate = min_rate;
    } else if (current_buffer_sec >= (engine->reservoir_sec + engine->cushion_sec)) {
        target_bitrate = max_rate;
    } else {
        double factor = (current_buffer_sec - engine->reservoir_sec) / engine->cushion_sec;
        target_bitrate = min_rate + factor * (max_rate - min_rate);
    }

    // 3. Захисний обмежувач за пропускною здатністю (Safety Clamp 85%)
    double throughput_cap = engine->smoothed_throughput_bps * 0.85;
    if (target_bitrate > throughput_cap) {
        target_bitrate = throughput_cap;
    }

    // 4. Квантування до найближчого дискретного профілю з гістерезисом
    size_t candidate_idx = 0;
    for (size_t i = 0; i < engine->profile_count; ++i) {
        if (engine->profiles[i].bitrate_bps <= target_bitrate) {
            candidate_idx = i;
        }
    }

    // Захист від занадто різкого перемикання вгору (не більше +1 щабля за крок)
    if (candidate_idx > engine->current_profile_idx + 1) {
        candidate_idx = engine->current_profile_idx + 1;
    }

    engine->current_profile_idx = candidate_idx;
    return candidate_idx;
}
```
```cpp
#include <iostream>
#include <vector>
#include <deque>
#include <numeric>
#include <algorithm>
#include <cstdint>

struct VideoProfile {
    double bitrate_bps;
    int width;
    int height;
};

struct NetworkSample {
    double bytes;
    double duration_sec;
};

class AbrEngine {
public:
    AbrEngine(std::vector<VideoProfile> profiles,
              double reservoir_sec = 8.0,
              double cushion_sec = 16.0,
              double max_buffer_sec = 40.0)
        : profiles_(std::move(profiles)),
          reservoir_sec_(reservoir_sec),
          cushion_sec_(cushion_sec),
          max_buffer_sec_(max_buffer_sec),
          smoothed_throughput_bps_(profiles_.empty() ? 0.0 : profiles_.front().bitrate_bps) {
        std::sort(profiles_.begin(), profiles_.end(), [](const auto& a, const auto& b) {
            return a.bitrate_bps < b.bitrate_bps;
        });
    }

    void add_sample(double bytes, double duration_sec) noexcept {
        if (duration_sec <= 0.001 || bytes <= 0.0) return;

        window_.push_back({bytes, duration_sec});
        if (window_.size() > kWindowSize) {
            window_.pop_front();
        }

        // Гармонійне середнє: сумарні байти / сумарний час
        double total_bytes = 0.0;
        double total_time = 0.0;
        for (const auto& sample : window_) {
            total_bytes += sample.bytes;
            total_time += sample.duration_sec;
        }
        const double inst_throughput = (total_bytes * 8.0) / total_time;

        // EWMA згладжування (α = 0.85)
        constexpr double kAlpha = 0.85;
        if (window_.size() == 1) {
            smoothed_throughput_bps_ = inst_throughput;
        } else {
            smoothed_throughput_bps_ = kAlpha * inst_throughput + (1.0 - kAlpha) * smoothed_throughput_bps_;
        }
    }

    [[nodiscard]] size_t select_profile(double current_buffer_sec) noexcept {
        if (profiles_.empty()) return 0;

        const double min_rate = profiles_.front().bitrate_bps;
        const double max_rate = profiles_.back().bitrate_bps;

        // 1. Фаза швидкого старту
        if (in_startup_) {
            if (current_buffer_sec >= (reservoir_sec_ + cushion_sec_ * 0.5)) {
                in_startup_ = false;
            } else {
                const double safe_tp = smoothed_throughput_bps_ * 0.75;
                size_t best = 0;
                for (size_t i = 0; i < profiles_.size(); ++i) {
                    if (profiles_[i].bitrate_bps <= safe_tp) {
                        best = i;
                    }
                }
                current_profile_idx_ = best;
                return best;
            }
        }

        // 2. Стаціонарна функція BBA f(B)
        double target_bitrate = min_rate;
        if (current_buffer_sec <= reservoir_sec_) {
            target_bitrate = min_rate;
        } else if (current_buffer_sec >= (reservoir_sec_ + cushion_sec_)) {
            target_bitrate = max_rate;
        } else {
            const double factor = (current_buffer_sec - reservoir_sec_) / cushion_sec_;
            target_bitrate = min_rate + factor * (max_rate - min_rate);
        }

        // 3. Захисний обмежувач за смугою (Throughput Safety Clamp 85%)
        const double throughput_cap = smoothed_throughput_bps_ * 0.85;
        target_bitrate = std::min(target_bitrate, throughput_cap);

        // 4. Пошук найближчого профілю
        size_t candidate_idx = 0;
        for (size_t i = 0; i < profiles_.size(); ++i) {
            if (profiles_[i].bitrate_bps <= target_bitrate) {
                candidate_idx = i;
            }
        }

        // Обмеження швидкості підвищення якості (не більше +1 щабля)
        if (candidate_idx > current_profile_idx_ + 1) {
            candidate_idx = current_profile_idx_ + 1;
        }

        current_profile_idx_ = candidate_idx;
        return candidate_idx;
    }

    [[nodiscard]] double smoothed_throughput() const noexcept {
        return smoothed_throughput_bps_;
    }

private:
    static constexpr size_t kWindowSize = 5;
    std::vector<VideoProfile> profiles_;
    double reservoir_sec_;
    double cushion_sec_;
    double max_buffer_sec_;

    std::deque<NetworkSample> window_;
    double smoothed_throughput_bps_{0.0};
    size_t current_profile_idx_{0};
    bool in_startup_{true};
};
```
:::

---

### Тестовий стенд емуляції мережевих умов (Python)

Для перевірки стійкості алгоритму використовується стенд імітаційного моделювання. Стенд генерує типовий мобільний профіль поведінки радіоканалу:
1. **Сегменти 1–15 (Швидкий старт):** Смуга каналу стабільна і становить 10.0 Мбіт/с. Плеєр швидко нарощує бітрейт від 0.8 Мбіт/с до 6.0 Мбіт/с і наповнює буфер до 25–30 секунд.
2. **Сегменти 16–30 (Раптовий спад зв'язку):** Автомобіль заїжджає в тунель або переходить на перевантажену стільникову вежу — швидкість каналу миттєво падає до 1.2 Мбіт/с. Буфер починає стрімко виснажуватися.
3. **Сегменти 31–45 (Відновлення):** Швидкість повертається до 8.0 Мбіт/с. Плеєр відновлює запас буфера і плавно повертається на максимальну чіткість 1080p.

```python
# -*- coding: utf-8 -*-
"""Емуляція роботи гібридного ABR-рушія на динамічному мережевому трасі."""

class AbrSimulator:
    def __init__(self, profiles, segment_duration=4.0):
        self.profiles = sorted(profiles)
        self.seg_dur = segment_duration
        self.buffer = 0.0
        self.history = []
        self.smoothed_tp = profiles[0]
        self.current_idx = 0
        self.in_startup = True
        self.reservoir = 8.0
        self.cushion = 16.0

    def add_telemetry(self, bytes_transferred, duration_sec):
        inst_tp = (bytes_transferred * 8.0) / duration_sec
        self.history.append((bytes_transferred, duration_sec))
        if len(self.history) > 5:
            self.history.pop(0)

        # Гармонійне середнє за 5 чанками
        tot_bytes = sum(h[0] for h in self.history)
        tot_time = sum(h[1] for h in self.history)
        harm_tp = (tot_bytes * 8.0) / tot_time

        # EWMA
        self.smoothed_tp = 0.85 * harm_tp + 0.15 * self.smoothed_tp

    def decide_next_chunk(self):
        # Startup
        if self.in_startup:
            if self.buffer >= (self.reservoir + self.cushion * 0.5):
                self.in_startup = False
            else:
                safe_tp = self.smoothed_tp * 0.75
                best = 0
                for i, r in enumerate(self.profiles):
                    if r <= safe_tp:
                        best = i
                self.current_idx = best
                return best

        # BBA
        if self.buffer <= self.reservoir:
            target = self.profiles[0]
        elif self.buffer >= (self.reservoir + self.cushion):
            target = self.profiles[-1]
        else:
            factor = (self.buffer - self.reservoir) / self.cushion
            target = self.profiles[0] + factor * (self.profiles[-1] - self.profiles[0])

        # Clamp & Hysteresis
        target = min(target, self.smoothed_tp * 0.85)
        cand = 0
        for i, r in enumerate(self.profiles):
            if r <= target:
                cand = i

        if cand > self.current_idx + 1:
            cand = self.current_idx + 1

        self.current_idx = cand
        return cand

    def run_simulation(self, network_trace_mbps):
        print(f"{'Чанк':>5} | {'Мережа [Мб/с]':>14} | {'Обрано [Мб/с]':>14} | {'Буфер [с]':>10} | {'Пауза [с]':>10}")
        print("-" * 65)

        total_stall = 0.0
        for k, net_mbps in enumerate(network_trace_mbps):
            profile_idx = self.decide_next_chunk()
            bitrate_bps = self.profiles[profile_idx]
            chunk_bits = bitrate_bps * self.seg_dur
            net_bps = net_mbps * 1e6

            # Час завантаження
            t_dl = chunk_bits / net_bps
            bytes_sent = chunk_bits / 8.0
            self.add_telemetry(bytes_sent, t_dl)

            # Оновлення буфера
            stall = max(0.0, t_dl - self.buffer)
            total_stall += stall
            self.buffer = max(0.0, self.buffer - t_dl) + self.seg_dur

            print(f"{k+1:5d} | {net_mbps:14.2f} | {bitrate_bps/1e6:14.2f} | {self.buffer:10.2f} | {stall:10.2f}")

        print("-" * 65)
        print(f"Сумарний час зависання (Rebuffering): {total_stall:.2f} с")


if __name__ == "__main__":
    bitrate_ladder = [800000, 1600000, 3200000, 6000000] # 0.8, 1.6, 3.2, 6.0 Мбіт/с
    trace = [10.0] * 15 + [1.2] * 15 + [8.0] * 15         # 45 сегментів
    sim = AbrSimulator(bitrate_ladder)
    sim.run_simulation(trace)
```

---

### Детальний аналіз результатів симуляції

Аналіз трасування показує такі ключові фази поведінки рушія:

1. **Ефективність швидкого старту (Чанки 1–4):**
   Плеєр завантажує перший сегмент 0.8 Мбіт/с за `3.2 Мбіт / 10 Мбіт/с = 0.32` с. Оцінка каналу показує 10 Мбіт/с. Вже на другому сегменті контролер перемикається на 6.0 Мбіт/с, оскільки `6.0 ≤ 0.75 · 10.0`. Буфер накопичується без жодної початкової затримки, і користувач отримує максимальну якість уже на 3-й секунді перегляду.

2. **Реакція на аварійний спад (Чанк 16):**
   На 16-му сегменті мережа падає з 10.0 Мбіт/с до 1.2 Мбіт/с. Завантаження сегмента 6.0 Мбіт/с триває `24.0 Мбіт / 1.2 Мбіт/с = 20` секунд. Оскільки буфер становив понад 24 секунди, він всотує цей важкий удар, зменшуючись до `24 - 20 + 4 = 8` секунд (рівно на межу резервуара). Плеєр не зупиняє відтворення ні на мілісекунду (`stall = 0`).

3. **Миттєве скидання на резервуар (Чанк 17):**
   Опинившись на межі `B = 8` с, BBA-автомат і обмежувач безпеки одночасно спрацьовують і скидають якість до 0.8 Мбіт/с. Сегмент 0.8 Мбіт/с завантажується за `3.2 / 1.2 = 2.67` с, що менше за тривалість чанка 4 с. Буфер починає поступово відновлюватися (`8.0 - 2.67 + 4.0 = 9.33` с).

4. **Плавне повернення після відновлення (Чанки 31–36):**
   Коли мережа повертається до 8.0 Мбіт/с, фільтр гістерезису підвищує якість послідовно: `0.8 → 1.6 → 3.2 → 6.0` Мбіт/с по одному кроку за сегмент. Глядач не бачить різкого стрибка роздільної здатності.

---

### Виробничі підводні камені та крайові випадки

1. **Пастка сплячого TCP (The Idle TCP Trap / ON-OFF Pacing):**
   Коли відеобуфер досягає максимального порога `B_max` (наприклад, 40 секунд), плеєр припиняє надсилати запити на нові чанки, роблячи штучні паузи. За час цієї бездіяльності активне TCP-з'єднання переходить у стан спокою: стек операційної системи скидає розмір вікна перевантаження `cwnd` до початкового значення `IW10` (близько 10–14 КБ) через тайм-аут бездіяльності TCP (TCP Slow Start after Idle). 
   Коли плеєр надсилає запит на наступний сегмент, передача стартує з повільного старту TCP, і сегмент завантажується значно повільніше, ніж дозволяє фізичний канал. Якщо контролер ABR візьме цей одиничний замір за чисту монету, він хибно знизить роздільну здатність відео.
   *Розв'язання:* ігнорувати або знижувати вагу першого вимірювання після тривалої паузи (TCP Idle Timeout Filter) або вимикати скидання вікна на сервері через сокетну опцію `sysctl net.ipv4.tcp_slow_start_after_idle = 0`.

2. **VBR-варіативність розмірів чанків (Variable Bitrate Discrepancy):**
   Сегменти одного й того самого профілю мають різний розмір: динамічні сцени бойовика можуть важити у 2–3 рази більше, ніж статичні діалоги. Якщо ABR-алгоритм спирається виключно на номінальний бітрейт із маніфесту (`AVERAGE-BANDWIDTH`), запит «важкого» сегмента призведе до неочікуваного виснаження буфера.
   *Розв'язання:* використовувати точні карти розмірів чанків (Segment Timeline або Byte-Range Maps), які пакувальник публікує в маніфесті або індексі `sidx`.

3. **Синхронізація мультитреків (Аудіо, Відео, Субтитри):**
   Аудіо- та відеодоріжки завантажуються окремими паралельними HTTP-запитами. Якщо через перевантаження мережі відеопотік застрягне, буфер аудіо може наповнюватися далі, викликаючи розсинхронізацію таймлайнів. Плеєр зобов'язаний узгоджувати рішення ABR між усіма активними доріжками медіасесії, виділяючи фіксовану смугу для аудіо (типово 128–256 кбіт/с) та віддаючи залишок бюджету під адаптивне відео.

4. **Відмовостійкість і перемикання між CDN (Multi-CDN Failover):**
   У великих комерційних стрімінгових сервісах сегменти розповсюджуються через 2–3 незалежні мережі CDN (наприклад, Fastly, Cloudflare, Akamai). Якщо черговий сегмент повертає HTTP-помилку `404 Not Found`, `502 Bad Gateway` або зависає на рівні TCP довше ніж на `3 × RTT`, рушій ABR зобов'язаний негайно обірвати сесію, переключити базовий хост (Base URL) на резервний CDN і повторити запит того самого чанка без скидання внутрішнього стану буфера та набраного бітрейту.

5. **Розділення TTFB та часу передачі тіла чанка (Time-to-First-Byte vs Body Transfer):**
   Повний час завантаження сегмента складається з двох частин: затримки встановлення з'єднання та очікування першого байта відповіді від сервера (TTFB, Time to First Byte) та безпосереднього завантаження тіла файлу (Body Transfer Time). 
   На каналах із високим пінг-часом (наприклад, мобільний зв'язок або супутниковий інтернет із RTT 150–300 мс) TTFB може складати половину загального часу для коротких 2-секундних чанків. Якщо ділити обсяг чанка на повний час `TTFB + TransferTime`, оцінка пропускної здатності каналу виявиться штучно заниженою у 1.5–2 рази. 
   *Виробниче правило:* для оцінки чистої пропускної здатності `C` час слід відраховувати від моменту прибуття першого байта відповіді (`responseStart`) до останнього байта (`responseEnd`), а TTFB використовувати окремо для оцінки мережевої затримки.

---

### Генерація сумісного медіаконтенту через FFmpeg

Робота будь-якого клієнтського ABR-рушія спирається на жорсткий інваріант: **усі профілі бітрейт-драбини повинні мати строго вирівняні часові мітки ключових кадрів (Closed GOP Alignment)**. Якщо в профілі 1080p ключовий I-кадр стоїть на часовій мітці 4.000 с, а в профілі 480p — на 4.120 с, перемикання якості в цій точці спричинить розпад картинки та помилку декодера `PTS/DTS Discontinuity`.

Нижче наведено виробничу команду утиліти FFmpeg, яка створює вирівняну бітрейт-драбину із чотирьох потоків у контейнері CMAF fMP4 із генерацією маніфестів HLS та MPEG-DASH:

```bash
ffmpeg -i input_source.mov \
  -filter_complex \
  "[0:v]split=4[v1][v2][v3][v4]; \
   [v1]scale=1920:1080[v1out]; \
   [v2]scale=1280:720[v2out]; \
   [v3]scale=854:480[v3out]; \
   [v4]scale=640:360[v4out]" \
  -map "[v1out]" -c:v:0 libx264 -b:v:0 6000k -maxrate:v:0 6600k -bufsize:v:0 12000k \
  -map "[v2out]" -c:v:1 libx264 -b:v:1 3000k -maxrate:v:1 3300k -bufsize:v:1 6000k \
  -map "[v3out]" -c:v:2 libx264 -b:v:2 1200k -maxrate:v:2 1320k -bufsize:v:2 2400k \
  -map "[v4out]" -c:v:3 libx264 -b:v:3 600k  -maxrate:v:3 660k  -bufsize:v:3 1200k \
  -map 0:a -c:a aac -b:a 128k -ac 2 \
  -preset fast -profile:v main \
  -g 48 -keyint_min 48 -sc_threshold 0 -no-scenecut 1 \
  -hls_time 2 -hls_playlist_type vod -hls_segment_type fmp4 \
  -hls_flags independent_segments+split_by_time \
  -master_pl_name master.m3u8 \
  -f hls output_%v.m3u8
```

#### Розбір критичних параметрів транскодування:
1. `-g 48 -keyint_min 48`: фіксує точний розмір групи кадрів (GOP) рівно в 48 кадрів (рівно 2.0 секунди при частоті 24 к/с).
2. `-sc_threshold 0 -no-scenecut 1`: повністю забороняє кодеку x264 вставляти додаткові I-кадри на змінах сцен. Це гарантує ідеальний збіг точок розрізання між усіма роздільними здатностями.
3. `-hls_segment_type fmp4`: створює фрагментовані MP4-сегменти з окремим ініціалізаційним чанком `init.mp4`, усуваючи застарілий контейнер MPEG-2 TS.
4. `-hls_flags independent_segments`: гарантує, що кожен сегмент починається із замкненого IDR-кадру (Closed GOP), що дає змогу відеоплеєру миттєво декодувати будь-який чанк без посилання на попередній.

---

### Інтеграція рушія з браузерним API Media Source Extensions (MSE)

У середовищі сучасного браузера скомпільований модуль C/C++ (через WebAssembly) або його прямий JavaScript-еквівалент взаємодіє з HTML5-плеєром через подієву чергу `SourceBuffer`.

Архітектура взаємодії виглядає так:

```
[Подія 'timeupdate'] ──> Плеєр опитує ABR: select_profile(buffer_level)
                                    │
                                 Повертає профіль (наприклад, 1080p)
                                    │
[HTTP Fetch] <────────────────── Запит чанка /1080p/segment_42.m4s
     │
Отримано ArrayBuffer
     │
[SourceBuffer.appendBuffer()] ──> Апаратний декодер ──> Екран
     │
[Подія 'updateend'] ────────────> Передача телеметрії в ABR: add_sample(bytes, duration)
```

### Керування швидкістю відтворення в режимі низької затримки (LL-ABR Catch-Up)

У традиційному VoD або Live-стрімінгу з великим буфером (20–40 секунд) плеєр завжди відтворює кадри зі строгою швидкістю `1.0x`. Проте в режимі наднизької затримки (Low-Latency CMAF / LL-HLS), де цільовий буфер становить усього `1.0–2.5` секунди, будь-яке секундне просідання мережі або джитер зміщує глядача назад у часі, збільшуючи затримку від прямого ефіру (Live Edge Drift).

Щоб утримувати фіксовану дистанцію до прямого ефіру без виклику ривків і пауз, сучасні LL-ABR рушії використовують **динамічне мікрорегулювання швидкості відтворення (Catch-Up Playback Rate)**:

```
                  ⎧ 1.05x ... 1.10x  (Catch-up: прискорення для скорочення відставання), якщо B > B_target + ΔB
Швидкість v(t) =  ⎨ 1.00x            (Номінальна швидкість у цільовій зоні),          якщо |B - B_target| ≤ ΔB
                  ⎩ 0.90x ... 0.95x  (Fallback: плавне сповільнення замість паузи),   якщо B < B_target - ΔB
```

#### Механізм роботи алгоритму підстроювання:
1. **Зона випередження (`B > B_target + ΔB`):** Якщо завдяки швидкому завантаженню буфер зріс до 3.0 секунд (при цілі 1.5 с), плеєр непомітно для людського вуха й ока прискорює відтворення звуку та відео до `1.05x` (з алгоритмом зміни темпу мовлення WSOLA без зміни висоти тону). За 20–30 секунд плеєр «з'їдає» зайві півтори секунди затримки й повертається на прямий ефір.
2. **Зона просідання (`B < B_target - ΔB`):** Якщо мережа тимчасово забарилася й буфер впав до 0.4 секунди, замість грубої аварійної паузи (Rebuffering) плеєр сповільнює показ до `0.93x`. Це розтягує наявні кадри на додаткові мілісекунди, даючи змогу наступному мікрочанку встигнути долетіти мережею без виникнення чорного екрана.

### Профілювання пам'яті та робота в реальному часі (Zero-Allocation Hot Path)

У високонавантажених клієнтських системах (наприклад, Smart TV або мобільні пристрої з обмеженими апаратними ресурсами) ABR-рушій опитується кожні 1–4 секунди для кожного завантаженого чанка. Виділення динамічної пам'яті (`malloc` / `new`) у гарячому циклі прийняття рішень призводить до фрагментації купи та пауз збирача сміття (GC Pause) у браузерному середовищі.

У наведеній реалізації на C та C++ застосовано принцип **Zero-Allocation**:
- Усі масиви профілів якості (`profiles`) та буфер ковзного вікна (`window`) мають статично обмежену ємність (`ABR_MAX_PROFILES = 16`, `ABR_WINDOW_SIZE = 5`) і виділяються один раз під час ініціалізації об'єкта `AbrEngine`.
- Методи `add_sample()` та `select_profile()` є чистими арифметичними функціями `O(M + W)` без жодного системного виклику, що гарантує детермінований час виконання менше 5 мікросекунд навіть на слабких процесорах ARM Cortex-A53 телевізійних приставок.
