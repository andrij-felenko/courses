#include <cstdint>
#include <format>
#include <iostream>
#include <limits>
#include <optional>
#include <string_view>
#include <utility>

#include "contracts.hpp"
#include "dry_run_sink.hpp"
#include "fault_injector.hpp"
#include "plant_model.hpp"
#include "rule_engine.hpp"

namespace {

int failures = 0;

void check(bool ok, std::string_view what) {
    std::cout << std::format("  [{}] {}\n", ok ? "OK  " : "ЗБІЙ", what);
    if (!ok) ++failures;
}

std::string_view on_off(bool v) { return v ? "УВІМК" : "ВИМК "; }

}  // namespace

int main() {
    std::cout << "=== SIL-СТЕНД РУШІЯ ПРАВИЛ БОЙЛЕРА ===\n\n";

    BoilerRuleEngine::Config cfg;
    cfg.temp_target_c = 60.0f;
    cfg.temp_hysteresis_c = 5.0f;
    cfg.temp_stage2_deficit_c = 15.0f;
    cfg.pump_pre_run_ms = 2000;

    BoilerRuleEngine engine(cfg);
    PlantModel plant(20.0f, PlantModel::Params{});
    FaultInjector injector(plant);
    DryRunSink sink(DryRunSink::Limits{cfg.pressure_min_bar, cfg.pressure_max_bar,
                                       cfg.temp_critical_c});

    constexpr float dt_s = 0.5f;

    // Один такт стенда: знімок → правила → суха прогонка → крок фізики.
    // Рушій бачить рівно те, що віддав ін'єктор, і монітор судить за тим самим.
    auto tick = [&]() -> std::pair<SensorSnapshot, Decision> {
        const SensorSnapshot in = injector.read_snapshot();
        const Decision d = engine.evaluate(in);
        sink.note_inputs(in, d.mode);
        sink.apply_commands(d.commands, in.timestamp_ms);
        plant.step(d.commands, dt_s);
        return {in, d};
    };

    auto trace = [](const SensorSnapshot& in, const Decision& d) {
        std::cout << std::format(
            "  t={:6.1f} с | T={:5.1f} °C | P={:4.2f} бар | помпа {} | ТЕН1 {} | ТЕН2 {} | {}\n",
            in.timestamp_ms / 1000.0f, in.temperature_c, in.pressure_bar,
            on_off(d.commands.circulation_pump), on_off(d.commands.heater_stage1),
            on_off(d.commands.heater_stage2), mode_name(d.mode));
    };

    // ── Сценарій 1: нормальний перехідний процес ─────────────────────────────
    std::cout << "[СЦЕНАРІЙ 1] Нагрів теплоносія від 20 до 60 °C\n";

    std::optional<std::uint32_t> first_heat_ms;
    std::optional<float> stage2_off_c;
    std::optional<float> stage1_off_c;
    bool prev_stage1 = false;
    bool prev_stage2 = false;

    for (int i = 0; i < 2400 && !stage1_off_c; ++i) {
        const auto [in, d] = tick();
        if (!first_heat_ms && heaters_on(d.commands)) {
            first_heat_ms = in.timestamp_ms;
        }
        if (prev_stage2 && !d.commands.heater_stage2 && !stage2_off_c) {
            stage2_off_c = in.temperature_c;
        }
        if (prev_stage1 && !d.commands.heater_stage1 && !stage1_off_c) {
            stage1_off_c = in.temperature_c;
        }
        prev_stage1 = d.commands.heater_stage1;
        prev_stage2 = d.commands.heater_stage2;
        if (i % 120 == 0) trace(in, d);
    }

    check(first_heat_ms && *first_heat_ms == cfg.pump_pre_run_ms,
          std::format("ТЕНи ввімкнулись рівно після {} мс прокачування контуру",
                      cfg.pump_pre_run_ms));
    check(stage2_off_c && *stage2_off_c >= 45.0f && *stage2_off_c < 45.5f,
          std::format("другий ступінь знявся на {:.2f} °C (розрахунково 45 °C)",
                      stage2_off_c.value_or(0.0f)));
    check(stage1_off_c && *stage1_off_c >= 60.0f && *stage1_off_c < 60.5f,
          std::format("перший ступінь знявся на {:.2f} °C (уставка 60 °C)",
                      stage1_off_c.value_or(0.0f)));
    check(sink.violations() == 0, "жодного порушення інваріантів безпеки");
    check(plant.dry_heating_steps() == 0, "жодного кроку сухого нагріву у моделі");

    // ── Сценарій 2: миттєве скидання тиску ───────────────────────────────────
    std::cout << "\n[СЦЕНАРІЙ 2] Розгерметизація контуру: тиск падає до 0.3 бар\n";
    sink.reset_counters();

    // Аварію треба ловити на гарячому й під навантаженням: чекаємо, доки
    // гістерезис сам поверне ТЕН у роботу після охолодження бака.
    for (int i = 0; i < 2400 && !sink.last_commands().heater_stage1; ++i) {
        tick();
    }
    check(sink.last_commands().heater_stage1, "перед ін'єкцією нагрів справді увімкнено");

    injector.override_pressure(0.3f);
    for (int i = 0; i < 20; ++i) {
        const auto [in, d] = tick();
        if (i < 2) trace(in, d);
    }

    check(!heaters_on(sink.last_commands()), "ТЕНи знеструмлені за падіння тиску");
    check(sink.last_commands().alarm_siren, "сирена увімкнена");
    check(sink.last_mode() == EngineMode::PressureFault, "рушій у режимі аварії тиску");
    check(sink.worst_reaction_ms() == 0,
          "реакція — 0 мс: нагрів знято на тому самому кроці обчислення");
    check(sink.violations() == 0, "монітор не зафіксував небезпечних команд");
    injector.clear_pressure();

    // ── Сценарій 3: некоректні числові дані й мертва шина ────────────────────
    std::cout << "\n[СЦЕНАРІЙ 3] Обрив АЦП: у показі температури NaN\n";
    sink.reset_counters();

    injector.override_temperature(std::numeric_limits<float>::quiet_NaN());
    for (int i = 0; i < 10; ++i) tick();

    check(!heaters_on(sink.last_commands()), "ТЕНи вимкнені за NaN у вимірюванні");
    check(sink.last_commands().alarm_siren, "сирена увімкнена");
    check(sink.last_mode() == EngineMode::SensorFault,
          "рушій пішов у режим відмови вимірювача, а не провалив порівняння");
    injector.clear_temperature();

    // Той самий обрив, але тихий: числа лишились правдоподібні, мертва лише мітка часу.
    std::cout << "  Той самий обрив без NaN: опитування завмерло\n";
    for (int i = 0; i < 4; ++i) tick();  // даємо контуру повернутись у роботу
    injector.freeze(true);
    for (int i = 0; i < cfg.max_stale_reads + 1; ++i) tick();

    check(sink.last_mode() == EngineMode::StaleData,
          "сторож упіймав завмерлу мітку часу й звів систему в безпечний стан");
    check(!heaters_on(sink.last_commands()), "ТЕНи вимкнені за застарілих даних");
    injector.freeze(false);

    std::cout << std::format("\n=== ПІДСУМОК: провалено перевірок — {} ===\n", failures);
    return failures == 0 ? 0 : 1;
}
