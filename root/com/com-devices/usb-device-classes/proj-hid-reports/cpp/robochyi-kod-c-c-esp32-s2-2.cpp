// Надіслати стан: modifier — бітова маска, usage — код звичайної клавіші.
// Якщо потрібно кілька клавіш одночасно — заповнити кілька слотів keys[].
void key_send(uint8_t modifier, uint8_t usage) {
    if (!usb_hid.ready()) return;   // endpoint ще не готовий — пропускаємо
    uint8_t keys[6] = { usage, 0, 0, 0, 0, 0 };  // масив 6 байтів, решта — 0
    // tud_hid_keyboard_report(report_id, modifier, keys[6])
    usb_hid.keyboardReport(0, modifier, keys);   // стан, не подія!
}

// Відпустити всі клавіші — порожній звіт (0x00 × 8).
// ОБОВ'ЯЗКОВО після кожного key_send(), інакше хост вважає клавішу затиснутою.
void key_release(void) {
    if (!usb_hid.ready()) return;
    usb_hid.keyboardRelease(0);
}
