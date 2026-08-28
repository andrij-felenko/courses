#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/fs.h>

int fd = open("/srv/data", O_RDONLY | O_DIRECTORY);
if (fd < 0)
        return -1;

if (ioctl(fd, FIFREEZE, 0) < 0)   /* аргумент є в підписі, але не читається */
        return -1;                /* errno — за таблицею нижче */

/* ... вікно: тут той, хто знімає копію, робить свою справу ... */

if (ioctl(fd, FITHAW, 0) < 0)
        return -1;

close(fd);                        /* close НЕ відтає — див. «Пастки» */
