// Device Descriptor — відповідь на GET_DESCRIPTOR(Device, 0)
static const uint8_t desc_device[18] = {
    18,           // bLength          = 18 (розмір цього дескриптора)
    0x01,         // bDescriptorType  = DEVICE (0x01)
    0x00, 0x02,   // bcdUSB           = 0x0200 → USB 2.0 (LE: low, high)
    0x00,         // bDeviceClass     = 0x00 (клас задається в інтерфейсі)
    0x00,         // bDeviceSubClass  = 0
    0x00,         // bDeviceProtocol  = 0
    64,           // bMaxPacketSize0  = 64 (EP0 max packet, Full Speed)
    0x03, 0x30,   // idVendor         = 0x3003 (LE: low, high) — тестовий / Espressif
    0x01, 0x00,   // idProduct        = 0x0001 (LE: low, high)
    0x00, 0x01,   // bcdDevice        = 0x0100 → версія прошивки 1.0 (LE: low, high)
    0x00,         // iManufacturer    = 0 (рядкового дескриптора нема)
    0x00,         // iProduct         = 0
    0x00,         // iSerialNumber    = 0
    1,            // bNumConfigurations = 1
};
