/* rseqcount.c — лічильник подій, розкладений по ядрах процесора.
   Збірка: gcc -O2 -pthread -o rseqcount rseqcount.c
   Запуск: ./rseqcount <потоків> <приростів на потік>              */
#define _GNU_SOURCE
#include <errno.h>
#include <pthread.h>
#include <sched.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/auxv.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

/* Табличку описуємо самі: linux/rseq.h є не в кожній системі,
   а розкладка полів — стала частина двійкового інтерфейсу ядра. */
struct rseq_area {
	uint32_t cpu_id_start;   /* пише ядро; це число вживаємо в ділянці  */
	uint32_t cpu_id;         /* пише ядро; −1 = ще не зареєстровано     */
	uint64_t rseq_cs;        /* пише програма: вказівник на дескриптор  */
	uint32_t flags;
	uint32_t node_id;        /* дописано пізніше за перші чотири поля */
	uint32_t mm_cid;         /* з Linux 6.3                          */
} __attribute__((aligned(32)));

#ifndef __NR_rseq
# define __NR_rseq 334                     /* x86-64 */
#endif
#ifndef AT_RSEQ_FEATURE_SIZE
# define AT_RSEQ_FEATURE_SIZE 27
#endif
#define RSEQ_FLAG_UNREGISTER (1u << 0)
#define RSEQ_SIG 0x53053053u               /* той самий, що в glibc і librseq */

/* Символи glibc ≥ 2.35. Слабкі — щоб програма зібралася й запустилася там,
   де їх немає: адреса відсутнього слабкого символу дорівнює нулю. */
extern __attribute__((weak)) ptrdiff_t    __rseq_offset;
extern __attribute__((weak)) unsigned int __rseq_size;

static inline char *thread_pointer(void)
{
#if defined(__x86_64__)
	char *tp;
	__asm__ ("movq %%fs:0, %0" : "=r" (tp));
	return tp;
#else
	return (char *)__builtin_thread_pointer();
#endif
}

static long sys_rseq(struct rseq_area *a, uint32_t len, int flags, uint32_t sig)
{
	return syscall(__NR_rseq, a, len, flags, sig);
}

/* Скільки байтів полів насправді підтримує ядро. */
static unsigned kernel_feature_size(void)
{
	unsigned long v = getauxval(AT_RSEQ_FEATURE_SIZE);
	return v ? (unsigned)v : 20;           /* нуль = ядро старше за 6.3 */
}

static __thread struct rseq_area own_area = { .cpu_id = (uint32_t)-1 };
static __thread struct rseq_area *area;    /* та табличка, з якою працюємо */
static __thread int own_registered;

/* Викликає КОЖЕН потік на старті. 0 — ділянки доступні, −1 — ні. */
static int rseq_thread_init(void)
{
	if (&__rseq_size != NULL && __rseq_size != 0) {
		area = (struct rseq_area *)(thread_pointer() + __rseq_offset);
		return 0;                          /* табличка вже є, беремо чужу */
	}
	/* rseq_len мусить бути не менший за 32 і адреса — вирівняна на 32. */
	if (sys_rseq(&own_area, 32, 0, RSEQ_SIG) != 0)
		return -1;                         /* ENOSYS, EINVAL, EFAULT — байдуже */
	own_registered = 1;
	area = &own_area;
	return 0;
}

static void rseq_thread_fini(void)
{
	if (own_registered) {
		sys_rseq(&own_area, 32, RSEQ_FLAG_UNREGISTER, RSEQ_SIG);
		own_registered = 0;
	}
	area = NULL;
}
