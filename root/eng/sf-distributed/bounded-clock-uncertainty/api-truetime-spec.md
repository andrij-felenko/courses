# 📋 Специфікація TrueTime API та інтерфейсу апаратного джерела часу

Ця специфікація визначає програмний контракт низькорівневої бібліотеки TrueTime, інтерфейс взаємодії з апаратними джерелами часу (драйвер синхронізації) та регламент поведінки розподіленої системи зберігання при виникненні аномалій шкали часу.

Абстракція TrueTime призначена для надання транзакційним розподіленим системам (таким як Google Spanner, CockroachDB, YugabyteDB) строго монотонного фізичного часу з детермінованою похибкою. Бібліотека абстрагує складність взаємодії з супутниковими навігаційними приймачами (GNSS/GPS), атомними рубідієвими або цезієвими стандартами частоти та мережевими протоколами точного часу (PTP IEEE 1588).

## 1. Базові типи даних та структури

Всі часові мітки в інтерфейсі виражаються як 64-бітні знакові цілі числа (`int64_t`), що представляють кількість наносекунд від початку епохи Unix (1970-01-01 00:00:00 UTC). Секунди координації (англ. *leap seconds*) згладжуються на рівні операційної системи та драйвера (технологія *leap smearing*), тому шкала часу є неперервною та монотонною.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Часовий інтервал TrueTime в наносекундах */
typedef struct {
    int64_t earliest_ns; /* Нижня межа довірчого інтервалу (t_local - ε) */
    int64_t latest_ns;   /* Верхня межа довірчого інтервалу (t_local + ε) */
} tt_interval_ns_t;

/* Статус джерела синхронізації */
typedef enum {
    TT_SOURCE_GPS_LOCKED      = 0, /* GNSS активний, сигнал PPS стабільний (ε < 10 мкс) */
    TT_SOURCE_PTP_LOCKED      = 1, /* Апаратний PTP IEEE 1588 активний (ε < 50 мкс) */
    TT_SOURCE_ATOMIC_HOLDOVER = 2, /* Робота від рубідієвого генератора без GPS (ε повільно росте) */
    TT_SOURCE_NTP_FALLBACK    = 3, /* Аварійний режим NTP (ε від 1 до 50 мс) */
    TT_SOURCE_UNSYNCHRONIZED  = 4  /* Критичний збій: перевищено ліміт безпеки MAX_UNCERTAINTY */
} tt_source_status_t;

/* Структура діагностики стану годинника */
typedef struct {
    tt_source_status_t status;
    int64_t current_uncertainty_ns;     /* Поточне значення ε в наносекундах */
    int64_t max_allowed_uncertainty_ns; /* Поріг аварійної паніки */
    int64_t time_since_last_sync_ns;    /* Час від останнього сеансу корекції */
    int32_t active_satellites;          /* Кількість відстежуваних супутників */
    double estimated_drift_ppm;         /* Оцінена швидкість локального дрейфу */
} tt_diagnostics_t;
```
```cpp
#include <cstdint>
#include <chrono>
#include <string_view>

namespace truetime {

using Nanoseconds = std::chrono::nanoseconds;
using Microseconds = std::chrono::microseconds;

/* Часовий інтервал TrueTime на базі стандартних типів chrono */
struct Interval {
    Nanoseconds earliest{0};
    Nanoseconds latest{0};

    [[nodiscard]] constexpr Nanoseconds width() const noexcept {
        return latest - earliest;
    }

    [[nodiscard]] constexpr Nanoseconds uncertainty() const noexcept {
        return width() / 2;
    }

    [[nodiscard]] constexpr bool contains(Nanoseconds t) const noexcept {
        return earliest <= t && t <= latest;
    }
};

enum class SourceStatus : std::uint8_t {
    GpsLocked = 0,
    PtpLocked = 1,
    AtomicHoldover = 2,
    NtpFallback = 3,
    Unsynchronized = 4
};

struct Diagnostics {
    SourceStatus status{SourceStatus::Unsynchronized};
    Nanoseconds current_uncertainty{0};
    Nanoseconds max_allowed_uncertainty{0};
    Nanoseconds time_since_last_sync{0};
    std::int32_t active_satellites{0};
    double estimated_drift_ppm{0.0};
};

} // namespace truetime
```
:::

## 2. Публічний клієнтський інтерфейс (TrueTime Core API)

Клієнтський інтерфейс розроблено для мінімізації накладних витрат у критичному шляху обробки розподілених запитів. Отримання поточного часу оптимізовано через механізм відображення пам'яті спільного простору ядра (vDSO) або атомарні змінні користувацького простору, що дозволяє виконувати виклик `tt_now()` безпосередньо за 10–30 наносекунд без перемикання контексту ядра ОС.

:::tabs
```c
/* Опитує підсистему часу та повертає поточний інтервал [earliest, latest] */
tt_interval_ns_t tt_now(void);

/* Перевіряє, чи момент часу target_time_ns гарантовано минув */
bool tt_after(int64_t target_time_ns);

/* Перевіряє, чи момент часу target_time_ns гарантовано знаходиться в майбутньому */
bool tt_before(int64_t target_time_ns);

/* Блокує потік виконання, доки не настане умова tt_after(commit_ts_ns) == true */
void tt_commit_wait(int64_t commit_ts_ns);

/* Отримує поточний діагностичний стан підсистеми */
int tt_get_diagnostics(tt_diagnostics_t *out_diag);
```
```cpp
namespace truetime {

class ITimeService {
public:
    virtual ~ITimeService() = default;

    /* Повертає поточний довірчий інтервал часу */
    [[nodiscard]] virtual Interval now() const = 0;

    /* Перевірка настання моменту в минулому */
    [[nodiscard]] virtual bool after(Nanoseconds target_time) const = 0;

    /* Перевірка знаходження моменту в майбутньому */
    [[nodiscard]] virtual bool before(Nanoseconds target_time) const = 0;

    /* Бар'єр Commit Wait */
    virtual void commit_wait(Nanoseconds commit_timestamp) const = 0;

    /* Отримання повної діагностики підсистеми */
    [[nodiscard]] virtual Diagnostics get_diagnostics() const = 0;
};

} // namespace truetime
```
:::

### Детальна специфікація функцій ядра

#### 1. `tt_now`
- **Опис:** Зчитує монотонний апаратний лічильник процесора (наприклад, TSC на x86_64 або Generic Timer на ARM64), додає калібрований базовий зсув до шкали UTC та розраховує поточну похибку `ε(t) = ε₀ + ρ·Δt`.
- **Гарантія безпеки:** Істинний астрономічний час виклику `t_real` строго відповідає нерівності `earliest_ns ≤ t_real ≤ latest_ns`.
- **Гарантія монотонності:** Межі інтервалу є монотонно неспадною функцією. Якщо запит `A` завершився до початку запиту `B` на тому самому вузлі, то `latest(B) ≥ latest(A)` та `earliest(B) ≥ earliest(A)`.

#### 2. `tt_after`
- **Опис:** Обчислює предикат `tt_now().earliest_ns > target_time_ns`.
- **Семантика:** Якщо функція повернула `true`, жоден процес у кластері не зможе в майбутньому отримати або призначити мітку, меншу або рівну `target_time_ns`. Це дозволяє безпечно публікувати результати транзакції клієнтам.

#### 3. `tt_before`
- **Опис:** Обчислює предикат `tt_now().latest_ns < target_time_ns`.
- **Семантика:** Використовується для планування відкладених транзакцій та перевірки дійсності тимчасових орендованих блокувань (англ. *leader leases*).

#### 4. `tt_commit_wait`
- **Опис:** Розраховує залишок часу до настання умови лінеаризовності: `Δt_wait = commit_ts_ns − tt_now().earliest_ns`.
- **Алгоритм очікування:** 
  - Якщо `Δt_wait > 200 мкс`, потік блокується за допомогою системного виклику `nanosleep` або `futex` на величину `Δt_wait − 100 мкс`.
  - Останні 100 мікросекунд потік виконує активне очікування (англ. *busy-spin*) з опитуванням лічильника через інструкцію паузи процесора (`_mm_pause()`), що запобігає непередбачуваним затримкам планувальника ядра ОС при пробудженні.

## 3. Оптимізація vDSO та структура спільної пам'яті ядра

Для виключення накладних витрат на системні виклики ядро ОС або спеціалізований фоновий демон TrueTime підтримує в оперативній пам'яті сторінку стану, доступну для читання всім процесам у режимі користувача (англ. *user-space lock-free read*).

Сторінка містить наступні поля, оновлювані через подвійний лічильник послідовності (англ. *seqlock*):
- `base_realtime_ns`: базове значення еталонного часу UTC під час останнього калібрування.
- `base_tsc_cycles`: значення апаратного лічильника тактів процесора на момент калібрування.
- `tsc_to_ns_mult` та `tsc_to_ns_shift`: коефіцієнти фіксованої коми для перетворення тактів процесора в наносекунди без використання операцій ділення з плаваючою комою.
- `current_eps_base_ns`: базова похибка еталону.
- `drift_rate_scaled`: масштабований коефіцієнт дрейфу кварцу.

Коли прикладний потік викликає `tt_now()`, він зчитує лічильник тактів процесора за допомогою апаратної інструкції `RDTSC` (або `RDTSCP` з бар'єром серіалізації конвеєра), обчислює минулий час `Δtsc` та розраховує поточні межі інтервалу за менш ніж 40 тактів CPU.

## 4. Інтерфейс драйвера джерела часу (Hardware Driver SPI)

Драйвер синхронізації є проміжним шаром між апаратними контролерами точного часу та користувацьким простором СУБД. Він відповідає за періодичне опитування зовнішніх еталонів, фільтрацію викидів (фільтр Калмана) та динамічну зміну частоти ходу ядра (англ. *clock slewing*).

:::tabs
```c
/* Інтерфейс плагіна апаратного джерела */
typedef struct {
    const char *driver_name;
    
    /* Ініціалізація апаратного пристрою (відкриття дескрипторів /dev/ptpX або /dev/ppsX) */
    int (*init)(void);
    
    /* Отримання поточного зсуву та похибки від зовнішнього еталону */
    int (*poll_sample)(int64_t *utc_time_ns, int64_t *reference_error_ns);
    
    /* Плавне коригування частоти локального генератора (ppb, parts-per-billion) */
    int (*adjust_frequency_ppb)(double offset_ppb);
    
    /* Звільнення ресурсів при зупинці демона */
    void (*shutdown)(void);
} tt_hardware_driver_t;
```
```cpp
#include <memory>
#include <expected>
#include <string_view>

namespace truetime {

struct TimeSample {
    Nanoseconds utc_time{0};
    Nanoseconds reference_error{0};
};

enum class DriverError : std::uint8_t {
    DeviceNotAvailable,
    SignalLost,
    InvalidMeasurement,
    HardwareFault
};

class IHardwareDriver {
public:
    virtual ~IHardwareDriver() = default;

    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
    virtual std::expected<void, DriverError> initialize() = 0;
    [[nodiscard]] virtual std::expected<TimeSample, DriverError> poll_sample() = 0;
    virtual std::expected<void, DriverError> adjust_frequency(double offset_ppb) = 0;
    virtual void shutdown() noexcept = 0;
};

} // namespace truetime
```
:::

## 5. Контракт інтеграції з транзакційним рушієм СУБД

Розподілений транзакційний рушій повинен дотримуватися наступних строгих правил при роботі з TrueTime API:

### 1. Правило призначення мітки коміту (Commit Timestamp Rule)
Координатор транзакції запису `T` під час двофазного коміту викликає `tt_now()` і вибирає мітку фіксації `s`:
```
s = max(tt_now().latest_ns, last_allocated_timestamp + 1)
```
Це гарантує строгу монотонність міток всередині одного вузла та дотримання умови `s ≥ t_real`.

### 2. Правило безпечного читання (Safe Read Rule)
Транзакція читання знімка стану за міткою `t_read` може виконуватися на довільній репліці без координації та блокувань за умови:
```
t_read < tt_now().earliest_ns
```
Якщо на даній репліці `tt_now().earliest_ns ≤ t_read`, запит читання повинен зачекати на локальному вузлі, доки годинник не просунеться вперед, або звернутися до репліки з більш актуальним станом.

### 3. Очищення застарілих версій (MVCC Garbage Collection)
Під час фонового очищення застарілих версій рядків рушій бази даних обчислює безпечний поріг видалення (англ. *GC Watermark*):
```
t_gc = tt_now().earliest_ns − retention_period_ns
```
Всі версії даних із мітками `s < t_gc`, які були перекриті новішими записами, можуть бути фізично видалені з диска, оскільки система гарантує, що жодна транзакція читання не зможе звернутися до знімка, старішого за `retention_period_ns`.

## 6. Обробка збоїв і аварійні інваріанти (Panic Conditions)

Підсистема TrueTime спроектована за принципом «безпека понад доступність» (англ. *Safety over Liveness*). Порушення часових інваріантів може призвести до незворотного спотворення даних у базі даних, тому у нештатних ситуаціях система застосовує наступні захисні бар'єри:

1. **Критичне перевищення похибки (`ε > MAX_UNCERTAINTY`):**
   - За замовчуванням константа `MAX_UNCERTAINTY` встановлюється рівною 100 мілісекундам.
   - Якщо через тривалу ізоляцію мережі та дрейф кварцу значення `ε` перевищує цей поріг, виклик `tt_now()` повертає статус `TT_SOURCE_UNSYNCHRONIZED`.
   - Демон ініціює аварійне завершення процесу СУБД (Server Panic / Fail-Fast). Вузол негайно припиняє обробку запитів і виключається з кворуму консенсусу до відновлення зв'язку з еталонами точного часу.

2. **Захист від немонотонних стрибків часу:**
   - Будь-яке ступінчасте переведення системного годинника операційної системи (наприклад, через виклик `settimeofday` або скидання вручну системним адміністратором) суворо заборонено.
   - Підсистема TrueTime відстежує показання апаратного лічильника інструкцій процесора. Якщо виявлено стрибок часу назад або вперед, що перевищує `ε`, драйвер фіксує фатальну помилку цілісності та зупиняє роботу сервера.

3. **Стійкість до збоїв супутникових систем (GNSS Jamming / Spoofing):**
   - Драйвер щосекунди зіставляє дані супутникових приймачів із автономними рубідієвими стандартами частоти.
   - Якщо покази GPS відхиляються від передбаченої траєкторії атомного генератора більш ніж на допустиму статистичну дисперсію, GPS-джерело негайно маркується як скомпрометоване, і система переходить у режим атомного утримання (Atomic Holdover Mode).
