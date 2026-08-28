/* usb_descriptors.h — Device Descriptor (USB 2.0, §9.6.1) */
struct __attribute__((packed)) usb_device_descriptor {
    uint8_t  bLength;            /* [00] = 0x12 (18 байтів)        */
    uint8_t  bDescriptorType;   /* [01] = 0x01 (DEVICE)           */
    uint16_t bcdUSB;            /* [02-03] = 0x0200 (USB 2.0)     */
    uint8_t  bDeviceClass;      /* [04] = 0x00 (клас в Interface) */
    uint8_t  bDeviceSubClass;   /* [05] = 0x00                    */
    uint8_t  bDeviceProtocol;   /* [06] = 0x00                    */
    uint8_t  bMaxPacketSize0;   /* [07] = 0x40 (64 байти EP0)     */
    uint16_t idVendor;          /* [08-09] = 0x0483 (STMicro) VID */
    uint16_t idProduct;         /* [0A-0B] = 0x5711           PID */
    uint16_t bcdDevice;         /* [0C-0D] = 0x0200               */
    uint8_t  iManufacturer;     /* [0E] = 1 (індекс String)       */
    uint8_t  iProduct;          /* [0F] = 2                       */
    uint8_t  iSerialNumber;     /* [10] = 3                       */
    uint8_t  bNumConfigurations;/* [11] = 1                       */
};
