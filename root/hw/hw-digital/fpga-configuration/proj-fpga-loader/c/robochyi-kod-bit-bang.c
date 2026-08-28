typedef enum {
    FPGA_OK = 0,
    FPGA_ERR_NO_STATUS,   // nSTATUS не піднявся — чип не відгукнувся
    FPGA_ERR_STATUS_DROP, // nSTATUS упав під час заливки — помилка конфігурації
    FPGA_ERR_NO_DONE,     // бітстрім вичерпано, а DONE так і не піднявся
    FPGA_ERR_EMPTY        // джерело бітстріму порожнє
} fpga_status_t;

fpga_status_t fpga_configure_slave_serial(void)
{
    uint8_t buf[256];
    size_t  n;

    // ── 1. Скидання: притиснути nCONFIG, витримати мінімальний імпульс ──
    gpio_write(PIN_DCLK, 0);        // такт у спокої — низько
    gpio_write(PIN_NCONFIG, 0);     // наказ «зітри SRAM, почнемо спочатку»
    delay_us(5);                    // тримаємо вниз довше за мінімум (~2 мкс)
    gpio_write(PIN_NCONFIG, 1);     // відпустили — чип починає чистку SRAM

    // ── 2. Рукостискання: чекаємо, поки чип відпустить nSTATUS угору ──
    // Активний-0, open-drain: 1 означає «SRAM очищено, лий бітстрім».
    {
        int tries = 1000;                       // ~1000 × 1 мкс = 1 мс стелі
        while (gpio_read(PIN_NSTATUS) == 0) {
            if (--tries == 0)
                return FPGA_ERR_NO_STATUS;       // чип мовчить — далі немає сенсу
            delay_us(1);
        }
    }

    // ── 3. Потік бітів: качаємо бітстрім байт за байтом ──
    size_t total = 0;
    while ((n = bitstream_read(buf, sizeof buf)) > 0) {
        total += n;
        for (size_t i = 0; i < n; ++i) {
            clock_one_byte(buf[i]);

            // Дешева страховка: чип під час заливки може ВПАСТИ у помилку
            // (CRC не збігся, живлення просіло) — тоді він притисне nSTATUS.
            // Перевіряти щобайт — доступно й ловить збій рано.
            if (gpio_read(PIN_NSTATUS) == 0)
                return FPGA_ERR_STATUS_DROP;
        }
    }
    if (total == 0)
        return FPGA_ERR_EMPTY;      // джерело нічого не дало — порожня флеш?

    // ── 4. Дожати такт, поки DONE не підніметься ──
    // Після бітстріму чипу треба ще трохи тактів на запуск. Женемо їх,
    // тримаючи DATA0 у 1 (так радять виробники — лінія в спокої висока).
    gpio_write(PIN_DATA0, 1);
    for (int extra = 0; extra < 1000; ++extra) {
        if (gpio_read(PIN_CONF_DONE) == 1) {
            // DONE піднявся. Дамо ще з десяток тактів — вимога запуску
            // (Xilinx 7-ї серії: щонайменше 8 після DONE).
            for (int i = 0; i < 16; ++i) {
                gpio_write(PIN_DCLK, 1);
                gpio_write(PIN_DCLK, 0);
            }
            return FPGA_OK;         // FPGA несе схему й готова до роботи
        }
        gpio_write(PIN_DCLK, 1);
        gpio_write(PIN_DCLK, 0);
    }
    return FPGA_ERR_NO_DONE;        // 1000 тактів — а DONE мовчить: дивись пастки
}
