static inline unsigned int __task_state_index(unsigned int tsk_state,
                                              unsigned int tsk_exit_state)
{
    unsigned int state = (tsk_state | tsk_exit_state) & TASK_REPORT;

    if ((tsk_state & TASK_IDLE) == TASK_IDLE)
        state = TASK_REPORT_IDLE;          /* 0x80 — понад маску */

    if ((tsk_state & TASK_RTLOCK_WAIT) || (tsk_state & TASK_FROZEN))
        state = TASK_UNINTERRUPTIBLE;      /* свідома підміна: показати як D */

    return fls(state);                     /* номер старшого одиничного біта */
}
