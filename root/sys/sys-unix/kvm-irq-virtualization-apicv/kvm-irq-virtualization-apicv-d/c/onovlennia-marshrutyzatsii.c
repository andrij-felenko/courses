int kvm_irq_delivery_to_apic(struct kvm *kvm, struct kvm_lapic *src,
                             struct kvm_lapic_irq *irq,
                             struct dest_map *dest_map)
{
    /* Перевірка можливості доставки через Posted Interrupts */
    if (kvm_x86_ops.deliver_posted_interrupt &&
        kvm_x86_ops.deliver_posted_interrupt(vcpu, irq->vector))
        return 1;

    /* Резервний шлях через програмне виставлення біта vIRR */
    return kvm_apic_set_irq(vcpu, irq, dest_map);
}
