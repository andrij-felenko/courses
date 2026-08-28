union bpf_attr {
    struct {
        __u32   prog_type;       // Тип програми (BPF_PROG_TYPE_KPROBE, BPF_PROG_TYPE_SCHED_CLS тощо)
        __u32   insn_cnt;        // Кількість 64-бітних інструкцій у байт-коді
        __aligned_u64 insns;     // Вказівник у просторі користувача (const struct bpf_insn *)
        __aligned_u64 license;   // Вказівник на рядок ліцензії (const char *), наприклад "GPL"
        __u32   log_level;       // Рівень деталей верифікатора: 0 (вимкнено), 1 (лог), 2 (детальний log)
        __u32   log_size;        // Розмір буфера для логу у байтах
        __aligned_u64 log_buf;   // Вказівник на буфер пам'яті (char *), куди ядро запише текстовий лог
        __u32   kern_version;    // Версія ядра (потрібна для старих kprobe у ядрах < 4.18)
        __u32   prog_flags;      // Прапорці (наприклад, BPF_F_STRICT_ALIGNMENT)
        char    prog_name[16];   // Символьна назва функції eBPF
        __u32   prog_btf_fd;     // fd завантаженого об'єкта BTF
        __u32   expected_attach_type; // Очікуваний тип прикріплення для Tracing/LSM
    };
};
