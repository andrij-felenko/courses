struct pci_device_id {
    u32 vendor, device;           /* Specific Vendor/Device ID або PCI_ANY_ID */
    u32 subvendor, subdevice;     /* Subsystem Vendor/Device ID або PCI_ANY_ID */
    u32 class, class_mask;        /* Class Code та маска для зіставлення за класом */
    kernel_ulong_t driver_data;   /* Приватне значення драйвера (наприклад, прапорці ревізії) */
};

/* Спеціальний макрос ініціалізації масиву для конкретної пари Vendor/Device */
#define PCI_DEVICE(vend, dev) \
    .vendor = (vend), .device = (dev), \
    .subvendor = PCI_ANY_ID, .subdevice = PCI_ANY_ID

/* Макрос для точного зіставлення із врахуванням підсистеми виробника */
#define PCI_DEVICE_SUB(vend, dev, subvend, subdev) \
    .vendor = (vend), .device = (dev), \
    .subvendor = (subvend), .subdevice = (subdev)

/* Макрос для класифікації пристрою (наприклад, для всіх NVMe контролерів) */
#define PCI_DEVICE_CLASS(dev_class, dev_class_mask) \
    .class = (dev_class), .class_mask = (dev_class_mask), \
    .vendor = PCI_ANY_ID, .device = PCI_ANY_ID, \
    .subvendor = PCI_ANY_ID, .subdevice = PCI_ANY_ID
