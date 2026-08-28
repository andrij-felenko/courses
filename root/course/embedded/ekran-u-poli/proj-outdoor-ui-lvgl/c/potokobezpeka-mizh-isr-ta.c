#include "lvgl.h"
#include <stdint.h>
#include <stdbool.h>

/* Зовнішні апаратні функції, що працюють з атомарними змінними переривань */
extern int16_t hardware_encoder_get_and_clear_diff(void);
extern bool    hardware_encoder_is_button_down(void);

static lv_indev_t *encoder_indev = NULL;
static lv_group_t *field_nav_group = NULL;

static void encoder_read_cb(lv_indev_t *indev, lv_indev_data_t *data) {
    LV_UNUSED(indev);

    /* Зчитуємо кроки, накопичені з моменту останнього виклику */
    data->enc_diff = hardware_encoder_get_and_clear_diff();

    /* Стан кнопки підтвердження енкодера */
    if (hardware_encoder_is_button_down()) {
        data->state = LV_INDEV_STATE_PRESSED;
    } else {
        data->state = LV_INDEV_STATE_RELEASED;
    }
}

void field_input_init(void) {
    field_nav_group = lv_group_create();
    lv_group_set_default(field_nav_group);

    encoder_indev = lv_indev_create();
    lv_indev_set_type(encoder_indev, LV_INDEV_TYPE_ENCODER);
    lv_indev_set_read_cb(encoder_indev, encoder_read_cb);
    lv_indev_set_group(encoder_indev, field_nav_group);
}

void field_input_add_widget(lv_obj_t *obj) {
    if (field_nav_group && obj) {
        lv_group_add_obj(field_nav_group, obj);
    }
}
