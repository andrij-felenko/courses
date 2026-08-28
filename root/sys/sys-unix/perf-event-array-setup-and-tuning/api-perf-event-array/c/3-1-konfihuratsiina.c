struct perf_event_attr {
    __u32 type;           /* PERF_TYPE_SOFTWARE */
    __u32 size;           /* sizeof(struct perf_event_attr) */
    __u64 config;         /* PERF_COUNT_SW_BPF_OUTPUT */
    __u64 sample_period;  /* 1 (вибірка кожної події) */
    __u64 sample_type;    /* PERF_SAMPLE_RAW */
    __u64 read_format;    /* Формат зчитаних даних */
    __u64 disabled : 1,   /* Початковий стан: 0 = включено */
          inherit  : 1,   /* Успадкування дочірніми процесами */
          pinned   : 1,   /* Закріплення на CPU */
          exclusive: 1;   /* Ексклюзивний доступ */
    __u32 wakeup_events;  /* Кількість подій для генерації переривання (batching) */
};
