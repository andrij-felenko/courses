struct pci_driver {
    const char *name;                       /* Унікальна назва драйвера у sysfs */
    const struct pci_device_id *id_table;   /* Таблиця підтримуваних ідентифікаторів пристроїв */
    int  (*probe)(struct pci_dev *dev, const struct pci_device_id *id);
    void (*remove)(struct pci_dev *dev);
    int  (*suspend)(struct pci_dev *dev, pm_message_t state);
    int  (*resume)(struct pci_dev *dev);
    void (*shutdown)(struct pci_dev *dev);
    const struct pci_error_handlers *err_handler; /* Колбеки обробки помилок AER */
    int  (*sriov_configure)(struct pci_dev *dev, int num_vfs); /* Налаштування SR-IOV */
    struct device_driver driver;            /* Внутрішній об'єкт для прив'язки в sysfs */
};
