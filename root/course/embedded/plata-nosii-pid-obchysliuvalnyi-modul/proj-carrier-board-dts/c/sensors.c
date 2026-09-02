/* sensors.c — читання давачів плати-носія через файлові інтерфейси ядра. */
#include "carrier.h"

#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

#include <linux/rtc.h>

/* Атрибути sysfs віддаються одним читанням і закінчуються переводом рядка. */
static int read_attr(const char *path, char *buf, size_t len)
{
	int fd = open(path, O_RDONLY | O_CLOEXEC);
	if (fd < 0)
		return -1;

	ssize_t n = read(fd, buf, len - 1);
	int saved = errno;
	close(fd);

	if (n <= 0) {
		errno = (n == 0) ? EIO : saved;
		return -1;
	}

	buf[n] = '\0';
	char *nl = strchr(buf, '\n');
	if (nl)
		*nl = '\0';
	return 0;
}

int carrier_find_hwmon(const char *driver_name, char *path, size_t path_len)
{
	DIR *dir = opendir("/sys/class/hwmon");
	if (!dir)
		return -1;

	int rc = -1;
	struct dirent *ent;
	while ((ent = readdir(dir)) != NULL) {
		if (strncmp(ent->d_name, "hwmon", 5) != 0)
			continue;

		char name_path[256];
		char name[64];
		snprintf(name_path, sizeof name_path,
			 "/sys/class/hwmon/%s/name", ent->d_name);
		if (read_attr(name_path, name, sizeof name) != 0)
			continue;
		if (strcmp(name, driver_name) != 0)
			continue;

		snprintf(path, path_len,
			 "/sys/class/hwmon/%s/temp1_input", ent->d_name);
		rc = 0;
		break;
	}

	closedir(dir);
	if (rc != 0)
		errno = ENODEV;	/* драйвер не зв'язався з вузлом sensor@48 */
	return rc;
}

int carrier_read_temperature(const char *temp_path, double *celsius)
{
	char buf[32];
	if (read_attr(temp_path, buf, sizeof buf) != 0)
		return -1;

	errno = 0;
	char *end = NULL;
	long milli = strtol(buf, &end, 10);
	if (errno != 0 || end == buf) {
		errno = EINVAL;
		return -1;
	}

	/* hwmon завжди міряє в тисячних градуса, незалежно від давача. */
	*celsius = milli / 1000.0;
	return 0;
}

int carrier_read_rtc(const char *rtc_dev, struct tm *out)
{
	int fd = open(rtc_dev, O_RDONLY | O_CLOEXEC);
	if (fd < 0)
		return -1;

	struct rtc_time rt;
	memset(&rt, 0, sizeof rt);
	if (ioctl(fd, RTC_RD_TIME, &rt) < 0) {
		int saved = errno;
		close(fd);
		errno = saved;
		return -1;
	}
	close(fd);

	/* struct rtc_time повторює поля struct tm, але не має tm_isdst
	   і не гарантує решти — тож переносимо поле за полем. */
	memset(out, 0, sizeof *out);
	out->tm_sec = rt.tm_sec;
	out->tm_min = rt.tm_min;
	out->tm_hour = rt.tm_hour;
	out->tm_mday = rt.tm_mday;
	out->tm_mon = rt.tm_mon;
	out->tm_year = rt.tm_year;
	out->tm_isdst = -1;
	return 0;
}

int carrier_read_board_id(const char *eeprom_path, char *buf, size_t buf_len)
{
	int fd = open(eeprom_path, O_RDONLY | O_CLOEXEC);
	if (fd < 0)
		return -1;

	ssize_t n = read(fd, buf, buf_len - 1);
	int saved = errno;
	close(fd);

	if (n < 0) {
		errno = saved;
		return -1;
	}

	/* Файл eeprom бінарний: на початку сторінки лежить текстова табличка,
	   далі — сміття або нулі. Непридатне для друку замінюємо крапками. */
	for (ssize_t i = 0; i < n; i++) {
		unsigned char c = (unsigned char)buf[i];
		if (c < 0x20 || c > 0x7e)
			buf[i] = '.';
	}
	buf[n] = '\0';
	return 0;
}
