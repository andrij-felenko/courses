// Неблокуюче зчитування накопиченої позиції у відліках
int32_t encoder_get_position(encoder_handle_t handle);

// Отримання поточної кутової швидкості в обертах за хвилину (RPM)
float encoder_get_velocity_rpm(encoder_handle_t handle);

typedef enum {
    BUTTON_STATE_RELEASED = 0,
    BUTTON_STATE_PRESSED,
    BUTTON_STATE_CLICKED,
    BUTTON_STATE_LONG_PRESS
} button_state_t;

// Зчитування стану кнопки з автоматичним відсіюванням брязкоту
button_state_t encoder_get_button_state(encoder_handle_t handle);
