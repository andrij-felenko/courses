/* probe.c — друкує один рядок орієнтирів адресного простору цього процесу.
 *
 *   cc -O2 -Wall -Wextra -fPIE -pie -o probe probe.c        (glibc ≥ 2.34)
 *   cc -O2 -Wall -Wextra -fPIE -pie -o probe probe.c -ldl   (старіші glibc)
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <link.h>
#include <stdio.h>
#include <string.h>
#include <sys/auxv.h>
#include <sys/syscall.h>
#include <unistd.h>

int main(int argc, char **argv)
{
	/* Межу купи знімаємо ПЕРШОЮ дією. Будь-який malloc — зокрема той,
	   яким stdio заводить буфер під перший же printf, — здатний зсунути
	   brk, і тоді ми виміряємо власний виклик, а не жереб ядра.
	   Сирий системний виклик, а не sbrk(0): обгортка тримає значення
	   в своїй змінній і може віддати кеш замість спитати ядро. */
	unsigned long brk0 = (unsigned long) syscall(SYS_brk, 0);

	volatile char anchor = 0;              /* локальна змінна = орієнтир стека */
	unsigned long stack = (unsigned long) &anchor;

	unsigned long entry = getauxval(AT_ENTRY);        /* точка входу програми */
	unsigned long vdso  = getauxval(AT_SYSINFO_EHDR); /* база vDSO            */
	unsigned long ldso  = getauxval(AT_BASE);         /* база ld-linux.so     */

	/* Символ шукаємо САМЕ в libc, а не «десь у програмі»: інакше легко
	   дістати канонічний перехідник із власного файлу замість адреси
	   в бібліотеці. RTLD_NOLOAD нічого не завантажує — лише бере ручку
	   до вже відображеного об'єкта. */
	unsigned long sym = 0, base = 0;
	const char *path = "?";
	void *h = dlopen("libc.so.6", RTLD_LAZY | RTLD_NOLOAD);
	if (h != NULL) {
		struct link_map *lm = NULL;
		sym = (unsigned long) dlsym(h, "printf");
		if (dlinfo(h, RTLD_DI_LINKMAP, &lm) == 0 && lm != NULL) {
			base = (unsigned long) lm->l_addr;
			path = lm->l_name;
		}
	}

	if (argc > 1 && strcmp(argv[1], "-v") == 0)
		fprintf(stderr, "відображений файл: %s\nзсув printf у ньому: %#lx\n",
		        path, sym - base);

	printf("libc=%#lx libcsym=%#lx entry=%#lx stack=%#lx brk=%#lx "
	       "vdso=%#lx ldso=%#lx\n",
	       base, sym, entry, stack, brk0, vdso, ldso);
	return 0;
}
