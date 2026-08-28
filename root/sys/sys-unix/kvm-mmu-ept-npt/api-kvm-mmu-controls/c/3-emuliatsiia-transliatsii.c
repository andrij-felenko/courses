struct kvm_translation {
    /* Вхідне поле */
    __u64 linear_address;  /* Віртуальна адреса гостя (GVA) */

    /* Вихідні поля стану */
    __u64 physical_address;/* Фізична адреса гостя (GPA) */
    __u8  valid;           /* 1 — трансляція успішна, 0 — виник page fault */
    __u8  writeable;       /* 1 — сторінка дозволена на запис */
    __u8  usermode;        /* 1 — сторінка доступна з неривілейованого Ring 3 */
    __u8  pad[5];
};

/* Виклик трансляції адреси */
int ret = ioctl(vcpu_fd, KVM_TRANSLATE, &translation);
