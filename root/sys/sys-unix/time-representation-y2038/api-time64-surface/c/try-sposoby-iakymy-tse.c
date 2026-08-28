/* include/uapi/asm-generic/sembuf.h */

struct semid64_ds {
	struct ipc64_perm sem_perm;
#if __BITS_PER_LONG == 64
	long		sem_otime;	/* last semop time */
	long		sem_ctime;	/* last change time */
#else
	unsigned long	sem_otime;	/* молодші 32 біти */
	unsigned long	sem_otime_high;	/* колишнє __unused1 */
	unsigned long	sem_ctime;
	unsigned long	sem_ctime_high;	/* колишнє __unused2 */
#endif
	unsigned long	sem_nsems;
	unsigned long	__unused3;
	unsigned long	__unused4;
};
