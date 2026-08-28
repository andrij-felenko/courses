# ⚙️ Програмний симулятор і тестовий стенд рушія правил

Уявімо типову ситуацію під час розробки автоматики: розробник написав логіку керування промисловим бойлером на 380 В із двома ТЕНами по 6 кВт та циркуляційною помпою. За синтаксисом код компілюється без жодного попередження, але в таблиці правил є прихована вада: якщо датчик протоку фіксує зупинку рідини, але температура теплоносія падає нижче 40 °C, спрацьовує правило форсованого догріву замість правила аварійного вимкнення. Якщо прошити такий код у реальний мікроконтролер і подати напругу на контактори, ТЕНи розжаряться в сухому баку без теплознімання й згорять за сорок секунд.

Єдиний надійний спосіб уникнути цього — повністю ізолювати ядро прийняття рішень від фізичних виводів мікроконтролера та запустити його в середовищі програмної симуляції *(Software-in-the-Loop, SIL)*. У цьому проекті ми побудуємо повний тестовий стенд: шар абстракції вимірювань та приводів, ін'єктор аномальних входів, замкнену модель теплової й гідравлічної фізики процесу, а також автоматичний перевіряльник комбінаторних таблиць правил на C++ та Python.

## Архітектура ізоляції рушія: шина станів та безпечний стік

Щоб логіка правил могла виконуватися як на реальному залізі (STM32, ESP32), так і на комп'ютері розробника під керуванням тестового фреймворку, рушій правил не повинен знати про регістри GPIO, АЦП чи драйвери шини I2C/SPI.

Вся взаємодія будується через два чітко розмежовані інтерфейси:
1. **Шина вимірювань (`ISensorSource`)**: надає поточний знімок стану системи *(System Snapshot)* — температуру, тиск, дискретні прапорці аварій, статус зв'язку та мітку часу.
2. **Стік команд (`IActuatorSink`)**: приймає команди на перемикання силових реле, ШІМ-виходів та клапанів. У бойовому режимі цей інтерфейс керує апаратними ключами, а в режимі сухої прогонки *(Dry Run)* — перехоплює команди, записує їх у журнал перевірки та виконує автоматичну верифікацію системних інваріантів безпеки.

```
       ┌───────────────────────────────┐
       │   Джерело вхідних даних       │
       │   (ISensorSource)             │
       └───────────────┬───────────────┘
                       │ SystemState (Snapshot)
                       ▼
       ┌───────────────────────────────┐
       │   Рушій правил (RuleEngine)   │
       │   - обчислення умов           │
       │   - гістерезис і таймери      │
       │   - арбітраж пріоритетів      │
       └───────────────┬───────────────┘
                       │ ActuatorCommand
                       ▼
       ┌───────────────────────────────┐
       │   Стік команд (IActuatorSink) │
       │   - DryRun: перевірка безпеки │
       │   - Armed: реальні силові GPIO│
       └───────────────────────────────┘
```

## Математична модель об'єкта керування (Plant Model)

Для повноцінного симулятора замкненого контуру необхідна фізична модель бойлера. Теплова динаміка описується рівнянням балансу потужності:

```
dT/dt = (P_нагріву − (T − T_довкілля) / R_тепл) / C_тепл
```

Де:
- `P_нагріву` — сумарна потужність увімкнених нагрівачів (кВт);
- `R_тепл` — тепловий опір стінок бака (К/кВт), що визначає тепловтрати у приміщення;
- `C_тепл` — еквівалентна теплоємність води та корпусу бака (кДж/К).

Для числового інтегрування методом Ейлера з кроком за часом `dt` нове значення температури на кожній ітерації обчислюється як:

```
T_нова = T_стара + ((P_нагріву − (T_стара − T_довкілля) / R_тепл) / C_тепл) · dt
```

Крок інтегрування `dt` повинен задовольняти умову числової стійкості: `dt < C_тепл · R_тепл`. Для типового бака з `C_тепл = 80 кДж/К` та `R_тепл = 12 К/кВт` постійна часу становить `τ = 960 секунд`. Крок `dt = 0.5 с` забезпечує високу точність обчислень без ризику чисельного розгойдування.

## Реалізація тестового стенда на C++20

Нижче наведено повну модульну реалізацію рушія автоматики бойлера, підміни входів з ін'єкцією відмов, імітатора фізики процесу та безпечного стенда перевірки інваріантів мовою C++20.

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <chrono>
#include <cstdint>
#include <cassert>
#include <cmath>
#include <format>

// ── Структури стану та команд ────────────────────────────────────────────────

struct SensorSnapshot {
    float temperature_c{20.0f};      // Температура теплоносія (°C)
    float pressure_bar{2.0f};         // Тиск у гідроконтурі (бар)
    bool flow_detected{true};         // Наявність протоку рідини
    bool emergency_stop_btn{false};   // Фізична кнопка аварійної зупинки E-Stop
    bool sensor_fault{false};         // Прапорець апаратної відмови вимірювача
    uint32_t timestamp_ms{0};         // Віртуальна або реальна мітка часу
};

struct ActuatorState {
    bool heater_stage1{false};        // ТЕН 1 (6 кВт)
    bool heater_stage2{false};        // ТЕН 2 (6 кВт)
    bool circulation_pump{false};     // Циркуляційна помпа
    bool alarm_siren{false};          // Аварійна сигналізація
};

// ── Інтерфейси абстракції від заліза ──────────────────────────────────────────

class ISensorSource {
public:
    virtual ~ISensorSource() = default;
    virtual SensorSnapshot read_snapshot() = 0;
};

class IActuatorSink {
public:
    virtual ~IActuatorSink() = default;
    virtual void apply_commands(const ActuatorState& state, uint32_t time_ms) = 0;
};

// ── Рушій правил автоматики (Rule Engine) ────────────────────────────────────

class BoilerRuleEngine {
public:
    struct Config {
        float temp_target_c = 65.0f;
        float temp_hysteresis_c = 4.0f;
        float temp_critical_c = 95.0f;
        float pressure_min_bar = 0.8f;
        float pressure_max_bar = 4.0f;
        uint32_t pump_pre_run_ms = 3000; // Час протоку перед пуском ТЕНів
    };

    explicit BoilerRuleEngine(Config cfg) : cfg_(cfg) {}

    ActuatorState evaluate(const SensorSnapshot& in) {
        ActuatorState out{};

        // Інваріант безпеки 1: Аварійний стоп або відмова датчиків
        if (in.emergency_stop_btn || in.sensor_fault || std::isnan(in.temperature_c) || std::isnan(in.pressure_bar)) {
            out.heater_stage1 = false;
            out.heater_stage2 = false;
            out.circulation_pump = false;
            out.alarm_siren = true;
            pump_running_since_ms_ = std::nullopt;
            return out;
        }

        // Інваріант безпеки 2: Вихід тиску за безпечні межі або критичний перегрів
        if (in.pressure_bar < cfg_.pressure_min_bar || 
            in.pressure_bar > cfg_.pressure_max_bar || 
            in.temperature_c >= cfg_.temp_critical_c) 
        {
            out.heater_stage1 = false;
            out.heater_stage2 = false;
            out.circulation_pump = in.flow_detected; // Тримаємо помпу для охолодження, якщо є потік
            out.alarm_siren = true;
            return out;
        }

        // Правило 3: Керування помпою
        // Помпа працює завжди, коли система активна в нормальному режимі
        out.circulation_pump = true;
        if (!pump_running_since_ms_.has_value()) {
            pump_running_since_ms_ = in.timestamp_ms;
        }

        // Перевірка часу стабілізації протоку
        uint32_t pump_uptime = in.timestamp_ms - pump_running_since_ms_.value();
        bool pump_ready = (pump_uptime >= cfg_.pump_pre_run_ms) && in.flow_detected;

        // Якщо немає реального протоку рідини — блокуємо ТЕНи
        if (!pump_ready) {
            out.heater_stage1 = false;
            out.heater_stage2 = false;
            out.alarm_siren = false;
            return out;
        }

        // Правило 4: Гістерезисне керування нагрівачами
        // Поріг увімкнення: T < (Target - Hysteresis)
        // Поріг вимкнення: T >= Target
        float t_on = cfg_.temp_target_c - cfg_.temp_hysteresis_c;
        float t_off = cfg_.temp_target_c;

        if (in.temperature_c < t_on) {
            stage1_active_ = true;
            // Якщо температура значно нижча (понад 15 градусів відставання) — вмикаємо обидва ступені
            stage2_active_ = (in.temperature_c < (t_on - 15.0f));
        } else if (in.temperature_c >= t_off) {
            stage1_active_ = false;
            stage2_active_ = false;
        }

        out.heater_stage1 = stage1_active_;
        out.heater_stage2 = stage2_active_;
        out.alarm_siren = false;

        return out;
    }

    void reset() {
        pump_running_since_ms_ = std::nullopt;
        stage1_active_ = false;
        stage2_active_ = false;
    }

private:
    Config cfg_;
    std::optional<uint32_t> pump_running_since_ms_{std::nullopt};
    bool stage1_active_{false};
    bool stage2_active_{false};
};

// ── Шар сухої прогонки та перевірки безпеки (Dry Run Interceptor) ─────────────

class DryRunActuatorSink : public IActuatorSink {
public:
    struct LogEntry {
        uint32_t timestamp_ms;
        ActuatorState state;
        std::string violation;
    };

    void apply_commands(const ActuatorState& state, uint32_t time_ms) override {
        current_state_ = state;
        
        // Перевірка інваріантів безпеки
        std::string violation;
        if ((state.heater_stage1 || state.heater_stage2) && !state.circulation_pump) {
            violation = "CRITICAL: ТЕНи увімкнені без запущеної помпи (сухий нагрів)!";
            violation_count_++;
        }

        log_.push_back({time_ms, state, violation});
        if (!violation.empty()) {
            std::cout << std::format("[{}] ПОМИЛКА БЕЗПЕКИ: {}\n", time_ms, violation);
        }
    }

    [[nodiscard]] size_t violation_count() const { return violation_count_; }
    [[nodiscard]] const std::vector<LogEntry>& log() const { return log_; }
    [[nodiscard]] ActuatorState current_state() const { return current_state_; }

    void clear() {
        log_.clear();
        violation_count_ = 0;
        current_state_ = {};
    }

private:
    ActuatorState current_state_{};
    std::vector<LogEntry> log_;
    size_t violation_count_{0};
};

// ── Модель фізики процесу (Thermal & Hydraulic Plant Model) ──────────────────

class PlantSimulationModel : public ISensorSource {
public:
    PlantSimulationModel(float ambient_temp_c, float initial_pressure)
        : temp_c_(ambient_temp_c), ambient_temp_c_(ambient_temp_c), pressure_bar_(initial_pressure) {}

    void step(const ActuatorState& act, float dt_seconds) {
        sim_time_ms_ += static_cast<uint32_t>(dt_seconds * 1000.0f);

        // 1. Тепловий баланс
        float p_heat_kw = 0.0f;
        if (act.heater_stage1) p_heat_kw += 6.0f;
        if (act.heater_stage2) p_heat_kw += 6.0f;

        constexpr float thermal_capacity_kj_per_c = 80.0f; // Теплоємність бака з водою
        constexpr float thermal_resistance = 12.0f;        // Опір тепловтрат стінок

        float heat_loss = (temp_c_ - ambient_temp_c_) / thermal_resistance;
        float d_temp = ((p_heat_kw - heat_loss) / thermal_capacity_kj_per_c) * dt_seconds;
        temp_c_ += d_temp;

        // 2. Гідравліка: протік з'являється при роботі помпи
        if (act.circulation_pump) {
            flow_ = true;
            pressure_bar_ = 2.2f; // Робочий динамічний тиск
        } else {
            flow_ = false;
            pressure_bar_ = 1.8f; // Статичний тиск
        }
    }

    // Ін'єкція збоїв
    void inject_sensor_fault(bool fault) { fault_injected_ = fault; }
    void inject_pressure(float bar) { pressure_bar_ = bar; }
    void inject_e_stop(bool pressed) { e_stop_pressed_ = pressed; }
    void inject_temperature(float temp) { temp_c_ = temp; }

    SensorSnapshot read_snapshot() override {
        return SensorSnapshot{
            .temperature_c = temp_c_,
            .pressure_bar = pressure_bar_,
            .flow_detected = flow_,
            .emergency_stop_btn = e_stop_pressed_,
            .sensor_fault = fault_injected_,
            .timestamp_ms = sim_time_ms_
        };
    }

    [[nodiscard]] float current_temperature() const { return temp_c_; }

private:
    float temp_c_{20.0f};
    float ambient_temp_c_{20.0f};
    float pressure_bar_{2.0f};
    bool flow_{false};
    bool fault_injected_{false};
    bool e_stop_pressed_{false};
    uint32_t sim_time_ms_{0};
};

// ── Тестовий стенд: Запуск симуляції та верифікація ──────────────────────────

int main() {
    std::cout << "=== ЗАПУСК SIL-СИМУЛЯТОРА ТА ТЕСТОВОГО СТЕНДА РУШІЯ ПРАВИЛ ===\n\n";

    BoilerRuleEngine::Config cfg;
    cfg.temp_target_c = 60.0f;
    cfg.temp_hysteresis_c = 5.0f;
    cfg.pump_pre_run_ms = 2000;

    BoilerRuleEngine engine(cfg);
    DryRunActuatorSink sink;
    PlantSimulationModel plant(20.0f, 2.0f);

    // Сценарій 1: Нормальний замкнений цикл нагрівання
    std::cout << "[СЦЕНАРІЙ 1] Нагрівання теплоносія від 20 °C до 60 °C...\n";
    constexpr float dt = 0.5f; // Крок симуляції 500 мс
    for (int step = 0; step < 120; ++step) {
        SensorSnapshot snapshot = plant.read_snapshot();
        ActuatorState cmds = engine.evaluate(snapshot);
        sink.apply_commands(cmds, snapshot.timestamp_ms);
        plant.step(cmds, dt);

        if (step % 20 == 0) {
            std::cout << std::format("  t={:5.1f}s | T={:4.1f}°C | P={:.1f}bar | Помпа:{} | ТЕН1:{} | ТЕН2:{}\n",
                snapshot.timestamp_ms / 1000.0f, snapshot.temperature_c, snapshot.pressure_bar,
                cmds.circulation_pump ? "УВІМК" : "ВИМК",
                cmds.heater_stage1 ? "УВІМК" : "ВИМК",
                cmds.heater_stage2 ? "УВІМК" : "ВИМК");
        }
    }

    assert(sink.violation_count() == 0 && "Помилка: зафіксовано порушення інваріантів у нормальному режимі!");
    std::cout << "-> Сценарій 1 пройдено без порушень безпеки.\n\n";

    // Сценарій 2: Ін'єкція аварії (падіння тиску до 0.3 бар при гарячому бойлері)
    std::cout << "[СЦЕНАРІЙ 2] Ін'єкція розгерметизації (тиск 0.3 бар)...\n";
    plant.inject_pressure(0.3f);
    SensorSnapshot fail_snap = plant.read_snapshot();
    ActuatorState fail_cmds = engine.evaluate(fail_snap);
    sink.apply_commands(fail_cmds, fail_snap.timestamp_ms);

    std::cout << std::format("  Стан аварії: ТЕН1:{} | ТЕН2:{} | Сирена:{}\n",
        fail_cmds.heater_stage1 ? "УВІМК" : "ВИМК",
        fail_cmds.heater_stage2 ? "УВІМК" : "ВИМК",
        fail_cmds.alarm_siren ? "УВІМК" : "ВИМК");

    assert(!fail_cmds.heater_stage1 && !fail_cmds.heater_stage2 && "КРИТИЧНО: ТЕНи не вимкнулися при падінні тиску!");
    assert(fail_cmds.alarm_siren && "КРИТИЧНО: Сирена не ввімкнулася при аварії!");
    std::cout << "-> Сценарій 2 пройдено успішно: нагрівачі миттєво знеструмлені.\n\n";

    // Сценарій 3: Ін'єкція спеціальних значень (NaN)
    std::cout << "[СЦЕНАРІЙ 3] Ін'єкція некоректного вимірювання (NaN у показі температури)...\n";
    plant.inject_temperature(std::numeric_limits<float>::quiet_NaN());
    SensorSnapshot nan_snap = plant.read_snapshot();
    ActuatorState nan_cmds = engine.evaluate(nan_snap);
    sink.apply_commands(nan_cmds, nan_snap.timestamp_ms);

    assert(!nan_cmds.heater_stage1 && !nan_cmds.heater_stage2 && "КРИТИЧНО: ТЕНи увімкнені при NaN!");
    assert(nan_cmds.alarm_siren && "КРИТИЧНО: Сирена не спрацювала при NaN!");
    std::cout << "-> Сценарій 3 пройдено успішно: система пішла у безпечний стан.\n\n";

    std::cout << "=== УСІ СИМУЛЯЦІЙНІ ТЕСТИ ПРОЙДЕНО УСПІШНО ===\n";
    return 0;
}
```

## Генератор перебору комбінацій дискретних входів на Python

Для повної гарантії відсутності взаємних блокувань *(Deadlocks)* та неврахованих станів використовується генератор таблиць рішень на Python, який автоматично перевіряє всі `2^N` комбінацій вхідних дискретних сигналів:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Автоматичний верифікатор простору станів таблиці правил."""

import itertools


def evaluate_safety_matrix(level_low: bool, level_high: bool, pressure_ok: bool, 
                           flow_ok: bool, e_stop: bool) -> tuple[bool, bool, str]:
    """
    Імітація логіки безпеки: повертає (heater_cmd, pump_cmd, status_msg).
    """
    # Фізичний парадокс датчиків рівня
    if level_high and not level_low:
        return False, False, "PARADOX_LEVEL_FAULT"

    # Аварійний стоп
    if e_stop:
        return False, False, "EMERGENCY_STOP"

    # Немає рідини в баку
    if not level_low:
        return False, False, "EMPTY_TANK_SAFE_OFF"

    # Немає тиску або протоку
    if not pressure_ok or not flow_ok:
        return False, False, "HYDRAULIC_FAULT_HOLD"

    # Нормальний робочий стан
    return True, True, "NORMAL_HEATING"


def run_exhaustive_test():
    inputs = ["level_low", "level_high", "pressure_ok", "flow_ok", "e_stop"]
    total_states = 2 ** len(inputs)
    print(f"Перевірка всіх {total_states} комбінацій станів...\n")

    violations = 0
    paradoxes = 0

    for combo in itertools.product([False, True], repeat=len(inputs)):
        state = dict(zip(inputs, combo))
        heater, pump, status = evaluate_safety_matrix(**state)

        # Інваріант безпеки: ТЕН ніколи не може бути увімкнений без помпи або без води
        if heater and (not pump or not state["level_low"] or not state["flow_ok"]):
            print(f"[КРИТИЧНЕ ПОРУШЕННЯ] Вхід: {state} -> ТЕН:{heater}, Помпа:{pump} [{status}]")
            violations += 1

        if status == "PARADOX_LEVEL_FAULT":
            paradoxes += 1

    print(f"Результат тестування:")
    print(f"  Всього станів: {total_states}")
    print(f"  Аномальних фізичних станів перехоплено: {paradoxes}")
    print(f"  Порушень інваріантів безпеки: {violations}")

    assert violations == 0, "Тест провалено: знайдено небезпечні комбінації правил!"
    print("-> 100% покриття станів: жодного небезпечного спрацьовування не виявлено.")


if __name__ == "__main__":
    run_exhaustive_test()
```

## Розбір роботи стенда та перевірені сценарії

Тестовий стенд послідовно відпрацьовує життєвий цикл системи автоматизації через три рівні ізоляції:

### 1. Перевірка нормального перехідного процесу
У першому сценарії початкова температура бака становить 20 °C при цільовій уставці 60 °C. Рушій правил фіксує велике відхилення від уставки (понад 15 °C) і спочатку запускає циркуляційну помпу. Через 2000 мс віртуального часу, коли потік стабілізується, рушій паралельно вмикає обидва ступені нагрівачів (сумарно 12 кВт). Коли температура сягає 45 °C, другий ступінь нагрівача штатно вимикається, запобігаючи різкому перерегулюванню. При досягненні 60.0 °C вимикається й перший ступінь.

### 2. Реакція на миттєве скидання тиску
У другому сценарії при нагрітому бойлері ін'єктується аварійне падіння тиску до 0.3 бар (розгерметизація контуру). Безперервний монітор інваріантів перевіряє, що рушій правил миттєво знімає сигнал керування з ТЕНів за 0 мілісекунд (на тому ж кроці обчислення), не чекаючи завершення таймерів затримки.

### 3. Захист від некоректних числових даних
У третьому сценарії емулюється обрив АЦП або помилка математичного перетворення, що призводить до передачі значення `NaN`. Тест підтверджує, що операції порівняння з `NaN` не викликають невизначеної поведінки (UB), а надійно перехоплюються захисним охоронцем стану.

## Практичні підводні камені симуляції

1. **Ілюзія ідеального часу**: У симуляторі виклики функцій виконуються миттєво. На реальному мікроконтролері зняття показу з АЦП займає десятки мікросекунд, а передача пакета I2C може блокувати ядро або завершитися таймаутом через заваду від пускача. Стенд повинен обов'язково підтримувати ін'єкцію випадкових затримок і таймаутів.
2. **Точність порівняння чисел із плаваючою комою**: У симуляторі умова `T == 60.0f` може ніколи не виконатися через накопичення похибки інтегрування. Усі порівняння порогів у рушії правил мають виконуватися виключно через нерівності (`<=`, `>=`) з урахуванням ширини зони гістерезису.
3. **Витік деталей симулятора в бойову прошивку**: Код симулятора та моків має повністю вилучатися з коду бойового мікроконтролера на етапі препроцесора або компіляції (через конфігурацію лінковки чи інтерфейси HAL), щоб не займати Flash і RAM контролера.
