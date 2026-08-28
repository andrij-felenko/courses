struct snd_sof_dsp_ops {
    int (*run)(struct snd_sof_dev *sdev);
    int (*reset)(struct snd_sof_dev *sdev);
    int (*load_firmware)(struct snd_sof_dev *sdev);
    
    /* Функції обслуговування поштової скриньки IPC */
    int (*send_msg)(struct snd_sof_dev *sdev, struct snd_sof_ipc_msg *msg);
    ipc_irq_handler_t irq_handler;
    
    /* Управління регістрами DMA та Boot */
    int (*block_read)(struct snd_sof_dev *sdev, u32 bar, u32 offset, void *dest, size_t size);
    int (*block_write)(struct snd_sof_dev *sdev, u32 bar, u32 offset, void *src, size_t size);
};
