#define W 320
#define STRIP_H 20                       /* висота смуги в рядках */
static uint16_t strip[W * STRIP_H];      /* малий буфер: 12.5 КіБ замість 150 КіБ */

/* намалювати весь кадр смугами (елементи задає draw_scene, що вміє обрізати по y) */
void render_by_strips(void)
{
    for (uint16_t y0 = 0; y0 < 240; y0 += STRIP_H) {
        uint16_t h = (y0 + STRIP_H <= 240) ? STRIP_H : (240 - y0);  /* остання смуга коротша */

        clear_strip(strip, W * h, BG);                 /* очистити буфер під нову смугу */
        draw_scene(strip, W, y0, h);   /* намалювати ВСЕ, що влучає в рядки [y0, y0+h),
                                          з обрізанням кожного елемента до цього діапазону */

        set_window(0, y0, W, h);                       /* вікно GRAM рівно на цю смугу */
        push_pixels(strip, (uint32_t)W * h);           /* виштовхнути смугу (RAMWR-потік) */
    }
}
