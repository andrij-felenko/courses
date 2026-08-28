struct virtio_pci_common_cfg {
        __le32 device_feature_select;  /* RW: яку половину маски пристрою читаємо  */
        __le32 device_feature;         /* RO                                       */
        __le32 guest_feature_select;   /* RW: яку половину маски драйвера пишемо   */
        __le32 guest_feature;          /* RW                                       */
        __le16 msix_config;            /* RW: вектор MSI-X для змін конфігурації   */
        __le16 num_queues;             /* RO                                       */
        __u8   device_status;          /* RW: байт статусу                         */
        __u8   config_generation;      /* RO                                       */
        __le16 queue_select;           /* RW: далі йдеться про ЦЮ чергу            */
        __le16 queue_size;             /* RW: степінь двійки                       */
        __le16 queue_msix_vector;      /* RW                                       */
        __le16 queue_enable;           /* RW: 1 — черга ввімкнена                  */
        __le16 queue_notify_off;       /* RO: позиція черги в області сповіщень    */
        __le32 queue_desc_lo,   queue_desc_hi;   /* RW: адреса таблиці ланок       */
        __le32 queue_avail_lo,  queue_avail_hi;  /* RW: адреса доступного кільця   */
        __le32 queue_used_lo,   queue_used_hi;   /* RW: адреса ужитого кільця      */
};
