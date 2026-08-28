/* opal-report.c — cc -O2 -Wall -o opal-report opal-report.c */
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/sed-opal.h>

static uint16_t be16(const unsigned char *p) { return (uint16_t)(p[0] << 8 | p[1]); }
static uint32_t be32(const unsigned char *p)
{
        return (uint32_t)p[0] << 24 | (uint32_t)p[1] << 16 | (uint32_t)p[2] << 8 | p[3];
}
static uint64_t be64(const unsigned char *p) { return (uint64_t)be32(p) << 32 | be32(p + 4); }

static void report_status(int fd)
{
        static const struct { unsigned bit; const char *name; } fl[] = {
                { OPAL_FL_SUPPORTED,         "Opal підтримується" },
                { OPAL_FL_LOCKING_SUPPORTED, "замикання можливе" },
                { OPAL_FL_LOCKING_ENABLED,   "замикання налаштовано" },
                { OPAL_FL_LOCKED,            "замкнено просто зараз" },
                { OPAL_FL_MBR_ENABLED,       "тіньовий MBR увімкнено" },
                { OPAL_FL_MBR_DONE,          "тіньовий MBR уже пройдено" },
        };
        struct opal_status st = { 0 };

        if (ioctl(fd, IOC_OPAL_GET_STATUS, &st) < 0) {
                printf("GET_STATUS: %s\n", strerror(errno));
                return;
        }
        printf("прапорці ядра: 0x%08x\n", st.flags);
        for (size_t i = 0; i < sizeof fl / sizeof *fl; i++)
                printf("  %s: %s\n", fl[i].name, (st.flags & fl[i].bit) ? "так" : "ні");
}
