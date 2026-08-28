struct kvm_segment {
    __u64 base;        // Базова адреса сегмента
    __u32 limit;       // Межа сегмента
    __u16 selector;    // Селектор сегмента
    __u8  type;        // Тип сегмента (Code, Data, System)
    __u8  present;     // Прапор наявності (P)
    __u8  dpl;         // Рівень привілеїв (Descriptor Privilege Level, 0..3)
    __u8  db;          // Default size (0 = 16-bit, 1 = 32-bit)
    __u8  s;           // Descriptor type (0 = system, 1 = code/data)
    __u8  l;           // Long mode прапор (1 = 64-bit code)
    __u8  g;           // Granularity (0 = byte, 1 = сторінка 4 КіБ)
    __u8  avl;
    __u8  unusable;
    __u8  padding;
};

struct kvm_sregs {
    struct kvm_segment cs, ds, es, fs, gs, ss;
    struct kvm_segment tr, ldt;
    struct kvm_dtable gdt, idt;
    __u64 cr0, cr2, cr3, cr4, cr8;
    __u64 efer;        // Extended Feature Enable Register (вмикає Long Mode)
    __u64 apic_base;   // Фізична адреса Local APIC
    __u64 interrupt_bitmap[(KVM_NR_INTERRUPTS + 63) / 64];
};
