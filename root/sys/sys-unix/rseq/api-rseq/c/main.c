#define _GNU_SOURCE
#include <errno.h>
#include <linux/rseq.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/auxv.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef AT_RSEQ_FEATURE_SIZE
#define AT_RSEQ_FEATURE_SIZE 27
#endif

#define RSEQ_SIG 0x53053053                       /* x86 */
#define OFFSETOFEND(t, f) (offsetof(t, f) + sizeof(((t *)0)->f))

/* Слабкі — щоб код лінкувався і з glibc без підтримки rseq. */
extern __attribute__((weak)) ptrdiff_t    __rseq_offset;
extern __attribute__((weak)) unsigned int __rseq_size;

/* Запасний варіант: власна табличка, якщо glibc своєї не зареєструвала. */
static __thread struct rseq own_area __attribute__((aligned(32))) = {
    .cpu_id = RSEQ_CPU_ID_UNINITIALIZED,
};
static __thread int own_state;                    /* 0 — не пробували, 1 — є, -1 — не вийшло */

static struct rseq *rseq_area(void)
{
    if (&__rseq_size != NULL && __rseq_size != 0)
        return (struct rseq *)((char *)__builtin_thread_pointer() + __rseq_offset);

    if (own_state == 0) {
        long rc = syscall(SYS_rseq, &own_area, sizeof(own_area), 0, RSEQ_SIG);
        own_state = (rc == 0) ? 1 : -1;           /* ENOSYS / EINVAL / EFAULT */
    }
    return own_state == 1 ? &own_area : NULL;
}

/* Нуль у допоміжному векторі означає ядро до 6.3: описано 20 байтів. */
static unsigned int feature_size(void)
{
    unsigned long v = getauxval(AT_RSEQ_FEATURE_SIZE);
    return v ? (unsigned int)v : 20u;
}

int main(void)
{
    struct rseq *r = rseq_area();
    if (r == NULL) {
        fprintf(stderr, "rseq недоступний\n");
        return 1;
    }

    printf("cpu_id_start = %u\n", r->cpu_id_start);
    printf("cpu_id       = %d\n", (int32_t)r->cpu_id);   /* -1 і -2 — стани, не номери */

    if (feature_size() >= OFFSETOFEND(struct rseq, mm_cid))
        printf("node_id = %u, mm_cid = %u\n", r->node_id, r->mm_cid);

    return 0;
}
