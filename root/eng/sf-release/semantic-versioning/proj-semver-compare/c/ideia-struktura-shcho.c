#include <ctype.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>

#define SEMVER_MAX_IDS 16          // стелі з головою вистачає на будь-який реальний передвипуск

typedef enum { SEMVER_OK = 0, SEMVER_EINVAL = -1 } semver_err;

typedef struct {
    unsigned long major, minor, patch;
    int  pre_count;                // 0 → це готовий випуск, без передвипуску
    char pre[SEMVER_MAX_IDS][64];  // ідентифікатори передвипуску; числові теж тримаємо ТЕКСТОМ
    // метадані збірки навмисно не зберігаємо: на старшинство не впливають
} semver_t;
