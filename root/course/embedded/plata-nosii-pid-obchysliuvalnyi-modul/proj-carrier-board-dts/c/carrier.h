/* carrier.h — інтерфейс монітора плати-носія.
 * Кожен вузол дерева пристроїв виходить у простір користувача своєю
 * підсистемою: TMP102 -> hwmon, PCF85063A -> rtc, 24LC64 -> at24 (sysfs),
 * MCP2518FD -> SocketCAN, вільна лінія GPIO -> libgpiod.
 *
 * Домовленість про помилки: 0 — успіх, -1 — збій, причина в errno.
 */
#ifndef CARRIER_H
#define CARRIER_H

#include <stdbool.h>
#include <stddef.h>
#include <time.h>

/* --- давачі (sensors.c) --- */

/* Шукає теку hwmon за іменем драйвера й складає шлях до temp1_input:
   номер hwmonN залежить від порядку probe і між завантаженнями їздить. */
int carrier_find_hwmon(const char *driver_name, char *path, size_t path_len);
int carrier_read_temperature(const char *temp_path, double *celsius);
int carrier_read_rtc(const char *rtc_dev, struct tm *out);
int carrier_read_board_id(const char *eeprom_path, char *buf, size_t buf_len);

/* --- індикація (indicator.c) --- */

struct carrier_panel;	/* непрозорий: усередині chip і лінії libgpiod */

struct carrier_panel *carrier_panel_open(const char *chip_path);
void carrier_panel_close(struct carrier_panel *panel);
int carrier_panel_fault(struct carrier_panel *panel, bool on);
/* Друкує, хто тримає лінії, віддані ядру в DTS, — швидка перевірка,
   що gpio-leds і gpio-keys справді зв'язалися зі своїм залізом. */
void carrier_panel_report_claimed(struct carrier_panel *panel);

/* --- CAN-шина (canlink.c) --- */

struct carrier_can {
	int fd;
};

int carrier_can_open(struct carrier_can *can, const char *ifname);
void carrier_can_close(struct carrier_can *can);
int carrier_can_send_status(struct carrier_can *can, double celsius, bool fault);
/* 1 — кадр прийнято й надруковано, 0 — тайм-аут, -1 — помилка. */
int carrier_can_poll(struct carrier_can *can, int timeout_ms);

#endif /* CARRIER_H */
