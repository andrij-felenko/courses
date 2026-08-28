/* Довжина запису, що починається на початку буфера buf довжиною avail байтів.
   Повертає 0, якщо байтів ще не вистачає або на місці магії щось інше. */
size_t tlog_record_len(const uint8_t *buf, size_t avail)
{
    if (avail < 10) return 0;                 /* 8 мітки + магія + довжина */

    const uint8_t magic = buf[8];
    const uint8_t len   = buf[9];             /* довжина навантаження */

    if (magic == 0xFE) {                      /* MAVLink 1 */
        return 8 + 6 + (size_t)len + 2;
    }
    if (magic != 0xFD) return 0;              /* це не початок кадру */

    if (avail < 11) return 0;                 /* потрібен ще байт прапорців */
    const uint8_t incompat = buf[10];
    const size_t  sig = (incompat & 0x01) ? 13 : 0;   /* MAVLINK_IFLAG_SIGNED */

    return 8 + 10 + (size_t)len + 2 + sig;
}
