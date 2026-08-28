/* Комірка на кожен номер ядра процесора. Крок — 128 байтів, тобто два
   рядки кеша: щоб сусідні комірки не тягли одна одну ані самим рядком,
   ані випереджальним читанням наступного. */
#define SLOT_STRIDE_LONGS 16               /* 16 · 8 = 128 байтів */

static long *counters;                     /* nr_slots · 16 елементів */
static unsigned nr_slots;

/* Приріст counters[cpu · 16] без жодної атомарної команди. */
static void percpu_inc(void)
{
	struct rseq_area *rs = area;
	long *cnt = counters;

	for (;;) {
		__asm__ __volatile__ goto (
		    /* Дескриптор — стала в окремій секції, не на гарячому шляху. */
		    ".pushsection __rseq_cs, \"aw\"\n\t"
		    ".balign 32\n\t"
		    "1:\t.long 0, 0\n\t"                 /* version = 0, flags = 0 */
		    "\t.quad 2f, 3f - 2f, 4f\n\t"        /* start_ip, довжина, abort_ip */
		    ".popsection\n\t"

		    /* Оголошення ділянки: один звичайний запис вказівника. */
		    "leaq 1b(%%rip), %%rax\n\t"
		    "movq %%rax, 8(%[rs])\n\t"           /* rs->rseq_cs */

		    "2:\n\t"                             /* ─── початок ділянки ─── */
		    "movl (%[rs]), %%eax\n\t"            /* rs->cpu_id_start        */
		    "shlq $4, %%rax\n\t"                 /* крок комірки            */
		    "movq (%[cnt],%%rax,8), %%rcx\n\t"
		    "addq $1, %%rcx\n\t"
		    "movq %%rcx, (%[cnt],%%rax,8)\n\t"   /* ЗАВЕРШАЛЬНИЙ ЗАПИС      */
		    "3:\n\t"                             /* ─── кінець ділянки ──── */

		    /* Обробник зриву — поза діапазоном, з підписом перед міткою. */
		    ".pushsection .text.rseq_abort, \"ax\"\n\t"
		    ".byte 0x0f, 0xb9, 0x3d\n\t"         /* ud1 0x53053053(%rip),%edi */
		    ".long 0x53053053\n\t"
		    "4:\n\t"
		    "jmp %l[restart]\n\t"
		    ".popsection\n\t"
		    : : [rs] "r" (rs), [cnt] "r" (cnt)
		    : "rax", "rcx", "memory"
		    : restart);
		return;                                  /* дійшли до кінця */
	restart: ;                                   /* ядро зірвало — ще раз */
	}
}
