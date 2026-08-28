struct irq_desc {
    struct irq_common_data  irq_common_data;
    struct irq_data         irq_data;
    unsigned int __percpu  *kstat_irqs;     /* Статистика спрацьовувань по ядрах */
    irq_flow_handler_t      handle_irq;     /* Диспетчер високого рівня */
    struct irqaction       *action;         /* Ланцюжок зареєстрованих обробників */
    unsigned int            status_use_accessors;
    unsigned int            core_internal_state__do_not_mess_with_it;
    unsigned int            depth;          /* Лічильник маскування лінії */
    raw_spinlock_t          lock;           /* Захист стану лінії */
    struct cpumask         *percpu_enabled;
    const char             *name;
};
