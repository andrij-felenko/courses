struct kvm_irq_routing {
    __u32 nr;           /* Кількість записів у масиві entries[] */
    __u32 flags;        /* Зарезервовано для розширень, обов'язково 0 */
    struct kvm_irq_routing_entry entries[0];
};

struct kvm_irq_routing_entry {
    __u32 gsi;          /* Номер Global System Interrupt */
    __u32 type;         /* Тип трансляції: IRQCHIP або MSI */
    __u32 flags;        /* Специфічні прапорці маршрутизації (зазвичай 0) */
    __u32 pad;
    union {
        struct kvm_irq_routing_irqchip irqchip;
        struct kvm_irq_routing_msi     msi;
        __u32 hv_sint;  /* Для синтетичних контролерів Hyper-V SynIC */
        __u32 pad[8];
    } u;
};
