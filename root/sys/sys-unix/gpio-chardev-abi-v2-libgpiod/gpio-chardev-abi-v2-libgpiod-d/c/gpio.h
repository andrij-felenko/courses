#include <linux/gpio.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

struct gpio_v2_line_request req;
memset(&req, 0, sizeof(req));

/* Вибір офсетів ліній на чипі */
req.offsets[0] = 4;  /* Пін D0 */
req.offsets[1] = 5;  /* Пін D1 */
req.offsets[2] = 6;  /* Пін D2 */
req.num_lines = 3;
strcpy(req.consumer, "lcd_data_bus");

/* Конфігурація: напрямок на вихід */
req.config.flags = GPIO_V2_LINE_FLAG_OUTPUT;

/* Атомарне отримання дескриптора володіння */
int ret = ioctl(chip_fd, GPIO_V2_GET_LINE_IOCTL, &req);
int req_fd = req.fd;
