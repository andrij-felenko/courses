struct counter_ops {
    int (*signal_read)(struct counter_device *counter,
                       struct counter_signal *signal,
                       enum counter_signal_level *level);
    int (*count_read)(struct counter_device *counter,
                      struct counter_count *count,
                      u64 *val);
    int (*count_write)(struct counter_device *counter,
                       struct counter_count *count,
                       u64 val);
    int (*function_read)(struct counter_device *counter,
                         struct counter_count *count,
                         enum counter_function *function);
    int (*function_write)(struct counter_device *counter,
                          struct counter_count *count,
                          enum counter_function function);
    int (*action_read)(struct counter_device *counter,
                       struct counter_count *count,
                       struct counter_synapse *synapse,
                       enum counter_synapse_action *action);
    int (*action_write)(struct counter_device *counter,
                        struct counter_count *count,
                        struct counter_synapse *synapse,
                        enum counter_synapse_action action);
};
