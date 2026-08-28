/* Фрагмент концептуальної логіки fs/binfmt_elf.c у ядрі Linux */
static int create_elf_tables(struct linux_binprm *bprm, const struct elfhdr *exec,
                             unsigned long load_addr, unsigned long interp_load_addr)
{
    unsigned long p = bprm->p;
    /* Копіювання 16 випадкових байтів для AT_RANDOM */
    u8 k_rand[16];
    get_random_bytes(k_rand, sizeof(k_rand));
    p = copy_strings_kernel(1, &k_rand_ptr, p);
    
    /* Розрахунок кількості записів у допоміжному векторі */
    struct elf_item auxv[AT_VECTOR_SIZE];
    int ei = 0;

    /* Заповнення обов'язкових векторів */
    NEW_AUX_ENT(AT_HWCAP, ELF_HWCAP);
    NEW_AUX_ENT(AT_PAGESZ, ELF_EXEC_PAGESIZE);
    NEW_AUX_ENT(AT_CLKTCK, CLK_TCK);
    NEW_AUX_ENT(AT_PHDR, load_addr + exec->e_phoff);
    NEW_AUX_ENT(AT_PHENT, sizeof(struct elf_phdr));
    NEW_AUX_ENT(AT_PHNUM, exec->e_phnum);
    NEW_AUX_ENT(AT_BASE, interp_load_addr);
    NEW_AUX_ENT(AT_FLAGS, 0);
    NEW_AUX_ENT(AT_ENTRY, exec->e_entry);
    NEW_AUX_ENT(AT_UID, from_kuid_munged(cred->user_ns, cred->uid));
    NEW_AUX_ENT(AT_EUID, from_kuid_munged(cred->user_ns, cred->euid));
    NEW_AUX_ENT(AT_GID, from_kgid_munged(cred->user_ns, cred->gid));
    NEW_AUX_ENT(AT_EGID, from_kgid_munged(cred->user_ns, cred->egid));
    NEW_AUX_ENT(AT_SECURE, bprm->secureexec);
    NEW_AUX_ENT(AT_RANDOM, rand_user_addr);
    NEW_AUX_ENT(AT_EXECFN, execfn_user_addr);
    
    if (vdso_enabled) {
        NEW_AUX_ENT(AT_SYSINFO_EHDR, vdso_addr);
    }

    NEW_AUX_ENT(AT_NULL, 0); /* Термінатор вектора */
}
