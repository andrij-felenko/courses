/* inspect_devices.c */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

#define PROC_PATH "/proc/device_inventory"
#define CHUNK_SIZE 128

int main(void)
{
	int fd = open(PROC_PATH, O_RDONLY);
	if (fd < 0) {
		perror("open " PROC_PATH);
		return EXIT_FAILURE;
	}

	printf("=== 1. Читання перших 256 байтів ===\n");
	char buf[CHUNK_SIZE];
	ssize_t n;
	int total_bytes = 0;

	while (total_bytes < 256 && (n = read(fd, buf, sizeof(buf) - 1)) > 0) {
		buf[n] = '\0';
		printf("%s", buf);
		total_bytes += n;
	}

	printf("\n=== 2. Перевірка lseek: повернення на початок ===\n");
	off_t new_off = lseek(fd, 0, SEEK_SET);
	if (new_off == (off_t)-1) {
		perror("lseek SEEK_SET");
		close(fd);
		return EXIT_FAILURE;
	}

	n = read(fd, buf, sizeof(buf) - 1);
	if (n > 0) {
		buf[n] = '\0';
		printf("Перший рядок після lseek(0):\n%s\n", buf);
	}

	close(fd);
	return EXIT_SUCCESS;
}
