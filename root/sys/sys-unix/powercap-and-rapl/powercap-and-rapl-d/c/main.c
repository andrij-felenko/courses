struct powercap_zone {
    struct device dev;
    struct powercap_zone *parent;
    const struct powercap_zone_ops *ops;
    const struct powercap_zone_constraint_ops *const_ops;
    int nr_constraints;
    struct powercap_control_type *control_type;
    void *allocated_zone_name;
    void *drv_data;
};
