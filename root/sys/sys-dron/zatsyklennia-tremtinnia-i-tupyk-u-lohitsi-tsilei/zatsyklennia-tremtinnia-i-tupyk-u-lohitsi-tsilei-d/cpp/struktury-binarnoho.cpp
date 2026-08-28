#include <cstdint>

namespace drone::telemetry {

struct GoalAnomalyTelemetry {
    uint64_t timestampUs{0};        // Системний час мікроконтролера
    float    inputMetricValue{0.0f};// Поточне значення вимірюваної метрики
    uint16_t activeGoalId{0};       // Ідентифікатор активної цілі місії
    uint16_t suppressedSwitches{0}; // Кількість заблокованих спроб перемикання
    uint8_t  switchingRateHz{0};    // Поточна частота запитів на перемикання (Гц)
    uint8_t  detectedCycleLen{0};   // Довжина зафіксованого N-грамного циклу
    uint8_t  escalationLevel{0};    // Поточний ступінь відновлення (0..4)
    uint8_t  flags{0};              // Бітові прапорці стану фільтра
};

} // namespace drone::telemetry
