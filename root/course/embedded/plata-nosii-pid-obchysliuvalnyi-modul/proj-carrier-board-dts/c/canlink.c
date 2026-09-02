/* canlink.c — телеметрія плати-носія в шину CAN-FD через SocketCAN. */
#include "carrier.h"

#include <errno.h>
#include <poll.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>

#include <linux/can.h>
#include <linux/can/raw.h>

#define STATUS_CAN_ID 0x100u
#define STATUS_FORMAT 0x01u

int carrier_can_open(struct carrier_can *can, const char *ifname)
{
	can->fd = -1;

	int fd = socket(PF_CAN, SOCK_RAW | SOCK_CLOEXEC, CAN_RAW);
	if (fd < 0)
		return -1;

	struct ifreq ifr;
	memset(&ifr, 0, sizeof ifr);
	strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);

	/* Інтерфейс з'являється лише тоді, коли драйвер mcp251xfd прив'язався
	   до вузла can@0, а адміністратор підняв його: ip link set can0 up. */
	if (ioctl(fd, SIOCGIFINDEX, &ifr) < 0)
		goto fail;

	int enable = 1;
	if (setsockopt(fd, SOL_CAN_RAW, CAN_RAW_FD_FRAMES,
		       &enable, sizeof enable) < 0)
		goto fail;	/* інтерфейс підняли без fd — кадри CAN-FD не пройдуть */

	struct sockaddr_can addr;
	memset(&addr, 0, sizeof addr);
	addr.can_family = AF_CAN;
	addr.can_ifindex = ifr.ifr_ifindex;
	if (bind(fd, (struct sockaddr *)&addr, sizeof addr) < 0)
		goto fail;

	can->fd = fd;
	return 0;

fail: {
		int saved = errno;
		close(fd);
		errno = saved;
		return -1;
	}
}

void carrier_can_close(struct carrier_can *can)
{
	if (can->fd >= 0) {
		close(can->fd);
		can->fd = -1;
	}
}

int carrier_can_send_status(struct carrier_can *can, double celsius, bool fault)
{
	static uint8_t seq;

	struct canfd_frame frame;
	memset(&frame, 0, sizeof frame);
	frame.can_id = STATUS_CAN_ID;
	frame.len = 8;
	frame.flags = CANFD_BRS;	/* дані швидшим бітрейтом */

	/* Температура — цілим у десятих градуса: у шину не пхають double. */
	double scaled = celsius * 10.0;
	int16_t deci = (int16_t)(scaled + (scaled >= 0 ? 0.5 : -0.5));

	frame.data[0] = STATUS_FORMAT;
	frame.data[1] = (uint8_t)(deci & 0xff);
	frame.data[2] = (uint8_t)((deci >> 8) & 0xff);
	frame.data[3] = fault ? 1 : 0;
	frame.data[4] = seq++;

	ssize_t n = write(can->fd, &frame, sizeof frame);
	if (n < 0)
		return -1;	/* ENOBUFS — черга передавання забита, ENETDOWN — шину поклали */
	if (n != (ssize_t)sizeof frame) {
		errno = EIO;
		return -1;
	}
	return 0;
}

int carrier_can_poll(struct carrier_can *can, int timeout_ms)
{
	struct pollfd pfd = { .fd = can->fd, .events = POLLIN, .revents = 0 };

	int ready = poll(&pfd, 1, timeout_ms);
	if (ready < 0)
		return (errno == EINTR) ? 0 : -1;
	if (ready == 0)
		return 0;

	struct canfd_frame frame;
	ssize_t n = read(can->fd, &frame, sizeof frame);
	if (n < 0)
		return -1;

	/* Класичний кадр приходить розміром CAN_MTU, кадр CAN-FD — CANFD_MTU:
	   інакше їх не розрізнити, бо структури збігаються початком. */
	if (n != (ssize_t)CAN_MTU && n != (ssize_t)CANFD_MTU) {
		errno = EIO;
		return -1;
	}

	if (frame.can_id & CAN_ERR_FLAG) {
		/* Кадр помилки від самого контролера, а не від вузла на шині. */
		fprintf(stderr, "CAN: кадр помилки, прапорці 0x%08x\n",
			frame.can_id & CAN_ERR_MASK);
		return 1;
	}

	printf("CAN rx id=0x%03x len=%u%s:",
	       frame.can_id & CAN_SFF_MASK, frame.len,
	       (n == (ssize_t)CANFD_MTU) ? " (fd)" : "");
	for (unsigned i = 0; i < frame.len; i++)
		printf(" %02x", frame.data[i]);
	printf("\n");
	return 1;
}
