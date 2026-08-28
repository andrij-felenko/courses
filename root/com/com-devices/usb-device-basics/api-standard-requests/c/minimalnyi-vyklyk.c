#include <stdint.h>

/* Setup-пакет — рівно 8 байтів; 16-бітові поля little-endian */
typedef struct __attribute__((packed)) {
    uint8_t  bmRequestType;   /* D7 напрям · D6-5 тип · D4-0 отримувач */
    uint8_t  bRequest;        /* код запиту */
    uint16_t wValue;
    uint16_t wIndex;
    uint16_t wLength;         /* байтів у стадії даних */
} usb_setup;                  /* sizeof(usb_setup) == 8 */
