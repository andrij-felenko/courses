#include <linux/thermal.h>
#include "thermal_core.h"

static void custom_trip_crossed(struct thermal_zone_device *tz,
                                const struct thermal_trip *trip,
                                bool upward)
{
    struct thermal_instance *instance;

    if (trip->type != THERMAL_TRIP_ACTIVE)
        return;

    /* прив'язки «зона — пристрій охолодження», зроблені cooling-maps */
    list_for_each_entry(instance, &tz->thermal_instances, tz_node) {
        if (instance->trip != trip)
            continue;

        instance->target = upward ? instance->upper : instance->lower;
        instance->initialized = true;
        thermal_cdev_update(instance->cdev);
    }
}

static struct thermal_governor thermal_gov_custom = {
    .name         = "custom_gov",
    .trip_crossed = custom_trip_crossed,
};
THERMAL_GOVERNOR_DECLARE(thermal_gov_custom);
