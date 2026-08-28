/* inspect_lsm.c */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <stdint.h>
#include <errno.h>

#ifndef __NR_lsm_list_modules
#define __NR_lsm_list_modules 461
#endif

int main(void)
{
	uint64_t ids[16];
	uint32_t size = sizeof(ids);

	/* Запитуємо у ядра масив ідентифікаторів активованих модулів LSM */
	long count = syscall(__NR_lsm_list_modules, ids, &size, 0);

	if (count < 0) {
		if (errno == ENOSYS) {
			printf("Системний виклик lsm_list_modules відсутній (потрібне ядро >= 6.8)\n");
		} else {
			perror("Помилка виконання lsm_list_modules");
		}
		return 1;
	}

	printf("Кількість активних модулів LSM у стеку: %ld\n", count);
	for (long i = 0; i < count; i++) {
		printf("  [%ld] Module LSM ID: 0x%lx\n", i, (unsigned long)ids[i]);
	}

	return 0;
}
