// У C++ заголовку <linux/input.h> структура доступна у просторі імен ::input_event
struct input_event {
#if (__BITS_PER_LONG == 32)
    std::uint32_t input_event_sec;
    std::uint32_t input_event_usec;
#else
    struct timeval time;
#endif
    std::uint16_t type;
    std::uint16_t code;
    std::int32_t  value;
};
