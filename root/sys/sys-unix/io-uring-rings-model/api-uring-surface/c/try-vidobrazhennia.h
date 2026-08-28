/* розміри рахують так і тільки так — константи тут не працюють */
size_t sring_sz = p.sq_off.array + p.sq_entries * sizeof(__u32);
size_t cring_sz = p.cq_off.cqes  + p.cq_entries * sizeof(struct io_uring_cqe);

/* із IORING_FEAT_SINGLE_MMAP — одне відображення на більший із двох розмірів */
if (cring_sz > sring_sz) sring_sz = cring_sz;

void *ring = mmap(NULL, sring_sz, PROT_READ | PROT_WRITE,
                  MAP_SHARED | MAP_POPULATE, ring_fd, IORING_OFF_SQ_RING);
void *sqes = mmap(NULL, p.sq_entries * sizeof(struct io_uring_sqe),
                  PROT_READ | PROT_WRITE,
                  MAP_SHARED | MAP_POPULATE, ring_fd, IORING_OFF_SQES);
