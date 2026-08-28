// TinyUSB викликає ці функції під час енумерації;
// ми лише повертаємо вказівник на static const буфер у Flash

uint8_t const *tud_descriptor_device_cb(void) {
    return desc_device;
}

uint8_t const *tud_descriptor_configuration_cb(uint8_t index) {
    (void)index;        // у нас одна конфігурація
    return desc_config;
}
