// Периферія вводу-виводу вміє кілька стандартів; вибираємо LVDS
// для конкретної пари ніжок. Значення полів — з даташита МК/ПЛІС.
#define IO_STD_LVCMOS33   0x0u
#define IO_STD_LVDS       0x3u   // струмовий диференціальний вихід ~3.5 мА

void lvds_pair_init(volatile uint32_t *io_cfg, unsigned pin_pair) {
    uint32_t v = io_cfg[pin_pair];
    v &= ~0x7u;                  // стерти старе поле стандарту
    v |=  IO_STD_LVDS;           // задати LVDS для цієї пари
    v |=  (1u << 8);             // увімкнути вихідний буфер
    io_cfg[pin_pair] = v;        // застосувати
}
