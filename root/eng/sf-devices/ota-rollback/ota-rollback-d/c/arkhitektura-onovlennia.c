typedef struct {
    uint32_t header;           /* Тег заголовка IVT (0x402000D1) */
    uint32_t entry;            /* Адреса точки входу Reset_Handler */
    uint32_t reserved1;
    uint32_t dcd;              /* Вказівник на таблицю конфігурації периферії DCD */
    uint32_t boot_data;        /* Вказівник на структуру Boot Data (розмір та адреса) */
    uint32_t self;             /* Абсолютна адреса самої структури IVT */
    uint32_t csf;              /* Вказівник на файл команд безпеки CSF (підписи, сертифікати) */
    uint32_t reserved2;
} ivt_t;
