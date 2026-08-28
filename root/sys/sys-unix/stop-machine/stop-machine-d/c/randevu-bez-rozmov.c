enum multi_stop_state {
        MULTI_STOP_NONE,
        MULTI_STOP_PREPARE,      /* усі прокинулися й крутяться в циклі */
        MULTI_STOP_DISABLE_IRQ,  /* усі вимкнули собі переривання */
        MULTI_STOP_RUN,          /* активні виконують fn */
        MULTI_STOP_EXIT,         /* можна розходитися */
};

static void set_state(struct multi_stop_data *msdata,
                      enum multi_stop_state newstate)
{
        atomic_set(&msdata->thread_ack, msdata->num_threads);
        smp_wmb();
        WRITE_ONCE(msdata->state, newstate);
}

/* хто підтвердив останнім — той і переводить у наступний стан */
static void ack_state(struct multi_stop_data *msdata)
{
        if (atomic_dec_and_test(&msdata->thread_ack))
                set_state(msdata, msdata->state + 1);
}
