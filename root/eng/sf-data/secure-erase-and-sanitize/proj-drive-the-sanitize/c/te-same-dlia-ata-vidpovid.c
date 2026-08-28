#include <scsi/sg.h>

/* progress — частка від 0xFFFF; flags — байт стану (біти 7:4) */
static int ata_sanitize_status(int fd, unsigned *progress, unsigned *flags)
{
    uint8_t cdb[16] = {0}, sense[64] = {0};
    sg_io_hdr_t io;

    cdb[0]  = 0x85;             /* ATA PASS-THROUGH (16) */
    cdb[1]  = (3 << 1) | 1;     /* PROTOCOL = 3 (Non-data), EXTEND = 1 */
    cdb[2]  = 0x20;             /* CK_COND = 1, T_LENGTH = 0 */
    cdb[4]  = 0x00;             /* FEATURE (7:0) = SANITIZE STATUS EXT */
    cdb[14] = 0xb4;             /* COMMAND = SANITIZE DEVICE */

    memset(&io, 0, sizeof io);
    io.interface_id    = 'S';
    io.dxfer_direction = SG_DXFER_NONE;
    io.cmdp = cdb;   io.cmd_len   = sizeof cdb;
    io.sbp  = sense; io.mx_sb_len = sizeof sense;
    io.timeout = 10000;

    if (ioctl(fd, SG_IO, &io) < 0) return -errno;

    unsigned code = sense[0] & 0x7f;
    if (code != 0x72 && code != 0x73) return -EPROTO;  /* потрібен descriptor-формат */

    unsigned end = 8 + sense[7];
    if (end > sizeof sense) end = sizeof sense;
    for (unsigned i = 8; i + 13 < end; i += sense[i + 1] + 2) {
        if (sense[i] != 0x09) continue;                /* ATA Status Return */
        const uint8_t *d = sense + i;
        *flags    = d[4];                              /* COUNT (15:8) */
        *progress = ((unsigned)d[9] << 8) | d[7];      /* LBA_MID : LBA_LOW */
        return 0;
    }
    return -ENOENT;
}
