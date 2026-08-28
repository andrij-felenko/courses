/* i3c_user_app.c - Приклад користувацької програми на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/types.h>

/* Структура приватного переказу для ioctl у користувацькому просторі */
struct i3c_ioc_priv_xfer {
	__u16 len;
	__u8 rnw;
	__u8 pad;
	__u64 data;
};

#define I3C_IOC_MAGIC 'I'
#define I3C_IOC_PRIV_XFER(n) _IOC(_IOC_WRITE, I3C_IOC_MAGIC, 0x01, (n) * sizeof(struct i3c_ioc_priv_xfer))

int main(void)
{
	int fd = open("/dev/i3c-0", O_RDWR);
	if (fd < 0) {
		perror("Не вдалося відкрити /dev/i3c-0");
		return 1;
	}

	uint8_t reg_addr = 0x0A;
	uint8_t read_buf[4] = {0};

	struct i3c_ioc_priv_xfer xfers[2] = {
		{
			.len = 1,
			.rnw = 0, /* Запис адреси регістра */
			.data = (uintptr_t)&reg_addr,
		},
		{
			.len = sizeof(read_buf),
			.rnw = 1, /* Читання даних */
			.data = (uintptr_t)read_buf,
		}
	};

	if (ioctl(fd, I3C_IOC_PRIV_XFER(2), xfers) < 0) {
		perror("Помилка виконання ioctl I3C_IOC_PRIV_XFER");
		close(fd);
		return 2;
	}

	printf("Прочитано значення: 0x%02X 0x%02X 0x%02X 0x%02X\n",
	       read_buf[0], read_buf[1], read_buf[2], read_buf[3]);

	close(fd);
	return 0;
}
