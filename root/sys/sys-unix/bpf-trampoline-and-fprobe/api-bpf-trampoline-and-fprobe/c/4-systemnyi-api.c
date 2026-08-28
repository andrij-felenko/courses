struct bpf_kprobe_multi_opts {
    /* Розмір структури для гарантії зворотної сумісності ABI */
    size_t sz;
    /* Масив назв символів (наприклад, ["vfs_read", "vfs_write"]) */
    const char **syms;
    /* Масив абсолютних адрес функцій у пам'яті ядра */
    const unsigned long long *addrs;
    /* Опціональний масив 64-бітних cookies для ідентифікації подій у BPF */
    const unsigned long long *cookies;
    /* Кількість елементів у масивах */
    size_t cnt;
    /* Прапорці: BPF_TRACE_MULTI_RETPROBE для виходу з функції */
    u32 flags;
};

/* Головна функція приєднання в libbpf */
struct bpf_link *
bpf_program__attach_kprobe_multi_opts(const struct bpf_program *prog,
                                       const char *pattern,
                                       const struct bpf_kprobe_multi_opts *opts);
