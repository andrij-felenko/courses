enum pm_qos_type {
    PM_QOS_UNITLESS,
    PM_QOS_MAX,   /* агрегат — найбільше зі значень */
    PM_QOS_MIN,   /* агрегат — найменше зі значень */
};

struct pm_qos_constraints {
    struct plist_head list;
    s32 target_value;
    s32 default_value;
    s32 no_constraint_value;
    enum pm_qos_type type;
    struct blocking_notifier_head *notifiers;
};

struct pm_qos_request {
    struct plist_node node;
    struct pm_qos_constraints *qos;
};
