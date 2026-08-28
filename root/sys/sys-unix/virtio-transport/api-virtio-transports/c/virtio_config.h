/* include/linux/virtio_config.h — це реалізує транспорт */
struct virtio_config_ops {
        void (*get)(struct virtio_device *vdev, unsigned offset,
                    void *buf, unsigned len);
        void (*set)(struct virtio_device *vdev, unsigned offset,
                    const void *buf, unsigned len);
        u32  (*generation)(struct virtio_device *vdev);
        u8   (*get_status)(struct virtio_device *vdev);
        void (*set_status)(struct virtio_device *vdev, u8 status);
        void (*reset)(struct virtio_device *vdev);
        int  (*find_vqs)(struct virtio_device *vdev, unsigned int nvqs,
                         struct virtqueue *vqs[],
                         struct virtqueue_info vqs_info[],
                         struct irq_affinity *desc);
        void (*del_vqs)(struct virtio_device *vdev);
        u64  (*get_features)(struct virtio_device *vdev);
        int  (*finalize_features)(struct virtio_device *vdev);
        int  (*set_vq_affinity)(struct virtqueue *vq,
                                const struct cpumask *cpu_mask);
        /* … synchronize_cbs, get_vq_affinity, get_shm_region,
             disable_vq_and_reset, enable_vq_after_reset;
             у свіжих ядрах поруч є get_extended_features —
             маска можливостей переросла 64 біти                */
};
