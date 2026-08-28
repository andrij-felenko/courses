static const char * const task_state_array[] = {
    /* стани в масці TASK_REPORT: */
    "R (running)",      /* 0x00 */
    "S (sleeping)",     /* 0x01 */
    "D (disk sleep)",   /* 0x02 */
    "T (stopped)",      /* 0x04 */
    "t (tracing stop)", /* 0x08 */
    "X (dead)",         /* 0x10 */
    "Z (zombie)",       /* 0x20 */
    "P (parked)",       /* 0x40 */
    /* стан поза маскою: */
    "I (idle)",         /* 0x80 */
};
