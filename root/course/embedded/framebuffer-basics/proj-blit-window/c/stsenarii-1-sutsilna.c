uint16_t swap16(uint16_t c) { return (uint16_t)((c >> 8) | (c << 8)); }

/* Залити прямокутник [x0..x1]×[y0..y1] суцільним кольором.
   color — «людський» RGB565 (як повертає rgb565); переворот робимо тут. */
static void fill_rect(uint16_t x0, uint16_t y0,
                      uint16_t x1, uint16_t y1, uint16_t color)
{
    set_window(x0, y0, x1, y1);                 // окреслили вікно, RAMWR уже пішов

    uint16_t wire = swap16(color);              // ПЕРЕВОРОТ РАЗ, перед циклом!
    uint32_t count = (uint32_t)(x1 - x0 + 1) * (y1 - y0 + 1);   // скільки пікселів

    /* лити один і той самий wire count разів — блоками, не поштучно */
    static uint16_t chunk[64];
    for (int i = 0; i < 64; i++) chunk[i] = wire; // заповнили буфер-шматок раз

    while (count) {
        uint32_t k = (count < 64) ? count : 64;
        send_data((const uint8_t *)chunk, k * 2);  // цілий шматок одним send_data
        count -= k;
    }
}
