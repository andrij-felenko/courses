/* Конфігурація CDC: 2 інтерфейси (керування + дані), склеєні IAD */
uint8_t const desc_configuration[] = {
    /* Config descriptor */
    9, TUSB_DESC_CONFIGURATION,
    U16_TO_U8S_LE(67),  /* wTotalLength = весь блок нижче */
    2,                  /* bNumInterfaces: 2 (CDC = 2 інтерфейси) */
    1,                  /* bConfigurationValue */
    0, 0x80, 250,       /* iConfiguration, bmAttributes, bMaxPower = 500 мА */

    /* Interface Association: каже хосту склеїти інтерфейси 0+1 у CDC */
    8, TUSB_DESC_INTERFACE_ASSOCIATION,
    0, 2,               /* bFirstInterface = 0, bInterfaceCount = 2 */
    TUSB_CLASS_CDC, 2, 0, 0,   /* клас CDC, підклас Abstract Control Model */

    /* Interface 0: CDC Control (керування) */
    9, TUSB_DESC_INTERFACE,
    0, 0, 1,            /* номер = 0, alt = 0, 1 кінцева точка */
    TUSB_CLASS_CDC, 2, 0, 0,   /* bInterfaceClass = CDC (0x02) */

    /* interrupt-IN: сигнали стану лінії */
    7, TUSB_DESC_ENDPOINT,
    0x81,               /* EP 1 IN */
    TUSB_XFER_INTERRUPT, U16_TO_U8S_LE(8), 16,

    /* Interface 1: CDC Data (потік байтів) */
    9, TUSB_DESC_INTERFACE,
    1, 0, 2,            /* номер = 1, alt = 0, 2 кінцеві точки */
    TUSB_CLASS_CDC_DATA, 0, 0, 0,   /* bInterfaceClass = CDC-Data (0x0A) */

    /* bulk-OUT: дані від хоста */
    7, TUSB_DESC_ENDPOINT, 0x02, TUSB_XFER_BULK, U16_TO_U8S_LE(64), 0,
    /* bulk-IN: дані до хоста */
    7, TUSB_DESC_ENDPOINT, 0x82, TUSB_XFER_BULK, U16_TO_U8S_LE(64), 0,
};
/* Хост прочитає клас CDC → підніме драйвер → з'явиться новий COM / ttyACM */
