namespace hal {

/* Еквівалент концептуального контракту C++20 без динамічних покажчиків */
template <typename T>
concept GpioPin = requires(T pin, PinLevel lvl) {
    { pin.set_level(lvl) } -> std::same_as<Status>;
    { pin.get_level() } -> std::same_as<PinLevel>;
    { pin.toggle() } -> std::same_as<Status>;
};

} // namespace hal
