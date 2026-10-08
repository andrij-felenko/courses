#include "esp_camera.h"

void adjust_sensor_settings(void) {
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        return;
    }

    s->set_hmirror(s, 1);
    s->set_vflip(s, 1);
    s->set_gain_ctrl(s, 1);
    s->set_exposure_ctrl(s, 1);
    s->set_awb_gain(s, 1);
    s->set_framesize(s, FRAMESIZE_VGA);
}
