/* vendorio.c — інтерфейс класу ff у своїх руках
   збирання:  cc -O2 -Wall -o vendorio vendorio.c -lusb-1.0            */
#include <libusb-1.0/libusb.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>

#define VID     0x1209      /* pid.codes: VID для відкритого заліза */
#define PID     0x0001      /* тестовий PID із їхнього діапазону    */
#define IFACE   0
#define EP_OUT  0x01
#define EP_IN   0x81
#define RING    4           /* скільки заявок тримаємо в польоті    */

static volatile sig_atomic_t running = 1;
static void on_sigint(int sig) { (void)sig; running = 0; }

static libusb_device_handle *find_device(libusb_context *ctx, const char *serial)
{
	libusb_device **list;
	libusb_device_handle *found = NULL;
	ssize_t n = libusb_get_device_list(ctx, &list);

	if (n < 0)
		return NULL;

	for (ssize_t i = 0; i < n && !found; i++) {
		struct libusb_device_descriptor d;
		libusb_device_handle *h;
		unsigned char sn[64];
		int rc;

		if (libusb_get_device_descriptor(list[i], &d) != 0)
			continue;
		if (d.idVendor != VID || d.idProduct != PID)
			continue;

		rc = libusb_open(list[i], &h);
		if (rc != 0) {
			/* Чужа плата з тим самим VID/PID, до якої нас не пустили,
			   не привід кидати пошук власної.                        */
			fprintf(stderr, "%d-%d: %s\n",
			        libusb_get_bus_number(list[i]),
			        libusb_get_device_address(list[i]),
			        libusb_error_name(rc));
			continue;
		}

		if (!serial) {
			found = h;
			continue;
		}
		/* iSerialNumber — це індекс, а не рядок: по ньому йде
		   окрема керуюча передача до самого пристрою.        */
		if (d.iSerialNumber &&
		    libusb_get_string_descriptor_ascii(h, d.iSerialNumber,
		                                       sn, sizeof sn) > 0 &&
		    strcmp((char *)sn, serial) == 0)
			found = h;
		else
			libusb_close(h);
	}

	libusb_free_device_list(list, 1);   /* 1 — відпустити посилання */
	return found;
}
