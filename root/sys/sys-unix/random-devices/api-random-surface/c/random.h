#include <linux/random.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <string.h>

struct {
	struct rand_pool_info hdr;
	unsigned char data[32];
} req;

memcpy(req.data, from_hwrng, sizeof req.data);
req.hdr.entropy_count = 8 * sizeof req.data;   /* 256 бітів */
req.hdr.buf_size      = sizeof req.data;       /* 32 байти  */

int fd = open("/dev/urandom", O_WRONLY);
if (ioctl(fd, RNDADDENTROPY, &req) < 0)
	perror("RNDADDENTROPY");                   /* EPERM — немає CAP_SYS_ADMIN */
