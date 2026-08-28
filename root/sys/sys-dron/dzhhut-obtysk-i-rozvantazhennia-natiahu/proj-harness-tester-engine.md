# ⚙️ Автоматизований тестер цілісності кабельного джгута та виявлення переплутаних пінів

Бортовий кабельний джгут безпілотного апарата об'єднує десятки сигнальних провідників шин I2C, SPI, UART, CAN та силових ліній живлення в єдину просторову мережу. Помилка ручного монтажу — переплутані піни передачі (TX) та прийому (RX), закорочення лінії живлення `+5 В` на сигнальний провід датчика або прихований мікрообрив усередині обтискного контакту (кримпу), який проявляється лише під час вібрації двигунів — виводить з ладу польотний контролер або спричиняє раптову відмову авіоніки в повітрі. Автоматизований тестер джгутів реалізує матричне сканування провідності за алгоритмом почергового збудження вузлів із синхронним зчитуванням відгуку всіх ліній. Це дозволяє за частки мікросекунди визначити повний топологічний граф з'єднань, виявити закорочення, обриви, перехресні з'єднання та плаваючі контакти в режимі вібраційного струшування.

---

### Математична модель матричного сканування топології джгута

Кабельний джгут із `N` контактними точками описується орієнтованим графом електричної провідності, де кожна контактна гільза або роз'єм є вершиною графу `V = {v₁, v₂, ..., v_N}`, а провідники між ними — ребрами. Повний стан комутації джгута задається квадратною бінарною матрицею суміжності (матрицею провідності) `A` розмірністю `N × N`:

```
A[i][j] = 1, якщо опір між контактом i та контактом j менший за поріг R_th (R_ij < R_th)
A[i][j] = 0, якщо опір між контактом i та контактом j перевищує поріг ізоляції R_iso
```

Для пасивного кабельного джгута без активних напівпровідникових елементів (наприклад, захисних діодів) матриця провідності є симетричною (`A[i][j] = A[j][i]`) та має рефлексивну діагональ (`A[i][i] = 1`, оскільки контакт завжди замкнений сам на себе).

Процес верифікації складається з чотирьох послідовних математичних фаз:

1. **Фаза поодинокого збудження (Single-Pin Drive & Multi-Pin Sense).**
   - Усі тестові лінії `1...N` конфігуруються у високоімпедансний стан із підтяжкою до землі через резистори `R_pd = 100 кОм` (High-Z Pull-Down).
   - Тестер вибирає одну активну лінію `i` (Drive Line), перемикає її вихідний каскад у режим генератора напруги (Push-Pull Output High, `V_test = 3.3 В`) і прикладає тестовий потенціал.
   - Одночасно виконується паралельне опитування логічних рівнів на всіх лініях `j ∈ {1...N}` (Sense Lines). Якщо провідник між точкою `i` та точкою `j` існує і цілий, напруга на вході `j` підніметься до високого рівня `V_test`, формуючи біт `A[i][j] = 1`.
   - Процедура повторюється циклічно для кожного `i` від `1` до `N`, формуючи виміряну матрицю провідності `A_meas`.

2. **Порозрядне бітмаскове порівняння з проєктним нетлістом (Netlist Golden Comparison).**
   - Виміряна матриця `A_meas` порівнюється з еталонною матрицею проєктної схеми `A_ref` за допомогою порозрядної операції XOR (виключного АБО):

```
Error_Matrix = A_meas ⊕ A_ref
```

Якщо `Error_Matrix` містить хоча б одну одиницю, джгут бракується, а позиція одиничного біта вказує точні координати дефектного провідника.

3. **Топологічна класифікація дефектів.**
   - **Обрив (Open Circuit):** `A_ref[i][j] = 1`, але `A_meas[i][j] = 0`. Лінія між контактами `i` та `j` розірвана, не обтиснута або контакт вискочив із замка роз'єму під час стикування.
   - **Коротке замикання (Short Circuit):** `A_ref[i][j] = 0`, але `A_meas[i][j] = 1`. Провідники двох незалежних електричних кіл замкнені між собою (наприклад, через злипання припою на виводах роз'єму, затискання джгута металевим гвинтом рами чи пробиття ізоляції об гостру карбонову кромку).
   - **Переплутані піни (Miswired Pin / Cross-Over):** Контакт `i` з'єднаний із хибним контактом `k` замість цільового `j`. При цьому спостерігається парна комбінація обриву в правильній ланці (`A_meas[i][j] = 0`) та замикання в хибній (`A_meas[i][k] = 1`).

4. **Алгоритм пошуку зв'язних компонентів для розгалужених мереж (Multipoint Splices).**
   У реальних бортових джгутах лінії живлення (`VCC_5V`) та землі (`GND`) не є простими з'єднаннями «точка-точка» (Point-to-Point), а утворюють зіркоподібні або шлейфові розгалуження (Multi-drop Nets), де одна вхідна лінія з'єднана з трьома-п'ятьма роз'ємами периферії. Для коректної верифікації таких ланцюгів тестер реалізує алгоритм пошуку зв'язних компонентів графу на основі системи неперетинних множин (Disjoint Set Union, DSU):
   - Кожен контакт `v_i` ініціалізується як окрема множина `MakeSet(i)`.
   - Для кожного виявленого ребра `(i, j)`, де `A_meas[i][j] == 1`, виконується операція об'єднання `Union(i, j)`.
   - Результуючий список множин еквівалентності порівнюється з проєктним переліком електричних ланцюгів (Netlist Nets). Це виключає помилкові спрацьовування тестера на розгалужених шинах живлення.

```
Збудження лінії i:
Drive (i) = HIGH ───┬─── [Провідник i-j] ───┬───> Sense (j) = HIGH  (Цілісність OK)
                    │                       │
                    └─── [Замикання i-k] ───┴───> Sense (k) = HIGH  (Дефект: Short)
```

---

### Апаратна архітектура комутаційної матриці тестера

Для комутації 64 або 128 контактних точок без використання дорогих високовольтних релейних матриць застосовується каскад швидкісних двонаправлених зсувних регістрів або спеціалізованих розширювачів введення-виведення:

1. **Драйверний каскад збудження:** Зсувні регістри з виходом із трьома станами (наприклад, 74HC595 або високовольтні TPIC6B595). Кожен вихід захищений струмообмежувальним резистором `R_lim = 330 Ом` та парою діодів Шотткі (BAV99), що шунтують лінії на шини `GND` та `VCC`. Це унеможливлює пошкодження мікросхем тестера у випадку випадкового підключення силового акумулятора 24 В замість сигнального джгута.
2. **Сенсорний каскад опитування:** Паралельно-послідовні регістри зчитування (74HC165) або матричні аналогові мультиплексори (CD74HC4067). Вхідний імпеданс кожної лінії становить `100 кОм` (Pull-Down), що гарантує чіткий рівень логічного нуля на обірваних або непідключених лініях.
3. **Модуль чотирипровідного вимірювання опору (Kelvin 4-Wire Sensing):**
   Для визначення якості обтиску окремих контактів (перехідний опір `R_contact < 20 мОм`) тестер комутує джерело каліброваного постійного струму `I_test = 100 мА` через два силові дроти (Force+ та Force-), а мікровольтний спад напруги `ΔU` знімає через два незалежні вимірювальні провідники (Sense+ та Sense-), підключені безпосередньо до контактних ламелей роз'єму. Опір обтиску розраховується за законом Ома:

```
R_crimp = ΔU_sense / I_force      [чотирипровідна схема Кельвіна]
```

Це виключає опір тестових шлейфів самого стенду з результатів вимірювання.

---

### Компенсація термоелектрорушійної сили та калібрування каналу Кельвіна

Під час мікроомних вимірювань перехідного опору контактів на рівні одиниць міліомів серйозною завадою стає явище термоелектрорушійної сили (ефект Зеєбека). На межі контакту між різнорідними металами (наприклад, мідний провідник, нікельований підшар клеми, золоте покриття піна та олов'яно-свинцевий або безсвинцевий припій тестової плати) виникає паразитна термо-ЕРС величиною `U_th ≈ 3...10 мкВ / °C`.

При тестовому струмі `I_force = 100 мА` вимірюваний спад напруги на якісному контакті з опором `R = 5 мОм` становить:

```
ΔU = I · R = 0.1 А · 0.005 Ом = 500 мкВ
```

Паразитна термо-ЕРС `U_th = 15 мкВ`, викликана локальним нагрівом контактів струмом або рукою оператора, створює відносну похибку вимірювання опору до 3–5%.

Для повної компенсації термо-ЕРС та напруги зсуву операційних підсилювачів (Offset Voltage) алгоритм тестера реалізує метод двофазного реверсивного вимірювання струму (Current Reversal Technique):

1. **Пряма фаза (Forward Phase):** Струм `+I_force` подається від контакту A до контакту B. АЦП вимірює напругу:
   `U_fwd = +I_force · R_contact + U_th + U_offset`
2. **Зворотна фаза (Reverse Phase):** Полярність джерела струму перемикається за допомогою H-моста, струм `-I_force` подається від контакту B до контакту A. АЦП вимірює напругу:
   `U_rev = -I_force · R_contact + U_th + U_offset`
3. **Обчислення істинного опору:** Віднімання двох виміряних значень повністю знищує синфазні адитивні похибки `U_th` та `U_offset`:

```
ΔU_true = (U_fwd - U_rev) / 2
= [(I · R + U_th + U_off) - (-I · R + U_th + U_off)] / 2
= (2 · I · R) / 2
= I_force · R_contact      [повна компенсація термо-ЕРС та зміщення]
```

Отримане значення `ΔU_true` використовується для прецизійного розрахунку перехідного опору гільзи з точністю до `0.1 мОм`.

---

### Рефлектометрія часової області (TDR) для локалізації місця обриву

Якщо матричний тест фіксує обрив довгого кабелю (наприклад, триметрового джгута живлення крилового сервоприводу літакового безпілотника), важливо визначити фізичне місце пошкодження: чи дріт перебитий біля кореневого роз'єму, чи обірваний усередині консолі крила.

Тестер використовує спрощений метод рефлектометрії часової області (Time-Domain Reflectometry, TDR). Вихідний каскад формує швидкий імпульс напруги з крутим фронтом наростання `t_rise < 1 нс`. Імпульс поширюється вздовж лінії зі швидкістю сигналу в діелектрику `v_prop`:

```
v_prop = c · VF      [швидкість поширення електромагнітної хвилі]
```

де `c = 3 · 10⁸ м/с` — швидкість світла у вакуумі, а `VF` (Velocity Factor) — коефіцієнт уповільнення діелектрика (для силіконової ізоляції `VF ≈ 0.66...0.70`, для фторопласту PTFE `VF ≈ 0.69`).

Коли електромагнітна хвиля досягає місця обриву (нескінченний імпеданс `Z_L = ∞`), коефіцієнт відбиття становить `Γ = +1`. Хвиля відбивається у фазі та повертається до початку кабелю через інтервал часу `Δt`:

```
L_break = (v_prop · Δt) / 2 = (c · VF · Δt) / 2      [відстань до точки обриву]
```

Швидкісний таймер мікроконтролера з блоком захоплення вхідного сигналу (Input Capture) вимірює часову затримку `Δt` між випроміненим та відбитим імпульсом. При затримці `Δt = 10 нс` координата обриву становить:

```
L_break = (3 · 10⁸ · 0.66 · 10 · 10⁻⁹) / 2 = 1.98 / 2 = 0.99 м ≈ 1.0 м
```

Оператор отримує точну вказівку на місце перебиття дроту без необхідності розпорювати захисне обплетення по всій довжині джгута.

---

### Виявлення плаваючих контактів та мікророзривів (Glitch Detection)

Найнебезпечніший клас дефектів бортових джгутів — це контактні мікротріщини в гільзі обтиску (crimping fatigue) або окислені ламелі роз'ємів JST-GH/JST-SH. У статичному стані на столі такий дріт показує нормальний електричний контакт. Однак під дією гармонійних вібрацій двигунів та пропелерів на частотах 100–500 Гц зазор між жилами розмикається на мікросекундні інтервали часу (Micro-Interruption / Fretting Corrosion).

Тестер реалізує режим динамічного струшування (Shake & Vibration Test):
- Входи апаратного матричного блоку налаштовуються на тригерне детектування спаду напруги за перериваннями (Falling Edge Interrupt) або через високошвидкісний таймер зі швидкістю опитування `f_sample ≥ 1 МГц`.
- Якщо під час механічного згинання джгута напруга на замкненій лінії падає нижче логічного порогу `V_IL = 0.8 В` на час `t_glitch > 1 мкс`, тестер фіксує подію нестабільного контакту `HARNESS_INTERMITTENT_FAULT` із зазначенням конкретного номера піна та тривалості збою.

---

### Реалізація програмного рушія тестування джгутів

Нижче наведено повну реалізацію тестера кабельних джгутів. Модуль містить механізми автонавчання за еталонним зразком (Golden Sample Learning), швидкісного порозрядного бітмаскового порівняння матриць суміжності до 64 контактів, локалізації топологічних дефектів та реєстрації мікророзривів у реальному часі.

:::tabs
```c
/**
 * @file harness_tester.h
 * @brief Драйвер та аналітичний рушій матричного тестування кабельних джгутів (C99).
 */

#ifndef HARNESS_TESTER_H
#define HARNESS_TESTER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HARNESS_MAX_PINS 64U
#define HARNESS_MATRIX_WORDS ((HARNESS_MAX_PINS + 63U) / 64U)

/**
 * @brief Типи топологічних дефектів кабельного джгута.
 */
typedef enum {
    HARNESS_DEFECT_NONE = 0,
    HARNESS_DEFECT_OPEN_CIRCUIT,       /**< Обрив провідника */
    HARNESS_DEFECT_SHORT_CIRCUIT,      /**< Закорочення між незалежними лініями */
    HARNESS_DEFECT_MISWIRED_PIN,       /**< Переплутаний пін (крос-з'єднання) */
    HARNESS_DEFECT_INTERMITTENT_GLITCH /**< Плаваючий контакт під вібрацією */
} harness_defect_type_t;

/**
 * @brief Запис про одиничний виявлений дефект.
 */
typedef struct {
    harness_defect_type_t type;
    uint8_t pin_a;                     /**< Номер ведучого піна (0..N-1) */
    uint8_t pin_b;                     /**< Номер веденого піна (0..N-1) */
    uint32_t glitch_duration_us;       /**< Тривалість мікрообриву в мікросекундах */
} harness_defect_entry_t;

/**
 * @brief Матриця провідності джгута (бітове представлення N x N).
 */
typedef struct {
    uint8_t pin_count;
    uint64_t rows[HARNESS_MAX_PINS];   /**< Бітова маска: біт j у rows[i] = 1, якщо i з'єднано з j */
} harness_matrix_t;

/**
 * @brief Апаратний інтерфейс низькорівневого доступу до пінів тестера.
 */
typedef struct {
    void (*set_pin_mode_drive)(uint8_t pin, bool level_high);
    void (*set_pin_mode_sense)(uint8_t pin);
    bool (*read_pin_level)(uint8_t pin);
    void (*delay_us)(uint32_t us);
    uint32_t (*get_time_us)(void);
} harness_hw_interface_t;

/**
 * @brief Результати повного тестування джгута.
 */
typedef struct {
    bool is_passed;
    uint32_t total_errors;
    uint32_t open_circuits;
    uint32_t short_circuits;
    uint32_t miswires;
    uint32_t intermittent_glitches;
    uint32_t test_duration_us;
} harness_test_summary_t;

/**
 * @brief Дескриптор стану сесії тестування джгута.
 */
typedef struct {
    uint8_t pin_count;
    harness_matrix_t ref_matrix;       /**< Еталонна матриця з'єднань */
    harness_matrix_t measured_matrix;  /**< Фактично виміряна матриця */
    harness_hw_interface_t hw;
    harness_defect_entry_t defect_log[128];
    uint32_t defect_count;
    uint32_t max_defects;
} harness_session_t;

/**
 * @brief Ініціалізація сесії тестування.
 */
void harness_session_init(harness_session_t *session, uint8_t pin_count, const harness_hw_interface_t *hw);

/**
 * @brief Очищення матриці з'єднань.
 */
void harness_matrix_clear(harness_matrix_t *mat, uint8_t pin_count);

/**
 * @brief Додавання зв'язку в матрицю (двосторонній симетричний зв'язок).
 */
bool harness_matrix_add_wire(harness_matrix_t *mat, uint8_t pin_a, uint8_t pin_b);

/**
 * @brief Режим навчання: зняття еталонної матриці з перевіреного зразка джгута.
 */
bool harness_learn_golden_sample(harness_session_t *session);

/**
 * @brief Виконання повного статичного сканування топології джгута.
 */
bool harness_scan_network(harness_session_t *session);

/**
 * @brief Порівняння виміряної матриці з еталонною та формування діагностичного звіту.
 */
void harness_analyze_defects(harness_session_t *session, harness_test_summary_t *summary);

/**
 * @brief Режим вібраційного моніторингу: швидкісне детектування мікрообривів.
 */
uint32_t harness_monitor_vibration_glitches(harness_session_t *session, uint32_t duration_ms);

#ifdef __cplusplus
}
#endif

#endif /* HARNESS_TESTER_H */
```
```cpp
/**
 * @file HarnessTester.hpp
 * @brief Об'єктно-орієнтований рушій верифікації кабельних мереж (C++20).
 */

#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <vector>
#include <span>
#include <expected>
#include <string_view>
#include <functional>
#include <bitset>
#include <chrono>

namespace DroneHarness {

constexpr size_t MaxPins = 64;

enum class DefectType : uint8_t {
    None = 0,
    OpenCircuit,
    ShortCircuit,
    MiswiredPin,
    IntermittentGlitch
};

struct DefectRecord {
    DefectType type{DefectType::None};
    uint8_t pinA{0};
    uint8_t pinB{0};
    uint32_t glitchDurationUs{0};
};

struct TestSummary {
    bool isPassed{false};
    size_t totalErrors{0};
    size_t openCircuits{0};
    size_t shortCircuits{0};
    size_t miswires{0};
    size_t intermittentGlitches{0};
    std::chrono::microseconds testDuration{0};
};

enum class HardwareError : uint8_t {
    InvalidPinIndex,
    PinDriveFailure,
    SensorTimeout,
    NullInterface
};

/**
 * @brief Концепт для апаратного рівня введення-виведення тестера.
 */
template <typename T>
concept HarnessHardwareDriver = requires(T hw, uint8_t pin, bool level, uint32_t us) {
    { hw.setDrive(pin, level) } -> std::same_as<void>;
    { hw.setSense(pin) } -> std::same_as<void>;
    { hw.readLevel(pin) } -> std::same_as<bool>;
    { hw.delayMicroseconds(us) } -> std::same_as<void>;
    { hw.micros() } -> std::same_as<uint64_t>;
};

/**
 * @brief Клас матриці електричної суміжності провідників.
 */
class AdjacencyMatrix {
public:
    explicit constexpr AdjacencyMatrix(size_t pinCount = 0) noexcept : pinCount_(pinCount) {
        clear();
    }

    constexpr void clear() noexcept {
        for (auto &row : rows_) {
            row.reset();
        }
    }

    constexpr bool addConnection(uint8_t pinA, uint8_t pinB) noexcept {
        if (pinA >= pinCount_ || pinB >= pinCount_) {
            return false;
        }
        rows_[pinA].set(pinB);
        rows_[pinB].set(pinA);
        return true;
    }

    constexpr bool isConnected(uint8_t pinA, uint8_t pinB) const noexcept {
        if (pinA >= pinCount_ || pinB >= pinCount_) {
            return false;
        }
        return rows_[pinA].test(pinB);
    }

    [[nodiscard]] constexpr size_t pinCount() const noexcept { return pinCount_; }
    [[nodiscard]] constexpr const std::bitset<MaxPins>& row(size_t index) const noexcept { return rows_[index]; }
    [[nodiscard]] constexpr std::bitset<MaxPins>& row(size_t index) noexcept { return rows_[index]; }

private:
    size_t pinCount_{0};
    std::array<std::bitset<MaxPins>, MaxPins> rows_{};
};

/**
 * @brief Рушій автоматизованого тестування топології та мікрообривів.
 */
template <HarnessHardwareDriver Driver>
class HarnessEngine {
public:
    HarnessEngine(Driver &hw, size_t pinCount)
        : hw_(hw), pinCount_(pinCount), refMatrix_(pinCount), measuredMatrix_(pinCount) {
        defects_.reserve(64);
    }

    void setGoldenNetlist(const AdjacencyMatrix &netlist) noexcept {
        refMatrix_ = netlist;
    }

    [[nodiscard]] std::expected<void, HardwareError> learnGoldenSample() noexcept {
        auto scanRes = scanPhysicalHarness();
        if (!scanRes) {
            return std::unexpected(scanRes.error());
        }
        refMatrix_ = measuredMatrix_;
        return {};
    }

    [[nodiscard]] std::expected<TestSummary, HardwareError> runFullDiagnostic() noexcept {
        const auto start = hw_.micros();
        defects_.clear();

        auto scanRes = scanPhysicalHarness();
        if (!scanRes) {
            return std::unexpected(scanRes.error());
        }

        TestSummary summary{};
        analyzeNetwork(summary);

        const auto end = hw_.micros();
        summary.testDuration = std::chrono::microseconds(end - start);
        summary.isPassed = (summary.totalErrors == 0);

        return summary;
    }

    [[nodiscard]] std::expected<size_t, HardwareError> runDynamicGlitchMonitor(std::chrono::milliseconds duration) noexcept {
        const uint64_t startUs = hw_.micros();
        const uint64_t durationUs = static_cast<uint64_t>(duration.count()) * 1000ULL;
        size_t glitchCount = 0;

        // Конфігуруємо тестові ланцюги за еталонною схемою
        for (uint8_t i = 0; i < pinCount_; ++i) {
            hw_.setSense(i);
        }

        while ((hw_.micros() - startUs) < durationUs) {
            for (uint8_t i = 0; i < pinCount_; ++i) {
                // Збуджуємо активний пін
                hw_.setDrive(i, true);
                hw_.delayMicroseconds(2);

                for (uint8_t j = 0; j < pinCount_; ++j) {
                    if (refMatrix_.isConnected(i, j) && i != j) {
                        if (!hw_.readLevel(j)) {
                            // Фіксація тривалості мікророзриву
                            const uint64_t glitchStart = hw_.micros();
                            while (!hw_.readLevel(j) && (hw_.micros() - glitchStart < 5000)) {
                                // Очікування відновлення контакту
                            }
                            const uint32_t glitchDur = static_cast<uint32_t>(hw_.micros() - glitchStart);

                            defects_.push_back({
                                .type = DefectType::IntermittentGlitch,
                                .pinA = i,
                                .pinB = j,
                                .glitchDurationUs = (glitchDur > 0) ? glitchDur : 1U
                            });
                            glitchCount++;
                        }
                    }
                }
                hw_.setSense(i);
            }
        }
        return glitchCount;
    }

    [[nodiscard]] std::span<const DefectRecord> defects() const noexcept {
        return defects_;
    }

private:
    std::expected<void, HardwareError> scanPhysicalHarness() noexcept {
        measuredMatrix_.clear();

        for (uint8_t i = 0; i < pinCount_; ++i) {
            hw_.setSense(i);
        }

        for (uint8_t drivePin = 0; drivePin < pinCount_; ++drivePin) {
            hw_.setDrive(drivePin, true);
            hw_.delayMicroseconds(5); // Час заряду ємності лінії

            for (uint8_t sensePin = 0; sensePin < pinCount_; ++sensePin) {
                if (hw_.readLevel(sensePin)) {
                    measuredMatrix_.addConnection(drivePin, sensePin);
                }
            }
            hw_.setSense(drivePin);
        }
        return {};
    }

    void analyzeNetwork(TestSummary &summary) noexcept {
        for (uint8_t i = 0; i < pinCount_; ++i) {
            for (uint8_t j = i + 1; j < pinCount_; ++j) {
                const bool expected = refMatrix_.isConnected(i, j);
                const bool actual = measuredMatrix_.isConnected(i, j);

                if (expected && !actual) {
                    summary.openCircuits++;
                    summary.totalErrors++;
                    defects_.push_back({DefectType::OpenCircuit, i, j, 0});
                } else if (!expected && actual) {
                    summary.shortCircuits++;
                    summary.totalErrors++;
                    defects_.push_back({DefectType::ShortCircuit, i, j, 0});
                }
            }
        }
    }

    Driver &hw_;
    size_t pinCount_{0};
    AdjacencyMatrix refMatrix_;
    AdjacencyMatrix measuredMatrix_;
    std::vector<DefectRecord> defects_;
};

} // namespace DroneHarness
```
:::

---

### Низькорівневий рушій тестування джгута на чистому C99

Реалізація файлу `harness_tester.c` демонструє обробку бітових масок, детектування переплутаних пінів та роботу з мікросекундними таймерами на мікроконтролерах STM32 / ESP32.

:::tabs
```c
/**
 * @file harness_tester.c
 * @brief Реалізація функцій матричного сканування та аналізу дефектів джгутів (C99).
 */

#include "harness_tester.h"
#include <string.h>

void harness_session_init(harness_session_t *session, uint8_t pin_count, const harness_hw_interface_t *hw)
{
    if (!session || !hw || pin_count > HARNESS_MAX_PINS) {
        return;
    }

    memset(session, 0, sizeof(harness_session_t));
    session->pin_count = pin_count;
    session->hw = *hw;
    session->max_defects = sizeof(session->defect_log) / sizeof(session->defect_log[0]);

    harness_matrix_clear(&session->ref_matrix, pin_count);
    harness_matrix_clear(&session->measured_matrix, pin_count);
}

void harness_matrix_clear(harness_matrix_t *mat, uint8_t pin_count)
{
    if (!mat) {
        return;
    }
    mat->pin_count = pin_count;
    for (uint8_t i = 0; i < HARNESS_MAX_PINS; ++i) {
        mat->rows[i] = 0ULL;
    }
}

bool harness_matrix_add_wire(harness_matrix_t *mat, uint8_t pin_a, uint8_t pin_b)
{
    if (!mat || pin_a >= mat->pin_count || pin_b >= mat->pin_count) {
        return false;
    }
    mat->rows[pin_a] |= (1ULL << pin_b);
    mat->rows[pin_b] |= (1ULL << pin_a);
    return true;
}

bool harness_scan_network(harness_session_t *session)
{
    if (!session || !session->hw.set_pin_mode_drive || !session->hw.read_pin_level) {
        return false;
    }

    const uint8_t n = session->pin_count;
    harness_matrix_clear(&session->measured_matrix, n);

    /* Усі піни переводяться в режим чутливого входу High-Z */
    for (uint8_t i = 0; i < n; ++i) {
        session->hw.set_pin_mode_sense(i);
    }

    /* Почергове сканування збудженням кожної тестової лінії */
    for (uint8_t drive_pin = 0; drive_pin < n; ++drive_pin) {
        session->hw.set_pin_mode_drive(drive_pin, true);
        session->hw.delay_us(5); /* Час стабілізації фронту напруги */

        for (uint8_t sense_pin = 0; sense_pin < n; ++sense_pin) {
            if (session->hw.read_pin_level(sense_pin)) {
                session->measured_matrix.rows[drive_pin] |= (1ULL << sense_pin);
            }
        }

        /* Повернення ведучого піна в безпечний стан High-Z */
        session->hw.set_pin_mode_sense(drive_pin);
    }

    return true;
}

bool harness_learn_golden_sample(harness_session_t *session)
{
    if (!harness_scan_network(session)) {
        return false;
    }
    memcpy(&session->ref_matrix, &session->measured_matrix, sizeof(harness_matrix_t));
    return true;
}

void harness_analyze_defects(harness_session_t *session, harness_test_summary_t *summary)
{
    if (!session || !summary) {
        return;
    }

    memset(summary, 0, sizeof(harness_test_summary_t));
    session->defect_count = 0;

    const uint8_t n = session->pin_count;
    const uint32_t t_start = session->hw.get_time_us ? session->hw.get_time_us() : 0;

    for (uint8_t i = 0; i < n; ++i) {
        for (uint8_t j = (uint8_t)(i + 1U); j < n; ++j) {
            const bool ref_conn = (session->ref_matrix.rows[i] & (1ULL << j)) != 0ULL;
            const bool meas_conn = (session->measured_matrix.rows[i] & (1ULL << j)) != 0ULL;

            if (ref_conn && !meas_conn) {
                summary->open_circuits++;
                summary->total_errors++;

                if (session->defect_count < session->max_defects) {
                    harness_defect_entry_t *entry = &session->defect_log[session->defect_count++];
                    entry->type = HARNESS_DEFECT_OPEN_CIRCUIT;
                    entry->pin_a = i;
                    entry->pin_b = j;
                    entry->glitch_duration_us = 0;
                }
            } else if (!ref_conn && meas_conn) {
                summary->short_circuits++;
                summary->total_errors++;

                if (session->defect_count < session->max_defects) {
                    harness_defect_entry_t *entry = &session->defect_log[session->defect_count++];
                    entry->type = HARNESS_DEFECT_SHORT_CIRCUIT;
                    entry->pin_a = i;
                    entry->pin_b = j;
                    entry->glitch_duration_us = 0;
                }
            }
        }
    }

    /* Аналіз на наявність переплутаних пінів (Miswired pins) */
    for (uint8_t i = 0; i < n; ++i) {
        uint8_t ref_target = 0xFF;
        uint8_t meas_target = 0xFF;

        for (uint8_t j = 0; j < n; ++j) {
            if (i != j) {
                if (session->ref_matrix.rows[i] & (1ULL << j)) {
                    ref_target = j;
                }
                if (session->measured_matrix.rows[i] & (1ULL << j)) {
                    meas_target = j;
                }
            }
        }

        if (ref_target != 0xFF && meas_target != 0xFF && ref_target != meas_target) {
            summary->miswires++;
            if (session->defect_count < session->max_defects) {
                harness_defect_entry_t *entry = &session->defect_log[session->defect_count++];
                entry->type = HARNESS_DEFECT_MISWIRED_PIN;
                entry->pin_a = i;
                entry->pin_b = meas_target;
                entry->glitch_duration_us = 0;
            }
        }
    }

    const uint32_t t_end = session->hw.get_time_us ? session->hw.get_time_us() : 0;
    summary->test_duration_us = t_end - t_start;
    summary->is_passed = (summary->total_errors == 0);
}

uint32_t harness_monitor_vibration_glitches(harness_session_t *session, uint32_t duration_ms)
{
    if (!session || !session->hw.get_time_us || !session->hw.read_pin_level) {
        return 0;
    }

    const uint8_t n = session->pin_count;
    const uint32_t start_us = session->hw.get_time_us();
    const uint32_t limit_us = duration_ms * 1000U;
    uint32_t glitches_found = 0;

    for (uint8_t i = 0; i < n; ++i) {
        session->hw.set_pin_mode_sense(i);
    }

    while ((session->hw.get_time_us() - start_us) < limit_us) {
        for (uint8_t i = 0; i < n; ++i) {
            session->hw.set_pin_mode_drive(i, true);
            session->hw.delay_us(2);

            for (uint8_t j = 0; j < n; ++j) {
                if (i != j && (session->ref_matrix.rows[i] & (1ULL << j))) {
                    if (!session->hw.read_pin_level(j)) {
                        const uint32_t g_start = session->hw.get_time_us();
                        while (!session->hw.read_pin_level(j) && (session->hw.get_time_us() - g_start < 5000U)) {
                            /* Очікування відновлення провідності */
                        }
                        const uint32_t g_dur = session->hw.get_time_us() - g_start;

                        if (session->defect_count < session->max_defects) {
                            harness_defect_entry_t *entry = &session->defect_log[session->defect_count++];
                            entry->type = HARNESS_DEFECT_INTERMITTENT_GLITCH;
                            entry->pin_a = i;
                            entry->pin_b = j;
                            entry->glitch_duration_us = (g_dur > 0) ? g_dur : 1U;
                        }
                        glitches_found++;
                    }
                }
            }
            session->hw.set_pin_mode_sense(i);
        }
    }

    return glitches_found;
}
```
```cpp
/**
 * @file HarnessTesterRunner.cpp
 * @brief Повний тестовий запуск діагностики кабельного джгута на C++20.
 */

#include "HarnessTester.hpp"
#include <iostream>
#include <chrono>
#include <thread>

namespace MockHardware {

class VirtualHarnessDriver {
public:
    void setDrive(uint8_t pin, bool level) noexcept {
        driveStates_[pin] = level;
    }

    void setSense(uint8_t pin) noexcept {
        driveStates_[pin] = false;
    }

    bool readLevel(uint8_t pin) noexcept {
        // Симуляція фізичних провідників: якщо активний пін з'єднаний з 'pin', повертаємо true
        for (size_t i = 0; i < DroneHarness::MaxPins; ++i) {
            if (driveStates_[i] && wiring_[i][pin]) {
                return true;
            }
        }
        return false;
    }

    void delayMicroseconds(uint32_t us) noexcept {
        auto start = std::chrono::steady_clock::now();
        while (std::chrono::duration_cast<std::chrono::microseconds>(
                   std::chrono::steady_clock::now() - start).count() < us) {
            // Spin-wait
        }
    }

    uint64_t micros() noexcept {
        return static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::microseconds>(
                std::chrono::steady_clock::now().time_since_epoch()).count());
    }

    void injectWire(uint8_t a, uint8_t b) noexcept {
        wiring_[a][b] = true;
        wiring_[b][a] = true;
    }

    void injectShort(uint8_t a, uint8_t b) noexcept {
        wiring_[a][b] = true;
        wiring_[b][a] = true;
    }

    void injectBreak(uint8_t a, uint8_t b) noexcept {
        wiring_[a][b] = false;
        wiring_[b][a] = false;
    }

private:
    std::array<bool, DroneHarness::MaxPins> driveStates_{};
    std::array<std::array<bool, DroneHarness::MaxPins>, DroneHarness::MaxPins> wiring_{};
};

} // namespace MockHardware

int main() {
    using namespace DroneHarness;

    MockHardware::VirtualHarnessDriver hw;
    constexpr size_t DroneGpsHarnessPins = 6; // JST-GH 6-pin (VCC, TX, RX, SCL, SDA, GND)

    // Конфігурація фізичного кабелю (GPS джгут)
    // 0: VCC_5V <-> 0
    // 1: UART_TX <-> 2 (Cross)
    // 2: UART_RX <-> 1 (Cross)
    // 3: I2C_SCL <-> 3
    // 4: I2C_SDA <-> 4
    // 5: GND     <-> 5
    for (uint8_t i = 0; i < DroneGpsHarnessPins; ++i) {
        hw.injectWire(i, i);
    }

    HarnessEngine<MockHardware::VirtualHarnessDriver> tester(hw, DroneGpsHarnessPins);

    // Встановлення еталонної схеми (прямий 6-піновий кабель)
    AdjacencyMatrix refNetlist(DroneGpsHarnessPins);
    for (uint8_t i = 0; i < DroneGpsHarnessPins; ++i) {
        refNetlist.addConnection(i, i);
    }
    tester.setGoldenNetlist(refNetlist);

    // 1. Тест справного кабелю
    auto res1 = tester.runFullDiagnostic();
    if (res1 && res1->isPassed) {
        std::cout << "[PASS] Еталонний джгут GPS JST-GH успішно верифіковано.\n";
    }

    // 2. Внесення дефекту: обрив лінії SDA (пін 4) та коротке замикання між пінами 1 та 2
    hw.injectBreak(4, 4);
    hw.injectShort(1, 2);

    auto res2 = tester.runFullDiagnostic();
    if (res2) {
        std::cout << "\n[DIAGNOSTIC] Знайдено дефектів: " << res2->totalErrors << "\n";
        std::cout << "  - Обривів: " << res2->openCircuits << "\n";
        std::cout << "  - Закорочень: " << res2->shortCircuits << "\n";

        for (const auto &def : tester.defects()) {
            if (def.type == DefectType::OpenCircuit) {
                std::cout << "  [FAIL] Обрив провідника між пінами: " 
                          << static_cast<int>(def.pinA) << " та " 
                          << static_cast<int>(def.pinB) << "\n";
            } else if (def.type == DefectType::ShortCircuit) {
                std::cout << "  [FAIL] Небажане замикання між пінами: " 
                          << static_cast<int>(def.pinA) << " та " 
                          << static_cast<int>(def.pinB) << "\n";
            }
        }
    }

    return 0;
}
```
:::

---

### Аналіз часової складності та параметричної оптимізації

Матричний алгоритм сканування має детерміновану часову складність `O(N²)`, де `N` — кількість контактних точок тестера. При розмірі джгута `N = 64` повна матриця суміжності містить `4096` потенційних перевірок зв'язку. При апаратному часі заряду паразитних ємностей лінії `t_settle = 5 мкс` повний цикл статичного опитування триває:

```
T_scan = N · (t_settle + N · t_read)
= 64 · (5 мкс + 64 · 0.1 мкс)
= 64 · 11.4 мкс
≈ 730 мкс      [менше однієї мілісекунди на повний джгут]
```

Завдяки мілісекундному циклу сканування тестер здатен виконувати понад 1000 повних топологічних опитувань за одну секунду, що робить його високоефективним інструментом для динамічних вібростендових випробувань (Vibration Table Testing) згідно з військовими та аерокосмічними стандартами MIL-STD-810H та DO-160G.

#### Крайові випадки та апаратні пастки:
1. **Паразитна ємність довгих екранованих кабелів.** У довгих сигнальних джгутах (понад 1.5–2 м) міжкабельна ємність досягає `100...200 пФ`. Якщо час очікування перед зчитуванням `t_settle` заданий меншим за `2 мкс`, залишковий заряд на ємності сусіднього провідника викликає хибне детектування короткого замикання (Phantom Short). Для усунення цього ефекту драйвер розряджає тестові піни через внутрішній транзистор підтяжки до землі перед переведенням у режим вимірювання.
2. **Захисні діоди ESD та супресори на платах.** Якщо кабель тестується підключеним до електронного модуля, захисні TVS-діоди або зворотні діоди польових транзисторів можуть проводити струм в одному напрямку. Матриця провідності стає асиметричною (`A[i][j] ≠ A[j][i]`). Програмний рушій розпізнає такі асиметричні вузли та виділяє їх в окремий клас напівпровідникових зв'язків.
3. **Витік через зволожений флюс.** Залишки невідмитого водорозчинного або каніфольного флюсу на виводах роз'ємів за підвищеної вологості створюють паразитний опір витоку порядку `100 кОм...1 МОм`. Використання регульованого порогу компаратора напруги дозволяє відрізнити металічне коротке замикання (`R < 10 Ом`) від поверхневого струму витоку.

---

### Цілісність високошвидкісних диференціальних сигналів у джгуті (CAN FD та 100BASE-T1)

Сучасні безпілотні авіаційні комплекси переходять від низькошвидкісних шин UART/I2C до високошвидкісних диференціальних інтерфейсів: CAN FD зі швидкістю передачі даних до 5–8 Мбіт/с та бортового Ethernet 100BASE-T1 (BroadR-Reach) зі швидкістю 100 Мбіт/с по одній неекранованій витій парі (UTP).

Для таких ліній простої перевірки провідності за постійним струмом недостатньо. Кабельний джгут повинен задовольняти суворим вимогам хвильового імпедансу та фазового перекосу (Skew):

1. **Хвильовий імпеданс витої пари (Differential Characteristic Impedance `Z_diff`):**
   - Для шини CAN FD: `Z_diff = 120 Ом ± 10%`.
   - Для шини 100BASE-T1: `Z_diff = 100 Ом ± 10%`.
   
   Хвильовий опір пари провідників у діелектрику з відносною проникністю `ε_r` визначається відношенням діаметра жили `d` до відстані між центрами жил `s`:

```
Z_diff = (120 / √ε_r) · ln(2 · s / d)      [хвильовий імпеданс симетричної витої пари]
```

Якщо під час монтажу джгута крок скрутки пари порушений або захисна термозбіжка надмірно здавила провідники, зменшуючи зазор `s`, хвильовий опір локально просідає до `80...90 Ом`. Це викликає паразитні хвильові відбиття сигналу на межі неоднорідності з коефіцієнтом `Γ = (Z_load - Z_0) / (Z_load + Z_0)`, що призводить до спотворення фронтів CAN-повідомлень та появи циклічних помилок CRC у польоті.

2. **Фазовий перекіс у парі (Intra-Pair Skew `Δt_skew`):**
   Різниця фізичної довжини провідників прямого (`CAN_H`) та інверсного (`CAN_L`) сигналів не повинна перевищувати `ΔL < 2 мм`, що відповідає часовому перекосу `Δt_skew < 15 пс`. Порушення симетрії пари перетворює диференціальний корисний сигнал на синфазну електромагнітну заваду (Common-Mode Noise), яка інтенсивно випромінюється джгутом на бортові антени супутникової навігації GNSS.

---

### Формат опису нетліста та автоматизація виробничого контролю

Для інтеграції тестера в автоматизовану лінію складання джгутів використовується стандартизований формат файлу схеми з'єднань (JSON / CSV Netlist Definition). Файл описує фізичні роз'єми, типи контактів та допустимі електричні пороги для кожного ланцюга:

```json
{
  "harness_name": "GPS_MAG_CAN_HARNESS_V3",
  "pin_count": 6,
  "connectors": [
    { "id": "J1", "type": "JST-GH-6P", "location": "FC_SIDE" },
    { "id": "J2", "type": "JST-GH-6P", "location": "GPS_SIDE" }
  ],
  "nets": [
    { "net_name": "VCC_5V",  "pins": ["J1.1", "J2.1"], "max_resistance_mohm": 35, "wire_awg": 26 },
    { "net_name": "CAN_TX",  "pins": ["J1.2", "J2.3"], "max_resistance_mohm": 60, "wire_awg": 28 },
    { "net_name": "CAN_RX",  "pins": ["J1.3", "J2.2"], "max_resistance_mohm": 60, "wire_awg": 28 },
    { "net_name": "I2C_SCL", "pins": ["J1.4", "J2.4"], "max_resistance_mohm": 60, "wire_awg": 30 },
    { "net_name": "I2C_SDA", "pins": ["J1.5", "J2.5"], "max_resistance_mohm": 60, "wire_awg": 30 },
    { "net_name": "GND",     "pins": ["J1.6", "J2.6"], "max_resistance_mohm": 35, "wire_awg": 26 }
  ],
  "insulation_voltage_v": 250,
  "min_insulation_mohm": 100
}
```

Прошивка тестера розбирає дану специфікацію, заповнює бітові матриці `A_ref` та встановлює пороги компаратора струму для кожного ланцюга відповідно до калібру проводу (AWG) та довжини джгута.

---

### Статистичний аналіз дефектів та візуалізація карти зв'язків

У промисловому виробництві тестер джгутів не лише виносить вердикт «Pass / Fail», а й веде накопичувальну базу даних статистичного контролю процесів (Statistical Process Control, SPC). Кожна зафіксована помилка класифікується за діаграмою Парето:

- **Знос матриці кримпера (Crimper Wear):** Якщо на певному типорозмірі контактів (наприклад, JST-GH AWG 28) спостерігається систематичне зростання перехідного опору або поява мікророзривів при вібрації у понад 2% виробів, система автоматично генерує сповіщення про необхідність регламентного калібрування або заміни механічних матриць кримпера.
- **Людський фактор при заправці пінів (Operator Pin Insertion Error):** Часті помилки переплутування пінів TX/RX сигналізують про потребу вдосконалення маркування проводів кольоровою смугою або застосування напівпрозорих корпусів роз'ємів з покроковою LED-підсвіткою гнізд на монтажному столі.
- **Тепловий дрейф тестового стенду:** Перед початком кожної робочої зміни стенд виконує автоматичне самокалібрування (Self-Test Fixture Loopback) з вимірюванням напруги зсуву ОУ та опору внутрішніх мультиплексорів за температурним діапазоном від `-10 °C` до `+45 °C`.

---

### Методика виробничої інтеграції та протокол випробувань

На серійному виробництві безпілотників автоматизований тестер джгутів підключається до тестової панелі (Test Fixture Bed-of-Nails або набір ответних колодок JST-GH, JST-SH, XT30). Процес контролю якості включає чотири обов'язкові етапи:

1. **Етап 1: Холодне статичне сканування (Static Continuity).**
   Оператор вставляє роз'єми свіжозібраного джгута у відповідні гнізда стенду. Тестер миттєво зчитує матрицю суміжності `A_meas` і звіряє її з завантаженим із бази даних файлом проєктного нетліста (JSON/CSV Netlist). Якщо знайдено переплутані піни або обриви, стенд блокує подальші тести та підсвічує червоним світлодіодом дефектне гніздо і номер контакту.

2. **Етап 2: Динамічний тест на вібростолі (Dynamic Flex & Shake).**
   Джгут піддається механічній деформації: оператор вручну згинає кабель у критичних зонах біля роз'ємів (Strain Relief Zone) або стенд вмикає електродинамічний вібростенд з прискоренням до 5–10 g на частотах 50–200 Гц. Протягом 10–30 секунд рушій виконує безперервний моніторинг мікророзривів за функцією `harness_monitor_vibration_glitches()`. Навіть поодинокий мікросекундний спад напруги призводить до відхилення джгута, оскільки в польоті такий мікророзрив на шині I2C призведе до апаратного зависання компаса чи барометра.

3. **Етап 3: Вимірювання падіння напруги силових шин (High-Current Voltage Drop).**
   Силові лінії живлення ESC та акумулятора навантажуються випробувальним струмом 10–20 А протягом 3 секунд з одночасним вимірюванням напруги на клемах. Падіння напруги `ΔU > 50 мВ` свідчить про неякісний обтиск гільзи або нещільну посадку пелюсток роз'єму XT60, що загрожує локальним перегрівом та плавленням пластикового корпусу під час зльоту дрона.

4. **Етап 4: Перевірка опору ізоляції та діелектричної міцності (Hi-Pot / Insulation Test).**
   Між силовими шинами живлення `+24...50 В` та слабкострумовими лініями датчиків `3.3 В` прикладається випробувальна напруга `V_iso = 250 В` постійного струму. Тестер вимірює струм витоку `I_leak`. За стандартом IPC/WHMA-A-620 опір ізоляції повинен перевищувати `R_iso ≥ 100 МОм` (що відповідає струму витоку `I_leak < 2.5 мкА`). Цей тест виявляє приховані мікропроколи ізоляції та залишки провідного карбонового пилу, які за підвищеної вологості або конденсату спричинять високовольтний пробій та миттєве вигорання вхідних кіл політного контролера.

Після успішного проходження всіх етапів тестер генерує цифровий сертифікат якості з унікальним хешем CRC32 та заносить серійний номер джгута у виробничу базу даних простежуваності (Traceability Log).
