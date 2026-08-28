void ow_write_byte(uint8_t b) {
    for (uint8_t i = 0; i < 8; i++) {
        ow_write_bit(b & 1);           // молодший біт — перший на дроті
        b >>= 1;
    }
}

uint8_t ow_read_byte(void) {
    uint8_t b = 0;
    for (uint8_t i = 0; i < 8; i++) {
        b >>= 1;                       // звільняємо старший розряд
        if (ow_read_bit()) b |= 0x80;  // прочитаний біт лягає згори…
    }
    return b;                          // …і за 8 зсувів перший біт опиниться в bit0
}
