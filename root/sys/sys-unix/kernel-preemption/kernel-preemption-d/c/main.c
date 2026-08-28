/* спрощено до суті — так виглядає вихід із ділянки, де витіснення заборонене */
static inline void preempt_enable(void)
{
    barrier();                        /* компілятор не сміє переносити код через межу */
    if (--current_thread_info()->preempt_count == 0 &&
        test_thread_flag(TIF_NEED_RESCHED))
        preempt_schedule();           /* саме тут задачу й знімуть */
}

void spin_unlock(spinlock_t *lock)
{
    release(lock);
    preempt_enable();                 /* остання заборона зникла — можна перемикати */
}
