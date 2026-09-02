/* indicator.c — аварійний світлодіод через символьний пристрій libgpiod. */
#include "carrier.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <gpiod.h>

#define LINE_FAULT_LED	26
#define LINE_HEARTBEAT	16
#define LINE_BUTTON	17
#define CONSUMER	"carrier-monitor"

struct carrier_panel {
	struct gpiod_chip *chip;
	struct gpiod_line *fault;
	int fault_state;
};

/* Друкує, хто вже тримає лінію. Ядро підписується назвою вузла з DTS,
   тож порожній власник означає, що gpio-leds або gpio-keys не зв'язалися. */
static void report_line(struct gpiod_chip *chip, unsigned int offset,
			const char *expected)
{
	struct gpiod_line *line = gpiod_chip_get_line(chip, offset);
	if (!line) {
		fprintf(stderr, "GPIO%u: лінію не прочитати: %s\n",
			offset, strerror(errno));
		return;
	}

	if (gpiod_line_is_used(line)) {
		const char *who = gpiod_line_consumer(line);
		printf("GPIO%u зайнято ядром (%s), очікували %s\n",
		       offset, who ? who : "невідомо", expected);
	} else {
		printf("GPIO%u вільна — вузол %s у дереві не спрацював\n",
		       offset, expected);
	}
}

struct carrier_panel *carrier_panel_open(const char *chip_path)
{
	struct carrier_panel *panel = calloc(1, sizeof *panel);
	if (!panel)
		return NULL;

	panel->chip = gpiod_chip_open(chip_path);
	if (!panel->chip) {
		int saved = errno;
		free(panel);
		errno = saved;
		return NULL;
	}

	panel->fault = gpiod_chip_get_line(panel->chip, LINE_FAULT_LED);
	if (!panel->fault)
		goto fail;

	/* Якщо GPIO26 усе-таки описали в gpio-leds, запит поверне -EBUSY:
	   лінія має рівно одного власника. */
	if (gpiod_line_request_output(panel->fault, CONSUMER, 0) < 0)
		goto fail;

	panel->fault_state = 0;
	return panel;

fail: {
		int saved = errno;
		gpiod_chip_close(panel->chip);
		free(panel);
		errno = saved;
		return NULL;
	}
}

void carrier_panel_close(struct carrier_panel *panel)
{
	if (!panel)
		return;

	/* Ядро звільнило б лінію й саме — при закритті дескриптора, навіть
	   якби процес упав; гасимо явно, щоб не лишити світлодіод горіти. */
	gpiod_line_set_value(panel->fault, 0);
	gpiod_line_release(panel->fault);
	gpiod_chip_close(panel->chip);
	free(panel);
}

int carrier_panel_fault(struct carrier_panel *panel, bool on)
{
	int value = on ? 1 : 0;
	if (value == panel->fault_state)
		return 0;

	if (gpiod_line_set_value(panel->fault, value) < 0)
		return -1;

	panel->fault_state = value;
	return 0;
}

void carrier_panel_report_claimed(struct carrier_panel *panel)
{
	report_line(panel->chip, LINE_HEARTBEAT, "led-heartbeat (gpio-leds)");
	report_line(panel->chip, LINE_BUTTON, "button-user (gpio-keys)");
}
