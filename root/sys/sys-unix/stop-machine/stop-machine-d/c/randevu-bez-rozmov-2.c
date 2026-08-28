do {
        stop_machine_yield(cpumask);          /* здебільшого це cpu_relax() */
        newstate = READ_ONCE(msdata->state);
        if (newstate != curstate) {
                curstate = newstate;
                switch (curstate) {
                case MULTI_STOP_DISABLE_IRQ:
                        local_irq_disable();
                        hard_irq_disable();
                        break;
                case MULTI_STOP_RUN:
                        if (is_active)
                                err = msdata->fn(msdata->data);
                        break;
                default:
                        break;
                }
                ack_state(msdata);
        }
} while (curstate != MULTI_STOP_EXIT);
