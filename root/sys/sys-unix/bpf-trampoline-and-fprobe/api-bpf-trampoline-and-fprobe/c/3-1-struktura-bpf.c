struct bpf_trampoline {
    /* Хеш-вузол для швидкого пошуку в глобальній таблиці tramp_table */
    struct hlist_node hlist;
    
    /* Ключ хешування (комбінація ID модуля ядра та адреси IP цільової функції) */
    u64 key;
    
    /* Лічильник активних посилань приєднаних BPF програм */
    int refcnt;
    
    /* Списки приєднаних програм за типами (fentry, fexit, fmod_ret) */
    struct hlist_head progs_hlist[BPF_TRAMP_MAX];
    
    /* Згенерований машинний код трампліна у виконуваній пам'яті JIT */
    void *image;
    u32 image_size;
    
    /* Прапорці стану (наприклад, BPF_TRAMP_F_ORIG_STACK) */
    u32 flags;
    
    /* Структура реєстрації в підсистемі ftrace */
    struct ftrace_ops fops;
};
