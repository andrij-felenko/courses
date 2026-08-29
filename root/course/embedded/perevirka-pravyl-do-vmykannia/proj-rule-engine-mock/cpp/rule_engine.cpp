#include "rule_engine.hpp"

#include <cmath>

namespace {

// Показ поза фізично можливим діапазоном небезпечніший за відсутній: NaN мовчки
// провалює будь-яке порівняння (і `<`, і `>=` дають false), тож ловимо його ДО
// того, як він потрапить у пороги.
bool implausible(float value, float lo, float hi) {
    return !std::isfinite(value) || value < lo || value > hi;
}

}  // namespace

const char* mode_name(EngineMode m) {
    switch (m) {
        case EngineMode::EmergencyStop: return "АВАРІЙНИЙ СТОП";
        case EngineMode::SensorFault:   return "ВІДМОВА ВИМІРЮВАЧА";
        case EngineMode::StaleData:     return "ДАНІ НЕ ОНОВЛЮЮТЬСЯ";
        case EngineMode::PressureFault: return "ТИСК ПОЗА МЕЖАМИ";
        case EngineMode::Overheat:      return "ПЕРЕГРІВ";
        case EngineMode::PumpPreRun:    return "ПРОКАЧУВАННЯ КОНТУРУ";
        case EngineMode::Heating:       return "НАГРІВ";
        case EngineMode::Holding:       return "УТРИМАННЯ УСТАВКИ";
    }
    return "?";
}

Decision BoilerRuleEngine::evaluate(const SensorSnapshot& in) {
    Decision d{};

    // Сторож завмерлого часу. Опитування може обірватися так, що числа лишаться
    // правдоподібними: драйвер віддає останній вдалий знімок, а мітка стоїть.
    if (last_timestamp_ms_ && *last_timestamp_ms_ == in.timestamp_ms) {
        ++stale_reads_;
    } else {
        stale_reads_ = 0;
    }
    last_timestamp_ms_ = in.timestamp_ms;
    const bool stale = stale_reads_ >= cfg_.max_stale_reads;

    // ── Пріоритет 0: даним вірити не можна або людина натиснула «стоп» ──
    const bool bad_input = implausible(in.temperature_c, -40.0f, 200.0f) ||
                           implausible(in.pressure_bar, 0.0f, 16.0f);
    if (in.emergency_stop_btn || in.sensor_fault || bad_input || stale) {
        // Усе, крім сирени, лишається false — це і є безпечний стан.
        d.commands.alarm_siren = true;
        if (in.emergency_stop_btn) {
            d.mode = EngineMode::EmergencyStop;
        } else if (in.sensor_fault || bad_input) {
            d.mode = EngineMode::SensorFault;
        } else {
            d.mode = EngineMode::StaleData;
        }
        drop_latches();
        return d;
    }

    // ── Пріоритет 1: перегрів і гідравліка ──
    if (in.temperature_c >= cfg_.temp_critical_c) {
        // Помпу лишаємо ввімкненою: вона знімає з ТЕНів залишкове тепло.
        d.commands.circulation_pump = true;
        d.commands.alarm_siren = true;
        d.mode = EngineMode::Overheat;
        drop_latches();
        return d;
    }
    if (in.pressure_bar < cfg_.pressure_min_bar || in.pressure_bar > cfg_.pressure_max_bar) {
        // Розгерметизація: качати в дірявий контур немає сенсу, спиняємо все.
        d.commands.alarm_siren = true;
        d.mode = EngineMode::PressureFault;
        drop_latches();
        return d;
    }

    // ── Пріоритет 2: помпа й вибіг перед пуском ТЕНів ──
    d.commands.circulation_pump = true;

    if (!in.flow_detected) {
        // Помпа крутиться, а протоку немає (повітряна пробка, закритий клапан) —
        // відлік починаємо спочатку, щойно протік з'явиться.
        pump_running_since_ms_ = in.timestamp_ms;
        drop_stages();
        d.mode = EngineMode::PumpPreRun;
        return d;
    }
    if (!pump_running_since_ms_) {
        pump_running_since_ms_ = in.timestamp_ms;
    }
    // Різниця беззнакових міток лишається правильною й на переповненні лічильника
    // (uint32 у мілісекундах обертається за 49 діб) — саме тому не віднімаємо у знакових.
    const std::uint32_t pump_uptime_ms = in.timestamp_ms - *pump_running_since_ms_;
    if (pump_uptime_ms < cfg_.pump_pre_run_ms) {
        drop_stages();
        d.mode = EngineMode::PumpPreRun;
        return d;
    }

    // ── Пріоритет 3: гістерезис і два ступені потужності ──
    // Порівнюємо лише нерівностями: рівність із числом із рухомою комою
    // після інтегрування може не настати ніколи.
    const float t_on = cfg_.temp_target_c - cfg_.temp_hysteresis_c;
    const float t_stage2 = cfg_.temp_target_c - cfg_.temp_stage2_deficit_c;

    if (in.temperature_c < t_on) {
        stage1_active_ = true;
    } else if (in.temperature_c >= cfg_.temp_target_c) {
        stage1_active_ = false;
    }
    // Другий ступінь — лише поки відставання від уставки більше за задане;
    // він знімається раніше за перший і тим гасить перерегулювання.
    stage2_active_ = stage1_active_ && (in.temperature_c < t_stage2);

    d.commands.heater_stage1 = stage1_active_;
    d.commands.heater_stage2 = stage2_active_;
    d.mode = stage1_active_ ? EngineMode::Heating : EngineMode::Holding;
    return d;
}

void BoilerRuleEngine::reset() {
    drop_latches();
    last_timestamp_ms_.reset();
    stale_reads_ = 0;
}

void BoilerRuleEngine::drop_stages() {
    stage1_active_ = false;
    stage2_active_ = false;
}

void BoilerRuleEngine::drop_latches() {
    drop_stages();
    pump_running_since_ms_.reset();
}
