#include "lvgl.h"

/* Розміри дисплея */
#define DISP_HOR_RES 240
#define DISP_VER_RES 240

/* Висота смуги: 1/10 від загальної кількості рядків */
#define BUFFER_ROWS  24
#define BUFFER_SIZE  (DISP_HOR_RES * BUFFER_ROWS)

/* Статичний буфер у пам'яті МК: 240 * 24 * 2 = 11520 байтів (11.25 КіБ) */
static lv_color_t buf_1[BUFFER_SIZE];

/* Структура дескриптора буфера відтворення */
static lv_disp_draw_buf_t draw_buf_dsc;

void lvgl_buffer_setup(void)
{
    /* 
     * Ініціалізація дескриптора буфера:
     * buf_1 — перший частковий буфер
     * NULL  — другий буфер відсутній (одинарний режим)
     * BUFFER_SIZE — розмір у пікселях
     */
    lv_disp_draw_buf_init(&draw_buf_dsc, buf_1, NULL, BUFFER_SIZE);
}
