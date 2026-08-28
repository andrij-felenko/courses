struct virtio_gpu_rect {
    uint32_t x;
    uint32_t y;
    uint32_t width;
    uint32_t height;
};

struct virtio_gpu_resource_create_2d {
    struct virtio_gpu_ctrl_hdr hdr;
    uint32_t resource_id; /* Унікальний ідентифікатор ресурсу, призначений гостем */
    uint32_t format;      /* Формат пікселів (наприклад, VIRTIO_GPU_FORMAT_B8G8R8A8_UNORM) */
    uint32_t width;       /* Ширина у пікселях */
    uint32_t height;      /* Висота у пікселях */
};
