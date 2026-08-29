#pragma once

#include <cstdint>
#include <optional>

#include "contracts.hpp"

// Режим, у якому рушій ухвалив рішення. Потрібен не для керування, а для
// журналу: без нього суха прогонка показує лише «ТЕНи вимкнено», і незрозуміло,
// котре саме правило виграло арбітраж.
enum class EngineMode {
    EmergencyStop,
    SensorFault,
    StaleData,
    PressureFault,
    Overheat,
    PumpPreRun,
    Heating,
    Holding,
};

const char* mode_name(EngineMode m);

struct Decision {
    ActuatorState commands{};
    EngineMode mode{EngineMode::Holding};
};

class BoilerRuleEngine {
public:
    struct Config {
        float temp_target_c{65.0f};           // уставка
        float temp_hysteresis_c{4.0f};         // ширина зони гістерезису під уставкою
        float temp_stage2_deficit_c{15.0f};    // відставання, за якого потрібен другий ТЕН
        float temp_critical_c{95.0f};          // поріг перегріву
        float pressure_min_bar{0.8f};
        float pressure_max_bar{4.0f};
        std::uint32_t pump_pre_run_ms{3000};   // час протоку перед пуском ТЕНів
        int max_stale_reads{3};                // скільки однакових міток часу терпимо
    };

    explicit BoilerRuleEngine(Config cfg) : cfg_(cfg) {}

    // Чиста функція від знімка й внутрішніх засувок: жодного вводу-виводу.
    Decision evaluate(const SensorSnapshot& in);

    void reset();

private:
    void drop_stages();   // скинути засувки ступенів нагріву
    void drop_latches();  // скинути й засувки, і відлік вибігу помпи

    Config cfg_;
    std::optional<std::uint32_t> pump_running_since_ms_{};
    std::optional<std::uint32_t> last_timestamp_ms_{};
    int stale_reads_{0};
    bool stage1_active_{false};
    bool stage2_active_{false};
};
