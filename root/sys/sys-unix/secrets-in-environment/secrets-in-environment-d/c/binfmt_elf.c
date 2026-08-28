/* Логіка визначення прапорця безпеки в ядрі Linux (fs/binfmt_elf.c) */
static int evaluate_secure_exec(struct linux_binprm *bprm) {
    if (bprm->cred->euid != current_euid() ||
        bprm->cred->egid != current_egid() ||
        !uid_eq(bprm->cred->uid, current_uid()) ||
        !gid_eq(bprm->cred->gid, current_gid()) ||
        !cap_issubset(bprm->cred->cap_permitted, current_cap_permitted())) {
            bprm->secureexec = 1;
    }
    return bprm->secureexec;
}
