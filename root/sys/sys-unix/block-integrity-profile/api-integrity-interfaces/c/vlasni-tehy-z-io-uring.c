/* include/uapi/linux/io_uring.h */
#define IORING_RW_ATTR_FLAG_PI	(1U << 0)

struct io_uring_attr_pi {
	__u16	flags;    /* IO_INTEGRITY_CHK_* — які саме перевірки вимагати */
	__u16	app_tag;  /* прикладний тег */
	__u32	len;      /* довжина буфера з тегами, байтів */
	__u64	addr;     /* сам буфер з тегами */
	__u64	seed;     /* посилальний тег першого блока запиту */
	__u64	rsvd;     /* мусить бути 0 */
};

/* include/uapi/linux/fs.h */
#define IO_INTEGRITY_CHK_GUARD	(1U << 0)
#define IO_INTEGRITY_CHK_REFTAG	(1U << 1)
#define IO_INTEGRITY_CHK_APPTAG	(1U << 2)
