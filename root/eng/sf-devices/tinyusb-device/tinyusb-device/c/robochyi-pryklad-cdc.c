#include "tusb.h"

/* Device Descriptor: хто ми загалом */
static const tusb_desc_device_t desc_device = {
    .bLength            = sizeof(tusb_desc_device_t),
    .bDescriptorType    = TUSB_DESC_DEVICE,
    .bcdUSB             = 0x0200,        /* USB 2.0 */
    .bDeviceClass       = TUSB_CLASS_MISC,       /* композит-сумісний клас */
    .bDeviceSubClass    = MISC_SUBCLASS_COMMON,
    .bDeviceProtocol    = MISC_PROTOCOL_IAD,
    .bMaxPacketSize0    = 64,            /* розмір пакета EP0 */
    .idVendor           = 0xCafe,        /* VID (тестовий) */
    .idProduct          = 0x4001,        /* PID */
    .bcdDevice          = 0x0100,        /* версія пристрою 1.0 */
    .iManufacturer      = 0x01,          /* індекси рядкових описів */
    .iProduct           = 0x02,
    .iSerialNumber      = 0x03,
    .bNumConfigurations = 0x01,
};

/* TinyUSB кличе цей колбек, коли хост просить Device Descriptor */
uint8_t const *tud_descriptor_device_cb(void) {
    return (uint8_t const *) &desc_device;
}
