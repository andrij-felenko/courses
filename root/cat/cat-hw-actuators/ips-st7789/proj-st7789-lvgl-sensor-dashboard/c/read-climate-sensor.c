#include <Arduino.h>
#include <lvgl.h>

// Вказівники на динамічні графічні елементи екрана 240x240
static lv_obj_t *arc_temperature = nullptr;
static lv_obj_t *lbl_temp_value = nullptr;

// Макет неблокуючого зчитування параметрів клімату
static void read_climate_sensor(int16_t *temperature, int16_t *humidity)
{
    // Імітація надходження даних без затримки виконання
    static int16_t sim_t = 21;
    sim_t = (sim_t >= 32) ? 18 : (sim_t + 1);
    *temperature = sim_t;
    *humidity = 48;
}

// Періодичний зворотний виклик таймера LVGL для оновлення дашборду
static void sensor_update_timer_cb(lv_timer_t *timer)
{
    int16_t temp_celsius = 0;
    int16_t hum_percent = 0;
    read_climate_sensor(&temp_celsius, &hum_percent);

    // Оновлення значення кругової шкали без перестворення об'єкта
    lv_arc_set_value(arc_temperature, temp_celsius);

    // Безпечне оновлення рядка з автоматичною інвалідацією ділянки
    lv_label_set_text_fmt(lbl_temp_value, "%d °C", temp_celsius);
}

void setup()
{
    lv_init();
    // Ініціалізація апаратного SPI та драйвера ST7789 відбувається тут...

    // Створення кругової шкали під роздільність 240x240
    arc_temperature = lv_arc_create(lv_scr_act());
    lv_obj_set_size(arc_temperature, 190, 190);
    lv_obj_center(arc_temperature);
    lv_arc_set_range(arc_temperature, 0, 50);
    lv_arc_set_bg_angles(arc_temperature, 135, 45);

    // Створення центрального числового напису
    lbl_temp_value = lv_label_create(lv_scr_act());
    lv_obj_center(lbl_temp_value);
    lv_label_set_text(lbl_temp_value, "-- °C");

    // Реєстрація періодичного таймера бібліотеки з інтервалом 1000 мс
    lv_timer_create(sensor_update_timer_cb, 1000, nullptr);
}

void loop()
{
    // Оновлення системного лічильника часу (крок 5 мс)
    lv_tick_inc(5);

    // Диспетчеризація завдань графічного інтерфейсу та анімацій
    lv_timer_handler();

    // Неблокуюча пауза для запобігання перевантаженню процесора
    delay(5);
}
