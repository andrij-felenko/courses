    /* 3. Виділити пам'ять гостя й віддати її машині. */
    const size_t mem_size = 0x1000;              /* одна сторінка, 4 КіБ */
    void *mem = mmap(NULL, mem_size, PROT_READ | PROT_WRITE,
                     MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    if (mem == MAP_FAILED) { perror("mmap пам'ять гостя"); return 1; }

    struct kvm_userspace_memory_region region = {
        .slot            = 0,
        .guest_phys_addr = 0x1000,     /* якою її бачить «фізично» гість */
        .memory_size     = mem_size,
        .userspace_addr  = (uint64_t)mem,  /* де вона насправді в нас */
    };
    if (ioctl(vmfd, KVM_SET_USER_MEMORY_REGION, &region) < 0) {
        perror("KVM_SET_USER_MEMORY_REGION"); return 1;
    }
