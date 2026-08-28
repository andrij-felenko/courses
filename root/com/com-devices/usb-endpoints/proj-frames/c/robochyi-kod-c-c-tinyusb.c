// Дескриптор HID-endpoint через TinyUSB
// bInterval = 8 → хост опитує раз на 8 мс = 125 Гц
static const tusb_desc_endpoint_t hid_ep_desc = {
    .bLength          = sizeof(tusb_desc_endpoint_t),
    .bDescriptorType  = TUSB_DESC_ENDPOINT,
    .bEndpointAddress = 0x81,          // EP1, напрям IN
    .bmAttributes = {
        .xfer = TUSB_XFER_INTERRUPT,   // тип = interrupt
    },
    .wMaxPacketSize   = 8,             // байтів у звіті
    .bInterval        = 8,             // 8 кадрів = 8 мс → 125 Гц
};
