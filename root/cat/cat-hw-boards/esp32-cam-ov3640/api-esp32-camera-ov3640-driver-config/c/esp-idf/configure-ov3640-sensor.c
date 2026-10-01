#include "esp_camera.h"

void configure_ov3640_sensor(void) {
    sensor_t *s = esp_camera_sensor_get();
    if (s == NULL) {
        return;
    }

    // Програмне повернення кадру на рівні сенсора
    s->set_hmirror(s, 1);
    s->set_vflip(s, 1);

    // Відключення автоматики для зафіксованого освітлення
    s->set_whitebal(s, 0); // Вимкнення AWB
    s->set_gain_ctrl(s, 0); // Вимкнення AGC

    // Прямий запис у регістр OV3640 по шині SCCB
    s->set_reg(s, 0x3000, 0xFF, 0x01);
}
