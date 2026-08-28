#include "lvgl.h"

#define DISP_HOR_RES 480
#define DISP_VER_RES 320
#define BUF_LINES    32

static lv_color_t __attribute__((aligned(32))) buf1[DISP_HOR_RES * BUF_LINES];
static lv_color_t __attribute__((aligned(32))) buf2[DISP_HOR_RES * BUF_LINES];

static lv_disp_draw_buf_t draw_buf;
static lv_disp_drv_t      disp_drv;

extern void my_lcd_flush_dma(lv_disp_drv_t *drv, const lv_area_t *area, lv_color_t *color_p);

void app_gui_setup(void)
{
    lv_init();

    /* 1. Ініціалізація структури подвійного буфера */
    lv_disp_draw_buf_init(&draw_buf, buf1, buf2, DISP_HOR_RES * BUF_LINES);

    /* 2. Налаштування та реєстрація драйвера дисплея */
    lv_disp_drv_init(&disp_drv);
    disp_drv.hor_res  = DISP_HOR_RES;
    disp_drv.ver_res  = DISP_VER_RES;
    disp_drv.flush_cb = my_lcd_flush_dma;
    disp_drv.draw_buf = &draw_buf;
    lv_disp_drv_register(&disp_drv);

    /* 3. Створення базових графічних об'єктів */
    lv_obj_t *btn = lv_btn_create(lv_scr_act());
    lv_obj_align(btn, LV_ALIGN_CENTER, 0, 0);

    lv_obj_t *label = lv_label_create(btn);
    lv_label_set_text(label, "Старт системи");
}
