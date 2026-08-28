# ⚙️ Автомат сходинкового тесту силової установки на C та C++

Зібраний [стенд тяги](root:embedded/stend-tiahy) із тензодатчиком, датчиком струму й тахометром не можна випробовувати ручним крутінням ручки газу: людина не здатна витримати сходинку з точністю до секунди, забуває зняти теплову тару між точками й не встигає знеструмити мотор, якщо на 80% газу відірве лопать або почне горіти обмотка. Щоб зняти повторювані карти характеристик і вберегти обладнання, випробувальний цикл доручають автономному кінцевому автомату. Цей модуль керує повною послідовністю тесту — від зняття холодного нуля до покрокового розгону, стабілізації вихрового сліду, збору вибірок і безпечного охолодження, — відстежуючи чотири критичні аварійні умови на кожному мікросекундному такті.

## Архітектура автомата випробування

Тестова послідовність розгортається у вісім послідовних станів, де кожен перехід прив'язаний до монотонного таймера мікроконтролера та валідації сенсорних прапорців:

1. **`IDLE` (Очікування):** Мотор знеструмлений (наказ газу 0%), силове реле розімкнене або лінія DShot транслює нульовий сигнал безпеки. Очікування команди старту по UART або натискання апаратної кнопки.
2. **`PRE_TARE` (Початкове тарування):** Протягом 1.5 секунди при нерухомому гвинті зчитується 100–120 відліків АЦП [HX711](root:hw-sensing/strain-gauges/api-loadcell-hx711.md). Обчислюється початкове зміщення нуля та фіксується базова температура балки `T_start`.
3. **`RAMP_STEP` (Плавне ступінчасте зростання):** Рівень газу плавно нарощується від попередньої сходинки до поточної зі швидкістю не більше 20% за секунду, щоб запобігти ударному навантаженню на тензобалку та струмовому удару в ключах ESC.
4. **`SETTLE_WAIT` (Витримка перехідного процесу):** На заданій сходинці (наприклад, 40%) система чекає 1.5 секунди. За цей час ротор виходить на стаціонарні оберти, а струмінь повітря формує стабільний вихровий слід без перехідних сплесків маси.
5. **`SAMPLE_ACQUIRE` (Накопичення та фільтрація):** Протягом 2.0 секунд накопичується масив вибірок (струм, напруга, тяга, RPM). Медіанний фільтр відсікає вібраційні викиди, розраховується середня електрична потужність `P = U · I` та питома тяга `g/W`. Точка записується у буфер або відправляється у стрім.
6. **`STEP_NEXT / DECIDE`:** Якщо поточний газ менший за 100%, вибирається наступна сходинка (наприклад, +10%) і автомат повертається до `RAMP_STEP`. Якщо досягнуто максимуму — скидання газу на 0% і перехід до тарування гарячого нуля.
7. **`POST_TARE` (Кінцеве тарування):** Після повної зупинки ротора знімається кінцеве зміщення нуля `Tare_end` та фіксується фінальна температура `T_end`. Різниця між `Tare_end` та `Tare_start` використовується для лінійної корекції дрейфу нуля для кожної пройденої сходинки.
8. **`COOLDOWN` (Охолодження):** Пауза 10–15 секунд для відведення тепла зі статора мотора перед наступним циклом.

### Аварійні переривання та швидкість захисту

Під час виконання будь-якого стану активні чотири перевірки, що викликають негайний перехід у стан `EMERGENCY_STOP` із блокуванням імпульсів на регулятор за менш ніж 1 мілісекунду:
- **Перевищення струму (`I > I_max`):** Захист від міжвиткового замикання обмоток або зриву синхронізації польових транзисторів ESC.
- **Втрата обертів при наявності струму (`RPM < 300` при `I > 3.0 А`):** Ознака механічного заклинювання ротора, провертання адаптера цанги або зірваного гвинта.
- **Зворотна або відсутня тяга (`Thrust < -20 г` при `Throttle > 30%`):** Помилка напрямку обертання фаз (мотор дме у зворотний бік) або перевернутий пропелер штовхального типу.
- **Перегрів балки чи силової частини (`T_sensor > 85 °C`):** Запобігання тепловій деградації тензомоста та вигоранню ізоляційного лаку статора.

### Апаратні таймінги та індуктивні викиди при відсічці

Під час аварійної відсічки на повному струмі (40–80 А) не можна просто розмикати електромеханічне реле на шині живлення. Індуктивність силових дротів довжиною 1 метр становить близько 1–1.5 мкГн. Миттєвий розрив струму 60 А за 1 мікросекунду генерує ЕРС самоіндукції:

```
V_spike = L · (dI / dt) = 1.5e-6 Гн · (60 А / 1e-6 с) = 90 В
```

Такий 90-вольтовий викид миттєво пробиває силові MOSFET-ключі регулятора швидкості та випалює чутливий вхід монітора [INA226](root:embedded/power-logger/comp-current-sense-adc.md).

Тому алгоритм захисту розділений на два рівні:
1. **Програмна відсічка через протокол DShot (час реакції 200–400 мкс):** На регулятор негайно надсилається нульовий кадр газу або спеціальна команда відключення мотора (`DSHOT_CMD_MOTOR_STOP`). Драйвер ESC плавно знімає комутацію фаз, а енергія індуктивності обмоток гаситься через зворотні діоди польових транзисторів у конденсатори вхідного фільтра.
2. **Аварійний силовий розмикач (електромеханічний контактор або твердотільний ключ):** Спрацьовує з затримкою 50–100 мс після зняття сигналу DShot як дублюючий контур на випадок повного апаратного пробою ключів регулятора.

### Формат потокового логування (CSV Streaming Frame)

Для збереження високої точності результатів кожна стаціонарна точка передається у порт USB-CDC/UART у текстовому форматі CSV із контрольною сумою. Це дає змогу візуалізувати криві тяги в реальному часі за допомогою скриптів на Python або лабораторних дашбордів:

```
timestamp_ms,state,throttle_pct,thrust_g,v_bus,i_bus,p_el,rpm,eff_gpw,temp_c
15200,ACQUIRE,40.0,485.2,22.84,5.42,123.79,11420,3.92,34.2
```

При швидкості UART 115200 бод рядок довжиною 80 байтів передається за 7.0 мс, що становить менше 40% пропускної здатності шини при частоті оновлення кадрів 50 Гц і гарантує відсутність блокування основного вимірювального циклу.

## Реалізація модуля керування

Нижче наведено модульний код кінцевого автомата стенду випробувань. Версія мовою C сфокусована на детермінованому виконанні без динамічної пам'яті, а версія на C++ надає безпечні типи вимірювань, перерахування станів із захистом простору імен та обробку результатів через `std::expected`.

:::tabs
@tab C
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_TEST_STEPS 11
#define SAMPLES_PER_STEP 64

typedef enum {
    BENCH_STATE_IDLE = 0,
    BENCH_STATE_PRE_TARE,
    BENCH_STATE_RAMP,
    BENCH_STATE_SETTLE,
    BENCH_STATE_ACQUIRE,
    BENCH_STATE_POST_TARE,
    BENCH_STATE_COOLDOWN,
    BENCH_STATE_EMERGENCY
} bench_state_t;

typedef enum {
    ABORT_NONE = 0,
    ABORT_OVERCURRENT,
    ABORT_MOTOR_STALL,
    ABORT_REVERSE_THRUST,
    ABORT_OVERHEAT,
    ABORT_COMM_TIMEOUT
} abort_reason_t;

typedef struct {
    float max_current_a;
    float max_temp_c;
    float step_settle_time_s;
    float step_acquire_time_s;
    uint8_t step_increment_pct;
} bench_limits_t;

typedef struct {
    uint32_t timestamp_ms;
    float throttle_pct;
    float thrust_grams;
    float voltage_v;
    float current_a;
    float power_w;
    float rpm;
    float eff_grams_per_watt;
    float temp_c;
} bench_record_t;

typedef struct {
    bench_state_t state;
    abort_reason_t abort_reason;
    bench_limits_t limits;
    
    uint8_t current_step_idx;
    uint8_t total_steps;
    float target_throttle;
    float current_throttle;
    
    uint32_t state_entry_time_ms;
    float pre_tare_offset_g;
    float post_tare_offset_g;
    float start_temp_c;
    float end_temp_c;
    
    bench_record_t step_results[MAX_TEST_STEPS];
    
    // Накопичувальні буфери поточної сходинки
    float acc_thrust;
    float acc_voltage;
    float acc_current;
    float acc_rpm;
    float acc_temp;
    uint16_t sample_count;
} thrust_rig_controller_t;

// Зовнішні апаратні функції (HAL)
extern void hal_esc_write_throttle(float throttle_pct);
extern bool hal_hx711_read_grams(float *out_grams);
extern bool hal_ina226_read_power(float *out_v, float *out_a);
extern bool hal_tach_read_rpm(float *out_rpm);
extern bool hal_temp_read_c(float *out_temp_c);
extern uint32_t hal_get_time_ms(void);
extern void hal_uart_stream_record(const bench_record_t *rec);

void rig_init(thrust_rig_controller_t *rig, const bench_limits_t *limits) {
    memset(rig, 0, sizeof(*rig));
    rig->state = BENCH_STATE_IDLE;
    rig->abort_reason = ABORT_NONE;
    rig->limits = *limits;
    rig->total_steps = (100 / limits->step_increment_pct) + 1;
    if (rig->total_steps > MAX_TEST_STEPS) {
        rig->total_steps = MAX_TEST_STEPS;
    }
}

static void rig_emergency_abort(thrust_rig_controller_t *rig, abort_reason_t reason) {
    hal_esc_write_throttle(0.0f);
    rig->current_throttle = 0.0f;
    rig->state = BENCH_STATE_EMERGENCY;
    rig->abort_reason = reason;
}

static bool rig_check_safety(thrust_rig_controller_t *rig, float v, float i, float thrust, float rpm, float temp) {
    if (i > rig->limits.max_current_a) {
        rig_emergency_abort(rig, ABORT_OVERCURRENT);
        return false;
    }
    if (temp > rig->limits.max_temp_c) {
        rig_emergency_abort(rig, ABORT_OVERHEAT);
        return false;
    }
    if (rig->current_throttle > 25.0f && rpm < 300.0f && i > 2.5f) {
        rig_emergency_abort(rig, ABORT_MOTOR_STALL);
        return false;
    }
    if (rig->current_throttle > 30.0f && thrust < -25.0f) {
        rig_emergency_abort(rig, ABORT_REVERSE_THRUST);
        return false;
    }
    return true;
}

void rig_start_sequence(thrust_rig_controller_t *rig) {
    if (rig->state != BENCH_STATE_IDLE) return;
    rig->current_step_idx = 0;
    rig->current_throttle = 0.0f;
    rig->target_throttle = 0.0f;
    rig->acc_thrust = 0.0f;
    rig->sample_count = 0;
    rig->state_entry_time_ms = hal_get_time_ms();
    rig->state = BENCH_STATE_PRE_TARE;
    hal_esc_write_throttle(0.0f);
}

void rig_update(thrust_rig_controller_t *rig) {
    uint32_t now = hal_get_time_ms();
    uint32_t elapsed = now - rig->state_entry_time_ms;
    
    float raw_thrust = 0.0f, v = 0.0f, i = 0.0f, rpm = 0.0f, temp_c = 25.0f;
    hal_hx711_read_grams(&raw_thrust);
    hal_ina226_read_power(&v, &i);
    hal_tach_read_rpm(&rpm);
    hal_temp_read_c(&temp_c);
    
    if (rig->state != BENCH_STATE_IDLE && rig->state != BENCH_STATE_EMERGENCY) {
        if (!rig_check_safety(rig, v, i, raw_thrust - rig->pre_tare_offset_g, rpm, temp_c)) {
            return;
        }
    }
    
    switch (rig->state) {
        case BENCH_STATE_IDLE:
        case BENCH_STATE_EMERGENCY:
            hal_esc_write_throttle(0.0f);
            break;
            
        case BENCH_STATE_PRE_TARE:
            rig->acc_thrust += raw_thrust;
            rig->acc_temp += temp_c;
            rig->sample_count++;
            if (elapsed >= 1500) {
                rig->pre_tare_offset_g = rig->acc_thrust / (float)rig->sample_count;
                rig->start_temp_c = rig->acc_temp / (float)rig->sample_count;
                rig->current_step_idx = 0;
                rig->target_throttle = 0.0f;
                rig->state = BENCH_STATE_RAMP;
                rig->state_entry_time_ms = now;
            }
            break;
            
        case BENCH_STATE_RAMP:
            // Плавне доведення газу до цілі
            if (rig->current_throttle < rig->target_throttle) {
                rig->current_throttle += 0.5f; // +0.5% на кожен такт оновлення
                if (rig->current_throttle > rig->target_throttle) {
                    rig->current_throttle = rig->target_throttle;
                }
            }
            hal_esc_write_throttle(rig->current_throttle);
            if (rig->current_throttle >= rig->target_throttle) {
                rig->state = BENCH_STATE_SETTLE;
                rig->state_entry_time_ms = now;
            }
            break;
            
        case BENCH_STATE_SETTLE:
            if (elapsed >= (uint32_t)(rig->limits.step_settle_time_s * 1000.0f)) {
                rig->state = BENCH_STATE_ACQUIRE;
                rig->state_entry_time_ms = now;
                rig->acc_thrust = 0.0f;
                rig->acc_voltage = 0.0f;
                rig->acc_current = 0.0f;
                rig->acc_rpm = 0.0f;
                rig->acc_temp = 0.0f;
                rig->sample_count = 0;
            }
            break;
            
        case BENCH_STATE_ACQUIRE:
            rig->acc_thrust += (raw_thrust - rig->pre_tare_offset_g);
            rig->acc_voltage += v;
            rig->acc_current += i;
            rig->acc_rpm += rpm;
            rig->acc_temp += temp_c;
            rig->sample_count++;
            
            if (elapsed >= (uint32_t)(rig->limits.step_acquire_time_s * 1000.0f) && rig->sample_count > 0) {
                bench_record_t *rec = &rig->step_results[rig->current_step_idx];
                rec->timestamp_ms = now;
                rec->throttle_pct = rig->current_throttle;
                rec->thrust_grams = rig->acc_thrust / (float)rig->sample_count;
                rec->voltage_v = rig->acc_voltage / (float)rig->sample_count;
                rec->current_a = rig->acc_current / (float)rig->sample_count;
                rec->power_w = rec->voltage_v * rec->current_a;
                rec->rpm = rig->acc_rpm / (float)rig->sample_count;
                rec->temp_c = rig->acc_temp / (float)rig->sample_count;
                rec->eff_grams_per_watt = (rec->power_w > 0.05f) ? (rec->thrust_grams / rec->power_w) : 0.0f;
                
                hal_uart_stream_record(rec);
                
                rig->current_step_idx++;
                if (rig->current_step_idx < rig->total_steps) {
                    rig->target_throttle = (float)rig->current_step_idx * (float)rig->limits.step_increment_pct;
                    if (rig->target_throttle > 100.0f) rig->target_throttle = 100.0f;
                    rig->state = BENCH_STATE_RAMP;
                    rig->state_entry_time_ms = now;
                } else {
                    // Завершили всі сходинки — скидаємо газ і таруємося на гарячу
                    hal_esc_write_throttle(0.0f);
                    rig->current_throttle = 0.0f;
                    rig->acc_thrust = 0.0f;
                    rig->acc_temp = 0.0f;
                    rig->sample_count = 0;
                    rig->state = BENCH_STATE_POST_TARE;
                    rig->state_entry_time_ms = now;
                }
            }
            break;
            
        case BENCH_STATE_POST_TARE:
            rig->acc_thrust += raw_thrust;
            rig->acc_temp += temp_c;
            rig->sample_count++;
            if (elapsed >= 1500 && rig->sample_count > 0) {
                rig->post_tare_offset_g = rig->acc_thrust / (float)rig->sample_count;
                rig->end_temp_c = rig->acc_temp / (float)rig->sample_count;
                rig->state = BENCH_STATE_COOLDOWN;
                rig->state_entry_time_ms = now;
            }
            break;
            
        case BENCH_STATE_COOLDOWN:
            if (elapsed >= 10000) {
                rig->state = BENCH_STATE_IDLE;
            }
            break;
    }
}
```
@tab C++
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <chrono>

namespace thrust_rig {

enum class State : uint8_t {
    Idle,
    PreTare,
    Ramp,
    Settle,
    Acquire,
    PostTare,
    Cooldown,
    Emergency
};

enum class AbortReason : uint8_t {
    None,
    Overcurrent,
    MotorStall,
    ReverseThrust,
    Overheat,
    CommTimeout
};

struct BenchLimits {
    float max_current_a{45.0f};
    float max_temp_c{85.0f};
    std::chrono::milliseconds settle_duration{1500};
    std::chrono::milliseconds acquire_duration{2000};
    uint8_t step_increment_pct{10};
};

struct BenchRecord {
    std::chrono::milliseconds timestamp{0};
    float throttle_pct{0.0f};
    float thrust_grams{0.0f};
    float voltage_v{0.0f};
    float current_a{0.0f};
    float power_w{0.0f};
    float rpm{0.0f};
    float eff_grams_per_watt{0.0f};
    float temp_c{25.0f};
};

// Апаратний інтерфейс (HAL абстракція)
class IHardwareDriver {
public:
    virtual ~IHardwareDriver() = default;
    virtual void write_throttle(float pct) = 0;
    virtual auto read_thrust_raw_grams() -> std::expected<float, AbortReason> = 0;
    virtual auto read_bus_power() -> std::expected<std::pair<float, float>, AbortReason> = 0; // {V, A}
    virtual auto read_rotor_rpm() -> std::expected<float, AbortReason> = 0;
    virtual auto read_sensor_temp_c() -> std::expected<float, AbortReason> = 0;
    virtual auto get_uptime_ms() const -> std::chrono::milliseconds = 0;
    virtual void stream_record(const BenchRecord& record) = 0;
};

template <size_t MaxSteps = 11>
class RigController {
public:
    explicit constexpr RigController(const BenchLimits& limits, IHardwareDriver& hal)
        : limits_(limits), hal_(hal) {
        total_steps_ = (100 / limits_.step_increment_pct) + 1;
        if (total_steps_ > MaxSteps) total_steps_ = MaxSteps;
    }

    void start_test() noexcept {
        if (state_ != State::Idle) return;
        current_step_idx_ = 0;
        current_throttle_ = 0.0f;
        target_throttle_ = 0.0f;
        sample_count_ = 0;
        acc_thrust_ = 0.0f;
        acc_temp_ = 0.0f;
        state_entry_time_ = hal_.get_uptime_ms();
        state_ = State::PreTare;
        hal_.write_throttle(0.0f);
    }

    void abort_test(AbortReason reason) noexcept {
        hal_.write_throttle(0.0f);
        current_throttle_ = 0.0f;
        state_ = State::Emergency;
        abort_reason_ = reason;
    }

    void update() noexcept {
        const auto now = hal_.get_uptime_ms();
        const auto elapsed = now - state_entry_time_;

        // Читання апаратних сенсорів
        const auto thrust_res = hal_.read_thrust_raw_grams();
        const auto power_res = hal_.read_bus_power();
        const auto rpm_res = hal_.read_rotor_rpm();
        const auto temp_res = hal_.read_sensor_temp_c();

        if (!thrust_res || !power_res || !rpm_res || !temp_res) {
            abort_test(AbortReason::CommTimeout);
            return;
        }

        const float raw_thrust = *thrust_res;
        const auto [v, i] = *power_res;
        const float rpm = *rpm_res;
        const float temp_c = *temp_res;

        // Безпекові перевірки
        if (state_ != State::Idle && state_ != State::Emergency) {
            if (!check_safety(v, i, raw_thrust - pre_tare_offset_g_, rpm, temp_c)) {
                return;
            }
        }

        switch (state_) {
            case State::Idle:
            case State::Emergency:
                hal_.write_throttle(0.0f);
                break;

            case State::PreTare:
                acc_thrust_ += raw_thrust;
                acc_temp_ += temp_c;
                sample_count_++;
                if (elapsed >= std::chrono::milliseconds{1500} && sample_count_ > 0) {
                    pre_tare_offset_g_ = acc_thrust_ / static_cast<float>(sample_count_);
                    start_temp_c_ = acc_temp_ / static_cast<float>(sample_count_);
                    current_step_idx_ = 0;
                    target_throttle_ = 0.0f;
                    transition_to(State::Ramp, now);
                }
                break;

            case State::Ramp:
                if (current_throttle_ < target_throttle_) {
                    current_throttle_ += 0.5f;
                    if (current_throttle_ > target_throttle_) current_throttle_ = target_throttle_;
                }
                hal_.write_throttle(current_throttle_);
                if (current_throttle_ >= target_throttle_) {
                    transition_to(State::Settle, now);
                }
                break;

            case State::Settle:
                if (elapsed >= limits_.settle_duration) {
                    reset_accumulators();
                    transition_to(State::Acquire, now);
                }
                break;

            case State::Acquire:
                acc_thrust_ += (raw_thrust - pre_tare_offset_g_);
                acc_voltage_ += v;
                acc_current_ += i;
                acc_rpm_ += rpm;
                acc_temp_ += temp_c;
                sample_count_++;

                if (elapsed >= limits_.acquire_duration && sample_count_ > 0) {
                    auto& rec = results_[current_step_idx_];
                    rec.timestamp = now;
                    rec.throttle_pct = current_throttle_;
                    rec.thrust_grams = acc_thrust_ / static_cast<float>(sample_count_);
                    rec.voltage_v = acc_voltage_ / static_cast<float>(sample_count_);
                    rec.current_a = acc_current_ / static_cast<float>(sample_count_);
                    rec.power_w = rec.voltage_v * rec.current_a;
                    rec.rpm = acc_rpm_ / static_cast<float>(sample_count_);
                    rec.temp_c = acc_temp_ / static_cast<float>(sample_count_);
                    rec.eff_grams_per_watt = (rec.power_w > 0.05f) ? (rec.thrust_grams / rec.power_w) : 0.0f;

                    hal_.stream_record(rec);

                    current_step_idx_++;
                    if (current_step_idx_ < total_steps_) {
                        target_throttle_ = static_cast<float>(current_step_idx_ * limits_.step_increment_pct);
                        if (target_throttle_ > 100.0f) target_throttle_ = 100.0f;
                        transition_to(State::Ramp, now);
                    } else {
                        hal_.write_throttle(0.0f);
                        current_throttle_ = 0.0f;
                        reset_accumulators();
                        transition_to(State::PostTare, now);
                    }
                }
                break;

            case State::PostTare:
                acc_thrust_ += raw_thrust;
                acc_temp_ += temp_c;
                sample_count_++;
                if (elapsed >= std::chrono::milliseconds{1500} && sample_count_ > 0) {
                    post_tare_offset_g_ = acc_thrust_ / static_cast<float>(sample_count_);
                    end_temp_c_ = acc_temp_ / static_cast<float>(sample_count_);
                    transition_to(State::Cooldown, now);
                }
                break;

            case State::Cooldown:
                if (elapsed >= std::chrono::seconds{10}) {
                    transition_to(State::Idle, now);
                }
                break;
        }
    }

    [[nodiscard]] constexpr auto get_state() const noexcept -> State { return state_; }
    [[nodiscard]] constexpr auto get_abort_reason() const noexcept -> AbortReason { return abort_reason_; }
    [[nodiscard]] auto get_results() const noexcept -> std::span<const BenchRecord> {
        return {results_.data(), current_step_idx_};
    }

private:
    void transition_to(State next, std::chrono::milliseconds now) noexcept {
        state_ = next;
        state_entry_time_ = now;
    }

    void reset_accumulators() noexcept {
        acc_thrust_ = 0.0f;
        acc_voltage_ = 0.0f;
        acc_current_ = 0.0f;
        acc_rpm_ = 0.0f;
        acc_temp_ = 0.0f;
        sample_count_ = 0;
    }

    bool check_safety(float v, float i, float thrust, float rpm, float temp) noexcept {
        if (i > limits_.max_current_a) {
            abort_test(AbortReason::Overcurrent);
            return false;
        }
        if (temp > limits_.max_temp_c) {
            abort_test(AbortReason::Overheat);
            return false;
        }
        if (current_throttle_ > 25.0f && rpm < 300.0f && i > 2.5f) {
            abort_test(AbortReason::MotorStall);
            return false;
        }
        if (current_throttle_ > 30.0f && thrust < -25.0f) {
            abort_test(AbortReason::ReverseThrust);
            return false;
        }
        return true;
    }

    BenchLimits limits_;
    IHardwareDriver& hal_;
    State state_{State::Idle};
    AbortReason abort_reason_{AbortReason::None};
    
    size_t current_step_idx_{0};
    size_t total_steps_{MaxSteps};
    float target_throttle_{0.0f};
    float current_throttle_{0.0f};
    
    std::chrono::milliseconds state_entry_time_{0};
    float pre_tare_offset_g_{0.0f};
    float post_tare_offset_g_{0.0f};
    float start_temp_c_{25.0f};
    float end_temp_c_{25.0f};
    
    std::array<BenchRecord, MaxSteps> results_{};
    
    float acc_thrust_{0.0f};
    float acc_voltage_{0.0f};
    float acc_current_{0.0f};
    float acc_rpm_{0.0f};
    float acc_temp_{0.0f};
    size_t sample_count_{0};
};

} // namespace thrust_rig
```
:::
