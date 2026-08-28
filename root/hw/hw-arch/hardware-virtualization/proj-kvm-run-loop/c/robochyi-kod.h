    /* 6. Налаштувати реальний режим: сегменти й лічильник команд. */
    struct kvm_sregs sregs;
    ioctl(vcpufd, KVM_GET_SREGS, &sregs);
    sregs.cs.base     = 0;       /* база сегмента коду */
    sregs.cs.selector = 0;       /* селектор — узгоджений із базою */
    ioctl(vcpufd, KVM_SET_SREGS, &sregs);

    struct kvm_regs regs = {
        .rip    = 0x1000,    /* CS.base(0) + IP(0x1000) = фізична 0x1000 */
        .rax    = 2,         /* al = 2 */
        .rbx    = 2,         /* bl = 2 */
        .rflags = 0x2,       /* біт 1 завжди 1 — інакше стан недійсний */
    };
    ioctl(vcpufd, KVM_SET_REGS, &regs);
