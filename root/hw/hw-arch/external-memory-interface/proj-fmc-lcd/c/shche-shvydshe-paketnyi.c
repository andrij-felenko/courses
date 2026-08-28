#include <stdint.h>

// Залити прямокутник суцільним кольором через DMA: джерело — одна комірка
// (інкремент джерела вимкнено), призначення — LCD_DATA (інкремент вимкнено теж).
void lcd_fill_rect_dma(uint16_t x, uint16_t y, uint16_t w, uint16_t h,
                       uint16_t color) {
    static volatile uint16_t src;            // одна комірка-джерело
    src = color;
    lcd_set_window(x, y, x + w - 1, y + h - 1);

    uint32_t n = (uint32_t)w * h;
    // Псевдо-налаштування потоку DMA (конкретні регістри — з CMSIS вашого МК):
    //   PAR  = (uint32_t)&src;   MINC = 0   (джерело не рухається)
    //   M0AR = (uint32_t)&LCD_DATA; PINC = 0 (призначення не рухається)
    //   PSIZE = MSIZE = 16 біт;  NDTR = n;   напрям M→M
    dma_mem_to_mem_16((uint32_t)&src, (uint32_t)&LCD_DATA, n, /*src_inc=*/0);
    // Ядро вільне: поки DMA переливає піксель за пікселем у дисплей, можна рахувати.
}
