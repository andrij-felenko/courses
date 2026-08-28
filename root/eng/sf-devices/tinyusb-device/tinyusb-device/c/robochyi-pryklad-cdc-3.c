/* Прийшли байти по CDC — відлунюємо їх назад до хоста */
void tud_cdc_rx_cb(uint8_t itf) {
    uint8_t buf[64];
    uint32_t count = tud_cdc_n_read(itf, buf, sizeof(buf));  /* прочитати */
    tud_cdc_n_write(itf, buf, count);                        /* записати назад */
    tud_cdc_n_write_flush(itf);                              /* проштовхнути */
}

int main(void) {
    tusb_init();                 /* підняти стек */
    while (1) {
        tud_task();              /* насос: тут і викличеться rx_cb */
    }
}
