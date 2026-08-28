/* Варіант 1: CDC (COM-порт для логів) */
/* tusb_config.h: CFG_TUD_CDC = 1, CFG_TUD_HID = 0, CFG_TUD_MSC = 0 */
tud_cdc_write_str("Hello from CDC!\r\n");
tud_cdc_write_flush();

/* Варіант 2: HID-клавіатура — надіслати натискання 'A' */
/* CFG_TUD_HID = 1 */
uint8_t keycode[6] = { HID_KEY_A, 0, 0, 0, 0, 0 };
tud_hid_keyboard_report(REPORT_ID_KEYBOARD, 0 /*modifier*/, keycode);
tud_task();                                       /* обробити USB-події */
tud_hid_keyboard_report(REPORT_ID_KEYBOARD, 0, NULL);  /* відпустити клавішу */

/* Варіант 3: MSC (флешка з SD-карткою) */
/* CFG_TUD_MSC = 1 */
/* реалізувати tud_msc_read10_cb() / tud_msc_write10_cb() → SD через SPI */
