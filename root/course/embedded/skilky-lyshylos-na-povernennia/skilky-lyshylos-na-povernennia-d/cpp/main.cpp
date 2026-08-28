#include "ReturnBudget.hpp"

namespace uav::flight {

void NavigationManager::evaluateReturnBudget(float dt_seconds) {
    const auto telemetry = telemetry_provider_.captureSnapshot();

    if (const auto budget = return_budget_estimator_.update(telemetry, dt_seconds)) {
        if (budget->rtl_mandatory) {
            flight_director_.engageMandatoryRtl(FailsafeSource::BatteryPointOfNoReturn);
        } else if (budget->state == 1 /* CAUTION */) {
            gcs_link_.broadcastWarning("Energy margin low: return path wind degraded");
        }
    } else {
        // Помилка геометрії або критичний вітер: перехід до аварійної стратегії
        flight_director_.engageEmergencyLanding(LandingReason::UnrecoverableWindDrift);
    }
}

} // namespace uav::flight
