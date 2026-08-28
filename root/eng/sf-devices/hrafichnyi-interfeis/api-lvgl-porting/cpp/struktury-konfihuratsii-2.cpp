namespace embedded::lvgl {

enum class InputDeviceType {
    None    = LV_INDEV_TYPE_NONE,
    Pointer = LV_INDEV_TYPE_POINTER,
    Keypad  = LV_INDEV_TYPE_KEYPAD,
    Button  = LV_INDEV_TYPE_BUTTON,
    Encoder = LV_INDEV_TYPE_ENCODER
};

enum class InputState {
    Released = LV_INDEV_STATE_RELEASED,
    Pressed  = LV_INDEV_STATE_PRESSED
};

} // namespace embedded::lvgl
