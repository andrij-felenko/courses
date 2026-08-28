void NavigationTask::onPeriodicUpdate(float dt_seconds) {
    const auto telemetry = sensor_manager_.getLatestTelemetry();
    
    if (const auto budget = return_estimator_.update(telemetry, dt_seconds)) {
        if (budget->rtl_mandatory) {
            failsafe_controller_.triggerRtl(FailsafeReason::BatteryPointOfNoReturn);
        } else if (budget->state == 1 /* CAUTION */) {
            telemetry_bus_.postWarning("PNR approaching: wind reserve critical");
        }
    } else {
        diagnostics_.reportError("Return budget estimation failed: invalid state");
    }
}
