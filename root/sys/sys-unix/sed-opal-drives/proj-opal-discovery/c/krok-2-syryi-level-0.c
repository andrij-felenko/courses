static void report_discovery(int fd)
{
        unsigned char buf[2048];
        struct opal_discovery d = { .data = (uint64_t)(uintptr_t)buf, .size = sizeof buf };
        int n = ioctl(fd, IOC_OPAL_DISCOVERY, &d);   /* n > 0 — довжина відповіді */

        if (n < 0) {
                printf("DISCOVERY: %s\n", strerror(errno));
                return;
        }
        size_t have = (size_t)n < sizeof buf ? (size_t)n : sizeof buf;
        if (have < 48) {
                printf("буфер закороткий: %zu байтів\n", have);
                return;
        }
        printf("Level 0 Discovery: тіло %u байтів, версія структури %u\n",
               be32(buf), be32(buf + 4));

        for (size_t off = 48; off + 4 <= have; ) {
                uint16_t code = be16(buf + off);
                unsigned ver  = buf[off + 2] >> 4;
                unsigned len  = buf[off + 3];
                const unsigned char *p = buf + off + 4;   /* дані дескриптора */
                unsigned need = code == 0x0003 ? 28 : code == 0x0203 ? 9 :
                                code == 0x0200 ? 4 : 1;   /* скільки байтів читає switch */

                if (off + 4 + len > have) {
                        printf("  дескриптор 0x%04x обрізано\n", code);
                        break;
                }
                if (len < need) {                         /* прошивка дала коротший дескриптор */
                        printf("  дескриптор 0x%04x: лише %u байтів даних\n", code, len);
                        off += 4u + len;
                        continue;
                }
                switch (code) {
                case 0x0001:
                        printf("  TPer v%u: синхронний=%d асинхронний=%d керування ComID=%d\n",
                               ver, !!(p[0] & 0x01), !!(p[0] & 0x02), !!(p[0] & 0x40));
                        break;
                case 0x0002:
                        printf("  Locking v%u: можливе=%d налаштовано=%d замкнено=%d "
                               "шифрування носія=%d тіньовий MBR=%d пройдено=%d\n", ver,
                               !!(p[0] & 0x01), !!(p[0] & 0x02), !!(p[0] & 0x04),
                               !!(p[0] & 0x08), !!(p[0] & 0x10), !!(p[0] & 0x20));
                        break;
                case 0x0003:
                        printf("  Geometry v%u: логічний блок=%u Б, гранула=%" PRIu64 " блоків, "
                               "перший вирівняний LBA=%" PRIu64 ", вирівнювання обов'язкове=%d\n",
                               ver, be32(p + 8), be64(p + 12), be64(p + 20), p[0] & 1);
                        break;
                case 0x0200:
                        printf("  Opal SSC v1.00: базовий ComID=0x%04x, усього ComID=%u\n",
                               be16(p), be16(p + 2));
                        break;
                case 0x0203:
                        printf("  Opal SSC v2.00: базовий ComID=0x%04x, усього ComID=%u, "
                               "адмінів Locking SP=%u, користувачів=%u\n",
                               be16(p), be16(p + 2), be16(p + 5), be16(p + 7));
                        break;
                default:
                        printf("  можливість 0x%04x v%u, %u байтів даних\n", code, ver, len);
                }
                off += 4u + len;
        }
}
