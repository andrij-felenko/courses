int main(void) {
    clock_init();
    adc_init();
    i2c_init();
    uart_init(115200);

    const char *serial = read_serial_from_flash();  // вписаний при провізіонуванні
    build_and_send_report(serial);                   // POST: сказати джигу, хто ми

    app_main_loop();                                 // далі — звичайна робота
}
