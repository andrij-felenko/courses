struct pci_dev {
    struct pci_bus  *bus;          /* Вказівник на шину, до якої підключено пристрій */
    unsigned int    devfn;        /* Кодована адреса пристрою та функції (dev<<3 | fn) */
    unsigned short  vendor;       /* 16-бітний Vendor ID (наприклад, 0x10de для NVidia) */
    unsigned short  device;       /* 16-бітний Device ID */
    unsigned short  subsystem_vendor; /* Subsystem Vendor ID */
    unsigned short  subsystem_device; /* Subsystem Device ID */
    unsigned int    class;        /* Class Code (24-бітний клас, підклас та інтерфейс) */
    u8              revision;     /* Ревізія кремнієвого кристала */
    
    struct resource resource[DEVICE_COUNT_RESOURCE]; /* Таблиця ресурсів BAR0-BAR5 та ROM */
    
    unsigned int    irq;          /* Номер системної лінії IRQ (legacy або першого MSI) */
    struct device   dev;          /* Внутрішній об'єкт драйверної моделі ядра Linux */
    
    pci_power_t     current_state;/* Поточний стан живлення (PCI_D0, PCI_D1, PCI_D2, PCI_D3hot, PCI_D3cold) */
    int             cfg_size;     /* Розмір конфігураційного простору (256 B для PCI, 4096 B для PCIe) */
    unsigned int    msi_enabled:1;  /* Прапор увімкнення режиму MSI */
    unsigned int    msix_enabled:1; /* Прапор увімкнення режиму MSI-X */
    unsigned int    is_virtfn:1;    /* Ознака віртуальної функції SR-IOV (VF) */
    atomic_t        enable_cnt;     /* Лічильник повторних викликів pci_enable_device */
};
