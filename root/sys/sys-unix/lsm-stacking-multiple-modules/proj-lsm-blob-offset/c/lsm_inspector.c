/* lsm_inspector.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <errno.h>
#include <stdint.h>

#ifndef __NR_lsm_list_modules
#define __NR_lsm_list_modules 461
#endif

#ifndef __NR_lsm_get_self_attr
#define __NR_lsm_get_self_attr 459
#endif

static void inspect_sysfs_lsm(void)
{
	int fd = open("/sys/kernel/security/lsm", O_RDONLY);
	if (fd < 0) {
		perror("open /sys/kernel/security/lsm failed");
		return;
	}

	char buffer[512];
	ssize_t bytes_read = read(fd, buffer, sizeof(buffer) - 1);
	close(fd);

	if (bytes_read > 0) {
		buffer[bytes_read] = '\0';
		/* Видаляємо символ переходу рядка наприкінці */
		char *newline = strchr(buffer, '\n');
		if (newline) *newline = '\0';
		printf("[sysfs] Активні модулі LSM (порядок виконання): %s\n", buffer);
	}
}

static void inspect_syscall_lsm(void)
{
	uint64_t ids[16];
	uint32_t size = sizeof(ids);

	long ret = syscall(__NR_lsm_list_modules, ids, &size, 0);
	if (ret < 0) {
		if (errno == ENOSYS) {
			printf("[syscall] lsm_list_modules не підтримується цим ядром (< 6.8).\n");
		} else {
			perror("[syscall] lsm_list_modules failed");
		}
		return;
	}

	printf("[syscall] Виявлено %ld активних модулів (IDs):\n", ret);
	for (long i = 0; i < ret; i++) {
		printf("  - Module [%ld]: ID 0x%lx\n", i, (unsigned long)ids[i]);
	}
}

int main(void)
{
	printf("=== Інспектор стеку Linux Security Modules (C Interface) ===\n");
	inspect_sysfs_lsm();
	inspect_syscall_lsm();
	return 0;
}
