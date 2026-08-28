struct vdpa_config_ops {
    /* Налаштування зв'язку з IOMMU та апаратними ASID */
    int (*set_map)(struct vdpa_device *vdev, u32 asid, struct vhost_iotlb *iotlb);
    int (*dma_map)(struct vdpa_device *vdev, u32 asid, u64 iova, u64 size, u64 pa, u32 perm);
    int (*dma_unmap)(struct vdpa_device *vdev, u32 asid, u64 iova, u64 size);

    /* Опитування та зміна стану virtqueue (потрібно для Live Migration) */
    int (*get_vq_state)(struct vdpa_device *vdev, u16 idx, struct vdpa_vq_state *state);
    int (*set_vq_state)(struct vdpa_device *vdev, u16 idx, const struct vdpa_vq_state *state);

    /* Ініціалізація структур ring адресації */
    void (*set_vq_address)(struct vdpa_device *vdev, u16 idx,
                           u64 desc_area, u64 driver_area, u64 device_area);
    void (*set_vq_num)(struct vdpa_device *vdev, u16 idx, u32 num);
    void (*kick_vq)(struct vdpa_device *vdev, u16 idx);
    void (*set_vq_cb)(struct vdpa_device *vdev, u16 idx, struct vdpa_callback *cb);
    void (*set_vq_ready)(struct vdpa_device *vdev, u16 idx, bool ready);
    bool (*get_vq_ready)(struct vdpa_device *vdev, u16 idx);

    /* Узгодження прапорів virtio та байтів статусу */
    u64 (*get_device_features)(struct vdpa_device *vdev);
    int (*set_driver_features)(struct vdpa_device *vdev, u64 features);
    u8 (*get_status)(struct vdpa_device *vdev);
    void (*set_status)(struct vdpa_device *vdev, u8 status);
    void (*reset)(struct vdpa_device *vdev);

    /* Робота з простором конфігурації пристрою (MAC, MTU, Links) */
    size_t (*get_config_size)(struct vdpa_device *vdev);
    void (*get_config)(struct vdpa_device *vdev, unsigned int offset,
                       void *buf, unsigned int len);
    void (*set_config)(struct vdpa_device *vdev, unsigned int offset,
                       const void *buf, unsigned int len);

    /* Прив'язка групи черг до індексу ASID */
    u32 (*get_vq_group)(struct vdpa_device *vdev, u16 idx);
    int (*set_group_asid)(struct vdpa_device *vdev, u32 group, u32 asid);
};
