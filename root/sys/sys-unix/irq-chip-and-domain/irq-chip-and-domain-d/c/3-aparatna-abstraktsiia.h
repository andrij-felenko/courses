struct irq_chip {
    const char  *name;
    void        (*irq_mask)(struct irq_data *data);
    void        (*irq_unmask)(struct irq_data *data);
    void        (*irq_ack)(struct irq_data *data);
    void        (*irq_eoi)(struct irq_data *data);
    int         (*irq_set_affinity)(struct irq_data *data,
                                    const struct cpumask *dest, bool force);
    int         (*irq_retrigger)(struct irq_data *data);
    int         (*irq_set_type)(struct irq_data *data, unsigned int flow_type);
    int         (*irq_set_wake)(struct irq_data *data, unsigned int on);
    void        (*irq_bus_lock)(struct irq_data *data);
    void        (*irq_bus_sync_unlock)(struct irq_data *data);
    unsigned long flags;
};
