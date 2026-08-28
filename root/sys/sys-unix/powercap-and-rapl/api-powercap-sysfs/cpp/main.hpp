#include <linux/powercap.h>

// Концептуальні C++ сигнатури для розробки обгорток ядра та тестових модулів

extern "C" {

struct powercap_zone_ops {
    int (*get_energy_uj)(struct powercap_zone *zone, u64 *energy_uj);
    int (*reset_energy_uj)(struct powercap_zone *zone);
    int (*get_max_energy_range_uj)(struct powercap_zone *zone, u64 *max_uj);
    int (*get_power_uw)(struct powercap_zone *zone, u64 *power_uw);
    int (*set_enable)(struct powercap_zone *zone, bool mode);
    int (*get_enable)(struct powercap_zone *zone, bool *mode);
    int (*release)(struct powercap_zone *zone);
};

struct powercap_zone_constraint_ops {
    int (*set_power_limit_uw)(struct powercap_zone *zone, int cid, u64 power_uw);
    int (*get_power_limit_uw)(struct powercap_zone *zone, int cid, u64 *power_uw);
    int (*set_time_window_us)(struct powercap_zone *zone, int cid, u64 time_us);
    int (*get_time_window_us)(struct powercap_zone *zone, int cid, u64 *time_us);
    int (*get_max_power_uw)(struct powercap_zone *zone, int cid, u64 *power_uw);
    int (*get_min_power_uw)(struct powercap_zone *zone, int cid, u64 *power_uw);
    int (*get_max_time_window_us)(struct powercap_zone *zone, int cid, u64 *time_us);
    int (*get_min_time_window_us)(struct powercap_zone *zone, int cid, u64 *time_us);
    const char *(*get_name)(struct powercap_zone *zone, int cid);
};

struct powercap_zone *powercap_register_zone(
    struct powercap_zone *parent,
    struct powercap_control_type *control_type,
    const char *name,
    const struct powercap_zone_ops *ops,
    int nr_constraints,
    const struct powercap_zone_constraint_ops *const_ops
);

int powercap_unregister_zone(
    struct powercap_control_type *control_type,
    struct powercap_zone *zone
);

}
