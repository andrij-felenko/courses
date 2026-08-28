/* fmap.c — карта файлу на екстенти через FIEMAP. */
#define _FILE_OFFSET_BITS 64

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>
#include <inttypes.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <linux/fiemap.h>
#include <linux/fs.h>

#define SLOTS 512          /* скільки екстентів беремо за один виклик */

static const struct { uint32_t bit; const char *name; } FLAGNAME[] = {
    { FIEMAP_EXTENT_LAST,           "last"        },
    { FIEMAP_EXTENT_UNKNOWN,        "unknown"     },
    { FIEMAP_EXTENT_DELALLOC,       "delalloc"    },
    { FIEMAP_EXTENT_ENCODED,        "encoded"     },
    { FIEMAP_EXTENT_DATA_ENCRYPTED, "encrypted"   },
    { FIEMAP_EXTENT_NOT_ALIGNED,    "not_aligned" },
    { FIEMAP_EXTENT_DATA_INLINE,    "inline"      },
    { FIEMAP_EXTENT_DATA_TAIL,      "tail"        },
    { FIEMAP_EXTENT_UNWRITTEN,      "unwritten"   },
    { FIEMAP_EXTENT_MERGED,         "merged"      },
    { FIEMAP_EXTENT_SHARED,         "shared"      },
};

static void flags_str(uint32_t f, char *out, size_t n)
{
    size_t used = 0;
    out[0] = '\0';
    for (size_t i = 0; i < sizeof FLAGNAME / sizeof FLAGNAME[0]; i++) {
        if (!(f & FLAGNAME[i].bit))
            continue;
        int k = snprintf(out + used, n - used, "%s%s", used ? "," : "", FLAGNAME[i].name);
        if (k < 0 || (size_t)k >= n - used)
            return;                       /* не влізло — обриваємо чесно */
        used += (size_t)k;
    }
}
