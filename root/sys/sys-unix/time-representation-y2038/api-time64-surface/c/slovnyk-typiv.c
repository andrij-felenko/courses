/* include/uapi/linux/time_types.h — форми, у яких час перетинає межу */

struct __kernel_timespec {
	__kernel_time64_t	tv_sec;		/* секунди — завжди 64 біти */
	long long		tv_nsec;
};

struct __kernel_itimerspec {
	struct __kernel_timespec it_interval;
	struct __kernel_timespec it_value;
};

struct __kernel_old_timespec {
	__kernel_old_time_t	tv_sec;		/* вузька форма */
	long			tv_nsec;
};

struct __kernel_old_timeval {
	__kernel_long_t		tv_sec;		/* лишили лише там, де це ТРИВАЛІСТЬ;
						   нових користувачів не заводять */
	__kernel_long_t		tv_usec;
};

struct __kernel_old_itimerval {
	struct __kernel_old_timeval it_interval;
	struct __kernel_old_timeval it_value;
};

struct __kernel_sock_timeval {
	__s64 tv_sec;				/* окрема широка форма для сокетів */
	__s64 tv_usec;
};
