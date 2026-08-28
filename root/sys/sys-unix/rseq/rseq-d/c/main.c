/* Приріст counters[cpu] без жодної атомарної команди.
   rs — зареєстрована табличка цього потоку. */
static void percpu_inc(struct rseq *rs, long *counters)
{
	for (;;) {
		__asm__ __volatile__ goto (
		    /* Дескриптор — стала, лежить у своїй секції, не на гарячому шляху. */
		    ".pushsection __rseq_cs, \"aw\"\n\t"
		    ".balign 32\n\t"
		    "1:\t.long 0, 0\n\t"               /* version = 0, flags = 0      */
		    "\t.quad 2f, 3f - 2f, 4f\n\t"      /* start_ip, довжина, abort_ip */
		    ".popsection\n\t"

		    /* Оголошення ділянки: один звичайний запис вказівника. */
		    "leaq 1b(%%rip), %%rax\n\t"
		    "movq %%rax, 8(%[rs])\n\t"         /* rs->rseq_cs                 */

		    /* ─── початок ділянки ─────────────────────────────── */
		    "2:\n\t"
		    "movl (%[rs]), %%eax\n\t"          /* rs->cpu_id_start            */
		    "movq (%[cnt],%%rax,8), %%rcx\n\t" /* counters[cpu]               */
		    "addq $1, %%rcx\n\t"
		    "movq %%rcx, (%[cnt],%%rax,8)\n\t" /* ЗАВЕРШАЛЬНИЙ ЗАПИС          */
		    "3:\n\t"
		    /* ─── кінець ділянки ──────────────────────────────── */

		    /* Обробник зриву — поза ділянкою, з підписом перед міткою. */
		    ".pushsection .text.rseq_abort, \"ax\"\n\t"
		    ".byte 0x0f, 0xb9, 0x3d\n\t"       /* ud1 0x53053053(%rip), %edi  */
		    ".long 0x53053053\n\t"             /* той самий sig, що в rseq(2) */
		    "4:\n\t"
		    "jmp %l[restart]\n\t"
		    ".popsection\n\t"
		    : : [rs] "r" (rs), [cnt] "r" (counters)
		    : "rax", "rcx", "memory"
		    : restart);
		return;                 /* ділянка дійшла до кінця */
	restart: ;                      /* ядро закинуло нас сюди — пробуємо ще */
	}
}
