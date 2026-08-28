struct sock_filter filter[] = {
    /* Перевірка архітектури процесора */
    BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

    /* Завантаження номера виклику */
    BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

    /* Блокування небезпечних викликів */
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_reboot, 4, 0),
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_kexec_load, 3, 0),
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_init_module, 2, 0),
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_swapon, 1, 0),

    /* Дозволити всі інші системні виклики */
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

    /* Заблоковані виклики повертають помилку EPERM */
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & 0xffff))
};
