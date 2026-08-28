#include <errno.h>

static long finish(long r)
{
    if ((unsigned long)r >= (unsigned long)-4095) {   /* тобто −4095 … −1 */
        errno = (int)(-r);
        return -1;
    }
    return r;
}
