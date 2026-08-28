#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <linux/usbdevice_fs.h>
#include <linux/usb/ch9.h>

int main(void)
{
	int fd = open("/dev/bus/usb/001/007", O_RDWR);   /* саме RDWR */
	if (fd < 0) { perror("open"); return 1; }        /* EACCES → правило udev */

	__u32 caps = 0;
	ioctl(fd, USBDEVFS_GET_CAPABILITIES, &caps);

	unsigned int ifnum = 0;
	if (ioctl(fd, USBDEVFS_CLAIMINTERFACE, &ifnum) < 0 && errno == EBUSY) {
		struct usbdevfs_ioctl cmd = {
			.ifno       = ifnum,
			.ioctl_code = USBDEVFS_DISCONNECT,
			.data       = NULL,
		};
		ioctl(fd, USBDEVFS_IOCTL, &cmd);             /* відчепити драйвер ядра */
		ioctl(fd, USBDEVFS_CLAIMINTERFACE, &ifnum);  /* і взяти ще раз */
	}

	unsigned char buf[18];
	struct usbdevfs_ctrltransfer ctrl = {
		.bRequestType = USB_DIR_IN | USB_TYPE_STANDARD | USB_RECIP_DEVICE,
		.bRequest     = USB_REQ_GET_DESCRIPTOR,
		.wValue       = (USB_DT_DEVICE << 8) | 0,
		.wIndex       = 0,
		.wLength      = 18,          /* дескриптор пристрою — рівно 18 байтів */
		.timeout      = 1000,        /* мілісекунди, і ніколи не 0 */
		.data         = buf,
	};

	int n = ioctl(fd, USBDEVFS_CONTROL, &ctrl);      /* n — скільки байтів прийшло */
	if (n < 0)
		perror("USBDEVFS_CONTROL");
	else
		printf("VID:PID = %04x:%04x, отримано %d байтів\n",
		       buf[8] | (buf[9] << 8), buf[10] | (buf[11] << 8), n);

	ioctl(fd, USBDEVFS_RELEASEINTERFACE, &ifnum);
	close(fd);
	return 0;
}
