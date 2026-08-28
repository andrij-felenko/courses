// Регістри ArduChip (реальні адреси зі старих SPI-камер ArduCam):
#define ARDUCHIP_FIFO     0x04   // керування буфером; біт «почати захоплення»
#define FIFO_START_MASK   0x02   // цей біт у ARDUCHIP_FIFO = «знімай кадр»
#define ARDUCHIP_TRIG     0x41   // регістр стану (тригерів)
#define CAP_DONE_MASK     0x08   // біт[3] тут = «кадр знято, лежить у буфері»
#define BURST_FIFO_READ   0x3C   // команда «віддавай байти кадру потоком»
#define FIFO_SIZE1        0x42   // довжина кадру в байтах: біти  [7:0]
#define FIFO_SIZE2        0x43   //                         біти [15:8]
#define FIFO_SIZE3        0x44   //                         біти [18:16]

void arducam_capture(uint8_t *dst)
{
    // 1. «Знімай»: піднімаємо біт захоплення в регістрі буфера.
    spi_write_reg(ARDUCHIP_FIFO, FIFO_START_MASK);

    // 2. «Ти вже?»: крутимося, поки чип не підніме прапорець готовності.
    //    МК тут вільний від потоку — кадр ловить ArduChip, не ми.
    while (!(spi_read_reg(ARDUCHIP_TRIG) & CAP_DONE_MASK)) {
        // за бажання — сон, інші справи; кадр не втечеться з буфера
    }

    // Скільки байтів у знятому кадрі — чип сам порахував і поклав у три регістри.
    uint32_t len =  (uint32_t)spi_read_reg(FIFO_SIZE1)
                 | ((uint32_t)spi_read_reg(FIFO_SIZE2) << 8)
                 | ((uint32_t)spi_read_reg(FIFO_SIZE3) << 16);

    // 3. «Віддавай»: одна команда — і тактуємо SPI, забираючи байт за байтом.
    spi_cs_low();
    spi_transfer(BURST_FIFO_READ);          // «лий FIFO потоком»
    for (uint32_t i = 0; i < len; i++)
        dst[i] = spi_transfer(0x00);        // кожен такт → наступний байт кадру
    spi_cs_high();
}
