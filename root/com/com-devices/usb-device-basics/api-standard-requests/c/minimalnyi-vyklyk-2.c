/* «Дай 18 байтів дескриптора пристрою» */
usb_setup get_dev_desc = {
    .bmRequestType = 0x80,    /* IN · стандартний · пристрій          */
    .bRequest      = 0x06,    /* GET_DESCRIPTOR                        */
    .wValue        = 0x0100,  /* тип 0x01 (DEVICE) << 8  |  індекс 0   */
    .wIndex        = 0x0000,  /* мова не потрібна                      */
    .wLength       = 18,      /* повний device-дескриптор = 18 байтів  */
};
/* на дротах:  80 06 00 01 00 00 12 00   (wValue, wLength — LSB перший) */

/* «Прийми адресу 7» — стадії даних немає */
usb_setup set_addr = {
    .bmRequestType = 0x00,    /* OUT · стандартний · пристрій */
    .bRequest      = 0x05,    /* SET_ADDRESS                  */
    .wValue        = 7,       /* нова адреса                  */
    .wIndex        = 0,
    .wLength       = 0,
};
/* на дротах:  00 05 07 00 00 00 00 00 */

/* «Увімкни конфігурацію 1» — завершення енумерації */
usb_setup set_config = {
    .bmRequestType = 0x00,
    .bRequest      = 0x09,    /* SET_CONFIGURATION  */
    .wValue        = 1,       /* номер конфігурації */
    .wIndex        = 0,
    .wLength       = 0,
};
/* на дротах:  00 09 01 00 00 00 00 00 */
