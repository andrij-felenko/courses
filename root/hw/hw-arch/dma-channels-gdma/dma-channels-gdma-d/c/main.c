#include <stdint.h>

/* Селектор периферії приймального каналу 0 GDMA (адреса умовна, з даташита).
   Записуємо номер периферії з довідника; 5 = LCD/CAM. */
#define GDMA_IN_PERI_SEL_CH0  (*(volatile uint32_t *)0x6003F000)

#define GDMA_PERI_LCD_CAM  5u   /* номер периферії за таблицею даташита */

void gdma_bind_ch0_to_lcdcam(void) {
    GDMA_IN_PERI_SEL_CH0 = GDMA_PERI_LCD_CAM;  /* канал 0 тепер слухає LCD/CAM */
    /* усе: лінія запиту камери приходить саме на цей канал */
}
