struct libinput_event_gesture *libinput_event_get_gesture_event(struct libinput_event *event);

/* Кількість одночасно задіяних пальців у поточному жесті (3 або 4 для свайпу; 2, 3 або 4 для щипка) */
int libinput_event_gesture_get_finger_count(struct libinput_event_gesture *event);

/* Зміщення центру мас групи пальців відносно попереднього кадру події */
double libinput_event_gesture_get_dx(struct libinput_event_gesture *event);
double libinput_event_gesture_get_dy(struct libinput_event_gesture *event);

/* Масштабний множник: 1.0 — початковий стан, >1.0 — розведення пальців, <1.0 — стискання */
double libinput_event_gesture_get_scale(struct libinput_event_gesture *event);

/* Кутова дельта повороту лінії між пальцями (у градусах, позитивне значення — за годинниковою стрілкою) */
double libinput_event_gesture_get_angle_delta(struct libinput_event_gesture *event);
