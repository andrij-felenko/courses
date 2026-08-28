static void install_seccomp(void)
{
#define ALLOW(nr) \
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, (nr), 0, 1), \
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW)

    struct sock_filter code[] = {
        /* номери викликів мають сенс лише разом з архітектурою */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, arch)),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
        ALLOW(__NR_read),    ALLOW(__NR_write),
        ALLOW(__NR_recvmsg), ALLOW(__NR_sendmsg),
        ALLOW(__NR_sendto),  /* glibc-івський send() на x86-64 — це sendto */
        ALLOW(__NR_close),   ALLOW(__NR_rt_sigreturn),
        ALLOW(__NR_exit_group),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
    };
#undef ALLOW
    struct sock_fprog prog = { .len = sizeof code / sizeof code[0], .filter = code };
    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog, 0, 0) != 0)
        die("seccomp");
}

static void cage(uid_t uid, gid_t gid)
{
    /* 1. Клітку ставимо, поки ще є права її поставити. */
    if (chroot("/var/empty") != 0 || chdir("/") != 0) die("chroot");

    /* 2. Обмежувальний набір знімаємо, доки в дії ще є CAP_SETPCAP. */
    for (int cap = 0; cap <= 63; cap++)
        prctl(PR_CAPBSET_DROP, cap, 0, 0, 0);   /* EINVAL на неіснуючих — очікувано */
    prctl(PR_CAP_AMBIENT, PR_CAP_AMBIENT_CLEAR_ALL, 0, 0, 0);

    /* 3. Групи — ПЕРЕД uid: без root setgroups уже не спрацює. */
    if (setgroups(0, NULL) != 0)      die("setgroups");
    if (setresgid(gid, gid, gid) != 0) die("setresgid");
    if (setresuid(uid, uid, uid) != 0) die("setresuid");

    /* 4. Не вірити, а перевірити: повернення має бути неможливим. */
    if (setresuid(0, 0, 0) == 0) { errno = 0; die("uid still root"); }
    uid_t r, e, s;
    if (getresuid(&r, &e, &s) != 0 || r != uid || e != uid || s != uid) die("uid");

    /* 5. Жодного нового привілею навіть через чужий setuid-файл. */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) die("no_new_privs");
    install_seccomp();
}
