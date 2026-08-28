struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
io_uring_prep_read(sqe, fd, data, 4096, offset);   /* fd відкрито з O_DIRECT */

struct io_uring_attr_pi pi = {
	.flags   = IO_INTEGRITY_CHK_GUARD | IO_INTEGRITY_CHK_REFTAG,
	.app_tag = 0,
	.addr    = (__u64)(uintptr_t)meta,   /* nblocks × metadata_size байтів */
	.len     = nblocks * 8,
	.seed    = lba,                      /* очікуваний посилальний тег першого блока */
	.rsvd    = 0,
};
sqe->attr_ptr       = (__u64)(uintptr_t)&pi;
sqe->attr_type_mask = IORING_RW_ATTR_FLAG_PI;
