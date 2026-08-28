enum dev_pm_qos_req_type {
    DEV_PM_QOS_RESUME_LATENCY = 1,
    DEV_PM_QOS_LATENCY_TOLERANCE,
    DEV_PM_QOS_FLAGS,
};

struct dev_pm_qos_request {
    enum dev_pm_qos_req_type type;
    union {
        struct plist_node pnode;
        struct pm_qos_flags_request flr;
    } data;
    struct device *dev;
};

struct dev_pm_qos {
    struct pm_qos_constraints resume_latency;
    struct pm_qos_constraints latency_tolerance;
    struct freq_constraints freq;
    struct pm_qos_flags flags;
    struct dev_pm_qos_request *resume_latency_req;
    struct dev_pm_qos_request *latency_tolerance_req;
    struct dev_pm_qos_request *flags_req;
};
