struct virtio_pci_common_cfg {
    /* Конфігурація Feature Bits */
    uint32_t device_feature_select; /* Читання/Запис: вибір селектора 32-біт слова фіч пристрою (0 або 1) */
    uint32_t device_feature;        /* Читання: 32-бітне слово маски фіч пристрою */
    uint32_t driver_feature_select; /* Запис: вибір селектора фіч драйвера */
    uint32_t driver_feature;        /* Запис: 32-бітне слово узгоджених фіч драйвера */

    /* Конфігурація MSI-X та статусу */
    uint16_t config_msix_vector;    /* Вектор MSI-X для сповіщень про зміну конфігурації */
    uint16_t num_queues;            /* Читання: максимальна кількість доступних черг */
    uint8_t  device_status;         /* Байт статусу пристрою (Device Status Field) */
    uint8_t  config_generation;     /* Лічильник змін конфігураційного простору */

    /* Селектор та параметри віртуальної черги (Virtqueue) */
    uint16_t queue_select;          /* Запис: вибір індексу черги (0..num_queues-1) */
    uint16_t queue_size;            /* Читання/Запис: розмір вибраної черги (N) */
    uint16_t queue_msix_vector;     /* Запис: вектор MSI-X для цієї черги */
    uint16_t queue_enable;          /* Запис: 1 для активації черги */
    uint16_t queue_notify_off;      /* Читання: зсув дверного дзвоника у NOTIFY_CFG */
    uint64_t queue_desc;            /* Запис: 64-бітна фізична адреса Descriptor Table */
    uint64_t queue_driver;          /* Запис: 64-бітна фізична адреса Available Ring */
    uint64_t queue_device;          /* Запис: 64-бітна фізична адреса Used Ring */
    uint16_t queue_notif_config_data;/* Дані для надсилання дверного дзвоника (v1.2) */
    uint16_t queue_reset;           /* Скидання конкретної черги (v1.2) */
};
