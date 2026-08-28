/* C structure for Stream Parameters configuration */
struct sof_ipc_stream_params {
    struct sof_ipc_cmd_hdr hdr;
    uint32_t comp_id;          /* ID Host-компонента в графу DSP */
    uint32_t buffer_fmt;       /* Формат буфера (interleaved / non-interleaved) */
    uint32_t frame_fmt;        /* Формат семплів (S16_LE, S24_LE, S32_LE) */
    uint32_t rate;             /* Частота дискретизації у Гц (наприклад, 48000) */
    uint32_t channels;         /* Кількість каналів (1, 2, 4, 8) */
    uint32_t buffer_size;      /* Загальний розмір ring-буфера в Host DRAM (байти) */
    uint32_t period_size;      /* Розмір одного періоду переривання (байти) */
    uint32_t sample_container_bytes; /* Розмір контейнера семпла у пам'яті (зазвичай 4 байти) */
    uint32_t host_period_bytes;/* Інтервал генерації Host DMA переривань */
    uint16_t reserved[4];      /* Резервні поля вирівнювання */
} __attribute__((packed));
