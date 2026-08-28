#define _GNU_SOURCE
#include <fcntl.h>
#include <errno.h>

enum reserve_result { RESERVE_OK, RESERVE_UNSUPPORTED, RESERVE_FAILED };

/* Закріпити місце під файл наперед — без тихого запису нулів. */
enum reserve_result reserve_space(int fd, off_t bytes)
{
    if (fallocate(fd, 0, 0, bytes) == 0)
        return RESERVE_OK;

    if (errno == EOPNOTSUPP || errno == ENOSYS)
        return RESERVE_UNSUPPORTED;  /* ФС або ядро не вміють */

    return RESERVE_FAILED;           /* ENOSPC, EFBIG, EIO — справжня відмова */
}
