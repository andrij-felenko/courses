struct snd_sof_dev {
    struct device *dev;
    spinlock_t ipc_lock;
    struct snd_sof_ipc *ipc;
    
    /* Опис апаратних областей MMIO */
    void __iomem *bar[SOF_MAX_MMIO_BAR_COUNT];
    struct snd_dma_buffer fw_state_buffer;
    
    enum snd_sof_fw_state fw_state;
    struct snd_soc_component *component;
    
    /* Таблиця апаратно-залежних callback-функцій */
    const struct snd_sof_dsp_ops *ops;
    
    /* Контекст топології та підсистеми живлення */
    struct list_head pcm_list;
    struct list_head kcontrol_list;
    struct list_head widget_list;
};
