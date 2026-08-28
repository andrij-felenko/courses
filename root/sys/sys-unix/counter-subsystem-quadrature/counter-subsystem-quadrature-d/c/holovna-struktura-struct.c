struct counter_device {
    const char *name;
    struct device *parent;
    const struct counter_ops *ops;
    
    struct counter_signal *signals;
    size_t num_signals;
    
    struct counter_count *counts;
    size_t num_counts;
    
    struct counter_ext *ext;
    size_t num_ext;
    
    void *priv;
};
