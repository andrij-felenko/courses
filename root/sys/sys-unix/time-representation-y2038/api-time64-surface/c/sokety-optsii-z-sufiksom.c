/* include/uapi/asm-generic/socket.h */

#if __BITS_PER_LONG == 64 || (defined(__x86_64__) && defined(__ILP32__))
/* на 64-бітних і на x32 обходимося без ?: */
#define SO_TIMESTAMP		SO_TIMESTAMP_OLD
#define SO_RCVTIMEO		SO_RCVTIMEO_OLD
#else
#define SO_TIMESTAMP	(sizeof(time_t) == sizeof(__kernel_long_t) ? \
			 SO_TIMESTAMP_OLD : SO_TIMESTAMP_NEW)
#define SO_RCVTIMEO	(sizeof(time_t) == sizeof(__kernel_long_t) ? \
			 SO_RCVTIMEO_OLD : SO_RCVTIMEO_NEW)
#endif
