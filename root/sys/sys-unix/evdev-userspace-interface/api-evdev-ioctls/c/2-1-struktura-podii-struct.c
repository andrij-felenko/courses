struct input_event {
#if (__BITS_PER_LONG == 32)
    __kernel_ulong_t input_event_sec;
    __kernel_ulong_t input_event_usec;
#else
    struct timeval time;
#endif
    __u16 type;
    __u16 code;
    __s32 value;
};
