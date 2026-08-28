// Шаблонний фільтр вибірки SCL у C++
template <typename Hal>
bool read_scl_filtered(Hal& hal) {
    uint8_t high_samples = 0;
    for (uint8_t i = 0; i < 3; ++i) {
        if (hal.read_scl()) {
            ++high_samples;
        }
    }
    return (high_samples >= 2);
}
