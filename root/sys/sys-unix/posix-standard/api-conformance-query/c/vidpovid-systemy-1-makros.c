#include <unistd.h>

static int have_spawn(void) {
#if !defined(_POSIX_SPAWN) || _POSIX_SPAWN == -1
    return 0;                          /* немає й не буде */
#elif _POSIX_SPAWN == 0
    return sysconf(_SC_SPAWN) > 0;     /* вирішиться на місці */
#else
    return 1;                          /* є завжди */
#endif
}
