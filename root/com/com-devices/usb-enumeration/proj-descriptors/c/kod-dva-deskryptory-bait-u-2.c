// Configuration + Interface + Endpoint — відповідь на GET_DESCRIPTOR(Configuration, 0)
// Три дескриптори склеєні в один буфер; хост читає все за один запит
static const uint8_t desc_config[] = {

    // ── Config Descriptor (9 байтів) ──────────────────────────────────────
    9,            // bLength              = 9
    0x02,         // bDescriptorType      = CONFIGURATION (0x02)
    0x19, 0x00,   // wTotalLength         = 25 (LE: 0x19, 0x00) = 9+9+7
    1,            // bNumInterfaces       = 1
    1,            // bConfigurationValue  = 1 (індекс конфігурації)
    0x00,         // iConfiguration       = 0 (рядка нема)
    0x80,         // bmAttributes         = 0x80 (bus-powered, без remote-wakeup)
    50,           // bMaxPower            = 50 × 2 мА = 100 мА (живлення по USB)

    // ── Interface Descriptor (9 байтів) ────────────────────────────────────
    9,            // bLength              = 9
    0x04,         // bDescriptorType      = INTERFACE (0x04)
    0,            // bInterfaceNumber     = 0
    0,            // bAlternateSetting    = 0
    1,            // bNumEndpoints        = 1 (крім EP0)
    0xFF,         // bInterfaceClass      = 0xFF vendor-specific (клас інтерфейсу)
    0x00,         // bInterfaceSubClass   = 0
    0x00,         // bInterfaceProtocol   = 0
    0x00,         // iInterface           = 0

    // ── Endpoint Descriptor (7 байтів) ─────────────────────────────────────
    7,            // bLength              = 7
    0x05,         // bDescriptorType      = ENDPOINT (0x05)
    0x81,         // bEndpointAddress     = 0x81 (IN, endpoint 1)
    0x03,         // bmAttributes         = 0x03 (interrupt; тип передачі)
    0x08, 0x00,   // wMaxPacketSize       = 8 (LE: low, high)
    10,           // bInterval            = 10 мс (інтервал опитування)
};
