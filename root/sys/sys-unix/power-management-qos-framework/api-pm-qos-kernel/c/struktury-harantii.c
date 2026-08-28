enum freq_qos_req_type {
    FREQ_QOS_MIN = 1,
    FREQ_QOS_MAX,
};

struct freq_constraints {
    struct pm_qos_constraints min_freq;
    struct pm_qos_constraints max_freq;
};

struct freq_qos_request {
    enum freq_qos_req_type type;
    struct plist_node pnode;
    struct freq_constraints *qos;
};
