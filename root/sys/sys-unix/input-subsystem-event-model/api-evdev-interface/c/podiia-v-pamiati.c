struct input_event {
#if (__BITS_PER_LONG != 32 || !defined(__USE_TIME_BITS64)) && !defined(__KERNEL__)
	struct timeval time;
#define input_event_sec  time.tv_sec
#define input_event_usec time.tv_usec
#else
	__kernel_ulong_t __sec;
	__kernel_ulong_t __usec;
#define input_event_sec  __sec
#define input_event_usec __usec
#endif
	__u16 type;
	__u16 code;
	__s32 value;
};
