#include <linux/kvm.h>

/* Базова структура першої версії (для зворотної сумісності) */
struct kvm_userspace_memory_region {
    __u32 slot;
    __u32 flags;
    __u64 guest_phys_addr;
    __u64 memory_size;
    __u64 userspace_addr;
};

/* Розширена структура другої версії (Linux 6.8+) */
struct kvm_userspace_memory_region2 {
    __u32 slot;            /* Унікальний індекс слота (0 .. KVM_USER_MEM_SLOTS - 1) */
    __u32 flags;           /* Конфігураційні прапорці слота пам'яті */
    __u64 guest_phys_addr; /* Початкова фізична адреса гостя (GPA, вирівняна на 4 КіБ) */
    __u64 memory_size;     /* Розмір регіону в байтах (повинен бути кратним 4 КіБ) */
    __u64 userspace_addr;  /* Віртуальна адреса буфера хоста (HVA, повернута mmap) */
    __u64 guest_memfd_offset; /* Зсув у файлі guest_memfd (для конфіденційних VM) */
    __u32 guest_memfd;     /* Файловий дескриптор анонімної пам'яті guest_memfd */
    __u32 pad1;
    __u64 pad2[14];
};

/* Приклад виклику в гіпервізорі */
int ret = ioctl(vm_fd, KVM_SET_USER_MEMORY_REGION2, &region);
