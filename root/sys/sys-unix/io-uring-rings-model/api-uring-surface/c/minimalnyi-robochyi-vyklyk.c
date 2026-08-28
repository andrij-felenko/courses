#define _GNU_SOURCE
#include <linux/io_uring.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

int main(void)
{
    struct io_uring_params p;
    memset(&p, 0, sizeof p);                        /* resv мусить бути нулем */

    int fd = (int)syscall(__NR_io_uring_setup, 8, &p);
    if (fd < 0) { perror("io_uring_setup"); return 1; }
    if (!(p.features & IORING_FEAT_SINGLE_MMAP) ||   /* 5.4: одне відображення  */
        !(p.features & IORING_FEAT_RW_CUR_POS)) {    /* 5.6: off = −1           */
        fprintf(stderr, "заслабке ядро: треба одне відображення й off = −1\n");
        return 1;
    }

    size_t sz = p.sq_off.array + p.sq_entries * sizeof(__u32);
    size_t cz = p.cq_off.cqes  + p.cq_entries * sizeof(struct io_uring_cqe);
    if (cz > sz) sz = cz;

    char *ring = mmap(NULL, sz, PROT_READ | PROT_WRITE,
                      MAP_SHARED | MAP_POPULATE, fd, IORING_OFF_SQ_RING);
    struct io_uring_sqe *sqes =
        mmap(NULL, p.sq_entries * sizeof(*sqes), PROT_READ | PROT_WRITE,
             MAP_SHARED | MAP_POPULATE, fd, IORING_OFF_SQES);

    unsigned *sq_tail  = (unsigned *)(ring + p.sq_off.tail);
    unsigned *sq_mask  = (unsigned *)(ring + p.sq_off.ring_mask);
    unsigned *sq_array = (unsigned *)(ring + p.sq_off.array);
    unsigned *cq_head  = (unsigned *)(ring + p.cq_off.head);
    unsigned *cq_tail  = (unsigned *)(ring + p.cq_off.tail);
    unsigned *cq_mask  = (unsigned *)(ring + p.cq_off.ring_mask);
    struct io_uring_cqe *cqes = (struct io_uring_cqe *)(ring + p.cq_off.cqes);

    static char buf[4096];
    unsigned tail = *sq_tail, i = tail & *sq_mask;

    memset(&sqes[i], 0, sizeof sqes[i]);            /* поля — об'єднання: нулюємо все */
    sqes[i].opcode    = IORING_OP_READ;
    sqes[i].fd        = 0;                          /* стандартний ввід          */
    sqes[i].off       = (__u64)-1;                  /* поточна позиція файлу     */
    sqes[i].addr      = (__u64)(uintptr_t)buf;
    sqes[i].len       = sizeof buf;
    sqes[i].user_data = 0x1234;

    sq_array[i] = i;
    __atomic_store_n(sq_tail, tail + 1, __ATOMIC_RELEASE);   /* запис-звільнення */

    /* один перехід межі: подати рівно 1 і дочекатися рівно 1 завершення */
    if (syscall(__NR_io_uring_enter, fd, 1, 1, IORING_ENTER_GETEVENTS, NULL, 0) < 0)
        { perror("io_uring_enter"); return 1; }

    unsigned t = __atomic_load_n(cq_tail, __ATOMIC_ACQUIRE); /* читання-захоплення */
    while (*cq_head != t) {
        struct io_uring_cqe *c = &cqes[*cq_head & *cq_mask];
        printf("user_data=0x%llx res=%d flags=0x%x\n",
               (unsigned long long)c->user_data, c->res, c->flags);
        __atomic_store_n(cq_head, *cq_head + 1, __ATOMIC_RELEASE);
    }
    return 0;
}
