struct virtio_pci_cap {
    uint8_t  cap_vndr;    /* 0x09: PCI_CAP_ID_VNDR */
    uint8_t  cap_next;    /* Зсув наступної capability у PCI config space */
    uint8_t  cap_len;     /* Загальна довжина цієї capability у байтах */
    uint8_t  cfg_type;    /* Тип структури Virtio (VIRTIO_PCI_CAP_*) */
    uint8_t  bar;         /* Індекс BAR (0..5), у якому розташовані регістри */
    uint8_t  id;          /* Ідентифікатор пристрою (для групування) */
    uint8_t  padding[2];  /* Зарезервовано для вирівнювання на 32-бітний кордон */
    uint32_t offset;      /* Зсув у байтах від початку вказаного BAR */
    uint32_t length;      /* Довжина регіону конфігурації у байтах */
};
