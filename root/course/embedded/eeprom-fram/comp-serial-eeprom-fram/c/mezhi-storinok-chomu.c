// Записати len байтів буфера buf, починаючи з addr, правильно ріжучи по
// сторінках: лічильник адреси чипа в межах сторінки лише обертається, а не
// переходить далі, — тож кожну сторінку пишемо й чекаємо окремо.
#define PAGE 32                      // розмір сторінки конкретного чипа (з даташита)

void eeprom_write(uint8_t dev, uint16_t addr, const uint8_t *buf, uint16_t len) {
    while (len) {
        uint16_t to_edge = PAGE - (addr % PAGE);     // скільки лишилось до межі
        uint16_t n = (len < to_edge) ? len : to_edge;

        i2c_start();
        i2c_send(dev << 1);
        i2c_send(addr >> 8);
        i2c_send(addr & 0xFF);
        for (uint16_t i = 0; i < n; i++) i2c_send(buf[i]);
        i2c_stop();
        eeprom_wait_ready(dev);      // той самий ACK polling — один цикл на сторінку

        addr += n;  buf += n;  len -= n;
    }
}
