// DE/RE — спільний вивід керування напрямом приймача-передавача (напр. MAX485):
//   високий → драйвер передає,  низький → приймає.
#define RS485_DRIVE_ENABLE()   gpio_set(DE_PIN, 1)
#define RS485_DRIVE_DISABLE()  gpio_set(DE_PIN, 0)

void rs485_send(const uint8_t *buf, size_t n) {
    RS485_DRIVE_ENABLE();          // взяли шину на передачу
    for (size_t i = 0; i < n; i++)
        uart_write_byte(buf[i]);   // байт іде в драйвер, далі — у пару A/B

    uart_wait_tx_complete();       // КЛЮЧОВЕ: чекаємо, поки останній біт ПОКИНЕ зсувний регістр,
                                   // інакше вимкнемо драйвер посеред стоп-біта й обріжемо кадр
    RS485_DRIVE_DISABLE();         // відпустили шину — тепер можна приймати
}
