struct libinput_event_tablet_tool *libinput_event_get_tablet_tool_event(struct libinput_event *event);

/* Нормалізована сила притискання наконечника до скла планшета в діапазоні [0.0, 1.0] */
double libinput_event_tablet_tool_get_pressure(struct libinput_event_tablet_tool *event);

/* Кути просторового нахилу пера у градусах відносно площини сенсора (зазвичай [-60.0, +60.0]) */
double libinput_event_tablet_tool_get_tilt_x(struct libinput_event_tablet_tool *event);
double libinput_event_tablet_tool_get_tilt_y(struct libinput_event_tablet_tool *event);

/* Висота безконтактного зависання пера над поверхнею планшета у діапазоні [0.0, 1.0] */
double libinput_event_tablet_tool_get_distance(struct libinput_event_tablet_tool *event);

/* Кут обертання пера довкола своєї поздовжньої осі (для симуляції каліграфічних плоских пензлів [0.0, 360.0]) */
double libinput_event_tablet_tool_get_rotation(struct libinput_event_tablet_tool *event);
