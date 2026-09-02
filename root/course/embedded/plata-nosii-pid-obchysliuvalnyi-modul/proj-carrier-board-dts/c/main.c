/* main.c — монітор плати-носія: усе, що описав DTS, з простору користувача. */
#include "carrier.h"

#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define HWMON_DRIVER	"tmp102"
#define RTC_DEVICE	"/dev/rtc0"
#define EEPROM_PATH	"/sys/bus/i2c/devices/1-0050/eeprom"
#define GPIO_CHIP	"/dev/gpiochip0"
#define CAN_IFACE	"can0"

/* Дві межі, а не одна: на рівно 60 °C одна межа дала б миготіння. */
#define TRIP_ON		60.0
#define TRIP_OFF	57.0

static volatile sig_atomic_t stop_requested;

static void on_signal(int sig)
{
	(void)sig;
	stop_requested = 1;
}

static void install_handlers(void)
{
	struct sigaction sa;
	memset(&sa, 0, sizeof sa);
	sa.sa_handler = on_signal;
	sigaction(SIGINT, &sa, NULL);
	sigaction(SIGTERM, &sa, NULL);
}

int main(void)
{
	char temp_path[256];
	if (carrier_find_hwmon(HWMON_DRIVER, temp_path, sizeof temp_path) != 0) {
		fprintf(stderr, "Драйвер %s не дав вузла hwmon: %s\n",
			HWMON_DRIVER, strerror(errno));
		fprintf(stderr, "Перевірте sensor@48 у дереві пристроїв і dmesg.\n");
		return EXIT_FAILURE;
	}
	printf("Термодавач: %s\n", temp_path);

	char board_id[33];
	if (carrier_read_board_id(EEPROM_PATH, board_id, sizeof board_id) == 0)
		printf("Табличка з EEPROM: %s\n", board_id);
	else
		fprintf(stderr, "EEPROM 24LC64 недоступна: %s\n", strerror(errno));

	struct tm rtc_now;
	if (carrier_read_rtc(RTC_DEVICE, &rtc_now) == 0) {
		char stamp[64];
		strftime(stamp, sizeof stamp, "%Y-%m-%d %H:%M:%S", &rtc_now);
		printf("Час PCF85063A (UTC): %s\n", stamp);
	} else {
		fprintf(stderr, "RTC %s мовчить: %s\n", RTC_DEVICE, strerror(errno));
	}

	struct carrier_panel *panel = carrier_panel_open(GPIO_CHIP);
	if (!panel) {
		fprintf(stderr, "Лінія аварійного світлодіода: %s\n", strerror(errno));
		return EXIT_FAILURE;
	}
	carrier_panel_report_claimed(panel);

	struct carrier_can can;
	int can_ready = (carrier_can_open(&can, CAN_IFACE) == 0);
	if (!can_ready)
		fprintf(stderr, "CAN %s недоступний (%s) — далі без телеметрії\n",
			CAN_IFACE, strerror(errno));

	install_handlers();
	printf("Моніторинг пішов, зупинка — Ctrl+C\n");

	bool fault = false;
	while (!stop_requested) {
		double celsius = 0.0;
		if (carrier_read_temperature(temp_path, &celsius) != 0) {
			/* Обрив на шині I2C зникає й повертається: не падаємо. */
			fprintf(stderr, "Читання температури: %s\n", strerror(errno));
			sleep(1);
			continue;
		}

		if (!fault && celsius >= TRIP_ON) {
			fault = true;
			printf("УВАГА: перегрів %.2f °C — вмикаємо аварійний світлодіод\n",
			       celsius);
		} else if (fault && celsius <= TRIP_OFF) {
			fault = false;
			printf("Температура в нормі: %.2f °C\n", celsius);
		}

		if (carrier_panel_fault(panel, fault) != 0)
			fprintf(stderr, "GPIO26: %s\n", strerror(errno));

		if (can_ready) {
			if (carrier_can_send_status(&can, celsius, fault) != 0) {
				fprintf(stderr, "CAN передавання: %s\n", strerror(errno));
				if (errno == ENETDOWN || errno == ENODEV) {
					carrier_can_close(&can);
					can_ready = 0;
				}
			}
			/* Пауза циклу — це очікування на шині, а не голий sleep. */
			if (carrier_can_poll(&can, 1000) < 0)
				fprintf(stderr, "CAN приймання: %s\n", strerror(errno));
		} else {
			sleep(1);
		}

		printf("t = %.2f °C, аварія: %s\n", celsius, fault ? "так" : "ні");
		fflush(stdout);
	}

	printf("\nЗупинка: гасимо індикацію, віддаємо лінії й сокет\n");
	carrier_panel_fault(panel, false);
	carrier_panel_close(panel);
	if (can_ready)
		carrier_can_close(&can);
	return EXIT_SUCCESS;
}
