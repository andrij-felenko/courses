#include <stdint.h>

typedef struct __attribute__((packed)) {
    uint8_t  bLength;             /* Розмір дескриптора = 9 байтів */
    uint8_t  bDescriptorType;     /* Тип дескриптора = 0x21 (DFU Functional Descriptor) */
    uint8_t  bmAttributes;        /* Бітова маска можливостей завантажувача:
                                     bit 0: bitCanDnload = 1 (підтримка запису Flash)
                                     bit 1: bitCanUpload = 1 (підтримка читання Flash)
                                     bit 2: bitManifestationTolerant = 0 (потрібен Reset)
                                     bit 3: bitWillDetach = 1 (самостійний вихід) */
    uint16_t wDetachTimeOut;      /* Таймаут очікування скидання шини після Detach (мс) */
    uint16_t wTransferSize;       /* Розмір одного блоку передачі даних (1024 або 2048 байтів) */
    uint16_t bcdDFUVersion;       /* Версія підтримуваної специфікації DFU = 0x0110 (DFU 1.1) */
} usb_dfu_functional_descriptor_t;

const usb_dfu_functional_descriptor_t dfu_descriptor = {
    .bLength = sizeof(usb_dfu_functional_descriptor_t),
    .bDescriptorType = 0x21U,
    .bmAttributes = 0x0BU,        /* CanDnload | CanUpload | WillDetach */
    .wDetachTimeOut = 250U,       /* 250 мс */
    .wTransferSize = 1024U,       /* 1 КБ буфер */
    .bcdDFUVersion = 0x0110U      /* Версія 1.1 */
};
