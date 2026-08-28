/* include/uapi/asm-generic/sockios.h — старі, лишилися незмінними */
#define SIOCGSTAMP_OLD		0x8906		/* struct timeval  */
#define SIOCGSTAMPNS_OLD	0x8907		/* struct timespec */

/* include/uapi/linux/sockios.h — нові */
#define SIOCGSTAMP_NEW		_IOR(SOCK_IOC_TYPE, 0x06, long long[2])
#define SIOCGSTAMPNS_NEW	_IOR(SOCK_IOC_TYPE, 0x07, long long[2])

#if __BITS_PER_LONG == 64 || (defined(__x86_64__) && defined(__ILP32__))
#define SIOCGSTAMP	SIOCGSTAMP_OLD
#else
#define SIOCGSTAMP	((sizeof(struct timeval)) == 8 ? \
			 SIOCGSTAMP_OLD : SIOCGSTAMP_NEW)
#endif
