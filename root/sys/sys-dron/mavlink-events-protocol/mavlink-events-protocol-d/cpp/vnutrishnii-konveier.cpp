#include <libevents/events.h>

// Типобезпечна публікація події у вихідному коді модуля автопілота
void CompassChecker::checkConsistency(uint8_t instance, float currentDeviation) {
    if (currentDeviation > MaxAllowedDeviationDeg) {
        events::send<uint8_t, float>(
            events::ID("sensors_compass_cal_failed"),
            events::Log::Error,
            instance,
            currentDeviation
        );
    }
}
