struct libinput_event_pointer *libinput_event_get_pointer_event(struct libinput_event *event);

/* Прискорені балістичні дельти переміщення в пікселях робочого столу */
double libinput_event_pointer_get_dx(struct libinput_event_pointer *event);
double libinput_event_pointer_get_dy(struct libinput_event_pointer *event);

/* Фізичні неприскорені зміщення (у міліметрах) для шутерів від першої особи та САПР */
double libinput_event_pointer_get_dx_unaccelerated(struct libinput_event_pointer *event);
double libinput_event_pointer_get_dy_unaccelerated(struct libinput_event_pointer *event);

/* Номер кнопки за стандартом Linux (BTN_LEFT = 272, BTN_RIGHT = 273, BTN_MIDDLE = 274) */
uint32_t libinput_event_pointer_get_button(struct libinput_event_pointer *event);
enum libinput_button_state libinput_event_pointer_get_button_state(struct libinput_event_pointer *event);

/* Значення прокрутки по осях LIBINPUT_POINTER_AXIS_SCROLL_VERTICAL або HORIZONTAL */
double libinput_event_pointer_get_scroll_value(struct libinput_event_pointer *event,
                                               enum libinput_pointer_axis axis);
/* Значення прокрутки під стандартом v120 (120 одиниць = 1 дискретний клік звичайного колеса) */
double libinput_event_pointer_get_scroll_value_v120(struct libinput_event_pointer *event,
                                                    enum libinput_pointer_axis axis);
