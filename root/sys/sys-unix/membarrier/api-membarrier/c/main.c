enum mb_mode { MB_PRIVATE, MB_GLOBAL, MB_NONE };
static enum mb_mode mode = MB_NONE;

void mb_setup(void)
{
    long mask = membarrier(MEMBARRIER_CMD_QUERY, 0, 0);
    if (mask < 0)                             /* ENOSYS: ядро старіше за 4.3 */
        return;                               /* лишається MB_NONE */

    if ((mask & MEMBARRIER_CMD_PRIVATE_EXPEDITED) &&
        membarrier(MEMBARRIER_CMD_REGISTER_PRIVATE_EXPEDITED, 0, 0) == 0) {
        mode = MB_PRIVATE;
        return;
    }
    if (mask & MEMBARRIER_CMD_GLOBAL)         /* при nohz_full біта немає */
        mode = MB_GLOBAL;
}
