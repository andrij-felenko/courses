struct irq_domain {
    const struct irq_domain_ops *ops;
    void                        *host_data;
    unsigned int                 flags;
    irq_hw_number_t              hwirq_max;
    
    /* Зворотне відображення для швидкого пошуку virq за hwirq */
    unsigned int                 revmap_size;
    struct radix_tree_root       revmap_tree;
    unsigned int                 linear_revmap[];
};
