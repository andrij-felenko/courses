struct devfreq_dev_profile {
    unsigned long initial_freq;
    unsigned int polling_ms;
    int (*target)(struct device *dev, unsigned long *freq, u32 flags);
    int (*get_dev_status)(struct device *dev, struct devfreq_dev_status *stat);
    int (*get_cur_freq)(struct device *dev, unsigned long *freq);
    void (*exit)(struct device *dev);
    unsigned long *freq_table;
    unsigned int max_state;
    bool is_cooling;
};
