struct kvm_lapic {
    unsigned long base_address;
    struct kvm_io_device dev;
    struct kvm_timer lapic_timer;
    u32 divide_count;
    struct kvm_vcpu *vcpu;
    bool sw_enabled;
    bool irr_pending;
    /* Вказівник на сторінку Virtual-APIC Page */
    void *regs;
    gfn_t vapic_gfn;
    struct page *vapic_page;
    /* Тіньові копії для швидкого доступу */
    u32 highest_isr_cache;
    void (*deliver)(struct kvm_lapic *apic, int delivery_mode, int trig_mode, int vector);
};
