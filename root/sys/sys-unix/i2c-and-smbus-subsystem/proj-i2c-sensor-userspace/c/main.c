#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

#define I2C_DEV_PATH     "/dev/i2c-1"
#define BMP280_ADDR      0x76
#define BMP280_REG_ID    0xD0
#define BMP280_REG_CTRL  0xF4
#define BMP280_REG_DATA  0xF7
#define BMP280_EXPECT_ID 0x58

/* Читання Chip ID через виклик I2C_RDWR з Repeated START */
static int bmp280_read_id(int fd, uint8_t *chip_id)
{
	uint8_t reg = BMP280_REG_ID;
	struct i2c_msg msgs[2];
	struct i2c_rdwr_ioctl_data rdwr;

	/* Повідомлення 1: Запис адреси цільового регістра */
	msgs[0].addr  = BMP280_ADDR;
	msgs[0].flags = 0;
	msgs[0].len   = 1;
	msgs[0].buf   = &reg;

	/* Повідомлення 2: Зчитування 1 байта значення */
	msgs[1].addr  = BMP280_ADDR;
	msgs[1].flags = I2C_M_RD;
	msgs[1].len   = 1;
	msgs[1].buf   = chip_id;

	rdwr.msgs  = msgs;
	rdwr.nmsgs = 2;

	if (ioctl(fd, I2C_RDWR, &rdwr) < 0)
		return -errno;

	return 0;
}

/* Запис 1 байта конфігурації у регістр пристрою */
static int bmp280_write_reg(int fd, uint8_t reg, uint8_t val)
{
	uint8_t buf[2] = { reg, val };
	struct i2c_msg msg;
	struct i2c_rdwr_ioctl_data rdwr;

	msg.addr  = BMP280_ADDR;
	msg.flags = 0;
	msg.len   = 2;
	msg.buf   = buf;

	rdwr.msgs  = &msg;
	rdwr.nmsgs = 1;

	if (ioctl(fd, I2C_RDWR, &rdwr) < 0)
		return -errno;

	return 0;
}

/* Зчитування блоку вимірювань (6 байтів: тиск + температура) */
static int bmp280_read_measurements(int fd, uint8_t raw_data[6])
{
	uint8_t reg = BMP280_REG_DATA;
	struct i2c_msg msgs[2];
	struct i2c_rdwr_ioctl_data rdwr;

	msgs[0].addr  = BMP280_ADDR;
	msgs[0].flags = 0;
	msgs[0].len   = 1;
	msgs[0].buf   = &reg;

	msgs[1].addr  = BMP280_ADDR;
	msgs[1].flags = I2C_M_RD;
	msgs[1].len   = 6;
	msgs[1].buf   = raw_data;

	rdwr.msgs  = msgs;
	rdwr.nmsgs = 2;

	if (ioctl(fd, I2C_RDWR, &rdwr) < 0)
		return -errno;

	return 0;
}

int main(void)
{
	int fd;
	unsigned long funcs;
	uint8_t chip_id = 0;
	uint8_t raw_data[6];

	fd = open(I2C_DEV_PATH, O_RDWR);
	if (fd < 0) {
		fprintf(stderr, "Помилка відкриття %s: %s\n", I2C_DEV_PATH, strerror(errno));
		return EXIT_FAILURE;
	}

	/* Перевірка підтримки атомарних транзакцій адаптером */
	if (ioctl(fd, I2C_FUNCS, &funcs) < 0) {
		fprintf(stderr, "Не вдалося отримати можливості адаптера: %s\n", strerror(errno));
		close(fd);
		return EXIT_FAILURE;
	}

	if (!(funcs & I2C_FUNC_I2C)) {
		fprintf(stderr, "Шинний адаптер не підтримує сирі I2C транзакції I2C_RDWR\n");
		close(fd);
		return EXIT_FAILURE;
	}

	/* Перевірка зв'язку з чипом */
	if (bmp280_read_id(fd, &chip_id) < 0) {
		fprintf(stderr, "Помилка зв'язку з BMP280 на адресі 0x%02X: %s\n",
			BMP280_ADDR, strerror(errno));
		close(fd);
		return EXIT_FAILURE;
	}

	printf("Знайдено чип з ID: 0x%02X (очікувався: 0x%02X)\n", chip_id, BMP280_EXPECT_ID);

	/* Налаштування: Normal Mode, оверсемплінг температури x2, тиску x16 */
	if (bmp280_write_reg(fd, BMP280_REG_CTRL, 0x57) < 0) {
		fprintf(stderr, "Помилка конфігурації сенсора: %s\n", strerror(errno));
		close(fd);
		return EXIT_FAILURE;
	}

	usleep(50000); /* Очікування завершення першого циклу вимірювання */

	if (bmp280_read_measurements(fd, raw_data) < 0) {
		fprintf(stderr, "Помилка зчитування результатів вимірювання: %s\n", strerror(errno));
		close(fd);
		return EXIT_FAILURE;
	}

	/* Декодування сирих 20-бітних відліків */
	int32_t raw_press = ((int32_t)raw_data[0] << 12) | ((int32_t)raw_data[1] << 4) | ((int32_t)raw_data[2] >> 4);
	int32_t raw_temp  = ((int32_t)raw_data[3] << 12) | ((int32_t)raw_data[4] << 4) | ((int32_t)raw_data[5] >> 4);

	printf("Сирі відліки: Температура = %d, Тиск = %d\n", raw_temp, raw_press);

	close(fd);
	return EXIT_SUCCESS;
}
