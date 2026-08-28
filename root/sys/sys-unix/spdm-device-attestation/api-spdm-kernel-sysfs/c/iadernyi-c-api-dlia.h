/* Структура стану поштового ящика DOE */
struct pci_doe_mb;

/* Ініціалізація та пошук поштового ящика DOE для вказаного пристрою */
struct pci_doe_mb *pci_find_doe_mailbox(struct pci_dev *pdev, u16 vendor_id, u8 type);

/* Синхронний обмін пакетами через поштовий ящик DOE */
int pci_doe_exchange(struct pci_doe_mb *doe_mb, 
                     const void *request, size_t req_len,
                     void *response, size_t resp_len);

/* Перевірка підтримки конкретного протоколу (наприклад, CMA / SPDM) */
bool pci_doe_supports_prot(struct pci_doe_mb *doe_mb, u16 vendor_id, u8 type);
